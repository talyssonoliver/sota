.PHONY: help setup dev test test-quick lint format docs clean install benchmark security deps backup validate

PYTHON?=python
VENV?=.venv/bin/

help:
@echo "Available commands: setup dev test test-quick lint format docs clean install benchmark security deps backup validate"

setup:
$(PYTHON) -m venv .venv && $(VENV)pip install -U pip
$(VENV)pip install -r requirements.txt

dev:
docker-compose -f docker-compose.dev.yml up -d

clean:
rm -rf .venv __pycache__ */__pycache__

lint:
$(VENV)ruff --fix .
$(VENV)isort .

format:
$(VENV)black .

docs:
$(VENV)pdoc agents -o docs/api

test:
$(VENV)pytest -v

test-quick:
$(VENV)pytest -q

install:
$(VENV)pip install -e .

benchmark:
$(VENV)python scripts/benchmark_agents.py

security:
$(VENV)pip install bandit && $(VENV)bandit -r agents

deps:
$(VENV)pip list --outdated

backup:
bash .git/hooks/post-commit

validate: lint test
@echo "Validation complete"
