-- SHARP AI MEMORY SYSTEM - COMPLETE DEPLOYMENT
-- Execute this entire script in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Enhanced User Profile Table (Complete User Memory)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone_number TEXT,
    email TEXT,
    last_intent TEXT,
    last_action TEXT,
    last_action_time TIMESTAMPTZ,
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

-- 2. Comprehensive Transaction Memory (All Money Movements)
CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('transfer', 'airtime', 'data', 'crypto_buy', 'crypto_sell', 'deposit', 'withdrawal')),
    amount NUMERIC NOT NULL,
    recipient_name TEXT,
    recipient_account TEXT,
    bank_name TEXT,
    narration TEXT,
    transaction_reference TEXT,
    status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed')),
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Conversation Context Memory (AI Context Awareness)
CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    context_type TEXT NOT NULL CHECK (context_type IN ('intent', 'question', 'complaint', 'request', 'command')),
    context_summary TEXT NOT NULL,
    full_context TEXT,
    resolution_status TEXT DEFAULT 'pending' CHECK (resolution_status IN ('pending', 'resolved', 'escalated')),
        importance_level INTEGER DEFAULT 1 CHECK (importance_level BETWEEN 1 AND 5),
    context_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Smart Spending Analytics (Financial Intelligence)
CREATE TABLE IF NOT EXISTS spending_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly')),
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

-- 5. AI Learning & Preferences (Personalization Memory)
CREATE TABLE IF NOT EXISTS ai_learning (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    learning_type TEXT NOT NULL CHECK (learning_type IN ('preference', 'habit', 'pattern', 'behavior')),
    learning_key TEXT NOT NULL,
    learning_value TEXT NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.50 CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    last_observed TIMESTAMPTZ DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(telegram_chat_id, learning_key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_chat_id ON user_profiles(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_chat_id ON transaction_memory(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_date ON transaction_memory(transaction_date);
CREATE INDEX IF NOT EXISTS idx_conversation_context_chat_id ON conversation_context(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_date ON conversation_context(context_date);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_chat_id ON spending_analytics(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_period ON spending_analytics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_ai_learning_chat_id ON ai_learning(telegram_chat_id);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE spending_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow service role access)
DO $$
BEGIN
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Enable all operations for service role" ON user_profiles;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON transaction_memory;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON conversation_context;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON spending_analytics;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON ai_learning;
EXCEPTION
    WHEN undefined_object THEN
        NULL;
END $$;

-- Create new policies
CREATE POLICY "Enable all operations for service role" ON user_profiles FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON transaction_memory FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON conversation_context FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON spending_analytics FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON ai_learning FOR ALL USING (true);

-- Verify tables created
SELECT 
    table_name,
    'Created successfully' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_profiles', 'transaction_memory', 'conversation_context', 'spending_analytics', 'ai_learning')
ORDER BY table_name;
