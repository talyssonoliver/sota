"""
Syntax Validator
Validates Python syntax and extract import statements safely.
"""

import ast
from pathlib import Path
from typing import List, Optional, Set

from .base_validator import BaseValidator
from .issue_model import IssueType, SeverityLevel, ValidationIssue


class SyntaxValidator(BaseValidator):
    """Validates Python syntax and extracts import statements."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize syntax validator."""
        super().__init__(root_path)
        self.syntax_errors: List[tuple] = []
        self.handled_imports: Set[str] = set()

    def validate(self, files: List[Path]) -> List[ValidationIssue]:
        """Validate syntax for the given files."""
        issues = []

        for file_path in files:
            if not self.validate_syntax(file_path):
                issues.append(
                    ValidationIssue(
                        category="syntax",
                        issue_type=IssueType.SYNTAX_ERROR,
                        file_path=str(file_path),
                        message="Syntax error in file",
                        severity=SeverityLevel.ERROR,
                    )
                )

        return issues

    def validate_syntax(self, py_file: Path) -> bool:
        """Validate Python syntax without executing imports."""
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.add_issue(
                category="syntax",
                issue_type="SYNTAX_ERROR",
                file_path=str(py_file),
                message=f"Syntax error: {e}",
                severity="error",
                line=e.lineno if hasattr(e, "lineno") else None,
            )
            self.syntax_errors.append((py_file, f"Syntax error: {e}"))
            return False
        except Exception as e:
            self.add_issue(
                category="syntax",
                issue_type="PARSE_ERROR",
                file_path=str(py_file),
                message=f"Parse error: {e}",
                severity="error",
            )
            self.syntax_errors.append((py_file, f"Parse error: {e}"))
            return False

    def extract_imports(self, py_file: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        imports = []
        handled_imports = set()  # Track imports handled by try/except

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # First pass: identify imports in try/except blocks
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    # Check if any import statements are in the try block
                    for try_node in node.body:
                        if isinstance(try_node, ast.Import):
                            for alias in try_node.names:
                                handled_imports.add(alias.name)
                        elif isinstance(try_node, ast.ImportFrom):
                            if try_node.module:
                                # For 'from x.y import z', we want to track 'x.y'
                                handled_imports.add(try_node.module)
                                # Also track submodules if they exist
                                module_parts = try_node.module.split(".")
                                for i in range(len(module_parts)):
                                    partial_module = ".".join(module_parts[: i + 1])
                                    handled_imports.add(partial_module)

            # Second pass: collect all imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Mark relative imports with a prefix so we can handle them differently
                        if node.level > 0:  # This is a relative import
                            imports.append("." + node.module)
                        else:
                            imports.append(node.module)

            # Store handled imports for later use
            self.handled_imports = handled_imports

        except Exception as e:
            self.add_issue(
                category="syntax",
                issue_type="IMPORT_EXTRACTION_ERROR",
                file_path=str(py_file),
                message=f"Could not extract imports: {e}",
                severity="warning",
            )

        return imports

    def validate_import(self, import_name: str, source_file: Path) -> bool:
        """Validate a single import statement (syntax-level validation only)."""
        try:
            # Handle relative imports
            if import_name.startswith("."):
                return True  # Relative imports are syntactically valid

            # Skip actual import validation - we only validate syntax, not availability
            # This prevents failures due to optional dependencies or development packages
            
            # Only check for obviously invalid import patterns
            if not import_name or import_name.isspace():
                self.add_issue(
                    category="imports",
                    issue_type="INVALID_IMPORT_NAME",
                    file_path=str(source_file),
                    message=f"Invalid import name: '{import_name}'",
                    severity="error",
                )
                return False
            
            # Check for common syntax errors in import names
            if any(char in import_name for char in ['/', '\\', ':', ';', '"', "'"]):
                self.add_issue(
                    category="imports",
                    issue_type="INVALID_IMPORT_SYNTAX",
                    file_path=str(source_file),
                    message=f"Invalid characters in import name: '{import_name}'",
                    severity="error",
                )
                return False
            
            # If import is in try/except block, log it as optional but don't fail validation
            if import_name in self.handled_imports:
                self.add_issue(
                    category="imports",
                    issue_type="OPTIONAL_DEPENDENCY",
                    file_path=str(source_file),
                    message=f"Optional dependency detected: '{import_name}' (handled gracefully)",
                    severity="info",
                )
            
            # All imports pass syntax validation - dependency availability is not our concern
            return True

        except Exception as e:
            self.add_issue(
                category="imports",
                issue_type="IMPORT_VALIDATION_ERROR",
                file_path=str(source_file),
                message=f"Error validating import '{import_name}': {e}",
                severity="warning",
            )
            return False

    def validate_all_imports(self, py_files: List[Path]) -> bool:
        """Validate imports for all Python files with parallel processing and detailed timing."""
        import time
        import concurrent.futures

        start_time = time.time()
        timeout = 300  # 5 minutes timeout for syntax validation
        all_valid = True
        max_workers = 4

        print(f"📝 Starting syntax validation of {len(py_files)} files with {max_workers} workers...")
        
        # Split files into chunks for better progress tracking
        chunk_size = max(1, len(py_files) // 20)  # 20 progress updates
        
        def validate_file_wrapper(file_path: Path) -> tuple:
            """Wrapper function for parallel validation."""
            file_start = time.time()
            syntax_valid = self.validate_syntax(file_path)
            
            if syntax_valid:
                imports = self.extract_imports(file_path)
                import_results = []
                for import_name in imports:
                    import_results.append(self.validate_import(import_name, file_path))
                imports_valid = all(import_results)
            else:
                imports_valid = False
            
            file_duration = time.time() - file_start
            return file_path, syntax_valid and imports_valid, file_duration

        processed_count = 0
        total_files = len(py_files)
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(validate_file_wrapper, py_file): py_file 
                    for py_file in py_files
                }
                
                for future in concurrent.futures.as_completed(future_to_file, timeout=timeout):
                    if time.time() - start_time > timeout:
                        print("⏱️  Syntax validation timeout reached, cancelling remaining tasks")
                        # Cancel remaining futures
                        for f in future_to_file:
                            f.cancel()
                        break
                    
                    try:
                        file_path, is_valid, duration = future.result()
                        if not is_valid:
                            all_valid = False
                        
                        processed_count += 1
                        
                        # Progress reporting
                        if processed_count % chunk_size == 0 or processed_count == total_files:
                            progress = (processed_count / total_files) * 100
                            elapsed = time.time() - start_time
                            rate = processed_count / elapsed if elapsed > 0 else 0
                            remaining = (total_files - processed_count) / rate if rate > 0 else 0
                            print(f"   Progress: {processed_count}/{total_files} ({progress:.1f}%) - "
                                  f"{rate:.1f} files/sec - ETA: {remaining:.1f}s")
                    
                    except Exception as e:
                        print(f"   Error processing file: {e}")
                        all_valid = False
                        processed_count += 1

        except concurrent.futures.TimeoutError:
            print("⏱️  Thread pool timeout reached")
            self.add_issue(
                category="system",
                issue_type="other",
                file_path="validation_system",
                message=f"Syntax validation timed out after {timeout} seconds",
                severity="error",
            )
            return False
        except Exception as e:
            print(f"❌ Error in parallel validation: {e}")
            # Fallback to sequential processing
            return self._validate_all_imports_sequential(py_files, timeout, start_time)

        total_duration = time.time() - start_time
        print(f"📝 Syntax validation completed in {total_duration:.2f}s "
              f"({processed_count} files, {processed_count/total_duration:.1f} files/sec)")
        
        return all_valid

    def _validate_all_imports_sequential(self, py_files: List[Path], timeout: int, start_time: float) -> bool:
        """Fallback sequential validation if parallel processing fails."""
        print("   Falling back to sequential processing...")
        all_valid = True

        for i, py_file in enumerate(py_files):
            if time.time() - start_time > timeout:
                print("⏱️  Sequential validation timeout reached, stopping")
                self.add_issue(
                    category="system",
                    issue_type="other",
                    file_path="validation_system",
                    message=f"Syntax validation timed out after {timeout} seconds",
                    severity="error",
                )
                return False

            if not self.validate_syntax(py_file):
                all_valid = False
                continue

            imports = self.extract_imports(py_file)
            for import_name in imports:
                if not self.validate_import(import_name, py_file):
                    all_valid = False
            
            # Progress reporting for sequential mode
            if (i + 1) % 50 == 0:
                progress = ((i + 1) / len(py_files)) * 100
                print(f"   Sequential progress: {i + 1}/{len(py_files)} ({progress:.1f}%)")

        return all_valid

    def get_syntax_errors(self) -> List[tuple]:
        """Get all syntax errors found during validation."""
        return self.syntax_errors

    def has_syntax_errors(self) -> bool:
        """Check if any syntax errors were found."""
        return len(self.syntax_errors) > 0

    def validate_file(self, file_path: Path) -> List:
        """Validate a single file for syntax issues."""
        if not file_path.exists() or file_path.suffix != ".py":
            return []

        if self.validate_syntax(file_path):
            return []
        else:
            # Return syntax errors for this file
            return [error for error in self.syntax_errors if error[0] == file_path]
