#!/usr/bin/env python3
"""
Test utils imports specifically
"""

print("🔍 Testing utils imports...")

try:
    print("1. Testing bank_api import...")
    from utils.bank_api import BankAPI
    print("✅ Bank API imported")
    
    print("2. Testing memory import...")
    from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
    print("✅ Memory utils imported")
    
    print("3. Testing conversation_state import...")
    from utils.conversation_state import conversation_state
    print("✅ Conversation state imported")
    
    print("\n🎯 All utils imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
