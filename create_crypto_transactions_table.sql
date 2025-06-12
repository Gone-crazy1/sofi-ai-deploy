-- create_crypto_transactions_table.sql
-- Create crypto_transactions table for logging all crypto-related transactions

CREATE TABLE IF NOT EXISTS crypto_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'deposit', 'withdrawal', 'deposit_pending'
    crypto_amount DECIMAL(18, 8) NOT NULL, -- Amount in cryptocurrency (supports 8 decimal places)
    crypto_currency VARCHAR(10) NOT NULL, -- BTC, ETH, USDT, etc.
    ngn_amount DECIMAL(15, 2) DEFAULT 0, -- NGN equivalent amount
    transaction_id VARCHAR(255), -- Bitnob transaction ID
    wallet_id VARCHAR(255), -- Bitnob wallet ID
    rate_used DECIMAL(15, 2) DEFAULT 0, -- Exchange rate used for conversion
    status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_type ON crypto_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_currency ON crypto_transactions(crypto_currency);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_transaction_id ON crypto_transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_created_at ON crypto_transactions(created_at);

-- Add foreign key constraint to users table (if needed)
-- ALTER TABLE crypto_transactions ADD CONSTRAINT fk_crypto_transactions_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add comments for documentation
COMMENT ON TABLE crypto_transactions IS 'Stores all cryptocurrency transactions including deposits, withdrawals, and conversions';
COMMENT ON COLUMN crypto_transactions.crypto_amount IS 'Amount in the specific cryptocurrency (e.g., 0.001 BTC)';
COMMENT ON COLUMN crypto_transactions.ngn_amount IS 'NGN equivalent at time of transaction';
COMMENT ON COLUMN crypto_transactions.rate_used IS 'Exchange rate used for NGN conversion';
COMMENT ON COLUMN crypto_transactions.transaction_id IS 'External transaction ID from Bitnob';

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for users to see only their own transactions
-- CREATE POLICY crypto_transactions_user_policy ON crypto_transactions
-- FOR ALL USING (user_id = current_setting('app.current_user_id'));

-- Grant permissions (adjust as needed for your security model)
-- GRANT SELECT, INSERT, UPDATE ON crypto_transactions TO authenticated;
-- GRANT USAGE, SELECT ON SEQUENCE crypto_transactions_id_seq TO authenticated;
