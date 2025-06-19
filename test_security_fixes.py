"""
🧪 SECURITY FIXES TEST SUITE

Tests the implemented security features:
1. Balance checking prevents overdrafts
2. PIN verification works with user-specific PINs
3. Account lockout works after failed attempts
4. Transaction limits are enforced
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add project path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SecurityTestSuite:
    """Test suite for security fixes"""
    
    def __init__(self):
        self.test_results = []
    
    async def test_balance_checking(self):
        """Test that balance checking prevents overdrafts"""
        print("\n💰 Testing Balance Checking...")
        
        try:
            from utils.permanent_memory import check_sufficient_balance
            
            # Mock user with ₦1000 balance trying to send ₦5000
            with patch('utils.permanent_memory.SecureTransactionValidator.get_user_balance') as mock_balance:
                mock_balance.return_value = {
                    "success": True,
                    "balance": 1000.0,
                    "source": "test"
                }
                
                # Test insufficient balance
                result = await check_sufficient_balance("test_user", 5000.0, include_fees=True)
                
                assert not result["sufficient"], "Should detect insufficient balance"
                assert result["balance"] == 1000.0, "Should return correct balance"
                assert result["shortfall"] > 0, "Should calculate shortfall"
                
                print("   ✅ Insufficient balance detected correctly")
                
                # Test sufficient balance
                result = await check_sufficient_balance("test_user", 500.0, include_fees=True)
                
                assert result["sufficient"], "Should allow transfer with sufficient balance"
                print("   ✅ Sufficient balance allows transfer")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Balance checking test failed: {e}")
            return False
    
    async def test_pin_verification(self):
        """Test secure PIN verification"""
        print("\n🔐 Testing PIN Verification...")
        
        try:
            from utils.permanent_memory import verify_user_pin
            import hashlib
            
            # Mock database with hashed PIN
            correct_pin = "1234"
            hashed_pin = hashlib.sha256(correct_pin.encode()).hexdigest()
            
            with patch('utils.permanent_memory.get_supabase_client') as mock_client:
                mock_client.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
                    {"pin": hashed_pin}
                ]
                
                # Test correct PIN
                result = await verify_user_pin("test_user", "1234")
                assert result == True, "Should accept correct PIN"
                print("   ✅ Correct PIN accepted")
                
                # Test incorrect PIN
                result = await verify_user_pin("test_user", "9999")
                assert result == False, "Should reject incorrect PIN"
                print("   ✅ Incorrect PIN rejected")
                
            return True
            
        except Exception as e:
            print(f"   ❌ PIN verification test failed: {e}")
            return False
    
    async def test_account_lockout(self):
        """Test account lockout after failed attempts"""
        print("\n🔒 Testing Account Lockout...")
        
        try:
            from utils.permanent_memory import track_pin_attempt, is_user_locked
            from datetime import datetime, timedelta
            
            with patch('utils.permanent_memory.get_supabase_client') as mock_client:
                # Mock successful PIN attempt tracking
                mock_client.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
                mock_client.return_value.table.return_value.insert.return_value.execute.return_value = MagicMock()
                mock_client.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
                
                # Test first failed attempt
                result = await track_pin_attempt("test_user", False)
                assert not result.get("locked", False), "Should not lock on first attempt"
                print("   ✅ First failed attempt does not lock account")
                
                # Mock lockout scenario
                locked_until = datetime.now() + timedelta(minutes=15)
                mock_client.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
                    {"locked_until": locked_until.isoformat()}
                ]
                
                # Test account lockout detection
                is_locked = await is_user_locked("test_user")
                assert is_locked == True, "Should detect locked account"
                print("   ✅ Account lockout detected correctly")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Account lockout test failed: {e}")
            return False
    
    async def test_transaction_limits(self):
        """Test transaction limit validation"""
        print("\n📊 Testing Transaction Limits...")
        
        try:
            from utils.permanent_memory import validate_transaction_limits
            
            with patch('utils.permanent_memory.get_supabase_client') as mock_client:
                # Mock no existing transactions today
                mock_client.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
                
                # Test normal transaction
                result = await validate_transaction_limits("test_user", 50000.0)
                assert result["valid"] == True, "Should allow normal transaction"
                print("   ✅ Normal transaction allowed")
                
                # Test oversized transaction (over 500k limit)
                result = await validate_transaction_limits("test_user", 600000.0)
                assert result["valid"] == False, "Should reject oversized transaction"
                assert "single transaction limit" in result["error"].lower(), "Should mention single transaction limit"
                print("   ✅ Oversized transaction rejected")
                
                # Mock 20 transactions today (daily limit)
                mock_client.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value.data = [
                    {"id": i} for i in range(20)
                ]
                
                # Test daily limit exceeded
                result = await validate_transaction_limits("test_user", 10000.0)
                assert result["valid"] == False, "Should reject when daily limit exceeded"
                assert "daily transaction limit" in result["error"].lower(), "Should mention daily limit"
                print("   ✅ Daily limit enforcement working")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Transaction limits test failed: {e}")
            return False
    
    async def test_secure_transfer_handler(self):
        """Test the secure transfer handler integration"""
        print("\n🔐 Testing Secure Transfer Handler...")
        
        try:
            from utils.secure_transfer_handler import handle_secure_transfer_confirmation
            
            # Mock user data and transfer data
            user_data = {"id": "test_user", "first_name": "Test"}
            transfer_data = {
                "amount": 1000,
                "account_number": "1234567890",
                "bank": "Test Bank",
                "recipient_name": "Test Recipient"
            }
            
            # Test cancellation
            with patch('utils.conversation_state.conversation_state') as mock_state:
                result = await handle_secure_transfer_confirmation(
                    "test_chat", "cancel", user_data, transfer_data
                )
                assert "cancelled" in result.lower(), "Should handle cancellation"
                print("   ✅ Transfer cancellation works")
            
            # Test insufficient balance scenario
            with patch('utils.permanent_memory.check_sufficient_balance') as mock_balance:
                mock_balance.return_value = {
                    "sufficient": False,
                    "balance": 500.0,
                    "required": 1050.0,
                    "transfer_amount": 1000.0,
                    "fees": 50.0,
                    "shortfall": 550.0
                }
                
                with patch('utils.secure_transfer_handler.SecureTransferHandler.get_virtual_account') as mock_account:
                    mock_account.return_value = {"accountNumber": "1234", "bankName": "Test Bank"}
                    
                    result = await handle_secure_transfer_confirmation(
                        "test_chat", "1234", user_data, transfer_data
                    )
                    assert "insufficient balance" in result.lower(), "Should detect insufficient balance"
                    assert "550.00" in result, "Should show correct shortfall"
                    print("   ✅ Insufficient balance handling works")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Secure transfer handler test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all security tests"""
        print("🧪 SECURITY FIXES TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Balance Checking", self.test_balance_checking),
            ("PIN Verification", self.test_pin_verification),
            ("Account Lockout", self.test_account_lockout),
            ("Transaction Limits", self.test_transaction_limits),
            ("Secure Transfer Handler", self.test_secure_transfer_handler)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    self.test_results.append(f"✅ {test_name}: PASSED")
                else:
                    self.test_results.append(f"❌ {test_name}: FAILED")
            except Exception as e:
                self.test_results.append(f"❌ {test_name}: ERROR - {e}")
        
        print(f"\n📊 TEST RESULTS:")
        print("=" * 30)
        for result in self.test_results:
            print(result)
        
        print(f"\n🎯 SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL SECURITY TESTS PASSED!")
            print("✅ Users cannot send more than they have")
            print("✅ PIN verification is secure")
            print("✅ Account lockout protection works")
            print("✅ Transaction limits are enforced")
            print("✅ Secure transfer handler is functional")
            
            print("\n🚀 READY FOR PRODUCTION!")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed")
            print("Please review the failed tests before deploying")
            return False

async def main():
    """Run the security test suite"""
    test_suite = SecurityTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n" + "="*50)
        print("STATUS: ✅ SECURITY FIXES VERIFIED")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("STATUS: ❌ SOME TESTS FAILED")
        print("="*50)
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test suite execution error: {e}")
        sys.exit(1)
