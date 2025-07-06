-- Create beneficiaries table for Sofi AI
-- This table stores saved recipients for quick transfers

CREATE TABLE IF NOT EXISTS beneficiaries (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL, -- Telegram chat ID
    beneficiary_name TEXT NOT NULL, -- Full name from bank verification
    account_number TEXT NOT NULL, -- Bank account number
    bank_name TEXT NOT NULL, -- Bank name
    bank_code TEXT, -- Bank code for API calls
    nickname TEXT, -- User-friendly nickname
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure no duplicate beneficiaries per user
    UNIQUE(user_id, account_number)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_last_used ON beneficiaries(user_id, last_used DESC);

-- Add RLS (Row Level Security) if needed
-- ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE beneficiaries IS 'Stores saved beneficiaries for Sofi AI users for quick money transfers';
COMMENT ON COLUMN beneficiaries.user_id IS 'Telegram chat ID of the user who saved this beneficiary';
COMMENT ON COLUMN beneficiaries.beneficiary_name IS 'Full name as returned by bank account verification';
COMMENT ON COLUMN beneficiaries.nickname IS 'User-friendly name like "my wife", "john", etc.';
COMMENT ON COLUMN beneficiaries.last_used IS 'When this beneficiary was last used for a transfer';
