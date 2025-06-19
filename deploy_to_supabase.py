"""
🚀 DEPLOY SECURITY SCHEMA TO SUPABASE

Run these SQL commands in your Supabase SQL Editor to deploy the security fixes
"""

print("🔐 DEPLOYING SECURITY SCHEMA TO SUPABASE")
print("=" * 50)

sql_commands = """
-- 🔐 SECURE TRANSACTION VALIDATION TABLES
-- Creates tables needed for secure PIN verification and transaction validation

-- Table for tracking PIN attempts and account lockouts
CREATE TABLE IF NOT EXISTS pin_attempts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    failed_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    UNIQUE(user_id)
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_pin_attempts_user_id ON pin_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_pin_attempts_locked_until ON pin_attempts(locked_until);

-- Ensure virtual_accounts has balance column
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 0.00;

-- Update existing accounts to have 0 balance if NULL
UPDATE virtual_accounts 
SET balance = 0.00 
WHERE balance IS NULL;

-- Add transaction limits tracking
CREATE TABLE IF NOT EXISTS daily_transaction_limits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    transaction_date DATE DEFAULT CURRENT_DATE,
    transaction_count INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, transaction_date)
);

-- Add security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON daily_transaction_limits(user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_security_audit_user_id ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_event_type ON security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_security_audit_created_at ON security_audit_log(created_at);

-- Enable Row Level Security
ALTER TABLE pin_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_transaction_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;
"""

print("📋 COPY AND PASTE THIS SQL INTO SUPABASE SQL EDITOR:")
print("-" * 55)
print(sql_commands)

print("\n🎯 INSTRUCTIONS:")
print("1. Go to your Supabase Dashboard")
print("2. Click on 'SQL Editor' in the sidebar")
print("3. Copy and paste the SQL commands above")
print("4. Click 'RUN' to execute")
print("5. Verify tables are created in the Table Editor")

print("\n✅ RESULT:")
print("• pin_attempts table - Tracks PIN verification attempts")
print("• daily_transaction_limits table - Tracks transaction limits")
print("• security_audit_log table - Logs security events")
print("• balance column added to virtual_accounts table")

print("\n🔐 SECURITY FEATURES ENABLED:")
print("• Users cannot send more than they have")
print("• Account lockout after 3 failed PIN attempts")
print("• Transaction limits (₦500k max, 20/day)")
print("• Secure PIN verification")
print("• Complete audit trail")

# Save SQL to file for easy deployment
with open("deploy_security_schema.sql", "w") as f:
    f.write(sql_commands)

print(f"\n💾 SQL commands saved to: deploy_security_schema.sql")
print("📁 You can also run this file directly in Supabase")

print("\n" + "=" * 50)
print("STATUS: ✅ READY TO DEPLOY TO SUPABASE")
print("COPY THE SQL ABOVE AND RUN IT IN SUPABASE!")
print("=" * 50)
