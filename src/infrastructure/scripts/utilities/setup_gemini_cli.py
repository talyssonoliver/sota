#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    json,
    os,
    subprocess,
    sys
)
"""
Gemini CLI Setup Script
Automates the installation and configuration of Gemini CLI integration.
"""

# import json  # Consolidated to common_imports
# import os  # Consolidated to common_imports
# import subprocess  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("🔍 Checking prerequisites...")

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])

    # Check Node.js (optional for official Gemini CLI)
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js version:", result.stdout.strip())
        else:
            print("⚠️  Node.js not found (optional for official Gemini CLI)")
    except FileNotFoundError:
        print("⚠️  Node.js not found (optional for official Gemini CLI)")

    return True


def install_dependencies():
    """Install required Python dependencies."""
    print("\n📦 Installing Python dependencies...")

    dependencies = [
        "langchain-google-genai>=2.0.6",
        "google-generativeai>=0.8.3",
    ]

    for dep in dependencies:
        print(f"Installing {dep}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dep],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ {dep} installed successfully")
        else:
            print(f"❌ Failed to install {dep}")
            print(result.stderr)
            return False

    return True


def setup_configuration():
    """Setup configuration files."""
    print("\n⚙️  Setting up configuration...")

    config_dir = Path("config")
    config_file = config_dir / "gemini_config.json"

    if config_file.exists():
        print(f"✅ Configuration file already exists: {config_file}")
        return True

    # Create configuration directory if it doesn't exist
    config_dir.mkdir(exist_ok=True)

    # Default configuration
    default_config = {
        "model": "gemini-2.0-flash-lite",
        "temperature": 0.7,
        "max_tokens": 8192,
        "system_instruction": "You are an AI assistant integrated with a sophisticated multi-agent system.",
        "tools_enabled": True,
        "mcp_integration": True,
        "langgraph_integration": True,
        "project_context": {
            "architecture": "Multi-Agent System with LangChain, LangGraph, CrewAI",
            "memory_engine": "ChromaDB with AES-256 encryption",
            "patterns": [
                "Clean Architecture",
                "DDD",
                "Hexagonal Architecture",
            ],
        },
    }

    try:
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Configuration file created: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False


def setup_api_key():
    """Guide user through API key setup."""
    print("\n🔑 Setting up API key...")

    if os.getenv("GEMINI_API_KEY"):
        print("✅ GEMINI_API_KEY environment variable is already set")
        return True

    print("📋 To use Gemini CLI, you need to set up your API key:")
    print("1. Visit https://ai.google.dev/ to get your API key")
    print("2. Set the environment variable:")
    print("   Windows: set GEMINI_API_KEY=your-key-here")
    print("   Linux/Mac: export GEMINI_API_KEY=your-key-here")
    print("3. Or add it to your .env file:")
    print("   echo 'GEMINI_API_KEY=your-key-here' >> .env")

    return True


def install_official_gemini_cli():
    """Install the official Gemini CLI (optional)."""
    print("\n🌟 Installing official Gemini CLI (optional)...")

    try:
        # Check if npm is available
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  npm not found. Skipping official Gemini CLI installation.")
            return True

        print("Installing @google/gemini-cli globally...")
        result = subprocess.run(
            ["npm", "install", "-g", "@google/gemini-cli"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Official Gemini CLI installed successfully")
            print("   You can now use 'gemini' command globally")
        else:
            print("⚠️  Failed to install official Gemini CLI")
            print("   You can install it manually: npm install -g @google/gemini-cli")

    except FileNotFoundError:
        print("⚠️  npm not found. Skipping official Gemini CLI installation.")

    return True


def run_tests():
    """Run basic tests to verify installation."""
    print("\n🧪 Running basic tests...")

    try:
        # Test import
        sys.path.insert(0, str(Path.cwd()))
        from src.interfaces.cli.gemini_cli import GeminiCLI

        # Create CLI instance
        cli = GeminiCLI()
        print("✅ GeminiCLI import and initialization successful")

        # Test tools
        if len(cli.tools) >= 3:
            print(f"✅ Tools loaded successfully: {len(cli.tools)} tools available")
        else:
            print(f"⚠️  Expected at least 3 tools, found {len(cli.tools)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    print("# Interactive chat session")
    print("python src/interfaces/cli/gemini_cli.py chat")
    print()
    print("# Process a file")
    print("python src/interfaces/cli/gemini_cli.py process README.md 'Summarize this'")
    print()
    print("# Analyze codebase")
    print(
        "python src/interfaces/cli/gemini_cli.py analyze ./src --output analysis.json"
    )
    print()
    print("# Generate code")
    print(
        "python src/interfaces/cli/gemini_cli.py generate 'Create a new agent' --output agent.py"
    )
    print()
    print("# Setup configuration")
    print("python src/interfaces/cli/gemini_cli.py config --init")


def main():
    """Main setup function."""
    print("🚀 Gemini CLI Setup")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please fix the issues and try again.")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies.")
        sys.exit(1)

    # Setup configuration
    if not setup_configuration():
        print("❌ Failed to setup configuration.")
        sys.exit(1)

    # Setup API key
    setup_api_key()

    # Install official Gemini CLI (optional)
    install_official_gemini_cli()

    # Run tests
    if not run_tests():
        print("❌ Tests failed. Please check the installation.")
        sys.exit(1)

    print("\n🎉 Gemini CLI setup completed successfully!")
    print("=" * 50)

    # Show usage examples
    show_usage_examples()


if __name__ == "__main__":
    main()
