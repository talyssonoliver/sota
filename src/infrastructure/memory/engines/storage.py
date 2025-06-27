"""Storage module."""

class StorageManager:
    def __init__(self):
        self.storage = {}
        self.metadata = {}
    
    def store(self, key, data):
        self.storage[key] = data
        return True
    
    def store_data(self, key, data, metadata=None):
        """Store data with optional metadata."""
        self.storage[key] = data
        if metadata:
            self.metadata[key] = metadata
        return True
    
    def retrieve(self, key):
        return self.storage.get(key)
    
    def retrieve_data(self, key):
        """Retrieve data and metadata."""
        data = self.storage.get(key)
        metadata = self.metadata.get(key, {})
        return {'data': data, 'metadata': metadata} if data else None

__all__ = ["StorageManager"]
