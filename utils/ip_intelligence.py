"""
SOFI AI IP INTELLIGENCE & RATE LIMITING
=======================================
Advanced IP filtering, rate limiting, and bot detection middleware
"""

import logging
import time
import json
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import re
from utils.security_monitor import security_monitor, AlertLevel

logger = logging.getLogger(__name__)

class IPIntelligence:
    """IP intelligence and threat detection"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = 3600  # 1 hour
        self.abuseipdb_api_key = os.getenv('ABUSEIPDB_API_KEY')
        self.ipinfo_token = os.getenv('IPINFO_TOKEN')
        
        # Known malicious IP patterns
        self.malicious_patterns = [
            r'^10\.0\.0\.1$',  # Example: specific bad IPs
            r'^192\.168\.1\.1$',  # Example: local network scanners
        ]
        
        # Known good IP patterns (whitelisted ranges)
        self.whitelist_patterns = [
            r'^127\.0\.0\.1$',  # localhost
            r'^::1$',  # IPv6 localhost
        ]
        
        # ISP/hosting provider patterns (higher suspicion)
        self.hosting_patterns = [
            r'amazonaws\.com',
            r'googlecloud\.com',
            r'digitalocean\.com',
            r'vultr\.com',
            r'linode\.com',
            r'hetzner\.com',
        ]
        
        # Bot user agent patterns
        self.bot_patterns = [
            r'googlebot',
            r'bingbot',
            r'slurp',
            r'facebookexternalhit',
            r'twitterbot',
            r'linkedinbot',
            r'whatsapp',
            r'telegrambot',
            # Malicious bots
            r'python-requests',
            r'curl',
            r'wget',
            r'scanner',
            r'exploit',
            r'hack',
            r'attack',
            r'penetration',
            r'nikto',
            r'sqlmap',
            r'nmap',
            r'dirb',
            r'gobuster',
            r'masscan',
            r'zmap',
        ]
        
        # Good bots (allowed)
        self.good_bots = [
            r'googlebot',
            r'bingbot',
            r'slurp',
            r'facebookexternalhit',
            r'twitterbot',
            r'linkedinbot',
            r'whatsapp',
            r'telegrambot',
        ]
    
    def is_whitelisted_ip(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        for pattern in self.whitelist_patterns:
            if re.match(pattern, ip, re.IGNORECASE):
                return True
        return False
    
    def is_malicious_pattern(self, ip: str) -> bool:
        """Check if IP matches known malicious patterns"""
        for pattern in self.malicious_patterns:
            if re.match(pattern, ip, re.IGNORECASE):
                return True
        return False
    
    def is_hosting_provider(self, hostname: str) -> bool:
        """Check if hostname suggests hosting provider"""
        if not hostname:
            return False
        
        for pattern in self.hosting_patterns:
            if re.search(pattern, hostname, re.IGNORECASE):
                return True
        return False
    
    def analyze_user_agent(self, user_agent: str) -> Dict:
        """Analyze user agent for bot detection"""
        result = {
            'is_bot': False,
            'is_good_bot': False,
            'is_malicious_bot': False,
            'confidence': 0.0,
            'details': {}
        }
        
        if not user_agent:
            result['is_bot'] = True
            result['confidence'] = 0.8
            result['details']['reason'] = 'Empty user agent'
            return result
        
        user_agent_lower = user_agent.lower()
        
        # Check for good bots first
        for pattern in self.good_bots:
            if re.search(pattern, user_agent_lower):
                result['is_bot'] = True
                result['is_good_bot'] = True
                result['confidence'] = 0.9
                result['details']['bot_type'] = pattern
                return result
        
        # Check for malicious bots
        for pattern in self.bot_patterns:
            if re.search(pattern, user_agent_lower):
                result['is_bot'] = True
                result['confidence'] = 0.9
                
                # Determine if malicious
                if pattern in ['python-requests', 'curl', 'wget', 'scanner', 'exploit', 'hack', 'attack', 'penetration', 'nikto', 'sqlmap', 'nmap', 'dirb', 'gobuster', 'masscan', 'zmap']:
                    result['is_malicious_bot'] = True
                    result['confidence'] = 0.95
                
                result['details']['bot_type'] = pattern
                return result
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'java',
            r'python',
            r'php',
            r'ruby',
            r'node',
            r'go-http',
            r'libwww',
            r'httpclient',
            r'okhttp',
            r'urllib',
            r'requests',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                result['is_bot'] = True
                result['confidence'] = 0.7
                result['details']['reason'] = f'Suspicious pattern: {pattern}'
                return result
        
        return result
    
    def get_ip_info(self, ip: str) -> Dict:
        """Get IP information with caching"""
        cache_key = f"ip_info_{ip}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_expiry:
                return cached_data
        
        # Get IP info
        ip_info = self._fetch_ip_info(ip)
        
        # Cache result
        self.cache[cache_key] = (ip_info, time.time())
        
        return ip_info
    
    def _fetch_ip_info(self, ip: str) -> Dict:
        """Fetch IP information from various sources"""
        info = {
            'ip': ip,
            'country': None,
            'region': None,
            'city': None,
            'isp': None,
            'hostname': None,
            'is_hosting': False,
            'is_vpn': False,
            'is_proxy': False,
            'is_tor': False,
            'abuse_confidence': 0,
            'reputation': 'unknown',
            'sources': []
        }
        
        # Try IPInfo.io
        if self.ipinfo_token:
            try:
                response = requests.get(
                    f"https://ipinfo.io/{ip}/json",
                    headers={'Authorization': f'Bearer {self.ipinfo_token}'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    info.update({
                        'country': data.get('country'),
                        'region': data.get('region'),
                        'city': data.get('city'),
                        'isp': data.get('org'),
                        'hostname': data.get('hostname'),
                        'is_hosting': self.is_hosting_provider(data.get('hostname', ''))
                    })
                    info['sources'].append('ipinfo.io')
                    
            except Exception as e:
                logger.warning(f"IPInfo.io lookup failed for {ip}: {e}")
        
        # Try AbuseIPDB
        if self.abuseipdb_api_key:
            try:
                response = requests.get(
                    'https://api.abuseipdb.com/api/v2/check',
                    headers={
                        'Key': self.abuseipdb_api_key,
                        'Accept': 'application/json'
                    },
                    params={'ipAddress': ip, 'maxAgeInDays': 90},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        abuse_data = data['data']
                        info.update({
                            'abuse_confidence': abuse_data.get('abuseConfidencePercentage', 0),
                            'is_tor': abuse_data.get('isTor', False),
                            'country': abuse_data.get('countryCode') or info['country'],
                            'isp': abuse_data.get('isp') or info['isp']
                        })
                        
                        # Set reputation based on abuse confidence
                        if info['abuse_confidence'] > 75:
                            info['reputation'] = 'malicious'
                        elif info['abuse_confidence'] > 25:
                            info['reputation'] = 'suspicious'
                        else:
                            info['reputation'] = 'clean'
                            
                        info['sources'].append('abuseipdb.com')
                        
            except Exception as e:
                logger.warning(f"AbuseIPDB lookup failed for {ip}: {e}")
        
        return info
    
    def assess_threat_level(self, ip: str, user_agent: str, path: str, method: str) -> Dict:
        """Comprehensive threat assessment"""
        assessment = {
            'threat_level': 'low',
            'confidence': 0.0,
            'factors': [],
            'recommendation': 'allow',
            'details': {}
        }
        
        # Check if whitelisted
        if self.is_whitelisted_ip(ip):
            assessment['threat_level'] = 'safe'
            assessment['recommendation'] = 'allow'
            assessment['factors'].append('whitelisted_ip')
            return assessment
        
        # Check malicious patterns
        if self.is_malicious_pattern(ip):
            assessment['threat_level'] = 'high'
            assessment['confidence'] = 0.95
            assessment['recommendation'] = 'block'
            assessment['factors'].append('malicious_ip_pattern')
            return assessment
        
        # Analyze user agent
        ua_analysis = self.analyze_user_agent(user_agent)
        assessment['details']['user_agent_analysis'] = ua_analysis
        
        if ua_analysis['is_malicious_bot']:
            assessment['threat_level'] = 'high'
            assessment['confidence'] = max(assessment['confidence'], 0.9)
            assessment['recommendation'] = 'block'
            assessment['factors'].append('malicious_bot')
        elif ua_analysis['is_good_bot']:
            assessment['factors'].append('good_bot')
        elif ua_analysis['is_bot']:
            assessment['threat_level'] = 'medium'
            assessment['confidence'] = max(assessment['confidence'], 0.7)
            assessment['factors'].append('suspicious_bot')
        
        # Get IP information
        ip_info = self.get_ip_info(ip)
        assessment['details']['ip_info'] = ip_info
        
        # Assess based on IP reputation
        if ip_info['reputation'] == 'malicious':
            assessment['threat_level'] = 'high'
            assessment['confidence'] = max(assessment['confidence'], 0.9)
            assessment['recommendation'] = 'block'
            assessment['factors'].append('malicious_ip_reputation')
        elif ip_info['reputation'] == 'suspicious':
            assessment['threat_level'] = 'medium'
            assessment['confidence'] = max(assessment['confidence'], 0.7)
            assessment['factors'].append('suspicious_ip_reputation')
        
        # Check for hosting provider
        if ip_info['is_hosting']:
            assessment['confidence'] = max(assessment['confidence'], 0.6)
            assessment['factors'].append('hosting_provider')
        
        # Check for VPN/Proxy/Tor
        if ip_info.get('is_tor'):
            assessment['threat_level'] = 'high'
            assessment['confidence'] = max(assessment['confidence'], 0.8)
            assessment['recommendation'] = 'block'
            assessment['factors'].append('tor_exit_node')
        
        # Path-based assessment
        if self._is_suspicious_path(path):
            assessment['threat_level'] = 'medium' if assessment['threat_level'] == 'low' else assessment['threat_level']
            assessment['confidence'] = max(assessment['confidence'], 0.6)
            assessment['factors'].append('suspicious_path')
        
        # Final recommendation
        if assessment['threat_level'] == 'high' or assessment['confidence'] > 0.8:
            assessment['recommendation'] = 'block'
        elif assessment['threat_level'] == 'medium' or assessment['confidence'] > 0.6:
            assessment['recommendation'] = 'challenge'
        else:
            assessment['recommendation'] = 'allow'
        
        return assessment
    
    def _is_suspicious_path(self, path: str) -> bool:
        """Check if path indicates suspicious activity"""
        suspicious_paths = [
            r'/wp-admin', r'/wp-login', r'/wp-config', r'/wp-content',
            r'/admin', r'/administrator', r'/login', r'/phpmyadmin',
            r'/xmlrpc\.php', r'/wp-includes', r'/wp-json',
            r'/\.env', r'/\.git', r'/\.svn', r'/\.htaccess',
            r'/config\.php', r'/database\.php', r'/db\.php',
            r'/backup', r'/sql', r'/dump', r'/export',
            r'/shell', r'/cmd', r'/exec', r'/system',
        ]
        
        for pattern in suspicious_paths:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        return False

class RateLimiter:
    """Advanced rate limiting with IP tracking"""
    
    def __init__(self):
        self.requests = defaultdict(deque)  # IP -> deque of timestamps
        self.violations = defaultdict(int)  # IP -> violation count
        self.blocked_until = defaultdict(float)  # IP -> timestamp when unblocked
        
        # Rate limiting rules
        self.rules = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
            'burst_requests': 10,  # max requests in 10 seconds
            'violation_threshold': 5,  # violations before long-term block
            'block_duration': 3600,  # 1 hour block
            'long_term_block_duration': 86400,  # 24 hour block
        }
    
    def is_rate_limited(self, ip: str) -> Tuple[bool, Dict]:
        """Check if IP is rate limited"""
        current_time = time.time()
        
        # Check if IP is currently blocked
        if ip in self.blocked_until:
            if current_time < self.blocked_until[ip]:
                return True, {
                    'blocked': True,
                    'reason': 'rate_limit_violation',
                    'unblocked_at': self.blocked_until[ip],
                    'violations': self.violations[ip]
                }
            else:
                # Block expired
                del self.blocked_until[ip]
        
        # Clean old requests
        self._cleanup_old_requests(ip, current_time)
        
        # Add current request
        self.requests[ip].append(current_time)
        
        # Check rate limits
        violation_info = self._check_rate_limits(ip, current_time)
        
        if violation_info['violated']:
            self.violations[ip] += 1
            
            # Determine block duration
            if self.violations[ip] >= self.rules['violation_threshold']:
                block_duration = self.rules['long_term_block_duration']
            else:
                block_duration = self.rules['block_duration']
            
            self.blocked_until[ip] = current_time + block_duration
            
            # Log violation
            logger.warning(f"🚫 Rate limit violation: IP {ip} blocked for {block_duration}s (violations: {self.violations[ip]})")
            
            # Send security alert
            security_monitor.send_telegram_alert(
                f"Rate limit violation: IP {ip} exceeded limits\n"
                f"Violations: {self.violations[ip]}\n"
                f"Blocked for: {block_duration}s",
                AlertLevel.MEDIUM
            )
            
            return True, violation_info
        
        return False, {'blocked': False}
    
    def _cleanup_old_requests(self, ip: str, current_time: float):
        """Remove old requests from tracking"""
        if ip not in self.requests:
            return
        
        # Remove requests older than 24 hours
        cutoff_time = current_time - 86400
        
        while self.requests[ip] and self.requests[ip][0] < cutoff_time:
            self.requests[ip].popleft()
    
    def _check_rate_limits(self, ip: str, current_time: float) -> Dict:
        """Check various rate limits"""
        requests_queue = self.requests[ip]
        
        # Check burst requests (last 10 seconds)
        burst_cutoff = current_time - 10
        burst_requests = sum(1 for t in requests_queue if t > burst_cutoff)
        
        if burst_requests > self.rules['burst_requests']:
            return {
                'violated': True,
                'rule': 'burst_requests',
                'limit': self.rules['burst_requests'],
                'actual': burst_requests,
                'window': '10 seconds'
            }
        
        # Check requests per minute
        minute_cutoff = current_time - 60
        minute_requests = sum(1 for t in requests_queue if t > minute_cutoff)
        
        if minute_requests > self.rules['requests_per_minute']:
            return {
                'violated': True,
                'rule': 'requests_per_minute',
                'limit': self.rules['requests_per_minute'],
                'actual': minute_requests,
                'window': '1 minute'
            }
        
        # Check requests per hour
        hour_cutoff = current_time - 3600
        hour_requests = sum(1 for t in requests_queue if t > hour_cutoff)
        
        if hour_requests > self.rules['requests_per_hour']:
            return {
                'violated': True,
                'rule': 'requests_per_hour',
                'limit': self.rules['requests_per_hour'],
                'actual': hour_requests,
                'window': '1 hour'
            }
        
        # Check requests per day
        day_cutoff = current_time - 86400
        day_requests = sum(1 for t in requests_queue if t > day_cutoff)
        
        if day_requests > self.rules['requests_per_day']:
            return {
                'violated': True,
                'rule': 'requests_per_day',
                'limit': self.rules['requests_per_day'],
                'actual': day_requests,
                'window': '1 day'
            }
        
        return {'violated': False}

# Global instances
ip_intelligence = IPIntelligence()
rate_limiter = RateLimiter()

def analyze_request_threat(ip: str, user_agent: str, path: str, method: str) -> Dict:
    """Analyze request for threats"""
    return ip_intelligence.assess_threat_level(ip, user_agent, path, method)

def check_rate_limit(ip: str) -> Tuple[bool, Dict]:
    """Check if IP is rate limited"""
    return rate_limiter.is_rate_limited(ip)

def is_ip_whitelisted(ip: str) -> bool:
    """Check if IP is whitelisted"""
    return ip_intelligence.is_whitelisted_ip(ip)

def get_ip_reputation(ip: str) -> Dict:
    """Get IP reputation information"""
    return ip_intelligence.get_ip_info(ip)
