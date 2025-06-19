#!/usr/bin/env python3
"""
Test script to verify Sofi AI's transaction history functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.transaction_history import handle_transaction_history_query

# Test queries that should be recognized as transaction history requests
HISTORY_QUERIES = [
    "send my last week transaction history",
    "show me my transaction history",
    "summarize my recent transaction history", 
    "how did I spend my money this month",
    "what did i spend last week",
    "tell me about my spending",
    "show my spending history",
    "my recent transactions",
    "transaction summary for this month",
    "how much did i spend today",
    "where did my money go",
    "analyze my transactions",
    "list my payments",
    "what i spent this year",
    "breakdown my spending",
    "show me what i paid for",
    "my financial activity",
    "recent activity",
    "spending analysis",
    "money summary"
]

# Test queries that should NOT be recognized as transaction history (transfer requests)
TRANSFER_QUERIES = [
    "send 5000 to john",
    "transfer 10000 to 0123456789 gtbank", 
    "pay 2000 to my brother",
    "send money to mary",
    "transfer funds to access bank",
    "make payment to someone",
    "send cash to my friend"
]

async def test_transaction_history_parsing():
    """Test that transaction history queries are correctly identified"""
    print("🧪 TESTING TRANSACTION HISTORY PARSING")
    print("=" * 50)
    
    # Test positive cases (should be recognized as history)
    print("\n✅ HISTORY QUERIES (should be recognized):")
    for i, query in enumerate(HISTORY_QUERIES, 1):
        result = await handle_transaction_history_query("test_user", query, {"first_name": "TestUser"})
        status = "✅ DETECTED" if result is not None else "❌ MISSED"
        print(f"{i:2d}. {query:<40} → {status}")
    
    # Test negative cases (should NOT be recognized as history)
    print("\n❌ TRANSFER QUERIES (should NOT be recognized as history):")
    for i, query in enumerate(TRANSFER_QUERIES, 1):
        result = await handle_transaction_history_query("test_user", query, {"first_name": "TestUser"})
        status = "❌ FALSE POSITIVE" if result is not None else "✅ CORRECTLY IGNORED"
        print(f"{i:2d}. {query:<40} → {status}")

async def test_sample_response():
    """Test sample response generation"""
    print("\n\n🎯 TESTING SAMPLE RESPONSE GENERATION")
    print("=" * 50)
    
    sample_query = "show me my transaction history this week"
    print(f"Query: '{sample_query}'")
    print("\nGenerated Response:")
    print("-" * 30)
    
    response = await handle_transaction_history_query("test_user", sample_query, {"first_name": "TestUser"})
    if response:
        print(response)
    else:
        print("❌ No response generated")

async def main():
    """Run all tests"""
    load_dotenv()
    
    print("🤖 SOFI AI TRANSACTION HISTORY SYSTEM TEST")
    print("=" * 60)
    
    await test_transaction_history_parsing()
    await test_sample_response()
    
    print("\n\n✅ TEST COMPLETED!")
    print("The transaction history system should now intelligently distinguish")
    print("between transaction history requests and transfer requests.")

if __name__ == "__main__":
    asyncio.run(main())
