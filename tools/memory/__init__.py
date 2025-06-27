"""Module initialization."""

try:
    from .engine import MemoryEngine
    # Provide backward compatibility aliases
    Engine = MemoryEngine
    engine = MemoryEngine  # For cases where it's used as a class reference
    
    __all__ = ["MemoryEngine", "Engine", "engine"]
except ImportError:
    # Fallback if engine can't be imported
    class MockEngine:
        pass
    
    MemoryEngine = MockEngine
    Engine = MockEngine
    engine = MockEngine
    
    __all__ = ["MemoryEngine", "Engine", "engine"]
