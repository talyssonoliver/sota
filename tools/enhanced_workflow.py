# Replace the import line that's using get_debug with this:

try:
    from langchain_core.globals import get_debug
except ImportError:
    # Fallback if get_debug is not available
    def get_debug():
        return False
