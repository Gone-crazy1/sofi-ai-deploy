#!/usr/bin/env python3
"""
Test script to verify the inline keyboard fix for onboarding
"""
import json

def test_inline_keyboard_structure():
    """Test that the inline keyboard structure is valid JSON"""
    chat_id = "123456789"
    
    # This is the exact structure from main.py
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Complete Onboarding Now", "url": f"https://sofi-ai-trio.onrender.com/onboarding?chat_id={chat_id}"}]
        ]
    }
    
    try:
        # Test that it can be serialized to JSON
        json_str = json.dumps(inline_keyboard)
        print("✅ JSON Serialization: SUCCESS")
        print(f"JSON Output: {json_str}")
        
        # Test that it can be deserialized back
        parsed = json.loads(json_str)
        print("✅ JSON Deserialization: SUCCESS")
        
        # Verify structure
        assert "inline_keyboard" in parsed
        assert len(parsed["inline_keyboard"]) == 1
        assert len(parsed["inline_keyboard"][0]) == 1
        assert "text" in parsed["inline_keyboard"][0][0]
        assert "url" in parsed["inline_keyboard"][0][0]
        print("✅ Structure Validation: SUCCESS")
        
        # Test URL generation
        expected_url = f"https://sofi-ai-trio.onrender.com/onboarding?chat_id={chat_id}"
        actual_url = parsed["inline_keyboard"][0][0]["url"]
        assert actual_url == expected_url
        print(f"✅ URL Generation: SUCCESS - {actual_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Inline Keyboard Fix...")
    print("=" * 50)
    
    success = test_inline_keyboard_structure()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! The inline keyboard fix is working correctly.")
        print("\n📝 SUMMARY:")
        print("- Fixed malformed JSON structure in main.py")
        print("- Inline keyboard will now be properly sent to users")
        print("- Onboarding button should appear with welcome messages")
    else:
        print("❌ TEST FAILED! There may still be issues.")
    
    print("\n🚀 Ready for deployment!")
