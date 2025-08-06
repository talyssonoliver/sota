# Development Setup

## Quick Start (Recommended)

Get started in under 5 minutes:

```bash
# Clone repository
git clone https://github.com/talyssonoliver/sota.git
cd sota

# One-command setup with Makefile
make setup    # Sets up environment, dependencies, git hooks
make dev      # Starts full development stack
```

## Manual Setup

If you prefer manual setup or troubleshooting:

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Optional dev tools
```

### 2. Git Hooks Installation
```bash
# Copy hooks (automatic with make setup)
cp githooks/pre-commit .git/hooks/pre-commit
cp githooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

### 3. VSCode Configuration
Open the project in VSCode and:
- Accept recommended extensions when prompted
- Python interpreter will auto-detect `.venv/bin/python`
- Debugging and testing will be pre-configured

### 4. Docker Development (Optional)
```bash
# Start full stack
docker-compose -f docker-compose.dev.yml up -d

# Check status
make ps

# View logs
make logs
```

## Verification

Test your setup:
```bash
make test-quick    # Should complete in &lt;60s
make lint          # Check code quality
python main.py     # Run main system
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
```bash
cp .env.template .env
# Add required keys:
# - OPENAI_API_KEY (required)
# - MEMORY_ENGINE_KEY (generate with provided script)
```

Generate memory engine key:
```bash
python scripts/generate_memory_key.py
```

## Next Steps

- See [Automation Guide](automation.md) for development workflow
- See [Troubleshooting](troubleshooting.md) for common issues
- Review `QUICK_START_GUIDE.md` for full documentation
