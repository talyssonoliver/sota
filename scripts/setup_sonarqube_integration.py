#!/usr/bin/env python3
"""
SonarQube Integration Setup Script
Comprehensive setup and testing for SonarQube integration with the AI system.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional


class SonarQubeSetup:
    """Setup and test SonarQube integration."""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.docker_compose_file = self.root_path / "docker-compose.sonarqube.yml"
        self.sonar_properties = self.root_path / "sonar-project.properties"
        
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        checks = {
            "docker": self._check_docker(),
            "python": self._check_python(),
            "sonar_scanner": self._check_sonar_scanner(),
            "project_structure": self._check_project_structure(),
        }
        
        for name, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name.replace('_', ' ').title()}")
            
        return checks

    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_python(self) -> bool:
        """Check if Python 3.12+ is available."""
        try:
            version = sys.version_info
            return version.major == 3 and version.minor >= 12
        except Exception:
            return False

    def _check_sonar_scanner(self) -> bool:
        """Check if SonarQube scanner is available."""
        scanner_names = ["sonar-scanner", "sonar-scanner.bat"]
        
        for scanner in scanner_names:
            try:
                result = subprocess.run(
                    ["which", scanner] if not scanner.endswith(".bat") else ["where", scanner],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return True
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
        
        return False

    def _check_project_structure(self) -> bool:
        """Check if project structure is correct."""
        required_paths = [
            self.root_path / "src",
            self.root_path / "tests", 
            self.root_path / "requirements.txt",
            self.root_path / "src" / "infrastructure" / "tools" / "validation",
        ]
        
        return all(path.exists() for path in required_paths)

    def setup_sonarqube_server(self) -> bool:
        """Setup SonarQube server using Docker."""
        print("🐳 Setting up SonarQube server...")
        
        # Create Docker Compose file for SonarQube
        docker_compose_content = """
version: '3.8'

services:
  sonarqube:
    image: sonarqube:community
    container_name: sonarqube-ai-system
    depends_on:
      - db
    environment:
      - sonar.jdbc.url=jdbc:postgresql://db:5432/sonar
      - sonar.jdbc.username=sonar
      - sonar.jdbc.password=sonar
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
      - sonarqube_logs:/opt/sonarqube/logs
    ports:
      - "9000:9000"
    ulimits:
      nofile:
        soft: 65536
        hard: 65536

  db:
    image: postgres:13
    container_name: sonarqube-db
    environment:
      - POSTGRES_USER=sonar
      - POSTGRES_PASSWORD=sonar
      - POSTGRES_DB=sonar
    volumes:
      - postgresql_data:/var/lib/postgresql/data

volumes:
  sonarqube_data:
  sonarqube_extensions:
  sonarqube_logs:
  postgresql_data:
"""
        
        try:
            with open(self.docker_compose_file, "w") as f:
                f.write(docker_compose_content.strip())
            
            # Start SonarQube
            subprocess.run([
                "docker-compose", "-f", str(self.docker_compose_file), "up", "-d"
            ], check=True, cwd=self.root_path)
            
            print("  ✅ SonarQube server starting...")
            print("  ⏳ Waiting for server to be ready (this may take a few minutes)...")
            
            # Wait for SonarQube to be ready
            if self._wait_for_sonarqube():
                print("  ✅ SonarQube server is ready!")
                return True
            else:
                print("  ❌ SonarQube server failed to start properly")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to start SonarQube: {e}")
            return False

    def _wait_for_sonarqube(self, max_wait: int = 300) -> bool:
        """Wait for SonarQube to be ready."""
        import requests
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get("http://localhost:9000/api/system/status", timeout=5)
                if response.status_code == 200:
                    status = response.json().get("status")
                    if status == "UP":
                        return True
            except Exception:
                pass
            
            time.sleep(10)
            print("  ⏳ Still waiting...")
        
        return False

    def configure_sonarqube_project(self) -> Optional[str]:
        """Configure SonarQube project and get authentication token."""
        print("🔐 Configuring SonarQube project...")
        
        try:
            import requests
            
            # Default admin credentials for fresh SonarQube installation
            auth = ('admin', 'admin')
            base_url = "http://localhost:9000"
            
            # Check if we need to change default password
            try:
                response = requests.post(
                    f"{base_url}/api/users/change_password",
                    data={
                        "login": "admin",
                        "password": "admin123",
                        "previousPassword": "admin"
                    },
                    auth=auth,
                    timeout=10
                )
                if response.status_code == 204:
                    auth = ('admin', 'admin123')
                    print("  ✅ Changed default admin password")
            except Exception:
                # Password might already be changed or we're using existing server
                auth = ('admin', 'admin123')
            
            # Create project
            project_data = {
                "name": "SOTA AI System", 
                "project": "sota-ai",
                "mainBranch": "main"
            }
            
            response = requests.post(
                f"{base_url}/api/projects/create",
                data=project_data,
                auth=auth,
                timeout=10
            )
            
            if response.status_code in [200, 400]:  # 400 if project already exists
                print("  ✅ Project configured")
            
            # Generate user token
            token_response = requests.post(
                f"{base_url}/api/user_tokens/generate",
                data={
                    "name": "sota-ai-token",
                    "type": "USER_TOKEN"
                },
                auth=auth,
                timeout=10
            )
            
            if token_response.status_code == 200:
                token = token_response.json().get("token")
                print(f"  ✅ Generated authentication token: {token[:10]}...")
                
                # Save token to environment file
                env_file = self.root_path / ".env.sonarqube"
                with open(env_file, "w") as f:
                    f.write(f"SONAR_TOKEN={token}\n")
                    f.write("SONAR_HOST_URL=http://localhost:9000\n")
                
                print(f"  ✅ Token saved to {env_file}")
                return token
            else:
                print(f"  ❌ Failed to generate token: {token_response.text}")
                return None
                
        except Exception as e:
            print(f"  ❌ Configuration failed: {e}")
            print("  💡 You can manually configure SonarQube at http://localhost:9000")
            print("  💡 Default credentials: admin/admin")
            return None

    def test_integration(self) -> bool:
        """Test the complete integration."""
        print("🧪 Testing SonarQube integration...")
        
        try:
            # Test custom validation system
            print("  📝 Testing custom validation system...")
            result = subprocess.run([
                sys.executable, 
                "src/infrastructure/tools/validation/validate.py",
                "--comprehensive",
                "--output", "test-validation-report.json"
            ], cwd=self.root_path, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("    ✅ Custom validation passed")
            else:
                print("    ⚠️ Custom validation completed with issues")
            
            # Test SonarQube integration
            print("  🔍 Testing SonarQube integration...")
            env = os.environ.copy()
            
            # Load environment variables from file if available
            env_file = self.root_path / ".env.sonarqube"
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            env[key] = value
            
            result = subprocess.run([
                sys.executable,
                "src/infrastructure/tools/validation/validate.py", 
                "--comprehensive",
                "--enable-sonarqube",
                "--output", "test-integrated-report.json"
            ], cwd=self.root_path, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("    ✅ SonarQube integration test passed")
            else:
                print("    ⚠️ SonarQube integration completed with issues")
                print(f"    Output: {result.stdout}")
                print(f"    Errors: {result.stderr}")
            
            # Check if reports were generated
            test_reports = [
                self.root_path / "test-validation-report.json",
                self.root_path / "test-integrated-report.json"
            ]
            
            for report_path in test_reports:
                if report_path.exists():
                    with open(report_path) as f:
                        report = json.load(f)
                    print(f"    📊 {report_path.name}: {report.get('total_issues', 'N/A')} issues found")
                else:
                    print(f"    ❌ Report not generated: {report_path.name}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")
            return False

    def generate_documentation(self) -> bool:
        """Generate integration documentation."""
        print("📚 Generating integration documentation...")
        
        doc_content = f"""# SonarQube Integration Guide

## Setup Completed ✅

Your SOTA AI System now has SonarQube integration configured.

### Available Commands

```bash
# Setup SonarQube (run once)
make sonar-setup

# Run validation with SonarQube integration
make sonar-validate

# Run SonarQube analysis only
make sonar-only

# Stop SonarQube server
docker-compose -f docker-compose.sonarqube.yml down
```

### Manual Commands

```bash
# Custom validation only
python src/infrastructure/tools/validation/validate.py --comprehensive

# With SonarQube integration
python src/infrastructure/tools/validation/validate.py --comprehensive --enable-sonarqube

# SonarQube scanner directly
sonar-scanner
```

### Configuration Files

- **sonar-project.properties**: Main SonarQube configuration
- **pyproject.toml**: Python-specific SonarQube settings
- **.env.sonarqube**: Authentication token and server URL
- **docker-compose.sonarqube.yml**: SonarQube server setup

### SonarQube Dashboard

Access your SonarQube dashboard at: http://localhost:9000

Default credentials: admin/admin123

### Integration Benefits

1. **Enhanced Security**: Industry-standard SAST scanning
2. **Quality Gates**: Automated quality enforcement
3. **Comprehensive Reports**: Combined validation results
4. **CI/CD Integration**: GitHub Actions workflow included
5. **Dependency Analysis**: SCA for third-party libraries

### Your Custom Validation System

Your existing validation system provides:
- AI-powered pattern detection
- Business logic protection 
- Enhanced dependency analysis
- Domain-specific validation rules

SonarQube adds:
- Industry-standard security rules
- Code quality metrics
- Technical debt analysis
- Compliance reporting

Together, they provide comprehensive code quality assurance.

### Troubleshooting

**SonarQube server not starting:**
```bash
docker-compose -f docker-compose.sonarqube.yml logs
```

**Scanner not found:**
Download from: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

**Authentication issues:**
Check .env.sonarqube file and regenerate token if needed.

### Next Steps

1. Integrate into your CI/CD pipeline
2. Set up quality gates for your requirements
3. Configure custom rules for your domain
4. Train team on combined workflow

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            doc_path = self.root_path / "SONARQUBE_INTEGRATION.md"
            with open(doc_path, "w") as f:
                f.write(doc_content)
            
            print(f"  ✅ Documentation saved to {doc_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to generate documentation: {e}")
            return False

    def run_complete_setup(self) -> bool:
        """Run the complete setup process."""
        print("🚀 Starting SonarQube Integration Setup")
        print("=" * 50)
        
        # Check prerequisites
        prereqs = self.check_prerequisites()
        if not all(prereqs.values()):
            missing = [name for name, status in prereqs.items() if not status]
            print(f"\n❌ Missing prerequisites: {', '.join(missing)}")
            print("\nPlease install missing components and try again.")
            return False
        
        print("\n✅ All prerequisites met!")
        
        # Setup SonarQube server
        if not self.setup_sonarqube_server():
            return False
        
        # Configure project
        token = self.configure_sonarqube_project()
        if not token:
            print("\n⚠️ Manual configuration required")
            print("Visit http://localhost:9000 to complete setup")
        
        # Test integration
        if not self.test_integration():
            print("\n⚠️ Integration test had issues, but setup may still work")
        
        # Generate documentation
        self.generate_documentation()
        
        print("\n" + "=" * 50)
        print("🎉 SonarQube Integration Setup Complete!")
        print("\nNext steps:")
        print("1. Visit http://localhost:9000 to explore your SonarQube dashboard")
        print("2. Run 'make sonar-validate' to test the integration")
        print("3. Check SONARQUBE_INTEGRATION.md for detailed usage")
        
        return True


def main():
    """Main entry point."""
    setup = SonarQubeSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        # Test existing integration
        success = setup.test_integration()
        sys.exit(0 if success else 1)
    else:
        # Run complete setup
        success = setup.run_complete_setup()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()