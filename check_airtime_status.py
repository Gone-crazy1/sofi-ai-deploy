#!/usr/bin/env python3
"""
Quick Nellobytes Service Status Checker
This script provides a quick way to check if Nellobytes services are available
"""

import requests
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def check_nellobytes_status():
    """Quick status check for Nellobytes API"""
    print("🔍 **Nellobytes Service Status Check**\n")
    
    # Check 1: DNS Resolution
    print("1️⃣ **DNS Resolution Test**")
    try:
        ip = socket.gethostbyname('nellobytesystem.com')
        print(f"   ✅ DNS OK: nellobytesystem.com -> {ip}")
        dns_ok = True
    except socket.gaierror as e:
        print(f"   ❌ DNS FAILED: {e}")
        dns_ok = False
    
    # Check 2: HTTP Connectivity
    print("\n2️⃣ **HTTP Connectivity Test**")
    if dns_ok:
        try:
            response = requests.get('https://nellobytesystem.com', timeout=10)
            print(f"   ✅ HTTP OK: Status {response.status_code}")
            http_ok = True
        except requests.exceptions.ConnectionError:
            print("   ❌ HTTP FAILED: Connection refused")
            http_ok = False
        except requests.exceptions.Timeout:
            print("   ❌ HTTP FAILED: Request timeout")
            http_ok = False
        except Exception as e:
            print(f"   ❌ HTTP FAILED: {e}")
            http_ok = False
    else:
        print("   ⏭️ SKIPPED: DNS resolution failed")
        http_ok = False
    
    # Check 3: Credentials
    print("\n3️⃣ **Credentials Check**")
    user_id = os.getenv("NELLOBYTES_USERID") or os.getenv("NELLOBYTES_USER_ID")
    api_key = os.getenv("NELLOBYTES_APIKEY") or os.getenv("NELLOBYTES_PASSWORD")
    
    if user_id and api_key:
        print(f"   ✅ CONFIGURED: User ID: {user_id[:4]}***, API Key: ***{api_key[-4:]}")
        creds_ok = True
    else:
        print("   ❌ MISSING: Check .env file for NELLOBYTES_USERID and NELLOBYTES_APIKEY")
        creds_ok = False
    
    # Overall Status
    print("\n" + "="*50)
    print("📊 **OVERALL STATUS**")
    
    if all([dns_ok, http_ok, creds_ok]):
        print("🎉 **ALL SYSTEMS OPERATIONAL** - Airtime should work!")
        return True
    elif not dns_ok:
        print("🌐 **DOMAIN ISSUE** - nellobytesystem.com is unreachable")
        print("\n💡 **Possible Causes:**")
        print("   • Domain expired or suspended")
        print("   • DNS server issues")
        print("   • Internet connectivity problems")
        print("   • Domain blocked by firewall/ISP")
        print("\n🔧 **Solutions:**")
        print("   • Wait and try again later")
        print("   • Try different DNS servers (8.8.8.8)")
        print("   • Contact Nellobytes support")
        print("   • Use USSD codes as backup")
        return False
    elif not http_ok:
        print("🚫 **CONNECTION ISSUE** - Server not responding")
        print("\n💡 **Possible Causes:**")
        print("   • Server maintenance")
        print("   • High traffic/overload")
        print("   • Service outage")
        print("\n🔧 **Solutions:**")
        print("   • Wait 10-15 minutes and retry")
        print("   • Check Nellobytes status page")
        print("   • Use alternative airtime methods")
        return False
    elif not creds_ok:
        print("🔑 **CONFIGURATION ISSUE** - Missing API credentials")
        print("\n🔧 **Solutions:**")
        print("   • Add NELLOBYTES_USERID to .env file")
        print("   • Add NELLOBYTES_APIKEY to .env file")
        print("   • Contact admin for credentials")
        return False
    else:
        print("⚠️ **PARTIAL ISSUES** - Some components failing")
        return False

if __name__ == "__main__":
    check_nellobytes_status()
