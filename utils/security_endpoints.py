"""
SOFI AI SECURITY ENDPOINTS
==========================
Flask endpoints for security monitoring, IP blocking, and health checks
"""

from flask import Blueprint, request, jsonify
from utils.security_monitor import security_monitor, AlertLevel
from utils.security import get_client_ip, is_rate_limited
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create security blueprint
security_bp = Blueprint('security', __name__, url_prefix='/security')

# Admin API key for security endpoints
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'your-secret-admin-key')

def require_admin_auth():
    """Check if request has valid admin authorization"""
    auth_header = request.headers.get('Authorization')
    api_key = request.headers.get('X-API-Key')
    
    # Check Authorization header
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if token == ADMIN_API_KEY:
            return True
    
    # Check X-API-Key header
    if api_key == ADMIN_API_KEY:
        return True
    
    return False

@security_bp.route('/health', methods=['GET'])
def security_health_check():
    """Health check endpoint"""
    try:
        # Get basic system stats
        stats = security_monitor.get_security_stats()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': 'active',
            'security_monitor': 'active',
            'total_events': stats.get('total_events', 0),
            'alerts_sent': stats.get('alerts_sent', 0),
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@security_bp.route('/stats', methods=['GET'])
def get_security_stats():
    """Get security statistics"""
    try:
        # Check if admin auth is required for stats
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        stats = security_monitor.get_security_stats()
        
        # Add additional stats
        stats.update({
            'blocked_ips': list(security_monitor.blocked_ips),
            'whitelisted_ips': list(security_monitor.whitelist_ips),
            'monitoring_active': True,
            'last_updated': datetime.now().isoformat()
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting security stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/events', methods=['GET'])
def get_security_events():
    """Get recent security events"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get query parameters
        count = request.args.get('count', 100, type=int)
        severity = request.args.get('severity', None)
        hours = request.args.get('hours', 24, type=int)
        
        # Get events
        events = security_monitor.get_recent_events(count)
        
        # Filter by severity if specified
        if severity:
            events = [e for e in events if e.get('severity') == severity]
        
        # Filter by time window
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            events = [e for e in events if datetime.fromisoformat(e['timestamp']) > cutoff_time]
        
        return jsonify({
            'events': events,
            'total_count': len(events),
            'filters': {
                'severity': severity,
                'hours': hours,
                'count': count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting security events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/block-ip', methods=['POST'])
def block_ip():
    """Block an IP address"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data or 'ip' not in data:
            return jsonify({'error': 'Missing IP address'}), 400
        
        ip = data['ip']
        reason = data.get('reason', 'Manual block via API')
        
        # Validate IP format (basic check)
        if not ip or len(ip.split('.')) != 4:
            return jsonify({'error': 'Invalid IP format'}), 400
        
        # Block the IP
        security_monitor.block_ip(ip, reason)
        
        return jsonify({
            'success': True,
            'blocked_ip': ip,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error blocking IP: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/unblock-ip', methods=['POST'])
def unblock_ip():
    """Unblock an IP address"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data or 'ip' not in data:
            return jsonify({'error': 'Missing IP address'}), 400
        
        ip = data['ip']
        
        # Unblock the IP
        security_monitor.unblock_ip(ip)
        
        return jsonify({
            'success': True,
            'unblocked_ip': ip,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error unblocking IP: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/whitelist-ip', methods=['POST'])
def whitelist_ip():
    """Add IP to whitelist"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data or 'ip' not in data:
            return jsonify({'error': 'Missing IP address'}), 400
        
        ip = data['ip']
        
        # Add to whitelist
        security_monitor.whitelist_ip(ip)
        
        return jsonify({
            'success': True,
            'whitelisted_ip': ip,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error whitelisting IP: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/check-ip', methods=['POST'])
def check_ip():
    """Check IP status (blocked/whitelisted)"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data or 'ip' not in data:
            return jsonify({'error': 'Missing IP address'}), 400
        
        ip = data['ip']
        
        return jsonify({
            'ip': ip,
            'blocked': security_monitor.is_ip_blocked(ip),
            'whitelisted': security_monitor.is_ip_whitelisted(ip),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error checking IP: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/alert', methods=['POST'])
def send_security_alert():
    """Send a manual security alert"""
    try:
        if not require_admin_auth():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing alert message'}), 400
        
        message = data['message']
        severity = data.get('severity', 'medium')
        
        # Convert severity to AlertLevel
        severity_map = {
            'low': AlertLevel.LOW,
            'medium': AlertLevel.MEDIUM,
            'high': AlertLevel.HIGH,
            'critical': AlertLevel.CRITICAL
        }
        
        alert_level = severity_map.get(severity.lower(), AlertLevel.MEDIUM)
        
        # Send alert
        success = security_monitor.send_telegram_alert(message, alert_level)
        
        return jsonify({
            'success': success,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error sending alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Global health endpoint (no auth required)
@security_bp.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint for uptime monitoring"""
    return jsonify({
        'status': 'pong',
        'timestamp': datetime.now().isoformat(),
        'service': 'sofi-ai-security'
    }), 200

# Bot detection endpoint
@security_bp.route('/detect-bot', methods=['POST'])
def detect_bot():
    """Detect if current request is from a bot"""
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        path = request.json.get('path', '/') if request.json else '/'
        method = request.json.get('method', 'GET') if request.json else 'GET'
        
        # Check for suspicious activity
        suspicious_event = security_monitor.detect_suspicious_activity(
            client_ip, path, user_agent, method
        )
        
        if suspicious_event:
            security_monitor.log_security_event(suspicious_event)
            
            return jsonify({
                'is_bot': True,
                'threat_level': suspicious_event.severity.value,
                'details': suspicious_event.details,
                'recommendation': 'Block this request'
            }), 200
        
        return jsonify({
            'is_bot': False,
            'threat_level': 'safe',
            'recommendation': 'Allow request'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error detecting bot: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def init_security_endpoints(app):
    """Initialize security endpoints with Flask app"""
    app.register_blueprint(security_bp)
    logger.info("🔐 Security endpoints initialized")
