#!/usr/bin/env python3
"""
SOFI AI END-TO-END SYSTEM TEST
==============================
Comprehensive test to verify all systems are working correctly before deployment
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime
import requests
from typing import Dict, Any, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SofiSystemTester:
    """Comprehensive system tester for Sofi AI"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TEST": "🧪"
        }.get(level, "📝")
        
        print(f"{symbol} [{timestamp}] {message}")
        
        if level == "ERROR":
            self.errors.append(message)
        elif level == "WARNING":
            self.warnings.append(message)
    
    def test_imports(self):
        """Test all critical imports"""
        self.log("Testing critical imports...", "TEST")
        
        try:
            # Test Flask app imports
            from main import app
            self.log("✓ Flask app imported successfully", "SUCCESS")
            
            # Test security system
            from utils.security import init_security
            from utils.security_monitor import security_monitor
            self.log("✓ Security system imported successfully", "SUCCESS")
            
            # Test assistant
            from assistant import get_assistant
            assistant = get_assistant()
            self.log("✓ AI Assistant imported successfully", "SUCCESS")
            
            # Test transfer functions
            from functions.transfer_functions import send_money
            from functions.verification_functions import verify_account_name
            self.log("✓ Transfer functions imported successfully", "SUCCESS")
            
            # Test security functions
            from functions.security_functions import verify_pin
            self.log("✓ Security functions imported successfully", "SUCCESS")
            
            self.test_results['imports'] = True
            
        except Exception as e:
            self.log(f"Import test failed: {str(e)}", "ERROR")
            self.test_results['imports'] = False
    
    def test_environment_variables(self):
        """Test required environment variables"""
        self.log("Testing environment variables...", "TEST")
        
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'OPENAI_API_KEY',
            'PAYSTACK_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"Missing environment variables: {', '.join(missing_vars)}", "ERROR")
            self.test_results['environment'] = False
        else:
            self.log("✓ All required environment variables present", "SUCCESS")
            self.test_results['environment'] = True
    
    def test_security_system(self):
        """Test security system functionality"""
        self.log("Testing security system...", "TEST")
        
        try:
            from utils.security_monitor import security_monitor
            
            # Test threat detection
            threat = security_monitor.detect_suspicious_activity(
                ip="192.168.1.100",
                path="/wp-admin/setup-config.php",
                user_agent="python-requests/2.25.1",
                method="GET"
            )
            
            if threat:
                self.log("✓ Threat detection working", "SUCCESS")
                self.test_results['security_detection'] = True
            else:
                self.log("Threat detection not working as expected", "WARNING")
                self.test_results['security_detection'] = False
            
            # Test security stats
            stats = security_monitor.get_security_stats()
            self.log(f"✓ Security stats: {stats}", "SUCCESS")
            
            self.test_results['security_system'] = True
            
        except Exception as e:
            self.log(f"Security system test failed: {str(e)}", "ERROR")
            self.test_results['security_system'] = False
    
    async def test_account_verification(self):
        """Test account name verification"""
        self.log("Testing account verification...", "TEST")
        
        try:
            from functions.verification_functions import verify_account_name
            
            # Test with a real account (use a test account)
            result = await verify_account_name("0123456789", "GTBank")
            
            if isinstance(result, dict):
                self.log("✓ Account verification function working", "SUCCESS")
                self.test_results['account_verification'] = True
            else:
                self.log("Account verification returned unexpected result", "WARNING")
                self.test_results['account_verification'] = False
                
        except Exception as e:
            self.log(f"Account verification test failed: {str(e)}", "ERROR")
            self.test_results['account_verification'] = False
    
    async def test_transfer_flow(self):
        """Test transfer flow without actual money movement"""
        self.log("Testing transfer flow (without actual transfer)...", "TEST")
        
        try:
            from functions.transfer_functions import send_money
            
            # Test transfer preparation (should fail at PIN stage, which is expected)
            result = await send_money(
                chat_id="test_user_123",
                amount=100,
                account_number="0123456789",
                bank_name="GTBank",
                narration="Test transfer"
                # No PIN provided - should trigger web PIN flow
            )
            
            if isinstance(result, dict) and result.get("show_web_pin"):
                self.log("✓ Transfer flow working - web PIN flow triggered", "SUCCESS")
                self.test_results['transfer_flow'] = True
            else:
                self.log(f"Transfer flow issue: {result}", "WARNING")
                self.test_results['transfer_flow'] = False
                
        except Exception as e:
            self.log(f"Transfer flow test failed: {str(e)}", "ERROR")
            self.test_results['transfer_flow'] = False
    
    def test_template_files(self):
        """Test that template files exist and are valid"""
        self.log("Testing template files...", "TEST")
        
        required_templates = [
            'templates/secure_pin_verification.html',
            'templates/index.html',
            'web_onboarding.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            if not os.path.exists(template):
                missing_templates.append(template)
        
        if missing_templates:
            self.log(f"Missing template files: {', '.join(missing_templates)}", "ERROR")
            self.test_results['templates'] = False
        else:
            self.log("✓ All required template files present", "SUCCESS")
            self.test_results['templates'] = True
    
    def test_onboarding_system(self):
        """Test onboarding system"""
        self.log("Testing onboarding system...", "TEST")
        
        try:
            # Check if web_onboarding.html exists and has correct content
            with open('web_onboarding.html', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for key elements
            if 'telegram_chat_id' in content and 'displayTelegramId' in content:
                self.log("✓ Onboarding template has Telegram ID integration", "SUCCESS")
                self.test_results['onboarding_telegram'] = True
            else:
                self.log("Onboarding template missing Telegram ID integration", "WARNING")
                self.test_results['onboarding_telegram'] = False
                
            # Check for no naked links
            if 'https://t.me/getsofi_bot' in content and 'window.location.href' in content:
                self.log("⚠️ Onboarding may contain naked links - should use Telegram buttons", "WARNING")
                self.test_results['onboarding_links'] = False
            else:
                self.log("✓ Onboarding appears to use proper Telegram integration", "SUCCESS")
                self.test_results['onboarding_links'] = True
                
            self.test_results['onboarding_system'] = True
            
        except Exception as e:
            self.log(f"Onboarding system test failed: {str(e)}", "ERROR")
            self.test_results['onboarding_system'] = False
    
    def test_pin_system(self):
        """Test PIN system"""
        self.log("Testing PIN system...", "TEST")
        
        try:
            # Check if secure_pin_verification.html exists
            if os.path.exists('templates/secure_pin_verification.html'):
                self.log("✓ PIN verification template exists", "SUCCESS")
                self.test_results['pin_template'] = True
            else:
                self.log("PIN verification template missing", "ERROR")
                self.test_results['pin_template'] = False
            
            # Check if old pin-entry.html is removed
            if os.path.exists('templates/pin-entry.html'):
                self.log("⚠️ Legacy pin-entry.html still exists - should be removed", "WARNING")
                self.test_results['pin_cleanup'] = False
            else:
                self.log("✓ Legacy PIN files cleaned up", "SUCCESS")
                self.test_results['pin_cleanup'] = True
                
            # Check if inline PIN keyboard is removed
            if os.path.exists('utils/inline_pin_keyboard.py'):
                self.log("⚠️ Inline PIN keyboard still exists - should be removed", "WARNING")
                self.test_results['inline_pin_cleanup'] = False
            else:
                self.log("✓ Inline PIN keyboard cleaned up", "SUCCESS")
                self.test_results['inline_pin_cleanup'] = True
                
            self.test_results['pin_system'] = True
            
        except Exception as e:
            self.log(f"PIN system test failed: {str(e)}", "ERROR")
            self.test_results['pin_system'] = False
    
    def test_receipt_system(self):
        """Test receipt generation system"""
        self.log("Testing receipt system...", "TEST")
        
        try:
            from utils.receipt_generator import create_transaction_receipt
            
            # Test receipt generation
            receipt_data = {
                'amount': 5000,
                'fee': 25,
                'total_charged': 5025,
                'new_balance': 15000,
                'recipient_name': 'JOHN DOE',
                'bank_name': 'GTBank',
                'account_number': '0123456789',
                'reference': 'TXN123456789',
                'transaction_id': 'test_txn_123',
                'transaction_time': '06/07/2025 10:30 AM',
                'narration': 'Test transfer'
            }
            
            receipt = create_transaction_receipt(receipt_data, "telegram")
            
            if receipt and len(receipt) > 0:
                self.log("✓ Receipt generation working", "SUCCESS")
                self.test_results['receipt_system'] = True
            else:
                self.log("Receipt generation issue", "WARNING")
                self.test_results['receipt_system'] = False
                
        except Exception as e:
            self.log(f"Receipt system test failed: {str(e)}", "ERROR")
            self.test_results['receipt_system'] = False
    
    def test_cleanup_status(self):
        """Test cleanup status - ensure legacy files are removed"""
        self.log("Testing cleanup status...", "TEST")
        
        legacy_files = [
            'templates/onboarding.html',
            'templates/pin-entry.html',
            'utils/inline_pin_keyboard.py'
        ]
        
        found_legacy = []
        for file in legacy_files:
            if os.path.exists(file):
                found_legacy.append(file)
        
        if found_legacy:
            self.log(f"⚠️ Legacy files still exist: {', '.join(found_legacy)}", "WARNING")
            self.test_results['cleanup_status'] = False
        else:
            self.log("✓ All legacy files cleaned up", "SUCCESS")
            self.test_results['cleanup_status'] = True
    
    async def run_all_tests(self):
        """Run all tests"""
        self.log("🧪 STARTING SOFI AI END-TO-END SYSTEM TEST", "TEST")
        self.log("=" * 60, "INFO")
        
        # Run tests
        self.test_imports()
        self.test_environment_variables()
        self.test_security_system()
        await self.test_account_verification()
        await self.test_transfer_flow()
        self.test_template_files()
        self.test_onboarding_system()
        self.test_pin_system()
        self.test_receipt_system()
        self.test_cleanup_status()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        self.log("=" * 60, "INFO")
        self.log("🧪 SOFI AI SYSTEM TEST REPORT", "TEST")
        self.log("=" * 60, "INFO")
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        self.log(f"Tests Passed: {passed}/{total}", "INFO")
        
        # Show detailed results
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}", "INFO")
        
        # Show errors and warnings
        if self.errors:
            self.log(f"❌ ERRORS ({len(self.errors)}):", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        
        if self.warnings:
            self.log(f"⚠️ WARNINGS ({len(self.warnings)}):", "WARNING")
            for warning in self.warnings:
                self.log(f"  - {warning}", "WARNING")
        
        # Final assessment
        if passed == total and not self.errors:
            self.log("🎉 ALL TESTS PASSED! System ready for deployment.", "SUCCESS")
        elif passed >= total * 0.8:  # 80% pass rate
            self.log("⚠️ MOSTLY READY - Address warnings before deployment.", "WARNING")
        else:
            self.log("❌ SYSTEM NOT READY - Critical issues need fixing.", "ERROR")
        
        self.log("=" * 60, "INFO")
        
        return passed == total and not self.errors

async def main():
    """Run the comprehensive system test"""
    tester = SofiSystemTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
