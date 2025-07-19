.DEFAULT_GOAL := help
.PHONY: help setup dev test test-quick test-agents lint format docs clean install benchmark security deps backup validate dev-setup dev-reset logs shell ps restart stop parallel-test quick full

BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

PYTHON := python3
PIP := pip3
PYTEST := pytest
VENV_DIR := .venv
DOCKER_COMPOSE := docker-compose -f docker-compose.dev.yml
PROJECT_NAME := sota

# Check if venv exists, use it if available, otherwise use system Python
VENV_PYTHON := $(shell [ -f $(VENV_DIR)/bin/python ] && echo "$(VENV_DIR)/bin/python" || echo "$(PYTHON)")
VENV_PIP := $(shell [ -f $(VENV_DIR)/bin/pip ] && echo "$(VENV_DIR)/bin/pip" || echo "$(PYTHON) -m pip")

define check_command
	@which $(1) > /dev/null || (echo "$(RED)❌ $(1) not found. Please install $(1)$(NC)" && exit 1)
endef

define run_parallel
	@echo "$(BLUE)🚀 Running $(1) in parallel...$(NC)"
	@$(1) &
endef

help: ## Show help
	@echo "$(BLUE)🤖 SOTA Multi-Agent AI System - Development Commands$(NC)"
	@awk 'BEGIN {FS=":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\n$(GREEN)Quick Start:$(NC)"
	@echo "  make setup     - Complete environment setup"
	@echo "  make dev       - Start development environment"
	@echo "  make test-quick - Fast validation (<60s)"

setup: ## Complete environment setup
	@echo "$(BLUE)🏗️ Setting up SOTA environment...$(NC)"
	$(call check_command,$(PYTHON))
	$(call check_command,git)
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@$(VENV_DIR)/bin/pip install -r requirements-dev.txt 2>/dev/null || echo "$(YELLOW)No dev requirements$(NC)"
	@cp githooks/pre-commit .git/hooks/pre-commit 2>/dev/null || true
	@cp githooks/post-commit .git/hooks/post-commit 2>/dev/null || true
	@chmod +x .git/hooks/pre-commit .git/hooks/post-commit 2>/dev/null || true
	@$(DOCKER_COMPOSE) build --parallel 2>/dev/null || echo "$(YELLOW)Docker build skipped$(NC)"
	@echo "$(GREEN)Setup completed! Run 'make dev'$(NC)"

dev: setup ## Start development environment
	@$(DOCKER_COMPOSE) up -d
	@$(DOCKER_COMPOSE) ps

dev-setup: setup dev ## Setup and start services
	@echo "$(GREEN)Full development environment ready!$(NC)"

dev-reset: clean dev-setup ## Reset environment
	@echo "$(GREEN)Environment reset completed!$(NC)"

test: lint ## Run full test suite
	@echo "$(BLUE)🧪 Running full test suite...$(NC)"
	@$(VENV_PYTHON) -m pytest tests/ -v
	@echo "$(BLUE)🧹 Cleaning up coverage files...$(NC)"
	@rm -f .coverage.*

test-quick: ## Fast validation
	@$(MAKE) lint --no-print-directory
	@echo "$(BLUE)🧪 Running quick tests...$(NC)"
	@$(VENV_PYTHON) -m pytest -n 2 --dist loadfile --tb=line --maxfail=5 -x tests/
	@echo "$(BLUE)🧹 Cleaning up coverage files...$(NC)"
	@rm -f .coverage.*

test-agents: ## Multi-agent tests
	@echo "$(BLUE)🤖 Running agent tests...$(NC)"
	@$(VENV_PYTHON) -m pytest tests/agents/ -v --tb=short

test-unit: ## Fast unit tests only
	@echo "$(BLUE)⚡ Running unit tests...$(NC)"
	@$(VENV_PYTHON) -m pytest -m unit -n auto --dist loadscope --tb=line

test-integration: ## Integration tests only
	@echo "$(BLUE)🔗 Running integration tests...$(NC)"
	@$(VENV_PYTHON) -m pytest -m integration -n auto --dist loadscope --tb=short

test-parallel: ## Full parallel test suite with optimal settings
	@echo "$(BLUE)🚀 Running full test suite in parallel...$(NC)"
	@$(VENV_PYTHON) -m pytest -n auto --dist loadscope tests/ --tb=line

lint: ## Code quality checks
	@echo "$(BLUE)🔍 Running linting checks...$(NC)"
	@$(VENV_PYTHON) -m ruff check . --fix 2>/dev/null || echo "$(YELLOW)⚠️  Ruff not available, install with: pip install ruff$(NC)"
	@$(VENV_PYTHON) -m isort . --check-only 2>/dev/null || echo "$(YELLOW)⚠️  isort not available, install with: pip install isort$(NC)"

format: ## Auto-format codebase
	@$(VENV_PYTHON) -m ruff format . 2>/dev/null || ($(VENV_PIP) install ruff && $(VENV_PYTHON) -m ruff format .)
	@$(VENV_PYTHON) -m isort . 2>/dev/null || ($(VENV_PIP) install isort && $(VENV_PYTHON) -m isort .)

docs: ## Build documentation
	@if [ -d "docs/" ]; then cd docs && make html || true; else $(VENV_DIR)/bin/pydoc-markdown || true; fi

clean: ## Remove artifacts
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@$(DOCKER_COMPOSE) down --volumes --remove-orphans 2>/dev/null || true
	@rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

clean-generated: ## Clean generated files (coverage, HITL test files, etc)
	@echo "$(BLUE)🧹 Cleaning generated files...$(NC)"
	@$(VENV_PYTHON) scripts/cleanup_generated_files.py
	@echo "$(GREEN)✅ Generated file cleanup complete$(NC)"

clean-generated-dry: ## Show what would be cleaned (dry run)
	@echo "$(BLUE)🔍 Checking generated files (dry run)...$(NC)"
	@$(VENV_PYTHON) scripts/cleanup_generated_files.py --dry-run

clean-hitl: ## Clean HITL storage files with retention policy
	@echo "$(BLUE)🧹 Cleaning HITL storage...$(NC)"
	@$(VENV_PYTHON) scripts/cleanup_hitl_storage.py
	@echo "$(GREEN)✅ HITL storage cleanup complete$(NC)"

clean-hitl-dry: ## Show what HITL files would be cleaned (dry run)
	@echo "$(BLUE)🔍 Checking HITL storage (dry run)...$(NC)"
	@$(VENV_PYTHON) scripts/cleanup_hitl_storage.py --dry-run

clean-all: clean clean-generated clean-hitl ## Full cleanup including all generated files

install: ## Production install
	@$(PIP) install -e . --no-deps

benchmark: ## Performance tests
	@$(VENV_DIR)/bin/$(PYTHON) scripts/benchmark_agents.py 2>/dev/null || echo "$(YELLOW)Benchmark script missing$(NC)"
	@$(VENV_DIR)/bin/$(PYTEST) tests/ -k "benchmark" --benchmark-only 2>/dev/null || true

security: ## Security scanning
	@$(VENV_DIR)/bin/bandit -r . -f json 2>/dev/null || ($(VENV_DIR)/bin/pip install bandit && $(VENV_DIR)/bin/bandit -r . -f json)
	@$(VENV_DIR)/bin/safety check 2>/dev/null || ($(VENV_DIR)/bin/pip install safety && $(VENV_DIR)/bin/safety check)

deps: ## Dependency management
	@$(VENV_DIR)/bin/pip list --outdated

backup: ## Manual backup
	@mkdir -p .sota_backups
	@tar -czf .sota_backups/manual_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.sota_backups' --exclude='node_modules' .

validate: test-quick benchmark ## Full validation
	@$(MAKE) security --no-print-directory

sonar-setup: ## Setup SonarQube integration
	@echo "$(BLUE)🔍 Setting up SonarQube integration...$(NC)"
	@$(VENV_PYTHON) -c "from src.infrastructure.tools.validation.sonarqube_integrator import SonarQubeIntegrator; integrator = SonarQubeIntegrator(); integrator.export_sonarqube_config()"
	@echo "$(GREEN)✅ SonarQube configuration exported$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Install SonarQube server: docker run -d --name sonarqube -p 9000:9000 sonarqube:community"
	@echo "  2. Download SonarQube scanner from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
	@echo "  3. Set SONAR_TOKEN environment variable"
	@echo "  4. Run 'make sonar-validate' for integrated analysis"

sonar-validate: ## Run validation with SonarQube integration
	@echo "$(BLUE)🔍 Running comprehensive validation with SonarQube...$(NC)"
	@$(VENV_PYTHON) -c "from src.infrastructure.tools.validation.validate import main; import sys; sys.argv = ['validate.py', '--comprehensive', '--enable-sonarqube']; main()" 2>/dev/null || echo "$(YELLOW)Run with SonarQube environment setup$(NC)"

sonar-only: ## Run SonarQube analysis only
	@echo "$(BLUE)🔍 Running SonarQube analysis...$(NC)"
	@sonar-scanner 2>/dev/null || echo "$(RED)❌ SonarQube scanner not found. Run 'make sonar-setup' first$(NC)"

logs: ## Show service logs
	@$(DOCKER_COMPOSE) logs -f

shell: ## Open shell in app container
	@$(DOCKER_COMPOSE) exec $(PROJECT_NAME)-app bash || $(DOCKER_COMPOSE) exec $(PROJECT_NAME)-app sh

ps: ## List services
	@$(DOCKER_COMPOSE) ps

restart: ## Restart services
	@$(DOCKER_COMPOSE) restart

stop: ## Stop services
	@$(DOCKER_COMPOSE) stop

parallel-test: ## Run tests in parallel
	$(call run_parallel,$(MAKE) test-agents)
	$(call run_parallel,$(MAKE) lint)
	$(call run_parallel,$(MAKE) security)
	@wait

quick: test-quick format ## Quick dev cycle

full: clean setup test benchmark docs ## Full dev cycle
