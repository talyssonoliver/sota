#!/bin/bash

# SonarQube Community Edition Local Setup Script
# ===============================================

set -e

echo "🚀 Setting up SonarQube Community Edition locally..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Stop and remove existing SonarQube container if it exists
if docker ps -a | grep -q sonarqube-community; then
    echo "🔄 Removing existing SonarQube container..."
    docker stop sonarqube-community || true
    docker rm sonarqube-community || true
fi

# Create Docker volumes for persistence
echo "📁 Creating Docker volumes..."
docker volume create sonarqube_data || true
docker volume create sonarqube_logs || true
docker volume create sonarqube_extensions || true

# Start SonarQube Community container
echo "🐳 Starting SonarQube Community container..."
docker run -d \
    --name sonarqube-community \
    -p 9000:9000 \
    -v sonarqube_data:/opt/sonarqube/data \
    -v sonarqube_logs:/opt/sonarqube/logs \
    -v sonarqube_extensions:/opt/sonarqube/extensions \
    -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
    sonarqube:community

echo "⏳ Waiting for SonarQube to start (this may take a few minutes)..."

# Wait for SonarQube to be ready
timeout 300 bash -c 'until curl -s http://localhost:9000/api/system/status | grep -q "UP"; do sleep 5; echo "Still waiting..."; done' || {
    echo "❌ SonarQube failed to start within 5 minutes"
    echo "Check logs with: docker logs sonarqube-community"
    exit 1
}

echo "✅ SonarQube is ready!"
echo ""
echo "🌐 Access SonarQube at: http://localhost:9000"
echo "🔑 Default credentials: admin/admin (you'll be prompted to change this)"
echo ""
echo "📋 Next steps:"
echo "1. Open http://localhost:9000 in your browser"
echo "2. Login with admin/admin"
echo "3. Change the default password when prompted"
echo "4. Create a project token for CI/CD"
echo ""
echo "🔧 To run analysis:"
echo "   python -m pytest --cov=src --cov-report=xml:coverage.xml tests/"
echo "   sonar-scanner (after installing SonarScanner CLI)"
echo ""
echo "🛑 To stop SonarQube:"
echo "   docker stop sonarqube-community"
echo ""
echo "🗑️  To remove SonarQube completely:"
echo "   docker stop sonarqube-community && docker rm sonarqube-community"
echo "   docker volume rm sonarqube_data sonarqube_logs sonarqube_extensions"
