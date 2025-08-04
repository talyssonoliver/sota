# Quick Tests (Parallel) - PowerShell Runner
Write-Host "🧪 Quick Tests (Parallel) - PowerShell Runner" -ForegroundColor Cyan
Set-Location $PSScriptRoot
python tests\enhanced_test_runner.py --quick --verbose
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed!" -ForegroundColor Red
}
Read-Host "Press Enter to continue..."
