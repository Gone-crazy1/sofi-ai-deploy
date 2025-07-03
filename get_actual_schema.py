"""
Check the actual bank_transactions table schema
"""

import os
from supabase import create_client

def get_table_schema():
    """Get the actual table schema"""
    
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("📋 Getting Actual bank_transactions Schema...")
        print("=" * 60)
        
        # Try to insert with required fields based on error messages
        test_data = {
            "bank_code": "999992",  # Required
            "account_number": "8104965538",  # Required  
            "reference": "TRF_test123",  # Required
            "amount": 100.0,
            "status": "completed",
            "created_at": "2025-07-03T08:40:16.394909"
        }
        
        print("🧪 Testing with required fields:")
        print(f"   {test_data}")
        
        try:
            result = supabase.table("bank_transactions").insert(test_data).execute()
            print("✅ Insert successful!")
            
            if result.data:
                print(f"📄 Inserted record: {result.data[0]}")
                
                # Get all columns from the returned data
                columns = list(result.data[0].keys())
                print(f"📋 Available columns: {columns}")
                
                # Clean up
                record_id = result.data[0].get('id')
                if record_id:
                    supabase.table("bank_transactions").delete().eq("id", record_id).execute()
                    print("🗑️ Test record cleaned up")
                    
                return columns
                
        except Exception as e:
            print(f"❌ Insert failed: {e}")
            
        return []
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    schema = get_table_schema()
    
    if schema:
        print(f"\n✅ FINAL SCHEMA:")
        for col in sorted(schema):
            print(f"   - {col}")
    else:
        print("\n❌ Could not determine schema")
