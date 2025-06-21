"""
🏦 COMPREHENSIVE NIGERIAN BANKS DATABASE
========================================

Complete database of 50+ Nigerian banks including:
- Traditional banks
- Fintech banks (Opay, Kuda, PalmPay, etc.)
- Microfinance banks
- Accurate bank codes for transfers
"""

NIGERIAN_BANKS = {
    # TRADITIONAL COMMERCIAL BANKS
    "access": {
        "name": "Access Bank",
        "code": "044",
        "full_name": "Access Bank Plc",
        "type": "commercial"
    },
    "gtbank": {
        "name": "GTBank",
        "code": "058",
        "full_name": "Guaranty Trust Bank",
        "type": "commercial"
    },
    "zenith": {
        "name": "Zenith Bank",
        "code": "057",
        "full_name": "Zenith Bank Plc",
        "type": "commercial"
    },
    "uba": {
        "name": "UBA",
        "code": "033",
        "full_name": "United Bank for Africa",
        "type": "commercial"
    },
    "firstbank": {
        "name": "First Bank",
        "code": "011",
        "full_name": "First Bank of Nigeria",
        "type": "commercial"
    },
    "fidelity": {
        "name": "Fidelity Bank",
        "code": "070",
        "full_name": "Fidelity Bank Plc",
        "type": "commercial"
    },
    "fcmb": {
        "name": "FCMB",
        "code": "214",
        "full_name": "First City Monument Bank",
        "type": "commercial"
    },
    "union": {
        "name": "Union Bank",
        "code": "032",
        "full_name": "Union Bank of Nigeria",
        "type": "commercial"
    },
    "sterling": {
        "name": "Sterling Bank",
        "code": "232",
        "full_name": "Sterling Bank Plc",
        "type": "commercial"
    },
    "stanbic": {
        "name": "Stanbic IBTC",
        "code": "221",
        "full_name": "Stanbic IBTC Bank",
        "type": "commercial"
    },
    "wema": {
        "name": "Wema Bank",
        "code": "035",
        "full_name": "Wema Bank Plc",
        "type": "commercial"
    },
    "ecobank": {
        "name": "Ecobank",
        "code": "050",
        "full_name": "Ecobank Nigeria",
        "type": "commercial"
    },
    "heritage": {
        "name": "Heritage Bank",
        "code": "030",
        "full_name": "Heritage Banking Company Ltd",
        "type": "commercial"
    },
    "keystone": {
        "name": "Keystone Bank",
        "code": "082",
        "full_name": "Keystone Bank Limited",
        "type": "commercial"
    },
    "polaris": {
        "name": "Polaris Bank",
        "code": "076",
        "full_name": "Polaris Bank Limited",
        "type": "commercial"
    },
    "providus": {
        "name": "Providus Bank",
        "code": "101",
        "full_name": "Providus Bank Limited",
        "type": "commercial"
    },
    "unity": {
        "name": "Unity Bank",
        "code": "215",
        "full_name": "Unity Bank Plc",
        "type": "commercial"
    },
    "citi": {
        "name": "Citibank",
        "code": "023",
        "full_name": "Citibank Nigeria Limited",
        "type": "international"
    },
    "standard": {
        "name": "Standard Chartered",
        "code": "068",
        "full_name": "Standard Chartered Bank",
        "type": "international"
    },
    
    # FINTECH BANKS (Most Popular)
    "opay": {
        "name": "Opay",
        "code": "999992",
        "full_name": "Opay Digital Services Limited",
        "type": "fintech"
    },
    "kuda": {
        "name": "Kuda Bank",
        "code": "50211",
        "full_name": "Kuda Microfinance Bank",
        "type": "fintech"
    },
    "palmpay": {
        "name": "PalmPay",
        "code": "999991",
        "full_name": "PalmPay Limited",
        "type": "fintech"
    },
    "carbon": {
        "name": "Carbon",
        "code": "565",
        "full_name": "Carbon Microfinance Bank",
        "type": "fintech"
    },
    "vfd": {
        "name": "VFD Bank",
        "code": "566",
        "full_name": "VFD Microfinance Bank",
        "type": "fintech"
    },
    "fairmoney": {
        "name": "FairMoney",
        "code": "51318",
        "full_name": "FairMoney Microfinance Bank",
        "type": "fintech"
    },
    "mint": {
        "name": "Mint Bank",
        "code": "50304",
        "full_name": "Mint Fintech Limited",
        "type": "fintech"
    },
    "rubies": {
        "name": "Rubies Bank",
        "code": "125",
        "full_name": "Rubies Microfinance Bank",
        "type": "fintech"
    },
    "sparkle": {
        "name": "Sparkle Bank",
        "code": "51310",
        "full_name": "Sparkle Microfinance Bank",
        "type": "fintech"
    },
    "raven": {
        "name": "Raven Bank",
        "code": "50746",
        "full_name": "Raven Bank Limited",
        "type": "fintech"
    },
    
    # MICROFINANCE BANKS
    "lapo": {
        "name": "LAPO MFB",
        "code": "50563",
        "full_name": "LAPO Microfinance Bank",
        "type": "microfinance"
    },
    "accion": {
        "name": "Accion MFB",
        "code": "50036",
        "full_name": "Accion Microfinance Bank",
        "type": "microfinance"
    },
    "ab": {
        "name": "AB Microfinance",
        "code": "50926",
        "full_name": "AB Microfinance Bank",
        "type": "microfinance"
    },
    "astrapolaris": {
        "name": "Astra Polaris MFB",
        "code": "MFB50094",
        "full_name": "Astra Polaris Microfinance Bank",
        "type": "microfinance"
    },
    "boctrust": {
        "name": "BOC Trust MFB",
        "code": "50117",
        "full_name": "BOC Trust Microfinance Bank",
        "type": "microfinance"
    },
    "cemcs": {
        "name": "CEMCS MFB",
        "code": "50823",
        "full_name": "CEMCS Microfinance Bank",
        "type": "microfinance"
    },
    "consumer": {
        "name": "Consumer MFB",
        "code": "50910",
        "full_name": "Consumer Microfinance Bank",
        "type": "microfinance"
    },
    "corestep": {
        "name": "Corestep MFB",
        "code": "50204",
        "full_name": "Corestep Microfinance Bank",
        "type": "microfinance"
    },
    "daylight": {
        "name": "Daylight MFB",
        "code": "50504",
        "full_name": "Daylight Microfinance Bank",
        "type": "microfinance"
    },
    "dot": {
        "name": "Dot MFB",
        "code": "50162",
        "full_name": "Dot Microfinance Bank",
        "type": "microfinance"
    },
    "empire": {
        "name": "Empire MFB",
        "code": "50126",
        "full_name": "Empire Microfinance Bank",
        "type": "microfinance"
    },
    "ffs": {
        "name": "FFS MFB",
        "code": "51229",
        "full_name": "FFS Microfinance Bank",
        "type": "microfinance"
    },
    "fullrange": {
        "name": "Fullrange MFB",
        "code": "50224",
        "full_name": "Fullrange Microfinance Bank",
        "type": "microfinance"
    },
    "hasal": {
        "name": "Hasal MFB",
        "code": "50383",
        "full_name": "Hasal Microfinance Bank",
        "type": "microfinance"
    },
    "ibile": {
        "name": "Ibile MFB",
        "code": "51244",
        "full_name": "Ibile Microfinance Bank",
        "type": "microfinance"
    },
    "infinity": {
        "name": "Infinity MFB",
        "code": "50457",
        "full_name": "Infinity Microfinance Bank",
        "type": "microfinance"
    },
    "kredi": {
        "name": "Kredi Money MFB",
        "code": "50200",
        "full_name": "Kredi Money Microfinance Bank",
        "type": "microfinance"
    },
    "mayfresh": {
        "name": "Mayfresh MFB",
        "code": "50603",
        "full_name": "Mayfresh Microfinance Bank",
        "type": "microfinance"
    },
    "moniepoint": {
        "name": "Moniepoint MFB",
        "code": "50515",
        "full_name": "Moniepoint Microfinance Bank",
        "type": "fintech"
    },
    "mutual": {
        "name": "Mutual Benefits MFB",
        "code": "50629",
        "full_name": "Mutual Benefits Microfinance Bank",
        "type": "microfinance"
    },
    "nova": {
        "name": "Nova MFB",
        "code": "50206",
        "full_name": "Nova Microfinance Bank",
        "type": "microfinance"
    },
    "page": {
        "name": "Page MFB",
        "code": "50551",
        "full_name": "Page Microfinance Bank",
        "type": "microfinance"
    },
    "pecantrust": {
        "name": "Pecan Trust MFB",
        "code": "50746",
        "full_name": "Pecan Trust Microfinance Bank",
        "type": "microfinance"
    },
    "regent": {
        "name": "Regent MFB",
        "code": "50554",
        "full_name": "Regent Microfinance Bank",
        "type": "microfinance"
    },
    "reliance": {
        "name": "Reliance MFB",
        "code": "50767",
        "full_name": "Reliance Microfinance Bank",
        "type": "microfinance"
    },
    "safe": {
        "name": "Safe Haven MFB",
        "code": "51113",
        "full_name": "Safe Haven Microfinance Bank",
        "type": "microfinance"
    },
    "shield": {
        "name": "Shield MFB",
        "code": "50582",
        "full_name": "Shield Microfinance Bank",
        "type": "microfinance"
    },
    "stellas": {
        "name": "Stellas MFB",
        "code": "51253",
        "full_name": "Stellas Microfinance Bank",
        "type": "microfinance"
    },
    "trustfund": {
        "name": "Trustfund MFB",
        "code": "51269",
        "full_name": "Trustfund Microfinance Bank",
        "type": "microfinance"
    }
}

# Quick lookup functions
def get_bank_by_name(bank_name):
    """Get bank info by name (case insensitive, partial match)"""
    bank_name = bank_name.lower().strip()
    
    # Direct key match
    if bank_name in NIGERIAN_BANKS:
        return NIGERIAN_BANKS[bank_name]
    
    # Search by bank name
    for key, bank in NIGERIAN_BANKS.items():
        if bank_name in bank["name"].lower() or bank_name in bank["full_name"].lower():
            return bank
    
    # Search by common aliases
    aliases = {
        "gt": "gtbank",
        "guaranty": "gtbank", 
        "first": "firstbank",
        "fbn": "firstbank",
        "access": "access",
        "zenith": "zenith",
        "uba": "uba",
        "united": "uba",
        "wema": "wema",
        "sterling": "sterling",
        "union": "union",
        "fcmb": "fcmb",
        "fidelity": "fidelity",
        "eco": "ecobank",
        "ecobank": "ecobank",
        "heritage": "heritage",
        "stanbic": "stanbic",
        "ibtc": "stanbic",
        "standard": "standard",
        "chartered": "standard",
        "polaris": "polaris",
        "keystone": "keystone",
        "providus": "providus",
        "unity": "unity",
        "citi": "citi",
        "citibank": "citi",
        "kuda": "kuda",
        "carbon": "carbon",
        "palmpay": "palmpay",
        "palm": "palmpay",
        "opay": "opay",
        "vfd": "vfd",
        "mint": "mint",
        "fairmoney": "fairmoney",
        "fair": "fairmoney",
        "moniepoint": "moniepoint",
        "monie": "moniepoint"
    }
    
    if bank_name in aliases:
        return NIGERIAN_BANKS[aliases[bank_name]]
    
    return None

def get_bank_by_code(bank_code):
    """Get bank info by bank code"""
    for bank in NIGERIAN_BANKS.values():
        if bank["code"] == str(bank_code):
            return bank
    return None

def get_all_banks():
    """Get all banks as a list"""
    return list(NIGERIAN_BANKS.values())

def get_banks_by_type(bank_type):
    """Get banks by type (commercial, fintech, microfinance)"""
    return [bank for bank in NIGERIAN_BANKS.values() if bank["type"] == bank_type]

def search_banks(query):
    """Search banks by name or code"""
    query = query.lower().strip()
    results = []
    
    for bank in NIGERIAN_BANKS.values():
        if (query in bank["name"].lower() or 
            query in bank["full_name"].lower() or 
            query in bank["code"]):
            results.append(bank)
    
    return results

# Popular banks for quick suggestions
POPULAR_BANKS = [
    "opay", "kuda", "palmpay", "gtbank", "access", "zenith", "uba", 
    "firstbank", "wema", "sterling", "fcmb", "carbon", "moniepoint"
]

def get_popular_banks():
    """Get list of popular banks"""
    return [NIGERIAN_BANKS[key] for key in POPULAR_BANKS if key in NIGERIAN_BANKS]
