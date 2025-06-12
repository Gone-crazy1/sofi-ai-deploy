import os
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict
from datetime import datetime

# Load environment variables
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
# Use service role key for server-side operations to bypass RLS
# Fall back to anon key if service role key is not set
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Warning: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    print("Some functionality may not work without proper Supabase configuration")

# Check if we have a valid key (not placeholder)
if supabase_key == "your_service_role_key_here":
    print("Warning: Using placeholder service role key. Please set SUPABASE_SERVICE_ROLE_KEY to your actual service role key.")
    supabase_key = os.getenv("SUPABASE_KEY")

# Lazy initialization of supabase client
supabase = None

def get_supabase_client():
    """Get or create supabase client"""
    global supabase
    if supabase is None:
        supabase = create_client(supabase_url, supabase_key)
    return supabase

async def save_chat_message(chat_id: str, role: str, content: str) -> bool:
    """Save a chat message to the conversation history.
    
    Args:
        chat_id: The Telegram chat ID
        role: Either 'user' or 'assistant'
        content: The message content
          Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase_client()
        client.table("chat_history").insert({
            "chat_id": str(chat_id),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return False

async def get_chat_history(chat_id: str, limit: int = 10) -> List[Dict]:
    """Get the recent chat history for a user.
    
    Args:
        chat_id: The Telegram chat ID
        limit: Number of recent messages to retrieve
          Returns:
        List of message dictionaries in OpenAI chat format
    """
    try:
        client = get_supabase_client()
        result = client.table("chat_history") \
            .select("*") \
            .eq("chat_id", str(chat_id)) \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
            
        # Convert to OpenAI chat format and reverse to get chronological order
        messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in reversed(result.data)
        ]
        
        return messages
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

async def clear_chat_history(chat_id: str) -> bool:
    """Clear chat history for a specific user.
    
    Args:
        chat_id: The Telegram chat ID
          Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase_client()
        client.table("chat_history") \
            .delete() \
            .eq("chat_id", str(chat_id)) \
            .execute()
        return True
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return False

# Legacy functions for backwards compatibility
async def save_memory(user_id, content):
    """Legacy function for backwards compatibility"""
    try:
        supabase.table("memories").insert({
            "user_id": user_id,
            "content": content
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False

async def list_memories(user_id, limit=5):
    """Legacy function for backwards compatibility"""
    try:
        result = supabase.table("memories") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
        return result.data
    except Exception as e:
        print(f"Error listing memories: {e}")
        return []
