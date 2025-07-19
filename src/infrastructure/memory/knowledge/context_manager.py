#!/usr/bin/env python3
"""
Unified Context Manager

Manages context information from memory-bank/ in unified structure.
"""


try:
    from pathlib import Path
except ImportError:
    pass
try:
    from typing import Any, Dict
except ImportError:
    pass


class ContextManager:
    """Manages system context and knowledge."""

    def __init__(self, config=None):
        self.config = config
        self.knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self.contexts = {}
        self._load_contexts()

    def _load_contexts(self):
        """Load all context files."""
        context_files = {
            "active": "active_context.md",
            "product": "product_context.md",
            "technical": "tech_context.md",
            "system": "system_patterns.md",
            "progress": "progress.md",
            "project": "project_brief.md",
        }

        for context_type, filename in context_files.items():
            file_path = self.knowledge_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.contexts[context_type] = f.read()
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")
                    self.contexts[context_type] = ""
            else:
                self.contexts[context_type] = ""

    def get_context(self, context_type: str = "active") -> Dict[str, Any]:
        """Get context information."""
        content = self.contexts.get(context_type, "")

        return {
            "type": context_type,
            "content": content,
            "length": len(content),
            "available_types": list(self.contexts.keys()),
        }

    def update_context(self, context_type: str, updates: Dict[str, Any]) -> bool:
        """Update context information."""
        try:
            if context_type in self.contexts:
                # Simple update - in production this would be more sophisticated
                if "content" in updates:
                    self.contexts[context_type] = updates["content"]
                return True
            return False
        except Exception as e:
            print(f"Error updating context: {e}")
            return False

    def get_all_contexts(self) -> Dict[str, str]:
        """Get all loaded contexts."""
        return self.contexts.copy()
