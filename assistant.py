"""
SOFI AI ASSISTANT INTEGRATION
=============================
OpenAI Assistant integration with money transfer capabilities
"""

import os
import json
import logging
import asyncio
import time
import threading
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from sofi_money_functions import SofiMoneyTransferService
from sofi_assistant_functions import SOFI_MONEY_FUNCTIONS, SOFI_MONEY_INSTRUCTIONS
from supabase import create_client
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """High-performance background task manager for OpenAI operations"""
    
    def __init__(self):
        self.active_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=50)  # Handle 50+ concurrent users
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
    async def send_telegram_message(self, chat_id: str, message: str):
        """Send message via Telegram API"""
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            # Use background thread for HTTP request
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, 
                lambda: requests.post(url, json=payload, timeout=5))
            logger.info(f"✅ Sent completion message to {chat_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
    
    async def process_openai_run_background(self, run, thread_id: str, chat_id: str, 
                                          assistant_client, money_service):
        """Process OpenAI run in background without blocking"""
        try:
            logger.info(f"🚀 Starting background processing for {chat_id}")
            start_time = time.time()
            
            function_data = {}
            max_iterations = 30  # 30 seconds max
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Check run status (non-blocking)
                try:
                    run = assistant_client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                except Exception as e:
                    logger.error(f"❌ OpenAI API error: {e}")
                    await self.send_telegram_message(chat_id, 
                        "❌ Sorry, I encountered a technical issue. Please try again.")
                    return
                
                if run.status == "completed":
                    # Get the response
                    messages = assistant_client.beta.threads.messages.list(thread_id=thread_id)
                    response_text = None
                    
                    if messages.data and messages.data[0].content:
                        response = messages.data[0].content[0].text.value
                        if response and response.strip() and response.strip().lower() not in ["null", "none", ""]:
                            response_text = response
                    
                    # Generate response from function data if needed
                    if not response_text and function_data:
                        response_text = self._generate_completion_message(function_data)
                    
                    if response_text:
                        elapsed = time.time() - start_time
                        logger.info(f"⚡ Background processing completed in {elapsed:.2f}s for {chat_id}")
                        await self.send_telegram_message(chat_id, response_text)
                    
                    # Clean up
                    self.active_tasks.pop(chat_id, None)
                    return
                
                elif run.status == "requires_action":
                    # Handle function calls in background
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"🔧 Background function execution: {function_name}")
                        
                        try:
                            # Execute function in background
                            result = await self._execute_function_background(
                                function_name, function_args, chat_id, money_service)
                            function_data[function_name] = result
                            
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(result)
                            })
                        except Exception as e:
                            logger.error(f"❌ Background function error: {e}")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": str(e)})
                            })
                    
                    # Submit tool outputs
                    try:
                        run = assistant_client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                    except Exception as e:
                        logger.error(f"❌ Failed to submit tool outputs: {e}")
                        await self.send_telegram_message(chat_id, 
                            "❌ Sorry, I encountered an issue processing your request.")
                        return
                
                elif run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"❌ Background run failed with status: {run.status}")
                    await self.send_telegram_message(chat_id, 
                        f"❌ Sorry, I encountered an error: {run.status}")
                    self.active_tasks.pop(chat_id, None)
                    return
                
                # Non-blocking wait
                await asyncio.sleep(0.5)  # Check every 500ms instead of 1s
            
            # Timeout fallback
            logger.warning(f"⏰ Background processing timeout for {chat_id}")
            await self.send_telegram_message(chat_id, 
                "⏰ Your request is taking longer than expected. I'll continue processing and update you shortly.")
            
        except Exception as e:
            logger.error(f"❌ Background processing error for {chat_id}: {e}")
            await self.send_telegram_message(chat_id, 
                "❌ Sorry, I encountered an unexpected error. Please try again.")
        finally:
            # Always clean up
            self.active_tasks.pop(chat_id, None)
    
    def _generate_completion_message(self, function_data: Dict) -> str:
        """Generate completion message from function results"""
        for func_name, func_result in function_data.items():
            if func_name == "send_money" and isinstance(func_result, dict):
                if func_result.get("success"):
                    reference = func_result.get("reference", "N/A")
                    message = f"✅ Transfer completed successfully! Reference: {reference}"
                    
                    # Add beneficiary save prompt if available
                    if func_result.get("save_beneficiary_prompt"):
                        message += f"\n\n{func_result['save_beneficiary_prompt']}"
                    
                    return message
                elif func_result.get("error"):
                    return f"❌ Transfer failed: {func_result.get('error')}"
            elif func_name == "check_balance" and isinstance(func_result, dict):
                if func_result.get("balance") is not None:
                    balance = func_result.get("balance", 0)
                    return f"💰 Your current balance is ₦{balance:,.2f}"
            elif func_name == "get_user_beneficiaries" and isinstance(func_result, dict):
                if func_result.get("success"):
                    return func_result.get("message", "✅ Beneficiaries loaded")
            elif func_name == "save_beneficiary" and isinstance(func_result, dict):
                if func_result.get("success"):
                    return func_result.get("message", "✅ Beneficiary saved successfully!")
                else:
                    return func_result.get("error", "❌ Failed to save beneficiary")
            elif func_name == "find_beneficiary_by_name" and isinstance(func_result, dict):
                return func_result.get("message", "✅ Search completed")
        
        return "✅ Your request has been processed successfully!"
    
    async def _execute_function_background(self, function_name: str, function_args: Dict, 
                                         chat_id: str, money_service) -> Dict[str, Any]:
        """Execute function in background thread"""
        try:
            # All the same function execution logic, but in background
            if function_name == "verify_account_name":
                return await money_service.verify_account_name(
                    account_number=function_args.get("account_number"),
                    bank_code=function_args.get("bank_name") or function_args.get("bank_code")
                )
            elif function_name == "check_balance":
                return await money_service.check_user_balance(telegram_chat_id=chat_id)
            elif function_name == "send_money":
                # Background transfer processing
                recipient_account = function_args.get("account_number") or function_args.get("recipient_account")
                recipient_bank = function_args.get("bank_name") or function_args.get("recipient_bank") 
                amount = function_args.get("amount")
                reason = function_args.get("narration") or function_args.get("reason", "Transfer via Sofi AI")
                
                if not all([recipient_account, recipient_bank, amount]):
                    return {"success": False, "error": "Missing transfer details"}
                
                # Import and execute transfer
                from functions.transfer_functions import send_money
                result = await send_money(
                    chat_id=chat_id,
                    account_number=recipient_account,
                    bank_name=recipient_bank,
                    amount=float(amount),
                    narration=reason
                )
                
                # If transfer successful, prepare beneficiary save prompt
                if result.get("success"):
                    from utils.supabase_beneficiary_service import beneficiary_service
                    if beneficiary_service:
                        save_prompt = beneficiary_service.create_save_prompt(
                            beneficiary_name=result.get("recipient_name", "Recipient"),
                            bank_name=recipient_bank,
                            account_number=recipient_account
                        )
                        result["save_beneficiary_prompt"] = save_prompt
                
                return result
            
            elif function_name == "get_user_beneficiaries":
                # Get user's integer ID from chat_id (convert to int for DB compatibility)
                user_id = await self._get_user_id_from_chat_id(chat_id)
                if not user_id:
                    return {"success": False, "error": "User not found"}
                
                from utils.supabase_beneficiary_service import beneficiary_service
                if beneficiary_service:
                    beneficiaries = await beneficiary_service.get_user_beneficiaries(user_id)
                    
                    if not beneficiaries:
                        return {"success": True, "message": "📱 **Your Saved Recipients**\n\nYou haven't saved any recipients yet.\n\nAfter your next transfer, I'll ask if you want to save the recipient for quick future transfers! 😊"}
                    
                    response = "📱 **Your Saved Recipients**\n\n"
                    for i, beneficiary in enumerate(beneficiaries, 1):
                        response += f"{i}. **{beneficiary.get('nickname', beneficiary.get('beneficiary_name', 'Unknown'))}**\n"
                        response += f"   {beneficiary.get('beneficiary_name', 'N/A')} - {beneficiary.get('bank_name', 'N/A')}\n"
                        response += f"   Account: {beneficiary.get('account_number', 'N/A')}\n\n"
                    
                    response += "💰 To send money, just say:\n"
                    response += "• \"Send 5000 to John\"\n"
                    response += "• \"Transfer 2000 to Mom\"\n"
                    response += "• Or just mention their name!"
                    
                    return {"success": True, "message": response}
                else:
                    return {"success": False, "error": "Beneficiary service not available"}
            
            elif function_name == "save_beneficiary":
                # Get user's integer ID from chat_id
                user_id = await self._get_user_id_from_chat_id(chat_id)
                if not user_id:
                    return {"success": False, "error": "User not found"}
                
                from utils.supabase_beneficiary_service import beneficiary_service
                if beneficiary_service:
                    success = await beneficiary_service.save_beneficiary(
                        user_id=user_id,
                        beneficiary_name=function_args.get("account_holder_name"),  # Real name
                        account_number=function_args.get("account_number"),
                        bank_code=function_args.get("bank_name"),  # Use bank_name as code for now
                        bank_name=function_args.get("bank_name"),
                        nickname=function_args.get("name")  # The friendly name user gave
                    )
                    
                    if success:
                        return {"success": True, "message": f"✅ Successfully saved {function_args.get('name')} as a beneficiary!"}
                    else:
                        return {"success": False, "error": "Failed to save beneficiary"}
                else:
                    return {"success": False, "error": "Beneficiary service not available"}
            
            elif function_name == "find_beneficiary_by_name":
                # Get user's integer ID from chat_id
                user_id = await self._get_user_id_from_chat_id(chat_id)
                if not user_id:
                    return {"success": False, "error": "User not found"}
                
                from utils.supabase_beneficiary_service import beneficiary_service
                if beneficiary_service:
                    beneficiary = await beneficiary_service.find_beneficiary_by_name(
                        user_id=user_id,
                        search_term=function_args.get("name")
                    )
                    
                    if beneficiary:
                        return {
                            "success": True, 
                            "found": True,
                            "beneficiary": beneficiary,
                            "message": f"Found {beneficiary.get('nickname', beneficiary.get('beneficiary_name'))}: {beneficiary.get('beneficiary_name')} - {beneficiary.get('bank_name')} - {beneficiary.get('account_number')}"
                        }
                    else:
                        return {
                            "success": True,
                            "found": False,
                            "message": f"No saved recipient found with name '{function_args.get('name')}'"
                        }
                else:
                    return {"success": False, "error": "Beneficiary service not available"}
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"❌ Background function execution error: {e}")
            return {"error": str(e)}
    
    async def _get_user_uuid_from_chat_id(self, chat_id: str) -> Optional[str]:
        """Get user's UUID from telegram chat_id"""
        try:
            result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user UUID: {e}")
            return None

    async def _get_user_id_from_chat_id(self, chat_id: str) -> Optional[int]:
        """Get user's integer ID from telegram chat_id (for beneficiary service compatibility)"""
        try:
            # First try to get from the users table (if it has integer IDs)
            result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            if result.data:
                user_id = result.data[0]["id"]
                # Convert to int if it's a string
                if isinstance(user_id, str):
                    return int(user_id)
                return user_id
                
            # Fallback: use chat_id directly as integer
            return int(chat_id)
        except Exception as e:
            logger.error(f"❌ Error getting user integer ID: {e}")
            # Fallback: use chat_id directly
            try:
                return int(chat_id)
            except:
                return None

# Global background task manager
background_manager = BackgroundTaskManager()

class SofiAssistant:
    """OpenAI Assistant integration for Sofi AI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.money_service = SofiMoneyTransferService()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.assistant_id = None
        self._create_or_get_assistant()
        logger.info("✅ Sofi Assistant initialized")
    
    def _create_or_get_assistant(self):
        """Create or retrieve the Sofi AI assistant"""
        try:
            # Try to get existing assistant
            assistants = self.client.beta.assistants.list()
            
            for assistant in assistants.data:
                if assistant.name == "Sofi AI Banking Assistant":
                    self.assistant_id = assistant.id
                    logger.info(f"✅ Found existing assistant: {self.assistant_id}")
                    
                    # Update the assistant with latest instructions and functions
                    self.client.beta.assistants.update(
                        assistant_id=self.assistant_id,
                        instructions=SOFI_MONEY_INSTRUCTIONS,
                        tools=SOFI_MONEY_FUNCTIONS
                    )
                    logger.info(f"🔄 Updated assistant instructions and functions")
                    return
            
            # Create new assistant if not found
            assistant = self.client.beta.assistants.create(
                name="Sofi AI Banking Assistant",
                instructions=SOFI_MONEY_INSTRUCTIONS,
                tools=SOFI_MONEY_FUNCTIONS,
                model="gpt-4o"  # Use the correct model name
            )
            
            self.assistant_id = assistant.id
            logger.info(f"✅ Created new assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating assistant: {e}")
            raise
    
    async def process_message(self, chat_id: str, message: str, user_data: Dict = None) -> Tuple[str, Dict]:
        """
        🚀 ULTRA-FAST process message with immediate real results
        
        Target: < 0.1 seconds response time with REAL DATA
        """
        try:
            start_time = time.time()
            logger.info(f"⚡ FAST processing message from {chat_id}: {message[:50]}...")
            
            # STEP 1: Check for instant executable commands first
            instant_result = await self._try_instant_execution(chat_id, message, user_data)
            if instant_result:
                elapsed = time.time() - start_time
                logger.info(f"⚡ INSTANT real result in {elapsed*1000:.1f}ms for {chat_id}")
                return instant_result, {}
            
            # STEP 2: Generate acknowledgment for complex requests
            quick_response = self._generate_instant_response(message, user_data)
            
            # STEP 3: Start background processing (non-blocking)
            asyncio.create_task(self._start_background_processing(chat_id, message, user_data))
            
            elapsed = time.time() - start_time
            logger.info(f"⚡ INSTANT response generated in {elapsed*1000:.1f}ms for {chat_id}")
            
            return quick_response, {}
            
        except Exception as e:
            logger.error(f"❌ Error in fast processing: {e}")
            return "I'm here to help! Let me process that for you.", {}
    
    async def _try_instant_execution(self, chat_id: str, message: str, user_data: Dict = None) -> Optional[str]:
        """Execute simple commands instantly with real data"""
        message_lower = message.lower().strip()
        
        # Balance check patterns - execute immediately
        balance_patterns = ['balance', 'my balance', 'check balance', 'wallet', 'how much', 'account balance']
        if any(pattern in message_lower for pattern in balance_patterns):
            try:
                # Get real balance instantly
                from functions.balance_functions import check_balance
                result = await check_balance(chat_id=chat_id)
                
                if result and result.get("success"):
                    balance = result.get("balance", 0)
                    return f"💰 Your current wallet balance is ₦{balance:,.2f}."
                elif result and result.get("error"):
                    return f"❌ {result.get('error')}"
                else:
                    return "❌ Unable to fetch your balance right now. Please try again."
                    
            except Exception as e:
                logger.error(f"❌ Instant balance check error: {e}")
                return "❌ Unable to check balance right now. Please try again."
        
        # PIN status check patterns - execute immediately  
        pin_check_patterns = ['pin status', 'do i have pin', 'pin set', 'my pin']
        if any(pattern in message_lower for pattern in pin_check_patterns):
            try:
                # Check if user has PIN set
                result = self.supabase.table("users").select("pin_hash").eq("telegram_chat_id", chat_id).execute()
                
                if result.data and result.data[0].get("pin_hash"):
                    return "🔐 Your transaction PIN is already set and secure."
                else:
                    return "🔓 You haven't set a transaction PIN yet. Would you like to create one?"
                    
            except Exception as e:
                logger.error(f"❌ Instant PIN check error: {e}")
                return "❌ Unable to check PIN status right now."
        
        # Virtual account info - execute immediately
        account_patterns = ['my account', 'account details', 'account number', 'virtual account']
        if any(pattern in message_lower for pattern in account_patterns):
            try:
                from functions.account_functions import get_virtual_account
                result = await get_virtual_account(chat_id=chat_id)
                
                if result and result.get("success"):
                    account_number = result.get("account_number")
                    bank_name = result.get("bank_name", "Providus Bank")
                    return f"🏦 Your virtual account:\n📞 {account_number}\n🏛️ {bank_name}"
                else:
                    return "❌ Unable to fetch account details. Please complete onboarding first."
                    
            except Exception as e:
                logger.error(f"❌ Instant account check error: {e}")
                return "❌ Unable to fetch account details right now."
        
        # No instant execution available
        return None
    
    def _generate_instant_response(self, message: str, user_data: Dict = None) -> str:
        """Generate precise instant responses for complex requests only"""
        message_lower = message.lower().strip()
        user_name = user_data.get('first_name', 'there') if user_data else 'there'
        
        # Simple greetings - provide instant friendly response (helps with double messages)
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in message_lower for pattern in greeting_patterns) and len(message_lower) < 20:
            # Vary responses to make double messages feel natural
            import random
            responses = [
                f"Hi {user_name}! How can I help you today? 😊",
                f"Hello {user_name}! What can I do for you?",
                f"Hey {user_name}! I'm here to help with your banking needs.",
                f"Hi there {user_name}! Ready to assist you! 💸"
            ]
            return random.choice(responses)
        
        # Transfer patterns - these need background processing
        elif any(word in message_lower for word in ['send', 'transfer', 'pay']) and any(word in message_lower for word in ['₦', 'naira', '1000', '5000', '10000']):
            # Only acknowledge transfers that require PIN/verification
            return "💸 Processing your transfer request..."
        
        # Airtime patterns - these need background processing
        elif any(word in message_lower for word in ['airtime', 'data', 'recharge']) and any(word in message_lower for word in ['₦', '100', '200', '500', '1000']):
            return "📱 Processing your airtime purchase..."
        
        # PIN setup patterns - these need background processing
        elif any(word in message_lower for word in ['set pin', 'create pin', 'new pin', 'change pin']):
            return "🔐 I'll help you set up your secure PIN..."
        
        # Complex transfer queries - need background processing
        elif 'transfer' in message_lower and any(word in message_lower for word in ['how', 'can', 'to someone', 'my friend']):
            return "💸 Let me guide you through the transfer process..."
        
        # Generic requests that need AI processing
        else:
            return f"🤖 Processing your request, {user_name}..."
    
    async def _start_background_processing(self, chat_id: str, message: str, user_data: Dict = None):
        """Start the actual OpenAI processing in background"""
        try:
            # Prevent duplicate processing with user-level locking
            if chat_id in background_manager.active_tasks:
                logger.info(f"🔄 Background task already running for {chat_id}")
                return
            
            background_manager.active_tasks[chat_id] = time.time()
            
            # Get or create thread
            thread_id = await self._get_or_create_thread(chat_id)
            
            # AGGRESSIVE FIX: Handle active runs properly
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                # Check for active runs
                active_run_id = self._check_active_run(thread_id)
                
                if active_run_id:
                    logger.info(f"🛑 Active run {active_run_id} found, attempting to handle it (attempt {retry_count + 1})")
                    
                    # Try to cancel the active run
                    try:
                        self.client.beta.threads.runs.cancel(
                            thread_id=thread_id,
                            run_id=active_run_id
                        )
                        logger.info(f"✅ Cancelled active run {active_run_id}")
                        
                        # Wait for cancellation to take effect
                        await asyncio.sleep(1.0)
                        
                        # Verify cancellation worked
                        run_status = self.client.beta.threads.runs.retrieve(
                            thread_id=thread_id,
                            run_id=active_run_id
                        )
                        
                        if run_status.status in ["cancelled", "completed", "failed", "expired"]:
                            logger.info(f"✅ Run {active_run_id} is now {run_status.status}")
                            break
                        else:
                            logger.warning(f"⚠️ Run {active_run_id} still active with status {run_status.status}")
                            
                    except Exception as cancel_error:
                        logger.error(f"❌ Failed to cancel run {active_run_id}: {cancel_error}")
                    
                    retry_count += 1
                    if retry_count < max_retries:
                        await asyncio.sleep(0.5)  # Wait before retry
                else:
                    # No active run, we can proceed
                    break
            
            # If we still have an active run after all retries, create a new thread
            if retry_count >= max_retries:
                logger.warning(f"⚠️ Could not resolve active run after {max_retries} attempts, creating new thread")
                # Create a completely new thread to bypass the stuck run
                new_thread = self.client.beta.threads.create()
                thread_id = new_thread.id
                
                # Update user's thread ID in database
                try:
                    self.supabase.table("users").update({
                        "assistant_thread_id": thread_id,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("telegram_chat_id", chat_id).execute()
                    logger.info(f"✅ Created new thread {thread_id} for user {chat_id}")
                except Exception as db_error:
                    logger.error(f"❌ Failed to update thread ID in database: {db_error}")
            
            # Add user context to the message
            context_message = self._prepare_context_message(message, chat_id, user_data)
            
            # Create message (should work now)
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=context_message
                )
                logger.info(f"✅ Message added to thread {thread_id}")
            except Exception as msg_error:
                logger.error(f"❌ Failed to create message: {msg_error}")
                # Last resort: send error message to user
                await background_manager.send_telegram_message(chat_id, 
                    "❌ I'm experiencing technical difficulties. Please try again in a moment.")
                return
            
            # Create run (should work now)
            try:
                run = self.client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant_id
                )
                logger.info(f"✅ Run {run.id} created for thread {thread_id}")
            except Exception as run_error:
                logger.error(f"❌ Failed to create run: {run_error}")
                await background_manager.send_telegram_message(chat_id, 
                    "❌ I'm experiencing technical difficulties. Please try again in a moment.")
                return
            
            # Start background completion processing
            await background_manager.process_openai_run_background(
                run, thread_id, chat_id, self.client, self.money_service
            )
            
        except Exception as e:
            logger.error(f"❌ Background processing setup error: {e}")
            await background_manager.send_telegram_message(chat_id, 
                "❌ Sorry, I encountered an issue. Please try again.")
        finally:
            # Always clean up our task tracking
            background_manager.active_tasks.pop(chat_id, None)
    
    async def process_telegram_message(self, chat_id: str, message: str, user_data: Dict = None, 
                                     chat_type: str = 'private', group_id: str = None, 
                                     is_admin: bool = False, new_member: Dict = None) -> Tuple[str, Dict]:
        """
        🚀 ULTRA-FAST Telegram message processing with instant responses
        """
        # Group handling (instant response)
        if chat_type in ['group', 'supergroup']:
            # Welcome new member logic (instant)
            if new_member:
                welcome_text = f"👋 Welcome @{new_member.get('username', 'new_user')} to the group! Please check your private messages to complete onboarding and claim your rewards."
                function_data = {
                    'group_admin_action': 'welcome_new_member',
                    'private_message': f"Hi @{new_member.get('username', 'new_user')}, welcome to Sofi!\nTo start using your account and claim rewards, please complete onboarding here."
                }
                return welcome_text, function_data
            
            # Only respond if mentioned (instant)
            if 'sofi' not in message.lower() and '@getsofi_bot' not in message.lower():
                return None, {}
            
            # Admin commands (instant responses)
            if is_admin:
                if 'kick' in message.lower():
                    return "🚫 User kicked (simulated).", {'group_admin_action': 'kick'}
                elif 'promote' in message.lower():
                    return "🎖️ User promoted to admin (simulated).", {'group_admin_action': 'promote'}
                elif 'announce' in message.lower():
                    return "📢 Announcement sent to group (simulated).", {'group_admin_action': 'announce'}
                elif 'update' in message.lower():
                    return "🔄 Group update sent (simulated).", {'group_admin_action': 'update'}
                elif 'tag' in message.lower():
                    return "🔔 Tagging all members: @all (simulated).", {'group_admin_action': 'tag_all'}
                else:
                    return "👋 Hello group! Sofi is here to help.", {'group_admin_action': 'greet'}
            else:
                return "👋 Hi! Sofi is here. Mention me for group admin actions.", {'group_admin_action': 'greet'}
        
        # Private chat: use ultra-fast processing
        return await self.process_message(chat_id, message, user_data)
    
    def _check_active_run(self, thread_id: str) -> Optional[str]:
        """Check if thread has an active run"""
        try:
            runs = self.client.beta.threads.runs.list(
                thread_id=thread_id,
                limit=1,
                order="desc"
            )
            
            if runs.data:
                latest_run = runs.data[0]
                if latest_run.status in ["queued", "in_progress", "requires_action"]:
                    logger.info(f"🔍 Found active run {latest_run.id} with status {latest_run.status}")
                    return latest_run.id
            
            return None
        except Exception as e:
            logger.error(f"❌ Error checking active run: {e}")
            return None
    
    async def _wait_for_run_completion(self, thread_id: str, run_id: str, max_wait_seconds: int = 3) -> bool:
        """Wait for run to complete with timeout"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_seconds:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run.status in ["completed", "failed", "cancelled", "expired"]:
                    logger.info(f"✅ Run {run_id} completed with status {run.status}")
                    return True
                
                # Short wait before checking again
                await asyncio.sleep(0.5)
            
            logger.info(f"⏰ Run {run_id} still active after {max_wait_seconds}s timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Error waiting for run completion: {e}")
            return False

    async def _get_or_create_thread(self, chat_id: str) -> str:
        """Get existing thread or create new one for user"""
        try:
            # Check if user has existing thread in database (try both column names)
            result = self.supabase.table("users").select("assistant_thread_id").eq("telegram_chat_id", chat_id).execute()
            
            if result.data and result.data[0].get("assistant_thread_id"):
                thread_id = result.data[0]["assistant_thread_id"]
                logger.info(f"✅ Found existing thread {thread_id} for user {chat_id}")
                return thread_id
            
            # Create new thread
            thread = self.client.beta.threads.create()
            
            # Update user record with thread ID
            try:
                self.supabase.table("users").update({
                    "assistant_thread_id": thread.id,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_chat_id", chat_id).execute()
                logger.info(f"✅ Created and saved new thread {thread.id} for user {chat_id}")
            except Exception as db_error:
                logger.warning(f"⚠️ Could not save thread ID to database: {db_error}")
                # Continue anyway with the thread
            
            return thread.id
            
        except Exception as e:
            logger.error(f"❌ Error managing thread: {e}")
            # Fallback: create temporary thread
            thread = self.client.beta.threads.create()
            logger.info(f"✅ Created fallback thread {thread.id} for user {chat_id}")
            return thread.id
    
    def _prepare_context_message(self, message: str, chat_id: str, user_data: Dict = None) -> str:
        """Prepare message with user context"""
        context = f"User ID: {chat_id}\n"
        
        if user_data:
            if user_data.get("first_name"):
                context += f"User Name: {user_data['first_name']}\n"
            if user_data.get("virtual_account"):
                context += f"Has Virtual Account: Yes\n"
        
        context += f"Message: {message}"
        return context

# Global assistant instance
_assistant_instance = None

def get_assistant() -> SofiAssistant:
    """Get or create the global assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = SofiAssistant()
    return _assistant_instance
