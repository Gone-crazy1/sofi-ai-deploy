#!/usr/bin/env python3
"""
Enhanced Notification System Test

Test script for the comprehensive deposit and transfer alert system
"""

import os
import sys
import asyncio
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from utils.notification_service import NotificationService

async def test_deposit_notification():
    """Test deposit notification functionality"""
    print("🏦 Testing Deposit Notification...")
    
    notification_service = NotificationService()
    
    # Mock user data
    user_data = {
        "user_id": "test_user_123",
        "chat_id": "test_chat_123",  # Replace with your actual chat_id for testing
        "account_number": "1234567890"
    }
    
    # Mock transaction data
    transaction_data = {
        "amount": 5000.00,
        "account_number": "1234567890",
        "reference": "TXN_TEST_001",
        "sender_name": "John Doe",
        "sender_bank": "First Bank",
        "status": "success"
    }
    
    try:
        result = await notification_service.send_deposit_alert(user_data, transaction_data)
        if result:
            print("  ✅ Deposit notification test passed")
        else:
            print("  ❌ Deposit notification test failed")
        return result
    except Exception as e:
        print(f"  ❌ Deposit notification error: {e}")
        return False

async def test_transfer_notification():
    """Test transfer notification functionality"""
    print("\n💸 Testing Transfer Notification...")
    
    notification_service = NotificationService()
    
    user_data = {
        "user_id": "test_user_123",
        "chat_id": "test_chat_123",
        "account_number": "1234567890"
    }
    
    transaction_data = {
        "amount": 2500.00,
        "recipient_name": "Jane Smith",
        "recipient_bank": "Access Bank",
        "recipient_account": "0987654321",
        "reference": "TXN_TEST_002",
        "status": "successful"
    }
    
    try:
        result = await notification_service.send_transfer_alert(user_data, transaction_data)
        if result:
            print("  ✅ Transfer notification test passed")
        else:
            print("  ❌ Transfer notification test failed")
        return result
    except Exception as e:
        print(f"  ❌ Transfer notification error: {e}")
        return False

async def test_airtime_notification():
    """Test airtime notification functionality"""
    print("\n📱 Testing Airtime Notification...")
    
    notification_service = NotificationService()
    
    user_data = {
        "user_id": "test_user_123",
        "chat_id": "test_chat_123",
        "account_number": "1234567890"
    }
    
    transaction_data = {
        "amount": 500.00,
        "phone_number": "+2348123456789",
        "network": "MTN",
        "reference": "AIR_TEST_001",
        "status": "success"
    }
    
    try:
        result = await notification_service.send_airtime_alert(user_data, transaction_data)
        if result:
            print("  ✅ Airtime notification test passed")
        else:
            print("  ❌ Airtime notification test failed")
        return result
    except Exception as e:
        print(f"  ❌ Airtime notification error: {e}")
        return False

async def test_low_balance_alert():
    """Test low balance alert functionality"""
    print("\n⚠️ Testing Low Balance Alert...")
    
    notification_service = NotificationService()
    
    user_data = {
        "user_id": "test_user_123",
        "chat_id": "test_chat_123",
        "account_number": "1234567890"
    }
    
    try:
        result = await notification_service.send_low_balance_alert(user_data, 500.00, 1000.00)
        if result:
            print("  ✅ Low balance alert test passed")
        else:
            print("  ❌ Low balance alert test failed")
        return result
    except Exception as e:
        print(f"  ❌ Low balance alert error: {e}")
        return False

async def test_daily_summary():
    """Test daily summary functionality"""
    print("\n📊 Testing Daily Summary...")
    
    notification_service = NotificationService()
    
    user_data = {
        "user_id": "test_user_123",
        "chat_id": "test_chat_123",
        "account_number": "1234567890"
    }
    
    try:
        result = await notification_service.send_daily_summary(user_data)
        if result:
            print("  ✅ Daily summary test passed")
        else:
            print("  ❌ Daily summary test failed")
        return result
    except Exception as e:
        print(f"  ❌ Daily summary error: {e}")
        return False

def test_currency_formatting():
    """Test currency formatting utility"""
    print("\n💰 Testing Currency Formatting...")
    
    notification_service = NotificationService()
    
    test_cases = [
        (1000.00, "₦1,000.00"),
        (25000.50, "₦25,000.50"),
        (1000000, "₦1,000,000.00"),
        (0.50, "₦0.50")
    ]
    
    all_passed = True
    for amount, expected in test_cases:
        result = notification_service.format_currency(amount)
        if result == expected:
            print(f"  ✅ {amount} → {result}")
        else:
            print(f"  ❌ {amount} → {result} (expected {expected})")
            all_passed = False
    
    return all_passed

def test_emoji_functions():
    """Test emoji utility functions"""
    print("\n😄 Testing Emoji Functions...")
    
    notification_service = NotificationService()
    
    # Test transaction emojis
    transaction_tests = [
        ("credit", "💰"),
        ("debit", "💸"),
        ("transfer", "📤"),
        ("airtime", "📱"),
        ("unknown", "💳")
    ]
    
    # Test status emojis  
    status_tests = [
        ("success", "✅"),
        ("failed", "❌"),
        ("pending", "⏳"),
        ("unknown", "ℹ️")
    ]
    
    all_passed = True
    
    print("  Transaction Emojis:")
    for transaction_type, expected in transaction_tests:
        result = notification_service.get_transaction_emoji(transaction_type)
        if result == expected:
            print(f"    ✅ {transaction_type} → {result}")
        else:
            print(f"    ❌ {transaction_type} → {result} (expected {expected})")
            all_passed = False
    
    print("  Status Emojis:")
    for status, expected in status_tests:
        result = notification_service.get_status_emoji(status)
        if result == expected:
            print(f"    ✅ {status} → {result}")
        else:
            print(f"    ❌ {status} → {result} (expected {expected})")
            all_passed = False
    
    return all_passed

async def run_notification_tests():
    """Run all notification system tests"""
    print("🚀 Starting Enhanced Notification System Tests")
    print("=" * 60)
    
    # Test utility functions first
    currency_test = test_currency_formatting()
    emoji_test = test_emoji_functions()
    
    # Test notification functions (these require Telegram bot token)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not telegram_token:
        print("\n⚠️ TELEGRAM_BOT_TOKEN not found - skipping Telegram notification tests")
        print("   To test notifications, set your bot token in environment variables")
        
        # Summary for utility tests only
        print("\n" + "=" * 60)
        print("📊 UTILITY TESTS SUMMARY")
        print("=" * 60)
        print(f"{'✅ PASS' if currency_test else '❌ FAIL':<8} Currency Formatting")
        print(f"{'✅ PASS' if emoji_test else '❌ FAIL':<8} Emoji Functions")
        
        return currency_test and emoji_test
    
    # Run notification tests
    print(f"\n🤖 Telegram bot token found: ***{telegram_token[-8:]}")
    print("📝 Note: Update test_chat_123 with your actual chat_id to receive test messages")
    
    deposit_test = await test_deposit_notification()
    transfer_test = await test_transfer_notification()
    airtime_test = await test_airtime_notification()
    low_balance_test = await test_low_balance_alert()
    daily_summary_test = await test_daily_summary()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"{'✅ PASS' if currency_test else '❌ FAIL':<8} Currency Formatting")
    print(f"{'✅ PASS' if emoji_test else '❌ FAIL':<8} Emoji Functions")
    print(f"{'✅ PASS' if deposit_test else '❌ FAIL':<8} Deposit Notifications")
    print(f"{'✅ PASS' if transfer_test else '❌ FAIL':<8} Transfer Notifications")
    print(f"{'✅ PASS' if airtime_test else '❌ FAIL':<8} Airtime Notifications")
    print(f"{'✅ PASS' if low_balance_test else '❌ FAIL':<8} Low Balance Alerts")
    print(f"{'✅ PASS' if daily_summary_test else '❌ FAIL':<8} Daily Summary")
    
    total_tests = 7
    passed_tests = sum([
        currency_test, emoji_test, deposit_test, 
        transfer_test, airtime_test, low_balance_test, daily_summary_test
    ])
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All notification tests passed! Enhanced alert system is ready!")
    else:
        print("⚠️ Some tests failed. Check configuration and try again.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    asyncio.run(run_notification_tests())
