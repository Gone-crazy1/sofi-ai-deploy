-- WhatsApp Integration Tables for Supabase
-- Execute these in your Supabase SQL editor

-- 1. webhook_events: Tracks all incoming webhook events for deduplication
CREATE TABLE IF NOT EXISTS webhook_events (
    id SERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    payload JSONB NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT DEFAULT 'whatsapp',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast event_id lookups
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_id ON webhook_events(event_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed_at ON webhook_events(processed_at);

-- 2. message_logs: Tracks all inbound/outbound messages with intent and session state
CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    platform TEXT DEFAULT 'whatsapp',
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    content TEXT NOT NULL,
    intent TEXT,
    raw_payload JSONB DEFAULT '{}',
    session_state JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for message logs
CREATE INDEX IF NOT EXISTS idx_message_logs_user_id ON message_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_platform ON message_logs(platform);
CREATE INDEX IF NOT EXISTS idx_message_logs_direction ON message_logs(direction);
CREATE INDEX IF NOT EXISTS idx_message_logs_intent ON message_logs(intent);
CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);

-- 3. onboarding_sessions: Multi-step onboarding before user row exists
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id SERIAL PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    step TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    session_data JSONB DEFAULT '{}',
    user_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for onboarding sessions
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_whatsapp_number ON onboarding_sessions(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);

-- Update trigger for onboarding_sessions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_onboarding_sessions_updated_at
    BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Update existing users table to support WhatsApp integration (only if table exists)
-- Add columns if they don't exist
DO $$ 
BEGIN
    -- Check if users table exists first
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name='users') THEN
        
        -- Add whatsapp_number column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='users' AND column_name='whatsapp_number') THEN
            ALTER TABLE users ADD COLUMN whatsapp_number TEXT;
        END IF;
        
        -- Add platform column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='users' AND column_name='platform') THEN
            ALTER TABLE users ADD COLUMN platform TEXT DEFAULT 'web';
        END IF;
        
        -- Add last_active_at column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='users' AND column_name='last_active_at') THEN
            ALTER TABLE users ADD COLUMN last_active_at TIMESTAMP WITH TIME ZONE;
        END IF;
        
        -- Add onboarding_completed column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='users' AND column_name='onboarding_completed') THEN
            ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE;
        END IF;
        
        -- Add kyc_status column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='users' AND column_name='kyc_status') THEN
            ALTER TABLE users ADD COLUMN kyc_status TEXT DEFAULT 'pending';
        END IF;
        
    END IF;
END $$;

-- Indexes for users table WhatsApp integration (only if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='users') THEN
        CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
        CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform);
        CREATE INDEX IF NOT EXISTS idx_users_last_active_at ON users(last_active_at);
    END IF;
END $$;

-- 5. Update virtual_accounts table if needed (only if table exists)
DO $$ 
BEGIN
    -- Check if virtual_accounts table exists first
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name='virtual_accounts') THEN
        
        -- Add account_name column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='virtual_accounts' AND column_name='account_name') THEN
            ALTER TABLE virtual_accounts ADD COLUMN account_name TEXT;
        END IF;
        
        -- Add bank_name column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='virtual_accounts' AND column_name='bank_name') THEN
            ALTER TABLE virtual_accounts ADD COLUMN bank_name TEXT DEFAULT 'Sofi Digital Bank';
        END IF;
        
        -- Add status column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='virtual_accounts' AND column_name='status') THEN
            ALTER TABLE virtual_accounts ADD COLUMN status TEXT DEFAULT 'active';
        END IF;
        
    END IF;
END $$;

-- 6. Row Level Security (RLS) Policies
-- Enable RLS on new tables
ALTER TABLE webhook_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your security requirements)
-- These are basic policies - customize based on your needs

-- webhook_events: Only service role can access
CREATE POLICY "Service role can manage webhook_events" ON webhook_events
    FOR ALL USING (auth.role() = 'service_role');

-- message_logs: Users can see their own messages, service role can see all
CREATE POLICY "Users can view own messages" ON message_logs
    FOR SELECT USING (user_id = auth.uid()::text OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage message_logs" ON message_logs
    FOR ALL USING (auth.role() = 'service_role');

-- onboarding_sessions: Service role can manage
CREATE POLICY "Service role can manage onboarding_sessions" ON onboarding_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE webhook_events IS 'Stores WhatsApp webhook events for deduplication';
COMMENT ON TABLE message_logs IS 'Logs all inbound/outbound WhatsApp messages with intent analysis';
COMMENT ON TABLE onboarding_sessions IS 'Tracks multi-step onboarding flow for new WhatsApp users';

COMMENT ON COLUMN webhook_events.event_id IS 'WhatsApp message ID for deduplication';
COMMENT ON COLUMN message_logs.intent IS 'Parsed user intent (balance, send_money, airtime, etc.)';
COMMENT ON COLUMN onboarding_sessions.step IS 'Current onboarding step (asked_to_create, collecting_name, etc.)';
COMMENT ON COLUMN onboarding_sessions.session_data IS 'Temporary data collected during onboarding';

-- Grant permissions to authenticated users (adjust as needed)
GRANT SELECT ON message_logs TO authenticated;
GRANT ALL ON webhook_events TO service_role;
GRANT ALL ON message_logs TO service_role;
GRANT ALL ON onboarding_sessions TO service_role;
