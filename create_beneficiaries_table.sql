-- Create beneficiaries table for Sofi AI
-- This table stores saved recipients for quick future transfers

CREATE TABLE IF NOT EXISTS beneficiaries (
    id bigserial PRIMARY KEY,
    user_id bigint REFERENCES users(id) ON DELETE CASCADE,
    name text NOT NULL,
    account_number text NOT NULL,
    bank_name text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_name ON beneficiaries(user_id, name);

-- Add unique constraint to prevent duplicate beneficiaries
CREATE UNIQUE INDEX IF NOT EXISTS idx_beneficiaries_unique 
ON beneficiaries(user_id, account_number, bank_name);

-- Add comments for documentation
COMMENT ON TABLE beneficiaries IS 'Stores saved beneficiaries for quick transfers';
COMMENT ON COLUMN beneficiaries.user_id IS 'References the user who saved this beneficiary';
COMMENT ON COLUMN beneficiaries.name IS 'Display name for the beneficiary (e.g., "John", "My Brother")';
COMMENT ON COLUMN beneficiaries.account_number IS 'Bank account number of the beneficiary';
COMMENT ON COLUMN beneficiaries.bank_name IS 'Bank name of the beneficiary account';
