#!/bin/bash

# SonarQube Local Setup Script for WSL2
# Alternative to Docker-based setup

echo "🔧 Setting up SonarQube for WSL2 environment"

# Check if running in WSL
if [[ -z "$WSL_DISTRO_NAME" ]]; then
    echo "❌ This script is designed for WSL2 environments"
    exit 1
fi

# Install Java (required for SonarQube)
echo "📦 Installing Java..."
sudo apt update
sudo apt install -y openjdk-17-jdk

# Download SonarQube Community Edition
echo "📥 Downloading SonarQube Community..."
cd /tmp
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-9.9.2.77730.zip
unzip sonarqube-9.9.2.77730.zip
sudo mv sonarqube-9.9.2.77730 /opt/sonarqube
sudo chown -R $USER:$USER /opt/sonarqube

# Download SonarQube Scanner
echo "📥 Downloading SonarQube Scanner..."
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
unzip sonar-scanner-cli-4.8.0.2856-linux.zip
sudo mv sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner
sudo ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# Create SonarQube service script
echo "🔧 Creating SonarQube service..."
cat > /tmp/start-sonarqube.sh << 'EOF'
#!/bin/bash
cd /opt/sonarqube/bin/linux-x86-64
./sonar.sh start
echo "SonarQube starting at http://localhost:9000"
echo "Default credentials: admin/admin"
EOF

chmod +x /tmp/start-sonarqube.sh
sudo mv /tmp/start-sonarqube.sh /usr/local/bin/start-sonarqube

# Create project configuration
echo "📝 Creating project configuration..."
cat > sonar-project.properties << 'EOF'
# SonarQube project configuration for SOTA AI System
sonar.projectKey=sota-ai
sonar.projectName=SOTA AI System
sonar.projectVersion=1.0

# Source and test directories
sonar.sources=src
sonar.tests=tests
sonar.python.version=3.12

# Coverage reports
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml

# Exclusions
sonar.exclusions=**/*_test.py,**/test_*.py,**/tests/**,**/__pycache__/**,**/venv/**

# Language settings
sonar.sourceEncoding=UTF-8
EOF

echo "✅ SonarQube setup complete!"
echo ""
echo "Next steps:"
echo "1. Start SonarQube: start-sonarqube"
echo "2. Wait 2-3 minutes for startup"
echo "3. Visit http://localhost:9000"
echo "4. Login with admin/admin"
echo "5. Run analysis: sonar-scanner"