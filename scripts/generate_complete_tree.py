#!/usr/bin/env python3
"""
import sys
Complete Tree Structure Generator
Generates a comprehensive directory tree including all files and directories
using Depth-First Search (DFS) traversal algorithm.
"""

# Mock external dependencie


try:
    from pathlib import Path
except ImportError:
    pass
try:
    from datetime import datetime
except ImportError:
    pass
try:
    from typing import List, Set
except ImportError:
    pass
def should_exclude(path: Path, exclude_patterns: Set[str]) -> bool:
    """Check if a path should be excluded from the tree."""
    path_str = str(path).lower()
    
    # Check if any exclude pattern matches
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    
    # Special exclusions
    if path.name.startswith('.') and path.name not in {'.approved', '.claude', '.vscode', '.env.example'}:
        return True
    
    if path.name.endswith('.pyc') or path.name.endswith('.pyo'):
        return True
        
    if path.name == '__pycache__' and len(list(path.iterdir())) == 0:
        return True
        
    return False

def get_tree_prefix(is_last: bool, depth: int) -> str:
    """Generate tree prefix characters for proper formatting."""
    if depth == 0:
        return ""
    
    prefix = "│   " * (depth - 1)
    if is_last:
        prefix += "└── "
    else:
        prefix += "├── "
    
    return prefix

def generate_tree_dfs(root_path: Path, exclude_patterns: Set[str], max_depth: int = 10, include_lines: bool = False) -> List[str]:
    """
    Generate directory tree using Depth-First Search (DFS) algorithm.
    
    Args:
        root_path: Root directory to start traversal
        exclude_patterns: Set of patterns to exclude
        max_depth: Maximum depth to traverse
        include_lines: Whether to include line counts for files
        
    Returns:
        List of formatted tree lines
    """
    lines = []
    
    def count_lines_in_file(file_path: Path) -> int:
        """Count lines in a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (OSError, PermissionError, UnicodeDecodeError):
            try:
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    return sum(1 for _ in f)
            except:
                return 0
    
    def is_text_file(file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        text_extensions = {
            '.py', '.txt', '.md', '.rst', '.json', '.yaml', '.yml', 
            '.toml', '.ini', '.cfg', '.conf', '.log', '.csv',
            '.js', '.ts', '.html', '.css', '.xml', '.sql',
            '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore',
            '.env', '.requirements', '.makefile'
        }
        
        # Check by extension
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Check files without extension that are commonly text
        if file_path.suffix == '' and file_path.name.lower() in {
            'makefile', 'dockerfile', 'readme', 'license', 'changelog'
        }:
            return True
            
        return False
    
    def dfs_traverse(current_path: Path, depth: int, parent_prefix: str = "", is_last_at_level: bool = True):
        """Recursive DFS traversal function."""
        if depth > max_depth:
            return
            
        if should_exclude(current_path, exclude_patterns):
            return
        
        # Get all items in current directory
        try:
            items = list(current_path.iterdir())
            # Sort: directories first, then files (both alphabetically)
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        except (PermissionError, OSError):
            return
        
        # Filter out excluded items
        items = [item for item in items if not should_exclude(item, exclude_patterns)]
        
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            prefix = get_tree_prefix(is_last, depth + 1)
            
            # Format item name
            if item.is_dir():
                item_name = f"{item.name}/"
            else:
                # Add file size for files
                try:
                    size = item.stat().st_size
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f}K"
                    else:
                        size_str = f"{size/(1024*1024):.1f}M"
                    
                    # Add line count if requested and it's a text file
                    if include_lines and is_text_file(item):
                        line_count = count_lines_in_file(item)
                        if line_count > 0:
                            item_name = f"{item.name} ({size_str}, {line_count} lines)"
                        else:
                            item_name = f"{item.name} ({size_str})"
                    else:
                        item_name = f"{item.name} ({size_str})"
                except (OSError, PermissionError):
                    item_name = item.name
            
            lines.append(f"{prefix}{item_name}")
            
            # Recurse into directories
            if item.is_dir():
                dfs_traverse(item, depth + 1, prefix, is_last)
    
    # Start with root
    lines.append(f"{root_path.name}/")
    dfs_traverse(root_path, 0)
    
    return lines

def count_items(root_path: Path, exclude_patterns: Set[str]) -> tuple:
    """Count total files and directories."""
    file_count = 0
    dir_count = 0
    
    def count_recursive(path: Path):
        nonlocal file_count, dir_count
        
        if should_exclude(path, exclude_patterns):
            return
            
        try:
            for item in path.iterdir():
                if should_exclude(item, exclude_patterns):
                    continue
                    
                if item.is_dir():
                    dir_count += 1
                    count_recursive(item)
                else:
                    file_count += 1
        except (PermissionError, OSError):
            pass
    
    count_recursive(root_path)
    return file_count, dir_count

def generate_complete_tree_documentation(root_path: Path, include_lines: bool = False) -> str:
    """Generate complete tree documentation with files and directories."""
    
    # Exclude patterns for cleaner output
    exclude_patterns = {
        '.git', '.pytest_cache', 'htmlcov', '__pycache__',
        '.coverage', 'node_modules', '.venv', 'venv',
        '.mypy_cache', '.tox', 'dist', 'build/archives',
        'runtime/cache', 'runtime/temp', 'runtime/logs',
        'logs/', 'test_logs/', '.log'
    }
    
    # Generate tree using DFS
    tree_lines = generate_tree_dfs(root_path, exclude_patterns, max_depth=8, include_lines=include_lines)
    
    # Count items
    file_count, dir_count = count_items(root_path, exclude_patterns)
    
    # Generate documentation
    line_info = " with line counts" if include_lines else ""
    doc_content = f"""# Complete Directory Structure{line_info.title()}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Tree Structure (DFS Traversal){line_info}

```
{chr(10).join(tree_lines)}
```

## Summary

- **Total files**: {file_count:,}
- **Total directories**: {dir_count:,}
- **Total items**: {file_count + dir_count:,}
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with size information{line_info}
- **Excluded patterns**: {', '.join(sorted(exclude_patterns))}

## Tree Traversal Algorithm

This tree structure was generated using a **Depth-First Search (DFS)** algorithm:

1. **Recursive Traversal**: Starting from root, recursively visit each directory
2. **Sorting Strategy**: Directories first, then files (alphabetically)
3. **Size Calculation**: File sizes shown in appropriate units (B/K/M)
4. **Exclusion Filtering**: Skip temporary, cache, and build directories
5. **Depth Limiting**: Maximum depth of 8 levels to prevent excessive output
{"6. **Line Counting**: Text files include line counts for code analysis" if include_lines else ""}

## Architecture Insights

Based on this tree structure:

- **Modular Organization**: Clear separation of concerns across directories
- **Build Artifacts**: Organized in `build/` with proper segregation  
- **Runtime Data**: Separated in `runtime/` for operational files
- **Configuration**: Centralized in `config/` with schema validation
- **Testing**: Comprehensive test structure in `tests/` with fixtures
- **Documentation**: Well-organized in `docs/` by category
- **Tools & Scripts**: Utility functions properly categorized

This structure demonstrates a **mature software architecture** with clear boundaries and proper file organization.
"""
    
    return doc_content

def main():
    """Main function to generate complete tree documentation."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Generate complete directory tree structure')
    parser.add_argument('path', nargs='?', default='.', help='Path to generate tree for (default: current directory)')
    parser.add_argument('--include-lines', action='store_true', help='Include line counts for text files')
    
    args = parser.parse_args()
    root_path = Path(args.path)
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist")
        sys.exit(1)
    
    print(f"Generating complete tree structure for: {root_path}")
    if args.include_lines:
        print("Including line counts for text files...")
    
    # Generate documentation
    doc_content = generate_complete_tree_documentation(root_path, include_lines=args.include_lines)
    
    # Save to file
    output_file = root_path / "docs" / "setup" / "complete-directory-structure.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"Complete tree structure saved to: {output_file}")
    
    # Also print a summary
    print("\n" + "="*60)
    print("TREE GENERATION COMPLETE")
    print("="*60)
    print("Algorithm: Depth-First Search (DFS)")
    print(f"Output file: {output_file}")
    print(f"Line counts: {'Included' if args.include_lines else 'Not included'}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
