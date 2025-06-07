#!/usr/bin/env python3
"""
Dashboard Configuration Module

Centralized configuration management for the dashboard API server.
Supports environment-based configuration for different deployment scenarios.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DashboardConfig:
    """Dashboard configuration with environment variable support."""
    
    # Server configuration
    host: str = "localhost"
    port: int = 5000
    debug: bool = False
    
    # Directory paths
    outputs_dir: str = "outputs"
    dashboard_dir: str = "dashboard"
    logs_dir: str = "logs"
    
    # Cache configuration
    cache_ttl: int = 300  # 5 minutes
    background_refresh_interval: int = 60  # 1 minute
    
    # API configuration
    cors_enabled: bool = True
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    request_timeout: int = 30
    
    # Health check configuration
    health_check_interval: int = 30
    dependency_timeout: int = 5
    
    # Error handling
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    retry_attempts: int = 3
    retry_delay: int = 1
    
    @classmethod
    def from_environment(cls) -> 'DashboardConfig':
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv('DASHBOARD_HOST', 'localhost'),
            port=int(os.getenv('DASHBOARD_PORT', 5000)),
            debug=os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true',
            
            outputs_dir=os.getenv('DASHBOARD_OUTPUTS_DIR', 'outputs'),
            dashboard_dir=os.getenv('DASHBOARD_DIR', 'dashboard'),
            logs_dir=os.getenv('DASHBOARD_LOGS_DIR', 'logs'),
            
            cache_ttl=int(os.getenv('DASHBOARD_CACHE_TTL', 300)),
            background_refresh_interval=int(os.getenv('DASHBOARD_REFRESH_INTERVAL', 60)),
            
            cors_enabled=os.getenv('DASHBOARD_CORS_ENABLED', 'true').lower() == 'true',
            max_request_size=int(os.getenv('DASHBOARD_MAX_REQUEST_SIZE', 16777216)),
            request_timeout=int(os.getenv('DASHBOARD_REQUEST_TIMEOUT', 30)),
            
            health_check_interval=int(os.getenv('DASHBOARD_HEALTH_INTERVAL', 30)),
            dependency_timeout=int(os.getenv('DASHBOARD_DEPENDENCY_TIMEOUT', 5)),
            
            circuit_breaker_threshold=int(os.getenv('DASHBOARD_CB_THRESHOLD', 5)),
            circuit_breaker_timeout=int(os.getenv('DASHBOARD_CB_TIMEOUT', 60)),
            retry_attempts=int(os.getenv('DASHBOARD_RETRY_ATTEMPTS', 3)),
            retry_delay=int(os.getenv('DASHBOARD_RETRY_DELAY', 1))
        )
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path based on dashboard directory."""
        if relative_path == 'outputs':
            return Path(__file__).parent.parent / self.outputs_dir
        elif relative_path == 'dashboard':
            return Path(__file__).parent
        elif relative_path == 'logs':
            return Path(__file__).parent.parent / self.logs_dir
        else:
            return Path(__file__).parent / relative_path
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        try:
            # Check required directories exist or can be created
            for dir_name in ['outputs', 'dashboard', 'logs']:
                path = self.get_absolute_path(dir_name)
                path.mkdir(parents=True, exist_ok=True)
            
            # Validate port range
            if not (1024 <= self.port <= 65535):
                raise ValueError(f"Port {self.port} is not in valid range 1024-65535")
            
            # Validate positive integers
            if self.cache_ttl <= 0:
                raise ValueError("Cache TTL must be positive")
            
            if self.background_refresh_interval <= 0:
                raise ValueError("Background refresh interval must be positive")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False
