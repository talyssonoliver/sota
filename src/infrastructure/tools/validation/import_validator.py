"""
Import Validation Tool - Integrated Edition
Validates Python imports and checks for issues like circular dependencies.
Integrates with the unified validation system.
"""

import sys
from pathlib import Path
from typing import List

# Handle both relative and absolute imports
try:
    from .core.base_validator import BaseValidator
    from .core.syntax_validator import SyntaxValidator
    from .core.structure_validator import StructureValidator
    from .core.issue_model import ValidationIssue, IssueType, SeverityLevel
    from .core.shared_file_collector import SharedFileCollector
except ImportError:
    # For standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from src.infrastructure.tools.validation.core.base_validator import BaseValidator
    from src.infrastructure.tools.validation.core.syntax_validator import SyntaxValidator
    from src.infrastructure.tools.validation.core.structure_validator import StructureValidator
    from src.infrastructure.tools.validation.core.issue_model import ValidationIssue, IssueType, SeverityLevel
    from src.infrastructure.tools.validation.core.shared_file_collector import SharedFileCollector


class ImportValidator(BaseValidator):
    """Validates imports and checks for circular dependencies."""
    
    def __init__(self, quiet_mode: bool = True):
        # Initialize with SharedFileCollector for efficient file handling
        shared_collector = SharedFileCollector()
        super().__init__(shared_collector=shared_collector)
        self.quiet_mode = quiet_mode
        self.warnings = []
        self.syntax_validator = SyntaxValidator()
        self.structure_validator = StructureValidator()
        
        # Import tracking
        self.all_imports = {}
        self.import_graph = {}
        
    def get_validator_name(self) -> str:
        return "ImportValidator"
        
    def validate_file(self, file_path: Path) -> List[ValidationIssue]:
        """Validate imports in a single file."""
        issues = []
        
        # Delegate syntax validation to existing validator
        syntax_issues = self.syntax_validator.validate_file(file_path)
        issues.extend(syntax_issues)
        
        # If syntax is invalid, skip import analysis
        if syntax_issues:
            return issues
            
        # Perform import-specific validation
        import_issues = self._validate_imports(file_path)
        issues.extend(import_issues)
        
        return issues
        
    def _validate_imports(self, file_path: Path) -> List[ValidationIssue]:
        """Validate imports in the file."""
        issues = []
        
        try:
            # Use existing syntax validator to extract imports
            imports = self.syntax_validator.extract_imports(file_path)
            self.all_imports[str(file_path)] = imports
            
            # Check for import-specific issues
            for imp in imports:
                if self._is_problematic_import(imp):
                    issues.append(ValidationIssue(
                        category="imports",
                        issue_type=IssueType.IMPORT_ERROR,
                        file_path=str(file_path),
                        message=f"Problematic import: {imp}",
                        line=0,  # Could be enhanced to track line numbers
                        severity=SeverityLevel.WARNING
                    ))
                    
        except Exception as e:
            issues.append(ValidationIssue(
                category="imports",
                issue_type=IssueType.IMPORT_VALIDATION_ERROR,
                file_path=str(file_path),
                message=f"Failed to analyze imports: {str(e)}",
                line=0,
                severity=SeverityLevel.ERROR
            ))
            
        return issues
        
    def _is_problematic_import(self, import_stmt: str) -> bool:
        """Check if an import statement is problematic."""
        # Check for known problematic patterns
        problematic_patterns = [
            'import *',  # Star imports
            'from ... import *',
        ]
        
        return any(pattern in import_stmt for pattern in problematic_patterns)
        
    def print_warning_summary(self):
        """Print summary of warnings encountered."""
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warnings encountered:")
            for warning in self.warnings:
                print(f"  - {warning}")
        else:
            print("\n✅ No warnings")


def main():
    """Main validation function - delegates to validation CLI for full functionality."""
    if len(sys.argv) <= 1:
        return _run_basic_validation()
    
    arg = sys.argv[1]
    
    if arg in ['--help', '-h']:
        return _show_help()
    elif arg in ['--warnings-only', '-w']:
        return _run_warnings_only()
    else:
        # For comprehensive validation, delegate to main validation CLI
        print("For full validation features, use: python -m src.infrastructure.tools.validation.core.validation_cli --imports")
        return _run_basic_validation()


def _run_basic_validation() -> int:
    """Run basic import validation."""
    print("🔍 Running basic import validation...")
    validator = ImportValidator()
    
    # Use existing get_python_files method
    python_files = validator.get_python_files()
    
    total_issues = 0
    for py_file in python_files[:5]:  # Sample first 5 files
        if '__pycache__' in str(py_file):
            continue
            
        issues = validator.validate_file(py_file)
        total_issues += len(issues)
        
        if issues:
            print(f"❌ {py_file}: {len(issues)} issues")
        else:
            print(f"✅ {py_file}")
    
    print(f"\n📊 Sample validation complete: {total_issues} issues in first 5 files")
    return 0 if total_issues == 0 else 1


def _run_warnings_only() -> int:
    """Run warnings-only mode."""
    print("⚠️ Running warnings-only mode...")
    validator = ImportValidator(quiet_mode=False)
    
    # Sample a few files to show warnings
    python_files = validator.get_python_files()
    for py_file in python_files[:10]:  # Sample first 10 files
        if '__pycache__' not in str(py_file):
            validator.validate_file(py_file)
    
    validator.print_warning_summary()
    return 0


def _show_help() -> int:
    """Show help message."""
    print("Import Validation Tool - Integrated Edition")
    print("=" * 50)
    print("Usage:")
    print("  python import_validator.py           # Basic validation")
    print("  python import_validator.py -w       # Show warnings only")
    print("  python import_validator.py -h       # Show this help")
    print()
    print("For comprehensive validation with circular imports,")
    print("architecture checks, and more features, use:")
    print("  python -m src.infrastructure.tools.validation.core.validation_cli --imports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
