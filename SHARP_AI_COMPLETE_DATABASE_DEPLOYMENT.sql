-- SHARP AI DATABASE FIXES - COMPLETE DEPLOYMENT
-- Execute this in Supabase SQL Editor to fix all database issues

-- 1. Create user_profiles table with all required columns
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone_number TEXT,
    email TEXT,
    last_intent TEXT,
    last_action TEXT,
    last_action_time TIMESTAMPTZ,
    last_message TEXT,  -- Added this missing column
    last_balance NUMERIC DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    total_spent NUMERIC DEFAULT 0,
    total_received NUMERIC DEFAULT 0,
    favorite_banks JSONB DEFAULT '[]'::jsonb,
    frequent_recipients JSONB DEFAULT '[]'::jsonb,
    spending_patterns JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create transaction_memory table
CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    recipient_name TEXT,
    recipient_account TEXT,
    bank_name TEXT,
    narration TEXT,
    transaction_reference TEXT,
    status TEXT DEFAULT 'completed',
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create conversation_context table
CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_summary TEXT NOT NULL,
    full_context TEXT,
    resolution_status TEXT DEFAULT 'pending',
    importance_level INTEGER DEFAULT 1,
    context_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create spending_analytics table
CREATE TABLE IF NOT EXISTS spending_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_spent NUMERIC DEFAULT 0,
    total_transfers NUMERIC DEFAULT 0,
    total_airtime NUMERIC DEFAULT 0,
    total_data NUMERIC DEFAULT 0,
    total_crypto NUMERIC DEFAULT 0,
    transaction_count INTEGER DEFAULT 0,
    top_recipient TEXT,
    top_bank TEXT,
    spending_category JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Create ai_learning table
CREATE TABLE IF NOT EXISTS ai_learning (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    learning_type TEXT NOT NULL,
    learning_key TEXT NOT NULL,
    learning_value TEXT NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    last_observed TIMESTAMPTZ DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_chat_id ON user_profiles(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_chat_id ON transaction_memory(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_date ON transaction_memory(transaction_date);
CREATE INDEX IF NOT EXISTS idx_conversation_context_chat_id ON conversation_context(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_date ON conversation_context(context_date);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_chat_id ON spending_analytics(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_period ON spending_analytics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_ai_learning_chat_id ON ai_learning(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_type ON ai_learning(learning_type);

-- 7. Add missing column to existing user_profiles table (if it already exists)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS last_message TEXT;

-- 8. Verify all tables and columns exist
SELECT 
    t.table_name,
    COUNT(c.column_name) as column_count,
    ARRAY_AGG(c.column_name ORDER BY c.ordinal_position) as columns
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_schema = 'public' 
AND t.table_name IN ('user_profiles', 'transaction_memory', 'conversation_context', 'spending_analytics', 'ai_learning')
GROUP BY t.table_name
ORDER BY t.table_name;

-- Success message
SELECT 'Sharp AI Memory System Deployed Successfully!' as status,
       'All 5 tables created with proper indexes and columns' as details;
