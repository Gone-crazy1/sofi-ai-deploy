"""
9PSB + Paystack Hybrid Architecture for Sofi AI
===============================================

MONEY FLOW:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User's Bank   │───▶│  9PSB Virtual   │───▶│   Sofi Wallet   │
│                 │    │    Account      │    │   (Supabase)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Paystack API  │
                                               │   (Transfers)   │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Recipient Bank  │
                                               └─────────────────┘

INTEGRATION POINTS:

1. USER ONBOARDING:
   - Create 9PSB virtual account for deposits
   - Store account details in Supabase
   - Link to user's Telegram chat_id

2. INCOMING MONEY (via 9PSB):
   - 9PSB webhook → Update user balance
   - Send Telegram notification
   - Low/no fees

3. OUTGOING TRANSFERS (via Paystack):
   - User initiates transfer via AI Assistant
   - Paystack API processes transfer
   - Deduct from user balance
   - Send confirmation & receipt

4. BALANCE MANAGEMENT:
   - Track all balances in Supabase
   - Real-time updates from both providers
   - Reconciliation system

COST STRUCTURE:
- Virtual Account: ~₦0-50/month (9PSB)
- Incoming transfers: ~₦0-25 (9PSB)
- Outgoing transfers: ~1.5% + ₦100 (Paystack)
- Net effect: Much cheaper than full Paystack

TECHNICAL BENEFITS:
- Separate concerns (deposits vs transfers)
- Better error handling (provider-specific)
- Easier to optimize each service independently
- Can switch providers per service type
"""
