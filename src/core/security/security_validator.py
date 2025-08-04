
from src.infrastructure.utils.common_imports import (
    Enum,
    Path,
    dataclass,
    logging,
    re
)
"""
Security Validator

Identifies and validates security issues in code and configurations.
"""

import ast
# import re  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, List, Optional, Set, Any
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports


class SecuritySeverity(Enum):
    """Security issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    """Represents a security issue"""
    file_path: str
    line_number: int
    severity: SecuritySeverity
    issue_type: str
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID


class SecurityValidator:
    """Validates code for security issues"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_security_patterns()
    
    def _setup_security_patterns(self):
        """Setup security vulnerability patterns"""
        self.patterns = {
            # Command injection
            'command_injection': {
                'patterns': [
                    r'os\.system\s*\(',
                    r'subprocess\.call\s*\([^)]*shell\s*=\s*True',
                    r'subprocess\.run\s*\([^)]*shell\s*=\s*True',
                    r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True',
                ],
                'severity': SecuritySeverity.HIGH,
                'cwe': 'CWE-78',
                'description': 'Potential command injection vulnerability',
                'recommendation': 'Avoid shell=True, use list arguments instead'
            },
            
            # Code injection
            'code_injection': {
                'patterns': [
                    r'\beval\s*\(',
                    r'\bexec\s*\(',
                    r'__import__\s*\(',
                ],
                'severity': SecuritySeverity.CRITICAL,
                'cwe': 'CWE-94',
                'description': 'Potential code injection vulnerability',
                'recommendation': 'Avoid eval/exec, use safer alternatives'
            },
            
            # Hardcoded secrets
            'hardcoded_secrets': {
                'patterns': [
                    r'password\s*=\s*["\'][^"\']{8,}["\']',
                    r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                    r'secret\s*=\s*["\'][^"\']{10,}["\']',
                    r'token\s*=\s*["\'][^"\']{20,}["\']',
                ],
                'severity': SecuritySeverity.HIGH,
                'cwe': 'CWE-798',
                'description': 'Hardcoded credentials detected',
                'recommendation': 'Use environment variables or secure credential storage'
            },
            
            # Insecure random
            'weak_random': {
                'patterns': [
                    r'\brandom\.random\s*\(',
                    r'\brandom\.randint\s*\(',
                    r'\brandom\.choice\s*\(',
                ],
                'severity': SecuritySeverity.MEDIUM,
                'cwe': 'CWE-338',
                'description': 'Use of weak random number generator',
                'recommendation': 'Use secrets module for cryptographic purposes'
            },
            
            # Path traversal
            'path_traversal': {
                'patterns': [
                    r'open\s*\([^)]*\.\./[^)]*\)',
                    r'file\s*\([^)]*\.\./[^)]*\)',
                    r'os\.path\.join\s*\([^)]*\.\.[^)]*\)',
                ],
                'severity': SecuritySeverity.HIGH,
                'cwe': 'CWE-22',
                'description': 'Potential path traversal vulnerability',
                'recommendation': 'Validate and sanitize file paths'
            },
            
            # SQL injection
            'sql_injection': {
                'patterns': [
                    r'execute\s*\([^)]*%[^)]*\)',
                    r'cursor\.execute\s*\([^)]*%[^)]*\)',
                    r'query\s*=.*%.*',
                ],
                'severity': SecuritySeverity.HIGH,
                'cwe': 'CWE-89',
                'description': 'Potential SQL injection vulnerability',
                'recommendation': 'Use parameterized queries'
            },
            
            # Insecure deserialization
            'insecure_deserialization': {
                'patterns': [
                    r'pickle\.loads?\s*\(',
                    r'yaml\.load\s*\(',
                    r'marshal\.loads?\s*\(',
                ],
                'severity': SecuritySeverity.HIGH,
                'cwe': 'CWE-502',
                'description': 'Insecure deserialization detected',
                'recommendation': 'Use safe loading methods or validate input'
            },
            
            # Weak cryptography
            'weak_crypto': {
                'patterns': [
                    r'md5\s*\(',
                    r'sha1\s*\(',
                    r'DES\s*\(',
                    r'RC4\s*\(',
                ],
                'severity': SecuritySeverity.MEDIUM,
                'cwe': 'CWE-326',
                'description': 'Use of weak cryptographic algorithm',
                'recommendation': 'Use strong cryptographic algorithms (SHA-256, AES)'
            },
            
            # Insecure HTTP
            'insecure_http': {
                'patterns': [
                    r'http://[^"\']+',
                    r'verify\s*=\s*False',
                    r'ssl_context\s*=\s*ssl\._create_unverified_context',
                ],
                'severity': SecuritySeverity.MEDIUM,
                'cwe': 'CWE-319',
                'description': 'Insecure HTTP communication',
                'recommendation': 'Use HTTPS and verify SSL certificates'
            }
        }
    
    def scan_file(self, file_path: str) -> List[SecurityIssue]:
        """Scan a single file for security issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check each pattern category
            for category, config in self.patterns.items():
                for pattern in config['patterns']:
                    issues.extend(self._find_pattern_matches(
                        file_path, lines, pattern, category, config
                    ))
            
            # Additional AST-based checks for Python files
            if file_path.endswith('.py'):
                issues.extend(self._ast_security_check(file_path, content))
                
        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")
        
        return issues
    
    def _find_pattern_matches(self, file_path: str, lines: List[str], 
                             pattern: str, category: str, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Find pattern matches in file content"""
        issues = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            if regex.search(line):
                # Skip comments and documentation
                stripped_line = line.strip()
                if stripped_line.startswith('#') or stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                    continue
                
                issues.append(SecurityIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=config['severity'],
                    issue_type=category,
                    description=config['description'],
                    recommendation=config['recommendation'],
                    code_snippet=line.strip(),
                    cwe_id=config.get('cwe')
                ))
        
        return issues
    
    def _ast_security_check(self, file_path: str, content: str) -> List[SecurityIssue]:
        """Perform AST-based security checks"""
        issues = []
        
        try:
            tree = ast.parse(content)
            visitor = SecurityASTVisitor(file_path)
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            self.logger.warning(f"AST parsing failed for {file_path}: {e}")
        
        return issues
    
    def scan_directory(self, directory: str, extensions: Optional[Set[str]] = None) -> List[SecurityIssue]:
        """Scan directory for security issues"""
        if extensions is None:
            extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.php'}
        
        issues = []
        directory_path = Path(directory)
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                issues.extend(self.scan_file(str(file_path)))
        
        return issues
    
    def generate_security_report(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Generate security report from issues"""
        report = {
            'total_issues': len(issues),
            'by_severity': {},
            'by_type': {},
            'by_cwe': {},
            'files_affected': set(),
            'issues': []
        }
        
        # Count by severity
        for severity in SecuritySeverity:
            report['by_severity'][severity.value] = 0
        
        for issue in issues:
            # Count by severity
            report['by_severity'][issue.severity.value] += 1
            
            # Count by type
            if issue.issue_type not in report['by_type']:
                report['by_type'][issue.issue_type] = 0
            report['by_type'][issue.issue_type] += 1
            
            # Count by CWE
            if issue.cwe_id:
                if issue.cwe_id not in report['by_cwe']:
                    report['by_cwe'][issue.cwe_id] = 0
                report['by_cwe'][issue.cwe_id] += 1
            
            # Track affected files
            report['files_affected'].add(issue.file_path)
            
            # Add to issues list
            report['issues'].append({
                'file': issue.file_path,
                'line': issue.line_number,
                'severity': issue.severity.value,
                'type': issue.issue_type,
                'description': issue.description,
                'recommendation': issue.recommendation,
                'code': issue.code_snippet,
                'cwe': issue.cwe_id
            })
        
        report['files_affected'] = len(report['files_affected'])
        return report


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor for security checks"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[SecurityIssue] = []
    
    def visit_Call(self, node):
        """Check function calls for security issues"""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            if func_name in ['eval', 'exec']:
                self.issues.append(SecurityIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    severity=SecuritySeverity.CRITICAL,
                    issue_type='code_injection',
                    description=f'Use of {func_name}() function',
                    recommendation=f'Avoid {func_name}(), use safer alternatives',
                    cwe_id='CWE-94'
                ))
        
        elif isinstance(node.func, ast.Attribute):
            # Check for os.system, subprocess calls with shell=True
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'os' and 
                node.func.attr == 'system'):
                
                self.issues.append(SecurityIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    severity=SecuritySeverity.HIGH,
                    issue_type='command_injection',
                    description='Use of os.system()',
                    recommendation='Use subprocess with list arguments',
                    cwe_id='CWE-78'
                ))
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Check assignments for hardcoded secrets"""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id.lower()
            
            # Check for password/secret assignments
            if any(keyword in var_name for keyword in ['password', 'secret', 'key', 'token']):
                if isinstance(node.value, ast.Str) and len(node.value.s) > 8:
                    self.issues.append(SecurityIssue(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        severity=SecuritySeverity.HIGH,
                        issue_type='hardcoded_secrets',
                        description=f'Hardcoded credential in variable: {var_name}',
                        recommendation='Use environment variables or secure storage',
                        cwe_id='CWE-798'
                    ))
        
        self.generic_visit(node)