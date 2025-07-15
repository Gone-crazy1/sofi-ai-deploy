# SOFI AI PERFORMANCE CONFIGURATION
# Fast mode settings to optimize response times

import os

# 🚀 PERFORMANCE MODE - Set to True for ultra-fast responses
ENABLE_FAST_MODE = True

# 🔒 SECURITY ALERT CONTROLS
ENABLE_SECURITY_ALERTS = False  # Disable Telegram alerts for speed
ENABLE_SECURITY_LOGGING = True  # Keep logging for review later
ENABLE_CRITICAL_ALERTS_ONLY = True  # Only send critical alerts

# ⚡ FAST MODE SETTINGS
if ENABLE_FAST_MODE:
    # Disable non-critical security notifications
    ENABLE_SECURITY_ALERTS = False
    
    # Reduce alert cooldowns (faster processing)
    ALERT_COOLDOWN_SECONDS = 0  # No cooldown in fast mode
    
    # Skip detailed logging for minor events
    ENABLE_DETAILED_LOGGING = False
    
    # Disable real-time monitoring thread (CPU saver)
    ENABLE_MONITORING_THREAD = False
else:
    # Normal mode - full security
    ENABLE_SECURITY_ALERTS = True
    ALERT_COOLDOWN_SECONDS = 60
    ENABLE_DETAILED_LOGGING = True
    ENABLE_MONITORING_THREAD = True

# Environment override
if os.getenv('SOFI_FAST_MODE') == 'true':
    ENABLE_FAST_MODE = True
    ENABLE_SECURITY_ALERTS = False
    
# Allow critical alerts even in fast mode
ALWAYS_ALLOW_CRITICAL = True

print(f"🚀 Sofi Performance Mode: {'FAST' if ENABLE_FAST_MODE else 'NORMAL'}")
print(f"🔒 Security Alerts: {'DISABLED' if not ENABLE_SECURITY_ALERTS else 'ENABLED'}")
