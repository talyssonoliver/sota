#!/bin/bash
# Cleanup script to remove identical duplicate files
# These files have been verified to be byte-for-byte identical

echo "Starting cleanup of identical duplicate files..."

# List of files to remove (verified as identical)
FILES_TO_REMOVE=(
    "/mnt/c/taly/ai-system/orchestration/execute_task.py"
    "/mnt/c/taly/ai-system/tools/context_tracker.py"
    "/mnt/c/taly/ai-system/tools/context_visualizer.py"
    "/mnt/c/taly/ai-system/tools/echo_tool.py"
    "/mnt/c/taly/ai-system/tools/supabase_tool.py"
    "/mnt/c/taly/ai-system/tools/tool_loader.py"
    "/mnt/c/taly/ai-system/tools/memory/config.py"
    "/mnt/c/taly/ai-system/tools/memory/storage.py"
)

# Counter for removed files
REMOVED=0

# Remove each file
for FILE in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$FILE" ]; then
        echo "Removing: $FILE"
        rm "$FILE"
        ((REMOVED++))
    else
        echo "File not found: $FILE"
    fi
done

echo ""
echo "Cleanup complete. Removed $REMOVED files."

# Show remaining Python files in old directories
echo ""
echo "Remaining Python files in old directories:"
echo ""
echo "In /tools directory:"
find /mnt/c/taly/ai-system/tools -name "*.py" -type f | grep -v __pycache__ | wc -l
echo ""
echo "In /orchestration directory:"
find /mnt/c/taly/ai-system/orchestration -name "*.py" -type f | grep -v __pycache__ | wc -l