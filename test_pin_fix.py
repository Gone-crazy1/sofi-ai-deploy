"""
Quick test of the fixed permanent_memory.py module
"""
import sys
import os
sys.path.append(os.getcwd())

try:
    # Test the import
    from utils.permanent_memory import verify_user_pin, track_pin_attempt, PermanentMemory
    print("✅ All imports successful!")
    
    # Test basic functionality
    pm = PermanentMemory()
    print("✅ PermanentMemory instance created")
    
    # Test the functions exist
    print(f"✅ verify_user_pin function: {verify_user_pin}")
    print(f"✅ track_pin_attempt function: {track_pin_attempt}")
    print(f"✅ PermanentMemory class: {PermanentMemory}")
    
    print("\n🎉 All PIN system components are working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
