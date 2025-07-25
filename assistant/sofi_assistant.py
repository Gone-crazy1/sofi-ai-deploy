"""
OpenAI Assistant Integration for Sofi AI
Handles function calling and thread management for each user
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SofiAssistant:
    """OpenAI Assistant integration for Sofi AI with function calling"""
    
    def __init__(self):
        """Initialize the OpenAI Assistant with v2 API"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            default_headers={
                "OpenAI-Beta": "assistants=v2"  # Fix deprecated v1 API
            }
        )
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        
        if not self.assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
        
        # Store user threads in memory (in production, store in database)
        self.user_threads: Dict[str, str] = {}
        
        logger.info(f"✅ Sofi Assistant initialized with ID: {self.assistant_id}")
    
    def get_or_create_thread(self, chat_id: str) -> str:
        """Get existing thread or create new one for user with v2 API"""
        if chat_id not in self.user_threads:
            try:
                thread = self.client.beta.threads.create()
                self.user_threads[chat_id] = thread.id
                logger.info(f"📧 Created new thread for user {chat_id}: {thread.id}")
            except Exception as e:
                logger.error(f"Error creating thread: {e}")
                # Fallback - disable assistant for now
                return None
        
        return self.user_threads[chat_id]
    
    async def process_message(self, chat_id: str, message: str, user_data: Dict = None) -> Tuple[str, Optional[Dict]]:
        """
        Process user message through OpenAI Assistant
        Returns: (response_text, function_call_data)
        """
        try:
            # Get or create thread for this user
            thread_id = self.get_or_create_thread(chat_id)
            
            # Add user context to the message if available
            enhanced_message = message
            if user_data:
                user_context = f"[User Context: Chat ID: {chat_id}"
                if user_data.get('full_name'):
                    user_context += f", Name: {user_data['full_name']}"
                if user_data.get('phone'):
                    user_context += f", Phone: {user_data['phone']}"
                user_context += f"] {message}"
                enhanced_message = user_context
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=enhanced_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion and handle function calls
            return await self._handle_run_completion(thread_id, run.id, chat_id)
            
        except Exception as e:
            logger.error(f"❌ Error processing message with assistant: {str(e)}")
            return f"Sorry, I encountered an error processing your request: {str(e)}", None
    
    async def _handle_run_completion(self, thread_id: str, run_id: str, chat_id: str) -> Tuple[str, Optional[Dict]]:
        """Handle run completion and function calls"""
        try:
            while True:
                # Check run status
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run.status == "completed":
                    # Get the assistant's response
                    messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                    latest_message = messages.data[0]
                    
                    if latest_message.role == "assistant":
                        response_text = latest_message.content[0].text.value
                        return response_text, None
                    
                elif run.status == "requires_action":
                    # Handle function calls
                    required_action = run.required_action
                    if required_action.type == "submit_tool_outputs":
                        return await self._handle_function_calls(
                            thread_id, run_id, required_action.submit_tool_outputs.tool_calls, chat_id
                        )
                
                elif run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"❌ Assistant run failed with status: {run.status}")
                    return "Sorry, I encountered an error processing your request.", None
                
                # Wait a bit before checking again
                import asyncio
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Error handling run completion: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}", None
    
    async def _handle_function_calls(self, thread_id: str, run_id: str, tool_calls: list, chat_id: str) -> Tuple[str, Optional[Dict]]:
        """Handle function calls from the assistant"""
        try:
            tool_outputs = []
            function_results = {}  # Track function results
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"🔧 Function called: {function_name} with args: {function_args}")
                
                # Add chat_id to function arguments
                function_args['chat_id'] = chat_id
                
                # Execute the function
                try:
                    result = await self._execute_function(function_name, function_args)
                    function_results[function_name] = result  # Store function result
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                except Exception as e:
                    logger.error(f"❌ Error executing function {function_name}: {str(e)}")
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)})
                    })
            
            # Submit tool outputs
            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            # Continue waiting for completion, but pass function results
            response, _ = await self._handle_run_completion(thread_id, run_id, chat_id)
            return response, function_results  # Return function results
            
        except Exception as e:
            logger.error(f"❌ Error handling function calls: {str(e)}")
            return f"Sorry, I encountered an error executing functions: {str(e)}", None
            return f"Sorry, I encountered an error executing functions: {str(e)}", None
    
    async def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested function"""
        
        # Import function handlers
        from functions.balance_functions import check_balance
        from functions.transfer_functions import send_money, calculate_transfer_fee
        from functions.transaction_functions import record_deposit, get_transfer_history, get_wallet_statement
        from functions.security_functions import verify_pin
        from functions.notification_functions import send_receipt, send_alert, update_transaction_status
        from functions.verification_functions import verify_account_name
        from functions.beneficiary_functions import save_beneficiary
        from functions.beneficiary_functions import get_user_beneficiaries
        from functions.beneficiary_functions import get_beneficiary_details

        
        # Function mapping
        function_map = {
            'check_balance': check_balance,
            'send_money': send_money,
            'record_deposit': record_deposit,
            'send_receipt': send_receipt,
            'send_alert': send_alert,
            'update_transaction_status': update_transaction_status,
            'calculate_transfer_fee': calculate_transfer_fee,
            'verify_pin': verify_pin,
            'get_transfer_history': get_transfer_history,
            'get_wallet_statement': get_wallet_statement,
            'verify_account_name': verify_account_name,
            'save_beneficiary': save_beneficiary,
            'get_user_beneficiaries': get_user_beneficiaries,
            'get_beneficiary_details': get_beneficiary_details
        }
        
        if function_name not in function_map:
            raise ValueError(f"Unknown function: {function_name}")
        
        # Execute the function
        function = function_map[function_name]
        result = await function(**args)
        
        logger.info(f"✅ Function {function_name} executed successfully")
        return result

# Global assistant instance
sofi_assistant = None

def get_assistant() -> SofiAssistant:
    """Get the global assistant instance"""
    global sofi_assistant
    if sofi_assistant is None:
        sofi_assistant = SofiAssistant()
    return sofi_assistant
