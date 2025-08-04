#!/usr/bin/env python3
"""
Fix the create_paystack_for_existing_user method
"""

def fix_paystack_method():
    """Fix the method by recreating it properly"""
    
    method_code = '''    def create_paystack_for_existing_user(self, user_id: str) -> Dict[str, Any]:
        """
        Create Paystack virtual account for an existing user who doesn't have one
        
        Args:
            user_id: The UUID of the existing user in the database
            
        Returns:
            Dict with Paystack account creation result
        """
        try:
            # Get user data from database
            user_response = self.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not user_response.data:
                return {
                    'success': False,
                    'error': f'User not found with ID: {user_id}'
                }
            
            user_data = user_response.data[0]
            
            whatsapp_number = user_data.get('whatsapp_number', '').strip()
            first_name = user_data.get('first_name', '').strip() 
            last_name = user_data.get('last_name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            email = user_data.get('email', '').strip()
            phone = user_data.get('whatsapp_number', '').strip()
            
            logger.info(f"🏦 Creating Paystack account for existing user: {whatsapp_number}")
            
            # Check if user already has Paystack account
            if user_data.get('account_number'):
                return {
                    'success': True,
                    'account_number': user_data['account_number'],
                    'bank_name': 'Wema Bank',
                    'customer_code': user_data.get('paystack_customer_code', ''),
                    'customer_id': user_data.get('paystack_customer_id', ''),
                    'message': 'User already has Paystack account'
                }
            
            # Create Paystack customer with virtual account using the Paystack integration
            logger.info(f"🏦 Creating Paystack account with data: {json.dumps({'email': email, 'first_name': first_name, 'last_name': last_name, 'phone': phone}, indent=2)}")
            
            # Prepare Paystack customer data
            paystack_data = {
                'email': email,
                'first_name': first_name if first_name else 'User',
                'last_name': last_name if last_name else 'Sofi',
                'phone': phone,
                'metadata': {
                    'whatsapp_number': whatsapp_number,
                    'phone': phone,
                    'platform': 'whatsapp',
                    'created_via': 'sofi_ai_assistant',
                    'existing_user_update': True
                }
            }
            
            # Create Paystack customer with virtual account
            paystack_result = self.paystack.create_user_account(paystack_data)
            logger.info(f"🏦 Paystack API response: {json.dumps(paystack_result, indent=2)}")
            
            if not paystack_result.get('success'):
                error_msg = paystack_result.get('error', 'Unknown Paystack error')
                logger.error(f"❌ Paystack account creation failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {error_msg}",
                    'paystack_response': paystack_result
                }
            
            # Extract account details
            virtual_account = paystack_result.get('account', {})
            customer = paystack_result.get('customer', {})
            
            logger.info(f"✅ Paystack account created: {virtual_account.get('account_number')}")
            
            # Update existing user record with Paystack details
            update_data = {
                'paystack_customer_id': customer.get('id'),
                'paystack_customer_code': customer.get('customer_code'),
                'account_number': virtual_account.get('account_number'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update user in Supabase
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if not result.data:
                logger.error(f"❌ Failed to update user with Paystack details")
                return {
                    'success': False,
                    'error': 'Failed to update user record with Paystack details'
                }
            
            logger.info(f"✅ User updated with Paystack details: {virtual_account.get('account_number')}")
            
            return {
                'success': True,
                'message': f'Paystack account created successfully for existing user',
                'account_number': virtual_account.get('account_number'),
                'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                'customer_code': customer.get('customer_code'),
                'customer_id': customer.get('id'),
                'account_data': {
                    'account_number': virtual_account.get('account_number'),
                    'account_name': virtual_account.get('account_name'),
                    'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                    'bank_code': virtual_account.get('bank_code', '035'),
                    'customer_code': customer.get('customer_code'),
                    'dva_id': virtual_account.get('account_reference')
                },
                'account_details': {
                    'account_number': virtual_account.get('account_number'),
                    'account_name': virtual_account.get('account_name'),
                    'bank_name': virtual_account.get('bank_name', 'Wema Bank')
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Exception creating Paystack account for existing user: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Exception creating Paystack account: {str(e)}'
            }
'''
    
    # Read the file and locate where the broken method starts
    with open('utils/paystack_account_manager.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find the method definition
    method_start = content.find('def create_paystack_for_existing_user(')
    if method_start == -1:
        print("❌ Method not found")
        return
    
    # Find the end of the method (next method or class end)
    remaining_content = content[method_start:]
    
    # Find the next method or end of class
    next_method_pos = remaining_content.find('\n    def ', 1)  # Skip the current method
    if next_method_pos == -1:
        # No next method, find end of class
        next_method_pos = remaining_content.find('\n\n# Global')
        if next_method_pos == -1:
            next_method_pos = len(remaining_content)
    
    method_end = method_start + next_method_pos
    
    # Replace the broken method
    new_content = content[:method_start] + method_code + content[method_end:]
    
    # Write the fixed file
    with open('utils/paystack_account_manager.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed create_paystack_for_existing_user method")

if __name__ == "__main__":
    fix_paystack_method()
