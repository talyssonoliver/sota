
from src.infrastructure.utils.common_imports import Enum
"""
Dependency Injection Interfaces

Defines abstract interfaces for dependency injection following
the Interface Segregation and Dependency Inversion principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar, List, Callable
# from enum import Enum  # Consolidated to common_imports

T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime enumeration"""
    SINGLETON = "singleton"
    SCOPED = "scoped" 
    TRANSIENT = "transient"


class IServiceProvider(ABC):
    """Interface for service provider (service locator pattern)"""
    
    @abstractmethod
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """Get service instance by type"""
        pass
    
    @abstractmethod
    def get_required_service(self, service_type: Type[T]) -> T:
        """Get required service instance by type (raises exception if not found)"""
        pass
    
    @abstractmethod
    def get_services(self, service_type: Type[T]) -> List[T]:
        """Get all service instances of given type"""
        pass
    
    @abstractmethod
    def create_scope(self) -> 'IServiceProvider':
        """Create a new service scope"""
        pass


class IServiceRegistry(ABC):
    """Interface for service registration"""
    
    @abstractmethod
    def register_singleton(self, service_type: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        pass
    
    @abstractmethod
    def register_scoped(self, service_type: Type[T], implementation: Type[T]) -> None:
        """Register a scoped service"""
        pass
    
    @abstractmethod
    def register_transient(self, service_type: Type[T], implementation: Type[T]) -> None:
        """Register a transient service"""
        pass
    
    @abstractmethod
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a specific instance"""
        pass
    
    @abstractmethod
    def register_factory(self, service_type: Type[T], factory: Callable[['IServiceProvider'], T]) -> None:
        """Register a factory function"""
        pass
    
    @abstractmethod
    def is_registered(self, service_type: Type[T]) -> bool:
        """Check if service type is registered"""
        pass


class IContainer(IServiceProvider, IServiceRegistry):
    """Combined container interface"""
    
    @abstractmethod
    def build(self) -> 'IServiceProvider':
        """Build the container and return service provider"""
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """Dispose the container and all managed resources"""
        pass


class IDependencyResolver(ABC):
    """Interface for dependency resolution"""
    
    @abstractmethod
    def resolve_dependencies(self, service_type: Type[T]) -> Dict[str, Any]:
        """Resolve constructor dependencies for given type"""
        pass
    
    @abstractmethod
    def can_resolve(self, service_type: Type[T]) -> bool:
        """Check if dependencies can be resolved for given type"""
        pass


class IServiceDescriptor(ABC):
    """Interface for service descriptor"""
    
    @property
    @abstractmethod
    def service_type(self) -> Type:
        """Get service type"""
        pass
    
    @property
    @abstractmethod
    def implementation_type(self) -> Optional[Type]:
        """Get implementation type"""
        pass
    
    @property
    @abstractmethod
    def lifetime(self) -> ServiceLifetime:
        """Get service lifetime"""
        pass
    
    @property
    @abstractmethod
    def factory(self) -> Optional[Callable]:
        """Get factory function"""
        pass
    
    @property
    @abstractmethod
    def instance(self) -> Optional[Any]:
        """Get instance (for singleton registration)"""
        pass


class ILifetimeManager(ABC):
    """Interface for managing service lifetimes"""
    
    @abstractmethod
    def get_instance(self, descriptor: IServiceDescriptor, provider: IServiceProvider) -> Any:
        """Get instance based on lifetime management"""
        pass
    
    @abstractmethod
    def dispose_instances(self) -> None:
        """Dispose all managed instances"""
        pass


class IServiceActivator(ABC):
    """Interface for service activation"""
    
    @abstractmethod
    def create_instance(self, service_type: Type[T], provider: IServiceProvider) -> T:
        """Create instance of service type with dependency injection"""
        pass
    
    @abstractmethod
    def can_activate(self, service_type: Type[T]) -> bool:
        """Check if service type can be activated"""
        pass