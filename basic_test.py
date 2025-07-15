import sys
print("Python version:", sys.version)
print("Testing basic import...")

try:
    import uuid
    print("✅ uuid imported")
    
    import os
    print("✅ os imported")
    
    import datetime
    print("✅ datetime imported")
    
    print("✅ All basic imports successful")
    
except Exception as e:
    print("❌ Import error:", e)
