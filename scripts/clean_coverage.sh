#!/bin/bash
# Clean Coverage Data Script
# Ensures consistent coverage collection by cleaning up old data

set -e

echo "🧹 Cleaning coverage data..."

# Remove all coverage data files
rm -f .coverage*
rm -f coverage.xml
rm -rf htmlcov/

# Clear coverage environment variables that might conflict
unset COVERAGE_FILE
unset COVERAGE_PROCESS_START

# Set consistent coverage context
export COVERAGE_CONTEXT="pytest"

echo "✅ Coverage data cleaned successfully"

# Optionally run coverage erase if coverage is available
if command -v coverage >/dev/null 2>&1; then
    coverage erase
    echo "✅ Coverage database erased"
fi

echo "🎯 Ready for clean coverage collection"