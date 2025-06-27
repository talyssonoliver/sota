"""ChromaDB API models compatibility module."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Document:
    """ChromaDB document model."""
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None

@dataclass
class Collection:
    """ChromaDB collection model."""
    name: str
    metadata: Optional[Dict[str, Any]] = None
    
    def add(self, documents: List[str], metadatas: Optional[List[Dict]] = None, 
            ids: Optional[List[str]] = None):
        """Add documents to collection."""
        print(f"Adding {len(documents)} documents to collection {self.name}")
    
    def query(self, query_texts: List[str], n_results: int = 10) -> Dict[str, Any]:
        """Query the collection."""
        return {
            "ids": [["doc1", "doc2"]],
            "distances": [[0.1, 0.2]],
            "documents": [["Mock document 1", "Mock document 2"]],
            "metadatas": [[{}, {}]]
        }
    
    def delete(self, ids: List[str]):
        """Delete documents from collection."""
        print(f"Deleting {len(ids)} documents from collection {self.name}")

class Client:
    """ChromaDB client model."""
    
    def __init__(self):
        self.collections = {}
    
    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Collection:
        """Create a new collection."""
        collection = Collection(name=name, metadata=metadata)
        self.collections[name] = collection
        return collection
    
    def get_collection(self, name: str) -> Collection:
        """Get an existing collection."""
        if name in self.collections:
            return self.collections[name]
        return Collection(name=name)
    
    def delete_collection(self, name: str):
        """Delete a collection."""
        if name in self.collections:
            del self.collections[name]

__all__ = ['Document', 'Collection', 'Client']