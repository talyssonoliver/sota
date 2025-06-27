"""Engine chunking module."""

class ChunkingEngine:
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size
    
    def chunk_text(self, text):
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

__all__ = ["ChunkingEngine"]
