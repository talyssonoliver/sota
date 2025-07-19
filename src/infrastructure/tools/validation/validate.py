#!/usr/bin/env python3
"""
Validation CLI Entry Point
Modern validation system with unified architecture.
"""

import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.tools.validation.core.validation_cli import ValidationCLI


def main():
    """Main CLI entry point."""
    print("🚀 Validation System v3.0")
    print("=" * 50)
    
    # Create and run CLI
    cli = ValidationCLI()
    success = cli.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
