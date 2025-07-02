-- Enhanced Fee Tracking Migration for Sofi AI
-- This adds columns to track Sofi fees (profit) and Paystack fees (costs) separately

-- Add new columns to bank_transactions table if they don't exist
DO $$
BEGIN
    -- Add sofi_fee column (your profit)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bank_transactions' AND column_name = 'sofi_fee') THEN
        ALTER TABLE bank_transactions ADD COLUMN sofi_fee DECIMAL(15,2) DEFAULT 0;
    END IF;
    
    -- Add paystack_fee column (your cost)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bank_transactions' AND column_name = 'paystack_fee') THEN
        ALTER TABLE bank_transactions ADD COLUMN paystack_fee DECIMAL(15,2) DEFAULT 0;
    END IF;
    
    -- Add balance_before column (for audit trail)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bank_transactions' AND column_name = 'balance_before') THEN
        ALTER TABLE bank_transactions ADD COLUMN balance_before DECIMAL(15,2) DEFAULT 0;
    END IF;
    
    -- Add balance_after column (for audit trail)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bank_transactions' AND column_name = 'balance_after') THEN
        ALTER TABLE bank_transactions ADD COLUMN balance_after DECIMAL(15,2) DEFAULT 0;
    END IF;
    
    -- Add net_profit column (calculated: sofi_fee - paystack_fee)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bank_transactions' AND column_name = 'net_profit') THEN
        ALTER TABLE bank_transactions ADD COLUMN net_profit DECIMAL(15,2) DEFAULT 0;
    END IF;
END
$$;

-- Update existing records to populate the new columns from existing fee column
UPDATE bank_transactions 
SET 
    sofi_fee = COALESCE(fee, 0),  -- Assume existing fees are Sofi fees
    paystack_fee = 10.0,          -- Assume ₦10 Paystack fee for all transfers
    net_profit = COALESCE(fee, 0) - 10.0  -- Calculate net profit
WHERE sofi_fee IS NULL OR sofi_fee = 0;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bank_transactions_sofi_fee ON bank_transactions(sofi_fee);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_paystack_fee ON bank_transactions(paystack_fee);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_net_profit ON bank_transactions(net_profit);

-- Create view for enhanced profit tracking
CREATE OR REPLACE VIEW profit_tracking_enhanced AS
SELECT 
    DATE(created_at) as transaction_date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_transfer_volume,
    SUM(sofi_fee) as total_sofi_fees,
    SUM(paystack_fee) as total_paystack_costs,
    SUM(sofi_fee - paystack_fee) as net_profit,
    AVG(sofi_fee) as avg_sofi_fee,
    AVG(paystack_fee) as avg_paystack_cost,
    ROUND((SUM(sofi_fee - paystack_fee) / SUM(amount)) * 100, 4) as profit_margin_percentage
FROM bank_transactions 
WHERE type = 'transfer_out' 
  AND sofi_fee > 0
GROUP BY DATE(created_at)
ORDER BY transaction_date DESC;

-- Create view for daily revenue summary
CREATE OR REPLACE VIEW daily_revenue_summary AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as transfers,
    SUM(amount) as volume,
    SUM(sofi_fee) as sofi_revenue,
    SUM(paystack_fee) as paystack_costs,
    SUM(sofi_fee - paystack_fee) as net_profit,
    CASE 
        WHEN SUM(amount) > 0 THEN ROUND((SUM(sofi_fee - paystack_fee) / SUM(amount)) * 100, 4)
        ELSE 0 
    END as profit_margin_pct
FROM bank_transactions 
WHERE type = 'transfer_out'
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Create trigger to auto-calculate net_profit when inserting/updating
CREATE OR REPLACE FUNCTION calculate_net_profit()
RETURNS TRIGGER AS $$
BEGIN
    NEW.net_profit = COALESCE(NEW.sofi_fee, 0) - COALESCE(NEW.paystack_fee, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calculate_net_profit ON bank_transactions;
CREATE TRIGGER trigger_calculate_net_profit
    BEFORE INSERT OR UPDATE ON bank_transactions
    FOR EACH ROW
    EXECUTE FUNCTION calculate_net_profit();

-- Display migration results
SELECT 
    'Enhanced Fee Tracking Migration Completed!' as status,
    COUNT(*) as total_transactions,
    SUM(sofi_fee) as total_sofi_fees,
    SUM(paystack_fee) as total_paystack_costs,
    SUM(net_profit) as total_net_profit
FROM bank_transactions;
