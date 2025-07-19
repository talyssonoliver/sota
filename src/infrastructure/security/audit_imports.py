#!/usr/bin/env python3
"""
Security Audit Script for Import Patterns

This script identifies and fixes insecure import patterns across the codebase.
It focuses on:
1. Silent import failures that could mask security issues
2. Standard library imports wrapped in try/except (suspicious)
3. Security-sensitive imports that fail silently
4. Missing fallback implementations for critical functionality
"""

import logging
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class SecurityIssue:
    file_path: str
    line_number: int
    issue_type: str
    security_level: SecurityLevel
    description: str
    module_name: str
    recommendation: str
    code_snippet: str


class ImportSecurityAuditor:
    """Audits import patterns for security issues"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues: List[SecurityIssue] = []
        self.suspicious_patterns = self._define_suspicious_patterns()
        self.stdlib_modules = self._get_stdlib_modules()
        self.security_sensitive_modules = self._get_security_sensitive_modules()

    def _define_suspicious_patterns(
        self,
    ) -> Dict[str, Tuple[str, SecurityLevel]]:
        """Define suspicious import patterns"""
        return {
            r"except ImportError:\s*pass\s*$": (
                "Silent import failure with bare 'pass'",
                SecurityLevel.HIGH,
            ),
            r"try:\s*import\s+(\w+)\s*except ImportError:\s*pass": (
                "Standard library import in try/except with silent failure",
                SecurityLevel.CRITICAL,
            ),
            r"try:\s*from\s+(\w+)\s+import.*except ImportError:\s*pass": (
                "Silent import failure without fallback",
                SecurityLevel.HIGH,
            ),
            r"import\s+(\w+)\s*except ImportError:\s*pass": (
                "Malformed import statement",
                SecurityLevel.CRITICAL,
            ),
        }

    def _get_stdlib_modules(self) -> Set[str]:
        """Get standard library modules that should never fail"""
        return {
            "os",
            "sys",
            "time",
            "datetime",
            "json",
            "logging",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
            "operator",
            "threading",
            "multiprocessing",
            "subprocess",
            "shutil",
            "tempfile",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "configparser",
            "argparse",
            "getopt",
            "traceback",
            "warnings",
            "contextlib",
            "abc",
            "enum",
            "dataclasses",
            "copy",
            "pickle",
            "base64",
            "hashlib",
            "hmac",
            "secrets",
            "uuid",
            "random",
            "math",
            "statistics",
            "decimal",
            "fractions",
            "cmath",
            "re",
            "string",
            "textwrap",
            "unicodedata",
            "calendar",
            "locale",
            "platform",
            "errno",
            "io",
            "socket",
            "ssl",
            "select",
            "signal",
            "mmap",
            "ctypes",
            "struct",
            "codecs",
            "encodings",
            "pkgutil",
            "importlib",
        }

    def _get_security_sensitive_modules(self) -> Set[str]:
        """Get modules that are security-sensitive"""
        return {
            "cryptography",
            "pycryptodome",
            "pycrypto",
            "nacl",
            "bcrypt",
            "scrypt",
            "argon2",
            "passlib",
            "keyring",
            "cryptography",
            "ssl",
            "tls",
            "oauth",
            "jwt",
            "authlib",
            "requests-oauthlib",
            "paramiko",
            "fabric",
            "sqlalchemy",
            "psycopg2",
            "pymongo",
            "redis",
            "ldap",
            "kerberos",
            "pam",
            "sudo",
        }

    def audit_file(self, file_path: Path) -> List[SecurityIssue]:
        """Audit a single Python file for import security issues"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return issues

        # Check for suspicious patterns
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith("#"):
                continue

            # Check for suspicious patterns
            for pattern, (
                description,
                level,
            ) in self.suspicious_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract module name if possible
                    module_match = re.search(r"import\s+(\w+)", line)
                    module_name = module_match.group(1) if module_match else "unknown"

                    # Determine security level
                    if module_name in self.stdlib_modules:
                        level = SecurityLevel.CRITICAL
                        description = f"Standard library module '{module_name}' should not be in try/except"
                    elif module_name in self.security_sensitive_modules:
                        level = SecurityLevel.CRITICAL
                        description = f"Security-sensitive module '{module_name}' failing silently"

                    issues.append(
                        SecurityIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type="SUSPICIOUS_IMPORT",
                            security_level=level,
                            description=description,
                            module_name=module_name,
                            recommendation=self._get_recommendation(module_name, level),
                            code_snippet=line.strip(),
                        )
                    )

            # Check for specific problematic patterns
            if "except ImportError:" in line and line_num < len(lines):
                next_line = lines[line_num].strip() if line_num < len(lines) else ""
                if next_line == "pass":
                    issues.append(
                        SecurityIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type="SILENT_IMPORT_FAILURE",
                            security_level=SecurityLevel.HIGH,
                            description="Import failure handled with silent 'pass'",
                            module_name="unknown",
                            recommendation="Add proper error handling or fallback implementation",
                            code_snippet=f"{line.strip()}\\n{next_line}",
                        )
                    )

        return issues

    def _get_recommendation(self, module_name: str, level: SecurityLevel) -> str:
        """Get security recommendation for a module"""
        if module_name in self.stdlib_modules:
            return f"Remove try/except - {module_name} is standard library and should always be available"
        elif module_name in self.security_sensitive_modules:
            return f"Add proper error handling for {module_name} - security implications if missing"
        elif level == SecurityLevel.CRITICAL:
            return f"Add proper error handling and fallback for {module_name}"
        else:
            return f"Consider adding fallback implementation for {module_name}"

    def audit_directory(self, directory: Path = None) -> List[SecurityIssue]:
        """Audit all Python files in a directory"""
        if directory is None:
            directory = self.root_path

        issues = []

        # Get all Python files
        python_files = list(directory.rglob("*.py"))

        logger.info(f"Auditing {len(python_files)} Python files in {directory}")

        for file_path in python_files:
            try:
                file_issues = self.audit_file(file_path)
                issues.extend(file_issues)
            except Exception as e:
                logger.error(f"Error auditing {file_path}: {e}")

        return issues

    def generate_report(self, issues: List[SecurityIssue]) -> str:
        """Generate a security audit report"""
        if not issues:
            return "✅ No security issues found in import patterns!"

        # Group issues by security level
        by_level = {}
        for issue in issues:
            level = issue.security_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(issue)

        report = []
        report.append("=" * 80)
        report.append("IMPORT SECURITY AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Total Issues Found: {len(issues)}")
        report.append("")

        # Summary by level
        report.append("SUMMARY BY SECURITY LEVEL:")
        for level in SecurityLevel:
            count = len(by_level.get(level, []))
            if count > 0:
                report.append(f"  {level.value}: {count} issues")
        report.append("")

        # Detailed issues
        for level in [
            SecurityLevel.CRITICAL,
            SecurityLevel.HIGH,
            SecurityLevel.MEDIUM,
            SecurityLevel.LOW,
        ]:
            level_issues = by_level.get(level, [])
            if not level_issues:
                continue

            report.append(f"{level.value} ISSUES ({len(level_issues)}):")
            report.append("-" * 40)

            for issue in level_issues:
                report.append(f"File: {issue.file_path}")
                report.append(f"Line: {issue.line_number}")
                report.append(f"Issue: {issue.description}")
                report.append(f"Code: {issue.code_snippet}")
                report.append(f"Recommendation: {issue.recommendation}")
                report.append("")

        return "\\n".join(report)

    def fix_issues(self, issues: List[SecurityIssue]) -> Dict[str, int]:
        """Automatically fix common import security issues"""
        fixes_applied = {"files_modified": 0, "issues_fixed": 0}

        # Group issues by file
        by_file = {}
        for issue in issues:
            file_path = issue.file_path
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)

        for file_path, file_issues in by_file.items():
            try:
                if self._fix_file_issues(file_path, file_issues):
                    fixes_applied["files_modified"] += 1
                    fixes_applied["issues_fixed"] += len(file_issues)
            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")

        return fixes_applied

    def _fix_file_issues(self, file_path: str, issues: List[SecurityIssue]) -> bool:
        """Fix issues in a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Could not read {file_path}: {e}")
            return False

        # Sort issues by line number in reverse order
        issues.sort(key=lambda x: x.line_number, reverse=True)

        modified = False
        for issue in issues:
            line_idx = issue.line_number - 1
            if line_idx < 0 or line_idx >= len(lines):
                continue

            original_line = lines[line_idx]

            # Apply fixes based on issue type
            if issue.issue_type == "SUSPICIOUS_IMPORT":
                if issue.module_name in self.stdlib_modules:
                    # Remove try/except for standard library modules
                    new_line = self._remove_try_except_for_stdlib(
                        original_line, issue.module_name
                    )
                    if new_line != original_line:
                        lines[line_idx] = new_line
                        modified = True

            elif issue.issue_type == "SILENT_IMPORT_FAILURE":
                # Replace silent pass with proper error handling
                new_line = self._add_proper_error_handling(
                    original_line, issue.module_name
                )
                if new_line != original_line:
                    lines[line_idx] = new_line
                    modified = True

        if modified:
            # Write back the modified file
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                logger.info(f"Fixed issues in {file_path}")
                return True
            except Exception as e:
                logger.error(f"Could not write {file_path}: {e}")
                return False

        return False

    def _remove_try_except_for_stdlib(self, line: str, module_name: str) -> str:
        """Remove try/except wrapper for standard library imports"""
        # Simple pattern - just extract the import statement
        import_match = re.search(r"(import\s+\w+|from\s+\w+\s+import\s+.*)", line)
        if import_match:
            return import_match.group(1) + "\\n"
        return line

    def _add_proper_error_handling(self, line: str, module_name: str) -> str:
        """Add proper error handling instead of silent pass"""
        if "pass" in line:
            return line.replace(
                "pass",
                f'logger.warning("Optional module {module_name} not available")',
            )
        return line


def main():
    """Main security audit function"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."

    auditor = ImportSecurityAuditor(root_path)

    print("🔍 Starting import security audit...")
    issues = auditor.audit_directory()

    print(f"\\n📊 Found {len(issues)} potential security issues")

    # Generate report
    report = auditor.generate_report(issues)
    print(report)

    # Save report to file
    report_file = Path("security_audit_report.txt")
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\\n📄 Full report saved to {report_file}")

    # Ask user if they want to apply automatic fixes
    if issues:
        response = input("\\n🔧 Apply automatic fixes? (y/N): ").strip().lower()
        if response == "y":
            print("🔧 Applying automatic fixes...")
            fixes = auditor.fix_issues(issues)
            print(
                f"✅ Applied fixes to {fixes['files_modified']} files, fixed {fixes['issues_fixed']} issues"
            )
        else:
            print("ℹ️ No fixes applied. Review the report and fix issues manually.")

    # Return exit code based on critical issues
    critical_issues = [i for i in issues if i.security_level == SecurityLevel.CRITICAL]
    if critical_issues:
        print(f"\\n❌ {len(critical_issues)} CRITICAL security issues found!")
        return 1
    else:
        print("\\n✅ No critical security issues found.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
