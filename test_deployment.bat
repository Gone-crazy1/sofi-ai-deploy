@echo off
cd /d "c:\Users\T\Sofi_AI_Project"
echo.
echo ============================================
echo SOFI AI DEPLOYMENT VERIFICATION
echo ============================================
echo.

echo Testing Flask Server Health...
curl -s http://localhost:5000/health
echo.
echo.

echo Running Simple Deployment Check...
python simple_deployment_check.py
echo.

echo ============================================
echo DEPLOYMENT CHECK COMPLETE
echo ============================================
pause
