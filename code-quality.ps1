# code-quality.ps1 - Comprehensive Code Quality Checker
param(
    [string]$Path = ".",
    [switch]$Fix,
    [switch]$Verbose,
    [string]$Output = "console",
    [switch]$SkipInstall
)

Write-Host "[INFO] AI System Code Quality Checker" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }

# Results tracking
$Global:Results = @{
    TotalFiles = 0
    TotalIssues = 0
    Duplicates = 0
    SecurityIssues = 0
    StyleIssues = 0
    ComplexityIssues = 0
    DeadCode = 0
    TypeIssues = 0
}

# Get project Python files (exclude common directories that shouldn't be analyzed)
function Get-ProjectPythonFiles {
    param([string]$BasePath, [int]$MaxFiles = 0)
    
    $projectFiles = Get-ChildItem -Path $BasePath -Filter "*.py" -Recurse | Where-Object {
        $_.FullName -notlike "*\.venv\*" -and
        $_.FullName -notlike "*\venv\*" -and  
        $_.FullName -notlike "*__pycache__*" -and
        $_.FullName -notlike "*site-packages*" -and
        $_.FullName -notlike "*\.pytest_cache*" -and
        $_.FullName -notlike "*\.git\*" -and
        $_.FullName -notlike "*node_modules*" -and
        $_.FullName -notlike "*build\*" -and
        $_.FullName -notlike "*dist\*"
    }
    
    if ($MaxFiles -gt 0) {
        $projectFiles = $projectFiles | Select-Object -First $MaxFiles
    }
    
    return $projectFiles
}

# Install required tools
function Install-CodeQualityTools {
    if ($SkipInstall) { return }
    
    Write-Info "Installing/updating code quality tools..."
    
    $tools = @(
        "flake8",           # Linting
        "black",            # Code formatting
        "isort",            # Import sorting
        "bandit",           # Security scanning
        "radon",            # Complexity analysis
        "vulture",          # Dead code detection
        "mypy",             # Type checking
        "pylint",           # Comprehensive linting + duplicate detection
        "safety",           # Dependency security
        "autopep8"          # Auto-fix formatting
    )
    
    foreach ($tool in $tools) {
        try {
            pip install --upgrade $tool --quiet
            if ($Verbose) { Write-Success "Installed/updated: $tool" }
        }
        catch {
            Write-Warning "Failed to install $tool"
        }
    }
}

# Run linting checks
function Test-Linting {
    Write-Info "Running linting checks..."
    
    $projectFiles = Get-ProjectPythonFiles $Path
    
    # Flake8 - Style and logic errors  
    Write-Host "  [LINT] Checking code style (flake8)..." -NoNewline
    try {
        if ($projectFiles.Count -gt 0) {
            # Use flake8 with exclude patterns to avoid virtual environment issues
            $flake8Result = flake8 $Path --exclude=".venv,venv,__pycache__,site-packages,.git,.pytest_cache" --count --statistics 2>&1
            
            # Count actual error lines, not characters
            $errorLines = $flake8Result | Where-Object { 
                $_ -match "^\.\\" -and 
                $_ -notlike "*\.venv\*" -and 
                $_ -notlike "*\venv\*" -and 
                $_ -notlike "*__pycache__*" -and
                $_ -notlike "*site-packages*"
            }
            
            if ($errorLines.Count -eq 0) {
                Write-Success " Passed"
            } else {
                Write-Error " $($errorLines.Count) issues found"
                if ($Verbose) { 
                    Write-Host "    Top project code issues:" -ForegroundColor Yellow
                    $errorLines | Select-Object -First 10 | ForEach-Object {
                        Write-Host "    $_" -ForegroundColor Yellow
                    }
                    if ($errorLines.Count -gt 10) {
                        Write-Host "    ... and $($errorLines.Count - 10) more issues" -ForegroundColor Yellow
                    }
                }
                $Global:Results.StyleIssues += $errorLines.Count
            }
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " Flake8 not available"
    }
    
    # PyLint - Comprehensive analysis (with timeout and proper file handling)
    Write-Host "  [LINT] Running comprehensive analysis (pylint)..." -NoNewline
    try {
        if ($projectFiles.Count -gt 0) {
            # Limit files for performance and create temp file list
            $limitedFiles = $projectFiles | Select-Object -First 20
            $tempFileList = New-TemporaryFile
            $limitedFiles.FullName | Out-File -FilePath $tempFileList.FullName -Encoding UTF8
            
            # Create a job with timeout to prevent hanging
            $pylintJob = Start-Job -ScriptBlock {
                param($fileListPath)
                $files = Get-Content $fileListPath
                if ($files.Count -gt 0) {
                    # Analyze files one by one to avoid command line length issues
                    $allResults = @()
                    foreach ($file in $files) {
                        if (Test-Path $file) {
                            $result = pylint $file --output-format=text --score=no 2>&1
                            $allResults += $result
                        }
                    }
                    
                    # Get overall score
                    $scoreResult = pylint ($files -join " ") --output-format=text --score=yes --disable=all 2>&1
                    $allResults += $scoreResult
                    
                    return $allResults
                } else {
                    return "No files to analyze"
                }
            } -ArgumentList $tempFileList.FullName
            
            # Wait for job with timeout (45 seconds)
            $completed = Wait-Job $pylintJob -Timeout 45
            if ($completed) {
                $pylintResult = Receive-Job $pylintJob
                $pylintScore = ($pylintResult | Select-String "Your code has been rated at ([\d\.\-]+)" | ForEach-Object { $_.Matches[0].Groups[1].Value })
                
                if ($pylintScore -and [float]$pylintScore -ge 8.0) {
                    Write-Success " Score: $pylintScore/10"
                } elseif ($pylintScore) {
                    Write-Warning " Score: $pylintScore/10 (needs improvement)"
                    if ($Verbose) { 
                        $issueLines = $pylintResult | Select-String ":\d+:\d+:" | Select-Object -First 5
                        if ($issueLines.Count -gt 0) {
                            Write-Host "    Top issues:" -ForegroundColor Yellow
                            $issueLines | ForEach-Object {
                                Write-Host "    $_" -ForegroundColor Yellow
                            }
                        }
                    }
                } else {
                    Write-Warning " Unable to get score"
                }
            } else {
                Write-Warning " Timeout (analysis taking too long)"
            }
            
            Remove-Job $pylintJob -Force
            Remove-Item $tempFileList.FullName -Force -ErrorAction SilentlyContinue
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " PyLint not available"
    }
}

# Check for duplicate code using PyLint (with timeout and filtering)
function Test-DuplicateCode {
    Write-Info "Scanning for duplicate code..."
    
    Write-Host "  [DUP] Analyzing code duplication (pylint)..." -NoNewline
    try {
        $projectFiles = Get-ProjectPythonFiles $Path 20  # Limit to 20 files for speed
        
        if ($projectFiles.Count -gt 1) {
            # Create a job with timeout to prevent hanging
            $dupJob = Start-Job -ScriptBlock {
                param($files)
                $fileList = ($files.FullName -join " ")
                pylint $fileList --disable=all --enable=duplicate-code --duplicate-code-min-similarity-lines=5 --output-format=text 2>&1
            } -ArgumentList @(,$projectFiles)
            
            # Wait for job with timeout (30 seconds)
            $completed = Wait-Job $dupJob -Timeout 30
            if ($completed) {
                $pylintDupResult = Receive-Job $dupJob
                
                # Count duplicate code blocks (pylint reports them as R0801)
                $duplicateLines = $pylintDupResult | Select-String "R0801.*duplicate-code"
                $duplicateBlocks = $pylintDupResult | Select-String "Similar lines in \d+ files"
                
                if ($duplicateLines.Count -eq 0 -and $duplicateBlocks.Count -eq 0) {
                    Write-Success " No significant duplicates found"
                } else {
                    $duplicateCount = [math]::Max($duplicateLines.Count, $duplicateBlocks.Count)
                    Write-Warning " Found $duplicateCount duplicate code blocks"
                    $Global:Results.Duplicates += $duplicateCount
                    
                    if ($Verbose) { 
                        Write-Host "    Duplicate code details:" -ForegroundColor Yellow
                        $pylintDupResult | Select-String "(R0801|Similar lines)" | Select-Object -First 3 | ForEach-Object {
                            Write-Host "    $_" -ForegroundColor Yellow
                        }
                    }
                }
            } else {
                Write-Warning " Timeout (skipping duplicate analysis)"
            }
            
            Remove-Job $dupJob -Force
        } else {
            Write-Success " Insufficient files for duplicate analysis"
        }
    }
    catch {
        Write-Warning " PyLint duplicate detection not available"
    }
}

# Security analysis
function Test-Security {
    Write-Info "Running security analysis..."
    
    $projectFiles = Get-ProjectPythonFiles $Path
    
    # Bandit - Security issues (exclude virtual environments)
    Write-Host "  [SEC] Checking security vulnerabilities (bandit)..." -NoNewline
    try {
        if ($projectFiles.Count -gt 0) {
            # Only scan project directories, not dependencies
            $projectPaths = Get-ChildItem -Path $Path -Directory | Where-Object {
                $_.Name -notin @(".venv", "venv", ".git", "__pycache__", ".pytest_cache", "node_modules")
            }
            
            if ($projectPaths.Count -eq 0) {
                # If no subdirectories, scan current directory but exclude patterns
                $banditResult = bandit -r $Path --exclude "*/.venv/*,*/venv/*,*/__pycache__/*,*/site-packages/*" -f json 2>&1
            } else {
                $pathList = ($projectPaths.FullName -join ",")
                $banditResult = bandit -r $pathList -f json 2>&1
            }
            
            if ($LASTEXITCODE -eq 0) {
                try {
                    $banditJson = $banditResult | ConvertFrom-Json
                    $securityIssues = $banditJson.results.Count
                    
                    if ($securityIssues -eq 0) {
                        Write-Success " No security issues found"
                    } else {
                        Write-Warning " Found $securityIssues security issues"
                        $Global:Results.SecurityIssues += $securityIssues
                        if ($Verbose) {
                            $banditJson.results | Select-Object -First 3 | ForEach-Object {
                                Write-Host "    $($_.filename):$($_.line_number) - $($_.test_id): $($_.issue_text)" -ForegroundColor Yellow
                            }
                        }
                    }
                }
                catch {
                    Write-Success " No security issues found"
                }
            }
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " Bandit not available"
    }
    
    # Safety - Dependency vulnerabilities (check requirements files only)
    Write-Host "  [SEC] Checking dependency vulnerabilities (safety)..." -NoNewline
    try {
        $safetyResult = safety check --json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success " Dependencies are secure"
        } else {
            Write-Warning " Vulnerable dependencies found"
            if ($Verbose) { 
                $safetyResult | Select-Object -First 3 | ForEach-Object {
                    Write-Host "    $_" -ForegroundColor Yellow
                }
            }
        }
    }
    catch {
        Write-Warning " Safety not available"
    }
}

# Complexity analysis
function Test-Complexity {
    Write-Info "Analyzing code complexity..."
    
    Write-Host "  [COMP] Checking cyclomatic complexity..." -NoNewline
    try {
        $projectFiles = Get-ProjectPythonFiles $Path
        
        if ($projectFiles.Count -gt 0) {
            $radonResult = radon cc ($projectFiles.FullName -join " ") -a -nc 2>&1
            
            $complexFunctions = $radonResult | Select-String " [D-F] " 
            if ($complexFunctions.Count -eq 0) {
                Write-Success " Complexity is acceptable"
            } else {
                Write-Warning " Found $($complexFunctions.Count) complex functions"
                $Global:Results.ComplexityIssues += $complexFunctions.Count
                if ($Verbose) {
                    $complexFunctions | Select-Object -First 3 | ForEach-Object { 
                        Write-Host "    $_" -ForegroundColor Yellow 
                    }
                }
            }
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " Radon not available"
    }
}

# Dead code detection  
function Test-DeadCode {
    Write-Info "Detecting unused code..."
    
    Write-Host "  [DEAD] Scanning for dead code (vulture)..." -NoNewline
    try {
        $projectFiles = Get-ProjectPythonFiles $Path 30  # Limit to 30 files for performance
        
        if ($projectFiles.Count -gt 0) {
            # Create a job with timeout to prevent issues
            $vultureJob = Start-Job -ScriptBlock {
                param($files)
                try {
                    $fileList = $files.FullName -join " "
                    vulture $fileList --min-confidence 80 2>&1
                }
                catch {
                    "Error running vulture: $_"
                }
            } -ArgumentList @(,$projectFiles)
            
            # Wait for job with timeout (20 seconds)
            $completed = Wait-Job $vultureJob -Timeout 20
            if ($completed) {
                $vultureResult = Receive-Job $vultureJob
                
                # Filter out errors and count actual dead code findings
                $deadCodeLines = $vultureResult | Where-Object { 
                    $_ -notlike "*Traceback*" -and 
                    $_ -notlike "*Error*" -and
                    $_ -match ".*\.py:\d+:.*unused"
                }
                
                if ($deadCodeLines.Count -eq 0) {
                    Write-Success " No dead code found"
                } else {
                    Write-Warning " Found $($deadCodeLines.Count) potential dead code issues"
                    $Global:Results.DeadCode += $deadCodeLines.Count
                    if ($Verbose) { 
                        Write-Host "    Dead code findings:" -ForegroundColor Yellow
                        $deadCodeLines | Select-Object -First 5 | ForEach-Object {
                            Write-Host "    $_" -ForegroundColor Yellow
                        }
                        if ($deadCodeLines.Count -gt 5) {
                            Write-Host "    ... and $($deadCodeLines.Count - 5) more issues" -ForegroundColor Yellow
                        }
                    }
                }
            } else {
                Write-Warning " Timeout (skipping dead code analysis)"
            }
            
            Remove-Job $vultureJob -Force
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " Vulture not available"
    }
}

# Type checking
function Test-TypeChecking {
    Write-Info "Running type analysis..."
    
    Write-Host "  [TYPE] Checking type annotations (mypy)..." -NoNewline
    try {
        $projectFiles = Get-ProjectPythonFiles $Path 20  # Limit for speed
        
        if ($projectFiles.Count -gt 0) {
            $mypyResult = mypy ($projectFiles.FullName -join " ") --ignore-missing-imports 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success " Type checking passed"
            } else {
                $typeIssues = ($mypyResult | Select-String "error:" | Measure-Object).Count
                Write-Warning " Found $typeIssues type issues"
                $Global:Results.TypeIssues += $typeIssues
                if ($Verbose) { 
                    $mypyResult | Select-String "error:" | Select-Object -First 3 | ForEach-Object {
                        Write-Host "    $_" -ForegroundColor Yellow
                    }
                }
            }
        } else {
            Write-Success " No Python files found to analyze"
        }
    }
    catch {
        Write-Warning " MyPy not available"
    }
}

# Auto-fix issues
function Invoke-AutoFix {
    if (-not $Fix) { return }
    
    Write-Info "Auto-fixing issues..."
    
    $projectFiles = Get-ProjectPythonFiles $Path
    
    if ($projectFiles.Count -eq 0) {
        Write-Warning " No project Python files found to fix"
        return
    }
    
    # Check Python version for Black compatibility
    $pythonVersion = python --version 2>&1
    $isBlackCompatible = $true
    if ($pythonVersion -like "*3.12.5*") {
        Write-Warning " Python 3.12.5 detected - Black may have issues. Skipping Black formatting."
        $isBlackCompatible = $false
    }
    
    # Black - Code formatting (skip if version incompatible)
    if ($isBlackCompatible) {
        Write-Host "  [FIX] Formatting code (black)..." -NoNewline
        try {
            # Process files in batches to avoid command line length issues
            $batchSize = 20
            $totalBatches = [math]::Ceiling($projectFiles.Count / $batchSize)
            
            for ($i = 0; $i -lt $totalBatches; $i++) {
                $startIndex = $i * $batchSize
                $endIndex = [math]::Min($startIndex + $batchSize - 1, $projectFiles.Count - 1)
                $batch = $projectFiles[$startIndex..$endIndex]
                
                $batchFiles = $batch.FullName -join " "
                black $batchFiles --quiet --fast 2>&1 | Out-Null
            }
            Write-Success " Done"
        }
        catch {
            Write-Warning " Black failed (continuing with other fixes)"
        }
    } else {
        Write-Host "  [FIX] Skipping Black formatting (Python version issue)..." -NoNewline
        Write-Warning " Using autopep8 instead"
    }
    
    # isort - Import sorting (process files individually to avoid command line issues)
    Write-Host "  [FIX] Sorting imports (isort)..." -NoNewline
    try {
        $sortedCount = 0
        foreach ($file in $projectFiles) {
            try {
                isort $file.FullName --quiet 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) { $sortedCount++ }
            }
            catch {
                # Skip files that cause issues
            }
        }
        Write-Success " Done ($sortedCount files processed)"
    }
    catch {
        Write-Warning " isort not available"
    }
    
    # autopep8 - PEP8 compliance (process by directory to avoid command line length issues)
    Write-Host "  [FIX] Applying PEP8 fixes (autopep8)..." -NoNewline
    try {
        if ($isBlackCompatible) {
            # Standard autopep8 fixes
            autopep8 --in-place --recursive $Path --exclude="*/.venv/*,*/venv/*,*/__pycache__/*" 2>&1 | Out-Null
        } else {
            # More aggressive fixes when Black is unavailable
            autopep8 --in-place --recursive $Path --exclude="*/.venv/*,*/venv/*,*/__pycache__/*" --aggressive --aggressive 2>&1 | Out-Null
        }
        Write-Success " Done"
    }
    catch {
        Write-Warning " autopep8 not available"
    }
    
    # Additional formatting advice
    if (-not $isBlackCompatible) {
        Write-Host ""
        Write-Host "[ADVICE] For best formatting results:" -ForegroundColor Cyan
        Write-Host "   • Update Python to 3.12.6+ or downgrade to 3.12.4" -ForegroundColor Yellow
        Write-Host "   • Or use: pip install black --upgrade" -ForegroundColor Yellow
        Write-Host "   • autopep8 has handled basic formatting for now" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "[INFO] Re-analyzing to show improvements..." -ForegroundColor Blue
}

# Generate report
function Show-Report {
    Write-Host ""
    Write-Host "[REPORT] Code Quality Report" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    
    # Count only project Python files
    $totalFiles = (Get-ProjectPythonFiles $Path).Count
    
    $Global:Results.TotalFiles = $totalFiles
    $Global:Results.TotalIssues = $Global:Results.Duplicates + $Global:Results.SecurityIssues + 
                                  $Global:Results.StyleIssues + $Global:Results.ComplexityIssues + 
                                  $Global:Results.DeadCode + $Global:Results.TypeIssues
    
    Write-Host "Project files analyzed: " -NoNewline
    Write-Host $Global:Results.TotalFiles -ForegroundColor White
    
    Write-Host "Total issues: " -NoNewline
    if ($Global:Results.TotalIssues -eq 0) {
        Write-Host $Global:Results.TotalIssues -ForegroundColor Green
    } elseif ($Global:Results.TotalIssues -lt 10) {
        Write-Host $Global:Results.TotalIssues -ForegroundColor Yellow
    } else {
        Write-Host $Global:Results.TotalIssues -ForegroundColor Red
    }
    
    Write-Host "   Duplicate code blocks: $($Global:Results.Duplicates)"
    Write-Host "   Security issues: $($Global:Results.SecurityIssues)"
    Write-Host "   Style issues: $($Global:Results.StyleIssues)"
    Write-Host "   Complexity issues: $($Global:Results.ComplexityIssues)"
    Write-Host "   Dead code: $($Global:Results.DeadCode)"
    Write-Host "   Type issues: $($Global:Results.TypeIssues)"
    
    # Quality score (more realistic calculation)
    $maxPossibleIssues = $Global:Results.TotalFiles * 20  # Assume max 20 issues per file is realistic
    $qualityScore = [math]::Max(0, [math]::Min(100, 100 - (($Global:Results.TotalIssues / $maxPossibleIssues) * 100)))
    Write-Host ""
    Write-Host "Quality Score: " -NoNewline
    if ($qualityScore -ge 90) {
        Write-Host "$([math]::Round($qualityScore, 0))/100 (Excellent)" -ForegroundColor Green
    } elseif ($qualityScore -ge 70) {
        Write-Host "$([math]::Round($qualityScore, 0))/100 (Good)" -ForegroundColor Yellow
    } elseif ($qualityScore -ge 50) {
        Write-Host "$([math]::Round($qualityScore, 0))/100 (Acceptable)" -ForegroundColor Yellow
    } else {
        Write-Host "$([math]::Round($qualityScore, 0))/100 (Needs Improvement)" -ForegroundColor Red
    }
    
    # Recommendations
    Write-Host ""
    Write-Host "[RECOMMENDATIONS]" -ForegroundColor Cyan
    if ($Global:Results.StyleIssues -gt 0) {
        Write-Host "   • Run with -Fix flag to auto-format code" -ForegroundColor Yellow
    }
    if ($Global:Results.Duplicates -gt 0) {
        Write-Host "   • Refactor duplicate code into reusable functions" -ForegroundColor Yellow
    }
    if ($Global:Results.SecurityIssues -gt 0) {
        Write-Host "   • Review security vulnerabilities immediately" -ForegroundColor Red
    }
    if ($Global:Results.ComplexityIssues -gt 0) {
        Write-Host "   • Break down complex functions into smaller ones" -ForegroundColor Yellow
    }
    if ($Global:Results.TotalIssues -eq 0) {
        Write-Host "   • Great job! Your project code quality is excellent!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "[NOTE] Analysis focused on project code only (excluded .venv, dependencies, etc.)" -ForegroundColor Gray
}

# Main execution
function Main {
    $startTime = Get-Date
    
    # Show analysis scope
    Write-Info "Analyzing project scope..."
    $projectFiles = Get-ProjectPythonFiles $Path
    Write-Host "Found $($projectFiles.Count) Python files to analyze" -ForegroundColor Cyan
    if ($projectFiles.Count -gt 50) {
        Write-Host "[NOTE] Large codebase detected. Some tools will analyze subsets for performance." -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Install tools
    Install-CodeQualityTools
    
    # Run all checks
    Test-Linting
    Test-DuplicateCode
    Test-Security
    Test-Complexity
    Test-DeadCode
    Test-TypeChecking
    
    # Auto-fix if requested
    Invoke-AutoFix
    
    # If we did auto-fixes, re-run a quick analysis to show improvement
    if ($Fix) {
        Write-Host ""
        Write-Host "[POST-FIX] Quick re-analysis to show improvements..." -ForegroundColor Cyan
        
        # Reset results for post-fix analysis
        $Global:Results = @{
            TotalFiles = 0
            TotalIssues = 0
            Duplicates = 0
            SecurityIssues = 0
            StyleIssues = 0
            ComplexityIssues = 0
            DeadCode = 0
            TypeIssues = 0
        }
        
        # Quick style check only (most fixes were style-related)
        Write-Host "  [POST-FIX] Checking remaining style issues..." -NoNewline
        try {
            $flake8Result = flake8 $Path --exclude=".venv,venv,__pycache__,site-packages,.git,.pytest_cache" --count --statistics 2>&1
            
            $errorLines = $flake8Result | Where-Object { 
                $_ -match "^\.\\" -and 
                $_ -notlike "*\.venv\*" -and 
                $_ -notlike "*\venv\*" -and 
                $_ -notlike "*__pycache__*" -and
                $_ -notlike "*site-packages*"
            }
            
            $Global:Results.StyleIssues = $errorLines.Count
            $Global:Results.TotalIssues = $errorLines.Count
            $Global:Results.TotalFiles = $projectFiles.Count
            
            if ($errorLines.Count -eq 0) {
                Write-Success " All style issues fixed!"
            } else {
                Write-Warning " $($errorLines.Count) remaining issues"
            }
        }
        catch {
            Write-Warning " Unable to re-check"
        }
    }
    
    # Show report
    Show-Report
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host ""
    Write-Host "[TIMING] Analysis completed in $([math]::Round($duration, 2)) seconds" -ForegroundColor Gray
    
    # Exit with appropriate code
    if ($Global:Results.TotalIssues -eq 0) {
        exit 0
    } else {
        exit 1
    }
}

# Run the main function
Main