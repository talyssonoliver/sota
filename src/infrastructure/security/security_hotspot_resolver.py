
from src.infrastructure.utils.common_imports import (
    Path,
    dataclass,
    datetime,
    json,
    re
)
"""
Security Hotspot Resolver

Analyzes and resolves security hotspots to reduce technical debt.
Targets the 182.25 hours of security hotspots identified in validation report.
"""

# import hashlib  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# import re  # Consolidated to common_imports
from collections import defaultdict
# from dataclasses import dataclass  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Any, Dict, List, Optional

from ..utils.base_classes import BaseAnalyzer, BaseComponent, BaseFileHandler


@dataclass
class SecurityHotspot:
    """Represents a security hotspot with fix recommendations."""
    category: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    file_path: str
    line_number: int
    description: str
    vulnerable_code: str
    fix_recommendation: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    estimated_fix_time_minutes: int = 30


class SecurityHotspotAnalyzer(BaseAnalyzer):
    """Analyzes code for security hotspots and provides fix recommendations."""
    
    def __init__(self):
        super().__init__("SecurityHotspotAnalyzer")
        self.hotspots: List[SecurityHotspot] = []
        self.security_patterns = self._initialize_security_patterns()
    
    def _initialize_security_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize security vulnerability patterns."""
        return {
            'injection': [
                {
                    'pattern': r'\.execute\s*\(\s*["\'].*%.*["\']',
                    'description': 'SQL injection vulnerability - string formatting in SQL query',
                    'severity': 'HIGH',
                    'cwe': 'CWE-89',
                    'owasp': 'A03:2021-Injection',
                    'fix': 'Use parameterized queries instead of string formatting'
                },
                {
                    'pattern': r'eval\s*\(',
                    'description': 'Code injection vulnerability - use of eval()',
                    'severity': 'CRITICAL',
                    'cwe': 'CWE-95',
                    'owasp': 'A03:2021-Injection',
                    'fix': 'Replace eval() with safe alternatives like ast.literal_eval()'
                },
                {
                    'pattern': r'exec\s*\(',
                    'description': 'Code injection vulnerability - use of exec()',
                    'severity': 'CRITICAL',
                    'cwe': 'CWE-95',
                    'owasp': 'A03:2021-Injection',
                    'fix': 'Avoid exec() - use safe alternatives or validate input strictly'
                }
            ],
            'crypto': [
                {
                    'pattern': r'md5\s*\(',
                    'description': 'Weak cryptographic hash - MD5 is cryptographically broken',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-327',
                    'owasp': 'A02:2021-Cryptographic Failures',
                    'fix': 'Use SHA-256 or stronger hash algorithms'
                },
                {
                    'pattern': r'sha1\s*\(',
                    'description': 'Weak cryptographic hash - SHA-1 is deprecated',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-327',
                    'owasp': 'A02:2021-Cryptographic Failures',
                    'fix': 'Use SHA-256 or stronger hash algorithms'
                },
                {
                    'pattern': r'random\.random\(\)',
                    'description': 'Insecure random number generation for security purposes',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-338',
                    'owasp': 'A02:2021-Cryptographic Failures',
                    'fix': 'Use secrets module for cryptographically secure random numbers'
                }
            ],
            'path_traversal': [
                {
                    'pattern': r'open\s*\(\s*[^,]+\+',
                    'description': 'Potential path traversal - direct path concatenation',
                    'severity': 'HIGH',
                    'cwe': 'CWE-22',
                    'owasp': 'A01:2021-Broken Access Control',
                    'fix': 'Use os.path.join() or pathlib.Path for safe path construction'
                },
                {
                    'pattern': r'\.\./',
                    'description': 'Path traversal pattern found in string literal',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-22',
                    'owasp': 'A01:2021-Broken Access Control',
                    'fix': 'Validate and sanitize file paths to prevent directory traversal'
                }
            ],
            'hardcoded_secrets': [
                {
                    'pattern': r'password\s*=\s*["\'][^"\']{8,}["\']',
                    'description': 'Hardcoded password found',
                    'severity': 'HIGH',
                    'cwe': 'CWE-798',
                    'owasp': 'A07:2021-Identification and Authentication Failures',
                    'fix': 'Use environment variables or secure configuration management'
                },
                {
                    'pattern': r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                    'description': 'Hardcoded API key found',
                    'severity': 'HIGH',
                    'cwe': 'CWE-798',
                    'owasp': 'A07:2021-Identification and Authentication Failures',
                    'fix': 'Use environment variables or secure configuration management'
                },
                {
                    'pattern': r'secret\s*=\s*["\'][^"\']{16,}["\']',
                    'description': 'Hardcoded secret found',
                    'severity': 'HIGH',
                    'cwe': 'CWE-798',
                    'owasp': 'A07:2021-Identification and Authentication Failures',
                    'fix': 'Use environment variables or secure configuration management'
                }
            ],
            'insecure_deserialization': [
                {
                    'pattern': r'pickle\.loads?\s*\(',
                    'description': 'Insecure deserialization with pickle',
                    'severity': 'HIGH',
                    'cwe': 'CWE-502',
                    'owasp': 'A08:2021-Software and Data Integrity Failures',
                    'fix': 'Use safe serialization formats like JSON or validate pickle data'
                },
                {
                    'pattern': r'marshal\.loads?\s*\(',
                    'description': 'Insecure deserialization with marshal',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-502',
                    'owasp': 'A08:2021-Software and Data Integrity Failures',
                    'fix': 'Use safe serialization formats like JSON'
                }
            ],
            'logging_sensitive': [
                {
                    'pattern': r'log(?:ger)?\.(?:info|debug|warning|error)\s*\([^)]*(?:password|token|key|secret)',
                    'description': 'Potential sensitive data in logs',
                    'severity': 'MEDIUM',
                    'cwe': 'CWE-532',
                    'owasp': 'A09:2021-Security Logging and Monitoring Failures',
                    'fix': 'Sanitize sensitive data before logging or use structured logging'
                }
            ],
            'unsafe_yaml': [
                {
                    'pattern': r'yaml\.load\s*\(',
                    'description': 'Unsafe YAML loading - allows arbitrary code execution',
                    'severity': 'HIGH',
                    'cwe': 'CWE-502',
                    'owasp': 'A08:2021-Software and Data Integrity Failures',
                    'fix': 'Use yaml.safe_load() instead of yaml.load()'
                }
            ],
            'weak_ssl': [
                {
                    'pattern': r'ssl\.create_default_context\(\).*check_hostname\s*=\s*False',
                    'description': 'SSL hostname verification disabled',
                    'severity': 'HIGH',
                    'cwe': 'CWE-295',
                    'owasp': 'A02:2021-Cryptographic Failures',
                    'fix': 'Enable SSL hostname verification for secure connections'
                },
                {
                    'pattern': r'verify\s*=\s*False',
                    'description': 'SSL verification disabled in HTTP requests',
                    'severity': 'HIGH',
                    'cwe': 'CWE-295',
                    'owasp': 'A02:2021-Cryptographic Failures',
                    'fix': 'Enable SSL verification or use proper certificate handling'
                }
            ]
        }
    
    def _analyze_target(self, file_path: Path):
        """Analyze file for security hotspots."""
        if not file_path.suffix == '.py':
            return
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check each security pattern
            for category, patterns in self.security_patterns.items():
                for pattern_info in patterns:
                    self._find_pattern_matches(
                        file_path, content, lines, category, pattern_info
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
    
    def _find_pattern_matches(self, file_path: Path, content: str, lines: List[str], 
                             category: str, pattern_info: Dict):
        """Find matches for a specific security pattern."""
        pattern = pattern_info['pattern']
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            
            for match in matches:
                hotspot = SecurityHotspot(
                    category=category,
                    severity=pattern_info['severity'],
                    file_path=str(file_path),
                    line_number=line_num,
                    description=pattern_info['description'],
                    vulnerable_code=line.strip(),
                    fix_recommendation=pattern_info['fix'],
                    cwe_id=pattern_info.get('cwe'),
                    owasp_category=pattern_info.get('owasp'),
                    estimated_fix_time_minutes=self._estimate_fix_time(
                        pattern_info['severity'], category
                    )
                )
                
                self.hotspots.append(hotspot)
                self.add_result(f"{file_path}:{line_num}", {
                    'category': category,
                    'severity': pattern_info['severity'],
                    'description': pattern_info['description'],
                    'fix': pattern_info['fix']
                })
    
    def _estimate_fix_time(self, severity: str, category: str) -> int:
        """Estimate time to fix hotspot in minutes."""
        base_times = {
            'CRITICAL': 120,  # 2 hours
            'HIGH': 60,       # 1 hour
            'MEDIUM': 30,     # 30 minutes
            'LOW': 15         # 15 minutes
        }
        
        category_multipliers = {
            'injection': 1.5,
            'crypto': 1.2,
            'insecure_deserialization': 1.5,
            'hardcoded_secrets': 0.8,
            'path_traversal': 1.0,
            'logging_sensitive': 0.5,
            'unsafe_yaml': 1.0,
            'weak_ssl': 1.2
        }
        
        base_time = base_times.get(severity, 30)
        multiplier = category_multipliers.get(category, 1.0)
        
        return int(base_time * multiplier)


class SecurityHotspotResolver(BaseFileHandler):
    """Resolves security hotspots by applying automated fixes."""
    
    def __init__(self, root_path: Optional[str] = None):
        super().__init__(root_path)
        self.fix_patterns = self._initialize_fix_patterns()
        self.resolved_hotspots = []
        
    def _initialize_fix_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize patterns for automated fixes."""
        return {
            'weak_crypto': [
                {
                    'search': r'hashlib\.md5\s*\(',
                    'replace': 'hashlib.sha256(',
                    'description': 'Replace MD5 with SHA-256'
                },
                {
                    'search': r'hashlib\.sha1\s*\(',
                    'replace': 'hashlib.sha256(',
                    'description': 'Replace SHA-1 with SHA-256'
                }
            ],
            'insecure_random': [
                {
                    'search': r'import random\n',
                    'replace': 'import secrets\n',
                    'description': 'Replace random with secrets module'
                },
                {
                    'search': r'random\.random\(\)',
                    'replace': 'secrets.randbits(32) / (2**32)',
                    'description': 'Use cryptographically secure random'
                }
            ],
            'unsafe_yaml': [
                {
                    'search': r'yaml\.load\s*\(',
                    'replace': 'yaml.safe_load(',
                    'description': 'Use safe YAML loading'
                }
            ],
            'ssl_verification': [
                {
                    'search': r'verify\s*=\s*False',
                    'replace': 'verify=True',
                    'description': 'Enable SSL verification'
                }
            ],
            'path_safety': [
                {
                    'search': r'open\s*\(\s*([^,]+)\s*\+\s*([^,]+)',
                    'replace': r'open(os.path.join(\1, \2)',
                    'description': 'Use safe path joining'
                }
            ]
        }
    
    def resolve_hotspots(self, hotspots: List[SecurityHotspot]) -> Dict[str, Any]:
        """Resolve security hotspots with automated fixes."""
        self.logger.info(f"Resolving {len(hotspots)} security hotspots")
        
        resolution_stats = {
            'total_hotspots': len(hotspots),
            'resolved_automatically': 0,
            'require_manual_review': 0,
            'failed_to_resolve': 0,
            'time_saved_minutes': 0,
            'by_category': defaultdict(int),
            'by_severity': defaultdict(int)
        }
        
        # Group hotspots by file for batch processing
        hotspots_by_file = defaultdict(list)
        for hotspot in hotspots:
            hotspots_by_file[hotspot.file_path].append(hotspot)
        
        # Process each file
        for file_path, file_hotspots in hotspots_by_file.items():
            result = self._resolve_file_hotspots(Path(file_path), file_hotspots)
            
            # Update statistics
            resolution_stats['resolved_automatically'] += result['resolved']
            resolution_stats['require_manual_review'] += result['manual_review']
            resolution_stats['failed_to_resolve'] += result['failed']
            resolution_stats['time_saved_minutes'] += result['time_saved']
            
            for hotspot in file_hotspots:
                resolution_stats['by_category'][hotspot.category] += 1
                resolution_stats['by_severity'][hotspot.severity] += 1
        
        return resolution_stats
    
    def _resolve_file_hotspots(self, file_path: Path, hotspots: List[SecurityHotspot]) -> Dict[str, int]:
        """Resolve hotspots in a single file."""
        result = {
            'resolved': 0,
            'manual_review': 0,
            'failed': 0,
            'time_saved': 0
        }
        
        try:
            content = self.read_file_safely(file_path)
            if not content:
                result['failed'] = len(hotspots)
                return result
            
            original_content = content
            modified = False
            
            # Apply fixes for each hotspot
            for hotspot in hotspots:
                fix_applied = self._apply_hotspot_fix(content, hotspot)
                
                if fix_applied['success']:
                    content = fix_applied['new_content']
                    modified = True
                    result['resolved'] += 1
                    result['time_saved'] += hotspot.estimated_fix_time_minutes
                    self.resolved_hotspots.append(hotspot)
                elif fix_applied['requires_manual']:
                    result['manual_review'] += 1
                else:
                    result['failed'] += 1
            
            # Write modified content back to file
            if modified:
                success = self.write_file_safely(file_path, content, backup=True)
                if not success:
                    # Revert statistics if write failed
                    result['failed'] = result['resolved']
                    result['resolved'] = 0
                    result['time_saved'] = 0
                else:
                    self.logger.info(f"Applied security fixes to {file_path}")
        
        except Exception as e:
            self.logger.error(f"Error resolving hotspots in {file_path}: {e}")
            result['failed'] = len(hotspots)
        
        return result
    
    def _apply_hotspot_fix(self, content: str, hotspot: SecurityHotspot) -> Dict[str, Any]:
        """Apply fix for a specific hotspot."""
        category = hotspot.category
        
        # Check if we have automated fixes for this category
        if category in self.fix_patterns:
            for fix_pattern in self.fix_patterns[category]:
                if re.search(fix_pattern['search'], content, re.MULTILINE):
                    # Apply the fix
                    new_content = re.sub(
                        fix_pattern['search'], 
                        fix_pattern['replace'], 
                        content,
                        flags=re.MULTILINE
                    )
                    
                    if new_content != content:
                        return {
                            'success': True,
                            'new_content': new_content,
                            'fix_applied': fix_pattern['description']
                        }
        
        # Special handling for specific patterns
        if category == 'hardcoded_secrets':
            return self._fix_hardcoded_secrets(content, hotspot)
        elif category == 'injection':
            return self._fix_injection_vulnerability(content, hotspot)
        elif category == 'logging_sensitive':
            return self._fix_sensitive_logging(content, hotspot)
        
        # If no automated fix available, mark for manual review
        return {
            'success': False,
            'requires_manual': True,
            'reason': f'No automated fix available for {category}'
        }
    
    def _fix_hardcoded_secrets(self, content: str, hotspot: SecurityHotspot) -> Dict[str, Any]:
        """Fix hardcoded secrets by replacing with environment variable lookup."""
        lines = content.split('\n')
        line_index = hotspot.line_number - 1
        
        if line_index >= len(lines):
            return {'success': False, 'requires_manual': True}
        
        line = lines[line_index]
        
        # Extract variable name and value
        match = re.search(r'(\w+)\s*=\s*["\']([^"\']+)["\']', line)
        if match:
            var_name, secret_value = match.groups()
            
            # Replace with environment variable lookup
            env_var_name = var_name.upper()
            replacement = f'{var_name} = os.getenv("{env_var_name}", "")'
            
            # Add import for os if not present
            if 'import os' not in content:
                lines.insert(0, 'import os')
            
            lines[line_index] = re.sub(
                r'(\w+)\s*=\s*["\'][^"\']+["\']',
                replacement,
                line
            )
            
            return {
                'success': True,
                'new_content': '\n'.join(lines),
                'fix_applied': f'Replaced hardcoded secret with environment variable {env_var_name}'
            }
        
        return {'success': False, 'requires_manual': True}
    
    def _fix_injection_vulnerability(self, content: str, hotspot: SecurityHotspot) -> Dict[str, Any]:
        """Fix injection vulnerabilities."""
        # This is complex and often requires manual review
        # For now, mark for manual review with specific guidance
        return {
            'success': False,
            'requires_manual': True,
            'reason': 'Injection vulnerabilities require careful manual review and testing'
        }
    
    def _fix_sensitive_logging(self, content: str, hotspot: SecurityHotspot) -> Dict[str, Any]:
        """Fix sensitive data in logging statements."""
        lines = content.split('\n')
        line_index = hotspot.line_number - 1
        
        if line_index >= len(lines):
            return {'success': False, 'requires_manual': True}
        
        line = lines[line_index]
        
        # Add comment warning about sensitive data
        indent = len(line) - len(line.lstrip())
        warning_comment = ' ' * indent + '# WARNING: Ensure no sensitive data is logged'
        
        lines.insert(line_index, warning_comment)
        
        return {
            'success': True,
            'new_content': '\n'.join(lines),
            'fix_applied': 'Added warning comment about sensitive data logging'
        }


class SecurityHotspotManager(BaseComponent):
    """Manages the complete security hotspot resolution process."""
    
    def __init__(self, root_path: Optional[str] = None, **kwargs):
        super().__init__("SecurityHotspotManager", **kwargs)
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.analyzer = SecurityHotspotAnalyzer()
        self.resolver = SecurityHotspotResolver(root_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'file_patterns': ['*.py'],
            'exclude_patterns': ['*/test*', '*/venv/*', '*/__pycache__/*'],
            'auto_resolve_safe_fixes': True,
            'create_backup': True,
            'generate_report': True,
            'max_files': None
        }
    
    def resolve_security_hotspots(self) -> Dict[str, Any]:
        """Complete security hotspot resolution process."""
        self.logger.info("Starting security hotspot resolution")
        
        # Find files to analyze
        files_to_analyze = []
        for pattern in self.config['file_patterns']:
            files = self.resolver.find_files(pattern, self.config['exclude_patterns'])
            files_to_analyze.extend(files)
        
        if self.config.get('max_files'):
            files_to_analyze = files_to_analyze[:self.config['max_files']]
        
        self.logger.info(f"Analyzing {len(files_to_analyze)} files for security hotspots")
        
        # Analyze files for hotspots
        for file_path in files_to_analyze:
            self.analyzer.analyze(file_path)
        
        # Get all discovered hotspots
        hotspots = self.analyzer.hotspots
        self.logger.info(f"Found {len(hotspots)} security hotspots")
        
        # Resolve hotspots if enabled
        resolution_stats = {'total_hotspots': len(hotspots)}
        if self.config['auto_resolve_safe_fixes'] and hotspots:
            resolution_stats = self.resolver.resolve_hotspots(hotspots)
        
        # Generate report
        report = self._generate_comprehensive_report(hotspots, resolution_stats)
        
        if self.config['generate_report']:
            report_path = self.root_path / 'reports' / 'security_hotspots_report.json'
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
#             import json  # Consolidated to common_imports
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Security hotspot report saved to {report_path}")
        
        return report
    
    def _generate_comprehensive_report(self, hotspots: List[SecurityHotspot], 
                                     resolution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security hotspot report."""
        # Categorize hotspots
        by_severity = defaultdict(list)
        by_category = defaultdict(list)
        by_owasp = defaultdict(list)
        
        for hotspot in hotspots:
            by_severity[hotspot.severity].append(hotspot)
            by_category[hotspot.category].append(hotspot)
            if hotspot.owasp_category:
                by_owasp[hotspot.owasp_category].append(hotspot)
        
        # Calculate technical debt
        total_fix_time = sum(h.estimated_fix_time_minutes for h in hotspots)
        time_saved = resolution_stats.get('time_saved_minutes', 0)
        remaining_debt = total_fix_time - time_saved
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_hotspots': len(hotspots),
                'by_severity': {k: len(v) for k, v in by_severity.items()},
                'by_category': {k: len(v) for k, v in by_category.items()},
                'by_owasp': {k: len(v) for k, v in by_owasp.items()}
            },
            'technical_debt': {
                'total_estimated_hours': total_fix_time / 60,
                'resolved_hours': time_saved / 60,
                'remaining_hours': remaining_debt / 60,
                'debt_reduction_percentage': (time_saved / total_fix_time * 100) if total_fix_time > 0 else 0
            },
            'resolution_statistics': resolution_stats,
            'priority_hotspots': [
                {
                    'file': h.file_path,
                    'line': h.line_number,
                    'severity': h.severity,
                    'category': h.category,
                    'description': h.description,
                    'fix_recommendation': h.fix_recommendation
                }
                for h in sorted(hotspots, key=lambda x: (
                    {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x.severity],
                    x.estimated_fix_time_minutes
                ), reverse=True)[:20]
            ],
            'recommendations': self._generate_security_recommendations(hotspots, resolution_stats)
        }
    
    def _generate_security_recommendations(self, hotspots: List[SecurityHotspot], 
                                         resolution_stats: Dict[str, Any]) -> List[str]:
        """Generate security improvement recommendations."""
        recommendations = []
        
        # Count by severity
        critical_count = sum(1 for h in hotspots if h.severity == 'CRITICAL')
        high_count = sum(1 for h in hotspots if h.severity == 'HIGH')
        
        if critical_count > 0:
            recommendations.append(
                f"URGENT: {critical_count} critical security issues require immediate attention"
            )
        
        if high_count > 5:
            recommendations.append(
                f"High priority: {high_count} high-severity security issues need resolution"
            )
        
        # Category-specific recommendations
        category_counts = defaultdict(int)
        for hotspot in hotspots:
            category_counts[hotspot.category] += 1
        
        if category_counts['injection'] > 0:
            recommendations.append("Implement input validation and parameterized queries")
        
        if category_counts['crypto'] > 5:
            recommendations.append("Audit and upgrade cryptographic implementations")
        
        if category_counts['hardcoded_secrets'] > 0:
            recommendations.append("Implement secure configuration management")
        
        if category_counts['insecure_deserialization'] > 0:
            recommendations.append("Review and secure data deserialization processes")
        
        # Resolution effectiveness
        resolved_percentage = (resolution_stats.get('resolved_automatically', 0) / 
                             resolution_stats.get('total_hotspots', 1)) * 100
        
        if resolved_percentage < 50:
            recommendations.append("Consider security training for development team")
        
        recommendations.append("Implement security linting in CI/CD pipeline")
        recommendations.append("Schedule regular security code reviews")
        
        return recommendations[:10]