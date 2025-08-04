#!/usr/bin/env python3
"""
Fix all non-existent database fields in main.py
"""

def fix_main_py_schema():
    """Fix main.py to use only existing database columns"""
    
    # Read the main.py file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all references to non-existent columns
    non_existent_fields = [
        "'paystack_integration_failed': True,",
        "'paystack_error': error_msg,",
        "'paystack_error': f\"Exception: {str(paystack_error)}\",", 
        "'paystack_retry_needed': True,"
    ]
    
    # Replace each occurrence
    for field in non_existent_fields:
        content = content.replace(field, "")
    
    # Clean up any empty lines and fix formatting
    lines = content.split('\n')
    cleaned_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # If this is a paystack_update dictionary definition
        if 'paystack_update = {' in line:
            cleaned_lines.append(line)
            i += 1
            
            # Add only the updated_at field
            while i < len(lines) and '}' not in lines[i]:
                if "'updated_at':" in lines[i]:
                    cleaned_lines.append(lines[i])
                i += 1
            
            # Add the closing brace
            if i < len(lines):
                cleaned_lines.append(lines[i])
        else:
            cleaned_lines.append(line)
        
        i += 1
    
    # Write back to file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Fixed main.py database schema compatibility")

if __name__ == "__main__":
    fix_main_py_schema()
