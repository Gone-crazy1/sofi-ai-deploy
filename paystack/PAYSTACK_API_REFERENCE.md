"""
Paystack API Integration for Sofi AI
===================================

Based on official Paystack API documentation:
https://paystack.com/docs/api/

CORE FEATURES NEEDED:
1. Virtual Accounts (Dedicated Accounts)
2. Transfers 
3. Webhooks
4. Customer Management
5. Transaction Verification

API ENDPOINTS:
- Create Customer: POST /customer
- Create Dedicated Account: POST /dedicated_account  
- Initialize Transfer: POST /transfer
- Finalize Transfer: POST /transfer/finalize_transfer
- Verify Transaction: GET /transaction/verify/:reference
- List Banks: GET /bank
- Resolve Account Number: GET /bank/resolve

WEBHOOKS:
- charge.success (incoming payments)
- transfer.success (outgoing transfers)
- transfer.failed (failed transfers)
- dedicated_account.assign (account created)

AUTHENTICATION:
- Secret Key: sk_live_xxx or sk_test_xxx
- Public Key: pk_live_xxx or pk_test_xxx
- All API calls use Authorization: Bearer {secret_key}
"""
