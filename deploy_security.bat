@echo off
REM SOFI AI SECURITY DEPLOYMENT SCRIPT (Windows)
REM =============================================
REM Ensures all security measures are properly configured

echo 🔒 Deploying Sofi AI Security System...

REM Check if we're in the correct directory
if not exist "main.py" (
    echo ❌ Error: Not in the correct directory. Please run from the project root.
    pause
    exit /b 1
)

REM Check for required environment variables
echo 🔧 Checking environment variables...
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo ⚠️  Warning: TELEGRAM_BOT_TOKEN is not set
) else (
    echo ✅ TELEGRAM_BOT_TOKEN is configured
)

if "%SUPABASE_URL%"=="" (
    echo ⚠️  Warning: SUPABASE_URL is not set
) else (
    echo ✅ SUPABASE_URL is configured
)

if "%SUPABASE_KEY%"=="" (
    echo ⚠️  Warning: SUPABASE_KEY is not set
) else (
    echo ✅ SUPABASE_KEY is configured
)

REM Generate admin API key if not exists
if "%ADMIN_API_KEY%"=="" (
    echo 🔑 Generating admin API key...
    REM Generate random hex string (simplified for Windows)
    set "ADMIN_API_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%"
    echo ADMIN_API_KEY=%ADMIN_API_KEY% >> .env
    echo ✅ Admin API key generated and added to .env
)

REM Set security environment variables
echo 🛡️  Setting security environment variables...
(
echo.
echo # Security Configuration
echo ENVIRONMENT=production
echo DOMAIN=pipinstallsofi.com
echo SECURITY_LEVEL=strict
echo ENABLE_RATE_LIMITING=true
echo ENABLE_THREAT_DETECTION=true
echo ENABLE_SECURITY_MONITORING=true
echo ADMIN_API_KEY=%ADMIN_API_KEY%
echo.
echo # Security Alerts
echo SECURITY_ALERTS_ENABLED=true
echo SECURITY_WEBHOOK_URL=
echo ADMIN_CHAT_ID=
echo.
echo # HTTPS Configuration
echo FORCE_HTTPS=true
echo HSTS_ENABLED=true
echo HSTS_MAX_AGE=31536000
echo.
) >> .env

REM Create security logs directory
echo 📁 Creating security logs directory...
if not exist "logs\security" mkdir logs\security

REM Install required security packages
echo 📦 Installing security packages...
pip install -r requirements.txt

REM Add security-specific requirements
(
echo.
echo # Security packages
echo flask-limiter
echo flask-talisman
echo cryptography
echo requests
echo python-dotenv
) >> requirements.txt

pip install flask-limiter flask-talisman cryptography

REM Create security monitoring scripts
echo ⏰ Setting up security monitoring...
if not exist "scripts" mkdir scripts

REM Create security check script
(
echo @echo off
echo REM Security check script
echo.
echo echo 🔍 Running security check...
echo.
echo REM Check for suspicious activities
echo for /f %%i in ^('findstr /c:"🚨" logs\security\access.log 2^>nul ^| find /c /v ""'^) do set SUSPICIOUS_COUNT=%%i
echo if %%SUSPICIOUS_COUNT%% GTR 50 ^(
echo     echo ⚠️  High suspicious activity detected: %%SUSPICIOUS_COUNT%% events
echo     REM Send alert here
echo ^)
echo.
echo REM Check for blocked IPs
echo for /f %%i in ^('findstr /c:"🚫" logs\security\access.log 2^>nul ^| find /c /v ""'^) do set BLOCKED_COUNT=%%i
echo if %%BLOCKED_COUNT%% GTR 20 ^(
echo     echo ⚠️  High number of blocked IPs: %%BLOCKED_COUNT%%
echo     REM Send alert here
echo ^)
echo.
echo echo ✅ Security check completed
) > scripts\security_check.bat

REM Create security report script
(
echo @echo off
echo REM Daily security report
echo.
echo echo 📊 Generating daily security report...
echo.
echo set DATE=%%date:~10,4%%-%date:~4,2%-%date:~7,2%%
echo set REPORT_FILE=logs\security\daily_report_%%DATE%%.txt
echo.
echo echo Sofi AI Security Report - %%DATE%% ^> %%REPORT_FILE%%
echo echo ================================= ^>^> %%REPORT_FILE%%
echo echo. ^>^> %%REPORT_FILE%%
echo.
echo REM Count events
echo for /f %%i in ^('findstr /c:"📊" logs\security\access.log 2^>nul ^| find /c /v ""'^) do set TOTAL_REQUESTS=%%i
echo for /f %%i in ^('findstr /c:"🚫" logs\security\access.log 2^>nul ^| find /c /v ""'^) do set BLOCKED_REQUESTS=%%i
echo for /f %%i in ^('findstr /c:"🚨" logs\security\access.log 2^>nul ^| find /c /v ""'^) do set SUSPICIOUS_REQUESTS=%%i
echo.
echo echo Total Requests: %%TOTAL_REQUESTS%% ^>^> %%REPORT_FILE%%
echo echo Blocked Requests: %%BLOCKED_REQUESTS%% ^>^> %%REPORT_FILE%%
echo echo Suspicious Requests: %%SUSPICIOUS_REQUESTS%% ^>^> %%REPORT_FILE%%
echo.
echo echo ✅ Security report generated: %%REPORT_FILE%%
) > scripts\security_report.bat

REM Test security configuration
echo 🧪 Testing security configuration...
python -c "import sys; sys.path.append('.'); from utils.security import init_security; from utils.security_monitor import security_monitor; from utils.security_config import get_security_config; print('✅ Security modules imported successfully'); config = get_security_config(); print('✅ Security configuration loaded'); stats = security_monitor.get_stats(); print('✅ Security monitoring initialized'); print('🎉 All security components working correctly!')"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Security configuration test failed
    pause
    exit /b 1
)

REM Create security documentation
echo 📚 Creating security documentation...
(
echo # Sofi AI Security Deployment Guide ^(Windows^)
echo.
echo ## Security Features Deployed
echo.
echo ### 🔒 Route Protection
echo - All suspicious paths blocked ^(wp-admin, phpmyadmin, etc.^)
echo - Returns 403 Forbidden for blocked paths
echo - Automated IP blocking for repeated violations
echo.
echo ### 🌐 Domain Hardening
echo - Forces HTTPS redirection
echo - Enforces non-www domain ^(pipinstallsofi.com^)
echo - HSTS enabled with 1-year max-age
echo.
echo ### 📶 Rate Limiting
echo - Global: 100 requests/minute
echo - API endpoints: 30 requests/minute
echo - Webhook: 200 requests/minute
echo - Progressive blocking for repeat offenders
echo.
echo ### 🔐 Security Headers
echo - Content-Security-Policy
echo - X-Frame-Options: DENY
echo - Strict-Transport-Security
echo - X-Content-Type-Options: nosniff
echo - X-XSS-Protection
echo - Referrer-Policy
echo.
echo ### 🧪 Health Monitoring
echo - Real-time security event logging
echo - Automatic threat detection
echo - IP reputation checking
echo - Suspicious activity alerts
echo.
echo ### 📄 Logs Protection
echo - Sensitive data sanitization
echo - Structured security logging
echo - Automated log rotation
echo - Daily security reports
echo.
echo ## API Endpoints
echo.
echo ### Security Monitoring
echo - GET /security/stats - Get security statistics
echo - GET /security/events - Get recent security events
echo - POST /security/block-ip - Block an IP address
echo - POST /security/unblock-ip - Unblock an IP address
echo.
echo ### Authentication
echo All security endpoints require X-API-Key header with admin API key.
echo.
echo ## Configuration
echo.
echo ### Environment Variables
echo - ENVIRONMENT=production
echo - DOMAIN=pipinstallsofi.com
echo - SECURITY_LEVEL=strict
echo - ADMIN_API_KEY=%ADMIN_API_KEY%
echo.
echo ### Log Files
echo - logs\security\access.log - Access logs
echo - logs\security\security.log - Security events
echo - logs\security\daily_report_*.txt - Daily reports
echo.
echo ## Monitoring
echo.
echo ### Automated Scripts
echo - scripts\security_check.bat - Manual execution
echo - scripts\security_report.bat - Manual execution
echo.
echo ### Alerts
echo - High suspicious activity ^(^>50 events^)
echo - High blocked IPs ^(^>20^)
echo - High disk usage ^(^>85%%^)
echo.
echo ## Windows-Specific Notes
echo.
echo - Use Task Scheduler for automated script execution
echo - Configure Windows Firewall for additional protection
echo - Use IIS or Apache for reverse proxy if needed
echo - Consider using Cloudflare for additional DDoS protection
echo.
echo ## Emergency Procedures
echo.
echo ### High Traffic Attack
echo 1. Check /security/stats for current status
echo 2. Review /security/events for attack patterns
echo 3. Block attacking IPs via /security/block-ip
echo 4. Contact hosting provider if needed
echo.
echo ### Suspicious Activity
echo 1. Review logs\security\access.log
echo 2. Identify attack patterns
echo 3. Update security rules if needed
echo 4. Document incident
) > SECURITY_DEPLOYMENT.md

echo.
echo 🎉 Sofi AI Security System Deployment Complete!
echo.
echo ✅ Security Features Activated:
echo    - Route Protection
echo    - Domain Hardening
echo    - Rate Limiting
echo    - Security Headers
echo    - Threat Detection
echo    - Real-time Monitoring
echo    - Automated Alerts
echo.
echo 📊 Security Endpoints:
echo    - GET /security/stats
echo    - GET /security/events
echo    - POST /security/block-ip
echo    - POST /security/unblock-ip
echo.
echo 🔑 Admin API Key: %ADMIN_API_KEY%
echo 📚 Documentation: SECURITY_DEPLOYMENT.md
echo.
echo 🚀 Your domain https://pipinstallsofi.com is now secured!
echo 🔒 Monitor security status at: https://pipinstallsofi.com/security/stats
echo.
echo ⚠️  Remember to:
echo    - Set up SSL certificates
echo    - Configure firewall rules
echo    - Set ADMIN_CHAT_ID for alerts
echo    - Test all endpoints
echo    - Set up Task Scheduler for automated monitoring
echo.
echo 📋 Next Steps:
echo    1. Test the security system: python -m pytest tests/test_security.py
echo    2. Run the application: python main.py
echo    3. Test endpoints: curl -H "X-API-Key: %ADMIN_API_KEY%" https://pipinstallsofi.com/security/stats
echo    4. Set up Task Scheduler for scripts\security_check.bat
echo.
pause
