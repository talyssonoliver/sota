
from src.infrastructure.utils.common_imports import Path, subprocess, sys
"""
Tool Installation and Detection System
Automatically detects and installs missing validation tools.
"""

# import subprocess  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, List, Optional, Tuple


class ToolInstaller:
    """Handles automatic detection and installation of validation tools."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize tool installer."""
        self.root_path = root_path or Path.cwd()
        self.required_tools = {
            "black": {
                "command": "black",
                "package": "black",
                "test_args": ["--version"],
                "description": "Code formatting tool",
            },
            "ruff": {
                "command": "ruff",
                "package": "ruff",
                "test_args": ["--version"],
                "description": "Fast Python linter",
            },
            "mypy": {
                "command": "mypy",
                "package": "mypy",
                "test_args": ["--version"],
                "description": "Static type checker",
            },
            "bandit": {
                "command": "bandit",
                "package": "bandit",
                "test_args": ["--version"],
                "description": "Security vulnerability scanner",
            },
            "sonar-scanner": {
                "command": "sonar-scanner",
                "package": None,  # Not pip installable
                "test_args": ["--version"],
                "description": "SonarQube scanner (manual installation required)",
            },
        }

    def detect_tools(self) -> Dict[str, bool]:
        """Detect which tools are available."""
        tool_status = {}

        print("🔍 Detecting available validation tools...")

        for tool_name, tool_config in self.required_tools.items():
            is_available = self._check_tool_available(tool_name, tool_config)
            tool_status[tool_name] = is_available

            status_icon = "✅" if is_available else "❌"
            print(f"   {status_icon} {tool_name}: {tool_config['description']}")

        return tool_status

    def _check_tool_available(self, tool_name: str, tool_config: Dict) -> bool:
        """Check if a specific tool is available."""
        try:
            result = subprocess.run(
                [tool_config["command"]] + tool_config["test_args"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            return False

    def install_missing_tools(
        self, tool_status: Dict[str, bool], auto_install: bool = False
    ) -> bool:
        """Install missing tools."""
        missing_tools = [
            tool for tool, available in tool_status.items() if not available
        ]

        if not missing_tools:
            print("✅ All required tools are already installed!")
            return True

        print(f"\n🔧 Found {len(missing_tools)} missing tools:")
        for tool in missing_tools:
            print(f"   - {tool}: {self.required_tools[tool]['description']}")

        if not auto_install:
            response = input(
                "\n❓ Would you like to install missing tools automatically? (y/n): "
            ).lower()
            if response not in ["y", "yes"]:
                print(
                    "⚠️  Skipping tool installation. Some validations may not work properly."
                )
                return False

        success = True
        for tool in missing_tools:
            if not self._install_tool(tool):
                success = False

        return success

    def _install_tool(self, tool_name: str) -> bool:
        """Install a specific tool."""
        tool_config = self.required_tools[tool_name]
        package = tool_config.get("package")

        if not package:
            print(
                f"⚠️  {tool_name} requires manual installation. Please install it manually."
            )
            if tool_name == "sonar-scanner":
                print(
                    "   📖 See: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
                )
            return False

        print(f"📦 Installing {tool_name}...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                print(f"   ✅ {tool_name} installed successfully!")
                return True
            else:
                print(f"   ❌ Failed to install {tool_name}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ❌ Installation of {tool_name} timed out")
            return False
        except Exception as e:
            print(f"   ❌ Error installing {tool_name}: {e}")
            return False

    def verify_installation(self) -> Tuple[bool, List[str]]:
        """Verify that all tools are properly installed."""
        print("\n🔍 Verifying tool installation...")

        tool_status = self.detect_tools()
        missing_tools = [
            tool for tool, available in tool_status.items() if not available
        ]

        if not missing_tools:
            print("✅ All validation tools are properly installed!")
            return True, []
        else:
            print(f"❌ {len(missing_tools)} tools are still missing:")
            for tool in missing_tools:
                print(f"   - {tool}")
            return False, missing_tools

    def generate_requirements_txt(self) -> str:
        """Generate requirements.txt entries for validation tools."""
        requirements = []

        for tool_name, tool_config in self.required_tools.items():
            package = tool_config.get("package")
            if package:
                requirements.append(f"{package}>=1.0.0  # {tool_config['description']}")

        return "\n".join(requirements)

    def check_tool_versions(self) -> Dict[str, str]:
        """Check versions of installed tools."""
        versions = {}

        print("\n📋 Checking tool versions...")

        for tool_name, tool_config in self.required_tools.items():
            if self._check_tool_available(tool_name, tool_config):
                version = self._get_tool_version(tool_name, tool_config)
                versions[tool_name] = version
                print(f"   {tool_name}: {version}")
            else:
                versions[tool_name] = "Not installed"
                print(f"   {tool_name}: Not installed")

        return versions

    def _get_tool_version(self, tool_name: str, tool_config: Dict) -> str:
        """Get the version of a specific tool."""
        try:
            result = subprocess.run(
                [tool_config["command"]] + tool_config["test_args"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Extract version from output
                version_line = result.stdout.strip().split("\n")[0]
                return version_line
            else:
                return "Unknown"

        except Exception:
            return "Unknown"

    def setup_validation_environment(self, auto_install: bool = False) -> bool:
        """Complete validation environment setup."""
        print("🚀 Setting up validation environment...")

        # Step 1: Detect tools
        tool_status = self.detect_tools()

        # Step 2: Install missing tools
        if not self.install_missing_tools(tool_status, auto_install):
            return False

        # Step 3: Verify installation
        success, missing_tools = self.verify_installation()

        if success:
            print("\n✅ Validation environment setup complete!")
            self.check_tool_versions()
            return True
        else:
            print(f"\n❌ Setup incomplete. Missing tools: {', '.join(missing_tools)}")
            return False

    def generate_installation_script(self) -> str:
        """Generate a shell script for tool installation."""
        script = """#!/bin/bash
# Validation Tools Installation Script
# Generated by ValidationSystemToolInstaller

echo "🚀 Installing validation tools..."

# Install Python packages
"""

        for tool_name, tool_config in self.required_tools.items():
            package = tool_config.get("package")
            if package:
                script += f'echo "📦 Installing {tool_name}..."\n'
                script += f"python -m pip install {package}\n\n"

        script += """
# Manual installations (if needed)
echo "📋 Manual installations required:"
echo "   - SonarQube Scanner: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"

echo "✅ Installation complete!"
"""

        return script
