---
sidebar_position: 3
---

# Requirements Management

This guide explains how the AI System manages Python dependencies following best practices and library documentation standards.

## Overview

The project uses a structured approach to dependency management that separates production, development, and enterprise dependencies while following each library's documented best practices.

## Installation Options

### Basic Installation (Production)

For production deployments, install only the core dependencies:

```bash
pip install -r requirements.txt
```

### Development Installation

For development work, install development tools and testing dependencies:

```bash
pip install -r requirements-dev.txt
```

### Enterprise Features

For enterprise secret management capabilities:

```bash
# Option 1: Install enterprise requirements file
pip install -r requirements-enterprise.txt

# Option 2: Use optional dependencies (if installed as package)
pip install -e .[enterprise]
```

### Full Development Setup

For complete development setup with all features:

```bash
# Install all dependencies including dev tools and enterprise features
pip install -r requirements-dev.txt -r requirements-enterprise.txt
```

## Requirements Structure

### Production Requirements (`requirements.txt`)

Contains only production dependencies with proper version constraints:

- **Core AI Framework Dependencies**
  - LangChain ecosystem (`langchain`, `langchain_openai`, `langchain_community`)
  - LangGraph for workflow orchestration
  - CrewAI for multi-agent coordination
  - OpenAI client library

- **Database and API Integrations**
  - Supabase for database operations
  - HTTP clients (`httpx`, `requests`)

- **Document Processing**
  - BeautifulSoup for HTML parsing
  - Markdown processing utilities

- **Runtime Utilities**
  - Environment management (`python-dotenv`)
  - CLI interfaces (`typer`)
  - File monitoring (`watchdog`)

### Development Requirements (`requirements-dev.txt`)

Includes production requirements plus development tools:

- **Testing Frameworks**
  - `pytest` with coverage and async support
  - Testing utilities and fixtures

- **Code Quality Tools**
  - `black` for code formatting
  - `isort` for import sorting
  - `mypy` for type checking
  - `ruff` for fast linting

- **Development Utilities**
  - `jupyterlab` for interactive development
  - `ipython` for enhanced REPL
  - Documentation tools (`sphinx`)
  - Performance profiling tools

### Enterprise Requirements (`requirements-enterprise.txt`)

Optional enterprise secret management integrations:

- **Azure Key Vault Support**
  - `azure-keyvault-secrets` for Azure secrets
  - `azure-identity` for Azure authentication

- **AWS Secrets Manager Support**
  - `boto3` for AWS SDK
  - `botocore` for AWS core functionality

- **HashiCorp Vault Support**
  - `hvac` for Vault API client

## Version Strategy

The project uses a consistent versioning strategy based on library documentation:

### Framework Packages
Use compatible version ranges to allow updates while preventing breaking changes:
```
langchain>=0.3.25,&lt;0.4.0
crewai>=0.118.0,&lt;0.119.0
```

### Security-Critical Packages
More restrictive ranges for security-sensitive dependencies:
```
openai>=1.77.0,&lt;2.0.0
```

### Stable Packages
Conservative ranges for well-established libraries:
```
requests>=2.32.3,&lt;3.0.0
```

## Python Version Requirements

### Compatibility Range
- **Minimum**: Python 3.10 (required by CrewAI)
- **Maximum**: Python 3.13 (CrewAI compatibility limit)
- **Recommended**: Python 3.13+ for latest security fixes

### Configuration Updates
The following files are configured for Python 3.10+:
- `pyproject.toml`: `requires-python = ">=3.10,&lt;3.14"`
- `mypy.ini`: `python_version = 3.10`
- Black configuration: `target-version = ["py310", "py311", "py312", "py313"]`

## Library Documentation Compliance

### LangChain Ecosystem ✅
- Proper version constraints following v0.3 compatibility
- Correct package separation (`langchain_openai`, `langchain_community`, etc.)
- Compatible with LangGraph integration

### CrewAI ✅
- Meets Python 3.10-3.14 requirement
- Version range allows patch updates
- Optional tools installation: `pip install 'crewai[tools]'`

### OpenAI ✅
- Current version with security updates
- Optional async support: `pip install 'openai[aiohttp]'`
- Proper API client configuration

### Supabase ✅
- Standard Python client installation
- Compatible version ranges
- Follows documented patterns

## Optional Dependencies

The project supports optional dependencies through `pyproject.toml`:

### Enterprise Features
```bash
pip install -e .[enterprise]
```

Includes:
- Azure Key Vault integration
- AWS Secrets Manager support
- HashiCorp Vault client

### Development Tools
```bash
pip install -e .[dev]
```

Includes:
- Testing frameworks
- Code quality tools
- Documentation generators

## Migration Guide

If upgrading from the previous requirements structure:

1. **Backup Current Environment**
   ```bash
   pip freeze > old-requirements.txt
   ```

2. **Install New Requirements**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Verify Installation**
   ```bash
   python -c "import langchain, crewai, openai; print('✅ Core imports successful')"
   ```

4. **Run Tests**
   ```bash
   pytest tests/ --maxfail=1
   ```

## Troubleshooting

### Common Issues

**ImportError for core libraries**
- Ensure Python version is 3.10+
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

**Version conflicts**
- Clear pip cache: `pip cache purge`
- Use fresh virtual environment

**Enterprise features not available**
- Install enterprise dependencies: `pip install -r requirements-enterprise.txt`
- Check cloud provider credentials configuration

### Getting Help

- Check the [Configuration Reference](../development/configuration_reference.md) for setup issues
- Review [Development Guide](../development/README.md) for development environment setup
- See [API Reference](../api/api_reference.md) for library usage examples
