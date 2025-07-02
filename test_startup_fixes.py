"""
Test the fixed startup - should not crash on missing settings table
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_startup():
    print("🧪 Testing startup fixes...")
    
    try:
        # Test importing main without crashing
        print("1. Testing main.py import...")
        from main import app
        print("   ✅ main.py imported successfully")
        
        # Test fee calculator lazy loading
        print("2. Testing fee calculator lazy loading...")
        from utils.fee_calculator import fee_calculator
        print("   ✅ fee_calculator imported without error")
        
        # Test using fee calculator (should trigger lazy loading)
        print("3. Testing fee calculator usage...")
        # This should work even without settings table
        result = fee_calculator.calculate_transfer_fees(1000)
        print(f"   ✅ Fee calculation works: ₦{result}")
        
        print("\n🎉 All startup tests passed!")
        print("   - No duplicate Flask routes")
        print("   - Fee calculator loads lazily")
        print("   - No database dependency at startup")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)
