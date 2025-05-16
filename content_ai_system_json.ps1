param(
    [string]$rootPath     = "C:\taly\ai-system",
    [string[]]$excludeDirs = @(
        "node_modules", ".bin", ".husky", "dist", ".swc", ".cache",
        ".git", "coverage", "logs", "tmp", "out", ".vscode", ".next",
        ".turbo", "pnpm-store", "__pycache__", ".pytest_cach", ".venv"
    ),
    [string[]]$excludeFiles = @(
        "pnpm-lock.yaml", ".prettierrc", ".vscodeignore", "turbo.json"
    ),
    [string]$outputFile    = "C:\taly\ai-system\projectContentAiSystem.txt",
    [switch]$maskSecrets,                # Added: Mask API keys and sensitive data
    [int]$maxFileSize      = 50000,                
    [switch]$includeContent,             # Added: Option to include file contents
    [switch]$skipLargeFiles,             # Added: Option to skip large binary files
    [int]$maxLargeFileSize  = 1024 * 1024,         # Added: Maximum size for files to include (1MB default)
    [string]$secondaryOutputFile = "C:\taly\projectContentAiSystem.json"  # Added: Secondary output location
)

# Initialize default values for switches
if (-not $PSBoundParameters.ContainsKey('maskSecrets')) { $maskSecrets = $true }
if (-not $PSBoundParameters.ContainsKey('includeContent')) { $includeContent = $true }
if (-not $PSBoundParameters.ContainsKey('skipLargeFiles')) { $skipLargeFiles = $true }

# remove existing output
Remove-Item -Path $outputFile -ErrorAction SilentlyContinue
New-Item -ItemType File -Path $outputFile | Out-Null

# If secondary output is specified, prepare that too
if ($secondaryOutputFile) {
    Remove-Item -Path $secondaryOutputFile -ErrorAction SilentlyContinue
    New-Item -ItemType File -Path $secondaryOutputFile | Out-Null
}

# supported text extensions
$extensoesTexto = @(
    ".md", ".env", ".env.local", ".mjs", ".txt", ".json", ".babelrc",
    ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx", ".html", ".css",
    ".scss", ".sh", ".ps1", ".sql", ".graphql", ".toml", ".ini",
    ".local" , ".config", ".dockerfile", ".gitignore", ".npmrc", ".py", ".log"
)

function IsExcluded($filePath, $excludedDirs, $excludedFiles) {
    foreach ($dir in $excludedDirs) {
        if ($filePath -match "\\$dir\\") { return $true }
    }
    foreach ($file in $excludedFiles) {
        if ($filePath -match "\\$file$") { return $true }
    }
    return $false
}

# Function to mask sensitive information
function MaskSensitiveData($content) {
    if (-not $maskSecrets) { return $content }
    
    # Mask API keys and tokens
    $maskedContent = $content -replace '(api[-_]?key["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(API[-_]?KEY["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(token["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(TOKEN["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(password["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(PASSWORD["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(secret["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    $maskedContent = $maskedContent -replace '(SECRET["''\s:=]+["'']?)([^"''\s]+)(["'']?)', '$1********$3'
    
    # Specifically mask OpenAI API keys (sk-...)
    $maskedContent = $maskedContent -replace '(sk-[a-zA-Z0-9]{16})[a-zA-Z0-9]+', '$1********'
    
    # Mask JWT tokens - Using single quotes to avoid variable interpolation issues
    $maskedContent = $maskedContent -replace '(eyJ[a-zA-Z0-9_-]{5,})[.](eyJ[a-zA-Z0-9_-]{5,})[.][a-zA-Z0-9_-]+', '$1.$2.********'
    
    return $maskedContent
}

# Structure to hold information about file dependencies and import relationships
$fileRelationships = @{}
$directoryMap = @{}
$filesByExtension = @{}
$importantFiles = @()

$files = [System.Collections.Generic.List[object]]::new()
$contadorArquivos = 0
$errorCount = 0

# First pass - collect all files
try {
    $allFiles = Get-ChildItem -Path $rootPath -Recurse -File -ErrorAction Continue | 
        Where-Object {
            -not (IsExcluded $_.FullName $excludeDirs $excludeFiles) -and
            (
                ($extensoesTexto -contains $_.Extension.ToLower()) -and
                ((-not $skipLargeFiles) -or ($_.Length -lt $maxLargeFileSize))
            )
        }
} catch {
    Write-Warning "Error while collecting files: $_"
    $errorCount++
}

# Map directory structure for easier navigation
$allFiles | ForEach-Object {
    try {
        $dir = Split-Path -Path $_.FullName -Parent
        $relativeDir = $dir.Replace($rootPath, "").TrimStart("\")
        
        if (-not $directoryMap.ContainsKey($relativeDir)) {
            $directoryMap[$relativeDir] = @()
        }
        $directoryMap[$relativeDir] += $_.Name
        
        # Group files by extension
        $ext = $_.Extension.ToLower()
        if (-not $filesByExtension.ContainsKey($ext)) {
            $filesByExtension[$ext] = @()
        }
        $filesByExtension[$ext] += $_.FullName.Replace($rootPath, "").TrimStart("\")
        
        # Identify potentially important files
        if ($_.Name -match "^(main|index)\." -or 
            $_.Name -eq "README.md" -or 
            $_.FullName -match "\\config\\" -or
            $_.Name -match "schema") {
            $importantFiles += $_.FullName.Replace($rootPath, "").TrimStart("\")
        }
    } catch {
        Write-Warning "Error processing file $($_.FullName): $_"
        $errorCount++
    }
}

# Second pass - read files and process content
$allFiles | ForEach-Object {
    try {
        $contadorArquivos++
        $raw = ""
        
        # Skip content if not required
        if ($includeContent) {
            try {
                # Ensure $raw is treated as a plain string
                $raw = [string](Get-Content -Path $_.FullName -Raw -Encoding utf8 -ErrorAction SilentlyContinue)
                if ($raw.Length -eq 0) {
                    $raw = "[Empty file]"
                } elseif ($raw.Length -gt $maxFileSize) {
                    $raw = $raw.Substring(0, $maxFileSize) + "`n[...truncated...]"
                }
                
                # Mask sensitive data in known sensitive files
                if ($_.Extension -eq ".env" -or $_.Name -like "*secret*" -or $_.Name -like "*credential*") {
                    $raw = MaskSensitiveData($raw)
                }
                
                # Simple detection of imports/requires to build relationship graph
                if ($_.Extension -match "\.(js|jsx|ts|tsx|py)$") {
                    $relativePath = $_.FullName.Replace($rootPath, "").TrimStart("\")
                    $fileRelationships[$relativePath] = @{
                        "imports" = @()
                        "importedBy" = @()
                    }
                    
                    # Extract imports using regex
                    if ($_.Extension -match "\.(js|jsx|ts|tsx)$") {
                        $imports = [regex]::Matches($raw, '(import .+ from [''"](.+)[''"]|require\([''"](.+)[''"]\))')
                        foreach ($import in $imports) {
                            $importPath = if ($import.Groups[2].Value) { $import.Groups[2].Value } else { $import.Groups[3].Value }
                            $fileRelationships[$relativePath]["imports"] += $importPath
                        }
                    }
                    elseif ($_.Extension -eq ".py") {
                        $imports = [regex]::Matches($raw, '(from .+ import|import .+)')
                        foreach ($import in $imports) {
                            $fileRelationships[$relativePath]["imports"] += $import.Value
                        }
                    }
                }
            } catch {
                $raw = "[Error reading file: $_]"
                $errorCount++
            }
        } else {
            $raw = "[Content skipped due to includeContent=false]"
        }

        # Assign the raw string directly to the Content property
        $obj = [PSCustomObject]@{
            FileName     = $_.Name
            RelativePath = $_.FullName.Replace($rootPath, "").TrimStart("\\") # Keep relative path, it's essential
            Extension    = $_.Extension.ToLower() # Keep extension, it's small and useful
            Content      = $raw 
        }
        $files.Add($obj)
    } catch {
        Write-Warning "Error processing file data for $($_.FullName): $_"
        $errorCount++
    }
}

# Process the second part of relationship mapping (importedBy)
foreach ($file in $fileRelationships.Keys) {
    try {
        foreach ($import in $fileRelationships[$file]["imports"]) {
            # Try to resolve the import to an actual file
            $possibleFiles = $allFiles | Where-Object { 
                $_.FullName.Replace($rootPath, "").TrimStart("\") -like "*$import*" -or
                $_.Name -like "*$import*"
            }
            
            foreach ($possibleFile in $possibleFiles) {
                $importPath = $possibleFile.FullName.Replace($rootPath, "").TrimStart("\")
                if ($fileRelationships.ContainsKey($importPath)) {
                    if ($fileRelationships[$importPath]["importedBy"] -notcontains $file) {
                        $fileRelationships[$importPath]["importedBy"] += $file
                    }
                }
            }
        }
    } catch {
        # Fix the variable reference error by using $() to properly evaluate the $_ variable
        Write-Warning "Error processing relationships for file ${file}: $($_)"
        $errorCount++
    }
}

# Generate project structure for the metadata
$rootDirs = $directoryMap.Keys | Where-Object { $_ -notmatch "\\" } | Sort-Object
$projectStructure = @{}
foreach ($dir in $rootDirs) {
    if ($dir -eq "") { 
        $projectStructure["root"] = $directoryMap[""]
    } else {
        $projectStructure[$dir] = $directoryMap[$dir]
    }
}

# Add metadata and project summary for LLM processing
$projectMetadata = @{
    "ProjectName" = "AI System"
    "Description" = "This project automates workflows using LangGraph and specialized agents."
    "RootPath" = $rootPath
    "FileCount" = $contadorArquivos
    "GeneratedOn" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "KeyComponents" = @(
        "Agents for task execution",
        "Graph-based workflow orchestration",
        "Critical path analysis",
        "Integration with external tools"
    )
    "ImportantFiles" = $importantFiles
    "FileTypes" = $filesByExtension.Keys | ForEach-Object { 
        @{
            "Extension" = $_
            "Count" = $filesByExtension[$_].Count
            "Examples" = if ($filesByExtension[$_].Count -gt 3) { $filesByExtension[$_][0..2] } else { $filesByExtension[$_] }
        }
    }
    "ProjectStructure" = $projectStructure
}

# Add LLM instructions on how to navigate the code
$llmInstructions = @{
    "FileName" = "_LLM_INSTRUCTIONS.md"
    "Path" = "Generated dynamically"
    "RelativePath" = $null
    "Extension" = $null
    "Content" = @"
# Instructions for LLM Code Understanding

This JSON file contains the source code and structure of the AI Agent System project.

## How to navigate this project:

1. **Start with key files:**
   - README.md - Project overview
   - main.py - Entry point
   - config/agents.yaml - Agent configuration
   - config/tools.yaml - Available tools

2. **Key directories:**
   - agents/ - Agent implementation files
   - graph/ - LangGraph workflow definitions
   - orchestration/ - Task orchestration logic
   - tools/ - Tool implementations

3. **Understanding the architecture:**
   - The system uses specialized agents (Technical Lead, Backend Engineer, etc.)
   - Agents communicate via LangGraph (in the graph/ directory)
   - Agent tasks are defined in task YAML files
   - Tools provide agents with capabilities (database queries, etc.)

4. **Request strategies:**
   - For architecture questions: Look at docs/ and graph/ directories
   - For agent capabilities: Check agents/ and their prompts in prompts/
   - For workflow questions: Examine graph/ and orchestration/
   - For tool functionality: Study tools/ directory

This project uses LangChain, LangGraph, and CrewAI to implement an agent-based system
for automating software development tasks, with MCP (Memory Context Protocol) for
context-aware operations.
"@
    "Size" = $null
    "LastModified" = $null
}

# Add project summary
$projectSummary = @{
    "FileName" = "_PROJECT_SUMMARY.md"
    "Path" = "Generated dynamically"
    "RelativePath" = $null
    "Extension" = $null
    "Content" = @"
# AI Agent System Project Summary

## Overview
This project implements a multi-agent AI system that automates software development tasks for the Artesanato E-commerce platform. It uses specialized agents, each focused on a specific role in the development process, coordinated through a LangGraph-based workflow system.

## Architecture
- **Agents**: Specialized roles (Technical Lead, Backend, Frontend, etc.) implemented with CrewAI
- **Workflow**: LangGraph-based task orchestration with dependency tracking
- **Memory**: Vector database (ChromaDB) for context-aware operations
- **Tools**: Specialized capabilities for agents (Supabase, GitHub, etc.)

## Key Components
1. **Agent System**: Defined in agents/ directory with role-specific implementations
2. **Workflow Engine**: Implemented in graph/ directory using LangGraph
3. **Tool System**: Provides agent capabilities in tools/ directory
4. **Orchestration**: Manages task execution in orchestration/ directory
5. **Context Store**: Knowledge base for agents in context-store/ directory

## Getting Started
See README.md for installation and usage instructions.

## Technology Stack
- LangChain/LangGraph for agent communication and workflow
- CrewAI for role-specialized agents
- ChromaDB for vector storage and context retrieval
- OpenAI models for agent intelligence
- Supabase for database operations
"@
    "Size" = $null
    "LastModified" = $null
}

# Add project relationships to help LLM understand connections
$fileRelationshipSummary = @{
    "FileName" = "_FILE_RELATIONSHIPS.json"
    "Path" = "Generated dynamically"
    "RelativePath" = $null
    "Extension" = $null
    "Content" = ($fileRelationships | ConvertTo-Json -Depth 5)
    "Size" = $null
    "LastModified" = $null
}

# Add the new entries to files collection
$files.Add([PSCustomObject]$llmInstructions)
$files.Add([PSCustomObject]$projectSummary)
$files.Add([PSCustomObject]$fileRelationshipSummary)

# Add the metadata to the output JSON at the beginning
$completeOutput = @{
    "ProjectMetadata" = $projectMetadata
    "Files" = $files | Select-Object FileName, Path, RelativePath, Extension, Content, Size, LastModified
}

# Write the enhanced output with metadata
try {
    $completeOutput | ConvertTo-Json -Depth 6 -Compress:$false | Set-Content -Path $outputFile -Encoding utf8
    
    # If a secondary output file is specified, copy the output there too
    if ($secondaryOutputFile) {
        $completeOutput | ConvertTo-Json -Depth 6 -Compress:$false | Set-Content -Path $secondaryOutputFile -Encoding utf8
    }
    
    Write-Host "Process completed! Total files processed: $contadorArquivos"
    Write-Host "Project content saved to: $outputFile"
    if ($secondaryOutputFile) {
        Write-Host "Secondary copy saved to: $secondaryOutputFile"
    }
    if ($errorCount -gt 0) {
        Write-Warning "Completed with $errorCount errors. Check warnings above."
    }
    Write-Host "File enhanced for better LLM understanding with metadata and file relationships."
} catch {
    Write-Error "Error saving output file: $_"
}