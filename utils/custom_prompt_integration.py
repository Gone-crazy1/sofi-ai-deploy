"""
🎯 CUSTOM PROMPT INTEGRATION FOR SOFI AI
=======================================

This adds your custom OpenAI prompt to Sofi AI for enhanced responses.
Prompt ID: pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d
"""

import os
from openai import OpenAI
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client for custom prompt
custom_prompt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_sofi_response_with_custom_prompt(user_message: str, context: str = "general") -> str:
    """
    Create Sofi AI response using your custom prompt from OpenAI
    
    Args:
        user_message: The user's message
        context: Banking context (transfer, balance, general, etc.)
        
    Returns:
        AI generated response using your custom prompt
    """
    try:
        # Use your custom prompt ID
        response = custom_prompt_client.responses.create(
            prompt={
                "id": "pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d",
                "version": "3"
            },
            # Add context variables
            variables={
                "user_message": user_message,
                "banking_context": context,
                "timestamp": datetime.now().isoformat(),
                "location": "Nigeria"
            }
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error with custom prompt: {e}")
        
        # Fallback to standard GPT-4o-latest if custom prompt fails
        try:
            response = custom_prompt_client.chat.completions.create(
                model="gpt-4o-latest",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Sofi AI, Nigeria's most advanced banking assistant. You understand:
                        - Nigerian expressions and Pidgin English
                        - Local banking customs and preferences  
                        - Cultural context and communication style
                        - Secure banking operations and fraud prevention
                        
                        Provide helpful, accurate, and culturally relevant banking assistance."""
                    },
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            return "I'm having trouble processing your request right now. Please try again."

def enhance_message_with_custom_prompt(message: str, intent: str = "unknown") -> str:
    """
    Enhance user message understanding using custom prompt
    
    Args:
        message: Original user message
        intent: Detected intent (transfer, balance, etc.)
        
    Returns:
        Enhanced understanding of user's request
    """
    try:
        context_prompt = f"""
        Analyze this Nigerian banking user message and provide enhanced understanding:
        
        Original Message: "{message}"
        Detected Intent: {intent}
        
        Please provide:
        1. Clear interpretation of what the user wants
        2. Any Nigerian/Pidgin expressions translated
        3. Banking action required
        4. Key details extracted
        
        Return as natural explanation.
        """
        
        return create_sofi_response_with_custom_prompt(context_prompt, "message_analysis")
        
    except Exception as e:
        logger.error(f"Error enhancing message: {e}")
        return message  # Return original if enhancement fails
