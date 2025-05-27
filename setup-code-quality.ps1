# setup-code-quality.ps1 - Setup script for Code Quality Checker
param(
    [switch]$SkipPowerShellConfig,
    [switch]$CreateVSCodeTasks,
    [switch]$SetupGitHooks,
    [switch]$Minimal
)

Write-Host "[SETUP] Setting up AI System Code Quality Checker" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }

# Check PowerShell execution policy
function Test-ExecutionPolicy {
    $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
    if ($currentPolicy -eq "Restricted" -or $currentPolicy -eq "AllSigned") {
        Write-Warning "PowerShell execution policy is restrictive: $currentPolicy"
        Write-Host "Setting execution policy to RemoteSigned for current user..."
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-Success "Execution policy updated"
        }
        catch {
            Write-Error "Failed to update execution policy. Run as administrator or update manually."
            return $false
        }
    }
    return $true
}

# Install Python tools
function Install-PythonTools {
    Write-Info "Installing Python code quality tools..."
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Python not found. Please install Python 3.8+ first."
        Write-Host "Download from: https://www.python.org/downloads/"
        return $false
    }
    
    # Install tools
    $tools = @(
        "flake8",
        "black", 
        "isort",
        "bandit",
        "radon",
        "vulture", 
        "mypy",
        "pylint",
        "duplicated",
        "safety",
        "autopep8"
    )
    
    foreach ($tool in $tools) {
        Write-Host "  Installing $tool..." -NoNewline
        try {
            pip install $tool --upgrade --quiet
            Write-Success " Done"
        }
        catch {
            Write-Error " Failed"
        }
    }
    
    return $true
}

# Create configuration files
function New-ConfigurationFiles {
    Write-Info "Creating configuration files..."
    
    # .flake8 configuration
    $flake8Config = @"
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .pytest_cache,
    build,
    dist
max-complexity = 10
"@
    
    if (-not (Test-Path ".flake8")) {
        $flake8Config | Out-File -FilePath ".flake8" -Encoding UTF8
        Write-Success "Created .flake8 configuration"
    }
    
    # pyproject.toml for black and isort
    $pyprojectConfig = @"
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line-length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
"@
    
    if (-not (Test-Path "pyproject.toml")) {
        $pyprojectConfig | Out-File -FilePath "pyproject.toml" -Encoding UTF8
        Write-Success "Created pyproject.toml configuration"
    }
    
    # mypy.ini
    $mypyConfig = @"
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = True
check_untyped_defs = True  
warn_redundant_casts = True
ignore_missing_imports = True
"@
    
    if (-not (Test-Path "mypy.ini")) {
        $mypyConfig | Out-File -FilePath "mypy.ini" -Encoding UTF8
        Write-Success "Created mypy.ini configuration"
    }
}

# Setup PowerShell profile aliases
function Set-PowerShellAliases {
    if ($SkipPowerShellConfig) { return }
    
    Write-Info "Setting up PowerShell aliases..."
    
    $aliases = @"

# Code Quality Checker Aliases
function lintcode { .\code-quality.ps1 @args }
function fixcode { .\code-quality.ps1 -Fix @args }
function checkcode { .\code-quality.ps1 -Verbose @args }
function quicklint { .\code-quality.ps1 -SkipInstall @args }

"@
    
    try {
        if (Test-Path $PROFILE) {
            $currentProfile = Get-Content $PROFILE -Raw
            if ($currentProfile -notlike "*lintcode*") {
                Add-Content -Path $PROFILE -Value $aliases
                Write-Success "Added aliases to PowerShell profile"
                Write-Info "Restart PowerShell to use aliases: lintcode, fixcode, checkcode"
            } else {
                Write-Info "Aliases already exist in profile"
            }
        } else {
            New-Item -Path $PROFILE -ItemType File -Force | Out-Null
            Set-Content -Path $PROFILE -Value $aliases
            Write-Success "Created PowerShell profile with aliases"
        }
    }
    catch {
        Write-Warning "Could not modify PowerShell profile. You can manually add aliases."
    }
}

# Create VS Code tasks
function New-VSCodeTasks {
    if (-not $CreateVSCodeTasks) { return }
    
    Write-Info "Creating VS Code tasks..."
    
    if (-not (Test-Path ".vscode")) {
        New-Item -Path ".vscode" -ItemType Directory | Out-Null
    }
    
    $tasksContent = @'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Lint Code",
            "type": "shell",
            "command": "powershell",
            "args": ["-File", "code-quality.ps1"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Fix Code",
            "type": "shell", 
            "command": "powershell",
            "args": ["-File", "code-quality.ps1", "-Fix"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always", 
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Check Code (Verbose)",
            "type": "shell",
            "command": "powershell", 
            "args": ["-File", "code-quality.ps1", "-Verbose"],
            "group": "build"
        }
    ]
}
'@
    
    $tasksContent | Out-File -FilePath ".vscode/tasks.json" -Encoding UTF8
    Write-Success "Created VS Code tasks (Ctrl+Shift+P > Tasks: Run Task)"
}

# Setup Git hooks
function Set-GitHooks {
    if (-not $SetupGitHooks) { return }
    
    Write-Info "Setting up Git hooks..."
    
    if (-not (Test-Path ".git")) {
        Write-Warning "Not a Git repository. Skipping Git hooks setup."
        return
    }
    
    $preCommitHook = @"
#!/bin/sh
# Pre-commit hook: Run code quality check
echo "Running code quality check..."
powershell.exe -File code-quality.ps1 -SkipInstall
if [ `$? -ne 0 ]; then
    echo "[ERROR] Code quality check failed. Fix issues before committing."
    echo "Run 'fixcode' to auto-fix formatting issues."
    exit 1
fi
echo "[SUCCESS] Code quality check passed."
"@
    
    $hookPath = ".git/hooks/pre-commit"
    $preCommitHook | Out-File -FilePath $hookPath -Encoding UTF8
    
    # Make executable (if on Unix-like system)
    try {
        if (Get-Command "chmod" -ErrorAction SilentlyContinue) {
            chmod +x $hookPath
        }
        Write-Success "Created Git pre-commit hook"
    }
    catch {
        Write-Success "Created Git pre-commit hook (may need manual chmod +x)"
    }
}

# Create shortcuts and batch files
function New-Shortcuts {
    Write-Info "Creating convenience shortcuts..."
    
    # Batch file for CMD users
    $batchContent = @"
@echo off
powershell -File "%~dp0code-quality.ps1" %*
"@
    
    $batchContent | Out-File -FilePath "lint.bat" -Encoding ASCII
    Write-Success "Created lint.bat for CMD users"
    
    # Quick fix batch file
    $fixBatchContent = @"
@echo off
powershell -File "%~dp0code-quality.ps1" -Fix %*
"@
    
    $fixBatchContent | Out-File -FilePath "fix.bat" -Encoding ASCII
    Write-Success "Created fix.bat for quick fixes"
}

# Main setup function
function Main {
    Write-Host ""
    
    # Test execution policy
    if (-not (Test-ExecutionPolicy)) {
        return
    }
    
    # Install Python tools
    if (-not (Install-PythonTools)) {
        return
    }
    
    # Create configuration files
    if (-not $Minimal) {
        New-ConfigurationFiles
        Set-PowerShellAliases
        New-VSCodeTasks
        Set-GitHooks
        New-Shortcuts
    }
    
    Write-Host ""
    Write-Success "Setup completed successfully!"
    Write-Host ""
    Write-Host "[QUICK START]" -ForegroundColor Cyan
    Write-Host "  .\code-quality.ps1           # Check code quality"
    Write-Host "  .\code-quality.ps1 -Fix      # Auto-fix issues"
    Write-Host "  .\code-quality.ps1 -Verbose  # Detailed output"
    Write-Host ""
    Write-Host "[FILES CREATED]"
    Write-Host "  • code-quality.ps1     # Main script"
    Write-Host "  • .flake8             # Style configuration"
    Write-Host "  • pyproject.toml      # Tool configuration"
    Write-Host "  • mypy.ini            # Type checking config"
    
    if (-not $Minimal) {
        Write-Host "  • lint.bat            # CMD shortcut"
        Write-Host "  • fix.bat             # Quick fix shortcut"
        
        if ($CreateVSCodeTasks) {
            Write-Host "  • .vscode/tasks.json   # VS Code tasks"
        }
        
        if ($SetupGitHooks) {
            Write-Host "  • .git/hooks/pre-commit # Git hook"
        }
    }
    
    Write-Host ""
    Write-Host "[USAGE EXAMPLES]" -ForegroundColor Cyan
    Write-Host "  lintcode              # Quick check (after profile reload)"
    Write-Host "  fixcode -Verbose      # Fix with details"
    Write-Host "  checkcode -Path src/  # Check specific folder"
    Write-Host ""
    Write-Host "[NOTE] Restart PowerShell to use the new aliases!" -ForegroundColor Yellow
}

# Run setup
Main