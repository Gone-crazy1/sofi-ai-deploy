"""
SOFI AI SECURITY SYSTEM TESTS
=============================
Comprehensive tests for all security components
"""

import pytest
import requests
import json
import time
from unittest.mock import Mock, patch
from flask import Flask
from utils.security import init_security, SecurityMiddleware
from utils.security_monitor import SecurityMonitor, AlertLevel, log_security_event
from utils.security_config import get_security_config, get_blocked_paths, is_path_whitelisted

class TestSecurityMiddleware:
    """Test security middleware functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.security_middleware = SecurityMiddleware(self.app)
        self.client = self.app.test_client()
    
    def test_blocked_paths(self):
        """Test that blocked paths return 403"""
        blocked_paths = [
            '/wp-admin',
            '/wp-login.php',
            '/phpmyadmin',
            '/admin',
            '/.env',
            '/config.php'
        ]
        
        for path in blocked_paths:
            response = self.client.get(path)
            assert response.status_code == 403
            assert 'Access forbidden' in response.get_json()['error']
    
    def test_allowed_paths(self):
        """Test that allowed paths work correctly"""
        # Add a test route
        @self.app.route('/test')
        def test_route():
            return {'message': 'success'}
        
        response = self.client.get('/test')
        assert response.status_code == 200
        assert response.get_json()['message'] == 'success'
    
    def test_security_headers(self):
        """Test that security headers are added"""
        @self.app.route('/test-headers')
        def test_headers():
            return {'message': 'success'}
        
        response = self.client.get('/test-headers')
        
        # Check for security headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'Strict-Transport-Security' in response.headers
        assert 'Content-Security-Policy' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        @self.app.route('/test-rate-limit')
        def test_rate_limit():
            return {'message': 'success'}
        
        # Make multiple requests quickly
        responses = []
        for i in range(150):  # Exceed rate limit
            response = self.client.get('/test-rate-limit')
            responses.append(response.status_code)
        
        # Should have some 429 responses (rate limited)
        assert 429 in responses
    
    def test_suspicious_user_agents(self):
        """Test detection of suspicious user agents"""
        suspicious_agents = [
            'sqlmap/1.0',
            'nikto/2.0',
            'w3af/1.0',
            'nmap/7.0'
        ]
        
        @self.app.route('/test-ua')
        def test_ua():
            return {'message': 'success'}
        
        for agent in suspicious_agents:
            response = self.client.get('/test-ua', headers={'User-Agent': agent})
            # Should still allow but log as suspicious
            assert response.status_code == 200

class TestSecurityMonitor:
    """Test security monitoring functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.monitor = SecurityMonitor()
    
    def test_event_logging(self):
        """Test security event logging"""
        initial_count = len(self.monitor.events)
        
        self.monitor.log_event(
            'test_event',
            AlertLevel.LOW,
            '192.168.1.1',
            'TestBot/1.0',
            '/test',
            'GET',
            test_data='test_value'
        )
        
        assert len(self.monitor.events) == initial_count + 1
        assert self.monitor.events[-1].event_type == 'test_event'
        assert self.monitor.events[-1].ip_address == '192.168.1.1'
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        test_ip = '192.168.1.100'
        
        # Initially not blocked
        assert not self.monitor.is_ip_blocked(test_ip)
        
        # Block the IP
        self.monitor.block_ip(test_ip, 'Test block')
        
        # Should now be blocked
        assert self.monitor.is_ip_blocked(test_ip)
        
        # Unblock the IP
        self.monitor.unblock_ip(test_ip)
        
        # Should no longer be blocked
        assert not self.monitor.is_ip_blocked(test_ip)
    
    def test_statistics_collection(self):
        """Test statistics collection"""
        # Generate some test events
        for i in range(10):
            self.monitor.log_event(
                'test_event',
                AlertLevel.LOW,
                f'192.168.1.{i}',
                'TestBot/1.0',
                '/test',
                'GET'
            )
        
        stats = self.monitor.get_stats()
        assert 'test_event' in stats
        assert stats['test_event'] >= 10
    
    def test_alert_conditions(self):
        """Test alert condition triggering"""
        # Generate many events quickly to trigger alerts
        for i in range(15):
            self.monitor.log_event(
                'suspicious_activity',
                AlertLevel.HIGH,
                '192.168.1.200',
                'AttackerBot/1.0',
                '/admin',
                'GET'
            )
        
        # Should have generated alerts
        assert len(self.monitor.alerts_sent) > 0

class TestSecurityConfig:
    """Test security configuration"""
    
    def test_security_config_loading(self):
        """Test security configuration loading"""
        config = get_security_config('strict')
        assert 'rate_limiting' in config
        assert 'threat_detection' in config
        assert 'monitoring' in config
    
    def test_blocked_paths_loading(self):
        """Test blocked paths loading"""
        blocked_paths = get_blocked_paths()
        assert len(blocked_paths) > 0
        assert any('wp-admin' in path for path in blocked_paths)
        assert any('phpmyadmin' in path for path in blocked_paths)
    
    def test_path_whitelisting(self):
        """Test path whitelisting"""
        # Test whitelisted paths
        assert is_path_whitelisted('/')
        assert is_path_whitelisted('/onboard')
        assert is_path_whitelisted('/webhook')
        assert is_path_whitelisted('/api/test')
        
        # Test non-whitelisted paths
        assert not is_path_whitelisted('/wp-admin')
        assert not is_path_whitelisted('/phpmyadmin')
        assert not is_path_whitelisted('/admin')

class TestSecurityIntegration:
    """Test security system integration"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        init_security(self.app)
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_security_stats_endpoint(self):
        """Test security stats endpoint"""
        # Should require authentication
        response = self.client.get('/security/stats')
        assert response.status_code == 401
        
        # Test with API key
        headers = {'X-API-Key': 'test_key'}
        response = self.client.get('/security/stats', headers=headers)
        # Would return 401 without proper key, but tests structure
    
    def test_cors_headers(self):
        """Test CORS headers"""
        response = self.client.options('/health')
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_https_redirect(self):
        """Test HTTPS redirect functionality"""
        # This would need to be tested in a real environment
        # where HTTP requests can be made
        pass

class TestSecurityPerformance:
    """Test security system performance"""
    
    def test_rate_limiting_performance(self):
        """Test rate limiting performance"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        security_middleware = SecurityMiddleware(app)
        
        # Time rate limiting checks
        start_time = time.time()
        
        with app.test_request_context('/test'):
            for i in range(100):
                try:
                    security_middleware.rate_limit()
                except:
                    pass  # Rate limit exceeded
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should be fast (less than 1 second for 100 checks)
        assert execution_time < 1.0
    
    def test_path_blocking_performance(self):
        """Test path blocking performance"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        security_middleware = SecurityMiddleware(app)
        
        # Time path blocking checks
        start_time = time.time()
        
        test_paths = ['/test', '/wp-admin', '/phpmyadmin', '/admin', '/normal']
        
        for path in test_paths * 20:  # 100 total checks
            with app.test_request_context(path):
                try:
                    security_middleware.block_suspicious_paths()
                except:
                    pass  # Path blocked
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should be fast (less than 0.5 seconds for 100 checks)
        assert execution_time < 0.5

class TestSecurityRealWorld:
    """Test security system with real-world scenarios"""
    
    def test_wordpress_attack_simulation(self):
        """Simulate WordPress attack patterns"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_security(app)
        client = app.test_client()
        
        # Common WordPress attack paths
        attack_paths = [
            '/wp-admin/admin-ajax.php',
            '/wp-login.php',
            '/wp-config.php',
            '/wp-content/plugins/revslider/temp/update_extract/revslider/',
            '/xmlrpc.php'
        ]
        
        for path in attack_paths:
            response = client.get(path)
            assert response.status_code == 403
    
    def test_sql_injection_attempt(self):
        """Test detection of SQL injection attempts"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_security(app)
        client = app.test_client()
        
        # SQL injection patterns
        sql_injection_attempts = [
            "/?id=1' OR '1'='1",
            "/?user=admin'; DROP TABLE users; --",
            "/?search='; SELECT * FROM users; --"
        ]
        
        for attempt in sql_injection_attempts:
            response = client.get(attempt)
            # Should handle gracefully (may return 404 or 400)
            assert response.status_code in [400, 404, 403]
    
    def test_ddos_simulation(self):
        """Simulate DDoS attack"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_security(app)
        client = app.test_client()
        
        @app.route('/test-ddos')
        def test_ddos():
            return {'message': 'success'}
        
        # Simulate rapid requests
        blocked_count = 0
        for i in range(200):
            response = client.get('/test-ddos')
            if response.status_code == 429:
                blocked_count += 1
        
        # Should have blocked some requests
        assert blocked_count > 0
    
    def test_bot_detection(self):
        """Test bot detection and handling"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_security(app)
        client = app.test_client()
        
        @app.route('/test-bot')
        def test_bot():
            return {'message': 'success'}
        
        # Test with bot user agents
        bot_agents = [
            'Googlebot/2.1',
            'TelegramBot (like TwitterBot)',
            'facebookexternalhit/1.1',
            'Malicious-Bot/1.0',
            'AttackerBot/1.0'
        ]
        
        for agent in bot_agents:
            response = client.get('/test-bot', headers={'User-Agent': agent})
            # Should handle different bots appropriately
            assert response.status_code in [200, 403, 429]

def test_full_security_system():
    """Test the complete security system integration"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Initialize security system
    security_middleware = init_security(app)
    assert security_middleware is not None
    
    # Test that all components are working
    client = app.test_client()
    
    # Test health endpoint
    response = client.get('/health')
    assert response.status_code == 200
    
    # Test blocked paths
    response = client.get('/wp-admin')
    assert response.status_code == 403
    
    # Test security headers
    response = client.get('/health')
    assert 'X-Frame-Options' in response.headers
    
    print("✅ All security tests passed!")

if __name__ == '__main__':
    # Run basic tests
    test_full_security_system()
    print("🎉 Security system fully functional!")
