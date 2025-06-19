"""
Fix user_onboarding.py indentation and name display issue
"""

def fix_user_onboarding_file():
    """Fix the indentation and name display in user_onboarding.py"""
    
    # Read the current file
    with open('utils/user_onboarding.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the main issues
    fixes = [
        # Fix the indentation issue in check_existing_user
        ('              response = supabase.table', '            response = supabase.table'),
        ('      async def check_existing_user', '    async def check_existing_user'),
        # Fix the welcome notification to use full name
        ('account_name = user_record.get(\'opay_account_name\')', 'display_name = user_record.get(\'full_name\', \'User\')'),
        ('👤 *Account Name:* {account_name}', '👤 *Account Name:* {display_name}'),
        # Fix the bank name reference
        ('Your funds are secured with OPay banking infrastructure', 'Your funds are secured with Monnify banking infrastructure')
    ]
    
    for old_text, new_text in fixes:
        content = content.replace(old_text, new_text)
    
    # Write the fixed content back
    with open('utils/user_onboarding.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed user_onboarding.py")
    print("✅ Users will now see their full name from Supabase")
    print("✅ Monnify integration maintained")

if __name__ == "__main__":
    fix_user_onboarding_file()
