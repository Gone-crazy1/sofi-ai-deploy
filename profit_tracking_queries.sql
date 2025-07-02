-- SOFI AI PROFIT TRACKING QUERIES
-- Use these in your Supabase SQL editor to track your profits

-- 1. Check your current withdrawable profit
SELECT * FROM withdrawable_profit;

-- 2. Daily profit breakdown  
SELECT 
    day,
    transactions,
    daily_sofi_profit as "Your Profit (₦)",
    daily_paystack_costs as "Paystack Costs (₦)"
FROM sofi_revenue_tracking 
WHERE day >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY day DESC;

-- 3. Monthly profit summary
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as transactions,
    SUM(amount) as total_transferred,
    SUM(fee) as monthly_profit
FROM bank_transactions 
WHERE type = 'transfer_out' AND status = 'completed'
AND created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- 4. Top users by fees generated (your best customers)
SELECT 
    user_id,
    COUNT(*) as transactions,
    SUM(amount) as total_transferred,
    SUM(fee) as profit_generated
FROM bank_transactions 
WHERE type = 'transfer_out' AND status = 'completed'
GROUP BY user_id
ORDER BY profit_generated DESC
LIMIT 10;

-- 5. Recent transactions with full fee breakdown
SELECT 
    created_at,
    amount as "Transfer Amount",
    fee as "Sofi Profit",
    paystack_fee as "Paystack Cost", 
    total_amount as "Total Charged",
    recipient_name,
    status
FROM bank_transactions 
WHERE type = 'transfer_out'
ORDER BY created_at DESC
LIMIT 20;
