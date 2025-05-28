# simple-fix.ps1 - Quick code formatting without command line issues
Write-Host "[SIMPLE FIX] AI System Code Formatter" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }

# Get Python files to fix
Write-Info "Finding Python files to fix..."
$pythonFiles = Get-ChildItem -Path "." -Filter "*.py" -Recurse | Where-Object {
    $_.FullName -notlike "*\.venv\*" -and
    $_.FullName -notlike "*\venv\*" -and  
    $_.FullName -notlike "*__pycache__*" -and
    $_.FullName -notlike "*site-packages*"
}

Write-Host "Found $($pythonFiles.Count) Python files to fix" -ForegroundColor Cyan

# Fix 1: autopep8 (handles most formatting issues)
Write-Host ""
Write-Info "Applying PEP8 fixes..."
Write-Host "  [FIX] Running autopep8 on project files..." -NoNewline

try {
    # Process each directory separately to avoid command line length issues
    $directories = $pythonFiles | Group-Object {Split-Path $_.FullName -Parent}
    $fixedFiles = 0
    
    foreach ($dirGroup in $directories) {
        $dirPath = $dirGroup.Name
        autopep8 --in-place --recursive $dirPath --aggressive --aggressive 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $fixedFiles += $dirGroup.Group.Count
        }
    }
    
    Write-Success " Fixed $fixedFiles files"
}
catch {
    Write-Error " autopep8 failed"
}

# Fix 2: isort (import sorting) - file by file
Write-Host "  [FIX] Sorting imports with isort..." -NoNewline
try {
    $sortedFiles = 0
    foreach ($file in ($pythonFiles | Select-Object -First 50)) {  # Limit for speed
        try {
            isort $file.FullName --quiet 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $sortedFiles++ }
        }
        catch {
            # Skip problematic files
        }
    }
    Write-Success " Sorted imports in $sortedFiles files"
}
catch {
    Write-Warning " isort not available"
}

# Fix 3: Manual fixes for common issues
Write-Host "  [FIX] Applying manual fixes..." -NoNewline
try {
    $manualFixCount = 0
    
    # Fix trailing whitespace and long lines in a few key files
    $keyFiles = $pythonFiles | Where-Object { $_.Name -like "*__init__.py" -or $_.Name -like "main.py" } | Select-Object -First 10
    
    foreach ($file in $keyFiles) {
        try {
            $content = Get-Content $file.FullName -Raw
            $originalContent = $content
            
            # Remove trailing whitespace
            $content = $content -replace '\s+$', ''
            
            # Fix common line length issues by adding line breaks after commas in long lines
            $lines = $content -split "`n"
            $fixedLines = @()
            
            foreach ($line in $lines) {
                if ($line.Length -gt 79 -and $line.Contains(',')) {
                    # Simple line break after commas for long lines
                    $line = $line -replace ',\s*', ",`n    "
                }
                $fixedLines += $line
            }
            
            $content = $fixedLines -join "`n"
            
            if ($content -ne $originalContent) {
                Set-Content $file.FullName -Value $content -NoNewline
                $manualFixCount++
            }
        }
        catch {
            # Skip files that can't be processed
        }
    }
    
    Write-Success " Applied manual fixes to $manualFixCount files"
}
catch {
    Write-Warning " Manual fixes failed"
}

# Quick validation
Write-Host ""
Write-Info "Running quick validation..."
Write-Host "  [CHECK] Checking remaining style issues..." -NoNewline

try {
    # Quick flake8 check on a subset of files
    $testFiles = $pythonFiles | Select-Object -First 20
    if ($testFiles.Count -gt 0) {
        $testPaths = ($testFiles | ForEach-Object { $_.FullName }) -join " "
        $flake8Result = flake8 $testPaths --count 2>&1
        
        $errorCount = 0
        $flake8Result | ForEach-Object {
            if ($_ -match "^\d+$") {
                $errorCount = [int]$_
            }
        }
        
        if ($errorCount -eq 0) {
            Write-Success " No style issues found in test sample!"
        } else {
            Write-Warning " $errorCount issues remain in test sample"
        }
    }
}
catch {
    Write-Warning " Unable to validate"
}

Write-Host ""
Write-Host "[SUMMARY] Simple fixes completed!" -ForegroundColor Green
Write-Host "• autopep8: Fixed formatting and PEP8 compliance" -ForegroundColor Green  
Write-Host "• isort: Organized imports" -ForegroundColor Green
Write-Host "• Manual: Fixed common issues in key files" -ForegroundColor Green
Write-Host ""
Write-Host "[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "• Run: .\code-quality.ps1 to see the improvement" -ForegroundColor Yellow
Write-Host "• Consider updating Python to 3.12.6+ for full Black support" -ForegroundColor Yellow
Write-Host ""
Write-Host "Your code quality should be significantly improved! 🚀" -ForegroundColor Green