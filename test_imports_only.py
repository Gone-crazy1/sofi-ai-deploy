"""
Test imports without connecting to database
"""
import sys
import os
sys.path.append(os.getcwd())

# Set dummy environment variables
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_key"

try:
    # Test the import
    from utils.permanent_memory import verify_user_pin, track_pin_attempt, PermanentMemory
    print("✅ All imports successful!")
    
    # Test the functions exist
    print(f"✅ verify_user_pin function: {verify_user_pin}")
    print(f"✅ track_pin_attempt function: {track_pin_attempt}")
    print(f"✅ PermanentMemory class: {PermanentMemory}")
    
    print("\n🎉 All PIN system components are available for import!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
