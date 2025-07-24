# SonarQube Community Edition Local Setup Script (PowerShell)
# ============================================================

Write-Host "🚀 Setting up SonarQube Community Edition locally..." -ForegroundColor Green

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is required but not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Stop and remove existing SonarQube container if it exists
$existingContainer = docker ps -a --filter "name=sonarqube-community" --format "{{.Names}}"
if ($existingContainer) {
    Write-Host "🔄 Removing existing SonarQube container..." -ForegroundColor Yellow
    docker stop sonarqube-community 2>$null
    docker rm sonarqube-community 2>$null
}

# Create Docker volumes for persistence
Write-Host "📁 Creating Docker volumes..." -ForegroundColor Cyan
docker volume create sonarqube_data 2>$null
docker volume create sonarqube_logs 2>$null
docker volume create sonarqube_extensions 2>$null

# Start SonarQube Community container
Write-Host "🐳 Starting SonarQube Community container..." -ForegroundColor Cyan
docker run -d `
    --name sonarqube-community `
    -p 9000:9000 `
    -v sonarqube_data:/opt/sonarqube/data `
    -v sonarqube_logs:/opt/sonarqube/logs `
    -v sonarqube_extensions:/opt/sonarqube/extensions `
    -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true `
    sonarqube:community

Write-Host "⏳ Waiting for SonarQube to start (this may take a few minutes)..." -ForegroundColor Yellow

# Wait for SonarQube to be ready
$timeout = 300
$elapsed = 0
$ready = $false

while ($elapsed -lt $timeout -and -not $ready) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9000/api/system/status" -TimeoutSec 5
        if ($response.status -eq "UP") {
            $ready = $true
        }
    } catch {
        # SonarQube not ready yet
    }
    
    if (-not $ready) {
        Start-Sleep -Seconds 5
        $elapsed += 5
        Write-Host "Still waiting..." -ForegroundColor Gray
    }
}

if (-not $ready) {
    Write-Host "❌ SonarQube failed to start within 5 minutes" -ForegroundColor Red
    Write-Host "Check logs with: docker logs sonarqube-community" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ SonarQube is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access SonarQube at: http://localhost:9000" -ForegroundColor Cyan
Write-Host "🔑 Default credentials: admin/admin (you'll be prompted to change this)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor White
Write-Host "1. Open http://localhost:9000 in your browser" -ForegroundColor White
Write-Host "2. Login with admin/admin" -ForegroundColor White
Write-Host "3. Change the default password when prompted" -ForegroundColor White
Write-Host "4. Create a project token for CI/CD" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To run analysis:" -ForegroundColor White
Write-Host "   python -m pytest --cov=src --cov-report=xml:coverage.xml tests/" -ForegroundColor Gray
Write-Host "   sonar-scanner (after installing SonarScanner CLI)" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop SonarQube:" -ForegroundColor White
Write-Host "   docker stop sonarqube-community" -ForegroundColor Gray
Write-Host ""
Write-Host "🗑️  To remove SonarQube completely:" -ForegroundColor White
Write-Host "   docker stop sonarqube-community; docker rm sonarqube-community" -ForegroundColor Gray
Write-Host "   docker volume rm sonarqube_data sonarqube_logs sonarqube_extensions" -ForegroundColor Gray
