#!/usr/bin/env python3
"""
Demo script showing Sofi AI's human-like transaction history responses
"""

import asyncio
import json
from utils.transaction_history import handle_transaction_history_query

# Sample user data
SAMPLE_USER = {
    "first_name": "Sarah", 
    "last_name": "Johnson",
    "chat_id": "demo_user"
}

# Various ways users might ask for transaction history
DEMO_QUERIES = [
    "Hey Sofi, send my last week transaction history",
    "Show me what I spent this month",
    "Sofi, how did I spend my money recently?",
    "Tell me about my spending patterns",
    "Summarize my recent transaction history",
    "What's my transaction history for today?",
    "How much money did I spend last week?",
    "Give me a breakdown of my spending",
    "Show me my recent financial activity",
]

async def demo_human_like_responses():
    """Demonstrate Sofi's human-like transaction history responses"""
    print("🤖 SOFI AI - HUMAN-LIKE TRANSACTION HISTORY DEMO")
    print("=" * 60)
    print("This demo shows how Sofi responds to transaction history queries")
    print("in a natural, human-like way (not bot-like responses).\n")
    
    for i, query in enumerate(DEMO_QUERIES, 1):
        print(f"👤 USER: {query}")
        print("🤖 SOFI:")
        print("-" * 40)
        
        response = await handle_transaction_history_query(
            SAMPLE_USER["chat_id"], 
            query, 
            SAMPLE_USER
        )
        
        if response:
            # Show just the first few lines for demo
            lines = response.split('\n')
            for line in lines[:5]:
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 5:
                print("   ... (response continues)")
        else:
            print("   [Not detected as transaction history query]")
        
        print("\n" + "="*60 + "\n")

async def demo_key_features():
    """Show key features of the transaction history system"""
    print("🎯 KEY FEATURES OF SOFI'S TRANSACTION HISTORY SYSTEM")
    print("=" * 60)
    
    features = [
        "✅ Distinguishes between history requests and transfer requests",
        "✅ Recognizes natural language patterns (20+ variations tested)",
        "✅ Provides human-like, personalized responses",
        "✅ Supports different time periods (today, week, month, year, all)",
        "✅ Offers both transaction lists and spending summaries",
        "✅ Includes smart financial insights and advice",
        "✅ Works with multiple transaction types (bank, crypto, airtime)",
        "✅ Handles users with no transaction history gracefully",
        "✅ Uses the user's first name for personalization",
        "✅ Provides helpful examples for follow-up queries"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "=" * 60)
    print("🎉 SOFI IS NOW READY TO HANDLE TRANSACTION HISTORY INTELLIGENTLY!")
    print("Users can ask in many natural ways and get helpful, human responses.")

async def main():
    await demo_human_like_responses()
    await demo_key_features()

if __name__ == "__main__":
    asyncio.run(main())
