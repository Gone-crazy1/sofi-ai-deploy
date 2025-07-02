-- Fix database column name mismatch for PIN entry system
-- Add recipient_account column to bank_transactions table

-- Check if column exists first, then add if missing
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'bank_transactions' 
        AND column_name = 'recipient_account'
    ) THEN
        ALTER TABLE bank_transactions 
        ADD COLUMN recipient_account VARCHAR(20);
        
        -- Update existing records to copy account_number to recipient_account
        UPDATE bank_transactions 
        SET recipient_account = account_number 
        WHERE account_number IS NOT NULL;
    END IF;
END $$;

-- Also ensure we have the recipient_bank column for consistency
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'bank_transactions' 
        AND column_name = 'recipient_bank'
    ) THEN
        ALTER TABLE bank_transactions 
        ADD COLUMN recipient_bank VARCHAR(100);
        
        -- Update existing records to copy bank_name to recipient_bank
        UPDATE bank_transactions 
        SET recipient_bank = bank_name 
        WHERE bank_name IS NOT NULL;
    END IF;
END $$;

-- Create index for better performance on recipient_account lookups
CREATE INDEX IF NOT EXISTS idx_bank_transactions_recipient_account 
ON bank_transactions(recipient_account);

-- Create index for better performance on recipient_bank lookups  
CREATE INDEX IF NOT EXISTS idx_bank_transactions_recipient_bank 
ON bank_transactions(recipient_bank);

-- Display current table structure to verify
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'bank_transactions' 
ORDER BY ordinal_position;
