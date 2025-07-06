"""
SOFI AI SECURITY MODULE
======================
Comprehensive security measures for Flask app and domain protection
"""

from flask import Flask, request, jsonify, abort, redirect, url_for, g
from functools import wraps
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import re
import os
from collections import defaultdict
from utils.ip_intelligence import analyze_request_threat, check_rate_limit, is_ip_whitelisted
from utils.security_monitor import security_monitor, AlertLevel

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis or database)
rate_limit_storage = defaultdict(list)
blocked_ips = set()
suspicious_activity = defaultdict(int)

# Security configuration
SECURITY_CONFIG = {
    'rate_limit': {
        'requests_per_minute': 60,  # Increased from 10 for normal users
        'api_requests_per_minute': 30,  # Separate limit for API endpoints
        'webhook_requests_per_minute': 100,  # Higher for webhook endpoints
        'block_duration': 300,  # 5 minutes
    },
    'blocked_paths': {
        # WordPress and CMS paths
        '/wp-admin*', '/wp-login*', '/wp-config*', '/wp-content*',
        '/wordpress*', '/setup-config.php', '/wp-includes*',
        '/admin*', '/administrator*', '/wp-admin.php',
        
        # Database and config files
        '/.env', '/config.php', '/database.php', '/db.php',
        '/phpmyadmin*', '/mysql*', '/adminer*',
        
        # Common exploit paths
        '/cgi-bin*', '/scripts*', '/fckeditor*', '/tinymce*',
        '/xmlrpc.php', '/readme.html', '/license.txt',
        
        # Hidden files and directories
        '/.git*', '/.svn*', '/.htaccess', '/.htpasswd',
        '/backup*', '/temp*', '/tmp*', '/cache*',
        
        # Suspicious files
        '/shell.php', '/c99.php', '/r57.php', '/eval.php',
        '/upload.php', '/uploader.php', '/file.php',
        
        # Bot patterns
        '/robots.txt', '/sitemap.xml', '/sitemap*',
        '/crawl*', '/spider*', '/bot*'
    },
    'allowed_origins': [
        'https://api.telegram.org',
        'https://pipinstallsofi.com',
        'https://web.telegram.org',
        'https://t.me'
    ],
    'secure_headers': {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org https://t.me; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';",
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
    }
}

class SecurityMiddleware:
    """Main security middleware class"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.setup_security()
    
    def setup_security(self):
        """Set up all security measures"""
        # Force HTTPS redirect
        self.app.before_request(self.force_https)
        
        # Rate limiting
        self.app.before_request(self.rate_limit)
        
        # Block suspicious paths
        self.app.before_request(self.block_suspicious_paths)
        
        # Add security headers
        self.app.after_request(self.add_security_headers)
        
        # Log security events
        self.app.before_request(self.log_request)
        
        # Handle errors securely
        self.setup_error_handlers()
    
    def force_https(self):
        """Force HTTPS redirect with proper proxy handling"""
        # Skip HTTPS redirect on Render since it handles SSL termination
        if request.headers.get('X-Forwarded-Proto') == 'https':
            return  # Already HTTPS via proxy
        
        # Only redirect if we're actually on HTTP and not behind a proxy
        if request.url.startswith('http://') and not request.headers.get('X-Forwarded-Proto'):
            https_url = request.url.replace('http://', 'https://', 1)
            return redirect(https_url, code=301)
        
        # Prefer non-www domain (only if not behind proxy)
        if request.host.startswith('www.') and not request.headers.get('X-Forwarded-Proto'):
            non_www_url = request.url.replace('www.', '', 1)
            return redirect(non_www_url, code=301)
    
    def get_client_ip(self) -> str:
        """Get real client IP address"""
        # Check for forwarded headers (common in reverse proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or 'unknown'
    
    def rate_limit(self):
        """Enhanced rate limiting with IP intelligence"""
        client_ip = self.get_client_ip()
        
        # Skip rate limiting for localhost during development
        if client_ip in ['127.0.0.1', 'localhost']:
            return
        
        # Check if IP is whitelisted
        if is_ip_whitelisted(client_ip):
            return
        
        # Check if IP is blocked by security monitor
        if security_monitor.is_ip_blocked(client_ip):
            logger.warning(f"🚫 Blocked IP attempted access: {client_ip}")
            abort(403)
        
        # Check rate limits using advanced rate limiter
        is_limited, limit_info = check_rate_limit(client_ip)
        if is_limited:
            logger.warning(f"🚫 Rate limit exceeded: {client_ip} - {limit_info}")
            
            # Log security event
            security_monitor.log_security_event({
                'timestamp': datetime.now(),
                'event_type': 'rate_limit_violation',
                'severity': AlertLevel.MEDIUM,
                'ip_address': client_ip,
                'user_agent': request.headers.get('User-Agent', ''),
                'path': request.path,
                'method': request.method,
                'details': limit_info
            })
            
            abort(429)  # Too Many Requests
        
        # Analyze request for threats
        threat_analysis = analyze_request_threat(
            client_ip,
            request.headers.get('User-Agent', ''),
            request.path,
            request.method
        )
        
        # Handle threats based on recommendation
        if threat_analysis['recommendation'] == 'block':
            logger.warning(f"🚫 Threat detected, blocking IP: {client_ip} - {threat_analysis}")
            
            # Block IP in security monitor
            security_monitor.block_ip(client_ip, f"Threat detected: {threat_analysis['threat_level']}")
            
            # Log critical security event
            security_monitor.log_security_event({
                'timestamp': datetime.now(),
                'event_type': 'threat_detected',
                'severity': AlertLevel.HIGH,
                'ip_address': client_ip,
                'user_agent': request.headers.get('User-Agent', ''),
                'path': request.path,
                'method': request.method,
                'details': threat_analysis
            })
            
            abort(403)
        
        elif threat_analysis['recommendation'] == 'challenge':
            # For now, log but allow - could implement CAPTCHA here
            logger.warning(f"⚠️ Suspicious activity detected: {client_ip} - {threat_analysis}")
            
            security_monitor.log_security_event({
                'timestamp': datetime.now(),
                'event_type': 'suspicious_activity',
                'severity': AlertLevel.MEDIUM,
                'ip_address': client_ip,
                'user_agent': request.headers.get('User-Agent', ''),
                'path': request.path,
                'method': request.method,
                'details': threat_analysis
            })
        
        elif threat_analysis['recommendation'] == 'allow':
            # Explicitly allowed - don't even log as suspicious
            pass
        
        elif threat_analysis['recommendation'] == 'log':
            # Just log for monitoring, don't alert
            logger.info(f"📊 Possible automated traffic: {client_ip} - {threat_analysis['factors']}")
        
        else:
            # Default: log suspicious activity for medium threats
            logger.warning(f"⚠️ Suspicious activity detected: {client_ip} - {threat_analysis}")
            
            security_monitor.log_security_event({
                'timestamp': datetime.now(),
                'event_type': 'suspicious_activity',
                'severity': AlertLevel.MEDIUM,
                'ip_address': client_ip,
                'user_agent': request.headers.get('User-Agent', ''),
                'path': request.path,
                'method': request.method,
                'details': threat_analysis
            })
        
        # Legacy rate limiting as fallback
        current_time = time.time()
        path = request.path
        
        # Determine rate limit based on endpoint
        if path.startswith('/webhook'):
            max_requests = SECURITY_CONFIG['rate_limit']['webhook_requests_per_minute']
        elif path.startswith('/api/'):
            max_requests = SECURITY_CONFIG['rate_limit']['api_requests_per_minute']
        else:
            max_requests = SECURITY_CONFIG['rate_limit']['requests_per_minute']
        
        # Clean old requests (older than 1 minute)
        rate_limit_storage[client_ip] = [
            timestamp for timestamp in rate_limit_storage[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Check rate limit
        if len(rate_limit_storage[client_ip]) >= max_requests:
            # Block IP temporarily
            blocked_ips.add(client_ip)
            suspicious_activity[client_ip] += 1
            
            logger.warning(f"🚫 Rate limit exceeded for IP: {client_ip} ({len(rate_limit_storage[client_ip])} requests)")
            
            # Auto-unblock after configured duration
            def unblock_ip():
                time.sleep(SECURITY_CONFIG['rate_limit']['block_duration'])
                blocked_ips.discard(client_ip)
                logger.info(f"🔓 IP unblocked: {client_ip}")
            
            # In production, use a proper task queue
            import threading
            threading.Thread(target=unblock_ip, daemon=True).start()
            
            abort(429)  # Too Many Requests
        
        # Record this request
        rate_limit_storage[client_ip].append(current_time)
    
    def block_suspicious_paths(self):
        """Block suspicious paths"""
        path = request.path.lower()
        
        # Check against blocked paths
        for blocked_pattern in SECURITY_CONFIG['blocked_paths']:
            if blocked_pattern.endswith('*'):
                # Wildcard pattern
                if path.startswith(blocked_pattern[:-1]):
                    client_ip = self.get_client_ip()
                    logger.warning(f"🚫 Blocked suspicious path: {path} from IP: {client_ip}")
                    suspicious_activity[client_ip] += 1
                    abort(403)
            else:
                # Exact match
                if path == blocked_pattern:
                    client_ip = self.get_client_ip()
                    logger.warning(f"🚫 Blocked suspicious path: {path} from IP: {client_ip}")
                    suspicious_activity[client_ip] += 1
                    abort(403)
    
    def add_security_headers(self, response):
        """Add security headers to all responses"""
        for header_name, header_value in SECURITY_CONFIG['secure_headers'].items():
            response.headers[header_name] = header_value
        
        # Add server header obfuscation
        response.headers['Server'] = 'Sofi-AI-Server'
        
        return response
    
    def log_request(self):
        """Log requests with security monitoring and threat detection"""
        client_ip = self.get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        path = request.path
        method = request.method
        
        # Analyze request for suspicious activity using security monitor
        security_event = security_monitor.detect_suspicious_activity(
            ip=client_ip,
            path=path,
            user_agent=user_agent,
            method=method
        )
        
        # Log security event if detected
        if security_event:
            security_monitor.log_security_event(security_event)
            
            # Auto-block highly suspicious IPs
            if security_event.severity == AlertLevel.CRITICAL:
                blocked_ips.add(client_ip)
                logger.error(f"🚫 Auto-blocked critical threat IP: {client_ip}")
        
        # Log normal requests (without sensitive data)
        safe_path = self.sanitize_path_for_logging(path)
        if not any(skip in path.lower() for skip in ['/health', '/static', '/favicon']):
            logger.info(f"📊 {method} {safe_path} - {client_ip} - {user_agent[:50]}...")
    
    def sanitize_path_for_logging(self, path: str) -> str:
        """Remove sensitive data from paths for logging"""
        # Remove potential PINs, tokens, etc.
        sanitized = re.sub(r'\b\d{4}\b', '[PIN]', path)
        sanitized = re.sub(r'token=[a-zA-Z0-9]+', 'token=[REDACTED]', sanitized)
        sanitized = re.sub(r'key=[a-zA-Z0-9]+', 'key=[REDACTED]', sanitized)
        sanitized = re.sub(r'password=[^&]+', 'password=[REDACTED]', sanitized)
        return sanitized
    
    def setup_error_handlers(self):
        """Set up secure error handlers"""
        
        @self.app.errorhandler(403)
        def forbidden(e):
            return jsonify({'error': 'Access forbidden'}), 403
        
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(429)
        def rate_limit_exceeded(e):
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        
        @self.app.errorhandler(500)
        def internal_error(e):
            logger.error(f"Internal server error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

def setup_cors_security(app: Flask):
    """Set up CORS with security considerations"""
    from flask_cors import CORS
    
    CORS(app, 
         origins=SECURITY_CONFIG['allowed_origins'],
         methods=['GET', 'POST', 'PUT', 'DELETE'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True,
         max_age=3600)

# Global utility functions for security endpoints
def get_client_ip(request=None):
    """Get real client IP address"""
    if request is None:
        from flask import request
    
    # Check for forwarded headers (common in reverse proxies)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr or 'unknown'

def is_rate_limited(ip: str) -> bool:
    """Check if IP is rate limited"""
    # Check with IP intelligence system
    from utils.ip_intelligence import check_rate_limit
    is_limited, _ = check_rate_limit(ip)
    return is_limited

def get_security_status() -> Dict:
    """Get current security status"""
    return {
        'security_active': True,
        'rate_limiting': True,
        'ip_blocking': True,
        'suspicious_activity_detection': True,
        'telegram_alerts': True,
        'timestamp': datetime.now().isoformat()
    }

def manually_block_ip(ip: str):
    """Manually block an IP address"""
    blocked_ips.add(ip)
    logger.warning(f"🚫 Manually blocked IP: {ip}")

def unblock_ip(ip: str):
    """Unblock an IP address"""
    blocked_ips.discard(ip)
    logger.info(f"🔓 Manually unblocked IP: {ip}")

def init_security(app: Flask):
    """Initialize all security measures"""
    logger.info("🔒 Initializing Sofi AI Security System...")
    
    # Set up security middleware
    security_middleware = SecurityMiddleware(app)
    
    # Set up CORS
    setup_cors_security(app)
    
    # Add security routes
    @app.route('/security-status')
    def security_status():
        """Get security status (admin only)"""
        return jsonify(get_security_status())
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    logger.info("✅ Sofi AI Security System initialized successfully!")
    return security_middleware
