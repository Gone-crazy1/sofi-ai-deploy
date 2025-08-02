-- Add WhatsApp support to Sofi AI database
-- Run this in your Supabase SQL editor STEP BY STEP

-- STEP 1: Add whatsapp_number column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);

-- STEP 2: Add whatsapp_number column to virtual_accounts table  
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);

-- STEP 3: Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_whatsapp_number ON virtual_accounts(whatsapp_number);

-- STEP 4: Add comments to document the change
COMMENT ON COLUMN users.whatsapp_number IS 'WhatsApp number for notifications (format: +234XXXXXXXXX)';
COMMENT ON COLUMN virtual_accounts.whatsapp_number IS 'WhatsApp number linked to this virtual account';

-- STEP 5: Update your specific user record (REPLACE WITH YOUR ACTUAL DATA)
-- Update users table with your WhatsApp number
UPDATE users 
SET whatsapp_number = '+2348104611794'  -- YOUR WhatsApp number
WHERE email = 'getsofi@gmail.com'      -- YOUR email
   OR paystack_customer_code = 'CUS_ichx3atw50fdhm6';  -- YOUR customer code from logs

-- STEP 6: Update virtual_accounts table with your WhatsApp number  
UPDATE virtual_accounts 
SET whatsapp_number = '+2348104611794'  -- YOUR WhatsApp number
WHERE account_number = '9325935424';    -- YOUR account number from logs

-- STEP 7: Verify the updates
SELECT 'Migration completed successfully!' as status;
SELECT id, email, whatsapp_number, paystack_customer_code FROM users WHERE whatsapp_number IS NOT NULL;
SELECT account_number, whatsapp_number FROM virtual_accounts WHERE whatsapp_number IS NOT NULL;
