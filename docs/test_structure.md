# Test Structure

This document describes how tests are organized within the repository and explains the most common fixtures.

## Directory Layout

```
tests/
├── conftest.py          # global fixtures and performance tweaks
├── fixtures/            # reusable fixture modules
├── helpers.py           # common test helpers
├── run_tests.py         # simple wrapper around pytest
├── integration_*.py     # integration test suites
└── test_*.py            # unit tests for modules
```

- **conftest.py** provides auto-used fixtures to mock external services and speed up the test suite.
- The **fixtures/** package contains mock objects used across multiple tests.
- Helper scripts like **run_tests.py** and **debug_*\*.py** assist with debugging failures.

## Key Fixtures

- `fast_test_environment` – creates isolated directories and mocks external services for every test run.
- `mock_memory_engine` – provides a consistent in-memory vector store for tests that require context retrieval.
- `enhanced_workflow` – returns a workflow object with recursion limits to prevent runaway loops.
- `track_test_performance` – logs slow tests to help maintain suite speed.

Refer to `tests/conftest.py` for a full list of available fixtures and their implementations.

## Writing New Tests

1. Place new test files under `tests/` using the `test_*.py` naming pattern.
2. Import any shared fixtures directly or rely on the auto-used fixtures defined in `conftest.py`.
3. Keep tests short and focused on a single behavior.
4. Run `pytest` from the repository root or execute `python tests/run_tests.py`.

These guidelines ensure a consistent and maintainable test suite.
