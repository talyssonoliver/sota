@echo off
echo 🧪 Quick Tests (Parallel) - Batch Runner
cd /d "%~dp0"
python tests\enhanced_test_runner.py --quick --verbose
pause
