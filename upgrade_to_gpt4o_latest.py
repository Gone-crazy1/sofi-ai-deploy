#!/usr/bin/env python3
"""
🚀 UPGRADE SOFI AI TO CHATGPT-4O-LATEST WITH CUSTOM PROMPT
=========================================================

This script upgrades Sofi AI from:
- OLD: GPT-3.5-turbo with openai v0.x API  
- NEW: ChatGPT-4o-latest with openai v1.x API + Custom Prompt

Your Custom Prompt ID: pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d

CHANGES:
1. Update OpenAI API calls from old format to new format
2. Switch model from "gpt-3.5-turbo" to "gpt-4o-latest" 
3. Integrate your custom prompt ID
4. Update import statements and client initialization
5. Fix all files that use OpenAI API
"""

import os
import re
import sys
from datetime import datetime

def backup_file(file_path):
    """Create backup of file before modifying"""
    try:
        backup_path = f"{file_path}.backup_{int(datetime.now().timestamp())}"
        with open(file_path, 'r', encoding='utf-8') as original:
            content = original.read()
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(content)
        print(f"   ✅ Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return False

def update_openai_imports(file_path):
    """Update OpenAI imports and initialization"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update import statement
        content = re.sub(r'import openai', 'from openai import OpenAI', content)
        
        # Update API key initialization 
        old_init = r'openai\.api_key\s*=\s*os\.getenv\("OPENAI_API_KEY"\)'
        new_init = '''# Initialize OpenAI client with API key
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))'''
        content = re.sub(old_init, new_init, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"   ❌ Error updating imports: {e}")
        return False

def update_openai_api_calls(file_path, use_custom_prompt=True):
    """Update OpenAI API calls from v0.x to v1.x format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if use_custom_prompt:
            # Replace API calls with custom prompt integration
            old_pattern = r'openai\.ChatCompletion\.create\(\s*model="gpt-3\.5-turbo",\s*messages=\[(.*?)\],\s*(.*?)\)'
            
            new_call = '''openai_client.chat.completions.create(
            model="gpt-4o-latest",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Sofi AI, Nigeria's most advanced banking assistant. You understand Nigerian expressions, Pidgin English, and provide secure, user-friendly banking services."
                },
                \\1
            ],
            \\2
        )'''
            
        else:
            # Standard API call update without custom prompt
            old_pattern = r'openai\.ChatCompletion\.create\('
            new_call = 'openai_client.chat.completions.create('
        
        content = re.sub(old_pattern, new_call, content, flags=re.DOTALL)
        
        # Update model references
        content = re.sub(r'"gpt-3\.5-turbo"', '"gpt-4o-latest"', content)
        
        # Update response parsing
        content = re.sub(
            r'response\.choices\[0\]\.message\.content',
            'response.choices[0].message.content',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"   ❌ Error updating API calls: {e}")
        return False

def add_custom_prompt_function(file_path):
    """Add custom prompt integration function"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add custom prompt function at the top after imports
        custom_prompt_code = '''
def create_sofi_ai_response_with_custom_prompt(user_message, context="general"):
    """
    Create Sofi AI response using custom prompt from OpenAI
    Prompt ID: pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d
    """
    try:
        # Use your custom prompt
        response = openai_client.responses.create(
            prompt={
                "id": "pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d",
                "version": "3"
            },
            # Add user message as context
            context={
                "user_message": user_message,
                "banking_context": context,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error with custom prompt: {e}")
        # Fallback to standard GPT-4o-latest
        response = openai_client.chat.completions.create(
            model="gpt-4o-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are Sofi AI, Nigeria's most advanced banking assistant. You understand Nigerian expressions, Pidgin English, and provide secure, user-friendly banking services."
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

'''
        
        # Insert after the imports section
        import_end = content.find('\\n\\n')
        if import_end != -1:
            content = content[:import_end] + custom_prompt_code + content[import_end:]
        else:
            content = custom_prompt_code + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"   ❌ Error adding custom prompt function: {e}")
        return False

def update_requirements():
    """Update requirements.txt with new OpenAI version"""
    try:
        requirements_path = "requirements.txt"
        
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                lines = f.readlines()
            
            # Update OpenAI version
            updated_lines = []
            openai_updated = False
            
            for line in lines:
                if line.strip().startswith('openai'):
                    updated_lines.append('openai>=1.12.0\\n')
                    openai_updated = True
                else:
                    updated_lines.append(line)
            
            # Add if not present
            if not openai_updated:
                updated_lines.append('openai>=1.12.0\\n')
            
            with open(requirements_path, 'w') as f:
                f.writelines(updated_lines)
            
            print("   ✅ Updated requirements.txt")
        else:
            # Create requirements.txt
            with open(requirements_path, 'w') as f:
                f.write('openai>=1.12.0\\n')
            print("   ✅ Created requirements.txt")
        
        return True
    except Exception as e:
        print(f"   ❌ Error updating requirements: {e}")
        return False

def main():
    """Main upgrade function"""
    print("🚀 UPGRADING SOFI AI TO CHATGPT-4O-LATEST")
    print("=" * 55)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Custom Prompt ID: pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d")
    
    # Files that need OpenAI API updates
    files_to_update = [
        "main.py",
        "utils/enhanced_intent_detection.py",
        "regional_integration_guide.py"
    ]
    
    success_count = 0
    total_files = len(files_to_update)
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue
        
        print(f"\\n🔄 Updating {file_path}...")
        
        # Backup file
        if not backup_file(file_path):
            continue
        
        # Update imports
        if not update_openai_imports(file_path):
            continue
        
        # Update API calls
        if not update_openai_api_calls(file_path, use_custom_prompt=True):
            continue
        
        # Add custom prompt function (only to main.py)
        if file_path == "main.py":
            if not add_custom_prompt_function(file_path):
                continue
        
        print(f"   ✅ Successfully updated {file_path}")
        success_count += 1
    
    # Update requirements
    print("\\n📦 Updating requirements...")
    if update_requirements():
        success_count += 0.5
    
    print("\\n" + "=" * 55)
    print(f"📊 UPGRADE SUMMARY: {success_count}/{total_files} files updated")
    
    if success_count >= total_files:
        print("🎉 UPGRADE COMPLETED SUCCESSFULLY!")
        print("\\n🚀 Next steps:")
        print("   1. Install new OpenAI package: pip install openai>=1.12.0")
        print("   2. Test Sofi AI with a simple message")
        print("   3. Verify GPT-4o-latest is working")
        print("   4. Test your custom prompt integration")
        print("\\n💡 Benefits:")
        print("   • Faster responses with GPT-4o-latest")
        print("   • Better understanding of Nigerian context")
        print("   • Custom prompt for banking-specific responses")
        print("   • More accurate intent detection")
    else:
        print("⚠️ Some files failed to update - check error messages above")
    
    print(f"\\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
