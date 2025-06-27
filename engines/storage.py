"""Engine storage module."""

class StorageEngine:
    def __init__(self):
        self.storage = {}
    
    def store(self, key, data):
        self.storage[key] = data
        return True
    
    def retrieve(self, key):
        return self.storage.get(key)

__all__ = ["StorageEngine"]
