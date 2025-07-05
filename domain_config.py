"""
Sofi AI Domain Configuration
All URLs and endpoints for the new domain: pipinstallsofi.com
"""

# Primary domain configuration
DOMAIN = "https://pipinstallsofi.com"

# API Endpoints
API_ENDPOINTS = {
    # Main routes
    "home": f"{DOMAIN}/",
    "health": f"{DOMAIN}/health",
    
    # Telegram webhook
    "telegram_webhook": f"{DOMAIN}/webhook",
    
    # Paystack webhooks
    "paystack_webhook": f"{DOMAIN}/api/paystack/webhook",
    "paystack_webhook_legacy": f"{DOMAIN}/paystack-webhook",
    
    # User onboarding
    "onboarding": f"{DOMAIN}/onboard",
    "onboard": f"{DOMAIN}/onboard",
    "verify_pin": f"{DOMAIN}/verify-pin",
    
    # API endpoints
    "create_virtual_account": f"{DOMAIN}/api/create_virtual_account",
    "verify_pin_api": f"{DOMAIN}/api/verify-pin",
    "cancel_transfer": f"{DOMAIN}/api/cancel-transfer",
    "onboard_api": f"{DOMAIN}/api/onboard",
    "notify_onboarding": f"{DOMAIN}/api/notify-onboarding",
}

# Webhook URLs for external services
WEBHOOK_URLS = {
    "telegram": API_ENDPOINTS["telegram_webhook"],
    "paystack": API_ENDPOINTS["paystack_webhook"],
    "monnify": f"{DOMAIN}/monnify_webhook",  # If you have Monnify integration
    "crypto": f"{DOMAIN}/crypto_webhook",    # If you have crypto integration
}

# Frontend URLs (for user-facing links)
FRONTEND_URLS = {
    "landing_page": DOMAIN,
    "create_account": API_ENDPOINTS["onboarding"],
    "verify_pin": API_ENDPOINTS["verify_pin"],
    "telegram_bot": "https://t.me/getsofi_bot",
}

# Configuration for different environments
ENVIRONMENTS = {
    "production": {
        "domain": "https://pipinstallsofi.com",
        "telegram_webhook": "https://pipinstallsofi.com/webhook",
        "paystack_webhook": "https://pipinstallsofi.com/api/paystack/webhook",
    },
    "development": {
        "domain": "http://localhost:5000",
        "telegram_webhook": "http://localhost:5000/webhook",
        "paystack_webhook": "http://localhost:5000/api/paystack/webhook",
    }
}

def get_base_url():
    """Get the base URL for the current environment"""
    import os
    env = os.getenv("ENVIRONMENT", "production")
    return ENVIRONMENTS.get(env, ENVIRONMENTS["production"])["domain"]

def get_webhook_url(service="telegram"):
    """Get webhook URL for a specific service"""
    import os
    env = os.getenv("ENVIRONMENT", "production")
    config = ENVIRONMENTS.get(env, ENVIRONMENTS["production"])
    
    webhook_mappings = {
        "telegram": config["telegram_webhook"],
        "paystack": config["paystack_webhook"],
    }
    
    return webhook_mappings.get(service, config["telegram_webhook"])

# Export commonly used URLs
BASE_URL = DOMAIN
ONBOARDING_URL = API_ENDPOINTS["onboarding"]
TELEGRAM_WEBHOOK_URL = API_ENDPOINTS["telegram_webhook"]
PAYSTACK_WEBHOOK_URL = API_ENDPOINTS["paystack_webhook"]

if __name__ == "__main__":
    print("🌐 Sofi AI Domain Configuration")
    print("=" * 50)
    print(f"Primary Domain: {DOMAIN}")
    print(f"Telegram Bot: {FRONTEND_URLS['telegram_bot']}")
    print(f"Landing Page: {FRONTEND_URLS['landing_page']}")
    print(f"Onboarding: {FRONTEND_URLS['create_account']}")
    print("")
    print("📡 Webhook URLs:")
    for service, url in WEBHOOK_URLS.items():
        print(f"  {service.capitalize()}: {url}")
    print("")
    print("🔗 API Endpoints:")
    for name, url in API_ENDPOINTS.items():
        print(f"  {name}: {url}")
    print("=" * 50)
