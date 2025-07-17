#!/usr/bin/env python3
"""
Create missing pin_attempts table for PIN lockout functionality
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def create_pin_attempts_table():
    """Create the pin_attempts table for tracking PIN attempts and lockouts"""
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Create pin_attempts table using SQL
        sql_query = """
        CREATE TABLE IF NOT EXISTS pin_attempts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            attempt_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            success BOOLEAN NOT NULL,
            ip_address TEXT,
            locked_until TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_pin_attempts_user_id ON pin_attempts(user_id);
        CREATE INDEX IF NOT EXISTS idx_pin_attempts_attempt_time ON pin_attempts(attempt_time);
        CREATE INDEX IF NOT EXISTS idx_pin_attempts_locked_until ON pin_attempts(locked_until);
        
        -- Enable RLS (Row Level Security)
        ALTER TABLE pin_attempts ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policy for authenticated users
        CREATE POLICY IF NOT EXISTS "Users can view their own PIN attempts" ON pin_attempts
            FOR ALL USING (auth.uid() = user_id);
        """
        
        result = supabase.rpc('exec_sql', {'sql': sql_query}).execute()
        
        print("✅ pin_attempts table created successfully!")
        print("✅ Indexes created")
        print("✅ RLS policies applied")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating pin_attempts table: {e}")
        # Try alternative method using direct SQL execution
        try:
            # Alternative: Create table manually using direct SQL
            print("🔄 Trying alternative method...")
            
            # Just create the basic table structure
            basic_sql = """
            CREATE TABLE IF NOT EXISTS pin_attempts (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                attempt_time TIMESTAMP DEFAULT NOW(),
                success BOOLEAN NOT NULL,
                locked_until TIMESTAMP
            );
            """
            
            # This might not work directly, but let's try a simpler approach
            print("📝 Table schema to create manually in Supabase dashboard:")
            print(basic_sql)
            print("\n💡 Or you can use the users table to track PIN attempts")
            
            return False
            
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False

if __name__ == "__main__":
    create_pin_attempts_table()
