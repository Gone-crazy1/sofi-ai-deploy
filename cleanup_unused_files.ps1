# Sofi AI Workspace Cleanup Script
# This script removes unused backup, test, and demo files to free up space

Write-Host "🧹 Starting Sofi AI workspace cleanup..." -ForegroundColor Green

# Files to remove (backup, test, demo files)
$patterns = @(
    "*backup*",
    "*_old*", 
    "*_test*",
    "*_demo*",
    "*_copy*",
    "main_backup*.py",
    "main_original_backup.py"
)

# Specific test and demo files to remove
$specificFiles = @(
    "admin_profit_demo.py",
    "advanced_bitnob_test.py",
    "check_and_create_test_user.py",
    "check_test_users.py",
    "complete_feature_test.py",
    "create_test_user.py",
    "direct_transfer_test.py",
    "final_assistant_transfer_test.py",
    "final_integration_test.py",
    "final_paystack_integration_test.py",
    "final_receipt_test.py",
    "final_working_test.py",
    "fix_pin_and_test_transfer.py",
    "inbound_transfer_branding_demo.py",
    "quick_assistant_test.py",
    "real_money_transfer_test.py",
    "recovery_test.py",
    "security_fixes_demo.py",
    "security_integration_demo.py",
    "simple_account_test.py",
    "sofi_natural_language_demo.py",
    "sofi_user_interaction_demo.py",
    "start_test_server.py",
    "web_app.py",
    "verify_packages.py",
    "validate_env_config.py"
)

# Directories to avoid (keep these safe)
$protectedDirs = @(
    "venv",
    "env",
    ".git",
    "node_modules",
    "templates",
    "static",
    "utils",
    "paystack",
    "functions",
    "nlp",
    "crypto",
    "assistant"
)

$removedCount = 0
$totalSize = 0

Write-Host "🔍 Scanning for unused files..." -ForegroundColor Yellow

# Remove files by pattern
foreach ($pattern in $patterns) {
    $files = Get-ChildItem -Path "." -Include $pattern -Recurse -File | Where-Object { 
        $protected = $false
        foreach ($protectedDir in $protectedDirs) {
            if ($_.FullName -match "\\$protectedDir\\.*site-packages") {
                $protected = $true
                break
            }
        }
        -not $protected
    }
    
    foreach ($file in $files) {
        try {
            $size = $file.Length
            $totalSize += $size
            Write-Host "🗑️  Removing: $($file.Name) ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Red
            Remove-Item $file.FullName -Force
            $removedCount++
        }
        catch {
            Write-Host "⚠️  Could not remove: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

# Remove specific files
foreach ($fileName in $specificFiles) {
    $file = Get-Item $fileName -ErrorAction SilentlyContinue
    if ($file) {
        try {
            $size = $file.Length
            $totalSize += $size
            Write-Host "🗑️  Removing: $($file.Name) ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Red
            Remove-Item $file.FullName -Force
            $removedCount++
        }
        catch {
            Write-Host "⚠️  Could not remove: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

# Clean up Python cache files
Write-Host "🧹 Cleaning Python cache files..." -ForegroundColor Yellow
$cacheFiles = Get-ChildItem -Path "." -Include "*.pyc", "__pycache__" -Recurse -Force
foreach ($cache in $cacheFiles) {
    try {
        if ($cache.PSIsContainer) {
            Remove-Item $cache.FullName -Recurse -Force
            Write-Host "🗑️  Removed cache dir: $($cache.Name)" -ForegroundColor Red
        } else {
            $size = $cache.Length
            $totalSize += $size
            Remove-Item $cache.FullName -Force
            Write-Host "🗑️  Removed cache file: $($cache.Name)" -ForegroundColor Red
        }
        $removedCount++
    }
    catch {
        Write-Host "⚠️  Could not remove cache: $($cache.Name)" -ForegroundColor Yellow
    }
}

# Clean up old log files
Write-Host "🧹 Cleaning old log files..." -ForegroundColor Yellow
$logFiles = Get-ChildItem -Path "." -Include "*.log", "*.txt" -Recurse | Where-Object { 
    $_.Name -match "(log|debug|error|test)" -and $_.Length -gt 1MB 
}
foreach ($log in $logFiles) {
    try {
        $size = $log.Length
        $totalSize += $size
        Write-Host "🗑️  Removing large log: $($log.Name) ($([math]::Round($size/1MB, 2)) MB)" -ForegroundColor Red
        Remove-Item $log.FullName -Force
        $removedCount++
    }
    catch {
        Write-Host "⚠️  Could not remove log: $($log.Name)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n✅ Cleanup completed!" -ForegroundColor Green
Write-Host "📊 Files removed: $removedCount" -ForegroundColor Cyan
Write-Host "💾 Space freed: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor Cyan

Write-Host "`n🔍 Current workspace structure:" -ForegroundColor Yellow
Get-ChildItem -Path "." -Directory | Select-Object Name, @{Name="Size (MB)"; Expression={
    [math]::Round((Get-ChildItem $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
}} | Sort-Object Name

Write-Host "`n🎉 Your Sofi AI workspace is now clean and optimized!" -ForegroundColor Green
