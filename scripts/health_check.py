#!/usr/bin/env python3
"""
Comprehensive Health Check for AI System
Checks all critical components and dependencies
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"

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
        return {"error": "Tasks directory not found"}
    
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
    key_files = ["main.py", "orchestration/execute_task.py", "orchestration/execute_workflow.py"]
    for file in key_files:
        if Path(file).exists():
            try:
                with open(file, "r") as f:
                    compile(f.read(), file, "exec")
            except SyntaxError as e:
                issues["syntax_errors"].append(f"{file}: {e}")
    
    return issues

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
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    critical_issues = []
    warnings = []
    
    if not py_ok:
        critical_issues.append("Python version too old")
    
    if not files.get(".env"):
        warnings.append(".env file missing (copy from .env.template)")
    
    if env_vars.get("OPENAI_API_KEY") in ["Test key (invalid for API calls)", "Invalid format", "Not set"]:
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
    
    print("=" * 60)

if __name__ == "__main__":
    main()