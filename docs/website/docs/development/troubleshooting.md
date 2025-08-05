# Troubleshooting

Comprehensive troubleshooting guide for common development issues and automated solutions.

## 🚑 Quick Diagnostics

### System Health Check
```bash
# Run automated system diagnostics
make health

# Check all services
make ps

# View recent logs
make logs
```

### Test Environment Validation
```bash
# Quick environment validation
python -m tests.run_tests --quick

# Full system validation
python main.py

# Check dependencies
pip check
```

## 🐍 Python Environment Issues

### Virtual Environment Problems

**Issue**: `python: command not found` or wrong Python version
```bash
# Solution 1: Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Solution 2: Use Makefile automation
make reset
make setup
```

**Issue**: `pip install` fails with permission errors
```bash
# Solution: Ensure virtual environment is active
source .venv/bin/activate
pip install --upgrade pip

# If still failing, use Makefile
make deps
```

### Dependency Conflicts

**Issue**: Package version conflicts
```bash
# Solution 1: Clean install
pip freeze > old_requirements.txt
pip uninstall -r old_requirements.txt -y
pip install -r requirements.txt

# Solution 2: Use automated reset
make clean
make setup
```

**Issue**: Missing development dependencies
```bash
# Solution: Install dev dependencies
pip install -r requirements-dev.txt

# OR use Makefile
make dev-deps
```

## 🚀 Git Hooks Issues

### Pre-commit Hook Failures

**Issue**: `ruff: command not found`
```bash
# Solution: Install ruff in virtual environment
source .venv/bin/activate
python3 -m pip install ruff

# OR reinstall hooks
make setup
```

**Issue**: Pre-commit hook takes too long
```bash
# Solution: Skip hooks temporarily (emergency only)
git commit --no-verify -m "your message"

# Permanent solution: Optimize hook
# Edit githooks/pre-commit to run only essential checks
```

**Issue**: Type checking errors blocking commits
```bash
# Solution 1: Fix type errors
mypy . --ignore-missing-imports

# Solution 2: Temporary bypass (use sparingly)
git commit --no-verify -m "fix: urgent fix"

# Solution 3: Configure mypy exclusions
# Edit mypy.ini to exclude problematic files
```

### Git Hook Installation Issues

**Issue**: Hooks not executing
```bash
# Solution: Check permissions and reinstall
ls -la .git/hooks/
chmod +x .git/hooks/pre-commit .git/hooks/post-commit

# Reinstall hooks
cp githooks/* .git/hooks/
chmod +x .git/hooks/*
```

## 🐳 Docker Issues

### Container Startup Problems

**Issue**: `docker-compose` command not found
```bash
# Solution: Install Docker Compose
# For Docker Desktop users, it's included
# For Linux:
sudo apt-get install docker-compose

# OR use docker compose (newer syntax)
docker compose -f docker-compose.dev.yml up -d
```

**Issue**: Port already in use
```bash
# Solution 1: Find and kill process using port
lsof -i :8000  # Find process using port 8000
kill -9 <PID>

# Solution 2: Use different ports
# Edit docker-compose.dev.yml port mappings

# Solution 3: Stop conflicting containers
docker ps
docker stop <container_name>
```

**Issue**: Container build failures
```bash
# Solution: Clean Docker cache and rebuild
docker system prune -f
docker-compose -f docker-compose.dev.yml build --no-cache

# OR use Makefile
make clean
make dev
```

### Volume Mount Issues

**Issue**: Code changes not reflected in container
```bash
# Solution: Check volume mounts
docker-compose -f docker-compose.dev.yml config

# Restart containers
make restart

# If on Windows, ensure proper path format
```

## 🧪 Memory Engine Issues

### ChromaDB Connection Problems

**Issue**: `chromadb.errors.ConnectionError`
```bash
# Solution 1: Restart ChromaDB container
docker-compose -f docker-compose.dev.yml restart chromadb

# Solution 2: Clear ChromaDB data
rm -rf runtime/chroma_db/*
make dev

# Solution 3: Check ChromaDB health
curl http://localhost:8001/api/v1/heartbeat
```

**Issue**: Memory engine encryption errors
```bash
# Solution: Regenerate encryption key
python scripts/generate_memory_key.py
# The script will help you add the key to your .env file

# Clear encrypted cache
rm -rf runtime/cache/*
```

### Vector Database Issues

**Issue**: Embedding generation failures
```bash
# Solution: Check OpenAI API key
echo $OPENAI_API_KEY
# Ensure it's set in .env file

# Test API connectivity
python -c "import openai; print(openai.Model.list())"
```

## 🧪 Test Suite Issues

### Test Failures

**Issue**: Import errors in tests
```bash
# Solution: Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Run with explicit path
PYTHONPATH=. python -m tests.run_tests --quick

# OR use pytest directly
pytest tests/ -v
```

**Issue**: Mock environment setup failures
```bash
# Solution: Reset test environment
rm -rf tests/__pycache__/
python -m tests.run_tests --quick

# Check mock imports
python -c "from tests.mock_environment import setup_mock_environment; setup_mock_environment()"
```

**Issue**: Tests timeout or hang
```bash
# Solution: Run with timeout
pytest tests/ --timeout=300

# OR use quick validation only
python -m tests.run_tests --quick

# Kill hanging processes
pkill -f python
```

### Performance Issues

**Issue**: Tests running slowly
```bash
# Solution: Use parallel execution
pytest tests/ -n 4

# OR use optimized quick tests
make test-quick

# Profile test performance
pytest tests/ --profile
```

## 📊 Dashboard Issues

### Dashboard Not Loading

**Issue**: Dashboard server not starting
```bash
# Solution: Check if port is available
lsof -i :8080

# Start dashboard manually
python dashboard/unified_api_server.py

# OR use Docker
make dev
```

**Issue**: Dashboard data not updating
```bash
# Solution: Regenerate dashboard data
python scripts/update_dashboard.py

# Check data files
ls -la dashboard/*.json

# Restart dashboard service
make restart
```

### API Integration Issues

**Issue**: API endpoints returning 404
```bash
# Solution: Check API routes
python -c "from dashboard.unified_api_server import app; print(app.url_map)"

# Test API health
curl http://localhost:8080/health

# Check logs
tail -f logs/dashboard.log
```

## 🔧 Development Tools Issues

### VSCode Configuration

**Issue**: Python interpreter not detected
```bash
# Solution: Select correct interpreter
# In VSCode: Ctrl+Shift+P -> "Python: Select Interpreter"
# Choose: ./venv/bin/python

# OR set manually in settings.json
{
    "python.pythonPath": "./.venv/bin/python"
}
```

**Issue**: Linting not working in VSCode
```bash
# Solution: Install extensions
# Install Python extension pack
# Install ruff extension

# Check settings.json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true
}
```

### Makefile Issues

**Issue**: `make: command not found`
```bash
# Solution for Windows: Install make
# Using chocolatey:
choco install make

# Using WSL:
wsl --install
# Then use Linux commands

# Alternative: Use commands directly
python -m pip install -r requirements.txt
```

**Issue**: Makefile commands failing
```bash
# Solution: Check tab vs spaces
# Makefile must use tabs, not spaces
sed -i 's/^    /\t/' Makefile

# OR regenerate from template
cp Makefile.template Makefile
```

## 🌐 Network & API Issues

### OpenAI API Problems

**Issue**: Rate limiting errors
```bash
# Solution: Add retry logic and delays
# Check current usage at https://platform.openai.com/usage

# Use environment variable for rate limiting
export OPENAI_RATE_LIMIT_DELAY=1

# OR upgrade OpenAI plan
```

**Issue**: Invalid API key errors
```bash
# Solution: Verify API key
echo $OPENAI_API_KEY

# Test key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Regenerate key if needed
```

### External Service Integration

**Issue**: Supabase connection errors
```bash
# Solution: Check credentials
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test connection
curl "$SUPABASE_URL/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY"
```

## 🤖 Agent Generation Issues

### Agent Template Problems

**Issue**: Agent generation script fails
```bash
# Solution: Check Jinja2 templates
ls -la templates/agent/

# Verify template syntax
python -c "from jinja2 import Template; Template(open('templates/agent/agent.py.j2').read())"

# Regenerate templates
python scripts/generate_agent.py "Test Agent" "Test description"
```

**Issue**: Generated agent not working
```bash
# Solution: Check agent configuration
cat config/agents.yaml

# Validate agent class
python -c "from agents.test_agent import TestAgent; print(TestAgent)"

# Run agent tests
python -m tests.run_tests --quick
```

## 📊 Automated Diagnostics

### Health Check Script
```bash
#!/bin/bash
# Create: scripts/health_check.sh

echo "🔍 Running system health check..."

# Check Python environment
echo "Python version: $(python --version)"
echo "Virtual env: $VIRTUAL_ENV"

# Check dependencies
echo "📦 Checking dependencies..."
pip check

# Check git hooks
echo "🪝 Checking git hooks..."
ls -la .git/hooks/pre-commit .git/hooks/post-commit

# Check Docker
echo "🐳 Checking Docker..."
docker --version
docker-compose --version

# Check services
echo "🔗 Checking services..."
curl -s http://localhost:8080/health || echo "Dashboard not running"
curl -s http://localhost:8001/api/v1/heartbeat || echo "ChromaDB not running"

# Check test suite
echo "🧪 Running quick tests..."
python -m tests.run_tests --quick

echo "✅ Health check complete!"
```

### Automated Recovery
```bash
#!/bin/bash
# Create: scripts/recovery.sh

echo "🔧 Starting automated recovery..."

# Stop all services
make stop

# Clean environment
make clean

# Reset and setup
make reset
make setup

# Restart services
make dev

# Validate
make health

echo "✅ Recovery complete!"
```

## 📊 Test Reporting

### Generate Full Test Report
When tests fail and you need to see the complete output:

```bash
# Generate comprehensive test report
python generate_test_report.py

# This creates a timestamped file like: test_report_20240615_143022.txt
```

### Windows Test Runner
For better output capture on Windows:

```bash
# Run with enhanced output capture
python run_tests_windows.py --all

# Quick tests only
python run_tests_windows.py --quick
```

## 📞 Getting Help

### Log Locations
- **System logs**: `logs/`
- **Test logs**: `tests/logs/`
- **Dashboard logs**: `dashboard/logs/`
- **Docker logs**: `docker-compose logs`
- **Test reports**: `test_report_*.txt`

### Debug Commands
```bash
# Enable debug mode
export DEBUG=1
export VERBOSE=1

# Run with detailed output
python main.py --debug --verbose

# Capture all logs
make logs > debug.log 2>&1
```

### Support Resources
- **Issue Tracker**: Create GitHub issues for bugs
- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` for working code
- **Community**: Discussion in project repository

---

**Remember**: Most issues can be resolved with `make clean && make setup`. When in doubt, start with the automated diagnostics and recovery scripts.
