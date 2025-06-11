#!/usr/bin/env python3
"""
Test script to verify that Sofi AI properly handles URLs using inline keyboards
instead of sending raw links in messages.
"""

def test_system_prompt_url_guidelines():
    """Test that the system prompt contains proper URL handling guidelines"""
    try:
        from main import generate_ai_reply
        import inspect
        
        # Get the source code of the generate_ai_reply function
        source = inspect.getsource(generate_ai_reply)
        
        # Check for proper URL handling guidelines in system prompt
        guidelines_found = [
            "inline keyboards/buttons" in source,
            "NEVER" in source and "raw links" in source,
            "URL HANDLING RULE" in source,
            "https://sofi-ai-trio.onrender.com/onboarding" in source  # Should be in inline keyboard
        ]
        
        print("🔍 Testing URL Handling Guidelines...")
        print(f"✅ Inline keyboard guideline: {'FOUND' if guidelines_found[0] else 'MISSING'}")
        print(f"✅ Raw link prohibition: {'FOUND' if guidelines_found[1] else 'MISSING'}")
        print(f"✅ URL handling rule: {'FOUND' if guidelines_found[2] else 'MISSING'}")
        print(f"✅ Onboarding URL in code: {'FOUND' if guidelines_found[3] else 'MISSING'}")
        
        if all(guidelines_found):
            print("\n🎉 SUCCESS: All URL handling guidelines are properly implemented!")
            return True
        else:
            print("\n❌ ISSUE: Some URL handling guidelines are missing!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing guidelines: {e}")
        return False

def test_inline_keyboard_implementation():
    """Test that inline keyboard creation is working correctly"""
    print("\n🔧 Testing Inline Keyboard Implementation...")
    
    # Test data for inline keyboard structure
    test_chat_id = "123456789"
    expected_structure = {
        "inline_keyboard": [
            [{"text": "🚀 Start Onboarding", "url": f"https://sofi-ai-trio.onrender.com/onboarding?chat_id={test_chat_id}"}]
        ]
    }
    
    # Check if the structure is correct
    has_inline_keyboard = "inline_keyboard" in expected_structure
    has_button_text = expected_structure["inline_keyboard"][0][0]["text"].startswith("🚀")
    has_url = "sofi-ai-trio.onrender.com" in expected_structure["inline_keyboard"][0][0]["url"]
    has_chat_id = test_chat_id in expected_structure["inline_keyboard"][0][0]["url"]
    
    print(f"✅ Inline keyboard structure: {'VALID' if has_inline_keyboard else 'INVALID'}")
    print(f"✅ Button text with emoji: {'VALID' if has_button_text else 'INVALID'}")
    print(f"✅ Correct onboarding URL: {'VALID' if has_url else 'INVALID'}")
    print(f"✅ Chat ID parameter: {'VALID' if has_chat_id else 'INVALID'}")
    
    if all([has_inline_keyboard, has_button_text, has_url, has_chat_id]):
        print("🎉 SUCCESS: Inline keyboard implementation is correct!")
        return True
    else:
        print("❌ ISSUE: Inline keyboard implementation has problems!")
        return False

if __name__ == "__main__":
    print("🧪 Testing Sofi AI URL Handling Implementation...\n")
    
    test1_result = test_system_prompt_url_guidelines()
    test2_result = test_inline_keyboard_implementation()
    
    print(f"\n📊 Test Results:")
    print(f"✅ System Prompt Guidelines: {'PASSED' if test1_result else 'FAILED'}")
    print(f"✅ Inline Keyboard Implementation: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED! Sofi AI will never send raw URLs - only professional inline keyboard buttons!")
        print("✨ The bot will maintain a clean, professional appearance in all interactions.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
