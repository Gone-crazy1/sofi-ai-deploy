-- Complete Crypto Integration Tables for Supabase
-- Run this in your Supabase SQL Editor

-- Table 1: crypto_wallets - Store user's crypto deposit addresses
CREATE TABLE IF NOT EXISTS crypto_wallets (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE, -- Links to users.id
    btc_address VARCHAR(255),
    usdt_address VARCHAR(255),
    eth_address VARCHAR(255),
    wallet_id VARCHAR(255), -- Bitnob wallet ID
    bitnob_customer_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: crypto_transactions - Record all crypto deposits and conversions
CREATE TABLE IF NOT EXISTS crypto_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    tx_hash VARCHAR(255), -- Blockchain transaction hash
    bitnob_tx_id VARCHAR(255), -- Bitnob transaction ID
    crypto_type VARCHAR(10) NOT NULL, -- BTC, ETH, USDT, etc.
    amount_crypto DECIMAL(18, 8) NOT NULL, -- Amount in crypto (8 decimal places)
    amount_naira DECIMAL(15, 2) NOT NULL, -- Converted NGN amount
    rate_used DECIMAL(15, 2) NOT NULL, -- Exchange rate at time of conversion
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed
    webhook_data JSONB, -- Store full webhook payload for debugging
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 3: wallet_balances - User's main NGN balance (extend or use existing)
CREATE TABLE IF NOT EXISTS wallet_balances (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    balance_naira DECIMAL(15, 2) DEFAULT 0.00,
    last_crypto_deposit TIMESTAMP WITH TIME ZONE,
    total_crypto_deposits DECIMAL(15, 2) DEFAULT 0.00, -- Total NGN from crypto
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_user_id ON crypto_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_status ON crypto_transactions(status);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_crypto_type ON crypto_transactions(crypto_type);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_created_at ON crypto_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_wallet_balances_user_id ON wallet_balances(user_id);

-- Add foreign key constraints (optional, adjust based on your users table)
-- ALTER TABLE crypto_wallets ADD CONSTRAINT fk_crypto_wallets_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ALTER TABLE crypto_transactions ADD CONSTRAINT fk_crypto_transactions_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ALTER TABLE wallet_balances ADD CONSTRAINT fk_wallet_balances_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add comments for documentation
COMMENT ON TABLE crypto_wallets IS 'Stores users crypto wallet addresses from Bitnob';
COMMENT ON TABLE crypto_transactions IS 'Records all crypto deposits and NGN conversions';
COMMENT ON TABLE wallet_balances IS 'Users main NGN balance including crypto conversions';

COMMENT ON COLUMN crypto_transactions.amount_crypto IS 'Amount in original cryptocurrency';
COMMENT ON COLUMN crypto_transactions.amount_naira IS 'Converted NGN amount credited to user';
COMMENT ON COLUMN crypto_transactions.rate_used IS 'Exchange rate used for conversion';
COMMENT ON COLUMN wallet_balances.total_crypto_deposits IS 'Total NGN earned from crypto deposits';

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE crypto_wallets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE wallet_balances ENABLE ROW LEVEL SECURITY;

-- Grant permissions (adjust as needed)
-- GRANT ALL ON crypto_wallets TO authenticated;
-- GRANT ALL ON crypto_transactions TO authenticated;
-- GRANT ALL ON wallet_balances TO authenticated;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
