Safely move file with dependency updates: $ARGUMENTS

ULTRA THINKING required. Steps:
1. First run /project:analyze-file-impact for the file
2. Create a git branch: `git checkout -b move-$FILENAME`
3. Generate a movement plan in MOVEMENT_PLAN.md
4. For each dependent file:
   - Update import statements using rope or manual updates
   - Verify syntax with `python -m py_compile $FILE`
5. Move the file to new location
6. Run affected tests in isolation
7. Create detailed log of all changes