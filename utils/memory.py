from supabase import create_client

supabase_url = "https://your-supabase-url"
supabase_key = "your-secret-key"
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
