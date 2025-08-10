#!/usr/bin/env python3
"""
Quick fix for try block import issues after consolidation
"""

import re
from pathlib import Path

def fix_try_block_imports():
    """Fix try blocks that were incorrectly commented out during consolidation"""
    src_path = Path("src")
    files_fixed = 0
    
    for file_path in src_path.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern: try: followed by # ... # Consolidated to common_imports
            # Fix by replacing the commented import with proper import from common_imports
            
            # Replace patterns like:
            # try:
            # #     import yaml  # Consolidated to common_imports  
            # except ImportError:
            
            patterns = [
                (r'try:\s*\n\s*#\s*import (\w+)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from datetime import (\w+(?:,\s*\w+)*)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from pathlib import (\w+)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from typing import ([^#\n]+)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from dataclasses import (\w+(?:,\s*\w+)*)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from enum import (\w+)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
                
                (r'try:\s*\n\s*#\s*from collections import ([^#\n]+)\s*#\s*Consolidated to common_imports\s*\nexcept ImportError:',
                 r'try:\n    from src.infrastructure.utils.common_imports import \1\nexcept ImportError:'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Handle other try block patterns that might exist
            # Pattern for inside functions/methods with more complex indentation
            content = re.sub(
                r'(\s+)try:\s*\n\s*#\s*import (\w+)\s*#\s*Consolidated to common_imports\s*\n(\s+)except ImportError:',
                r'\1try:\n\1    from src.infrastructure.utils.common_imports import \2\n\3except ImportError:',
                content,
                flags=re.MULTILINE
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_fixed += 1
                print(f"✅ Fixed: {file_path}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n🎉 Fixed {files_fixed} files with try block import issues")

if __name__ == "__main__":
    fix_try_block_imports()