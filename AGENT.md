# Codex Agent Guidelines

This file contains instructions for the Codex agent contributing to the SOTA repository.

## Development setup
- Use `make setup` to create the virtual environment and install all dependencies.
- Start the development stack with `make dev`.

## Testing and formatting
- Run `make test-quick` before committing changes. This executes linting and critical tests.
- Use `make lint` to run Ruff and isort checks.
- Use `make format` to apply automatic formatting.

## Contribution rules
- Follow the existing code style defined in `pyproject.toml` and `.ruff.toml`.
- Ensure new files include informative comments when necessary.
- Keep pull request summaries concise but descriptive.
- Include a **Testing** section describing any `make` or `pytest` commands executed.

