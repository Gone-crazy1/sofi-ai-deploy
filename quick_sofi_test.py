"""
⚡ QUICK SOFI AI MODULE TEST
==========================

Test that all Sofi components load and work
"""

def test_modules():
    """Test that all modules import correctly"""
    print("📦 Testing Module Imports...")
    
    modules_to_test = [
        ("main", "Main Sofi AI module"),
        ("utils.nigerian_banks", "Nigerian banks database"),
        ("utils.enhanced_intent_detection", "Enhanced NLP"),
        ("utils.real_monnify_transfer", "Monnify API"),
        ("utils.admin_command_handler", "Admin handler"),
        ("utils.secure_transfer_handler", "Transfer handler")
    ]
    
    passed = 0
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}")
            passed += 1
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    print(f"\n📊 Module Test: {passed}/{len(modules_to_test)} passed")
    return passed == len(modules_to_test)

def test_banks_database():
    """Test banks database functionality"""
    print("\n🏦 Testing Banks Database...")
    
    try:
        from utils.nigerian_banks import NIGERIAN_BANKS, get_bank_by_name
        
        total_banks = len(NIGERIAN_BANKS)
        print(f"📊 Total banks: {total_banks}")
        
        # Test some popular banks
        test_banks = ['gtbank', 'access', 'opay', 'kuda']
        found = 0
        
        for bank in test_banks:
            bank_info = get_bank_by_name(bank)
            if bank_info:
                print(f"✅ {bank_info['name']} (Code: {bank_info['code']})")
                found += 1
            else:
                print(f"❌ {bank} not found")
        
        success = total_banks >= 50 and found == len(test_banks)
        print(f"🎯 Banks test: {'✅ PASSED' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Banks test failed: {e}")
        return False

def test_transfer_detection():
    """Test transfer intent detection"""
    print("\n🧠 Testing Transfer Detection...")
    
    try:
        from utils.enhanced_intent_detection import EnhancedIntentDetector
        
        detector = EnhancedIntentDetector()
        
        # Test messages from the screenshot
        test_messages = [
            ("8104611794 Opay", True),           # Should detect transfer
            ("Send 5k to GTBank", True),        # Should detect transfer  
            ("Hello how are you", False),       # Should NOT detect transfer
            ("What's my balance", False),       # Should NOT detect transfer
            ("Transfer 2000 to access", True)   # Should detect transfer
        ]
        
        correct = 0
        for message, should_detect in test_messages:
            result = detector.detect_transfer_intent(message)
            is_correct = bool(result) == should_detect
            status = "✅" if is_correct else "❌"
            expected = "transfer" if should_detect else "non-transfer"
            
            print(f"{status} '{message[:20]}...' -> {expected}")
            if is_correct:
                correct += 1
        
        success = correct == len(test_messages)
        print(f"🎯 Transfer detection: {'✅ PASSED' if success else '❌ FAILED'} ({correct}/{len(test_messages)})")
        return success
        
    except Exception as e:
        print(f"❌ Transfer detection test failed: {e}")
        return False

def test_sofi_functions():
    """Test key Sofi functions exist"""
    print("\n🤖 Testing Sofi Functions...")
    
    try:
        import main
        
        required_functions = [
            "create_sofi_ai_response_with_custom_prompt",
            "handle_incoming_message", 
            "generate_ai_reply"
        ]
        
        found = 0
        for func_name in required_functions:
            if hasattr(main, func_name):
                print(f"✅ {func_name}")
                found += 1
            else:
                print(f"❌ {func_name} not found")
        
        success = found == len(required_functions)
        print(f"🎯 Functions test: {'✅ PASSED' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Functions test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SOFI AI QUICK TEST")
    print("=" * 30)
    
    tests = [
        ("Module Imports", test_modules),
        ("Banks Database", test_banks_database), 
        ("Transfer Detection", test_transfer_detection),
        ("Sofi Functions", test_sofi_functions)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
    
    print("\n" + "=" * 30)
    print(f"🎯 OVERALL RESULT: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🚀 ✅ SOFI AI IS READY TO CHAT!")
        print("💬 All core components working")
        print("🏦 Nigerian banks support ready")
        print("🧠 Enhanced NLP working")
        print("🔧 All functions available")
    else:
        print("⚠️ Some issues found - check failures above")

if __name__ == "__main__":
    main()
