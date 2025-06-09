# qa_cli.py

Command-line interface used by the QA agent to run automated quality assurance
tasks. It exposes subcommands for generating tests, analyzing coverage, and
validating quality gates.

## CLI Commands

- `generate-tests` – scaffold QA test cases using templates.
- `analyze-coverage` – invoke the CoverageTool and print a summary.
- `detect-integration-gaps` – inspect integration points for missing tests.
- `validate-quality` – run linters and static analysis tools.
- `report` – generate an overall QA report in Markdown.

All commands are implemented in the `main()` dispatcher and log to
`outputs/qa/qa_cli.log`.
