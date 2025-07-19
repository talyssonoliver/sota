"""Thread safety utilities."""

try:
    import threading
except ImportError:
    pass


def thread_safe_decorator(func):
    """Thread safe decorator."""
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper


__all__ = ["thread_safe_decorator"]
