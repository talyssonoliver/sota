# /setup-dev - Development Environment Setup

Set up the complete development environment for the AI system project.

## Steps:

1. **Python Environment**
   ```bash
   echo "🐍 Setting up Python environment..."
   
   # Check Python version
   python3 --version
   
   # Install/upgrade pip
   python3 -m pip install --upgrade pip
   
   # Install requirements
   if [ -f "requirements.txt" ]; then
       pip3 install -r requirements.txt
       echo "✅ Requirements installed"
   else
       echo "❌ requirements.txt not found"
   fi
   ```

2. **Environment Variables**
   ```bash
   echo "🔧 Setting up environment variables..."
   
   # Set PYTHONPATH
   export PYTHONPATH="${PWD}:${PYTHONPATH}"
   echo "export PYTHONPATH=${PWD}:\$PYTHONPATH" >> ~/.bashrc
   
   # Create .env from example if not exists
   if [ ! -f ".env" ] && [ -f ".env.example" ]; then
       cp .env.example .env
       echo "✅ Created .env from example"
       echo "⚠️ Please configure .env with your settings"
   fi
   ```

3. **Git Configuration**
   ```bash
   echo "📚 Configuring Git..."
   
   # Set up git hooks if available
   if [ -d ".git/hooks" ]; then
       # Copy pre-commit hook if exists
       if [ -f "scripts/git-hooks/pre-commit" ]; then
           cp scripts/git-hooks/pre-commit .git/hooks/
           chmod +x .git/hooks/pre-commit
           echo "✅ Git hooks installed"
       fi
   fi
   
   echo "Current branch: $(git branch --show-current)"
   ```

4. **Development Tools**
   ```bash
   echo "🛠️ Setting up development tools..."
   
   # Install development dependencies
   pip3 install black isort mypy pytest pytest-cov ruff bandit
   
   # Create necessary directories
   mkdir -p logs outputs test_outputs runtime/cache runtime/storage
   
   echo "✅ Development tools installed"
   ```

5. **Database Setup** 
   ```bash
   echo "🗃️ Setting up databases..."
   
   # Create runtime directories
   mkdir -p runtime/chroma_db runtime/storage/{hot,warm,cold}
   
   # Initialize storage metadata if not exists
   if [ ! -f "runtime/storage/storage_metadata.json" ]; then
       echo '{"version": "1.0", "created": "'$(date -Iseconds)'", "tiers": ["hot", "warm", "cold"]}' > runtime/storage/storage_metadata.json
       echo "✅ Storage metadata initialized"
   fi
   ```

6. **Validation Tests**
   ```bash
   echo "🧪 Running validation tests..."
   
   # Quick import test
   PYTHONPATH=. python3 -c "
   try:
       from src.core.agents.factory import create_backend_agent
       from src.infrastructure.memory.engines.memory_engine import MemoryEngine
       from src.core.workflows.execute_task import execute_task_workflow
       print('✅ Core imports successful')
   except ImportError as e:
       print(f'❌ Import error: {e}')
       exit(1)
   "
   
   # Run quick tests
   echo "Running quick test suite..."
   PYTHONPATH=. python3 -m pytest tests/unit/core/ -x --tb=short -q
   ```

7. **IDE Configuration**
   ```bash
   echo "💻 IDE Configuration..."
   
   if [ -d ".vscode" ]; then
       echo "✅ VS Code configuration found"
   fi
   
   # Create .editorconfig if not exists
   if [ ! -f ".editorconfig" ]; then
       cat > .editorconfig << 'EOF'
   root = true

   [*]
   charset = utf-8
   end_of_line = lf
   indent_style = space
   indent_size = 4
   insert_final_newline = true
   trim_trailing_whitespace = true

   [*.{yaml,yml}]
   indent_size = 2

   [*.md]
   trim_trailing_whitespace = false
   EOF
       echo "✅ .editorconfig created"
   fi
   ```

8. **Final Status Check**
   ```bash
   echo "🏁 Setup Complete!"
   echo "================================="
   echo "Project: $(basename $(pwd))"
   echo "Python: $(python3 --version)"
   echo "Pip packages: $(pip3 list | wc -l) installed"
   echo "Git branch: $(git branch --show-current)"
   echo "PYTHONPATH: $PYTHONPATH"
   echo ""
   echo "Next steps:"
   echo "1. Configure .env file with your settings"
   echo "2. Run /agent-status to check system health"
   echo "3. Run /test-quick for quick validation"
   echo "4. Run /check for comprehensive quality check"
   ```