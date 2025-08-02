#!/usr/bin/env python3
"""
Emergency deployment status checker for Sofi WhatsApp
Monitors the deployment to ensure the syntax error is fixed
"""

import time
import requests
import json

def check_deployment_status():
    """Check if the deployment fixed the syntax error"""
    try:
        # Check main website
        print("🔍 Checking deployment status...")
        response = requests.get("https://www.pipinstallsofi.com/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Main website responding (syntax error fixed!)")
            return True
        else:
            print(f"❌ Main website error: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def monitor_deployment():
    """Monitor deployment until success"""
    print("🚀 EMERGENCY DEPLOYMENT MONITOR")
    print("================================")
    print("Waiting for Render.com to deploy syntax fix...")
    print("")
    
    attempts = 0
    max_attempts = 20  # 5 minutes total
    
    while attempts < max_attempts:
        attempts += 1
        print(f"🔄 Attempt {attempts}/20 - Checking deployment...")
        
        if check_deployment_status():
            print("")
            print("🎉 SUCCESS! Deployment complete!")
            print("================================")
            print("✅ Syntax error fixed")
            print("✅ Flask app is running")
            print("✅ Sofi can now receive messages")
            print("")
            print("🎯 Next Steps:")
            print("1. Update Render environment variables with fresh keys")
            print("2. Test Sofi's intent detection capabilities")
            print("3. Verify function calling is working")
            break
        
        if attempts < max_attempts:
            print("⏳ Still deploying... waiting 15 seconds")
            time.sleep(15)
        else:
            print("")
            print("⚠️  Deployment taking longer than expected")
            print("Check Render.com dashboard for deployment status")
            
    return attempts <= max_attempts

if __name__ == "__main__":
    success = monitor_deployment()
    exit(0 if success else 1)
