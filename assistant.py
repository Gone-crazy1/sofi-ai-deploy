"""
SOFI AI ASSISTANT INTEGRATION
=============================
OpenAI Assistant integration with money transfer capabilities
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from sofi_money_functions import SofiMoneyTransferService
from sofi_assistant_functions import SOFI_MONEY_FUNCTIONS, SOFI_MONEY_INSTRUCTIONS
from supabase import create_client

load_dotenv()

logger = logging.getLogger(__name__)

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
                    logger.info(f"✅ Using existing assistant: {self.assistant_id}")
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
        Process user message through OpenAI Assistant
        
        Returns:
            Tuple of (response_text, function_data)
        """
        try:
            logger.info(f"🤖 Processing message from {chat_id}: {message[:50]}...")
            
            # Get or create thread for this user
            thread_id = await self._get_or_create_thread(chat_id)
            
            # Add user context to the message
            context_message = self._prepare_context_message(message, chat_id, user_data)
            
            # Create message in thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=context_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion and handle function calls
            response_text, function_data = await self._wait_for_completion(run, thread_id, chat_id)
            
            return response_text, function_data
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}", {}
    
    async def _get_or_create_thread(self, chat_id: str) -> str:
        """Get existing thread or create new one for user"""
        try:
            # Check if user has existing thread in database
            result = self.supabase.table("users").select("assistant_thread_id").eq("telegram_id", chat_id).execute()
            
            if result.data and result.data[0].get("assistant_thread_id"):
                return result.data[0]["assistant_thread_id"]
            
            # Create new thread
            thread = self.client.beta.threads.create()
            
            # Update user record with thread ID
            self.supabase.table("users").update({
                "assistant_thread_id": thread.id,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("telegram_id", chat_id).execute()
            
            logger.info(f"✅ Created new thread {thread.id} for user {chat_id}")
            return thread.id
            
        except Exception as e:
            logger.error(f"❌ Error managing thread: {e}")
            # Fallback: create temporary thread
            thread = self.client.beta.threads.create()
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
    
    async def _wait_for_completion(self, run, thread_id: str, chat_id: str) -> Tuple[str, Dict]:
        """Wait for assistant completion and handle function calls"""
        function_data = {}
        
        while True:
            # Check run status
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run.status == "completed":
                # Get the response
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                response = messages.data[0].content[0].text.value
                return response, function_data
            
            elif run.status == "requires_action":
                # Handle function calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"🔧 Executing function: {function_name}")
                    
                    # Execute the function
                    try:
                        result = await self._execute_function(function_name, function_args, chat_id)
                        function_data[function_name] = result
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    except Exception as e:
                        logger.error(f"❌ Function execution error: {e}")
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"error": str(e)})
                        })
                
                # Submit tool outputs
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            elif run.status in ["failed", "cancelled", "expired"]:
                logger.error(f"❌ Run failed with status: {run.status}")
                return f"Sorry, I encountered an error: {run.status}", function_data
            
            # Wait before checking again
            await asyncio.sleep(1)
    
    async def _execute_function(self, function_name: str, function_args: Dict, chat_id: str) -> Dict[str, Any]:
        """Execute assistant function calls"""
        try:
            logger.info(f"🔧 Function called: {function_name} with args: {function_args}")
            
            if function_name == "verify_account_name":
                # Use the correct method from money service
                from sofi_money_functions import SofiMoneyTransferService
                service = SofiMoneyTransferService()
                return await service.verify_account_name(
                    account_number=function_args.get("account_number"),
                    bank_code=function_args.get("bank_name") or function_args.get("bank_code")
                )
            
            elif function_name == "send_money":
                # For transfers, we need to initiate PIN entry flow instead of expecting PIN in args
                logger.info(f"🔧 send_money called with args: {function_args}")
                logger.info(f"🔧 chat_id: {chat_id}")
                
                # Extract parameters (supporting both old and new formats for compatibility)
                recipient_account = function_args.get("account_number") or function_args.get("recipient_account")
                recipient_bank = function_args.get("bank_name") or function_args.get("recipient_bank") 
                amount = function_args.get("amount")
                reason = function_args.get("narration") or function_args.get("reason", "Transfer via Sofi AI")
                
                # Validate we have the required data
                if not recipient_account:
                    logger.error(f"❌ Missing recipient account number")
                    return {"success": False, "error": "Missing recipient account number"}
                
                if not recipient_bank:
                    logger.error(f"❌ Missing recipient bank")
                    return {"success": False, "error": "Missing recipient bank"}
                
                if not amount:
                    logger.error(f"❌ Missing transfer amount")
                    return {"success": False, "error": "Missing transfer amount"}
                
                logger.info(f"✅ Parsed transfer details: ₦{amount} to {recipient_account} at {recipient_bank}")
                
                # Check if PIN is provided (for direct calls) or if we need to start PIN entry
                if "pin" in function_args and function_args["pin"]:
                    # Direct PIN provided - execute transfer immediately
                    from functions.transfer_functions import send_money
                    
                    return await send_money(
                        chat_id=chat_id,
                        account_number=recipient_account,  # Use new parameter name
                        bank_name=recipient_bank,          # Use new parameter name
                        amount=float(amount),
                        pin=function_args["pin"],
                        narration=reason
                    )
                else:
                    # No PIN provided - start inline PIN entry flow
                    from functions.transfer_functions import send_money
                    
                    # Call the transfer function without PIN to trigger the inline keyboard
                    return await send_money(
                        chat_id=chat_id,
                        account_number=recipient_account,
                        bank_name=recipient_bank,
                        amount=float(amount),
                        narration=reason
                        # No PIN provided - this will trigger the inline keyboard flow
                    )
            
            elif function_name == "check_balance":
                # Use the balance functions directly
                from functions.balance_functions import check_balance
                return await check_balance(chat_id=chat_id)
            
            elif function_name == "set_transaction_pin":
                # Use the security functions directly
                from functions.security_functions import set_pin
                new_pin = function_args["new_pin"]
                confirm_pin = function_args["confirm_pin"]
                
                if new_pin != confirm_pin:
                    return {"success": False, "error": "PIN confirmation does not match"}
                
                return await set_pin(chat_id=chat_id, pin=new_pin)
            
            else:
                logger.error(f"❌ Unknown function: {function_name}")
                return {"error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}")
            return {"error": str(e)}

# Global assistant instance
_assistant_instance = None

def get_assistant() -> SofiAssistant:
    """Get or create the global assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = SofiAssistant()
    return _assistant_instance
