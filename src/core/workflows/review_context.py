"""Review context workflow."""


def review_context(context):
    """Review context."""
    return {"context": context, "review": "approved"}


__all__ = ["review_context"]
