@echo off
REM Security check script

echo 🔍 Running security check...

REM Check for suspicious activities
for /f %i in ('findstr /c:"🚨" logs\security\access.log 2>nul | find /c /v ""') do set SUSPICIOUS_COUNT=%i
if %SUSPICIOUS_COUNT% GTR 50 (
    echo ⚠️  High suspicious activity detected: %SUSPICIOUS_COUNT% events
    REM Send alert here
)

REM Check for blocked IPs
for /f %i in ('findstr /c:"🚫" logs\security\access.log 2>nul | find /c /v ""') do set BLOCKED_COUNT=%i
if %BLOCKED_COUNT% GTR 20 (
    echo ⚠️  High number of blocked IPs: %BLOCKED_COUNT%
    REM Send alert here
)

echo ✅ Security check completed
