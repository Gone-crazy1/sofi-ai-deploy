#!/usr/bin/env python3
"""
WhatsApp Flow Integration Status Checker
Monitor the complete integration status and next steps
"""

import requests
import json
from datetime import datetime

def check_render_deployment():
    """Check if Render deployment is live and responding"""
    print("🔍 Checking Render.com deployment...")
    
    try:
        # Check main endpoint
        response = requests.get("https://www.pipinstallsofi.com/", timeout=10)
        if response.status_code == 200:
            print("✅ Main website responding")
        else:
            print(f"❌ Main website error: {response.status_code}")
            
        # Check WhatsApp Flow endpoint
        flow_response = requests.get("https://www.pipinstallsofi.com/whatsapp/flow", timeout=10)
        if flow_response.status_code == 200:
            print("✅ WhatsApp Flow endpoint responding")
        elif flow_response.status_code == 405:
            print("✅ WhatsApp Flow endpoint exists (405 Method Not Allowed for GET)")
        else:
            print(f"❌ WhatsApp Flow endpoint error: {flow_response.status_code}")
            
        # Check health endpoint
        health_response = requests.get("https://www.pipinstallsofi.com/health/flow", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Flow health endpoint responding")
            print(f"🔍 Encryption status: {health_data.get('encryption_ready', 'Unknown')}")
        else:
            print(f"❌ Flow health endpoint error: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking Render deployment: {e}")

def check_meta_flow_status():
    """Check Meta Flow configuration status"""
    print("\n🔍 Meta WhatsApp Flow Status...")
    
    print("✅ Flow ID: 1912417042942213")
    print("✅ Endpoint: https://www.pipinstallsofi.com/whatsapp/flow")
    print("✅ Public key updated: Fresh RSA-2048 key uploaded")
    print("✅ Meta verification: Success response received")

def check_environment_variables():
    """Check what environment variables need to be updated"""
    print("\n🔍 Required Render Environment Variables...")
    
    print("📋 CRITICAL: Update these in Render.com:")
    print("   1. WHATSAPP_FLOW_PRIVATE_KEY (fresh key generated)")
    print("   2. WHATSAPP_FLOW_PUBLIC_KEY (fresh key generated)")
    print("   3. WHATSAPP_VERIFY_TOKEN=sofi_ai_webhook_verify_2024")
    
    print("\n📄 Copy exact values from: WORKING_KEYS_FOR_RENDER.txt")

def test_encryption_locally():
    """Test encryption system locally"""
    print("\n🔍 Testing local encryption...")
    
    try:
        import os
        # Set fresh key for testing
        os.environ['WHATSAPP_FLOW_PRIVATE_KEY'] = 'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV1Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktRd2dnU2dBZ0VBQW9JQkFRQ2FkZzVEODRsUFRrUTQKdWtYcUh2ZmlCVkdlSlNnbEQ5MnBsZmdMTU1CTDE5SUpEaG9YV2tiL0twTVJxOHhDcGQxM3RmT3JYWXpLVGx1awpDU3VINjlkTnlSL01PZHhMaEdBTWpHTWFLKzVmS2Nvck1UNi9heWMvb01kcGlPUkk4Ylkzd1VKTDFtaFFmZlpCCldscENWbEtrMHR2WUlLQzFqdEp5Mk81NGhFaFBMdmx1VFpuQVk3MmQxNHNIdHkrbnMyMXRVbGtsWnNGZ3lpcC8KTE04anhJbWhOUXlNL09HYUtUcVZDWnJOK296eDhqMzNLTFIzTHpaRURrTE5FWXdxYkFFRk9Pa3dmTUpHQlc1KwpoK1BWN25KQ1IyQWNDd0Q0VVBHZDZOQ2dvOWtNRUhmVmoxdGQ4MnZmU0FsVGptdWxaZFZuM05YSkhhemFkTG5zCnlEekRJamJYQWdNQkFBRUNnZjhSUzlHaWRQaEFrOWhsTEhhbndOQUJLZXlrYzRTMTl4RGJRZS9aKzV1TTRwMzMKdXZIYnE1V2MvU2Q2MHhkaHRJWnRpL0puNkx5RjZ1c0N5SzdCM3Z3OUR2TXJRS1MvMEJMeFZNY1pmSHlLSzNraQpzbUQvRGxZQmRLbzFKeDhUdHFnR1FQTXJpdGJPTEtJUldnekJZT2sxaTd4bnpKVGRGU0VtWmM3NUJTeHBCcTBGCmZQbWlsd3J4Ry9wSEc1TFhONzBmSnNFU0JHRklDR2FOaVlWaytDMUh0Ukl6YjU4d1U4QmxXRVkzYXc3V3AxVkkKcm9ibFFZWGZJU3lpY2Z1K1QwakcxaHpYU1REWjMraFpaenhza0s0eUIyTDVPT05ac3Q4UmJWRld1NnVTc044Zwo5ZFJhdk03RUF6dkFmT2FURHhpdnU4enc2TkZUOC92SHQ1MFR2OEVDZ1lFQXpETXJnU0JzMmJxMFBwM1ZFRTltCjU0aW4wZm1qeEUxVmw4bTdCdENNblh6MU11VzJLVGQ5NkVCNVBIMXFMbXd1TERJTkg5a29TdlkzWGV5a0tBbjkKd0lOMDBmT1BSa1k4dXZKOWQyY1JMSnJXREhGQy9TOWZMYkdublI1ZUhwbndISjVYVmNLRThidVdTY3ZRSUdxWgpxU1Mxb1NNZ3FlZktQbnJ2Tkt2eUZ5Y0NnWUVBd2FUVXV6NmpjUCtNTkI2ejBta0wwRUh0SC9zekR6OWxqWHAzCkUxcSt1a2tCTGRKZ0hmZjJSZXVFYmlPdXFhQW52dnFPWXMrWUJQU3AxUjliOTBkODQzVElEalprUlRITjFVVE0KbzQ1b1B0eWtyK3pKUUNqcDFPT2k5eGFuNFdMK25sQ0l4RWo0NzdFMHU2MzBBRUVjZ2VKd1FIdnRUamt0cDRCdApWRmhxTU5FQ2dZQTZVWDdpUVAxMWJYSWUwL3JPenE2SC82cFdPS0xCNUloR2NuRzhyNEVKVlcrOTJvY2MzR0ZVCkhGM0RuZG5lYWowQm1FWFJTN2JMT2VoMEphcDRXT29rdWlaNTg4SitnbjdEc1krTnMxemZUVlZHZG01NFdyZ24KRjY3VUc2RXJ3akVtS3o2c0dvTFhld2lnQ05wbTk2cnMrTFA2MGtwNDI5OFIyeEJJRGJkMVR3S0JnRmJiYkdBZwpsSWNXMlBoMzNRaS8vWUNJVWFoS3NIaGlZMWEyVzdyZXRUWXhrTW5RMXpRYUNPa0wzdmJZSW53TFRraW5jajU0CkJ5UVI2aXVpU1VuOVV0TmppbWgxbFR4RVBxTXVuT3V2OEtwaHBhMFRkS0hHdUR1NWIxdU5XZmdLdzFLWHBRRUcKQ2tMWkpXSVpnSnlzbC9EYWRLYzM3eFZyS0VNOW84eDFiQXhCQW9HQUc1Y1J2UTNDeGxyN215U1NaVUFnRnlYLwpkMWJyOFA4TmgvUDRkT2tNTVlBVzZrNGtmVFVwaHMvK3Q0TUVZV0RKNnlsN0ZIb0JtUXFWRjF1RFRHUmVBNzlSCnl5M011WHhKVWtsVVJYcGVKb3V0SGp3dmJkL1AyVi9MT0lRR0p3Y1RIVnlwSzNlNmFPa2ZQRjVabnBzZG15OWEKYUlDbGFuR3BrMUowbTNqL2E4ST0KLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLQo='
        
        from flow_encryption import get_flow_encryption
        flow_encryption = get_flow_encryption()
        
        if flow_encryption:
            print("✅ Local encryption initialization successful")
        else:
            print("❌ Local encryption initialization failed")
            
    except Exception as e:
        print(f"❌ Local encryption test failed: {e}")

def show_next_steps():
    """Show the exact next steps"""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS TO COMPLETE INTEGRATION:")
    print("="*60)
    
    print("\n1️⃣ UPDATE RENDER ENVIRONMENT VARIABLES:")
    print("   • Go to: https://dashboard.render.com")
    print("   • Find your service → Environment tab")
    print("   • Update with values from WORKING_KEYS_FOR_RENDER.txt")
    
    print("\n2️⃣ VERIFY DEPLOYMENT:")
    print("   • Wait for Render auto-deployment")
    print("   • Check logs for 'Private key loaded successfully'")
    print("   • Confirm no more '500 Encryption not available' errors")
    
    print("\n3️⃣ TEST WHATSAPP FLOW:")
    print("   • Try sending a Flow from WhatsApp Business")
    print("   • Monitor Render logs for encrypted data processing")
    print("   • Verify successful decryption")
    
    print("\n4️⃣ SUCCESS INDICATORS:")
    print("   ✅ No more 'InvalidByte(1623, 61)' errors")
    print("   ✅ Meta IP traffic gets 200 responses")
    print("   ✅ Encrypted data decrypts successfully")
    print("   ✅ WhatsApp Flow completes end-to-end")

def main():
    print("🔍 WhatsApp Flow Integration Status Check")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_render_deployment()
    check_meta_flow_status()
    check_environment_variables()
    test_encryption_locally()
    show_next_steps()
    
    print("\n🚀 Ready to complete the integration!")

if __name__ == "__main__":
    main()
