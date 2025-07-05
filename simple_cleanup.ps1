# Sofi AI Workspace Cleanup Script
# This script removes unused backup, test, and demo files to free up space

Write-Host "Starting Sofi AI workspace cleanup..." -ForegroundColor Green

# Get all backup files
$backupFiles = Get-ChildItem -Path "." -Include "*backup*" -Recurse -File | Where-Object { 
    $_.FullName -notmatch "site-packages" 
}

# Get all test files
$testFiles = Get-ChildItem -Path "." -Include "*test*" -Recurse -File | Where-Object { 
    $_.FullName -notmatch "site-packages" -and $_.Extension -eq ".py"
}

# Get all demo files
$demoFiles = Get-ChildItem -Path "." -Include "*demo*" -Recurse -File | Where-Object { 
    $_.FullName -notmatch "site-packages" -and $_.Extension -eq ".py"
}

# Get all old files
$oldFiles = Get-ChildItem -Path "." -Include "*_old*" -Recurse -File | Where-Object { 
    $_.FullName -notmatch "site-packages" 
}

# Combine all files to remove
$allFiles = $backupFiles + $testFiles + $demoFiles + $oldFiles

$removedCount = 0
$totalSize = 0

Write-Host "Found $($allFiles.Count) files to remove" -ForegroundColor Yellow

foreach ($file in $allFiles) {
    try {
        $size = $file.Length
        $totalSize += $size
        Write-Host "Removing: $($file.Name)" -ForegroundColor Red
        Remove-Item $file.FullName -Force
        $removedCount++
    }
    catch {
        Write-Host "Could not remove: $($file.Name)" -ForegroundColor Yellow
    }
}

# Clean up Python cache files
Write-Host "Cleaning Python cache files..." -ForegroundColor Yellow
$cacheFiles = Get-ChildItem -Path "." -Include "*.pyc" -Recurse -Force
$cacheDirs = Get-ChildItem -Path "." -Include "__pycache__" -Recurse -Force -Directory

foreach ($cache in $cacheFiles) {
    try {
        Remove-Item $cache.FullName -Force
        $removedCount++
    }
    catch {
        Write-Host "Could not remove cache file: $($cache.Name)" -ForegroundColor Yellow
    }
}

foreach ($cacheDir in $cacheDirs) {
    try {
        Remove-Item $cacheDir.FullName -Recurse -Force
        $removedCount++
    }
    catch {
        Write-Host "Could not remove cache dir: $($cacheDir.Name)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "Cleanup completed!" -ForegroundColor Green
Write-Host "Files removed: $removedCount" -ForegroundColor Cyan
Write-Host "Space freed: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor Cyan

Write-Host "Workspace is now clean!" -ForegroundColor Green
