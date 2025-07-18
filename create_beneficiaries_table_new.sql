-- Create beneficiaries table in Supabase
-- This table stores saved recipients for users

CREATE TABLE IF NOT EXISTS beneficiaries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, -- Nickname/friendly name (e.g., "Mum", "John")
  bank_name TEXT NOT NULL, -- Bank name (e.g., "Opay", "GTBank")
  account_number TEXT NOT NULL, -- Account number
  account_holder_name TEXT NOT NULL, -- Real account holder name
  account_type TEXT DEFAULT 'bank', -- Can be 'bank', 'wallet', 'crypto', etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_account_number ON beneficiaries(account_number);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_account ON beneficiaries(user_id, account_number);

-- Create unique constraint to prevent duplicate account numbers per user
CREATE UNIQUE INDEX IF NOT EXISTS unique_user_account_beneficiary 
ON beneficiaries(user_id, account_number) 
WHERE account_type = 'bank';

-- Add RLS (Row Level Security) policies
ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own beneficiaries
CREATE POLICY "Users can view own beneficiaries" ON beneficiaries
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only insert their own beneficiaries
CREATE POLICY "Users can insert own beneficiaries" ON beneficiaries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only update their own beneficiaries
CREATE POLICY "Users can update own beneficiaries" ON beneficiaries
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can only delete their own beneficiaries
CREATE POLICY "Users can delete own beneficiaries" ON beneficiaries
    FOR DELETE USING (auth.uid() = user_id);

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_beneficiaries_updated_at 
    BEFORE UPDATE ON beneficiaries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE beneficiaries IS 'Stores saved beneficiaries/recipients for users to enable quick transfers';
COMMENT ON COLUMN beneficiaries.name IS 'User-friendly nickname for the beneficiary';
COMMENT ON COLUMN beneficiaries.bank_name IS 'Bank name where the account is held';
COMMENT ON COLUMN beneficiaries.account_number IS 'Account number of the beneficiary';
COMMENT ON COLUMN beneficiaries.account_holder_name IS 'Official account holder name from bank verification';
COMMENT ON COLUMN beneficiaries.account_type IS 'Type of account: bank, wallet, crypto, etc.';
