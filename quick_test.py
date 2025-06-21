"""Simple test to verify fixes"""
print("🚀 TESTING SOFI AI FIXES")
print("=" * 30)

# Test 1: Main syntax
print("\n1. Testing main.py syntax...")
try:
    import main
    print("✅ main.py loads without syntax errors")
except Exception as e:
    print(f"❌ Syntax error: {e}")

# Test 2: Banks database
print("\n2. Testing banks database...")
try:
    from utils.nigerian_banks import NIGERIAN_BANKS
    total = len(NIGERIAN_BANKS)
    fintechs = [b for b in NIGERIAN_BANKS.values() if b.get('type') == 'fintech']
    print(f"✅ {total} banks loaded ({len(fintechs)} fintechs)")
except Exception as e:
    print(f"❌ Banks error: {e}")

# Test 3: Monnify API
print("\n3. Testing Monnify API...")
try:
    from utils.real_monnify_transfer import MonnifyTransferAPI
    api = MonnifyTransferAPI()
    print("✅ Monnify API class loads")
except Exception as e:
    print(f"❌ Monnify error: {e}")

print("\n🎯 BASIC TESTS COMPLETE")
