-- SQL to create all Sofi AI Supabase tables
-- Run these in Supabase SQL Editor

-- 1. transfer_requests - User transfer intentions
CREATE TABLE IF NOT EXISTS transfer_requests (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    telegram_chat_id TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    reason TEXT,
    recipient_code TEXT NOT NULL,
    recipient_name TEXT,
    recipient_account TEXT NOT NULL,
    recipient_bank TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'successful', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. payment_attempts - Paystack API attempts
CREATE TABLE IF NOT EXISTS payment_attempts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    reference TEXT UNIQUE NOT NULL,
    request_id UUID REFERENCES transfer_requests(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'successful', 'failed')),
    response_payload JSONB,
    channel TEXT DEFAULT 'telegram' CHECK (channel IN ('telegram', 'web', 'api')),
    provider TEXT DEFAULT 'paystack',
    amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. refunds - Money refunded to users
CREATE TABLE IF NOT EXISTS refunds (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    original_payment_id UUID REFERENCES payment_attempts(id) ON DELETE CASCADE,
    refund_reference TEXT UNIQUE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'successful', 'failed')),
    response_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. bank_verification - Cache verified bank accounts
CREATE TABLE IF NOT EXISTS bank_verification (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    account_number TEXT NOT NULL,
    bank_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    verified BOOLEAN DEFAULT TRUE,
    verification_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_number, bank_code)
);

-- 5. paystack_errors - Log all Paystack errors
CREATE TABLE IF NOT EXISTS paystack_errors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    context TEXT NOT NULL, -- e.g., 'transfer', 'refund', 'verification'
    request_payload JSONB,
    response_payload JSONB,
    error_code TEXT,
    error_message TEXT,
    related_reference TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. audit_logs - Track all user actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    telegram_chat_id TEXT,
    action TEXT NOT NULL, -- e.g., 'transfer_initiated', 'refund_requested'
    target_table TEXT,
    target_id UUID,
    metadata JSONB, -- IP, browser, Telegram info, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. beneficiaries - Saved recipient accounts
CREATE TABLE IF NOT EXISTS beneficiaries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- Friendly name like "Mum's account"
    account_number TEXT NOT NULL,
    bank_code TEXT NOT NULL,
    account_name TEXT NOT NULL, -- Verified account name
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. sofi_transfer_profit - Track platform earnings
CREATE TABLE IF NOT EXISTS sofi_transfer_profit (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    transfer_reference TEXT NOT NULL, -- Links to payment_attempts.reference
    transfer_amount DECIMAL(15,2) NOT NULL,
    paystack_fee DECIMAL(15,2) NOT NULL,
    platform_fee DECIMAL(15,2) NOT NULL,
    total_fee DECIMAL(15,2) GENERATED ALWAYS AS (paystack_fee + platform_fee) STORED,
    net_revenue DECIMAL(15,2) GENERATED ALWAYS AS (platform_fee) STORED,
    withdrawable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transfer_requests_user_id ON transfer_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_transfer_requests_telegram_chat_id ON transfer_requests(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transfer_requests_status ON transfer_requests(status);
CREATE INDEX IF NOT EXISTS idx_payment_attempts_reference ON payment_attempts(reference);
CREATE INDEX IF NOT EXISTS idx_payment_attempts_status ON payment_attempts(status);
CREATE INDEX IF NOT EXISTS idx_bank_verification_account ON bank_verification(account_number, bank_code);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_sofi_transfer_profit_reference ON sofi_transfer_profit(transfer_reference);

-- Enable Row Level Security (RLS)
ALTER TABLE transfer_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_verification ENABLE ROW LEVEL SECURITY;
ALTER TABLE paystack_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_transfer_profit ENABLE ROW LEVEL SECURITY;
