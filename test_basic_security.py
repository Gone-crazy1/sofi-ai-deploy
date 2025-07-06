"""
SIMPLE SECURITY TEST
==================
Quick test to verify basic security components
"""

def test_basic_imports():
    """Test basic imports work"""
    try:
        import sys
        import os
        
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        print("Testing security imports...")
        
        try:
            from utils.security_monitor import SecurityMonitor
            print("✅ SecurityMonitor imported")
        except Exception as e:
            print(f"❌ SecurityMonitor import failed: {e}")
            return False
        
        try:
            from utils.security import SecurityManager
            print("✅ SecurityManager imported")
        except Exception as e:
            print(f"❌ SecurityManager import failed: {e}")
            return False
        
        try:
            from main import app
            print("✅ Flask app imported")
        except Exception as e:
            print(f"❌ Flask app import failed: {e}")
            return False
        
        print("✅ All basic imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔒 BASIC SECURITY TEST")
    print("=" * 30)
    
    if test_basic_imports():
        print("\n🎉 Basic security components are working!")
    else:
        print("\n❌ Basic security components have issues")
