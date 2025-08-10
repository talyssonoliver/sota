# Clean Coverage Script for Windows
# Removes corrupted or stale coverage files to prevent test failures

Write-Host "🧹 Cleaning coverage files..." -ForegroundColor Blue

# Remove all coverage database files
Get-ChildItem -Path . -Recurse -Name ".coverage*" -File | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove main coverage files
Remove-Item -Path "coverage.xml", ".coverage" -Force -ErrorAction SilentlyContinue

# Remove HTML coverage directory and recreate it
Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Name "htmlcov" -Force | Out-Null

# Remove pytest cache
Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue

# Clear coverage environment variables
Remove-Item Env:COVERAGE_FILE -ErrorAction SilentlyContinue
Remove-Item Env:COVERAGE_PROCESS_START -ErrorAction SilentlyContinue

Write-Host "✅ Coverage files cleaned successfully!" -ForegroundColor Green
Write-Host "You can now run tests with: python -m pytest --tb=short --no-cov" -ForegroundColor Yellow