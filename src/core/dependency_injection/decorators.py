"""
Dependency Injection Decorators

Provides decorators for marking classes as injectable and
for automatic dependency injection.
"""

import functools
import inspect
from typing import Type, TypeVar, Any, Dict, Optional, get_type_hints
from .interfaces import IServiceProvider

T = TypeVar('T')


def injectable(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as injectable.
    
    This decorator adds metadata to the class to indicate it supports
    dependency injection and validates its constructor parameters.
    """
    # Validate that class can be injected
    try:
        signature = inspect.signature(cls.__init__)
        
        # Check for type annotations on parameters
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
                
            if param.annotation == inspect.Parameter.empty and param.default == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter '{param_name}' in {cls.__name__}.__init__ "
                    f"must have type annotation for dependency injection"
                )
    except Exception as e:
        raise ValueError(f"Class {cls.__name__} cannot be marked as injectable: {e}")
    
    # Add metadata to class
    setattr(cls, '_injectable', True)
    setattr(cls, '_injection_metadata', {
        'constructor_params': list(signature.parameters.keys())[1:],  # Exclude 'self'
        'type_hints': get_type_hints(cls.__init__)
    })
    
    return cls


def inject(service_provider: IServiceProvider):
    """
    Decorator factory for injecting dependencies into method parameters.
    
    Usage:
        @inject(service_provider)
        def my_function(param1: SomeService, param2: str = "default"):
            # param1 will be automatically injected
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            signature = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            # Resolve dependencies for parameters not provided
            for param_name, param in signature.parameters.items():
                if param_name not in kwargs and param_name in type_hints:
                    param_type = type_hints[param_name]
                    
                    # Try to get service from provider
                    service = service_provider.get_service(param_type)
                    if service is not None:
                        kwargs[param_name] = service
                    elif param.default == inspect.Parameter.empty:
                        # Required parameter not available
                        raise ValueError(
                            f"Cannot inject required parameter '{param_name}' "
                            f"of type {param_type.__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def auto_inject(cls: Type[T]) -> Type[T]:
    """
    Class decorator that automatically injects dependencies into the constructor.
    
    This decorator modifies the class to automatically resolve and inject
    dependencies when the class is instantiated, assuming a service provider
    is available.
    
    Note: This requires the class to be registered in a container that provides
    the service provider through a class attribute or global registry.
    """
    original_init = cls.__init__
    
    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # Try to get service provider from various sources
        service_provider = None
        
        # Check if class has a service provider attribute
        if hasattr(cls, '_service_provider'):
            service_provider = cls._service_provider
        
        # Check if there's a global service provider registry
        elif hasattr(cls, '_global_service_provider'):
            service_provider = cls._global_service_provider
        
        if service_provider is not None:
            # Get constructor signature
            signature = inspect.signature(original_init)
            type_hints = get_type_hints(original_init)
            
            # Resolve dependencies for parameters not provided
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                    
                if param_name not in kwargs and param_name in type_hints:
                    param_type = type_hints[param_name]
                    
                    # Try to get service from provider
                    service = service_provider.get_service(param_type)
                    if service is not None:
                        kwargs[param_name] = service
        
        # Call original constructor
        original_init(self, *args, **kwargs)
    
    cls.__init__ = new_init
    setattr(cls, '_auto_inject_enabled', True)
    
    return cls


class ServiceProviderHolder:
    """
    Utility class to hold service provider for auto-injection.
    
    This can be used to set a global service provider that auto_inject
    decorator can use.
    """
    _global_provider: Optional[IServiceProvider] = None
    
    @classmethod
    def set_global_provider(cls, provider: IServiceProvider):
        """Set global service provider"""
        cls._global_provider = provider
    
    @classmethod
    def get_global_provider(cls) -> Optional[IServiceProvider]:
        """Get global service provider"""
        return cls._global_provider
    
    @classmethod
    def clear_global_provider(cls):
        """Clear global service provider"""
        cls._global_provider = None


def requires(*service_types: Type):
    """
    Decorator to specify required service dependencies for a class.
    
    This is mainly for documentation and validation purposes.
    
    Usage:
        @requires(SomeService, AnotherService)
        @injectable
        class MyClass:
            def __init__(self, service1: SomeService, service2: AnotherService):
                self.service1 = service1
                self.service2 = service2
    """
    def decorator(cls: Type[T]) -> Type[T]:
        setattr(cls, '_required_services', service_types)
        
        # Validate that required services match constructor parameters
        try:
            signature = inspect.signature(cls.__init__)
            type_hints = get_type_hints(cls.__init__)
            
            constructor_types = set()
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                if param_name in type_hints:
                    constructor_types.add(type_hints[param_name])
            
            required_set = set(service_types)
            
            # Check if all required services are in constructor
            missing_in_constructor = required_set - constructor_types
            if missing_in_constructor:
                raise ValueError(
                    f"Required services {missing_in_constructor} not found in "
                    f"{cls.__name__} constructor"
                )
            
        except Exception as e:
            raise ValueError(f"Invalid @requires decorator on {cls.__name__}: {e}")
        
        return cls
    
    return decorator


def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as singleton.
    
    This is a marker decorator that can be used by dependency injection
    containers to automatically register the class as singleton.
    """
    setattr(cls, '_singleton', True)
    return cls


def scoped(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as scoped.
    
    This is a marker decorator that can be used by dependency injection
    containers to automatically register the class as scoped.
    """
    setattr(cls, '_scoped', True)
    return cls


def transient(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as transient.
    
    This is a marker decorator that can be used by dependency injection
    containers to automatically register the class as transient.
    """
    setattr(cls, '_transient', True)
    return cls


def get_injection_metadata(cls: Type) -> Dict[str, Any]:
    """
    Get injection metadata from a class.
    
    Returns dictionary with injection information or empty dict if not injectable.
    """
    if not hasattr(cls, '_injectable'):
        return {}
    
    return {
        'injectable': getattr(cls, '_injectable', False),
        'metadata': getattr(cls, '_injection_metadata', {}),
        'required_services': getattr(cls, '_required_services', []),
        'singleton': getattr(cls, '_singleton', False),
        'scoped': getattr(cls, '_scoped', False),
        'transient': getattr(cls, '_transient', False),
        'auto_inject_enabled': getattr(cls, '_auto_inject_enabled', False)
    }