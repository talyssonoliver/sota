# HITL Dashboard Startup Script
# Starts the HITL Kanban board dashboard with proper dependency handling

param(
    [string]$Host = "localhost",
    [int]$Port = 8080,
    [switch]$Demo = $false,
    [switch]$Background = $false
)

Write-Host "🔄 HITL Kanban Dashboard Startup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the right directory
$CurrentDir = Get-Location
if (-not (Test-Path "dashboard\hitl_kanban_demo.py")) {
    Write-Host "❌ Error: Please run this script from the ai-system root directory" -ForegroundColor Red
    Write-Host "Current directory: $CurrentDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 Working directory: $CurrentDir" -ForegroundColor Green

# Check Python availability
try {
    $PythonVersion = python --version 2>&1
    Write-Host "🐍 Python version: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python." -ForegroundColor Red
    exit 1
}

# Install required packages if missing
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

$RequiredPackages = @("flask", "flask-cors", "rich")
foreach ($Package in $RequiredPackages) {
    try {
        python -c "import $($Package.Replace('-', '_'))" 2>$null
        Write-Host "✅ $Package - installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  $Package - missing, installing..." -ForegroundColor Yellow
        pip install $Package
    }
}

# Start the appropriate dashboard
if ($Demo) {
    Write-Host "🎮 Starting Demo Dashboard..." -ForegroundColor Cyan
    Write-Host "URL: http://$($Host):$Port/demo" -ForegroundColor Yellow
    
    if ($Background) {
        Start-Process python -ArgumentList "dashboard\unified_api_server.py", "--host", $Host, "--port", $Port -WindowStyle Hidden
        Write-Host "🚀 Dashboard started in background" -ForegroundColor Green
        Write-Host "Access at: http://$($Host):$Port" -ForegroundColor Yellow
    } else {
        python dashboard\unified_api_server.py --host $Host --port $Port
    }
} else {
    Write-Host "🔄 Starting HITL Kanban Dashboard..." -ForegroundColor Cyan
    
    # Try the full dashboard first, fall back to demo if components missing
    Write-Host "Testing dashboard components..." -ForegroundColor Yellow
    $TestResult = python -c "
try:
    from dashboard.hitl_widgets import HITLDashboardManager
    print('FULL')
except:
    print('DEMO')
" 2>$null

    if ($TestResult -eq "FULL") {
        Write-Host "✅ Full dashboard components available" -ForegroundColor Green
        Write-Host "🌐 Starting full dashboard at http://$($Host):$Port" -ForegroundColor Yellow
        
        if ($Background) {
            Start-Process python -ArgumentList "dashboard\unified_api_server.py", "--host", $Host, "--port", $Port -WindowStyle Hidden
            Write-Host "🚀 Dashboard started in background" -ForegroundColor Green
        } else {
            python dashboard\unified_api_server.py --host $Host --port $Port
        }
    } else {
        Write-Host "⚠️  Some dashboard components missing, using demo mode" -ForegroundColor Yellow
        Write-Host "🎮 Starting demo dashboard at http://$($Host):$Port/demo" -ForegroundColor Yellow
        
        if ($Background) {
            Start-Process python -ArgumentList "dashboard\unified_api_server.py", "--host", $Host, "--port", $Port -WindowStyle Hidden
            Write-Host "🚀 Demo dashboard started in background" -ForegroundColor Green
        } else {
            python dashboard\unified_api_server.py --host $Host --port $Port
        }
    }
}

Write-Host ""
Write-Host "📊 Dashboard Features:" -ForegroundColor Cyan
Write-Host "  • Kanban-style HITL review board" -ForegroundColor White
Write-Host "  • Real-time status updates" -ForegroundColor White
Write-Host "  • Priority-based sorting" -ForegroundColor White
Write-Host "  • Deadline tracking with overdue alerts" -ForegroundColor White
Write-Host "  • One-click approval actions" -ForegroundColor White
Write-Host "  • Live updates from pending_reviews/ and feedback_logs/" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Available URLs:" -ForegroundColor Cyan
Write-Host "  • Main Dashboard: http://$($Host):$Port/" -ForegroundColor White
Write-Host "  • Demo Page: http://$($Host):$Port/demo" -ForegroundColor White
Write-Host "  • API Status: http://$($Host):$Port/api/hitl/status" -ForegroundColor White
Write-Host "  • Kanban Data: http://$($Host):$Port/api/hitl/kanban-data" -ForegroundColor White
