# Directory Tree Visualization Utility

## Overview

The `visualize_directory_tree.py` script is a comprehensive directory tree visualization utility that generates detailed project structure documentation using Depth-First Search (DFS) traversal algorithm.

## Location
`src/infrastructure/scripts/monitoring/visualize_directory_tree.py`

## Features

- **File sizes** in appropriate units (B/K/M)
- **Line counts** for text files (optional, disabled by default for performance)
- **Complete project structure** documentation
- **Auto-updates** directory-structure.md files
- **Multiple output formats** and options
- **DFS traversal algorithm** for systematic exploration
- **Exclusion patterns** for cleaner output

## Main Functions

### Core Functions
- **`is_text_file(file_path)`** (line ~42) - Check if a file is likely a text file
- **`count_lines_in_file(file_path)`** (line ~57) - Count lines in a text file with robust error handling
- **`format_size(size_bytes)`** (line ~75) - Format file size in appropriate units (B/K/M)
- **`should_exclude(path, exclude_patterns)`** (line ~83) - Check if a path should be excluded from the tree

### Tree Generation
- **`generate_tree_structure(root_path, max_depth, exclude_patterns, show_files, show_sizes, show_lines)`** (line ~99) - Generate ASCII tree structure using DFS traversal with enhanced information
- **`generate_tree_dfs_alternative(root_path, exclude_patterns, max_depth, include_lines)`** (line ~442) - Alternative DFS tree generation method
- **`get_tree_prefix(is_last, depth)`** (line ~421) - Generate tree prefix characters for proper formatting

### Documentation Generation
- **`update_directory_structure_files(tree_structure, file_count, dir_count, total_lines, root_path, exclude_patterns)`** (line ~230) - Update both directory structure documentation files
- **`generate_complete_tree_documentation(root_path, include_lines)`** (line ~345) - Generate complete tree documentation with files and directories

### Utility Functions
- **`count_items_alternative(root_path, exclude_patterns)`** (line ~497) - Count total files and directories
- **`main()`** (line ~515) - Command-line interface for directory tree visualization

## Usage

### Basic Usage
```bash
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py
```

### Advanced Options
```bash
# Generate with line counts
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --lines

# Generate complete documentation
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --simple-format

# Update documentation files
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --update-docs

# Save to custom file
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --output file.md

# Show directories only
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --dirs-only

# Set maximum depth
python src/infrastructure/scripts/monitoring/visualize_directory_tree.py --max-depth 5
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Directory path to visualize | current directory |
| `--output`, `-o` | Output file path (markdown format) | stdout |
| `--max-depth`, `-d` | Maximum depth to traverse | 8 |
| `--dirs-only` | Show directories only (no files) | false |
| `--no-sizes` | Don't show file sizes | false |
| `--lines` | Show line counts for text files | false |
| `--exclude` | Additional patterns to exclude | none |
| `--update-docs` | Update directory-structure.md files automatically | false |
| `--include-lines` | Include line counts for text files | false |
| `--simple-format` | Use simplified documentation format | false |

## Default Exclusion Patterns

The script automatically excludes these patterns:
- `__pycache__`, `.git`, `.venv`, `venv`, `node_modules`
- `.pytest_cache`, `htmlcov`, `.coverage`, `.mypy_cache`
- `.tox`, `dist`, `build`, `deployment`, `.ruff_cache`
- `runtime/cache`, `runtime/temp`, `runtime/logs`

## Algorithm Details

### Depth-First Search (DFS) Traversal
1. **Recursive Traversal**: Starting from root, recursively visit each directory
2. **Sorting Strategy**: Directories first, then files (both alphabetically)
3. **Size Calculation**: File sizes shown in appropriate units (B/K/M)
4. **Line Counting**: Text files include line counts for code analysis (when enabled)
5. **Exclusion Filtering**: Skip temporary, cache, and build directories
6. **Depth Limiting**: Maximum depth of 8 levels to prevent excessive output

### Text File Detection
The script identifies text files by:
- **Extensions**: `.py`, `.txt`, `.md`, `.rst`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.log`, `.csv`, `.js`, `.ts`, `.html`, `.css`, `.xml`, `.sql`, `.sh`, `.bat`, `.ps1`, `.dockerfile`, `.gitignore`, `.env`, `.requirements`, `.makefile`
- **Special files**: `makefile`, `dockerfile`, `readme`, `license`, `changelog` (without extension)

## Output Formats

### Standard Output
- Console output with tree structure
- File counts and directory counts
- Optional line counts summary

### Markdown Documentation
- Complete tree structure in markdown format
- Summary statistics
- Algorithm details and architecture insights
- File type analysis

### Documentation Files
- `docs/setup/directory-structure.md` - Simplified directory-only view
- `docs/setup/complete-directory-structure.md` - Complete structure with files and metadata

## Performance Considerations

- **Line counting disabled by default** for better performance
- **Maximum depth limiting** to prevent excessive output
- **Exclusion patterns** to skip unnecessary directories
- **Error handling** for permission issues and broken symlinks
- **Efficient sorting** and filtering algorithms

## Error Handling

The script includes robust error handling for:
- **Permission errors** when accessing restricted directories
- **Broken symlinks** that can't be resolved
- **Unicode decode errors** when reading files
- **File system errors** during traversal

## Integration

This utility integrates with the project's documentation system by:
- **Auto-updating** documentation files when requested
- **Generating** consistent markdown output
- **Providing** architecture insights based on file structure
- **Supporting** CI/CD documentation workflows
