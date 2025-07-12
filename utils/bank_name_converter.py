"""
🏦 BANK CODE TO NAME CONVERTER

Converts bank codes to friendly bank names for better UX
"""

def get_bank_name_from_code(bank_code: str) -> str:
    """Convert bank code to friendly bank name"""
    
    # Nigerian bank codes mapping
    bank_codes = {
        "044": "Access Bank",
        "014": "Afribank",
        "023": "Citibank",
        "050": "EcoBank",
        "011": "First Bank",
        "214": "First City Monument Bank (FCMB)",
        "070": "Fidelity Bank",
        "058": "Guaranty Trust Bank (GTBank)",
        "030": "Heritage Bank",
        "301": "Jaiz Bank",
        "082": "Keystone Bank",
        "076": "Polaris Bank",
        "221": "Stanbic IBTC Bank",
        "068": "Standard Chartered Bank",
        "232": "Sterling Bank",
        "033": "United Bank for Africa (UBA)",
        "032": "Union Bank",
        "215": "Unity Bank",
        "035": "Wema Bank",
        "057": "Zenith Bank",
        "039": "Stanbic IBTC Bank",
        "232": "Sterling Bank",
        "101": "ProvidusBank",
        "100": "SunTrust Bank",
        "102": "Titan Trust Bank",
        "103": "Globus Bank",
        "104": "PremiumTrust Bank",
        "090": "VFD Microfinance Bank",
        "50515": "Moniepoint MFB",
        "999991": "PalmPay",
        "999992": "OPay",
        "999993": "Kuda Bank",
        "50746": "Sparkle Microfinance Bank",
        "51251": "Rubies Bank",
        "090364": "Carbon",
        "090416": "Eyowo",
        "100029": "TAJBank",
        "000": "Central Bank of Nigeria (CBN)",
        
        # Additional fintech and mobile money codes
        "120001": "9mobile 9Payment Service Bank",
        "120002": "Airtel Smartcash PSB",
        "120003": "MTN MoMo PSB",
        "070006": "Covenant Microfinance Bank",
        "070007": "Finca Microfinance Bank",
        "070008": "Page Microfinance Bank",
        "070009": "Gateway Mortgage Bank",
        "070010": "VFD Microfinance Bank",
        "070011": "Eartholeum",
        "070012": "Lagos Building Investment Company Plc",
        "070013": "FFS Microfinance Bank",
        "070014": "NIRSAL Microfinance Bank",
        "070015": "Infinity MFB",
        "070016": "SafeMFB",
        "070017": "Daylight Microfinance Bank",
        "070018": "Kredi Money MFB LTD",
        "070019": "Mayfresh Mortgage Bank",
        "070020": "Gowans Microfinance Bank",
        "566": "NPF Microfinance Bank"
    }
    
    # Clean the bank code (remove spaces, convert to string)
    if bank_code:
        bank_code = str(bank_code).strip()
        
        # Return the friendly name if found, otherwise return the code with "Bank"
        friendly_name = bank_codes.get(bank_code)
        if friendly_name:
            return friendly_name
        else:
            # For unknown codes, return the code with "Bank" suffix
            return f"Bank ({bank_code})"
    
    return "Unknown Bank"


def format_transfer_message(amount, recipient_name, account_number, bank_code, status="successful"):
    """Format a user-friendly transfer confirmation message"""
    
    bank_name = get_bank_name_from_code(bank_code)
    
    if status == "successful":
        emoji = "✅"
        status_text = "Transfer Successful!"
    else:
        emoji = "❌"
        status_text = "Transfer Failed"
    
    message = f"""
{emoji} *{status_text}*

💰 *Amount:* ₦{amount:,}
👤 *To:* {recipient_name}
🏦 *Bank:* {bank_name}
📱 *Account:* {account_number}

Your transfer has been {'completed' if status == 'successful' else 'unsuccessful'}!
"""
    
    return message.strip()


def enhance_transaction_description(description, bank_code=None):
    """Enhance transaction descriptions by converting bank codes to names"""
    if not description:
        return description
    
    # If bank_code is provided, try to replace codes in description
    if bank_code:
        bank_name = get_bank_name_from_code(bank_code)
        # Replace any occurrence of the bank code with the bank name
        description = description.replace(f"({bank_code})", f"({bank_name})")
        description = description.replace(bank_code, bank_name)
    
    return description


# Test function
if __name__ == "__main__":
    # Test cases
    print("Testing bank code converter:")
    print(f"035: {get_bank_name_from_code('035')}")
    print(f"058: {get_bank_name_from_code('058')}")
    print(f"50515: {get_bank_name_from_code('50515')}")
    print(f"999991: {get_bank_name_from_code('999991')}")
    print(f"Unknown code: {get_bank_name_from_code('999999')}")
    
    print("\nTesting transfer message:")
    print(format_transfer_message(5000, "John Doe", "1234567890", "035"))
