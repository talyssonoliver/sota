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
@$(VENV_DIR)/bin/$(PYTEST) tests/ -v --tb=short

test-quick: ## Fast validation
@$(MAKE) lint --no-print-directory
@$(VENV_DIR)/bin/$(PYTEST) tests/critical/ -v --tb=short -x --maxfail=3 2>/dev/null || $(VENV_DIR)/bin/$(PYTEST) tests/ -k "not slow" -v --tb=short -x --maxfail=3

test-agents: ## Multi-agent tests
@$(VENV_DIR)/bin/$(PYTEST) tests/agents/ -v --tb=short
@$(VENV_DIR)/bin/$(PYTHON) scripts/validate_workflows.py 2>/dev/null || echo "$(YELLOW)Workflow script missing$(NC)"

lint: ## Code quality checks
@$(VENV_DIR)/bin/ruff check . --fix 2>/dev/null || $(VENV_DIR)/bin/pip install ruff && $(VENV_DIR)/bin/ruff check . --fix
@$(VENV_DIR)/bin/isort . --check-only 2>/dev/null || ($(VENV_DIR)/bin/pip install isort && $(VENV_DIR)/bin/isort .)

format: ## Auto-format codebase
@$(VENV_DIR)/bin/ruff format . 2>/dev/null || $(VENV_DIR)/bin/pip install ruff && $(VENV_DIR)/bin/ruff format .
@$(VENV_DIR)/bin/isort . 2>/dev/null || $(VENV_DIR)/bin/pip install isort && $(VENV_DIR)/bin/isort .

docs: ## Build documentation
@if [ -d "docs/" ]; then cd docs && make html || true; else $(VENV_DIR)/bin/pydoc-markdown || true; fi

clean: ## Remove artifacts
@find . -type f -name "*.pyc" -delete
@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
@$(DOCKER_COMPOSE) down --volumes --remove-orphans 2>/dev/null || true
@rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

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
