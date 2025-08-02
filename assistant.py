"""
SOFI AI WHATSAPP ASSISTANT INTEGRATION
=====================================
OpenAI Assistant integration with WhatsApp and money transfer capabilities
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
        self.whatsapp_access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
    async def send_whatsapp_message(self, phone_number: str, message: str):
        """Send message via WhatsApp Cloud API"""
        try:
            import requests
            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.whatsapp_access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            # Use background thread for HTTP request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(self.executor, 
                lambda: requests.post(url, json=payload, headers=headers, timeout=5))
            
            if response.status_code == 200:
                logger.info(f"✅ Sent completion message to WhatsApp {phone_number}")
            else:
                logger.error(f"❌ WhatsApp API error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
    
    async def _send_platform_message(self, whatsapp_number: str, platform: str, message: str):
        """Send message to WhatsApp (platform parameter kept for compatibility)"""
        try:
            await self.send_whatsapp_message(whatsapp_number, message)
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
    
    async def process_openai_run_background(self, run, thread_id: str, phone_number: str, 
                                          assistant_client, money_service):
        """Process OpenAI run in background without blocking"""
        try:
            logger.info(f"🚀 Starting background processing for WhatsApp {phone_number}")
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
                    await self._send_platform_message(phone_number, "whatsapp",
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
                        logger.info(f"⚡ Background processing completed in {elapsed:.2f}s for WhatsApp {phone_number}")
                        await self._send_platform_message(phone_number, "whatsapp", response_text)
                    
                    # Clean up
                    self.active_tasks.pop(phone_number, None)
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
                                function_name, function_args, phone_number, money_service)
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
                        await self._send_platform_message(phone_number, "whatsapp",
                            "❌ Sorry, I encountered an issue processing your request.")
                        return
                
                elif run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"❌ Background run failed with status: {run.status}")
                    await self._send_platform_message(phone_number, "whatsapp",
                        f"❌ Sorry, I encountered an error: {run.status}")
                    self.active_tasks.pop(phone_number, None)
                    return
                
                # Non-blocking wait
                await asyncio.sleep(0.5)  # Check every 500ms instead of 1s
            
            # Timeout fallback
            logger.warning(f"⏰ Background processing timeout for WhatsApp {phone_number}")
            await self._send_platform_message(phone_number, "whatsapp",
                "⏰ Your request is taking longer than expected. I'll continue processing and update you shortly.")
            
        except Exception as e:
            logger.error(f"❌ Background processing error for WhatsApp {phone_number}: {e}")
            await self._send_platform_message(phone_number, "whatsapp",
                "❌ Sorry, I encountered an unexpected error. Please try again.")
        finally:
            # Always clean up
            self.active_tasks.pop(phone_number, None)
    
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
                                         phone_number: str, money_service) -> Dict[str, Any]:
        """Execute function in background thread"""
        try:
            # All the same function execution logic, but in background
            if function_name == "verify_account_name":
                return await money_service.verify_account_name(
                    account_number=function_args.get("account_number"),
                    bank_code=function_args.get("bank_name") or function_args.get("bank_code")
                )
            elif function_name == "check_balance":
                return await money_service.check_user_balance(whatsapp_number=phone_number)
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
                    whatsapp_number=phone_number,
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
                # Get user's integer ID from phone_number
                user_id = await self._get_user_id_from_phone_number(phone_number)
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
                # Get user's integer ID from phone_number
                user_id = await self._get_user_id_from_phone_number(phone_number)
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
                # Get user's integer ID from phone_number
                user_id = await self._get_user_id_from_phone_number(phone_number)
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
    
    async def _get_user_uuid_from_phone_number(self, phone_number: str) -> Optional[str]:
        """Get user's UUID from WhatsApp phone number"""
        try:
            result = self.supabase.table("users").select("id").eq("whatsapp_number", str(phone_number)).execute()
            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user UUID: {e}")
            return None

    async def _get_user_id_from_phone_number(self, phone_number: str) -> Optional[int]:
        """Get user's integer ID from WhatsApp phone number (for beneficiary service compatibility)"""
        try:
            # First try to get from the users table (if it has integer IDs)
            result = self.supabase.table("users").select("id").eq("whatsapp_number", str(phone_number)).execute()
            if result.data:
                user_id = result.data[0]["id"]
                # Convert to int if it's a string
                if isinstance(user_id, str):
                    return int(user_id)
                return user_id
                
            # Fallback: use phone_number hash as integer
            import hashlib
            return int(hashlib.md5(phone_number.encode()).hexdigest()[:8], 16)
        except Exception as e:
            logger.error(f"❌ Error getting user integer ID: {e}")
            # Fallback: use phone_number hash as integer
            try:
                import hashlib
                return int(hashlib.md5(phone_number.encode()).hexdigest()[:8], 16)
            except:
                return None

# Global background task manager
background_manager = BackgroundTaskManager()

class SofiAssistant:
    """OpenAI Assistant integration for Sofi AI WhatsApp"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.money_service = SofiMoneyTransferService()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.assistant_id = None
        self._create_or_get_assistant()
        logger.info("✅ Sofi WhatsApp Assistant initialized")
    
    def _create_or_get_assistant(self):
        """Create or retrieve the Sofi AI assistant"""
        try:
            # Try to get existing assistant
            assistants = self.client.beta.assistants.list()
            
            for assistant in assistants.data:
                if assistant.name == "Sofi AI WhatsApp Banking Assistant":
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
                name="Sofi AI WhatsApp Banking Assistant",
                instructions=SOFI_MONEY_INSTRUCTIONS,
                tools=SOFI_MONEY_FUNCTIONS,
                model="gpt-3.5-turbo"  # Use GPT-3.5-turbo for cost optimization
            )
            
            self.assistant_id = assistant.id
            logger.info(f"✅ Created new assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating assistant: {e}")
            raise
    
    async def process_message(self, phone_number: str, message: str, user_data: Dict = None) -> Tuple[str, Dict]:
        """
        🚀 ULTRA-FAST process WhatsApp message with immediate real results
        
        Target: < 0.1 seconds response time with REAL DATA
        WhatsApp-only processing
        """
        try:
            start_time = time.time()
            logger.info(f"⚡ FAST processing WhatsApp message from {phone_number}: {message[:50]}...")
            
            # STEP 1: Check for instant executable commands first
            instant_result = await self._try_instant_execution(phone_number, message, user_data)
            if instant_result:
                elapsed = time.time() - start_time
                logger.info(f"⚡ INSTANT real result in {elapsed*1000:.1f}ms for {phone_number}")
                return instant_result, {}
            
            # STEP 2: Generate acknowledgment for complex requests
            quick_response = self._generate_instant_response(message, user_data)
            
            # STEP 3: Start background processing (non-blocking)
            asyncio.create_task(self._start_background_processing(phone_number, message, user_data))
            
            elapsed = time.time() - start_time
            logger.info(f"⚡ INSTANT response generated in {elapsed*1000:.1f}ms for {phone_number}")
            
            return quick_response, {}
            
        except Exception as e:
            logger.error(f"❌ Error in fast processing: {e}")
            return "I'm here to help! Let me process that for you.", {}
    
    async def _try_instant_execution(self, phone_number: str, message: str, user_data: Dict = None) -> Optional[str]:
        """Execute simple commands instantly with real data"""
        message_lower = message.lower().strip()
        
        # Balance check patterns - execute immediately
        balance_patterns = ['balance', 'my balance', 'check balance', 'wallet', 'how much', 'account balance']
        if any(pattern in message_lower for pattern in balance_patterns):
            try:
                # Get real balance instantly
                from functions.balance_functions import check_balance
                result = await check_balance(whatsapp_number=phone_number)
                
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
                # WhatsApp user lookup for PIN check
                result = self.supabase.table("users").select("pin_hash").eq("whatsapp_number", phone_number).execute()
                
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
                result = await get_virtual_account(whatsapp_number=phone_number)
                
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
    
    async def _start_background_processing(self, phone_number: str, message: str, user_data: Dict = None):
        """Start the actual OpenAI processing in background"""
        try:
            # 🚀 ENHANCED FIX: Prevent duplicate processing with better user-level locking
            if phone_number in background_manager.active_tasks:
                logger.info(f"🔄 Background task already running for {phone_number} - sending duplicate message response")
                # For double messages, send the same type of response instead of ignoring
                await background_manager._send_platform_message(phone_number, "whatsapp",
                    "Hi there! How can I help you today? 😊")
                return
            
            background_manager.active_tasks[phone_number] = time.time()
            
            # Get or create thread (fast)
            thread_id = await self._get_or_create_thread(phone_number)
            
            # 🚀 ENHANCED FIX: Better active run detection with cancellation
            active_run_id = self._check_active_run(thread_id)
            
            if active_run_id:
                logger.info(f"⏳ Thread {thread_id} has active run {active_run_id}")
                
                # Try to cancel the active run if it's stuck
                try:
                    self.client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=active_run_id
                    )
                    logger.info(f"🛑 Cancelled active run {active_run_id}")
                    # Wait a moment for cancellation to take effect
                    await asyncio.sleep(0.5)
                except Exception as cancel_error:
                    logger.warning(f"⚠️ Could not cancel run {active_run_id}: {cancel_error}")
                
                # Try to wait for completion (short timeout)
                completed = await self._wait_for_run_completion(thread_id, active_run_id, max_wait_seconds=2)
                
                if not completed:
                    # Run is still active, send friendly duplicate response for double messages
                    user_name = user_data.get('first_name', 'there') if user_data else 'there'
                    await background_manager._send_platform_message(phone_number, "whatsapp",
                        f"Hi {user_name}! I'm still working on your previous message. How can I help you today? 😊")
                    # Clean up our task
                    if phone_number in background_manager.active_tasks:
                        del background_manager.active_tasks[phone_number]
                    return
                
                logger.info(f"✅ Previous run completed, proceeding with new message")
            
            # Add small delay to prevent race conditions with rapid double messages
            await asyncio.sleep(0.1)
            
            # Double-check for active runs one more time after delay
            active_run_id_recheck = self._check_active_run(thread_id)
            if active_run_id_recheck:
                logger.info(f"⏳ Race condition detected: Found active run {active_run_id_recheck} after delay")
                user_name = user_data.get('first_name', 'there') if user_data else 'there'
                await background_manager._send_platform_message(phone_number, "whatsapp",
                    f"Hi {user_name}! How can I help you today? 😊")
                if phone_number in background_manager.active_tasks:
                    del background_manager.active_tasks[phone_number]
                return
            
            # Add user context to the message
            context_message = self._prepare_context_message(message, phone_number, user_data)
            
            # 🚀 ENHANCED FIX: Safe message creation with better double message handling
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=context_message
                )
            except Exception as msg_error:
                if "while a run" in str(msg_error) and "is active" in str(msg_error):
                    logger.warning(f"⚠️ Message creation failed due to active run: {msg_error}")
                    user_name = user_data.get('first_name', 'there') if user_data else 'there'
                    await background_manager._send_platform_message(phone_number, "whatsapp",
                        f"Hi {user_name}! How can I help you today? 😊")
                    # Clean up our task
                    if phone_number in background_manager.active_tasks:
                        del background_manager.active_tasks[phone_number]
                    return
                else:
                    raise msg_error
            
            # 🚀 ENHANCED FIX: Safe run creation with better double message handling
            try:
                run = self.client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant_id
                )
            except Exception as run_error:
                if "while a run" in str(run_error) and "is active" in str(run_error):
                    logger.warning(f"⚠️ Run creation failed due to active run: {run_error}")
                    user_name = user_data.get('first_name', 'there') if user_data else 'there'
                    await background_manager._send_platform_message(phone_number, "whatsapp",
                        f"Hi {user_name}! How can I help you today? 😊")
                    # Clean up our task
                    if phone_number in background_manager.active_tasks:
                        del background_manager.active_tasks[phone_number]
                    return
                else:
                    raise run_error
            
            # Start background completion processing
            await background_manager.process_openai_run_background(
                run, thread_id, phone_number, self.client, self.money_service
            )
            
        except Exception as e:
            logger.error(f"❌ Background processing setup error: {e}")
            await background_manager._send_platform_message(phone_number, "whatsapp",
                "❌ Sorry, I encountered an issue. Please try again.")
            # Clean up our task
            if phone_number in background_manager.active_tasks:
                del background_manager.active_tasks[phone_number]
        finally:
            # Ensure we clean up the task tracking
            if phone_number in background_manager.active_tasks:
                del background_manager.active_tasks[phone_number]
    
    async def _get_or_create_thread(self, phone_number: str) -> str:
        """Get existing thread or create new one for user"""
        try:
            # Check if user has existing thread in database based on WhatsApp number
            result = self.supabase.table("users").select("assistant_thread_id").eq("whatsapp_number", phone_number).execute()
            
            if result.data and result.data[0].get("assistant_thread_id"):
                logger.info(f"🔍 Found existing thread for WhatsApp {phone_number}: {result.data[0]['assistant_thread_id']}")
                return result.data[0]["assistant_thread_id"]
            
            # Create new thread
            thread = self.client.beta.threads.create()
            
            # Update user record with thread ID based on WhatsApp number
            self.supabase.table("users").update({
                "assistant_thread_id": thread.id,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("whatsapp_number", phone_number).execute()
            
            logger.info(f"✅ Created new thread {thread.id} for WhatsApp user {phone_number}")
            return thread.id
            
        except Exception as e:
            logger.error(f"❌ Error managing thread for WhatsApp {phone_number}: {e}")
            # Fallback: create temporary thread
            thread = self.client.beta.threads.create()
            return thread.id
    
    def _prepare_context_message(self, message: str, phone_number: str, user_data: Dict = None) -> str:
        """Prepare message with user context"""
        context = f"WhatsApp Number: {phone_number}\n"
        
        if user_data:
            if user_data.get("first_name"):
                context += f"User Name: {user_data['first_name']}\n"
            if user_data.get("virtual_account"):
                context += f"Has Virtual Account: Yes\n"
        
        context += f"Message: {message}"
        return context
    
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

# Global assistant instance
_assistant_instance = None

def get_assistant() -> SofiAssistant:
    """Get or create the global assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = SofiAssistant()
    return _assistant_instance
