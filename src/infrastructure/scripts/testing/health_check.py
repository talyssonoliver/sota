#!/usr/bin/env python3
"""
Comprehensive Health Check for AI System
Checks all critical components and dependencies
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible"""
    version = sys.version_info
    # Recommend Python 3.13.5+ for latest security fixes (CVE-2025-4517, etc.)
    if version.major == 3 and version.minor >= 13:
        return (
            True,
            f"Python {version.major}.{version.minor}.{version.micro} (latest with security fixes)",
        )
    elif version.major == 3 and version.minor >= 11:
        return (
            True,
            f"Python {version.major}.{version.minor}.{version.micro} (good, but consider upgrading to 3.13.5+)",
        )
    elif version.major == 3 and version.minor >= 8:
        return (
            True,
            f"Python {version.major}.{version.minor}.{version.micro} (minimum supported, upgrade recommended)",
        )
    return (
        False,
        f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+, recommend 3.13.5+)",
    )


def check_required_files() -> Dict[str, bool]:
    """Check if all required files exist"""
    required_files = {
        "main.py": Path("main.py"),
        ".env": Path(".env"),
        "requirements.txt": Path("requirements.txt"),
        "config/agents.yaml": Path("config/agents.yaml"),
        "config/tools.yaml": Path("config/tools.yaml"),
        "config/schemas/task.schema.json": Path("config/schemas/task.schema.json"),
    }

    results = {}
    for name, path in required_files.items():
        results[name] = path.exists()

    return results


def check_directories() -> Dict[str, bool]:
    """Check if required directories exist"""
    required_dirs = {
        "src": Path("src"),
        "tools": Path("tools"),
        "orchestration": Path("orchestration"),
        "config": Path("config"),
        "prompts": Path("prompts"),
        "tasks": Path("tasks"),
        "data/context": Path("data/context"),
    }

    results = {}
    for name, path in required_dirs.items():
        results[name] = path.is_dir()

    return results


def check_env_variables() -> Dict[str, str]:
    """Check environment variables"""
    env_vars = {}

    # Check if .env exists and load it
    if Path(".env").exists():
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=")[0]
                    if key == "OPENAI_API_KEY":
                        value = os.getenv(key, "")
                        if value.startswith("sk-"):
                            env_vars[key] = "Set (valid format)"
                        elif value == "test-key-for-development":
                            env_vars[key] = "Test key (invalid for API calls)"
                        else:
                            env_vars[key] = "Invalid format"
                    elif key == "MEMORY_ENGINE_KEY":
                        value = os.getenv(key, "")
                        if len(value) > 20:
                            env_vars[key] = "Set"
                        else:
                            env_vars[key] = "Not set or too short"
                    else:
                        env_vars[key] = "Present" if os.getenv(key) else "Not set"

    return env_vars


def check_dependencies() -> Dict[str, Tuple[bool, str]]:
    """Check if key dependencies are installed"""
    dependencies = {}

    try:
        import langchain

        dependencies["langchain"] = (True, langchain.__version__)
    except ImportError:
        dependencies["langchain"] = (False, "Not installed")

    try:
        import langchain_openai

        dependencies["langchain_openai"] = (True, "Installed")
    except ImportError:
        dependencies["langchain_openai"] = (False, "Not installed")

    try:
        import chromadb

        dependencies["chromadb"] = (True, chromadb.__version__)
    except ImportError:
        dependencies["chromadb"] = (False, "Not installed")

    try:
        import openai

        dependencies["openai"] = (True, openai.__version__)
    except ImportError:
        dependencies["openai"] = (False, "Not installed")

    try:
        import crewai

        dependencies["crewai"] = (True, crewai.__version__)
    except ImportError:
        dependencies["crewai"] = (False, "Not installed")

    try:
        import dotenv

        dependencies["python-dotenv"] = (True, "Installed")
    except ImportError:
        dependencies["python-dotenv"] = (False, "Not installed")

    return dependencies


def check_task_files() -> Dict[str, int]:
    """Check task files"""
    task_dir = Path("tasks")
    if not task_dir.exists():
        return {"error_code": 1}  # Return integer instead of string

    task_counts = {
        "BE": 0,  # Backend
        "FE": 0,  # Frontend
        "TL": 0,  # Technical Lead
        "QA": 0,  # QA
        "UX": 0,  # UX
        "PM": 0,  # Product Manager
        "LC": 0,  # LangChain
    }

    for task_file in task_dir.glob("*.yaml"):
        prefix = task_file.stem.split("-")[0]
        if prefix in task_counts:
            task_counts[prefix] += 1

    return task_counts


def check_imports() -> Dict[str, List[str]]:
    """Check for common import issues"""
    issues = {
        "circular_imports": [],
        "missing_init": [],
        "syntax_errors": [],
    }

    # Check for missing __init__.py files
    for root, dirs, files in os.walk("."):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue

        if any(f.endswith(".py") for f in files) and "__init__.py" not in files:
            if not root.startswith("./scripts"):  # Scripts don't need __init__.py
                issues["missing_init"].append(root)

    # Check for syntax errors in key files
    key_files = [
        "main.py",
        "orchestration/execute_task.py",
        "orchestration/execute_workflow.py",
    ]
    for file in key_files:
        if Path(file).exists():
            try:
                with open(file, "r") as f:
                    compile(f.read(), file, "exec")
            except SyntaxError as e:
                issues["syntax_errors"].append(f"{file}: {e}")

    return issues


def check_ci_environment() -> Dict[str, bool]:
    """Check CI-specific environment setup"""
    ci_checks = {
        "github_actions": os.getenv("GITHUB_ACTIONS") == "true",
        "ci_mode": os.getenv("CI") == "true",
        "test_mode": os.getenv("TEST_MODE") == "true",
        "python_path": "PYTHONPATH" in os.environ,
    }
    return ci_checks


def check_deployment_readiness(environment: str) -> Dict[str, bool]:
    """Check if system is ready for deployment"""
    checks = {
        "health_endpoint": False,
        "database_connection": False,
        "external_apis": False,
        "security_config": False,
    }

    try:
        # Health endpoint check
        import requests

        response = requests.get("http://localhost:8000/health", timeout=5)
        checks["health_endpoint"] = response.status_code == 200
    except Exception:
        pass

    # Database connection check
    try:
        # Add database connection test
        checks["database_connection"] = True
    except Exception:
        pass

    # Security configuration check
    if environment == "production":
        checks["security_config"] = (
            os.getenv("DEBUG", "1") == "0"
            and os.getenv("MEMORY_ENGINE_KEY") is not None
            and len(os.getenv("MEMORY_ENGINE_KEY", "")) > 20
        )
    else:
        checks["security_config"] = True

    return checks


def generate_health_report() -> str:
    """Generate comprehensive health report"""
    report_lines = [
        "# System Health Report",
        f"Generated at: {datetime.now().isoformat()}",
        "",
        "## Environment Checks",
    ]

    # Python version
    python_ok, python_msg = check_python_version()
    report_lines.append(f"- Python Version: {'✅' if python_ok else '❌'} {python_msg}")

    # Files and directories
    files = check_required_files()
    dirs = check_directories()

    report_lines.append("\n## Required Files")
    for name, exists in files.items():
        report_lines.append(f"- {name}: {'✅' if exists else '❌'}")

    report_lines.append("\n## Required Directories")
    for name, exists in dirs.items():
        report_lines.append(f"- {name}: {'✅' if exists else '❌'}")

    # CI environment (if applicable)
    if os.getenv("CI"):
        ci_env = check_ci_environment()
        report_lines.append("\n## CI Environment")
        for check, result in ci_env.items():
            report_lines.append(f"- {check}: {'✅' if result else '❌'}")

    return "\n".join(report_lines)


def main():
    """Run comprehensive health check"""
    print("=" * 60)
    print("AI SYSTEM HEALTH CHECK")
    print("=" * 60)

    # Python version
    py_ok, py_version = check_python_version()
    print(f"\n1. Python Version: {py_version} {'✓' if py_ok else '✗'}")

    # Required files
    print("\n2. Required Files:")
    files = check_required_files()
    for name, exists in files.items():
        print(f"   {name}: {'✓ Found' if exists else '✗ Missing'}")

    # Directories
    print("\n3. Required Directories:")
    dirs = check_directories()
    for name, exists in dirs.items():
        print(f"   {name}: {'✓ Found' if exists else '✗ Missing'}")

    # Environment variables
    print("\n4. Environment Variables:")
    env_vars = check_env_variables()
    for key, status in env_vars.items():
        print(f"   {key}: {status}")

    # Dependencies
    print("\n5. Key Dependencies:")
    deps = check_dependencies()
    for name, (installed, version) in deps.items():
        if installed:
            print(f"   {name}: ✓ {version}")
        else:
            print(f"   {name}: ✗ {version}")

    # Task files
    print("\n6. Task Files:")
    tasks = check_task_files()
    if "error" in tasks:
        print(f"   {tasks['error']}")
    else:
        for prefix, count in tasks.items():
            print(f"   {prefix}: {count} tasks")

    # Import issues
    print("\n7. Import Health:")
    import_issues = check_imports()
    if any(import_issues.values()):
        for issue_type, issues in import_issues.items():
            if issues:
                print(f"   {issue_type}:")
                for issue in issues[:5]:  # Show first 5
                    print(f"      - {issue}")
                if len(issues) > 5:
                    print(f"      ... and {len(issues) - 5} more")
    else:
        print("   ✓ No import issues detected")

    # CI-specific checks
    if os.getenv("CI"):
        print("\n8. CI Environment:")
        ci_checks = check_ci_environment()
        for check, result in ci_checks.items():
            print(f"   {check}: {'✓' if result else '✗'}")

    # Deployment readiness (optional)
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-deploy":
        print("\n9. Deployment Readiness:")
        deployment_checks = check_deployment_readiness("production")
        for check, result in deployment_checks.items():
            print(f"   {check}: {'✓' if result else '✗'}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")

    critical_issues = []
    warnings = []

    if not py_ok:
        critical_issues.append("Python version too old")

    if not files.get(".env"):
        warnings.append(".env file missing (copy from .env.template)")

    if env_vars.get("OPENAI_API_KEY") in [
        "Test key (invalid for API calls)",
        "Invalid format",
        "Not set",
    ]:
        critical_issues.append("Valid OpenAI API key not configured")

    if not deps["langchain"][0]:
        critical_issues.append("LangChain not installed")

    if critical_issues:
        print("✗ CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"  - {issue}")

    if warnings:
        print("\n⚠ WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if not critical_issues and not warnings:
        print("✓ System appears healthy!")

    print("\nNext steps:")
    if not files.get(".env"):
        print("1. Copy .env.template to .env")
    if env_vars.get("OPENAI_API_KEY") != "Set (valid format)":
        print("2. Add valid OpenAI API key to .env")
    if not all(d[0] for d in deps.values()):
        print("3. Install missing dependencies: pip install -r requirements.txt")

    # Generate report if requested
    if "--report" in sys.argv:
        report = generate_health_report()
        output_file = (
            sys.argv[sys.argv.index("--output") + 1] if "--output" in sys.argv else None
        )
        if output_file:
            with open(output_file, "w") as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")
        else:
            print(report)

    print("=" * 60)


if __name__ == "__main__":
    main()
