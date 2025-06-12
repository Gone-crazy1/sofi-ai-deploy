-- ================================================================================================
-- SOFI AI CRYPTO INTEGRATION - COMPLETE DATABASE SETUP
-- ================================================================================================
-- Copy and paste this entire script into your Supabase SQL Editor and run it
-- This will create all necessary tables, indexes, and constraints for crypto functionality
-- ================================================================================================

-- ===========================
-- TABLE 1: crypto_wallets
-- ===========================
-- Stores user's crypto deposit addresses from Bitnob API
CREATE TABLE IF NOT EXISTS crypto_wallets (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE, -- Links to users.id or telegram_chat_id
    wallet_id VARCHAR(255) NOT NULL, -- Bitnob wallet ID
    bitnob_customer_email VARCHAR(255) NOT NULL,
    btc_address VARCHAR(255), -- Bitcoin deposit address
    usdt_address VARCHAR(255), -- USDT deposit address  
    eth_address VARCHAR(255), -- Ethereum deposit address
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, deleted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABLE 2: crypto_transactions  
-- ===========================
-- Records all crypto deposits, conversions, and transaction history
CREATE TABLE IF NOT EXISTS crypto_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    tx_hash VARCHAR(255), -- Blockchain transaction hash
    bitnob_tx_id VARCHAR(255) NOT NULL, -- Bitnob transaction ID
    transaction_type VARCHAR(20) DEFAULT 'deposit', -- deposit, withdrawal, conversion
    crypto_type VARCHAR(10) NOT NULL, -- BTC, ETH, USDT, etc.
    amount_crypto DECIMAL(18, 8) NOT NULL, -- Amount in crypto (8 decimal places for precision)
    amount_naira DECIMAL(15, 2) NOT NULL, -- Converted NGN amount
    rate_used DECIMAL(15, 2) NOT NULL, -- Exchange rate at time of conversion (e.g., 1 BTC = 95000000 NGN)
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, processing
    webhook_data JSONB, -- Store full Bitnob webhook payload for debugging
    processed_at TIMESTAMP WITH TIME ZONE, -- When conversion was completed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABLE 3: wallet_balances
-- ===========================
-- User's main NGN balance from all sources including crypto conversions
CREATE TABLE IF NOT EXISTS wallet_balances (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    balance_naira DECIMAL(15, 2) DEFAULT 0.00, -- Current NGN balance
    total_deposits DECIMAL(15, 2) DEFAULT 0.00, -- Total deposits (bank transfers + crypto)
    total_crypto_deposits DECIMAL(15, 2) DEFAULT 0.00, -- Total NGN from crypto conversions only
    total_withdrawals DECIMAL(15, 2) DEFAULT 0.00, -- Total withdrawals/transfers sent
    last_crypto_deposit TIMESTAMP WITH TIME ZONE, -- Last crypto deposit timestamp
    last_transaction TIMESTAMP WITH TIME ZONE, -- Last any transaction
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABLE 4: crypto_rates_cache
-- ===========================
-- Cache live crypto rates to reduce API calls and track rate history
CREATE TABLE IF NOT EXISTS crypto_rates_cache (
    id BIGSERIAL PRIMARY KEY,
    crypto_symbol VARCHAR(10) NOT NULL, -- BTC, ETH, USDT
    rate_ngn DECIMAL(15, 2) NOT NULL, -- Rate in NGN (e.g., 95000000.00 for 1 BTC)
    rate_usd DECIMAL(15, 2), -- Rate in USD for reference
    source VARCHAR(50) DEFAULT 'coingecko', -- Rate source API
    expires_at TIMESTAMP WITH TIME ZONE, -- Cache expiration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABLE 5: crypto_statistics
-- ===========================
-- Track crypto usage statistics for analytics and insights
CREATE TABLE IF NOT EXISTS crypto_statistics (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    total_crypto_transactions INTEGER DEFAULT 0,
    favorite_crypto VARCHAR(10), -- Most used crypto (BTC, ETH, USDT)
    total_btc_deposits DECIMAL(18, 8) DEFAULT 0,
    total_eth_deposits DECIMAL(18, 8) DEFAULT 0,
    total_usdt_deposits DECIMAL(18, 8) DEFAULT 0,
    total_ngn_earned DECIMAL(15, 2) DEFAULT 0, -- Total NGN from all crypto
    first_crypto_deposit TIMESTAMP WITH TIME ZONE,
    last_crypto_deposit TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ================================================================================================

-- crypto_wallets indexes
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_user_id ON crypto_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_wallet_id ON crypto_wallets(wallet_id);
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_email ON crypto_wallets(bitnob_customer_email);

-- crypto_transactions indexes  
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_status ON crypto_transactions(status);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_crypto_type ON crypto_transactions(crypto_type);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_created_at ON crypto_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_bitnob_tx_id ON crypto_transactions(bitnob_tx_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_tx_hash ON crypto_transactions(tx_hash);

-- wallet_balances indexes
CREATE INDEX IF NOT EXISTS idx_wallet_balances_user_id ON wallet_balances(user_id);
CREATE INDEX IF NOT EXISTS idx_wallet_balances_last_updated ON wallet_balances(last_updated DESC);

-- crypto_rates_cache indexes
CREATE INDEX IF NOT EXISTS idx_crypto_rates_symbol ON crypto_rates_cache(crypto_symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_rates_created_at ON crypto_rates_cache(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_crypto_rates_expires_at ON crypto_rates_cache(expires_at);

-- crypto_statistics indexes
CREATE INDEX IF NOT EXISTS idx_crypto_statistics_user_id ON crypto_statistics(user_id);

-- ================================================================================================
-- FOREIGN KEY CONSTRAINTS (Uncomment if you have a users table)
-- ================================================================================================

-- Uncomment these if you want to enforce referential integrity with your users table:
-- ALTER TABLE crypto_wallets ADD CONSTRAINT fk_crypto_wallets_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ALTER TABLE crypto_transactions ADD CONSTRAINT fk_crypto_transactions_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ALTER TABLE wallet_balances ADD CONSTRAINT fk_wallet_balances_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ALTER TABLE crypto_statistics ADD CONSTRAINT fk_crypto_statistics_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ================================================================================================
-- TABLE CONSTRAINTS AND VALIDATIONS
-- ================================================================================================

-- Ensure positive balances and amounts
ALTER TABLE wallet_balances ADD CONSTRAINT chk_balance_non_negative 
CHECK (balance_naira >= 0 AND total_deposits >= 0 AND total_crypto_deposits >= 0);

ALTER TABLE crypto_transactions ADD CONSTRAINT chk_crypto_amount_positive 
CHECK (amount_crypto > 0 AND amount_naira > 0 AND rate_used > 0);

ALTER TABLE crypto_rates_cache ADD CONSTRAINT chk_rate_positive 
CHECK (rate_ngn > 0);

-- Ensure valid crypto symbols
ALTER TABLE crypto_transactions ADD CONSTRAINT chk_valid_crypto_type 
CHECK (crypto_type IN ('BTC', 'ETH', 'USDT', 'BNB', 'ADA', 'XRP', 'DOT', 'LTC'));

ALTER TABLE crypto_rates_cache ADD CONSTRAINT chk_valid_crypto_symbol 
CHECK (crypto_symbol IN ('BTC', 'ETH', 'USDT', 'BNB', 'ADA', 'XRP', 'DOT', 'LTC'));

-- Ensure valid transaction statuses
ALTER TABLE crypto_transactions ADD CONSTRAINT chk_valid_status 
CHECK (status IN ('pending', 'processing', 'success', 'failed', 'cancelled'));

-- ================================================================================================
-- TABLE COMMENTS FOR DOCUMENTATION
-- ================================================================================================

COMMENT ON TABLE crypto_wallets IS 'Stores users crypto wallet addresses and details from Bitnob API';
COMMENT ON TABLE crypto_transactions IS 'Records all crypto deposits, conversions, and transaction history';
COMMENT ON TABLE wallet_balances IS 'Users main NGN balance including crypto conversions and traditional deposits';
COMMENT ON TABLE crypto_rates_cache IS 'Caches live crypto exchange rates to reduce API calls';
COMMENT ON TABLE crypto_statistics IS 'Tracks user crypto usage patterns and statistics';

-- Column comments
COMMENT ON COLUMN crypto_transactions.amount_crypto IS 'Amount in original cryptocurrency (8 decimal precision)';
COMMENT ON COLUMN crypto_transactions.amount_naira IS 'Converted NGN amount credited to user balance';
COMMENT ON COLUMN crypto_transactions.rate_used IS 'Exchange rate used for conversion (crypto to NGN)';
COMMENT ON COLUMN crypto_transactions.webhook_data IS 'Full Bitnob webhook payload for debugging and audit';
COMMENT ON COLUMN wallet_balances.total_crypto_deposits IS 'Total NGN earned from all crypto deposits';
COMMENT ON COLUMN crypto_rates_cache.rate_ngn IS 'Current exchange rate in Nigerian Naira';

-- ================================================================================================
-- ROW LEVEL SECURITY (RLS) - OPTIONAL
-- ================================================================================================

-- Uncomment to enable RLS for additional security:
-- ALTER TABLE crypto_wallets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE wallet_balances ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE crypto_statistics ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (adjust based on your authentication system):
-- CREATE POLICY "Users can only see their own crypto wallets" ON crypto_wallets
--   FOR ALL USING (user_id = current_user_id());

-- CREATE POLICY "Users can only see their own transactions" ON crypto_transactions
--   FOR ALL USING (user_id = current_user_id());

-- CREATE POLICY "Users can only see their own balances" ON wallet_balances
--   FOR ALL USING (user_id = current_user_id());

-- ================================================================================================
-- PERMISSIONS (Adjust based on your needs)
-- ================================================================================================

-- Grant permissions to authenticated users
GRANT ALL ON crypto_wallets TO authenticated;
GRANT ALL ON crypto_transactions TO authenticated;
GRANT ALL ON wallet_balances TO authenticated;
GRANT ALL ON crypto_rates_cache TO authenticated;
GRANT ALL ON crypto_statistics TO authenticated;

-- Grant sequence permissions
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ================================================================================================
-- INITIAL DATA SETUP
-- ================================================================================================

-- Insert initial crypto rate cache entries (optional)
INSERT INTO crypto_rates_cache (crypto_symbol, rate_ngn, rate_usd, expires_at) VALUES
('BTC', 95000000.00, 65000.00, NOW() + INTERVAL '15 minutes'),
('ETH', 5800000.00, 4000.00, NOW() + INTERVAL '15 minutes'),
('USDT', 1450.00, 1.00, NOW() + INTERVAL '15 minutes')
ON CONFLICT DO NOTHING;

-- ================================================================================================
-- SETUP COMPLETE!
-- ================================================================================================

-- Your crypto integration database is now ready! 🚀
-- 
-- Next steps:
-- 1. Update your .env file with BITNOB_SECRET_KEY
-- 2. Test crypto wallet creation via your app
-- 3. Set up Bitnob webhook endpoint: /crypto/webhook
-- 4. Test end-to-end crypto deposit and NGN conversion flow
--
-- Tables created:
-- ✅ crypto_wallets - User crypto deposit addresses
-- ✅ crypto_transactions - All crypto transaction history  
-- ✅ wallet_balances - User NGN balances
-- ✅ crypto_rates_cache - Exchange rate caching
-- ✅ crypto_statistics - User crypto analytics
--
-- Features enabled:
-- ✅ Instant crypto-to-NGN conversion
-- ✅ Multi-crypto support (BTC, ETH, USDT)
-- ✅ Transaction history and analytics
-- ✅ Rate caching for performance
-- ✅ Comprehensive indexing for fast queries
-- ✅ Data validation and constraints
-- ================================================================================================
