"""Simple review context workflow."""


def review_context_simple(context):
    """Simple review context."""
    return {"context": context, "review": "simple_approved"}


__all__ = ["review_context_simple"]
