"""
Dependency Injection Module

Implements Inversion of Control (IoC) container and dependency injection
patterns to support clean architecture and break circular dependencies.
"""

from .container import DependencyContainer, IContainer
from .interfaces import IServiceProvider, IServiceRegistry, ServiceLifetime
from .decorators import injectable, inject

__all__ = [
    "DependencyContainer",
    "IContainer", 
    "IServiceProvider",
    "IServiceRegistry",
    "injectable",
    "inject",
    "ServiceLifetime"
]