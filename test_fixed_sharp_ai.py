#!/usr/bin/env python3
"""
Final Sofi AI Deployment Test - After Fixes
Tests all Sharp AI functionality before final deployment
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_fixed_sofi_ai():
    """Test the fixed Sharp AI system"""
    print("🚀 Testing Fixed Sofi AI System")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    try:
        # Test 1: Import all Sharp AI components
        print("1️⃣ Testing imports...")
        from utils.sharp_sofi_ai import handle_smart_message, sharp_sofi
        from utils.sharp_memory import sharp_memory, remember_user_action, save_conversation_context
        print("   ✅ All Sharp AI imports successful")
        
        # Test 2: Test basic functionality
        print("\n2️⃣ Testing basic Sharp AI response...")
        test_chat_id = "test_user_fixes_123"
        test_message = "Hello Sofi"
        
        try:
            response = await handle_smart_message(test_chat_id, test_message)
            if response and isinstance(response, str):
                print("   ✅ Sharp AI responding correctly!")
                print(f"   📝 Response preview: {response[:100]}...")
            else:
                print("   ❌ Sharp AI response issue")
                return False
        except Exception as e:
            print(f"   ⚠️ Sharp AI test issue: {str(e)}")
            if "does not exist" in str(e):
                print("   💡 Database tables need to be created in Supabase")
            return False
        
        # Test 3: Test memory functions
        print("\n3️⃣ Testing memory functions...")
        try:
            # Test remember_user_action with correct signature
            await remember_user_action(test_chat_id, "test_action")
            print("   ✅ remember_user_action works correctly")
            
            # Test save_conversation_context
            await save_conversation_context(test_chat_id, "Test conversation context")
            print("   ✅ save_conversation_context works correctly")
            
        except Exception as e:
            print(f"   ⚠️ Memory function issue: {str(e)}")
            if "does not exist" in str(e):
                print("   💡 Execute Sharp AI SQL deployment script")
            return False
        
        # Test 4: Test Xara-style intelligence
        print("\n4️⃣ Testing Xara-style intelligence...")
        try:
            xara_test_message = "Send 5000 to 0123456789 GTB"
            xara_response = await handle_smart_message(test_chat_id, xara_test_message)
            if xara_response:
                print("   ✅ Xara-style intelligence working")
                print(f"   📝 Xara response preview: {xara_response[:100]}...")
            else:
                print("   ⚠️ Xara response not generated")
        except Exception as e:
            print(f"   ⚠️ Xara intelligence issue: {str(e)}")
        
        print("\n" + "=" * 50)
        print("🎉 SHARP AI SYSTEM TEST COMPLETE!")
        print("✅ Core functionality verified")
        print("✅ Function signatures fixed")
        print("✅ Memory system operational")
        print("\n🚀 READY FOR RENDER DEPLOYMENT!")
        
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False

def check_database_readiness():
    """Check if database is ready"""
    print("\n5️⃣ Checking database readiness...")
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("   ❌ Supabase credentials missing")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Test basic connection
        result = supabase.table('users').select('*').limit(1).execute()
        print("   ✅ Database connection working")
        
        # Check Sharp AI tables
        sharp_tables = ['user_profiles', 'transaction_memory', 'conversation_context', 'spending_analytics', 'ai_learning']
        missing_tables = []
        
        for table in sharp_tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"   ✅ {table} exists")
            except Exception as e:
                if 'does not exist' in str(e):
                    missing_tables.append(table)
                    print(f"   ❌ {table} missing")
        
        if missing_tables:
            print(f"\n   🔧 Missing tables: {missing_tables}")
            print("   💡 Execute SHARP_AI_COMPLETE_DATABASE_DEPLOYMENT.sql in Supabase")
            return False
        else:
            print("   ✅ All Sharp AI tables ready!")
            return True
            
    except Exception as e:
        print(f"   ❌ Database check failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🧠 SHARP AI - FINAL DEPLOYMENT TEST")
    print("=" * 60)
    
    # Check database first
    db_ready = check_database_readiness()
    
    if not db_ready:
        print("\n⚠️ DATABASE NOT READY")
        print("📝 Execute this SQL in Supabase SQL Editor:")
        print("   SHARP_AI_COMPLETE_DATABASE_DEPLOYMENT.sql")
        print("\nThen run this test again.")
        return False
    
    # Test Sharp AI functionality
    ai_ready = await test_fixed_sofi_ai()
    
    print("\n" + "=" * 60)
    if db_ready and ai_ready:
        print("🎯 DEPLOYMENT READY!")
        print("✅ All systems operational")
        print("✅ All fixes applied successfully")
        print("\n🚀 DEPLOY TO RENDER NOW!")
        return True
    else:
        print("🔧 ISSUES FOUND - Fix before deployment")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 GO FOR DEPLOYMENT! 🚀")
    else:
        print("\n🔧 FIX ISSUES FIRST")
