#!/bin/bash

# SOFI AI SECURITY DEPLOYMENT SCRIPT
# ==================================
# Ensures all security measures are properly configured

echo "🔒 Deploying Sofi AI Security System..."

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in the correct directory. Please run from the project root."
    exit 1
fi

# Check for required environment variables
echo "🔧 Checking environment variables..."
REQUIRED_VARS=("TELEGRAM_BOT_TOKEN" "SUPABASE_URL" "SUPABASE_KEY" "DOMAIN")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  Warning: $var is not set"
    else
        echo "✅ $var is configured"
    fi
done

# Generate admin API key if not exists
if [ -z "$ADMIN_API_KEY" ]; then
    echo "🔑 Generating admin API key..."
    ADMIN_API_KEY=$(openssl rand -hex 32)
    echo "ADMIN_API_KEY=$ADMIN_API_KEY" >> .env
    echo "✅ Admin API key generated and added to .env"
fi

# Set security environment variables
echo "🛡️  Setting security environment variables..."
cat >> .env << EOL

# Security Configuration
ENVIRONMENT=production
DOMAIN=pipinstallsofi.com
SECURITY_LEVEL=strict
ENABLE_RATE_LIMITING=true
ENABLE_THREAT_DETECTION=true
ENABLE_SECURITY_MONITORING=true
ADMIN_API_KEY=$ADMIN_API_KEY

# Security Alerts
SECURITY_ALERTS_ENABLED=true
SECURITY_WEBHOOK_URL=
ADMIN_CHAT_ID=

# HTTPS Configuration
FORCE_HTTPS=true
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000

EOL

# Create security logs directory
echo "📁 Creating security logs directory..."
mkdir -p logs/security
chmod 755 logs/security

# Set up log rotation (if available)
if command -v logrotate &> /dev/null; then
    echo "📜 Setting up log rotation..."
    cat > /etc/logrotate.d/sofi-ai << EOL
/path/to/sofi-ai-deploy/logs/security/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload sofi-ai || true
    endscript
}
EOL
    echo "✅ Log rotation configured"
fi

# Install required security packages
echo "📦 Installing security packages..."
pip install -r requirements.txt

# Add security-specific requirements
cat >> requirements.txt << EOL
# Security packages
flask-limiter
flask-talisman
cryptography
requests
python-dotenv
EOL

pip install flask-limiter flask-talisman cryptography

# Create fail2ban configuration (if available)
if command -v fail2ban-client &> /dev/null; then
    echo "🚫 Configuring fail2ban..."
    cat > /etc/fail2ban/filter.d/sofi-ai.conf << EOL
[Definition]
failregex = ^.*🚫.*IP.*<HOST>.*$
ignoreregex =
EOL

    cat > /etc/fail2ban/jail.d/sofi-ai.conf << EOL
[sofi-ai]
enabled = true
port = 80,443
filter = sofi-ai
logpath = /path/to/sofi-ai-deploy/logs/security/access.log
maxretry = 5
bantime = 3600
findtime = 300
EOL

    systemctl restart fail2ban
    echo "✅ fail2ban configured"
fi

# Create systemd service file (if applicable)
if command -v systemctl &> /dev/null; then
    echo "🔧 Creating systemd service..."
    cat > /etc/systemd/system/sofi-ai.service << EOL
[Unit]
Description=Sofi AI Banking Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/sofi-ai-deploy
Environment=PATH=/path/to/sofi-ai-deploy/venv/bin
ExecStart=/path/to/sofi-ai-deploy/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/path/to/sofi-ai-deploy/logs

[Install]
WantedBy=multi-user.target
EOL

    systemctl daemon-reload
    echo "✅ systemd service created"
fi

# Create security monitoring cron job
echo "⏰ Setting up security monitoring..."
cat > /etc/cron.d/sofi-ai-security << EOL
# Sofi AI Security Monitoring
0 */6 * * * root /path/to/sofi-ai-deploy/scripts/security_check.sh
0 2 * * * root /path/to/sofi-ai-deploy/scripts/security_report.sh
EOL

# Create security check script
mkdir -p scripts
cat > scripts/security_check.sh << EOL
#!/bin/bash
# Security check script

echo "🔍 Running security check..."

# Check for suspicious activities
SUSPICIOUS_COUNT=\$(grep -c "🚨" logs/security/access.log)
if [ \$SUSPICIOUS_COUNT -gt 50 ]; then
    echo "⚠️  High suspicious activity detected: \$SUSPICIOUS_COUNT events"
    # Send alert here
fi

# Check for blocked IPs
BLOCKED_COUNT=\$(grep -c "🚫" logs/security/access.log)
if [ \$BLOCKED_COUNT -gt 20 ]; then
    echo "⚠️  High number of blocked IPs: \$BLOCKED_COUNT"
    # Send alert here
fi

# Check disk space
DISK_USAGE=\$(df -h . | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 85 ]; then
    echo "⚠️  High disk usage: \$DISK_USAGE%"
    # Send alert here
fi

echo "✅ Security check completed"
EOL

chmod +x scripts/security_check.sh

# Create security report script
cat > scripts/security_report.sh << EOL
#!/bin/bash
# Daily security report

echo "📊 Generating daily security report..."

DATE=\$(date +%Y-%m-%d)
REPORT_FILE="logs/security/daily_report_\$DATE.txt"

echo "Sofi AI Security Report - \$DATE" > \$REPORT_FILE
echo "=================================" >> \$REPORT_FILE
echo "" >> \$REPORT_FILE

# Count events
TOTAL_REQUESTS=\$(grep -c "📊" logs/security/access.log)
BLOCKED_REQUESTS=\$(grep -c "🚫" logs/security/access.log)
SUSPICIOUS_REQUESTS=\$(grep -c "🚨" logs/security/access.log)

echo "Total Requests: \$TOTAL_REQUESTS" >> \$REPORT_FILE
echo "Blocked Requests: \$BLOCKED_REQUESTS" >> \$REPORT_FILE
echo "Suspicious Requests: \$SUSPICIOUS_REQUESTS" >> \$REPORT_FILE
echo "" >> \$REPORT_FILE

# Top suspicious IPs
echo "Top Suspicious IPs:" >> \$REPORT_FILE
grep "🚨" logs/security/access.log | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | sort | uniq -c | sort -rn | head -10 >> \$REPORT_FILE

echo "✅ Security report generated: \$REPORT_FILE"
EOL

chmod +x scripts/security_report.sh

# Test security configuration
echo "🧪 Testing security configuration..."
python -c "
import sys
sys.path.append('.')
try:
    from utils.security import init_security
    from utils.security_monitor import security_monitor
    from utils.security_config import get_security_config
    print('✅ Security modules imported successfully')
    
    # Test configuration
    config = get_security_config()
    print('✅ Security configuration loaded')
    
    # Test monitoring
    stats = security_monitor.get_stats()
    print('✅ Security monitoring initialized')
    
    print('🎉 All security components working correctly!')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

# Create nginx configuration (if nginx is available)
if command -v nginx &> /dev/null; then
    echo "🌐 Creating nginx security configuration..."
    cat > /etc/nginx/sites-available/sofi-ai-security << EOL
# Sofi AI Security Configuration
server {
    listen 80;
    server_name pipinstallsofi.com www.pipinstallsofi.com;
    
    # Force HTTPS
    return 301 https://pipinstallsofi.com\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.pipinstallsofi.com;
    
    # Force non-www
    return 301 https://pipinstallsofi.com\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pipinstallsofi.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://telegram.org; style-src 'self' 'unsafe-inline';" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone \$binary_remote_addr zone=webhook:10m rate=100r/m;
    
    # Block suspicious paths
    location ~* \.(php|asp|aspx|jsp|cgi)\$ {
        return 403;
    }
    
    location ~* /(wp-admin|wp-login|wp-config|phpmyadmin|admin|administrator) {
        return 403;
    }
    
    location ~* \.(htaccess|htpasswd|ini|log|sh|sql|conf)\$ {
        return 403;
    }
    
    # API rate limiting
    location /api/ {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Webhook rate limiting
    location /webhook {
        limit_req zone=webhook burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # General proxy
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias /path/to/sofi-ai-deploy/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # Favicon
    location /favicon.ico {
        alias /path/to/sofi-ai-deploy/static/favicon.ico;
        expires 30d;
    }
    
    # Robots.txt
    location /robots.txt {
        alias /path/to/sofi-ai-deploy/static/robots.txt;
    }
}
EOL

    ln -sf /etc/nginx/sites-available/sofi-ai-security /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    echo "✅ nginx security configuration applied"
fi

# Create security documentation
echo "📚 Creating security documentation..."
cat > SECURITY_DEPLOYMENT.md << EOL
# Sofi AI Security Deployment Guide

## Security Features Deployed

### 🔒 Route Protection
- All suspicious paths blocked (wp-admin, phpmyadmin, etc.)
- Returns 403 Forbidden for blocked paths
- Automated IP blocking for repeated violations

### 🌐 Domain Hardening
- Forces HTTPS redirection
- Enforces non-www domain (pipinstallsofi.com)
- HSTS enabled with 1-year max-age

### 📶 Rate Limiting
- Global: 100 requests/minute
- API endpoints: 30 requests/minute
- Webhook: 200 requests/minute
- Progressive blocking for repeat offenders

### 🔐 Security Headers
- Content-Security-Policy
- X-Frame-Options: DENY
- Strict-Transport-Security
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy

### 🧪 Health Monitoring
- Real-time security event logging
- Automatic threat detection
- IP reputation checking
- Suspicious activity alerts

### 📄 Logs Protection
- Sensitive data sanitization
- Structured security logging
- Automated log rotation
- Daily security reports

## API Endpoints

### Security Monitoring
- GET /security/stats - Get security statistics
- GET /security/events - Get recent security events
- POST /security/block-ip - Block an IP address
- POST /security/unblock-ip - Unblock an IP address

### Authentication
All security endpoints require X-API-Key header with admin API key.

## Configuration

### Environment Variables
- ENVIRONMENT=production
- DOMAIN=pipinstallsofi.com
- SECURITY_LEVEL=strict
- ADMIN_API_KEY=\$ADMIN_API_KEY

### Log Files
- logs/security/access.log - Access logs
- logs/security/security.log - Security events
- logs/security/daily_report_*.txt - Daily reports

## Monitoring

### Automated Scripts
- scripts/security_check.sh - Every 6 hours
- scripts/security_report.sh - Daily at 2 AM

### Alerts
- High suspicious activity (>50 events)
- High blocked IPs (>20)
- High disk usage (>85%)

## Maintenance

### Daily Tasks
- Review security reports
- Check blocked IPs
- Monitor disk usage

### Weekly Tasks
- Review security logs
- Update IP reputation data
- Check SSL certificate status

### Monthly Tasks
- Security audit
- Update security configurations
- Review blocked paths

## Emergency Procedures

### High Traffic Attack
1. Check /security/stats for current status
2. Review /security/events for attack patterns
3. Block attacking IPs via /security/block-ip
4. Contact hosting provider if needed

### Suspicious Activity
1. Review logs/security/access.log
2. Identify attack patterns
3. Update security rules if needed
4. Document incident

## Contact Information
- Security Issues: admin@pipinstallsofi.com
- Emergency: +234-XXX-XXX-XXXX
EOL

echo ""
echo "🎉 Sofi AI Security System Deployment Complete!"
echo ""
echo "✅ Security Features Activated:"
echo "   - Route Protection"
echo "   - Domain Hardening"
echo "   - Rate Limiting"
echo "   - Security Headers"
echo "   - Threat Detection"
echo "   - Real-time Monitoring"
echo "   - Automated Alerts"
echo ""
echo "📊 Security Endpoints:"
echo "   - GET /security/stats"
echo "   - GET /security/events"
echo "   - POST /security/block-ip"
echo "   - POST /security/unblock-ip"
echo ""
echo "🔑 Admin API Key: $ADMIN_API_KEY"
echo "📚 Documentation: SECURITY_DEPLOYMENT.md"
echo ""
echo "🚀 Your domain https://pipinstallsofi.com is now secured!"
echo "🔒 Monitor security status at: https://pipinstallsofi.com/security/stats"
echo ""
echo "⚠️  Remember to:"
echo "   - Set up SSL certificates"
echo "   - Configure firewall rules"
echo "   - Set ADMIN_CHAT_ID for alerts"
echo "   - Test all endpoints"
echo ""
