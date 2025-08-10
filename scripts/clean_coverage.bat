@echo off
REM Clean Coverage Script for Windows (Batch)
REM Removes corrupted or stale coverage files to prevent test failures

echo 🧹 Cleaning coverage files...

REM Remove all coverage database files
for /f "delims=" %%i in ('dir /s /b .coverage* 2^>nul') do del "%%i" >nul 2>&1

REM Remove main coverage files
del coverage.xml >nul 2>&1
del .coverage >nul 2>&1

REM Remove HTML coverage directory and recreate it
rmdir /s /q htmlcov >nul 2>&1
mkdir htmlcov >nul 2>&1

REM Remove pytest cache
rmdir /s /q .pytest_cache >nul 2>&1

REM Clear coverage environment variables
set COVERAGE_FILE=
set COVERAGE_PROCESS_START=

echo ✅ Coverage files cleaned successfully!
echo You can now run tests with: python -m pytest --tb=short --no-cov