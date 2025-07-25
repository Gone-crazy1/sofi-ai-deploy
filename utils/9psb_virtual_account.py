"""
9PSB Virtual Account Management for Sofi AI
Handles creation, lookup, and linking of virtual accounts to users.
"""


import os
from utils.9psb_api import NINEPSBApi
from supabase import create_client

# Initialize Supabase and 9PSB API (ensure your env variables are set)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
ninepsb = NINEPSBApi(
    api_key=os.getenv("NINEPSB_API_KEY"),
    base_url=os.getenv("NINEPSB_BASE_URL")
    # Add secretKey if needed
)

def create_virtual_account_for_user(user_id: str, user_data: dict):
    """
    Create a 9PSB virtual account for the user and store it in Supabase.
    """
    result = ninepsb.create_virtual_account(user_id, user_data)
    if result.get("success") or result.get("accountNumber"):
        supabase.table("users").update({
            "virtual_account_number": result.get("accountNumber"),
            "virtual_account_bank": "9PSB",
            "virtual_account_data": result
        }).eq("id", user_id).execute()
    return result

def get_virtual_account(user_id: str):
    """
    Fetch the user's 9PSB virtual account from Supabase.
    """
    user = supabase.table("users").select("virtual_account_number", "virtual_account_bank", "virtual_account_data").eq("id", user_id).execute()
    if user.data:
        return user.data[0]
    return None
