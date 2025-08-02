-- Add WhatsApp support to Sofi AI database
-- Run this in your Supabase SQL editor

-- 1. Add whatsapp_number column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);

-- 2. Add whatsapp_number column to virtual_accounts table  
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);

-- 3. Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_whatsapp_number ON virtual_accounts(whatsapp_number);

-- 4. Add comment to document the change
COMMENT ON COLUMN users.whatsapp_number IS 'WhatsApp number for notifications (format: +234XXXXXXXXX)';
COMMENT ON COLUMN virtual_accounts.whatsapp_number IS 'WhatsApp number linked to this virtual account';

-- 5. Update existing users to have whatsapp_number based on telegram_chat_id if available
-- You may need to manually update this based on your data migration strategy

SELECT 'WhatsApp columns added successfully!' as status;
