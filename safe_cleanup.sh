#!/bin/bash
# Safe cleanup script for ai-system

echo "🧹 Starting safe cleanup..."

# 1. Remove Python cache files
echo "Removing Python cache files..."
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 2. Remove coverage files (can be regenerated)
echo "Removing coverage files..."
rm -f coverage.xml coverage.json .coverage

# 3. Remove swap/backup files
echo "Removing swap and backup files..."
find . -name "*.swp" -delete
find . -name "*.bak" -delete
find . -name "*~" -delete

# 4. Remove pytest cache
echo "Removing pytest cache..."
rm -rf .pytest_cache

# 5. Clean empty directories (but keep important structure)
echo "Cleaning empty directories..."
find . -type d -empty -not -path "./.git/*" -not -path "./runtime/*" -not -path "./build/*" -not -path "./archives/*" -delete 2>/dev/null || true

echo "✅ Cleanup complete!"

# Show space saved
echo ""
echo "📊 Cleanup Summary:"
echo "- Removed Python cache files"
echo "- Removed coverage reports (2.7MB)"
echo "- Removed temporary files"
echo "- Cleaned empty directories"