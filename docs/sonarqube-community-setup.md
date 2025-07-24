# SonarQube Community Edition Setup

This project has been configured to work with SonarQube Community Edition, which provides essential code quality analysis features without requiring a commercial license.

## What's Included in Community Edition

✅ **Available Features:**
- Code quality analysis (bugs, code smells, vulnerabilities)
- Basic security hotspot detection
- Code duplication detection
- Test coverage tracking
- Basic quality gates
- Python language support
- Integration with external tools (Bandit, etc.)

❌ **Premium Features Removed:**
- Advanced security rules
- Branch analysis (requires Developer Edition)
- Pull request decoration (requires Developer Edition)
- Portfolio management
- Advanced reporting

## Local Development Setup

### Option 1: Docker (Recommended)
```bash
# Run SonarQube Community in Docker
docker run -d --name sonarqube -p 9000:9000 sonarqube:community

# Wait for startup (may take a few minutes)
# Access at http://localhost:9000
# Default credentials: admin/admin (change on first login)
```

### Option 2: Manual Installation
1. Download SonarQube Community Edition from https://www.sonarqube.org/downloads/
2. Extract and run `bin/[OS]/sonar.sh start`
3. Access at http://localhost:9000

## GitHub Actions Integration

The workflow (`.github/workflows/sonarqube-analysis.yml`) automatically:
1. Starts a SonarQube Community container
2. Configures the project
3. Runs your custom validation system
4. Generates test coverage
5. Performs SonarQube analysis
6. Checks basic quality gates

## Configuration Files

- `sonar-project.properties`: Main SonarQube configuration
- `sonarqube_integration_config.json`: Integration settings for your custom validation system
- `.github/workflows/sonarqube-analysis.yml`: CI/CD workflow

## Manual Analysis

To run analysis locally:

```bash
# Install SonarScanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
unzip sonar-scanner-cli-4.8.0.2856-linux.zip

# Run analysis
./sonar-scanner-4.8.0.2856-linux/bin/sonar-scanner \
  -Dsonar.projectKey=sota-ai-system \
  -Dsonar.sources=src \
  -Dsonar.tests=tests \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN
```

## Upgrading to Premium Features

If you later need premium features:
1. Purchase SonarQube Developer/Enterprise Edition
2. Update `sonar-project.properties` to include organization settings
3. Configure branch analysis and PR decoration
4. Update the GitHub workflow to use SonarCloud or your hosted instance

## Troubleshooting

### Common Issues:
1. **Port 9000 already in use**: Change the port mapping in docker run
2. **Analysis fails**: Check SonarQube logs for detailed error messages
3. **Quality gate fails**: Review the issues in the SonarQube UI

### Getting Help:
- SonarQube Community: https://community.sonarsource.com/
- Documentation: https://docs.sonarqube.org/latest/
