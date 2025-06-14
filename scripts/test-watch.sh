#!/usr/bin/env bash
# Simple pytest watch mode using pytest-watch (ptw)

if ! command -v ptw >/dev/null 2>&1; then
  echo "pytest-watch is not installed. Please run: pip install pytest-watch" >&2
  exit 1
fi

# Use ptw with markers for quick feedback
ptw -q -- --maxfail=1

