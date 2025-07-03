"""
Try to create a minimal transaction record to see what columns work
"""

import os
from datetime import datetime
from supabase import create_client

def test_minimal_transaction():
    """Try to insert minimal transaction to see what columns work"""
    
    try:
        # Create Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("🧪 Testing Minimal Transaction Insert...")
        print("=" * 50)
        
        # Try minimal data first
        minimal_data = {
            "amount": 100.0,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        print("1️⃣ Trying minimal data:", minimal_data)
        try:
            result = supabase.table("bank_transactions").insert(minimal_data).execute()
            print("✅ Minimal insert worked!")
            print(f"   Inserted: {result.data}")
            
            # Delete the test record
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    supabase.table("bank_transactions").delete().eq("id", record_id).execute()
                    print("🗑️ Test record deleted")
                    
        except Exception as e:
            print(f"❌ Minimal insert failed: {e}")
        
        # Try adding more fields one by one
        fields_to_test = [
            ("sender_telegram_id", "5495194750"),
            ("recipient_account", "8104965538"),
            ("recipient_name", "Test Recipient"),
            ("bank_code", "999992"),
            ("bank_name", "OPay"),
            ("narration", "Test transfer"),
            ("transfer_code", "TRF_test123"),
            ("balance_before", 1000.0),
            ("balance_after", 900.0),
            ("transaction_id", "test_txn_123"),
            ("user_id", "5495194750"),
            ("type", "transfer_out"),
            ("fee", 20.0)
        ]
        
        working_data = minimal_data.copy()
        
        for field_name, field_value in fields_to_test:
            test_data = working_data.copy()
            test_data[field_name] = field_value
            
            print(f"\n2️⃣ Testing with {field_name}: {field_value}")
            try:
                result = supabase.table("bank_transactions").insert(test_data).execute()
                print(f"✅ {field_name} works!")
                working_data[field_name] = field_value
                
                # Delete the test record
                if result.data:
                    record_id = result.data[0].get('id')
                    if record_id:
                        supabase.table("bank_transactions").delete().eq("id", record_id).execute()
                        
            except Exception as e:
                print(f"❌ {field_name} failed: {e}")
        
        print(f"\n✅ Working columns: {list(working_data.keys())}")
        print(f"❌ Failed columns: {[field[0] for field in fields_to_test if field[0] not in working_data]}")
        
        return working_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

if __name__ == "__main__":
    test_minimal_transaction()
