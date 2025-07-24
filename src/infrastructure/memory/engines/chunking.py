"""Chunking module."""


class ChunkProcessor:
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size

    def chunk_text(self, text):
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]

    def chunk(self, content, file_path, content_type=None):
        """Chunk content into smaller pieces with metadata."""
        text_chunks = self.chunk_text(content)
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            metadata = {
                "source_file": file_path,
                "chunk_index": i,
                "chunk_size": len(chunk_text),
            }
            if content_type:
                metadata["content_type"] = content_type

            chunk_data = {
                "text": chunk_text,
                "chunk_index": i,
                "source_file": file_path,
                "chunk_size": len(chunk_text),
                "metadata": metadata,
            }
            chunks.append(chunk_data)
        return chunks


__all__ = ["ChunkProcessor"]
