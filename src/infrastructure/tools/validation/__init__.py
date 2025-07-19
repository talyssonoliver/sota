"""
Validation Infrastructure Package
Comprehensive code validation system for AI-driven development.
"""

from .ai.business_logic_protector import BusinessLogicProtector
from .ai.pattern_detector import AIPatternDetector
from .core.auto_fixer import AutoFixer
from .core.base_validator import BaseValidator
from .core.dependency_validator import DependencyValidator
from .core.issue_model import IssueType, SeverityLevel, ValidationIssue
from .core.performance_validator import PerformanceValidator
from .core.structure_validator import StructureValidator
from .core.syntax_validator import SyntaxValidator
from .core.validator import Validator

__all__ = [
    "BaseValidator",
    "ValidationIssue",
    "IssueType",
    "SeverityLevel",
    "Validator",
    "DependencyValidator",
    "SyntaxValidator",
    "StructureValidator",
    "PerformanceValidator",
    "AutoFixer",
    "AIPatternDetector",
    "BusinessLogicProtector",
]

__version__ = "3.0.0"
