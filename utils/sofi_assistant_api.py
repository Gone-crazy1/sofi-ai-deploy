"""
OpenAI Assistant API Integration for WhatsApp
Manages threads for each user and uses the Sofi Assistant
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import json
import time

logger = logging.getLogger(__name__)

class SofiAssistantManager:
    """Manages OpenAI Assistant API for WhatsApp users"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")  # Get from environment variable
        if not self.assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID environment variable is required")
        self.user_threads = {}  # Store thread IDs for each user
        
    def get_or_create_thread(self, phone_number: str) -> str:
        """Get existing thread or create new one for user"""
        try:
            if phone_number not in self.user_threads:
                logger.info(f"🧵 Creating new thread for user {phone_number}")
                thread = self.client.beta.threads.create()
                self.user_threads[phone_number] = thread.id
                logger.info(f"✅ Thread created: {thread.id}")
            else:
                logger.info(f"🧵 Using existing thread for {phone_number}: {self.user_threads[phone_number]}")
                
            return self.user_threads[phone_number]
        except Exception as e:
            logger.error(f"❌ Error creating/getting thread for {phone_number}: {e}")
            raise
    
    async def send_message_to_assistant(self, phone_number: str, message: str) -> str:
        """Send message to Sofi Assistant and get response"""
        try:
            logger.info(f"🤖 Sending message to Sofi Assistant: {phone_number} -> {message}")
            
            # Store phone number for function execution context
            self._current_phone_number = phone_number
            
            # Get or create thread for this user
            thread_id = self.get_or_create_thread(phone_number)
            
            # Add user message to thread
            logger.info(f"📝 Adding message to thread {thread_id}")
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Run the assistant
            logger.info(f"🚀 Running Sofi Assistant on thread {thread_id}")
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            logger.info(f"⏳ Waiting for assistant response... Run ID: {run.id}")
            run = await self.wait_for_run_completion(thread_id, run.id)
            
            if run.status == "completed":
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    order="desc",
                    limit=1
                )
                
                if messages.data:
                    response = messages.data[0].content[0].text.value
                    logger.info(f"✅ Sofi Assistant response received for {phone_number}")
                    return response
                else:
                    logger.error(f"❌ No response from assistant for {phone_number}")
                    return "I'm having trouble processing your request. Please try again."
            else:
                logger.error(f"❌ Assistant run failed with status: {run.status}")
                return "I'm having trouble processing your request. Please try again."
                
        except Exception as e:
            logger.error(f"❌ Error in assistant conversation for {phone_number}: {e}")
            return "I'm having trouble right now. Please try again in a moment."
    
    async def wait_for_run_completion(self, thread_id: str, run_id: str, max_wait: int = 30) -> Any:
        """Wait for assistant run to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run.status in ["completed", "failed", "cancelled", "expired"]:
                    logger.info(f"🏁 Assistant run finished with status: {run.status}")
                    return run
                elif run.status == "requires_action":
                    logger.info(f"🔧 Assistant requires action - handling tool calls")
                    run = await self.handle_tool_calls(thread_id, run)
                    if run.status in ["completed", "failed", "cancelled", "expired"]:
                        return run
                else:
                    logger.info(f"⏳ Assistant still running... Status: {run.status}")
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error checking run status: {e}")
                time.sleep(1)
        
        logger.error(f"⏰ Assistant run timed out after {max_wait} seconds")
        return run
    
    async def handle_tool_calls(self, thread_id: str, run: Any) -> Any:
        """Handle function calls from the assistant"""
        try:
            if run.required_action and run.required_action.submit_tool_outputs:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                logger.info(f"🛠️ Processing {len(tool_calls)} tool calls")
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"🔧 Executing function: {function_name}")
                    
                    # Set current phone number context for function execution
                    self._current_phone_number = getattr(self, '_current_phone_number', '')
                    
                    # Execute the function (now properly async)
                    result = await self.execute_function(function_name, function_args)
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                
                # Submit tool outputs
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                logger.info(f"✅ Tool outputs submitted, continuing run...")
                return await self.wait_for_run_completion(thread_id, run.id)
                
        except Exception as e:
            logger.error(f"❌ Error handling tool calls: {e}")
            
        return run
    
    async def execute_function(self, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call from the assistant"""
        try:
            logger.info(f"⚡ Executing function: {function_name} with args: {function_args}")
            
            # Import and execute the appropriate function
            if function_name == "check_balance":
                from functions.balance_functions import check_balance
                # Properly await the async function instead of using asyncio.run()
                phone_number = function_args.get("whatsapp_number", function_args.get("chat_id", ""))
                result = await check_balance(phone_number)
                return result
            elif function_name == "send_money":
                from functions.transfer_functions import send_money
                # Fix parameter mapping - send_money expects chat_id as first parameter
                # Get phone number from context (need to pass it from the call)
                phone_number = getattr(self, '_current_phone_number', function_args.get("chat_id", ""))
                result = await send_money(
                    chat_id=phone_number,
                    amount=function_args.get("amount"),
                    account_number=function_args.get("account_number"),
                    bank_name=function_args.get("bank_name"),
                    narration=function_args.get("narration", "Transfer via Sofi AI")
                )
                return result
            elif function_name == "verify_account_name":
                # Use the verify_account_name function from main.py
                from main import verify_account_name
                result = verify_account_name(
                    account_number=function_args.get("account_number"),
                    bank_name=function_args.get("bank_name")
                )
                return result
            # Add more function handlers as needed
            else:
                logger.warning(f"⚠️ Unknown function: {function_name}")
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}", exc_info=True)
            return {"error": f"Failed to execute {function_name}: {str(e)}"}

# Global instance
sofi_assistant = SofiAssistantManager()
