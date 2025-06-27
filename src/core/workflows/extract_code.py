"""Extract code workflow."""

def extract_code(source, target=None):
    """Extract code from source."""
    return {"source": source, "target": target, "status": "extracted"}

__all__ = ["extract_code"]
