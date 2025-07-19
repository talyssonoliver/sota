"""
Memory Engine Chunking Module

Provides text chunking functionality for the memory engine.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a text chunk"""

    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    overlap_with_previous: int = 0
    overlap_with_next: int = 0


class ChunkingStrategy:
    """Base class for chunking strategies"""

    def chunk(self, text: str, **kwargs) -> List[TextChunk]:
        """Chunk text into smaller pieces"""
        raise NotImplementedError


class CharacterChunker(ChunkingStrategy):
    """Simple character-based chunking"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """Initialize character chunker

        Args:
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """Chunk text by character count

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0
        index = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # Get chunk content
            content = text[start:end]

            # Calculate overlaps
            overlap_prev = self.overlap if start > 0 else 0
            overlap_next = self.overlap if end < len(text) else 0

            # Create chunk
            chunk = TextChunk(
                content=content,
                index=index,
                start_char=start,
                end_char=end,
                metadata=metadata or {},
                overlap_with_previous=overlap_prev,
                overlap_with_next=overlap_next,
            )

            chunks.append(chunk)

            # Move to next chunk
            start = end - self.overlap if end < len(text) else end
            index += 1

        return chunks


class SentenceChunker(ChunkingStrategy):
    """Sentence-aware chunking"""

    def __init__(self, target_chunk_size: int = 1000, max_chunk_size: int = 1500):
        """Initialize sentence chunker

        Args:
            target_chunk_size: Target size for each chunk
            max_chunk_size: Maximum allowed chunk size
        """
        self.target_chunk_size = target_chunk_size
        self.max_chunk_size = max_chunk_size
        self.sentence_endings = re.compile(r"[.!?]\s+")

    def chunk(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """Chunk text by sentences

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Split into sentences
        sentences = self.sentence_endings.split(text)

        chunks = []
        current_chunk = []
        current_size = 0
        start_char = 0
        index = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_size = len(sentence)

            # If sentence is too large, use character chunking
            if sentence_size > self.max_chunk_size:
                # Finish current chunk
                if current_chunk:
                    chunk_content = " ".join(current_chunk)
                    chunks.append(
                        TextChunk(
                            content=chunk_content,
                            index=index,
                            start_char=start_char,
                            end_char=start_char + len(chunk_content),
                            metadata=metadata or {},
                        )
                    )
                    index += 1
                    start_char += len(chunk_content) + 1
                    current_chunk = []
                    current_size = 0

                # Chunk the large sentence
                char_chunker = CharacterChunker(self.target_chunk_size, 100)
                sub_chunks = char_chunker.chunk(sentence, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk.index = index
                    sub_chunk.start_char += start_char
                    sub_chunk.end_char += start_char
                    chunks.append(sub_chunk)
                    index += 1
                start_char += sentence_size + 1
                continue

            # Check if adding sentence exceeds target size
            if current_size + sentence_size > self.target_chunk_size and current_chunk:
                # Create chunk
                chunk_content = " ".join(current_chunk)
                chunks.append(
                    TextChunk(
                        content=chunk_content,
                        index=index,
                        start_char=start_char,
                        end_char=start_char + len(chunk_content),
                        metadata=metadata or {},
                    )
                )
                index += 1
                start_char += len(chunk_content) + 1
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                # Add to current chunk
                current_chunk.append(sentence)
                current_size += sentence_size

        # Handle remaining sentences
        if current_chunk:
            chunk_content = " ".join(current_chunk)
            chunks.append(
                TextChunk(
                    content=chunk_content,
                    index=index,
                    start_char=start_char,
                    end_char=start_char + len(chunk_content),
                    metadata=metadata or {},
                )
            )

        return chunks


class ParagraphChunker(ChunkingStrategy):
    """Paragraph-aware chunking"""

    def __init__(self, target_chunk_size: int = 1000):
        """Initialize paragraph chunker

        Args:
            target_chunk_size: Target size for each chunk
        """
        self.target_chunk_size = target_chunk_size

    def chunk(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """Chunk text by paragraphs

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Split into paragraphs
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = []
        current_size = 0
        start_char = 0
        index = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            para_size = len(paragraph)

            # Check if adding paragraph exceeds target size
            if current_size + para_size > self.target_chunk_size and current_chunk:
                # Create chunk
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(
                    TextChunk(
                        content=chunk_content,
                        index=index,
                        start_char=start_char,
                        end_char=start_char + len(chunk_content),
                        metadata=metadata or {},
                    )
                )
                index += 1
                start_char += len(chunk_content) + 2  # +2 for \n\n
                current_chunk = [paragraph]
                current_size = para_size
            else:
                # Add to current chunk
                current_chunk.append(paragraph)
                current_size += para_size

        # Handle remaining paragraphs
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunks.append(
                TextChunk(
                    content=chunk_content,
                    index=index,
                    start_char=start_char,
                    end_char=start_char + len(chunk_content),
                    metadata=metadata or {},
                )
            )

        return chunks


class ChunkingManager:
    """Manages text chunking with multiple strategies"""

    def __init__(self):
        """Initialize chunking manager"""
        self.strategies = {
            "character": CharacterChunker(),
            "sentence": SentenceChunker(),
            "paragraph": ParagraphChunker(),
        }

    def chunk_text(
        self,
        text: str,
        strategy: str = "sentence",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[TextChunk]:
        """Chunk text using specified strategy

        Args:
            text: Text to chunk
            strategy: Chunking strategy ('character', 'sentence', 'paragraph')
            metadata: Optional metadata to attach to chunks
            **kwargs: Additional arguments for the chunking strategy

        Returns:
            List of text chunks
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        chunker = self.strategies[strategy]

        # Apply custom parameters if provided
        if kwargs:
            if strategy == "character" and "chunk_size" in kwargs:
                chunker = CharacterChunker(
                    chunk_size=kwargs.get("chunk_size", 1000),
                    overlap=kwargs.get("overlap", 200),
                )
            elif strategy == "sentence" and "target_chunk_size" in kwargs:
                chunker = SentenceChunker(
                    target_chunk_size=kwargs.get("target_chunk_size", 1000),
                    max_chunk_size=kwargs.get("max_chunk_size", 1500),
                )
            elif strategy == "paragraph" and "target_chunk_size" in kwargs:
                chunker = ParagraphChunker(
                    target_chunk_size=kwargs.get("target_chunk_size", 1000)
                )

        return chunker.chunk(text, metadata)

    def add_strategy(self, name: str, strategy: ChunkingStrategy):
        """Add custom chunking strategy

        Args:
            name: Strategy name
            strategy: ChunkingStrategy instance
        """
        self.strategies[name] = strategy


# Global chunking manager
_chunking_manager: Optional[ChunkingManager] = None


def get_chunking_manager() -> ChunkingManager:
    """Get the global chunking manager instance"""
    global _chunking_manager
    if _chunking_manager is None:
        _chunking_manager = ChunkingManager()
    return _chunking_manager
