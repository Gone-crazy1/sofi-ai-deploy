import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

supabase_url = "https://qbxherpwkxckwlkwjhpm.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFieGhlcnB3a3hja3dsa3dqaHBtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNDQ1MzYsImV4cCI6MjA2NDcyMDUzNn0._YOyoxWVoaOD7VMl_OwP1t-duw6s4qWmtNZm2rrcskM"
supabase = create_client(supabase_url, supabase_key)

async def save_memory(user_id, content):
    supabase.table("memories").insert({
        "user_id": user_id,
        "content": content
    }).execute()

async def list_memories(user_id, limit=5):
    result = supabase.table("memories") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("timestamp", desc=True) \
        .limit(limit) \
        .execute()
    return result.data

def clear_all_memories():
    """Synchronous function to clear all memories"""
    try:
        supabase.table("memories").delete().neq('user_id', '').execute()
        return True
    except Exception as e:
        print(f"Error clearing memories: {e}")
        return False
