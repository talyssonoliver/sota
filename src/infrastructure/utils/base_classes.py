
from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    logging,
    os
)
"""
Base Classes for Code Duplication Reduction

Enhanced base classes that encapsulate common patterns across the AI system
to reduce code duplication from 56.44% toward target of <3%.
Provides standardized interfaces for validation, configuration, API handling, and more.
"""

# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# import os  # Consolidated to common_imports
from abc import ABC, abstractmethod
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, Any, Optional, List, Union

from .common_utils import (
    setup_logging, read_json, write_json, safe_get_env, 
    is_test_mode, format_api_response
)


class BaseComponent(ABC):
    """Base class for system components with common initialization"""
    
    def __init__(self, name: str = None, config_path: str = None, **kwargs):
        self.name = name or self.__class__.__name__
        self.logger = setup_logging(f"{__name__}.{self.name}")
        self.config = self._load_config(config_path, **kwargs)
        self.initialized_at = datetime.now()
        self._setup()
    
    def _load_config(self, config_path: str = None, **kwargs) -> Dict[str, Any]:
        """Load configuration from file or kwargs"""
        # Start with defaults
        config = self._get_default_config().copy()
        
        # Load from file if provided (overrides defaults)
        if config_path:
            config.update(read_json(config_path, {}))
        
        # Update with kwargs (overrides file and defaults)
        config.update(kwargs)
        
        return config
    
    @abstractmethod
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this component"""
        pass
    
    def _setup(self):
        """Setup component after initialization (override in subclasses)"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        return {
            "name": self.name,
            "initialized_at": self.initialized_at.isoformat(),
            "config_loaded": self.config is not None,
            "status": "active"
        }


class BaseTool(BaseComponent):
    """Base class for tools with common patterns"""
    
    def __init__(self, name: str = None, **kwargs):
        self.token = None
        self.base_url = None
        super().__init__(name, **kwargs)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default tool configuration"""
        return {
            "timeout": 30,
            "retries": 3,
            "test_mode": is_test_mode()
        }
    
    def _setup(self):
        """Setup tool-specific configuration"""
        self._load_credentials()
        self._validate_config()
    
    def _load_credentials(self):
        """Load credentials from environment or config"""
        # Override in subclasses to load specific credentials
        pass
    
    def _validate_config(self):
        """Validate tool configuration"""
        required_fields = self._get_required_fields()
        missing_fields = []
        
        for field in required_fields:
            if not self.config.get(field) and not getattr(self, field, None):
                missing_fields.append(field)
        
        if missing_fields and not self.config.get("test_mode", False):
            self.logger.warning(f"Missing required fields: {missing_fields}")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required configuration fields"""
        return []
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute tool operation with error handling"""
        try:
            return self._execute(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return self._format_error_response(str(e))
    
    @abstractmethod
    def _execute(self, *args, **kwargs) -> Any:
        """Actual tool execution (implement in subclasses)"""
        pass
    
    def _format_success_response(self, data: Any, message: str = None) -> Dict[str, Any]:
        """Format successful response"""
        return format_api_response(
            data=data,
            status="success", 
            message=message or f"{self.name} operation completed"
        )
    
    def _format_error_response(self, error: str) -> Dict[str, Any]:
        """Format error response"""
        return format_api_response(
            status="error",
            errors=[error],
            message=f"{self.name} operation failed"
        )


class BaseAPITool(BaseTool):
    """Base class for API-based tools"""
    
    def _get_default_config(self) -> Dict[str, Any]:
        config = super()._get_default_config()
        config.update({
            "base_url": "http://localhost:3000",
            "timeout": 30,
            "verify_ssl": True
        })
        return config
    
    def _load_credentials(self):
        """Load API credentials"""
        # Look for token in multiple places
        token_env_vars = [
            f"{self.name.upper()}_TOKEN",
            f"{self.name.upper()}_API_KEY", 
            "API_TOKEN",
            "API_KEY"
        ]
        
        for env_var in token_env_vars:
            self.token = safe_get_env(env_var)
            if self.token:
                break
        
        # Load from config if not found in environment
        if not self.token:
            self.token = self.config.get("token") or self.config.get("api_key")
        
        # Load base URL
        url_env_vars = [
            f"{self.name.upper()}_BASE_URL",
            f"{self.name.upper()}_URL",
            "API_BASE_URL"
        ]
        
        for env_var in url_env_vars:
            self.base_url = safe_get_env(env_var)
            if self.base_url:
                break
        
        if not self.base_url:
            self.base_url = self.config.get("base_url")
    
    def _get_required_fields(self) -> List[str]:
        return ["token"] if not self.config.get("test_mode") else []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{self.name}-tool/1.0"
        }
        
        if self.token:
            # Try different authorization formats
            if self.token.startswith("Bearer "):
                headers["Authorization"] = self.token
            else:
                headers["Authorization"] = f"Bearer {self.token}"
        
        return headers


class BaseValidator(BaseComponent):
    """Base class for validators"""
    
    def __init__(self, name: str = None, **kwargs):
        self.issues: List[Dict[str, Any]] = []
        super().__init__(name, **kwargs)
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "strict_mode": False,
            "auto_fix": False,
            "max_issues": 1000
        }
    
    def validate(self, target: Any) -> Dict[str, Any]:
        """Validate target and return results"""
        self.issues.clear()
        
        try:
            self._validate_target(target)
            
            return {
                "valid": len(self.issues) == 0,
                "issues": self.issues[:self.config.get("max_issues", 1000)],
                "total_issues": len(self.issues),
                "validator": self.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "validator": self.name
            }
    
    @abstractmethod
    def _validate_target(self, target: Any):
        """Perform actual validation (implement in subclasses)"""
        pass
    
    def add_issue(self, severity: str, message: str, location: str = None, 
                  fix_suggestion: str = None):
        """Add validation issue"""
        issue = {
            "severity": severity,
            "message": message,
            "validator": self.name,
            "timestamp": datetime.now().isoformat()
        }
        
        if location:
            issue["location"] = location
        
        if fix_suggestion:
            issue["fix_suggestion"] = fix_suggestion
        
        self.issues.append(issue)


class BaseWorkflow(BaseComponent):
    """Base class for workflow components"""
    
    def __init__(self, name: str = None, **kwargs):
        self.state = "initialized"
        self.steps: List[Dict[str, Any]] = []
        super().__init__(name, **kwargs)
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "timeout": 300,  # 5 minutes
            "max_retries": 3,
            "parallel_execution": False
        }
    
    async def execute_workflow(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow with steps"""
        self.state = "running"
        context = context or {}
        results = []
        
        try:
            for step in self.steps:
                step_result = await self._execute_step(step, context)
                results.append(step_result)
                
                # Stop on failure if not configured to continue
                if not step_result.get("success", False) and not self.config.get("continue_on_error", False):
                    break
            
            self.state = "completed"
            
            return {
                "success": all(r.get("success", False) for r in results),
                "results": results,
                "workflow": self.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.state = "failed"
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow": self.name
            }
    
    @abstractmethod
    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        pass
    
    def add_step(self, name: str, handler: callable, **kwargs):
        """Add step to workflow"""
        self.steps.append({
            "name": name,
            "handler": handler,
            "config": kwargs
        })


class BaseService(BaseComponent):
    """Base class for service components"""
    
    def __init__(self, name: str = None, **kwargs):
        self.status = "stopped"
        super().__init__(name, **kwargs)
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "auto_start": True,
            "health_check_interval": 60,
            "max_retries": 5
        }
    
    def _setup(self):
        """Setup service"""
        if self.config.get("auto_start", True):
            self.start()
    
    def start(self) -> bool:
        """Start service"""
        try:
            self._start_service()
            self.status = "running"
            self.logger.info(f"Service {self.name} started")
            return True
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"Failed to start service {self.name}: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop service"""
        try:
            self._stop_service()
            self.status = "stopped"
            self.logger.info(f"Service {self.name} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop service {self.name}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            health_data = self._health_check()
            return {
                "healthy": True,
                "status": self.status,
                "service": self.name,
                "data": health_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "status": self.status,
                "service": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @abstractmethod
    def _start_service(self):
        """Start service implementation"""
        pass
    
    @abstractmethod
    def _stop_service(self):
        """Stop service implementation"""
        pass
    
    def _health_check(self) -> Dict[str, Any]:
        """Health check implementation (override in subclasses)"""
        return {"status": "ok"}


class BaseFileHandler:
    """Base class for file handling operations to eliminate file I/O duplication."""
    
    def __init__(self, root_path: Optional[str] = None):
        """Initialize file handler with root path."""
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.logger = setup_logging(f"{__name__}.{self.__class__.__name__}")
        self.processed_files: List[Path] = []
        self.failed_files: List[Path] = []
    
    def find_files(self, pattern: str = "*.py", 
                   exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """Find files matching pattern with common exclusions."""
        exclude_patterns = exclude_patterns or [
            "*/venv/*", "*/env/*", "*/__pycache__/*", "*/node_modules/*",
            "*.pyc", "*/migrations/*", "*/.git/*", "*/build/*", "*/dist/*"
        ]
        
        files = []
        for file_path in self.root_path.rglob(pattern):
            if file_path.is_file():
                # Check exclusions
                should_exclude = any(
                    file_path.match(exclude) for exclude in exclude_patterns
                )
                if not should_exclude:
                    files.append(file_path)
        
        return sorted(files)
    
    def read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file with encoding fallback."""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")
                return None
        
        self.logger.warning(f"Could not decode {file_path} with any encoding")
        return None
    
    def write_file_safely(self, file_path: Path, content: str, 
                         backup: bool = True) -> bool:
        """Safely write file with backup option."""
        try:
            # Create backup
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
                file_path.rename(backup_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.processed_files.append(file_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing {file_path}: {e}")
            self.failed_files.append(file_path)
            return False
    
    def get_file_stats(self) -> Dict[str, int]:
        """Get file processing statistics."""
        return {
            'processed': len(self.processed_files),
            'failed': len(self.failed_files),
            'total': len(self.processed_files) + len(self.failed_files)
        }


class BaseAnalyzer:
    """Base class for code analysis components."""
    
    def __init__(self, name: str):
        """Initialize analyzer."""
        self.name = name
        self.logger = setup_logging(f"{__name__}.{self.name}")
        self.results: Dict[str, Any] = {}
        self.metrics: Dict[str, Union[int, float]] = {}
    
    def analyze(self, target: Any) -> Dict[str, Any]:
        """Analyze target and return results."""
        try:
            start_time = datetime.now()
            
            # Perform analysis
            self._analyze_target(target)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'analyzer': self.name,
                'success': True,
                'duration_seconds': duration,
                'results': self.results,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {
                'analyzer': self.name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @abstractmethod
    def _analyze_target(self, target: Any):
        """Perform actual analysis (implement in subclasses)."""
        pass
    
    def add_metric(self, name: str, value: Union[int, float]):
        """Add analysis metric."""
        self.metrics[name] = value
    
    def add_result(self, key: str, value: Any):
        """Add analysis result."""
        self.results[key] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        return {
            'analyzer': self.name,
            'total_metrics': len(self.metrics),
            'total_results': len(self.results),
            'key_metrics': {k: v for k, v in list(self.metrics.items())[:5]}
        }


class BaseReporter:
    """Base class for report generation."""
    
    def __init__(self, name: str, output_dir: Optional[str] = None):
        """Initialize reporter."""
        self.name = name
        self.output_dir = Path(output_dir) if output_dir else Path("reports")
        self.logger = setup_logging(f"{__name__}.{self.name}")
        self.data: Dict[str, Any] = {}
    
    def add_data(self, key: str, value: Any):
        """Add data to report."""
        self.data[key] = value
    
    def generate_report(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate report."""
        try:
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate report content
            report_content = self._generate_content()
            
            # Save report if filename provided
            if filename:
                report_path = self.output_dir / filename
                success = write_json(report_path, report_content)
                
                return {
                    'success': success,
                    'report_path': str(report_path) if success else None,
                    'content': report_content,
                    'reporter': self.name
                }
            
            return {
                'success': True,
                'content': report_content,
                'reporter': self.name
            }
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'reporter': self.name
            }
    
    def _generate_content(self) -> Dict[str, Any]:
        """Generate report content (override in subclasses)."""
        return {
            'reporter': self.name,
            'timestamp': datetime.now().isoformat(),
            'data': self.data
        }


class BaseCache:
    """Base class for caching implementations."""
    
    def __init__(self, name: str, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize cache."""
        self.name = name
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.logger = setup_logging(f"{__name__}.{self.name}")
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        # Check TTL
        if self._is_expired(key):
            self.remove(key)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def remove(self, key: str):
        """Remove key from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self):
        """Clear entire cache."""
        self._cache.clear()
        self._timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._timestamps:
            return True
        
        age = (datetime.now() - self._timestamps[key]).total_seconds()
        return age > self.ttl_seconds
    
    def _evict_oldest(self):
        """Remove oldest cache entry."""
        if not self._timestamps:
            return
        
        oldest_key = min(self._timestamps.keys(), 
                        key=lambda k: self._timestamps[k])
        self.remove(oldest_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'name': self.name,
            'size': len(self._cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'utilization': len(self._cache) / self.max_size
        }