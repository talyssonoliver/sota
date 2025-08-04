
from src.infrastructure.utils.common_imports import (
    Enum,
    Path,
    datetime,
    json,
    logging,
    os,
    traceback,
    uuid
)
"""
Error Reporting System

Provides comprehensive error reporting, logging, and notification
capabilities for the error handling framework.
"""

# import asyncio  # Consolidated to common_imports
# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass, field, asdict
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports

from .error_types import SystemError, ErrorSeverity, ErrorCategory


class ReportingLevel(Enum):
    """Error reporting levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReportingChannel(Enum):
    """Error reporting channels"""
    LOG = "log"
    FILE = "file"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"
    METRICS = "metrics"


@dataclass
class ErrorReport:
    """Comprehensive error report"""
    timestamp: str
    error_id: str
    error_type: str
    error_message: str
    severity: str
    category: str
    level: ReportingLevel
    
    # Context information
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    
    # System context
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Error details
    stack_trace: Optional[str] = None
    error_data: Dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_successful: bool = False
    
    # Metrics
    response_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert report to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class ReportingConfig:
    """Configuration for error reporting"""
    enabled: bool = True
    min_level: ReportingLevel = ReportingLevel.WARNING
    channels: List[ReportingChannel] = field(default_factory=lambda: [ReportingChannel.LOG])
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5
    include_stack_trace: bool = True
    include_system_metrics: bool = False
    buffer_size: int = 100
    flush_interval_seconds: int = 60


class IErrorReporter(Protocol):
    """Interface for error reporters"""
    
    async def report(self, error_report: ErrorReport) -> bool:
        """Report an error"""
        ...
    
    async def can_report(self, level: ReportingLevel) -> bool:
        """Check if can report at this level"""
        ...


class ConsoleErrorReporter:
    """Console-based error reporter"""
    
    def __init__(self, config: Optional[ReportingConfig] = None):
        self.config = config or ReportingConfig()
        self.logger = logging.getLogger(__name__)
    
    async def can_report(self, level: ReportingLevel) -> bool:
        """Check if can report at this level"""
        level_priority = {
            ReportingLevel.DEBUG: 0,
            ReportingLevel.INFO: 1,
            ReportingLevel.WARNING: 2,
            ReportingLevel.ERROR: 3,
            ReportingLevel.CRITICAL: 4
        }
        
        return level_priority.get(level, 0) >= level_priority.get(self.config.min_level, 2)
    
    async def report(self, error_report: ErrorReport) -> bool:
        """Report error to console"""
        try:
            if not await self.can_report(error_report.level):
                return True
            
            # Format error message
            message = f"[{error_report.timestamp}] {error_report.level.value.upper()}: {error_report.error_message}"
            
            if error_report.module:
                message += f" (in {error_report.module})"
            
            # Print to console with appropriate color
            if error_report.level == ReportingLevel.CRITICAL:
                print(f"\033[91m{message}\033[0m")  # Red
            elif error_report.level == ReportingLevel.ERROR:
                print(f"\033[31m{message}\033[0m")  # Dark red
            elif error_report.level == ReportingLevel.WARNING:
                print(f"\033[33m{message}\033[0m")  # Yellow
            elif error_report.level == ReportingLevel.INFO:
                print(f"\033[36m{message}\033[0m")  # Cyan
            else:
                print(message)  # Default
            
            # Print stack trace if available and enabled
            if (self.config.include_stack_trace and 
                error_report.stack_trace and 
                error_report.level in [ReportingLevel.ERROR, ReportingLevel.CRITICAL]):
                print(f"\033[90m{error_report.stack_trace}\033[0m")  # Gray
            
            return True
            
        except Exception as e:
            self.logger.error(f"Console reporter failed: {e}")
            return False


class LogErrorReporter:
    """Log-based error reporter"""
    
    def __init__(self, config: Optional[ReportingConfig] = None):
        self.config = config or ReportingConfig()
        self.logger = logging.getLogger("error_reporter")
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration"""
        # Configure formatter
        formatter = logging.Formatter(self.config.log_format)
        
        # Setup handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
    
    async def can_report(self, level: ReportingLevel) -> bool:
        """Check if can report at this level"""
        return self.config.enabled
    
    async def report(self, error_report: ErrorReport) -> bool:
        """Report error to log"""
        try:
            # Map reporting level to logging level
            level_map = {
                ReportingLevel.DEBUG: logging.DEBUG,
                ReportingLevel.INFO: logging.INFO,
                ReportingLevel.WARNING: logging.WARNING,
                ReportingLevel.ERROR: logging.ERROR,
                ReportingLevel.CRITICAL: logging.CRITICAL
            }
            
            log_level = level_map.get(error_report.level, logging.ERROR)
            
            # Create log message
            log_data = {
                "error_id": error_report.error_id,
                "error_type": error_report.error_type,
                "severity": error_report.severity,
                "category": error_report.category,
                "module": error_report.module,
                "recovery_attempted": error_report.recovery_attempted,
                "recovery_successful": error_report.recovery_successful
            }
            
            if error_report.error_data:
                log_data["error_data"] = error_report.error_data
            
            # Log the error
            self.logger.log(
                log_level,
                f"{error_report.error_message} | {json.dumps(log_data)}",
                extra=log_data
            )
            
            # Log stack trace separately if available
            if (self.config.include_stack_trace and 
                error_report.stack_trace and 
                error_report.level in [ReportingLevel.ERROR, ReportingLevel.CRITICAL]):
                self.logger.log(log_level, f"Stack trace:\n{error_report.stack_trace}")
            
            return True
            
        except Exception as e:
            print(f"Log reporter failed: {e}")  # Fallback to print
            return False


class FileErrorReporter:
    """File-based error reporter"""
    
    def __init__(self, config: Optional[ReportingConfig] = None):
        self.config = config or ReportingConfig()
        self.logger = logging.getLogger(__name__)
        self.file_path = Path(self.config.file_path or "error_reports.jsonl")
        self.buffer: List[ErrorReport] = []
        self.last_flush = datetime.now()
    
    async def can_report(self, level: ReportingLevel) -> bool:
        """Check if can report at this level"""
        return self.config.enabled and self.config.file_path is not None
    
    async def report(self, error_report: ErrorReport) -> bool:
        """Report error to file"""
        try:
            # Add to buffer
            self.buffer.append(error_report)
            
            # Check if we should flush
            should_flush = (
                len(self.buffer) >= self.config.buffer_size or
                (datetime.now() - self.last_flush).total_seconds() >= self.config.flush_interval_seconds or
                error_report.level == ReportingLevel.CRITICAL
            )
            
            if should_flush:
                await self._flush_buffer()
            
            return True
            
        except Exception as e:
            self.logger.error(f"File reporter failed: {e}")
            return False
    
    async def _flush_buffer(self):
        """Flush buffered reports to file"""
        if not self.buffer:
            return
        
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write reports to file (JSONL format)
            with open(self.file_path, 'a', encoding='utf-8') as f:
                for report in self.buffer:
                    f.write(report.to_json() + '\n')
            
            # Check file size and rotate if needed
            await self._rotate_file_if_needed()
            
            # Clear buffer
            self.buffer.clear()
            self.last_flush = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Failed to flush error reports: {e}")
    
    async def _rotate_file_if_needed(self):
        """Rotate file if it exceeds max size"""
        try:
            if not self.file_path.exists():
                return
            
            file_size_mb = self.file_path.stat().st_size / (1024 * 1024)
            
            if file_size_mb > self.config.max_file_size_mb:
                # Rotate files
                for i in range(self.config.backup_count - 1, 0, -1):
                    old_file = self.file_path.with_suffix(f'.{i}.jsonl')
                    new_file = self.file_path.with_suffix(f'.{i+1}.jsonl')
                    
                    if old_file.exists():
                        if new_file.exists():
                            new_file.unlink()
                        old_file.rename(new_file)
                
                # Move current file to .1
                backup_file = self.file_path.with_suffix('.1.jsonl')
                if backup_file.exists():
                    backup_file.unlink()
                self.file_path.rename(backup_file)
                
        except Exception as e:
            self.logger.error(f"File rotation failed: {e}")


class ErrorReporter:
    """Main error reporting coordinator"""
    
    def __init__(self, config: Optional[ReportingConfig] = None):
        self.config = config or ReportingConfig()
        self.reporters: Dict[ReportingChannel, IErrorReporter] = {}
        self.logger = logging.getLogger(__name__)
        self._setup_reporters()
    
    def _setup_reporters(self):
        """Setup default reporters based on configuration"""
        if ReportingChannel.CONSOLE in self.config.channels:
            self.reporters[ReportingChannel.CONSOLE] = ConsoleErrorReporter(self.config)
        
        if ReportingChannel.LOG in self.config.channels:
            self.reporters[ReportingChannel.LOG] = LogErrorReporter(self.config)
        
        if ReportingChannel.FILE in self.config.channels:
            self.reporters[ReportingChannel.FILE] = FileErrorReporter(self.config)
    
    def register_reporter(self, channel: ReportingChannel, reporter: IErrorReporter):
        """Register a custom reporter"""
        self.reporters[channel] = reporter
        self.logger.debug(f"Registered error reporter: {channel.value}")
    
    async def report_error(self, error: Exception, 
                          level: Optional[ReportingLevel] = None,
                          context: Optional[Dict[str, Any]] = None) -> ErrorReport:
        """Report an error through all configured channels"""
#         import traceback  # Consolidated to common_imports
#         import uuid  # Consolidated to common_imports
#         import os  # Consolidated to common_imports
        import psutil
        
        # Determine reporting level
        if level is None:
            if isinstance(error, SystemError):
                level_map = {
                    ErrorSeverity.LOW: ReportingLevel.INFO,
                    ErrorSeverity.MEDIUM: ReportingLevel.WARNING,
                    ErrorSeverity.HIGH: ReportingLevel.ERROR,
                    ErrorSeverity.CRITICAL: ReportingLevel.CRITICAL
                }
                level = level_map.get(error.severity, ReportingLevel.ERROR)
            else:
                level = ReportingLevel.ERROR
        
        # Create error report
        error_report = ErrorReport(
            timestamp=datetime.now().isoformat(),
            error_id=str(uuid.uuid4()),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=getattr(error, 'severity', ErrorSeverity.MEDIUM).value if hasattr(error, 'severity') else 'unknown',
            category=getattr(error, 'category', ErrorCategory.OPERATION).value if hasattr(error, 'category') else 'unknown',
            level=level,
            stack_trace=traceback.format_exc() if self.config.include_stack_trace else None,
            process_id=os.getpid(),
            recovery_attempted=getattr(error, 'recovery_attempted', False),
            recovery_successful=getattr(error, 'recovery_successful', False)
        )
        
        # Add context information
        if context:
            error_report.module = context.get('module')
            error_report.function = context.get('function')
            error_report.line_number = context.get('line_number')
            error_report.file_path = context.get('file_path')
            error_report.user_id = context.get('user_id')
            error_report.session_id = context.get('session_id')
            error_report.error_data.update(context.get('error_data', {}))
            error_report.metadata.update(context.get('metadata', {}))
        
        # Add system metrics if enabled
        if self.config.include_system_metrics:
            try:
                process = psutil.Process()
                error_report.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
                error_report.cpu_usage_percent = process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                self.logger.debug(f"Failed to collect system metrics: {e}")
            except Exception as e:
                self.logger.debug(f"Unexpected error collecting system metrics: {e}")
        
        # Report through all channels
        success_count = 0
        for channel, reporter in self.reporters.items():
            try:
                if await reporter.can_report(level):
                    success = await reporter.report(error_report)
                    if success:
                        success_count += 1
            except Exception as reporter_error:
                self.logger.error(f"Reporter {channel.value} failed: {reporter_error}")
        
        if success_count == 0:
            self.logger.error("All error reporters failed")
        
        return error_report
    
    async def report_system_error(self, system_error: SystemError,
                                 context: Optional[Dict[str, Any]] = None) -> ErrorReport:
        """Report a SystemError with enhanced context"""
        enhanced_context = context or {}
        enhanced_context.update({
            'error_data': {
                'recoverable': system_error.recoverable,
                'error_code': system_error.error_code,
                'component': system_error.component,
                'operation': system_error.operation
            }
        })
        
        return await self.report_error(system_error, context=enhanced_context)
    
    def get_reporting_stats(self) -> Dict[str, Any]:
        """Get error reporting statistics"""
        return {
            "config": {
                "enabled": self.config.enabled,
                "min_level": self.config.min_level.value,
                "channels": [ch.value for ch in self.config.channels]
            },
            "reporters": list(self.reporters.keys()),
            "total_reporters": len(self.reporters)
        }


# Global error reporter
_global_error_reporter: Optional[ErrorReporter] = None


def get_error_reporter() -> ErrorReporter:
    """Get global error reporter"""
    global _global_error_reporter
    if _global_error_reporter is None:
        _global_error_reporter = ErrorReporter()
    return _global_error_reporter


def configure_error_reporting(config: ReportingConfig):
    """Configure global error reporting"""
    global _global_error_reporter
    _global_error_reporter = ErrorReporter(config)


# Convenience function for quick error reporting
async def report_error(error: Exception, 
                      level: Optional[ReportingLevel] = None,
                      context: Optional[Dict[str, Any]] = None) -> ErrorReport:
    """Quick error reporting function"""
    reporter = get_error_reporter()
    return await reporter.report_error(error, level, context)