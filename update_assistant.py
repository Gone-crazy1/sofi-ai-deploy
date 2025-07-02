#!/usr/bin/env python3
"""
Update the existing OpenAI Assistant with new instructions
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from sofi_assistant_functions import SOFI_MONEY_FUNCTIONS, SOFI_MONEY_INSTRUCTIONS

load_dotenv()

def update_assistant():
    """Update the existing assistant with new instructions"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Find existing assistant
        assistants = client.beta.assistants.list()
        assistant_id = None
        
        for assistant in assistants.data:
            if assistant.name == "Sofi AI Banking Assistant":
                assistant_id = assistant.id
                print(f"✅ Found existing assistant: {assistant_id}")
                break
        
        if assistant_id:
            # Update the existing assistant
            updated_assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                instructions=SOFI_MONEY_INSTRUCTIONS,
                tools=SOFI_MONEY_FUNCTIONS,
                model="gpt-4o"  # Use the correct model name
            )
            
            print(f"✅ Updated assistant {assistant_id} with new instructions:")
            print(f"   Name: {updated_assistant.name}")
            print(f"   Model: {updated_assistant.model}")
            print(f"   Tools: {len(updated_assistant.tools)} functions")
            print(f"\n📋 New Instructions:")
            print(updated_assistant.instructions)
            
        else:
            print(f"❌ No existing assistant found - creating new one")
            # Create new assistant
            assistant = client.beta.assistants.create(
                name="Sofi AI Banking Assistant",
                instructions=SOFI_MONEY_INSTRUCTIONS,
                tools=SOFI_MONEY_FUNCTIONS,
                model="gpt-4o"  # Use the correct model name
            )
            
            print(f"✅ Created new assistant: {assistant.id}")
            
    except Exception as e:
        print(f"❌ Error updating assistant: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_assistant()
