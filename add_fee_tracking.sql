-- Add comprehensive fee tracking columns to bank_transactions table
-- Run this in your Supabase SQL editor

ALTER TABLE bank_transactions 
ADD COLUMN IF NOT EXISTS fee NUMERIC(15,2) DEFAULT 0,  -- Sofi fee (your profit)
ADD COLUMN IF NOT EXISTS paystack_fee NUMERIC(15,2) DEFAULT 10,  -- Paystack charges
ADD COLUMN IF NOT EXISTS total_amount NUMERIC(15,2),  -- Total amount deducted from user
ADD COLUMN IF NOT EXISTS balance_before NUMERIC(15,2),
ADD COLUMN IF NOT EXISTS balance_after NUMERIC(15,2);

-- Update existing records for backward compatibility
UPDATE bank_transactions 
SET fee = 0, paystack_fee = 10, total_amount = amount + 10
WHERE fee IS NULL;

-- Create indexes for profit analysis
CREATE INDEX IF NOT EXISTS idx_bank_transactions_fee ON bank_transactions(fee);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_paystack_fee ON bank_transactions(paystack_fee);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_created_at ON bank_transactions(created_at);

-- Create a view for SOFI PROFIT tracking (excluding Paystack fees)
CREATE OR REPLACE VIEW sofi_profit_summary AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_transferred,
    SUM(fee) as sofi_profit,  -- Your actual profit
    SUM(paystack_fee) as paystack_costs,  -- What you pay Paystack
    SUM(fee + paystack_fee) as total_fees_collected,  -- What users paid in fees
    AVG(fee) as avg_sofi_fee_per_transaction
FROM bank_transactions 
WHERE type = 'transfer_out' AND status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Create a view for revenue tracking (your profit only)
CREATE OR REPLACE VIEW sofi_revenue_tracking AS
SELECT 
    DATE_TRUNC('day', created_at) as day,
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as transactions,
    SUM(fee) as daily_sofi_profit,  -- Only your profit
    SUM(paystack_fee) as daily_paystack_costs,  -- What you owe Paystack
    SUM(fee) - SUM(paystack_fee) as net_daily_profit  -- Your net profit
FROM bank_transactions 
WHERE type = 'transfer_out' AND status = 'completed'
GROUP BY DATE_TRUNC('day', created_at), DATE_TRUNC('month', created_at)
ORDER BY day DESC;

-- Create a view for withdrawable profit (what you can withdraw from Paystack)
CREATE OR REPLACE VIEW withdrawable_profit AS
SELECT 
    SUM(fee) as total_sofi_profit,
    SUM(paystack_fee) as total_paystack_costs,
    COUNT(*) as total_transactions,
    SUM(fee) as withdrawable_amount  -- This is what you can withdraw
FROM bank_transactions 
WHERE type = 'transfer_out' AND status = 'completed';
