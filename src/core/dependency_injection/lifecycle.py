"""
Service Lifecycle Management

Manages service lifetimes and provides utilities for proper
resource management in the dependency injection container.
"""

import weakref
import threading
from typing import Dict, Any, Set, Optional, Type, List
from abc import ABC, abstractmethod


class IDisposable(ABC):
    """Interface for disposable services"""
    
    @abstractmethod
    def dispose(self) -> None:
        """Dispose the service and release resources"""
        pass


class DisposableService(IDisposable):
    """Base class for disposable services"""
    
    def __init__(self):
        self._disposed = False
        self._lock = threading.Lock()
    
    def dispose(self) -> None:
        """Dispose the service and release resources"""
        with self._lock:
            if not self._disposed:
                self._dispose_resources()
                self._disposed = True
    
    def _dispose_resources(self) -> None:
        """Override this method to implement resource disposal"""
        pass
    
    @property
    def is_disposed(self) -> bool:
        """Check if service is disposed"""
        return self._disposed
    
    def _check_not_disposed(self):
        """Check if service is not disposed, raise exception if it is"""
        if self._disposed:
            raise RuntimeError(f"{self.__class__.__name__} has been disposed")


class ServiceLifecycleManager:
    """Manages service lifecycles and disposal"""
    
    def __init__(self):
        self._disposable_services: Set[weakref.ReferenceType] = set()
        self._singleton_instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
    
    def register_disposable(self, service: IDisposable) -> None:
        """Register a disposable service for lifecycle management"""
        with self._lock:
            weak_ref = weakref.ref(service, self._remove_weak_reference)
            self._disposable_services.add(weak_ref)
    
    def _remove_weak_reference(self, weak_ref: weakref.ReferenceType) -> None:
        """Remove weak reference when service is garbage collected"""
        with self._lock:
            self._disposable_services.discard(weak_ref)
    
    def register_singleton(self, service_type: Type, instance: Any) -> None:
        """Register singleton instance"""
        with self._lock:
            self._singleton_instances[service_type] = instance
            if isinstance(instance, IDisposable):
                self.register_disposable(instance)
    
    def register_scoped(self, service_type: Type, instance: Any) -> None:
        """Register scoped instance"""
        with self._lock:
            self._scoped_instances[service_type] = instance
            if isinstance(instance, IDisposable):
                self.register_disposable(instance)
    
    def get_singleton(self, service_type: Type) -> Optional[Any]:
        """Get singleton instance"""
        with self._lock:
            return self._singleton_instances.get(service_type)
    
    def get_scoped(self, service_type: Type) -> Optional[Any]:
        """Get scoped instance"""
        with self._lock:
            return self._scoped_instances.get(service_type)
    
    def dispose_scoped_services(self) -> None:
        """Dispose all scoped services"""
        with self._lock:
            for instance in self._scoped_instances.values():
                if isinstance(instance, IDisposable):
                    try:
                        instance.dispose()
                    except Exception as e:
                        # Log error but continue disposing other services
                        print(f"Error disposing scoped service: {e}")
            
            self._scoped_instances.clear()
    
    def dispose_all_services(self) -> None:
        """Dispose all managed services"""
        with self._lock:
            # Dispose scoped services first
            self.dispose_scoped_services()
            
            # Dispose singleton services
            for instance in self._singleton_instances.values():
                if isinstance(instance, IDisposable):
                    try:
                        instance.dispose()
                    except Exception as e:
                        # Log error but continue disposing other services
                        print(f"Error disposing singleton service: {e}")
            
            self._singleton_instances.clear()
            
            # Dispose any remaining services
            for weak_ref in list(self._disposable_services):
                service = weak_ref()
                if service is not None:
                    try:
                        service.dispose()
                    except Exception as e:
                        print(f"Error disposing service: {e}")
            
            self._disposable_services.clear()
    
    def get_service_count(self) -> Dict[str, int]:
        """Get count of services by type"""
        with self._lock:
            return {
                'singletons': len(self._singleton_instances),
                'scoped': len(self._scoped_instances),
                'disposable_tracked': len(self._disposable_services)
            }


class ScopedServiceContext:
    """Context manager for scoped services"""
    
    def __init__(self, lifecycle_manager: ServiceLifecycleManager):
        self._lifecycle_manager = lifecycle_manager
        self._initial_scoped_count = 0
    
    def __enter__(self):
        """Enter scoped context"""
        self._initial_scoped_count = len(self._lifecycle_manager._scoped_instances)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit scoped context and dispose scoped services"""
        self._lifecycle_manager.dispose_scoped_services()


class ServiceActivationTracker:
    """Tracks service activation for debugging and monitoring"""
    
    def __init__(self):
        self._activation_count: Dict[Type, int] = {}
        self._active_instances: Dict[Type, List[weakref.ReferenceType]] = {}
        self._lock = threading.Lock()
    
    def track_activation(self, service_type: Type, instance: Any) -> None:
        """Track service activation"""
        with self._lock:
            # Increment activation count
            self._activation_count[service_type] = self._activation_count.get(service_type, 0) + 1
            
            # Track active instance
            if service_type not in self._active_instances:
                self._active_instances[service_type] = []
            
            weak_ref = weakref.ref(instance, lambda ref: self._remove_instance(service_type, ref))
            self._active_instances[service_type].append(weak_ref)
    
    def _remove_instance(self, service_type: Type, weak_ref: weakref.ReferenceType) -> None:
        """Remove instance when garbage collected"""
        with self._lock:
            if service_type in self._active_instances:
                try:
                    self._active_instances[service_type].remove(weak_ref)
                except ValueError:
                    pass  # Reference already removed
    
    def get_activation_stats(self) -> Dict[Type, Dict[str, int]]:
        """Get activation statistics"""
        with self._lock:
            stats = {}
            for service_type in self._activation_count:
                active_count = len([ref for ref in self._active_instances.get(service_type, []) if ref() is not None])
                stats[service_type] = {
                    'total_activations': self._activation_count[service_type],
                    'active_instances': active_count
                }
            return stats
    
    def clear_stats(self) -> None:
        """Clear all tracking statistics"""
        with self._lock:
            self._activation_count.clear()
            self._active_instances.clear()


class ServiceHealthChecker:
    """Checks health of registered services"""
    
    def __init__(self, lifecycle_manager: ServiceLifecycleManager):
        self._lifecycle_manager = lifecycle_manager
    
    def check_service_health(self) -> Dict[str, Any]:
        """Check overall service health"""
        health_report = {
            'healthy': True,
            'service_counts': self._lifecycle_manager.get_service_count(),
            'issues': []
        }
        
        # Check for disposed services that are still referenced
        disposed_services = []
        for weak_ref in self._lifecycle_manager._disposable_services:
            service = weak_ref()
            if service is not None and isinstance(service, DisposableService) and service.is_disposed:
                disposed_services.append(service.__class__.__name__)
        
        if disposed_services:
            health_report['issues'].append(f"Disposed services still referenced: {disposed_services}")
            health_report['healthy'] = False
        
        return health_report
    
    def cleanup_disposed_references(self) -> int:
        """Clean up references to disposed services"""
        cleanup_count = 0
        weak_refs_to_remove = []
        
        for weak_ref in self._lifecycle_manager._disposable_services:
            service = weak_ref()
            if service is None or (isinstance(service, DisposableService) and service.is_disposed):
                weak_refs_to_remove.append(weak_ref)
                cleanup_count += 1
        
        for weak_ref in weak_refs_to_remove:
            self._lifecycle_manager._disposable_services.discard(weak_ref)
        
        return cleanup_count