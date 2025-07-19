#!/usr/bin/env python3
"""Update OpenAI Assistant with latest function definitions."""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import after env loaded
from openai import OpenAI
from sofi_assistant_functions import SOFI_MONEY_FUNCTIONS

def update_assistant():
    """Update assistant with latest functions."""
    try:
        # Initialize client with just API key
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("🔍 Looking for Sofi AI Banking Assistant...")
        
        # Find existing assistant
        assistants = client.beta.assistants.list()
        
        sofi_assistant = None
        for assistant in assistants.data:
            if "Sofi" in assistant.name or "Banking" in assistant.name:
                sofi_assistant = assistant
                print(f"✅ Found Assistant: {assistant.name} ({assistant.id})")
                break
        
        if not sofi_assistant:
            print("❌ No Sofi assistant found")
            return
            
        # Update with latest functions
        print("🔄 Updating assistant with latest functions...")
        
        updated = client.beta.assistants.update(
            assistant_id=sofi_assistant.id,
            tools=SOFI_MONEY_FUNCTIONS
        )
        
        print(f"✅ Updated assistant with {len(SOFI_MONEY_FUNCTIONS)} functions")
        
        # Verify functions are registered
        assistant_functions = []
        for tool in updated.tools:
            if tool.type == 'function':
                assistant_functions.append(tool.function.name)
        
        print(f"\n📋 Registered functions ({len(assistant_functions)}):")
        for func_name in sorted(assistant_functions):
            is_beneficiary = 'beneficiary' in func_name
            marker = "🎯" if is_beneficiary else "🔧"
            print(f"  {marker} {func_name}")
        
        # Check specifically for beneficiary functions
        beneficiary_functions = [f for f in assistant_functions if 'beneficiary' in f]
        print(f"\n💼 Beneficiary functions: {len(beneficiary_functions)}")
        for func in beneficiary_functions:
            print(f"  ✅ {func}")
            
        if 'save_beneficiary' in assistant_functions:
            print("\n🎉 SUCCESS: save_beneficiary is now registered!")
        else:
            print("\n❌ ERROR: save_beneficiary still not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error updating assistant: {e}")
        return False

if __name__ == "__main__":
    success = update_assistant()
    if success:
        print("\n✅ Assistant update complete!")
    else:
        print("\n❌ Assistant update failed!")
