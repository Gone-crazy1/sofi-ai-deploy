"""
Debug OpenAI Assistant Function Recognition
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from sofi_assistant_functions import SOFI_MONEY_FUNCTIONS

load_dotenv()

def debug_assistant_functions():
    """Debug which functions are registered with the assistant"""
    
    print("🔍 DEBUGGING ASSISTANT FUNCTIONS")
    print("=" * 50)
    
    # Check function definitions
    print(f"📋 Total functions defined: {len(SOFI_MONEY_FUNCTIONS)}")
    
    function_names = []
    for func in SOFI_MONEY_FUNCTIONS:
        name = func["function"]["name"]
        function_names.append(name)
        print(f"  ✅ {name}")
    
    print(f"\n🔍 Beneficiary functions:")
    beneficiary_functions = [name for name in function_names if "beneficiary" in name]
    for func in beneficiary_functions:
        print(f"  ✅ {func}")
    
    if not beneficiary_functions:
        print("  ❌ NO BENEFICIARY FUNCTIONS FOUND!")
    
    # Check OpenAI client
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Try to find existing assistant
        assistants = client.beta.assistants.list()
        
        for assistant in assistants.data:
            if assistant.name == "Sofi AI Banking Assistant":
                print(f"\n🤖 Found Assistant: {assistant.id}")
                
                # Check assistant's tools
                print(f"📋 Assistant has {len(assistant.tools)} tools:")
                for i, tool in enumerate(assistant.tools):
                    if tool.type == "function":
                        print(f"  {i+1}. {tool.function.name}")
                
                assistant_function_names = [tool.function.name for tool in assistant.tools if tool.type == "function"]
                assistant_beneficiary_functions = [name for name in assistant_function_names if "beneficiary" in name]
                
                print(f"\n🔍 Assistant beneficiary functions:")
                for func in assistant_beneficiary_functions:
                    print(f"  ✅ {func}")
                
                if not assistant_beneficiary_functions:
                    print("  ❌ ASSISTANT HAS NO BENEFICIARY FUNCTIONS!")
                    print("  🔧 Need to update assistant with latest functions")
                
                break
        else:
            print("\n❌ No Sofi AI Banking Assistant found!")
            
    except Exception as e:
        print(f"\n❌ Error checking OpenAI: {e}")

if __name__ == "__main__":
    debug_assistant_functions()
