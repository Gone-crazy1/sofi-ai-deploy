"""
SOFI AI SECURITY CONFIGURATION
==============================
Advanced security configurations and monitoring
"""

import os
from typing import Dict, List, Set

# Environment-specific security settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DOMAIN = os.getenv('DOMAIN', 'pipinstallsofi.com')

# Enhanced security configuration
ENHANCED_SECURITY_CONFIG = {
    'domain': {
        'primary_domain': f'https://{DOMAIN}',
        'allowed_domains': [f'https://{DOMAIN}', f'https://www.{DOMAIN}'],
        'force_https': True,
        'force_non_www': True,
        'hsts_max_age': 31536000,  # 1 year
    },
    
    'rate_limiting': {
        'global': {
            'requests_per_minute': 100,
            'burst_limit': 20,
        },
        'api_endpoints': {
            'requests_per_minute': 30,
            'burst_limit': 10,
        },
        'webhook_endpoints': {
            'requests_per_minute': 200,
            'burst_limit': 50,
        },
        'auth_endpoints': {
            'requests_per_minute': 5,
            'burst_limit': 3,
        },
        'block_duration': 300,  # 5 minutes
        'progressive_blocking': True,
    },
    
    'threat_detection': {
        'suspicious_user_agents': [
            'sqlmap', 'nikto', 'w3af', 'dirbuster', 'gobuster',
            'masscan', 'nmap', 'zap', 'burp', 'acunetix',
            'netsparker', 'appscan', 'skipfish', 'wapiti',
            'havij', 'pangolin', 'jsql', 'blind-sql-injection'
        ],
        'blocked_countries': [],  # Add country codes if needed
        'honeypot_paths': [
            '/admin', '/login', '/wp-admin', '/phpmyadmin',
            '/backup', '/config', '/test', '/dev'
        ],
        'max_suspicious_score': 10,
        'auto_block_threshold': 5,
    },
    
    'content_security': {
        'max_request_size': 10 * 1024 * 1024,  # 10MB
        'allowed_file_types': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'],
        'blocked_file_types': ['.php', '.exe', '.bat', '.sh', '.py', '.js'],
        'scan_uploads': True,
        'quarantine_suspicious': True,
    },
    
    'monitoring': {
        'log_level': 'INFO',
        'log_retention_days': 30,
        'alert_thresholds': {
            'failed_requests_per_minute': 20,
            'blocked_ips_per_hour': 10,
            'suspicious_activities_per_hour': 50,
        },
        'webhook_notifications': {
            'enabled': False,
            'url': '',  # Add webhook URL for alerts
        },
        'email_notifications': {
            'enabled': False,
            'recipients': [],
        }
    },
    
    'advanced_protection': {
        'ddos_protection': {
            'enabled': True,
            'threshold_requests_per_second': 10,
            'mitigation_duration': 600,  # 10 minutes
        },
        'bot_protection': {
            'enabled': True,
            'challenge_suspicious_requests': True,
            'whitelist_known_bots': ['TelegramBot', 'GoogleBot'],
        },
        'geo_blocking': {
            'enabled': False,
            'blocked_countries': [],
            'allowed_countries': [],
        },
        'ip_reputation': {
            'enabled': True,
            'check_malicious_ips': True,
            'reputation_sources': ['AbuseIPDB', 'VirusTotal'],
        }
    }
}

# Telegram-specific security
TELEGRAM_SECURITY = {
    'webhook_security': {
        'verify_webhook_signature': True,
        'allowed_telegram_ips': [
            '149.154.160.0/20',
            '91.108.4.0/22',
            '91.108.56.0/22',
            '91.108.8.0/22',
            '95.161.64.0/20',
            '149.154.164.0/22',
            '149.154.168.0/22',
            '149.154.172.0/22',
        ],
        'max_webhook_retries': 3,
        'webhook_timeout': 30,
    },
    'bot_protection': {
        'rate_limit_per_user': 10,
        'ban_duration': 3600,  # 1 hour
        'max_message_length': 4096,
        'block_forwarded_messages': False,
        'whitelist_admins': True,
    }
}

# Security headers configuration
SECURITY_HEADERS = {
    'strict': {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://telegram.org https://t.me; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=(), bluetooth=(), midi=(), sync-xhr=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Permitted-Cross-Domain-Policies': 'none',
        'Cross-Origin-Embedder-Policy': 'require-corp',
        'Cross-Origin-Opener-Policy': 'same-origin',
        'Cross-Origin-Resource-Policy': 'same-origin',
    },
    'moderate': {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
}

# Blocked paths and patterns
BLOCKED_PATHS = {
    'wordpress': [
        '/wp-admin*', '/wp-login*', '/wp-config*', '/wp-content*',
        '/wp-includes*', '/wp-json*', '/xmlrpc.php', '/wp-admin.php',
        '/wp-login.php', '/wp-config.php', '/wp-settings.php',
        '/wp-config-sample.php', '/wp-load.php', '/wp-blog-header.php',
        '/wordpress*', '/blog*', '/cms*'
    ],
    'admin_panels': [
        '/admin*', '/administrator*', '/manage*', '/control*',
        '/dashboard*', '/cpanel*', '/plesk*', '/directadmin*',
        '/webmin*', '/phpmyadmin*', '/adminer*', '/mysql*',
        '/panel*', '/backend*', '/management*'
    ],
    'config_files': [
        '/.env*', '/config*', '/settings*', '/database*',
        '/db.php', '/config.php', '/settings.php', '/local.php',
        '/production.php', '/development.php', '/.htaccess',
        '/.htpasswd', '/web.config', '/app.config'
    ],
    'development': [
        '/.git*', '/.svn*', '/.hg*', '/.bzr*', '/CVS*',
        '/node_modules*', '/vendor*', '/.vscode*', '/.idea*',
        '/debug*', '/test*', '/tests*', '/tmp*', '/temp*',
        '/cache*', '/logs*', '/log*', '/backup*', '/backups*'
    ],
    'exploits': [
        '/shell*', '/c99*', '/r57*', '/eval*', '/backdoor*',
        '/upload*', '/uploader*', '/file*', '/files*',
        '/cgi-bin*', '/scripts*', '/bin*', '/usr*', '/etc*',
        '/proc*', '/sys*', '/dev*', '/boot*', '/home*',
        '/root*', '/var*', '/tmp*', '/opt*'
    ],
    'suspicious': [
        '/robots.txt', '/sitemap*', '/crawl*', '/spider*',
        '/bot*', '/scan*', '/probe*', '/check*', '/ping*',
        '/health*', '/status*', '/info*', '/version*',
        '/readme*', '/license*', '/changelog*', '/install*'
    ]
}

# Whitelist for legitimate paths
WHITELISTED_PATHS = [
    '/', '/onboard', '/webhook', '/api/*', '/verify-pin',
    '/health', '/security-status', '/static/*', '/favicon.ico'
]

def get_security_config(level: str = 'strict') -> Dict:
    """Get security configuration for specified level"""
    if level == 'strict':
        return ENHANCED_SECURITY_CONFIG
    elif level == 'moderate':
        return {
            'rate_limiting': {
                'global': {'requests_per_minute': 200},
                'api_endpoints': {'requests_per_minute': 60},
            },
            'threat_detection': {
                'max_suspicious_score': 20,
                'auto_block_threshold': 10,
            }
        }
    else:
        return ENHANCED_SECURITY_CONFIG

def get_blocked_paths() -> List[str]:
    """Get all blocked paths"""
    all_paths = []
    for category, paths in BLOCKED_PATHS.items():
        all_paths.extend(paths)
    return all_paths

def is_path_whitelisted(path: str) -> bool:
    """Check if path is whitelisted"""
    for whitelist_pattern in WHITELISTED_PATHS:
        if whitelist_pattern.endswith('*'):
            if path.startswith(whitelist_pattern[:-1]):
                return True
        else:
            if path == whitelist_pattern:
                return True
    return False
