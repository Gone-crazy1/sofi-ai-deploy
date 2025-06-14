import asyncio
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock

# Mock problematic modules before importing main
sys.modules['usd_based_crypto_system'] = MagicMock()
sys.modules['supabase'] = MagicMock()

async def test_transfer_improvements():
    """Test that Sofi's transfer responses are now conversational and intelligent"""
    print("🚀 TESTING SOFI'S IMPROVED TRANSFER RESPONSES")
    print("=" * 60)
    
    try:
        # Set up environment
        os.environ['OPENAI_API_KEY'] = 'test_key'
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_KEY'] = 'test_key'
        
        # Mock all external dependencies
        with patch('openai.ChatCompletion.create') as mock_openai:
            mock_openai.return_value = {
                'choices': [{'message': {'content': 'Test response'}}]
            }
            
            # Import after setting env vars and mocks
            from main import generate_ai_reply, find_beneficiary_by_name, detect_intent
            
            # Test data
            test_chat_id = "test_chat_123"
            test_user_data = {
                "id": "test_user_123",
                "first_name": "Test User",
                "telegram_chat_id": test_chat_id
            }
            
            mock_virtual_account = {
                "accountnumber": "1234567890",
                "accountName": "Test User",
                "bankName": "Test Bank"
            }
            
            print("\n1️⃣ Testing 'transfer money to mella' - should check beneficiaries first")
            
            with patch('main.check_virtual_account', return_value=mock_virtual_account), \
                 patch('main.get_supabase_client') as mock_supabase, \
                 patch('main.save_chat_message', new_callable=AsyncMock), \
                 patch('main.find_beneficiary_by_name') as mock_find_beneficiary, \
                 patch('main.detect_intent') as mock_detect_intent, \
                 patch('main.handle_transfer_flow') as mock_handle_transfer_flow, \
                 patch('openai.ChatCompletion.create') as mock_openai_create:
                
                # Configure mocks
                mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user_data]
                
                # Mock OpenAI response
                mock_openai_create.return_value = {
                    'choices': [{'message': {'content': 'Fallback response'}}]
                }
                
                # Mock that Mella is NOT found in beneficiaries
                mock_find_beneficiary.return_value = None
                
                # Mock intent detection
                mock_detect_intent.return_value = {
                    "intent": "transfer",
                    "details": {
                        "recipient_name": "mella"
                    }
                }
                
                # Mock that handle_transfer_flow doesn't handle it (returns None)
                mock_handle_transfer_flow.return_value = None
                
                # Test the actual response
                response = await generate_ai_reply(test_chat_id, "i want to transfer money to mella")
                
                print(f"Response: {response}")
                
                # Verify the response is conversational and mentions beneficiary checking
                assert isinstance(response, str), "Response should be a string"
                assert "mella" in response.lower(), "Response should mention 'mella'"
                assert ("don't have" in response.lower() or 
                        "not" in response.lower() or 
                        "saved" in response.lower()), "Should indicate Mella not found"
                assert "bank" in response.lower(), "Should ask for bank details"
                
                print("✅ Response is conversational and checks beneficiaries!")
            
            print("\n2️⃣ Testing 'send 5k to mella' where Mella is a saved beneficiary")
            
            with patch('main.check_virtual_account', return_value=mock_virtual_account), \
                 patch('main.get_supabase_client') as mock_supabase, \
                 patch('main.save_chat_message', new_callable=AsyncMock), \
                 patch('main.find_beneficiary_by_name') as mock_find_beneficiary, \
                 patch('main.detect_intent') as mock_detect_intent, \
                 patch('main.handle_transfer_flow') as mock_handle_transfer_flow, \
                 patch('openai.ChatCompletion.create') as mock_openai_create:
                
                # Configure mocks
                mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user_data]
                
                # Mock OpenAI response
                mock_openai_create.return_value = {
                    'choices': [{'message': {'content': 'Fallback response'}}]
                }
                
                # Mock that Mella IS found in beneficiaries
                mock_find_beneficiary.return_value = {
                    "name": "Mella",
                    "account_number": "0123456789",
                    "bank_name": "Access Bank"
                }
                
                # Mock intent detection for "send 5k to mella"
                mock_detect_intent.return_value = {
                    "intent": "transfer",
                    "details": {
                        "recipient_name": "mella",
                        "amount": 5000
                    }
                }
                
                # Mock that handle_transfer_flow doesn't handle it (returns None)
                mock_handle_transfer_flow.return_value = None
                
                # Test the actual response
                response = await generate_ai_reply(test_chat_id, "send 5k to mella")
                
                print(f"Response: {response}")
                
                # Verify the response shows beneficiary found
                assert isinstance(response, str), "Response should be a string"
                assert "found" in response.lower(), "Should mention beneficiary found"
                assert "mella" in response.lower(), "Should mention Mella"
                assert "access bank" in response.lower(), "Should show bank name"
                assert "0123456789" in response, "Should show account number"
                assert ("5,000" in response or "5000" in response), "Should show amount"
                assert ("proceed" in response.lower() or "confirm" in response.lower()), "Should ask for confirmation"
                
                print("✅ Response recognizes saved beneficiary and is conversational!")
            
            print("\n3️⃣ Testing generic transfer request - should be helpful, not robotic")
            
            with patch('main.check_virtual_account', return_value=mock_virtual_account), \
                 patch('main.get_supabase_client') as mock_supabase, \
                 patch('main.save_chat_message', new_callable=AsyncMock), \
                 patch('main.detect_intent') as mock_detect_intent, \
                 patch('main.handle_transfer_flow') as mock_handle_transfer_flow, \
                 patch('openai.ChatCompletion.create') as mock_openai_create:
                
                # Configure mocks
                mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user_data]
                
                # Mock OpenAI response
                mock_openai_create.return_value = {
                    'choices': [{'message': {'content': 'Fallback response'}}]
                }
                
                # Mock intent detection for generic transfer
                mock_detect_intent.return_value = {
                    "intent": "transfer",
                    "details": {}
                }
                
                # Mock that handle_transfer_flow doesn't handle it (returns None)
                mock_handle_transfer_flow.return_value = None
                
                # Test the actual response
                response = await generate_ai_reply(test_chat_id, "I want to transfer money")
                
                print(f"Response: {response}")
                
                # Verify the response is helpful and conversational
                assert isinstance(response, str), "Response should be a string"
                assert ("send money" in response.lower() or "transfer" in response.lower()), "Should be about transfers"
                assert ("example" in response.lower() or "like" in response.lower()), "Should give examples"
                # Should NOT contain the old robotic template
                assert "Please provide the recipient's complete details:" not in response, "Should not be robotic"
                assert "• Full name (as registered with bank)" not in response, "Should not use bullet points template"
                
                print("✅ Response is helpful and conversational, not robotic!")
        
        print("\n🎉 TRANSFER FLOW IMPROVEMENTS: SUCCESS!")
        print("✅ Sofi now checks beneficiaries BEFORE asking for account details")
        print("✅ Responses are conversational, not robotic templates")
        print("✅ Better user experience when transferring to saved contacts")
        print("✅ Natural language understanding enhanced for transfers")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print("❌ TRANSFER FLOW IMPROVEMENTS: FAILED!")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_transfer_improvements())
    if success:
        print("\n🚀 ALL TESTS PASSED! Sofi's transfer responses are now much more intelligent!")
    else:
        print("\n💥 TESTS FAILED! Issues need to be addressed.")
