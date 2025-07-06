@echo off
REM Daily security report

echo 📊 Generating daily security report...

set DATE=%date:~10,4%-07-06
set REPORT_FILE=logs\security\daily_report_%DATE%.txt

echo Sofi AI Security Report - %DATE% > %REPORT_FILE%
echo ================================= >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM Count events
for /f %i in ('findstr /c:"📊" logs\security\access.log 2>nul | find /c /v ""') do set TOTAL_REQUESTS=%i
for /f %i in ('findstr /c:"🚫" logs\security\access.log 2>nul | find /c /v ""') do set BLOCKED_REQUESTS=%i
for /f %i in ('findstr /c:"🚨" logs\security\access.log 2>nul | find /c /v ""') do set SUSPICIOUS_REQUESTS=%i

echo Total Requests: %TOTAL_REQUESTS% >> %REPORT_FILE%
echo Blocked Requests: %BLOCKED_REQUESTS% >> %REPORT_FILE%
echo Suspicious Requests: %SUSPICIOUS_REQUESTS% >> %REPORT_FILE%

echo ✅ Security report generated: %REPORT_FILE%
