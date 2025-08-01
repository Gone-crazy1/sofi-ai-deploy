#!/usr/bin/env python3
"""
WhatsApp Access Token Management
Helps generate and manage WhatsApp Cloud API access tokens
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_whatsapp_app_credentials():
    """Get WhatsApp app credentials for token generation"""
    
    print("🔑 WhatsApp Cloud API Token Generation")
    print("=" * 50)
    print("To get a permanent access token, you need:")
    print("1. Your Facebook App ID")
    print("2. Your Facebook App Secret")
    print("3. Your WhatsApp Business Account ID")
    print()
    
    # Check if we have app credentials in environment
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    
    if not app_id:
        app_id = input("📱 Enter your Facebook App ID: ").strip()
    
    if not app_secret:
        app_secret = input("🔐 Enter your Facebook App Secret: ").strip()
    
    if not business_account_id:
        business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "683628188046191")
    
    return app_id, app_secret, business_account_id

def generate_system_user_token(app_id: str, app_secret: str, business_account_id: str):
    """Generate a system user access token (permanent)"""
    
    try:
        # Step 1: Get app access token
        print("🔄 Getting app access token...")
        
        app_token_url = "https://graph.facebook.com/oauth/access_token"
        app_token_params = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "client_credentials"
        }
        
        response = requests.get(app_token_url, params=app_token_params)
        
        if response.status_code != 200:
            print(f"❌ Failed to get app token: {response.text}")
            return None
        
        app_token = response.json()["access_token"]
        print("✅ App access token obtained")
        
        # Step 2: Create system user
        print("🔄 Creating system user...")
        
        system_user_url = f"https://graph.facebook.com/v22.0/{business_account_id}/system_users"
        system_user_data = {
            "name": "Sofi AI System User",
            "system_user_role": "ADMIN",
            "access_token": app_token
        }
        
        response = requests.post(system_user_url, data=system_user_data)
        
        if response.status_code != 200:
            print(f"❌ Failed to create system user: {response.text}")
            # Try to get existing system users
            get_users_url = f"https://graph.facebook.com/v22.0/{business_account_id}/system_users"
            response = requests.get(get_users_url, params={"access_token": app_token})
            if response.status_code == 200:
                users = response.json().get("data", [])
                if users:
                    system_user_id = users[0]["id"]
                    print(f"✅ Using existing system user: {system_user_id}")
                else:
                    return None
            else:
                return None
        else:
            system_user_id = response.json()["id"]
            print(f"✅ System user created: {system_user_id}")
        
        # Step 3: Generate system user access token
        print("🔄 Generating system user access token...")
        
        token_url = f"https://graph.facebook.com/v22.0/{system_user_id}/access_tokens"
        token_data = {
            "app_id": app_id,
            "access_token": app_token
        }
        
        response = requests.post(token_url, data=token_data)
        
        if response.status_code != 200:
            print(f"❌ Failed to generate system user token: {response.text}")
            return None
        
        system_token = response.json()["access_token"]
        print("✅ System user access token generated!")
        
        return system_token
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        return None

def test_new_token(token: str):
    """Test the new access token"""
    
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "791159074061207")
    
    try:
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ New token is working!")
            print(f"📞 Phone: {data.get('display_phone_number', 'N/A')}")
            print(f"🏷️ Name: {data.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Token test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Token test error: {e}")
        return False

def update_env_file(new_token: str):
    """Update the .env file with the new token"""
    
    try:
        env_path = "c:\\Users\\Mrhaw\\sofi-ai-deploy\\.env"
        
        # Read current .env content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace the old token
        old_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        if old_token:
            content = content.replace(old_token, new_token)
        else:
            # Add new token if not exists
            content += f"\\nWHATSAPP_ACCESS_TOKEN={new_token}\\n"
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ .env file updated with new token!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def main():
    """Main token management function"""
    
    print("🚀 WhatsApp Access Token Management")
    print("=" * 50)
    print()
    print("Your current access token has expired.")
    print("Let's generate a permanent system user token.")
    print()
    
    # Get credentials
    app_id, app_secret, business_account_id = get_whatsapp_app_credentials()
    
    if not all([app_id, app_secret, business_account_id]):
        print("❌ Missing required credentials.")
        print()
        print("🔗 To get these credentials:")
        print("1. Go to https://developers.facebook.com/apps")
        print("2. Select your WhatsApp Business app")
        print("3. Go to App Settings > Basic")
        print("4. Copy App ID and App Secret")
        print("5. Your Business Account ID is: 683628188046191")
        return
    
    # Generate new token
    new_token = generate_system_user_token(app_id, app_secret, business_account_id)
    
    if not new_token:
        print("❌ Failed to generate new token.")
        print()
        print("🔗 Alternative method:")
        print("1. Go to https://developers.facebook.com/apps")
        print("2. Select your WhatsApp app")
        print("3. Go to WhatsApp > API Setup")
        print("4. Generate a new temporary token")
        print("5. For permanent token, create a System User in Business Manager")
        return
    
    print(f"🎉 New permanent access token generated!")
    print(f"🔑 Token: {new_token[:50]}...")
    print()
    
    # Test the token
    if test_new_token(new_token):
        # Update .env file
        if update_env_file(new_token):
            print()
            print("🎉 Success! Your WhatsApp integration is now ready!")
            print("✅ New permanent token is working")
            print("✅ .env file updated")
            print("🚀 You can now run the main application")
        else:
            print(f"⚠️ Please manually update your .env file:")
            print(f"WHATSAPP_ACCESS_TOKEN={new_token}")
    else:
        print("❌ New token is not working. Please check your setup.")

if __name__ == "__main__":
    main()
