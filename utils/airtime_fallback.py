#!/usr/bin/env python3
"""
Airtime Fallback System
Provides USSD codes and alternative solutions when Nellobytes is unavailable
"""

import logging

logger = logging.getLogger(__name__)

def get_ussd_codes(network: str, amount: float, phone_number: str = None) -> str:
    """Get USSD codes for manual airtime purchase when API is down"""
    
    network_lower = network.lower()
    
    # Network USSD codes for airtime purchase
    ussd_codes = {
        'mtn': {
            'recharge': '*555*PIN#',
            'transfer': f'*777*{phone_number}*{int(amount)}*PIN#' if phone_number else '*777*PHONE*AMOUNT*PIN#',
            'buy_for_self': f'*555*{int(amount)}*PIN#',
            'customer_care': '*199#'
        },
        'airtel': {
            'recharge': '*432*PIN#',
            'transfer': f'*432*1*{int(amount)}*{phone_number}*PIN#' if phone_number else '*432*1*AMOUNT*PHONE*PIN#',
            'buy_for_self': f'*432*{int(amount)}*PIN#',
            'customer_care': '*121#'
        },
        'glo': {
            'recharge': '*321*PIN#',
            'transfer': f'*321*{phone_number}*{int(amount)}*PIN#' if phone_number else '*321*PHONE*AMOUNT*PIN#',
            'buy_for_self': f'*321*{int(amount)}*PIN#',
            'customer_care': '*121#'
        },
        '9mobile': {
            'recharge': '*200*PIN#',
            'transfer': f'*223*{phone_number}*{int(amount)}*PIN#' if phone_number else '*223*PHONE*AMOUNT*PIN#',
            'buy_for_self': f'*200*{int(amount)}*PIN#',
            'customer_care': '*200#'
        }
    }
    
    if network_lower in ussd_codes:
        codes = ussd_codes[network_lower]
        
        response = f"📱 **{network.upper()} USSD Codes for ₦{amount:,.0f} Airtime**\n\n"
        
        if phone_number:
            response += f"🎯 **Transfer to {phone_number}:**\n"
            response += f"• Dial: `{codes['transfer']}`\n"
            response += f"• Replace PIN with your {network.upper()} transaction PIN\n\n"
        
        response += f"🔄 **Buy for yourself:**\n"
        response += f"• Dial: `{codes['buy_for_self']}`\n"
        response += f"• Replace PIN with your {network.upper()} transaction PIN\n\n"
        
        response += f"💳 **Alternative Options:**\n"
        response += f"• Visit any {network.upper()} outlet\n"
        response += f"• Use your bank's mobile app\n"
        response += f"• Buy airtime voucher/recharge card\n"
        response += f"• Use ATM airtime purchase\n\n"
        
        response += f"📞 **Need Help?**\n"
        response += f"• Customer care: `{codes['customer_care']}`\n"
        response += f"• Visit {network.upper()} website or app"
        
        return response
    else:
        return f"❌ Unknown network: {network}"

def get_data_bundle_ussd(network: str) -> str:
    """Get USSD codes for data bundle purchase"""
    
    network_lower = network.lower()
    
    data_ussd = {
        'mtn': {
            'code': '*131#',
            'description': 'MTN Data Plans'
        },
        'airtel': {
            'code': '*141#',
            'description': 'Airtel Data Plans'
        },
        'glo': {
            'code': '*127*0#',
            'description': 'Glo Data Plans'
        },
        '9mobile': {
            'code': '*200#',
            'description': '9mobile Data Plans'
        }
    }
    
    if network_lower in data_ussd:
        info = data_ussd[network_lower]
        return f"📶 **{network.upper()} Data Bundle:**\n• Dial: `{info['code']}`\n• Follow menu to select plan"
    else:
        return f"❌ Unknown network: {network}"

def get_comprehensive_alternatives(network: str, amount: float, phone_number: str = None, is_data: bool = False) -> str:
    """Get comprehensive alternative solutions when main service is down"""
    
    response = f"🚨 **Service Temporarily Unavailable**\n\n"
    response += f"Our automated {network.upper()} {'data' if is_data else 'airtime'} service is currently down.\n\n"
    
    if is_data:
        response += f"📶 **Get Data Bundle Instead:**\n"
        response += get_data_bundle_ussd(network) + "\n\n"
    else:
        response += get_ussd_codes(network, amount, phone_number) + "\n\n"
    
    response += f"⏱️ **Service Recovery:**\n"
    response += f"• We're working to fix this issue\n"
    response += f"• Try again in 15-30 minutes\n"
    response += f"• Follow our status updates\n\n"
    
    response += f"🙏 **We apologize for the inconvenience!**\n"
    response += f"The alternatives above should help you complete your purchase."
    
    return response

def create_airtime_service_status_message() -> str:
    """Create a service status message for airtime issues"""
    return """🔧 **Airtime Service Status Update**

**Current Issue:** Our airtime provider (Nellobytes) is experiencing connectivity problems.

**What's happening:**
• Domain resolution failure
• Service may be under maintenance
• Network connectivity issues

**Your Options:**
1️⃣ **Use USSD Codes** (Recommended)
   • MTN: *555*AMOUNT*PIN#
   • Airtel: *432*AMOUNT*PIN#
   • Glo: *321*AMOUNT*PIN#
   • 9mobile: *200*AMOUNT*PIN#

2️⃣ **Mobile Banking**
   • Use your bank's app
   • Most support airtime purchase

3️⃣ **Physical Options**
   • Network outlets
   • Recharge cards
   • ATM airtime purchase

**When will it be fixed?**
We're monitoring the situation and expect service restoration within 1-2 hours.

**Questions?** Contact support or use the alternatives above.

Thank you for your patience! 🙏"""

if __name__ == "__main__":
    # Test the fallback system
    print("Testing USSD fallback system...")
    print(get_ussd_codes("MTN", 1000, "08012345678"))
    print("\n" + "="*50 + "\n")
    print(get_comprehensive_alternatives("Airtel", 500, "08023456789"))
