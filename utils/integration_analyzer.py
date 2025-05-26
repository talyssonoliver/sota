"""
Integration Gap Detection - Step 5.3
Identifies missing integration points or untested code paths.
"""

import os
import ast
import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class GapSeverity(Enum):
    """Severity levels for integration gaps."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GapType(Enum):
    """Types of integration gaps that can be detected."""
    MISSING_INTERFACE_TEST = "missing_interface_test"
    UNVALIDATED_DATA_FLOW = "unvalidated_data_flow"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    INCOMPLETE_API_COVERAGE = "incomplete_api_coverage"
    MISSING_COMPONENT_INTERACTION = "missing_component_interaction"
    UNTESTED_BOUNDARY = "untested_boundary"


@dataclass
class IntegrationGap:
    """Represents an identified integration gap."""
    gap_type: GapType
    severity: GapSeverity
    description: str
    file_path: str
    line_number: Optional[int] = None
    component1: Optional[str] = None
    component2: Optional[str] = None
    recommendation: Optional[str] = None


class IntegrationAnalyzer:
    """Analyzes codebase for integration gaps and missing test coverage."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        self.gaps: List[IntegrationGap] = []
        self.components: Dict[str, Dict[str, Any]] = {}
        
    def analyze_project(self, project_path: str = None) -> Dict[str, Any]:
        """Analyze the entire project for integration gaps."""
        if project_path:
            self.project_root = Path(project_path)
        
        self.gaps.clear()
        self.components.clear()
        
        try:
            # Discover and analyze components
            self._discover_components()
            
            # Analyze integration points
            self._analyze_integration_points()
            
            # Check for missing tests
            self._check_missing_tests()
            
            # Analyze data flows
            self._analyze_data_flows()
            
            # Check API coverage
            self._check_api_coverage()
            
            return self._generate_report()
            
        except Exception as e:
            self.logger.error(f"Error analyzing project: {e}")
            return {"error": str(e), "gaps": [], "components": []}
    
    def _discover_components(self):
        """Discover all components in the project."""
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            try:
                component_info = self._analyze_file_structure(py_file)
                if component_info:
                    rel_path = str(py_file.relative_to(self.project_root))
                    self.components[rel_path] = component_info
            except Exception as e:
                self.logger.warning(f"Failed to analyze {py_file}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis."""
        skip_patterns = [
            "__pycache__", ".git", ".venv", "node_modules",
            "test_", "_test", ".test.", "conftest.py"
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze the structure of a Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            info = {
                "classes": [],
                "functions": [],
                "imports": [],
                "external_calls": [],
                "interfaces": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "line": node.lineno,
                        "bases": [self._get_base_name(base) for base in node.bases]
                    }
                    info["classes"].append(class_info)
                    
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line": node.lineno,
                        "returns": self._get_return_annotation(node)
                    }
                    info["functions"].append(func_info)
                    
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info["imports"].append(node.module)
                        
                elif isinstance(node, ast.Call):
                    call_name = self._get_call_name(node)
                    if call_name and "." in call_name:
                        info["external_calls"].append({
                            "call": call_name,
                            "line": node.lineno
                        })
            
            return info
            
        except (SyntaxError, UnicodeDecodeError) as e:
            self.logger.warning(f"Could not parse {file_path}: {e}")
            return None
    
    def _get_base_name(self, base_node) -> str:
        """Extract base class name from AST node."""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{self._get_call_name(base_node.value)}.{base_node.attr}"
        return "Unknown"
    
    def _get_return_annotation(self, func_node) -> Optional[str]:
        """Extract return type annotation if present."""
        if func_node.returns:
            if isinstance(func_node.returns, ast.Name):
                return func_node.returns.id
            elif isinstance(func_node.returns, ast.Constant):
                return str(func_node.returns.value)
        return None
    
    def _get_call_name(self, call_node) -> str:
        """Extract the name of a function call."""
        if isinstance(call_node, ast.Name):
            return call_node.id
        elif isinstance(call_node, ast.Attribute):
            base = self._get_call_name(call_node.value) if hasattr(call_node, 'value') else ""
            return f"{base}.{call_node.attr}" if base else call_node.attr
        return ""
    
    def _analyze_integration_points(self):
        """Analyze integration points between components."""
        for file_path, component in self.components.items():
            self._check_component_interactions(file_path, component)
            self._check_interface_implementations(file_path, component)
    
    def _check_component_interactions(self, file_path: str, component: Dict[str, Any]):
        """Check for missing tests of component interactions."""
        external_calls = component.get("external_calls", [])
        
        if len(external_calls) > 5:  # Component has many external dependencies
            # Check if there are corresponding integration tests
            test_file_exists = self._has_integration_tests(file_path)
            
            if not test_file_exists:
                self.gaps.append(IntegrationGap(
                    gap_type=GapType.MISSING_COMPONENT_INTERACTION,
                    severity=GapSeverity.MEDIUM,
                    description=f"Component has {len(external_calls)} external calls but no integration tests",
                    file_path=file_path,
                    recommendation="Create integration tests to verify component interactions"
                ))
    
    def _check_interface_implementations(self, file_path: str, component: Dict[str, Any]):
        """Check for missing interface tests."""
        classes = component.get("classes", [])
        
        for class_info in classes:
            if class_info.get("bases"):  # Class implements interfaces/inherits
                if not self._has_interface_tests(file_path, class_info["name"]):
                    self.gaps.append(IntegrationGap(
                        gap_type=GapType.MISSING_INTERFACE_TEST,
                        severity=GapSeverity.HIGH,
                        description=f"Class {class_info['name']} implements interfaces but lacks interface tests",
                        file_path=file_path,
                        line_number=class_info.get("line"),
                        component1=class_info["name"],
                        recommendation="Add tests to verify interface contract compliance"
                    ))
    
    def _check_missing_tests(self):
        """Check for components without adequate test coverage."""
        for file_path, component in self.components.items():
            if not self._has_test_file(file_path):
                classes = len(component.get("classes", []))
                functions = len(component.get("functions", []))
                
                if classes > 0 or functions > 2:  # Significant component
                    self.gaps.append(IntegrationGap(
                        gap_type=GapType.INCOMPLETE_API_COVERAGE,
                        severity=GapSeverity.MEDIUM,
                        description=f"Component has {classes} classes and {functions} functions but no test file",
                        file_path=file_path,
                        recommendation="Create comprehensive test file for this component"
                    ))
    
    def _analyze_data_flows(self):
        """Analyze data flows for validation gaps."""
        for file_path, component in self.components.items():
            functions = component.get("functions", [])
            
            for func in functions:
                # Look for functions that process data but might lack validation
                if any(keyword in func["name"].lower() for keyword in 
                       ["process", "parse", "handle", "validate", "transform"]):
                    
                    if not self._has_validation_tests(file_path, func["name"]):
                        self.gaps.append(IntegrationGap(
                            gap_type=GapType.UNVALIDATED_DATA_FLOW,
                            severity=GapSeverity.HIGH,
                            description=f"Function {func['name']} processes data but lacks validation tests",
                            file_path=file_path,
                            line_number=func.get("line"),
                            recommendation="Add tests for data validation and error cases"
                        ))
    
    def _check_api_coverage(self):
        """Check for incomplete API test coverage."""
        for file_path, component in self.components.items():
            # Look for API-like patterns
            if any(keyword in file_path.lower() for keyword in ["api", "endpoint", "route", "handler"]):
                classes = component.get("classes", [])
                functions = component.get("functions", [])
                
                public_methods = 0
                for class_info in classes:
                    public_methods += len([m for m in class_info.get("methods", []) if not m.startswith("_")])
                
                public_functions = len([f for f in functions if not f["name"].startswith("_")])
                total_public = public_methods + public_functions
                
                if total_public > 0 and not self._has_comprehensive_api_tests(file_path):
                    self.gaps.append(IntegrationGap(
                        gap_type=GapType.INCOMPLETE_API_COVERAGE,
                        severity=GapSeverity.HIGH,
                        description=f"API component has {total_public} public methods but incomplete test coverage",
                        file_path=file_path,
                        recommendation="Create comprehensive API tests including error scenarios"
                    ))
    
    def _has_integration_tests(self, file_path: str) -> bool:
        """Check if component has integration tests."""
        test_patterns = [
            f"test_integration_{Path(file_path).stem}.py",
            f"integration_test_{Path(file_path).stem}.py",
            f"test_{Path(file_path).stem}_integration.py"
        ]
        
        test_dirs = ["tests", "test", "tests/integration"]
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    if (test_path / pattern).exists():
                        return True
        
        return False
    
    def _has_interface_tests(self, file_path: str, class_name: str) -> bool:
        """Check if class has interface/contract tests."""
        # Simple heuristic: look for test files that mention the class
        stem = Path(file_path).stem
        test_file = self.project_root / "tests" / f"test_{stem}.py"
        
        if test_file.exists():
            try:
                content = test_file.read_text(encoding='utf-8')
                return class_name.lower() in content.lower()
            except:
                pass
        
        return False
    
    def _has_test_file(self, file_path: str) -> bool:
        """Check if component has any test file."""
        stem = Path(file_path).stem
        test_patterns = [
            f"test_{stem}.py",
            f"{stem}_test.py",
            f"test_{stem}_unit.py"
        ]
        
        test_dirs = ["tests", "test"]
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    if (test_path / pattern).exists():
                        return True
        
        return False
    
    def _has_validation_tests(self, file_path: str, func_name: str) -> bool:
        """Check if function has validation tests."""
        stem = Path(file_path).stem
        test_file = self.project_root / "tests" / f"test_{stem}.py"
        
        if test_file.exists():
            try:
                content = test_file.read_text(encoding='utf-8')
                # Look for test methods that might test validation
                validation_keywords = ["validation", "error", "invalid", "exception"]
                return any(keyword in content.lower() and func_name.lower() in content.lower() 
                          for keyword in validation_keywords)
            except:
                pass
        
        return False
    
    def _has_comprehensive_api_tests(self, file_path: str) -> bool:
        """Check if API component has comprehensive tests."""
        stem = Path(file_path).stem
        test_patterns = [
            f"test_{stem}.py",
            f"test_{stem}_api.py",
            f"api_test_{stem}.py"
        ]
        
        for pattern in test_patterns:
            test_file = self.project_root / "tests" / pattern
            if test_file.exists():
                try:
                    content = test_file.read_text(encoding='utf-8')
                    # Look for comprehensive test indicators
                    indicators = ["error", "exception", "invalid", "edge", "boundary"]
                    return sum(1 for indicator in indicators if indicator in content.lower()) >= 2
                except:
                    pass
        
        return False
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate analysis report."""
        gaps_by_severity = {}
        for severity in GapSeverity:
            gaps_by_severity[severity.value] = [
                {
                    "type": gap.gap_type.value,
                    "description": gap.description,
                    "file_path": gap.file_path,
                    "line_number": gap.line_number,
                    "component1": gap.component1,
                    "component2": gap.component2,
                    "recommendation": gap.recommendation
                }
                for gap in self.gaps if gap.severity == severity
            ]
        
        return {
            "summary": {
                "total_components": len(self.components),
                "total_gaps": len(self.gaps),
                "critical_gaps": len([g for g in self.gaps if g.severity == GapSeverity.CRITICAL]),
                "high_priority_gaps": len([g for g in self.gaps if g.severity == GapSeverity.HIGH])
            },
            "gaps": [
                {
                    "type": gap.gap_type.value,
                    "severity": gap.severity.value,
                    "description": gap.description,
                    "file_path": gap.file_path,
                    "line_number": gap.line_number,
                    "component1": gap.component1,
                    "component2": gap.component2,
                    "recommendation": gap.recommendation
                }
                for gap in self.gaps
            ],
            "gaps_by_severity": gaps_by_severity,
            "components": [
                {
                    "file_path": path,
                    "classes": len(info.get("classes", [])),
                    "functions": len(info.get("functions", [])),
                    "external_calls": len(info.get("external_calls", []))
                }
                for path, info in self.components.items()
            ]
        }


def detect_integration_gaps():
    """Stub: Detect integration gaps (expand with real logic)."""
    # Placeholder: In a real system, analyze test and code integration
    return [
        {"file": "orchestration/qa_validation.py", "gap": "No integration test for error handling"},
        {"file": "agents/qa.py", "gap": "Missing test for edge case: empty input"}
    ]

if __name__ == "__main__":
    gaps = detect_integration_gaps()
    for gap in gaps:
        print(f"Integration gap: {gap['file']} - {gap['gap']}")
