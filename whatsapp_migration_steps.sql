-- STEP-BY-STEP WhatsApp Migration for Sofi AI
-- Copy and paste each step one at a time into Supabase SQL Editor

-- === STEP 1: Add columns (run this first) ===
ALTER TABLE users ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);
ALTER TABLE virtual_accounts ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);

-- === STEP 2: Create indexes (run this second) ===
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_whatsapp_number ON virtual_accounts(whatsapp_number);

-- === STEP 3: Update your user record (CUSTOMIZE WITH YOUR DATA) ===
-- From your logs, I can see:
-- Customer Code: CUS_ichx3atw50fdhm6
-- Email: getsofi@gmail.com  
-- Phone: +2348104611794
-- Account: 9325935424

UPDATE users 
SET whatsapp_number = '+2348104611794'
WHERE paystack_customer_code = 'CUS_ichx3atw50fdhm6';

-- === STEP 4: Update your virtual account (CUSTOMIZE WITH YOUR DATA) ===
UPDATE virtual_accounts 
SET whatsapp_number = '+2348104611794'
WHERE account_number = '9325935424';

-- === STEP 5: Verify the changes ===
SELECT 'Users with WhatsApp numbers:' as info;
SELECT id, email, whatsapp_number, paystack_customer_code 
FROM users 
WHERE whatsapp_number IS NOT NULL;

SELECT 'Virtual accounts with WhatsApp numbers:' as info;
SELECT account_number, whatsapp_number, bank_name, balance 
FROM virtual_accounts 
WHERE whatsapp_number IS NOT NULL;
