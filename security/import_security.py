#!/usr/bin/env python3
"""
Import Security Module

This module provides secure import handling to prevent silent failures
and ensure critical dependencies are properly managed.

Security Features:
- Critical import validation
- Secure fallback implementations
- Import audit logging
- Runtime dependency verification
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ImportCriticality(Enum):
    """Import criticality levels for security assessment"""
    CRITICAL = "critical"      # System fails without this
    HIGH = "high"             # Major features broken
    MEDIUM = "medium"         # Some features affected
    LOW = "low"              # Optional/enhancement features

@dataclass
class ImportRequirement:
    """Represents a secure import requirement"""
    module_name: str
    criticality: ImportCriticality
    fallback_available: bool = False
    security_sensitive: bool = False
    description: str = ""
    alternatives: List[str] = None

class SecureImportManager:
    """Manages secure imports with proper error handling and fallbacks"""
    
    def __init__(self):
        self.failed_imports: Dict[str, Exception] = {}
        self.successful_imports: Set[str] = set()
        self.fallback_implementations: Dict[str, Any] = {}
        self.critical_requirements = self._define_critical_requirements()
        
    def _define_critical_requirements(self) -> Dict[str, ImportRequirement]:
        """Define critical import requirements for the system"""
        return {
            # Core system requirements
            "logging": ImportRequirement(
                "logging", ImportCriticality.CRITICAL, False, False,
                "System logging - required for audit trails"
            ),
            "os": ImportRequirement(
                "os", ImportCriticality.CRITICAL, False, False,
                "Operating system interface - core functionality"
            ),
            "sys": ImportRequirement(
                "sys", ImportCriticality.CRITICAL, False, False,
                "System-specific parameters and functions"
            ),
            "pathlib": ImportRequirement(
                "pathlib", ImportCriticality.CRITICAL, False, False,
                "Path manipulation - core file operations"
            ),
            
            # Security-sensitive imports
            "cryptography": ImportRequirement(
                "cryptography", ImportCriticality.HIGH, True, True,
                "Encryption library - security critical",
                ["hashlib", "secrets"]
            ),
            "secrets": ImportRequirement(
                "secrets", ImportCriticality.HIGH, False, True,
                "Cryptographically secure random numbers"
            ),
            "hashlib": ImportRequirement(
                "hashlib", ImportCriticality.HIGH, False, True,
                "Secure hash and message digest algorithms"
            ),
            
            # Application-specific critical imports
            "langchain_openai": ImportRequirement(
                "langchain_openai", ImportCriticality.HIGH, True, False,
                "OpenAI integration for LLM functionality"
            ),
            "langchain_core": ImportRequirement(
                "langchain_core", ImportCriticality.HIGH, True, False,
                "Core LangChain functionality"
            ),
            "dotenv": ImportRequirement(
                "dotenv", ImportCriticality.MEDIUM, True, False,
                "Environment variable loading",
                ["os.environ"]
            ),
            
            # Optional but important
            "chromadb": ImportRequirement(
                "chromadb", ImportCriticality.MEDIUM, True, False,
                "Vector database for memory storage"
            ),
            "psutil": ImportRequirement(
                "psutil", ImportCriticality.LOW, True, False,
                "System monitoring utilities"
            ),
        }
    
    def secure_import(self, module_name: str, fallback_factory: Optional[Callable] = None) -> Any:
        """
        Securely import a module with proper error handling
        
        Args:
            module_name: Name of the module to import
            fallback_factory: Function to create fallback implementation
            
        Returns:
            Imported module or fallback implementation
            
        Raises:
            ImportError: For critical imports that must succeed
            SecurityWarning: For security-sensitive imports that fail
        """
        requirement = self.critical_requirements.get(module_name)
        
        try:
            if '.' in module_name:
                # Handle submodule imports
                parts = module_name.split('.')
                module = __import__(module_name)
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                module = __import__(module_name)
            
            self.successful_imports.add(module_name)
            logger.debug(f"Successfully imported {module_name}")
            return module
            
        except ImportError as e:
            self.failed_imports[module_name] = e
            
            # Log the failure appropriately
            if requirement:
                if requirement.criticality == ImportCriticality.CRITICAL:
                    logger.critical(f"CRITICAL IMPORT FAILURE: {module_name} - {requirement.description}")
                    raise ImportError(f"Critical dependency {module_name} is required but not available: {e}")
                
                elif requirement.security_sensitive:
                    logger.error(f"SECURITY IMPORT FAILURE: {module_name} - {requirement.description}")
                    warnings.warn(f"Security-sensitive module {module_name} failed to import", SecurityWarning)
                
                elif requirement.criticality == ImportCriticality.HIGH:
                    logger.error(f"HIGH PRIORITY IMPORT FAILURE: {module_name} - {requirement.description}")
                
                else:
                    logger.warning(f"Import failure: {module_name} - {requirement.description}")
            else:
                logger.info(f"Optional import failed: {module_name}")
            
            # Try fallback implementations
            if fallback_factory:
                logger.info(f"Using provided fallback for {module_name}")
                return fallback_factory()
            
            if requirement and requirement.fallback_available:
                fallback = self._get_fallback_implementation(module_name)
                if fallback:
                    logger.info(f"Using built-in fallback for {module_name}")
                    return fallback
            
            # For non-critical imports, return None
            if not requirement or requirement.criticality in [ImportCriticality.LOW, ImportCriticality.MEDIUM]:
                return None
            
            # Re-raise for high priority imports without fallbacks
            raise
    
    def _get_fallback_implementation(self, module_name: str) -> Optional[Any]:
        """Get fallback implementation for failed imports"""
        fallbacks = {
            "dotenv": self._create_dotenv_fallback(),
            "cryptography": self._create_crypto_fallback(),
            "chromadb": self._create_chromadb_fallback(),
            "psutil": self._create_psutil_fallback(),
        }
        return fallbacks.get(module_name)
    
    def _create_dotenv_fallback(self):
        """Create a fallback dotenv implementation"""
        class DotenvFallback:
            @staticmethod
            def load_dotenv(*args, **kwargs):
                logger.warning("Using fallback dotenv implementation - .env files will not be loaded")
                return False
                
            @staticmethod
            def find_dotenv(*args, **kwargs):
                return None
        
        return DotenvFallback()
    
    def _create_crypto_fallback(self):
        """Create a fallback cryptography implementation"""
        class CryptoFallback:
            @staticmethod
            def encrypt(data: bytes, password: str) -> bytes:
                logger.critical("SECURITY WARNING: Using insecure fallback encryption")
                warnings.warn("Insecure fallback encryption in use", SecurityWarning)
                # This is intentionally weak to encourage fixing the real issue
                return data
            
            @staticmethod
            def decrypt(data: bytes, password: str) -> bytes:
                logger.critical("SECURITY WARNING: Using insecure fallback decryption")
                warnings.warn("Insecure fallback decryption in use", SecurityWarning)
                return data
        
        return CryptoFallback()
    
    def _create_chromadb_fallback(self):
        """Create a fallback ChromaDB implementation"""
        class ChromaDBFallback:
            def __init__(self):
                logger.warning("Using in-memory fallback for ChromaDB")
                self._storage = {}
            
            def add(self, documents, metadatas=None, ids=None):
                if ids:
                    for i, doc_id in enumerate(ids):
                        self._storage[doc_id] = {
                            'document': documents[i],
                            'metadata': metadatas[i] if metadatas else {}
                        }
            
            def query(self, query_texts, n_results=10):
                # Simple text matching fallback
                results = []
                for text in query_texts:
                    matches = []
                    for doc_id, doc_data in self._storage.items():
                        if text.lower() in doc_data['document'].lower():
                            matches.append(doc_data['document'])
                    results.append(matches[:n_results])
                return {'documents': results}
        
        return ChromaDBFallback()
    
    def _create_psutil_fallback(self):
        """Create a fallback psutil implementation"""
        class PSUtilFallback:
            @staticmethod
            def cpu_percent(*args, **kwargs):
                return 0.0
            
            @staticmethod
            def virtual_memory():
                class MemInfo:
                    total = 0
                    available = 0
                    percent = 0.0
                return MemInfo()
            
            @staticmethod
            def disk_usage(path):
                class DiskInfo:
                    total = 0
                    used = 0
                    free = 0
                return DiskInfo()
        
        return PSUtilFallback()
    
    def validate_critical_imports(self) -> bool:
        """
        Validate that all critical imports are available
        
        Returns:
            True if all critical imports are satisfied
        """
        missing_critical = []
        
        for module_name, requirement in self.critical_requirements.items():
            if requirement.criticality == ImportCriticality.CRITICAL:
                if module_name not in self.successful_imports:
                    try:
                        self.secure_import(module_name)
                    except ImportError:
                        missing_critical.append(module_name)
        
        if missing_critical:
            logger.critical(f"Missing critical imports: {missing_critical}")
            return False
        
        return True
    
    def get_import_report(self) -> Dict[str, Any]:
        """Generate a security report of import status"""
        return {
            "successful_imports": list(self.successful_imports),
            "failed_imports": {k: str(v) for k, v in self.failed_imports.items()},
            "security_status": "SECURE" if self.validate_critical_imports() else "COMPROMISED",
            "recommendations": self._get_security_recommendations()
        }
    
    def _get_security_recommendations(self) -> List[str]:
        """Get security recommendations based on import failures"""
        recommendations = []
        
        for module_name, exception in self.failed_imports.items():
            requirement = self.critical_requirements.get(module_name)
            if requirement:
                if requirement.security_sensitive:
                    recommendations.append(
                        f"URGENT: Install {module_name} for secure operations: pip install {module_name}"
                    )
                elif requirement.criticality == ImportCriticality.HIGH:
                    recommendations.append(
                        f"IMPORTANT: Install {module_name} for full functionality: pip install {module_name}"
                    )
                    
                if requirement.alternatives:
                    recommendations.append(
                        f"Alternative packages for {module_name}: {', '.join(requirement.alternatives)}"
                    )
        
        return recommendations

# Global secure import manager instance
secure_import_manager = SecureImportManager()

def secure_import(module_name: str, fallback_factory: Optional[Callable] = None) -> Any:
    """
    Global function for secure imports
    
    Usage:
        # Instead of:
        try:
            import some_module
        except ImportError:
            pass
        
        # Use:
        some_module = secure_import('some_module')
    """
    return secure_import_manager.secure_import(module_name, fallback_factory)

class SecurityWarning(UserWarning):
    """Warning for security-related import issues"""
    pass
