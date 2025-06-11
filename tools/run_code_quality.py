#!/usr/bin/env python
"""Simple code quality runner: ruff check and formatting"""
import subprocess
import sys

commands = [
    ["ruff", "--fix", "--exit-zero"],
    ["black", "."],
    ["isort", "."],
]

for cmd in commands:
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)
