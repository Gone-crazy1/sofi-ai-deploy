#!/usr/bin/env python3
"""
Script to check what data is currently in Supabase tables
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def check_supabase_data():
    """Check what data exists in Supabase tables"""
    
    # Initialize Supabase client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=== Checking Supabase Data ===\n")
    
    # Check users table
    try:
        users_result = supabase.table("users").select("*").execute()
        print(f"📊 Users table: {len(users_result.data)} records")
        for i, user in enumerate(users_result.data, 1):
            print(f"  {i}. {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')} - Phone: {user.get('phone', 'N/A')}")
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
    
    print()
    
    # Check virtual_accounts table
    try:
        accounts_result = supabase.table("virtual_accounts").select("*").execute()
        print(f"🏦 Virtual accounts table: {len(accounts_result.data)} records")
        for i, account in enumerate(accounts_result.data, 1):
            print(f"  {i}. Account: {account.get('accountNumber', 'N/A')} - Bank: {account.get('bankName', 'N/A')}")
            print(f"      Name: {account.get('accountName', 'N/A')} - Ref: {account.get('accountReference', 'N/A')}")
    except Exception as e:
        print(f"❌ Error checking virtual_accounts table: {e}")
    
    print()
    
    # Check chat_history table
    try:
        chat_result = supabase.table("chat_history").select("*").limit(5).execute()
        print(f"💬 Chat history table: {len(chat_result.data)} recent records")
        for i, chat in enumerate(chat_result.data, 1):
            print(f"  {i}. Chat ID: {chat.get('chat_id', 'N/A')} - Role: {chat.get('role', 'N/A')}")
    except Exception as e:
        print(f"❌ Error checking chat_history table: {e}")

if __name__ == "__main__":
    check_supabase_data()
