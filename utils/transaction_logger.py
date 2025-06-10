import openai
from supabase import create_client
from dotenv import load_dotenv
import os
import logging

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
# Use service role key for server-side operations to bypass RLS
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def categorize_expense(narration):
    """Categorize an expense using GPT."""
    prompt = f"What category is this expense? '{narration}'. Return a one-word lowercase category like food, transport, bills, etc."
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion['choices'][0]['message']['content'].strip().lower()
    except openai.error.OpenAIError as e:
        logger.error("Error with OpenAI API: %s", e)
        return "uncategorized"
    except Exception as e:
        logger.error("Unexpected error occurred while categorizing expense: %s", e)
        return "uncategorized"

async def save_transaction(user_id, amount, type, narration):
    try:
        # Categorize expense
        category = categorize_expense(narration)

        # Save to Supabase
        supabase.table("transactions").insert({
            "user_id": user_id,
            "amount": amount,
            "type": type,
            "narration": narration,
            "category": category
        }).execute()
    except supabase.exceptions.SupabaseException as e:
        logger.error("Error with Supabase operation: %s", e)
    except Exception as e:
        logger.error("Unexpected error occurred while saving transaction: %s", e)
