# PowerShell script to test Sofi AI deployment
Write-Host "🚀 SOFI AI DEPLOYMENT TEST" -ForegroundColor Green
Write-Host "=========================="

# Test 1: Python availability
Write-Host "`n🐍 Testing Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python: Not available" -ForegroundColor Red
}

# Test 2: Flask server health
Write-Host "`n🌐 Testing Flask Server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Flask Server: Running (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Flask Server: Not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Test 3: Environment Variables
Write-Host "`n🔧 Testing Environment Variables..." -ForegroundColor Yellow
$envVars = @("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN")
$missingVars = @()

foreach ($var in $envVars) {
    if ($env:$var) {
        Write-Host "✅ $var: Present" -ForegroundColor Green
    } else {
        Write-Host "❌ $var: Missing" -ForegroundColor Red
        $missingVars += $var
    }
}

# Test 4: Simple deployment check
Write-Host "`n📊 Running Deployment Check..." -ForegroundColor Yellow
try {
    python simple_deployment_check.py
} catch {
    Write-Host "❌ Deployment check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n" + "="*50
Write-Host "📈 DEPLOYMENT STATUS SUMMARY" -ForegroundColor Blue
Write-Host "="*50

if ($missingVars.Count -eq 0) {
    Write-Host "✅ Environment Variables: All present" -ForegroundColor Green
} else {
    Write-Host "❌ Missing Variables: $($missingVars -join ', ')" -ForegroundColor Red
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Ensure Flask server is running (python main.py)"
Write-Host "2. Check missing environment variables"
Write-Host "3. Run comprehensive tests"
Write-Host "4. Deploy to Render when ready"

Write-Host "`n✨ Test Complete!" -ForegroundColor Green
