"""
SOFI AI SECURITY MONITORING
===========================
Real-time security monitoring and alerting system with Telegram alerts
"""

import logging
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import threading
import requests
import hashlib
import re
from dataclasses import dataclass, asdict
from enum import Enum

# ⚡ IMPORT PERFORMANCE CONFIG for fast mode
try:
    from .performance_config import (
        ENABLE_FAST_MODE, ENABLE_SECURITY_ALERTS, ENABLE_SECURITY_LOGGING,
        ENABLE_CRITICAL_ALERTS_ONLY, ALERT_COOLDOWN_SECONDS, ALWAYS_ALLOW_CRITICAL,
        ENABLE_MONITORING_THREAD
    )
    print("✅ Performance config loaded - Fast mode controls active")
except ImportError:
    # Fallback to normal mode if config not found
    ENABLE_FAST_MODE = False
    ENABLE_SECURITY_ALERTS = True
    ENABLE_SECURITY_LOGGING = True
    ENABLE_CRITICAL_ALERTS_ONLY = False
    ALERT_COOLDOWN_SECONDS = 60
    ALWAYS_ALLOW_CRITICAL = True
    ENABLE_MONITORING_THREAD = True
    print("⚠️ Performance config not found - using normal mode")

logger = logging.getLogger(__name__)

# Admin Telegram ID for security alerts
ADMIN_TELEGRAM_ID = "5495194750"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    timestamp: datetime
    event_type: str
    severity: AlertLevel
    ip_address: str
    user_agent: str
    path: str
    method: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severity'] = self.severity.value
        return data

class SecurityMonitor:
    """Real-time security monitoring system with Telegram alerts"""
    
    def __init__(self):
        self.events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.stats = defaultdict(int)
        self.alerts_sent = defaultdict(int)
        self.suspicious_ips = defaultdict(int)
        self.alert_cooldown = defaultdict(int)  # Prevent spam alerts
        self.last_alert_time = defaultdict(float)
        
        # Initialize alert counters
        self.daily_alerts = defaultdict(int)
        self.last_daily_reset = datetime.now().date()
        
        # Initialize security monitor components
        self._initialize_security_monitor()
        
    def send_telegram_alert(self, message: str, severity: AlertLevel = AlertLevel.MEDIUM):
        """Send security alert to admin via Telegram - FAST MODE OPTIMIZED"""
        
        # 🚀 FAST MODE: Skip non-critical alerts entirely
        if ENABLE_FAST_MODE and not ENABLE_SECURITY_ALERTS:
            if severity != AlertLevel.CRITICAL or not ALWAYS_ALLOW_CRITICAL:
                if ENABLE_SECURITY_LOGGING:
                    logger.debug(f"⚡ FAST MODE: Skipped alert - {message[:50]}...")
                return True  # Return True to not break workflows
        
        try:
            if not TELEGRAM_BOT_TOKEN:
                if ENABLE_SECURITY_LOGGING:
                    logger.error("❌ No Telegram bot token configured for security alerts")
                return False
                
            # Rate limiting for alerts - FAST MODE uses no cooldown
            alert_key = hashlib.md5(message.encode()).hexdigest()
            current_time = time.time()
            
            if not ENABLE_FAST_MODE and alert_key in self.last_alert_time:
                if current_time - self.last_alert_time[alert_key] < ALERT_COOLDOWN_SECONDS:
                    if ENABLE_SECURITY_LOGGING:
                        logger.debug(f"⏳ Alert suppressed (cooldown): {message[:50]}...")
                    return False
            
            self.last_alert_time[alert_key] = current_time
            
            # 🚀 FAST MODE: Only send critical alerts
            if ENABLE_CRITICAL_ALERTS_ONLY and severity not in [AlertLevel.CRITICAL, AlertLevel.HIGH]:
                if ENABLE_SECURITY_LOGGING:
                    logger.debug(f"⚡ FAST MODE: Non-critical alert skipped - {message[:50]}...")
                return True
            
            # Format alert message with severity emoji
            severity_emoji = {
                AlertLevel.LOW: "ℹ️",
                AlertLevel.MEDIUM: "⚠️",
                AlertLevel.HIGH: "🚨",
                AlertLevel.CRITICAL: "🔥"
            }
            
            alert_message = f"{severity_emoji.get(severity, '⚠️')} **SOFI SECURITY ALERT**\n\n{message}\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ADMIN_TELEGRAM_ID,
                "text": alert_message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            # 🚀 FAST MODE: Use shorter timeout
            response = requests.post(url, json=payload, timeout=3 if ENABLE_FAST_MODE else 10)
            
            if response.status_code == 200:
                if ENABLE_SECURITY_LOGGING:
                    logger.info(f"✅ Security alert sent to admin: {message[:50]}...")
                self.stats['alerts_sent'] += 1
                return True
            else:
                if ENABLE_SECURITY_LOGGING:
                    logger.error(f"❌ Failed to send security alert: {response.text}")
                return False
                
        except Exception as e:
            if ENABLE_SECURITY_LOGGING:
                logger.error(f"❌ Error sending security alert: {str(e)}")
            return False
    
    def send_sofi_alert(self, message: str, severity: AlertLevel = AlertLevel.MEDIUM):
        """Send security alert through Sofi AI assistant"""
        try:
            # This will be called by the assistant when suspicious activity is detected
            from assistant import get_assistant
            
            assistant = get_assistant()
            
            # Create a security-focused message from Sofi
            sofi_message = f"""🤖 **Sofi Security Alert**
            
I've detected suspicious activity on your backend:

{message}

As your AI assistant, I recommend reviewing this activity immediately.

Stay secure! 🔒
"""
            
            # Send through Sofi's messaging system
            return self.send_telegram_alert(sofi_message, severity)
            
        except Exception as e:
            logger.error(f"❌ Error sending Sofi security alert: {str(e)}")
            # Fallback to regular alert
            return self.send_telegram_alert(message, severity)
    
    def _initialize_security_monitor(self):
        """Initialize security monitor components - FAST MODE OPTIMIZED"""
        self.blocked_ips = set()
        self.whitelist_ips = set()
        
        # Alert thresholds
        self.thresholds = {
            'failed_requests_per_minute': 20,
            'blocked_ips_per_hour': 10,
            'suspicious_activities_per_hour': 50,
            'rate_limit_violations_per_hour': 100,
            'exploit_attempts_per_hour': 5,
        }
        
        # 🚀 FAST MODE: Skip monitoring thread for better performance
        if ENABLE_MONITORING_THREAD and not ENABLE_FAST_MODE:
            # Start monitoring thread only in normal mode
            self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("🔍 Security Monitor thread started")
        else:
            logger.info("⚡ Security Monitor in FAST MODE - thread disabled for speed")
        
        mode_status = "FAST MODE" if ENABLE_FAST_MODE else "NORMAL MODE"
        logger.info(f"🔍 Security Monitor initialized in {mode_status}")
    
    def log_event(self, event_type: str, severity: AlertLevel, ip: str, 
                  user_agent: str, path: str, method: str, **details):
        """Log a security event - FAST MODE OPTIMIZED"""
        
        # 🚀 FAST MODE: Skip detailed logging for minor events
        if ENABLE_FAST_MODE and severity in [AlertLevel.LOW, AlertLevel.MEDIUM]:
            if not ENABLE_SECURITY_LOGGING:
                return  # Skip entirely in fast mode
        
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            ip_address=ip,
            user_agent=user_agent,
            path=path,
            method=method,
            details=details
        )
        
        # Only store events if logging is enabled
        if ENABLE_SECURITY_LOGGING:
            self.events.append(event)
            self.stats[event_type] += 1
        
        # Update suspicious IP tracking
        if severity in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            self.suspicious_ips[ip] += 1
        
        # 🚀 FAST MODE: Minimal logging for speed
        if ENABLE_FAST_MODE:
            if severity in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
                logger.warning(f"🚨 Critical Security Event: {event_type} from {ip}")
        else:
            # Full logging in normal mode
            logger.warning(f"🚨 Security Event: {event_type} from {ip} -> {path} [{severity.value}]")
        
        # Check for alert conditions only if alerts are enabled
        if ENABLE_SECURITY_ALERTS or (ALWAYS_ALLOW_CRITICAL and severity == AlertLevel.CRITICAL):
            self._check_alert_conditions(event)
    
    def _check_alert_conditions(self, event: SecurityEvent):
        """Check if event triggers alerts"""
        current_time = datetime.now()
        
        # Count recent events of same type
        recent_events = [
            e for e in self.events 
            if e.event_type == event.event_type and 
            (current_time - e.timestamp) < timedelta(minutes=5)
        ]
        
        # Alert conditions
        if len(recent_events) >= 10:
            self._send_alert(f"High frequency {event.event_type} events", AlertLevel.HIGH, {
                'event_count': len(recent_events),
                'time_window': '5 minutes',
                'source_ip': event.ip_address
            })
        
        # Critical conditions
        if event.severity == AlertLevel.CRITICAL:
            self._send_alert(f"Critical security event: {event.event_type}", AlertLevel.CRITICAL, {
                'event': event.to_dict()
            })
    
    def _send_alert(self, message: str, level: AlertLevel, details: Dict):
        """Send security alert"""
        alert_key = f"{message}_{level.value}"
        
        # Rate limit alerts (max 1 per hour for same alert)
        if self.alerts_sent[alert_key] > 0:
            last_alert_time = self.alerts_sent[alert_key]
            if time.time() - last_alert_time < 3600:  # 1 hour
                return
        
        # Record alert
        self.alerts_sent[alert_key] = time.time()
        
        # Log alert
        logger.critical(f"🚨 SECURITY ALERT [{level.value.upper()}]: {message}")
        logger.critical(f"📋 Details: {json.dumps(details, indent=2, default=str)}")
        
        # Send notifications (implement as needed)
        self._send_notifications(message, level, details)
    
    def _send_notifications(self, message: str, level: AlertLevel, details: Dict):
        """Send notifications via various channels"""
        
        # Email notifications (implement if needed)
        if level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            self._send_email_alert(message, level, details)
        
        # Webhook notifications (implement if needed)
        self._send_webhook_alert(message, level, details)
        
        # Telegram admin notifications for critical alerts
        if level == AlertLevel.CRITICAL:
            self._send_telegram_admin_alert(message, details)
    
    def _send_email_alert(self, message: str, level: AlertLevel, details: Dict):
        """Send email alert (placeholder)"""
        # Implement email sending logic here
        pass
    
    def _send_webhook_alert(self, message: str, level: AlertLevel, details: Dict):
        """Send webhook alert (placeholder)"""
        # Implement webhook sending logic here
        pass
    
    def _send_telegram_admin_alert(self, message: str, details: Dict):
        """Send Telegram alert to admin"""
        try:
            import os
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            admin_chat_id = os.getenv('ADMIN_CHAT_ID')
            
            if not bot_token or not admin_chat_id:
                return
            
            alert_text = f"🚨 SOFI AI SECURITY ALERT\n\n{message}\n\n"
            alert_text += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            alert_text += f"Details: {json.dumps(details, indent=2, default=str)}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": admin_chat_id,
                "text": alert_text[:4096],  # Telegram message limit
                "parse_mode": "Markdown"
            }
            
            requests.post(url, json=payload, timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                self._analyze_trends()
                self._cleanup_old_events()
                self._update_statistics()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _analyze_trends(self):
        """Analyze security trends"""
        current_time = datetime.now()
        
        # Analyze last hour
        hour_ago = current_time - timedelta(hours=1)
        recent_events = [e for e in self.events if e.timestamp > hour_ago]
        
        # Count by type
        event_counts = defaultdict(int)
        for event in recent_events:
            event_counts[event.event_type] += 1
        
        # Check thresholds
        for event_type, count in event_counts.items():
            threshold_key = f"{event_type}_per_hour"
            if threshold_key in self.thresholds:
                if count >= self.thresholds[threshold_key]:
                    self._send_alert(f"High {event_type} activity", AlertLevel.MEDIUM, {
                        'count': count,
                        'threshold': self.thresholds[threshold_key],
                        'time_window': '1 hour'
                    })
    
    def _cleanup_old_events(self):
        """Clean up old events"""
        cutoff_time = datetime.now() - timedelta(days=1)
        
        # Remove events older than 24 hours
        while self.events and self.events[0].timestamp < cutoff_time:
            self.events.popleft()
    
    def _update_statistics(self):
        """Update security statistics"""
        current_time = datetime.now()
        
        # Update hourly stats
        hour_ago = current_time - timedelta(hours=1)
        recent_events = [e for e in self.events if e.timestamp > hour_ago]
        
        self.stats['events_last_hour'] = len(recent_events)
        self.stats['blocked_ips_count'] = len(self.blocked_ips)
        self.stats['suspicious_ips_count'] = len(self.suspicious_ips)
        self.stats['total_events'] = len(self.events)
    
    def detect_suspicious_activity(self, ip: str, path: str, user_agent: str, method: str) -> Optional[SecurityEvent]:
        """Detect suspicious activity and return security event if found"""
        current_time = datetime.now()
        severity = AlertLevel.LOW
        details = {}
        
        # Check for WordPress/CMS attacks
        wp_patterns = [
            r'/wp-admin', r'/wp-login', r'/wp-config', r'/wp-content',
            r'/wordpress', r'/setup-config\.php', r'/wp-includes',
            r'/admin', r'/administrator', r'/wp-admin\.php'
        ]
        
        for pattern in wp_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                severity = AlertLevel.HIGH
                details['attack_type'] = 'WordPress/CMS Attack'
                details['pattern_matched'] = pattern
                break
        
        # Check for suspicious user agents
        suspicious_agents = [
            r'python-requests', r'curl', r'wget', r'bot', r'crawler', r'spider',
            r'scanner', r'exploit', r'hack', r'attack', r'penetration',
            r'nikto', r'sqlmap', r'nmap', r'dirb', r'gobuster'
        ]
        
        for agent_pattern in suspicious_agents:
            if re.search(agent_pattern, user_agent, re.IGNORECASE):
                if severity == AlertLevel.LOW:
                    severity = AlertLevel.MEDIUM
                details['suspicious_agent'] = True
                details['agent_pattern'] = agent_pattern
                break
        
        # Check for high-frequency requests (simple rate limiting detection)
        self.suspicious_ips[ip] += 1
        if self.suspicious_ips[ip] > 50:  # More than 50 requests
            severity = AlertLevel.HIGH
            details['high_frequency'] = True
            details['request_count'] = self.suspicious_ips[ip]
        
        # Check for database/config file access
        dangerous_paths = [
            r'\.env', r'config\.php', r'database\.php', r'db\.php',
            r'phpmyadmin', r'mysql', r'adminer',
            r'\.git', r'\.svn', r'\.htaccess', r'\.htpasswd'
        ]
        
        for danger_pattern in dangerous_paths:
            if re.search(danger_pattern, path, re.IGNORECASE):
                severity = AlertLevel.CRITICAL
                details['attack_type'] = 'Sensitive File Access'
                details['pattern_matched'] = danger_pattern
                break
        
        # Only return event if suspicious activity detected
        if severity != AlertLevel.LOW or details:
            return SecurityEvent(
                timestamp=current_time,
                event_type='suspicious_activity',
                severity=severity,
                ip_address=ip,
                user_agent=user_agent,
                path=path,
                method=method,
                details=details
            )
        
        return None
    
    def log_security_event(self, event):
        """Log security event and send alert if necessary"""
        try:
            # Handle both SecurityEvent objects and dictionaries
            if isinstance(event, dict):
                # Convert dict to SecurityEvent
                security_event = SecurityEvent(
                    timestamp=event.get('timestamp', datetime.now()),
                    event_type=event.get('event_type', 'unknown'),
                    severity=event.get('severity', AlertLevel.LOW),
                    ip_address=event.get('ip_address', 'unknown'),
                    user_agent=event.get('user_agent', ''),
                    path=event.get('path', ''),
                    method=event.get('method', ''),
                    details=event.get('details', {})
                )
            else:
                security_event = event
            
            self.events.append(security_event)
            self.stats[f'events_{security_event.severity.value}'] += 1
            
            # Log to file
            logger.warning(f"🔒 Security Event: {security_event.event_type} - {security_event.severity.value} - {security_event.ip_address} - {security_event.path}")
            
            # Send alert for medium+ severity events
            if security_event.severity in [AlertLevel.MEDIUM, AlertLevel.HIGH, AlertLevel.CRITICAL]:
                self.send_security_alert(security_event)
                
        except Exception as e:
            logger.error(f"❌ Error logging security event: {str(e)}")
    
    def send_security_alert(self, event: SecurityEvent):
        """Send formatted security alert"""
        try:
            # Format alert message
            alert_message = self.format_alert_message(event)
            
            # Send via Telegram
            if event.severity == AlertLevel.CRITICAL:
                self.send_telegram_alert(alert_message, event.severity)
                self.send_sofi_alert(alert_message, event.severity)
            elif event.severity == AlertLevel.HIGH:
                self.send_telegram_alert(alert_message, event.severity)
            else:
                self.send_sofi_alert(alert_message, event.severity)
                
        except Exception as e:
            logger.error(f"❌ Error sending security alert: {str(e)}")
    
    def format_alert_message(self, event: SecurityEvent) -> str:
        """Format security alert message"""
        attack_type = event.details.get('attack_type', 'Suspicious Activity')
        
        message = f"""**{attack_type} Detected**

🌐 **IP Address:** {event.ip_address}
📁 **Path:** {event.path}
🔗 **Method:** {event.method}
🤖 **User Agent:** {event.user_agent[:100]}...
⏰ **Time:** {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Add specific details
        if event.details.get('pattern_matched'):
            message += f"🎯 **Pattern:** {event.details['pattern_matched']}\n"
        
        if event.details.get('request_count'):
            message += f"📊 **Request Count:** {event.details['request_count']}\n"
            
        if event.details.get('suspicious_agent'):
            message += f"🚨 **Suspicious Agent Detected**\n"
        
        # Add recommendation
        if event.severity == AlertLevel.CRITICAL:
            message += "\n⚠️ **Immediate action recommended - Block this IP**"
        elif event.severity == AlertLevel.HIGH:
            message += "\n🔍 **Review this activity - Potential threat**"
        
        return message
    
    def monitor_pin_attempts(self, ip: str, success: bool):
        """Monitor PIN entry attempts for brute force detection"""
        try:
            key = f"pin_attempts_{ip}"
            
            if not success:
                self.suspicious_ips[key] += 1
                
                # Alert after 3 failed attempts
                if self.suspicious_ips[key] >= 3:
                    event = SecurityEvent(
                        timestamp=datetime.now(),
                        event_type='brute_force_pin',
                        severity=AlertLevel.HIGH,
                        ip_address=ip,
                        user_agent='PIN Entry System',
                        path='/verify-pin',
                        method='POST',
                        details={
                            'attack_type': 'PIN Brute Force',
                            'failed_attempts': self.suspicious_ips[key]
                        }
                    )
                    self.log_security_event(event)
            else:
                # Reset counter on successful PIN
                if key in self.suspicious_ips:
                    del self.suspicious_ips[key]
                    
        except Exception as e:
            logger.error(f"❌ Error monitoring PIN attempts: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get security statistics (alias for get_security_stats)"""
        return self.get_security_stats()
    
    def get_recent_events(self, count: int = 100) -> List[Dict]:
        """Get recent security events"""
        events = list(self.events)[-count:]
        return [event.to_dict() for event in events]
    
    def block_ip(self, ip: str, reason: str = "Security threat"):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        logger.warning(f"🚫 IP {ip} blocked: {reason}")
        
        # Log the block event
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type='ip_blocked',
            severity=AlertLevel.HIGH,
            ip_address=ip,
            user_agent='Security System',
            path='/security/block-ip',
            method='BLOCK',
            details={'reason': reason}
        )
        self.log_security_event(event)
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"✅ IP {ip} unblocked")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def whitelist_ip(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist_ips.add(ip)
        logger.info(f"✅ IP {ip} added to whitelist")
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        return ip in self.whitelist_ips
    
    def get_security_stats(self) -> Dict:
        """Get current security statistics"""
        return {
            'total_events': len(self.events),
            'stats': dict(self.stats),
            'suspicious_ips': len(self.suspicious_ips),
            'blocked_ips': len(self.blocked_ips),
            'whitelisted_ips': len(self.whitelist_ips),
            'alerts_sent': self.stats.get('alerts_sent', 0),
            'last_24h_events': len([e for e in self.events if e.timestamp > datetime.now() - timedelta(hours=24)]),
            'monitoring_active': True,
            'last_updated': datetime.now().isoformat()
        }
    
    def is_telegram_user(self, user_id: str = None, user_agent: str = None) -> bool:
        """Detect if user is a Telegram user (by ID or user agent)"""
        # You can expand this logic as needed
        if user_id and str(user_id).isdigit():
            return True
        if user_agent and 'Telegram' in user_agent:
            return True
        return False

    def is_android_user(self, user_agent: str = None) -> bool:
        """Detect if user is using Android device"""
        if user_agent and 'Android' in user_agent:
            return True
        return False

    def should_rate_limit(self, ip: str, user_id: str = None, user_agent: str = None) -> bool:
        """Decide if rate limiting should apply to this user/IP"""
        # Whitelist Telegram users and Android users
        if self.is_telegram_user(user_id, user_agent):
            logger.info(f"✅ Whitelisted Telegram user: {user_id} / {user_agent}")
            return False
        if self.is_android_user(user_agent):
            logger.info(f"✅ Whitelisted Android user: {ip} / {user_agent}")
            return False
        # ...existing rate limit logic...
        return True

# Global security monitor instance
security_monitor = SecurityMonitor()

def log_security_event(event_type: str, severity: AlertLevel, ip: str, 
                      user_agent: str, path: str, method: str, **details):
    """Log a security event - FAST MODE OPTIMIZED"""
    # 🚀 FAST MODE: Skip minor events entirely for speed
    if ENABLE_FAST_MODE and severity in [AlertLevel.LOW]:
        return  # Skip low severity events completely
    
    security_monitor.log_event(event_type, severity, ip, user_agent, path, method, **details)

def send_security_alert(message: str, severity: AlertLevel = AlertLevel.MEDIUM):
    """Send security alert - FAST MODE OPTIMIZED"""
    # 🚀 FAST MODE: Only critical alerts
    if ENABLE_FAST_MODE and not ENABLE_SECURITY_ALERTS:
        if severity != AlertLevel.CRITICAL or not ALWAYS_ALLOW_CRITICAL:
            return True  # Silently skip
    
    return security_monitor.send_telegram_alert(message, severity)

def get_security_stats() -> Dict:
    """Get security statistics"""
    return security_monitor.get_stats()

def get_recent_security_events(count: int = 100) -> List[Dict]:
    """Get recent security events"""
    return security_monitor.get_recent_events(count)

def block_ip_address(ip: str, reason: str = "Security threat"):
    """Block an IP address"""
    security_monitor.block_ip(ip, reason)

def unblock_ip_address(ip: str):
    """Unblock an IP address"""
    security_monitor.unblock_ip(ip)

def is_ip_blocked(ip: str) -> bool:
    """Check if IP is blocked"""
    return security_monitor.is_ip_blocked(ip)

# 🚀 FAST MODE CONTROL FUNCTIONS
def enable_fast_mode():
    """Enable fast mode - disables non-critical alerts for ultra-fast responses"""
    global ENABLE_FAST_MODE, ENABLE_SECURITY_ALERTS
    ENABLE_FAST_MODE = True
    ENABLE_SECURITY_ALERTS = False
    print("⚡ SOFI FAST MODE ENABLED - Security alerts suppressed for speed")
    return True

def disable_fast_mode():
    """Disable fast mode - enables all security features"""
    global ENABLE_FAST_MODE, ENABLE_SECURITY_ALERTS
    ENABLE_FAST_MODE = False
    ENABLE_SECURITY_ALERTS = True
    print("🔒 SOFI NORMAL MODE ENABLED - Full security monitoring active")
    return True

def get_fast_mode_status():
    """Get current fast mode status"""
    return {
        'fast_mode': ENABLE_FAST_MODE,
        'security_alerts': ENABLE_SECURITY_ALERTS,
        'critical_alerts_only': ENABLE_CRITICAL_ALERTS_ONLY,
        'monitoring_thread': ENABLE_MONITORING_THREAD
    }

def get_enhanced_security_stats() -> Dict:
    """Get enhanced security statistics with fast mode info"""
    base_stats = security_monitor.get_security_stats()
    fast_mode_status = "ENABLED" if ENABLE_FAST_MODE else "DISABLED"
    alerts_status = "ENABLED" if ENABLE_SECURITY_ALERTS else "DISABLED"
    
    base_stats.update({
        'fast_mode': fast_mode_status,
        'security_alerts': alerts_status,
        'performance_mode': 'FAST' if ENABLE_FAST_MODE else 'NORMAL'
    })
    
    return base_stats
