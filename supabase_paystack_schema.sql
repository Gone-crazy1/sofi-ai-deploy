-- =======================================================
-- SOFI AI - COMPLETE SUPABASE SCHEMA FOR PAYSTACK
-- =======================================================
-- Run these SQL commands in your Supabase SQL Editor
-- This will create all required tables for Paystack integration

-- First, add missing columns to existing users table (if it exists)
-- =======================================================
DO $$
BEGIN
    -- Add Paystack integration columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'paystack_customer_code') THEN
        ALTER TABLE users ADD COLUMN paystack_customer_code TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'paystack_dva_id') THEN
        ALTER TABLE users ADD COLUMN paystack_dva_id TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'paystack_account_number') THEN
        ALTER TABLE users ADD COLUMN paystack_account_number TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'paystack_bank_name') THEN
        ALTER TABLE users ADD COLUMN paystack_bank_name TEXT;
    END IF;
    
    -- Add wallet balance (rename from balance for clarity)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'wallet_balance') THEN
        -- If balance column exists, rename it to wallet_balance
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'balance') THEN
            ALTER TABLE users RENAME COLUMN balance TO wallet_balance;
        ELSE
            ALTER TABLE users ADD COLUMN wallet_balance NUMERIC(15,2) DEFAULT 0.00;
        END IF;
    END IF;
    
    -- Add other missing columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'pin_hash') THEN
        ALTER TABLE users ADD COLUMN pin_hash TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'pin_attempts') THEN
        ALTER TABLE users ADD COLUMN pin_attempts INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'pin_locked_until') THEN
        ALTER TABLE users ADD COLUMN pin_locked_until TIMESTAMP;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        -- Table doesn't exist, will be created below
        NULL;
END $$;

-- 1. USERS TABLE (Main user information with Paystack integration)
-- =======================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    whatsapp_number TEXT UNIQUE NOT NULL,
    phone_number TEXT,
    full_name TEXT,
    email TEXT,
    
    -- Paystack Integration Columns (Recommended)
    paystack_customer_code TEXT,        -- From customer.code after creation
    paystack_dva_id TEXT,              -- From dedicated_account.id
    paystack_account_number TEXT,       -- Assigned account number
    paystack_bank_name TEXT,           -- e.g. Wema, Providus
    wallet_balance NUMERIC(15,2) DEFAULT 0.00,  -- Your internal wallet balance
    
    -- User Status & Security
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    pin_hash TEXT,
    pin_attempts INTEGER DEFAULT 0,
    pin_locked_until TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. VIRTUAL ACCOUNTS TABLE (Paystack dedicated accounts)
-- =======================================================
CREATE TABLE IF NOT EXISTS virtual_accounts (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    whatsapp_number TEXT NOT NULL, -- Store chat_id but no foreign key constraint
    account_number TEXT UNIQUE NOT NULL,
    account_name TEXT,
    bank_name TEXT,
    bank_code TEXT,
    paystack_customer_code TEXT,
    paystack_account_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. BANK TRANSACTIONS TABLE (All payment transactions)
-- =======================================================
CREATE TABLE IF NOT EXISTS bank_transactions (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id TEXT NOT NULL, -- whatsapp_number
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('credit', 'debit')),
    amount NUMERIC(15,2) NOT NULL,
    reference TEXT UNIQUE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'cancelled')),
    description TEXT,
    paystack_data JSONB,
    wallet_balance_before NUMERIC(15,2),  -- Balance before transaction
    wallet_balance_after NUMERIC(15,2),   -- Balance after transaction
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. TRANSFER RECIPIENTS TABLE (For outgoing transfers)
-- =======================================================
CREATE TABLE IF NOT EXISTS transfer_recipients (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id TEXT NOT NULL, -- whatsapp_number
    recipient_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    bank_code TEXT NOT NULL,
    bank_name TEXT,
    paystack_recipient_code TEXT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. BENEFICIARIES TABLE (Saved recipients for users)
-- =======================================================
CREATE TABLE IF NOT EXISTS beneficiaries (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id TEXT NOT NULL, -- whatsapp_number
    beneficiary_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    bank_code TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    nickname TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, account_number, bank_code)
);

-- 6. PAYSTACK WEBHOOKS LOG (For debugging webhook events)
-- =======================================================
CREATE TABLE IF NOT EXISTS paystack_webhook_logs (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    event_type TEXT NOT NULL,
    reference TEXT,
    payload JSONB NOT NULL,
    signature TEXT,
    processed BOOLEAN DEFAULT FALSE,
    processing_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. USER SETTINGS TABLE (User preferences and configurations)
-- =======================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL, -- whatsapp_number
    transfer_limit_daily DECIMAL(15,2) DEFAULT 1000000.00, -- 1M NGN default
    transfer_limit_monthly DECIMAL(15,2) DEFAULT 10000000.00, -- 10M NGN default
    require_pin_for_transfers BOOLEAN DEFAULT TRUE,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =======================================================
-- INDEXES FOR PERFORMANCE
-- =======================================================

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_users_paystack_customer_code ON users(paystack_customer_code);
CREATE INDEX IF NOT EXISTS idx_users_paystack_dva_id ON users(paystack_dva_id);
CREATE INDEX IF NOT EXISTS idx_users_paystack_account_number ON users(paystack_account_number);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Virtual accounts indexes
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_user_id ON virtual_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_whatsapp_number ON virtual_accounts(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_account_number ON virtual_accounts(account_number);

-- Bank transactions indexes
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user_id ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_reference ON bank_transactions(reference);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_status ON bank_transactions(status);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_created_at ON bank_transactions(created_at);

-- Transfer recipients indexes
CREATE INDEX IF NOT EXISTS idx_transfer_recipients_user_id ON transfer_recipients(user_id);

-- Beneficiaries indexes
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);

-- Webhook logs indexes
CREATE INDEX IF NOT EXISTS idx_webhook_logs_event_type ON paystack_webhook_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_reference ON paystack_webhook_logs(reference);

-- User settings indexes
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- =======================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =======================================================

-- Enable RLS on all tables (after tables are created)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE virtual_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_recipients ENABLE ROW LEVEL SECURITY;
ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Create policies for service role (bypass RLS for your backend)
CREATE POLICY "Service role can manage all users" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all virtual_accounts" ON virtual_accounts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all bank_transactions" ON bank_transactions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all transfer_recipients" ON transfer_recipients
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all beneficiaries" ON beneficiaries
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all user_settings" ON user_settings
    FOR ALL USING (auth.role() = 'service_role');

-- =======================================================
-- FUNCTIONS AND TRIGGERS
-- =======================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers to tables (after tables are created)
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_virtual_accounts_updated_at BEFORE UPDATE ON virtual_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bank_transactions_updated_at BEFORE UPDATE ON bank_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transfer_recipients_updated_at BEFORE UPDATE ON transfer_recipients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_beneficiaries_updated_at BEFORE UPDATE ON beneficiaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =======================================================
-- INSERT SAMPLE DATA (OPTIONAL - FOR TESTING)
-- =======================================================

-- Insert a test user with Paystack columns (uncomment if you want to test)
-- INSERT INTO users (whatsapp_number, phone_number, full_name, email, wallet_balance) 
-- VALUES ('test_user_123', '+2348123456789', 'Test User', 'test@sofi.ai', 0.00)
-- ON CONFLICT (whatsapp_number) DO NOTHING;

-- =======================================================
-- SUMMARY
-- =======================================================
-- ✅ Tables Created:
-- 1. users - Main user information with balance
-- 2. virtual_accounts - Paystack dedicated accounts  
-- 3. bank_transactions - All payment transactions
-- 4. transfer_recipients - Recipients for outgoing transfers
-- 5. beneficiaries - Saved recipients for users
-- 6. paystack_webhook_logs - Webhook event logging
-- 7. user_settings - User preferences
-- 
-- ✅ Features Added:
-- - Proper indexes for performance
-- - Row Level Security (RLS) with service role policies
-- - Auto-updating timestamps
-- - Data validation constraints
-- - Foreign key relationships
-- 
-- 🚀 Your Paystack integration is now database-ready!
