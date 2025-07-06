# Sofi AI Security Deployment Guide (Windows)

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
- ADMIN_API_KEY=20826226312945929509

### Log Files
- logs\security\access.log - Access logs
- logs\security\security.log - Security events
- logs\security\daily_report_*.txt - Daily reports

## Monitoring

### Automated Scripts
- scripts\security_check.bat - Manual execution
- scripts\security_report.bat - Manual execution

### Alerts
- High suspicious activity (>50 events)
- High blocked IPs (>20)
- High disk usage (>85%)

## Windows-Specific Notes

- Use Task Scheduler for automated script execution
- Configure Windows Firewall for additional protection
- Use IIS or Apache for reverse proxy if needed
- Consider using Cloudflare for additional DDoS protection

## Emergency Procedures

### High Traffic Attack
1. Check /security/stats for current status
2. Review /security/events for attack patterns
3. Block attacking IPs via /security/block-ip
4. Contact hosting provider if needed

### Suspicious Activity
1. Review logs\security\access.log
2. Identify attack patterns
3. Update security rules if needed
4. Document incident
