"""
Memory Engine Chunking System
Handles semantic and adaptive chunking of documents
"""

import logging
import re
from typing import List, Dict, Any, Optional

from .config import ChunkingConfig
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class SemanticChunker:
    """
    Advanced semantic chunking with context awareness and overlap management.
    """
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self.min_chunk_size = config.min_chunk_size
        self.use_semantic_chunking = config.use_semantic_chunking
        
        # Semantic boundary patterns
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        self.paragraph_breaks = re.compile(r'\n\s*\n')
        self.section_headers = re.compile(r'^\s*#{1,6}\s+', re.MULTILINE)
        
        logger.info("SemanticChunker initialized")
    
    def chunk(self, text: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """
        Chunk text with semantic awareness and context preservation.
        
        Args:
            text: Text to chunk
            source: Source identifier for the text
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text or not text.strip():
            return []
        
        try:
            if self.use_semantic_chunking:
                chunks = self._semantic_chunk(text)
            else:
                chunks = self._simple_chunk(text)
            
            # Add metadata to chunks
            enriched_chunks = []
            for i, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    enriched_chunks.append({
                        'text': chunk_text.strip(),
                        'source': source,
                        'chunk_index': i,
                        'chunk_size': len(chunk_text),
                        'metadata': {
                            'total_chunks': len(chunks),
                            'chunk_method': 'semantic' if self.use_semantic_chunking else 'simple'
                        }
                    })
            
            logger.debug(f"Chunked text from {source} into {len(enriched_chunks)} chunks")
            return enriched_chunks
            
        except Exception as e:
            logger.error(f"Chunking failed for source {source}: {e}")
            raise ValidationError(f"Text chunking failed: {e}")
    
    def _semantic_chunk(self, text: str) -> List[str]:
        """
        Perform semantic chunking based on document structure.
        """
        chunks = []
        current_chunk = ""
        
        # First, try to split by sections (headers)
        sections = self.section_headers.split(text)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Process each section
            section_chunks = self._chunk_section(section)
            
            for section_chunk in section_chunks:
                if len(current_chunk) + len(section_chunk) <= self.chunk_size:
                    current_chunk += section_chunk
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = section_chunk
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_section(self, section: str) -> List[str]:
        """
        Chunk a section by paragraphs and sentences.
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = self.paragraph_breaks.split(section)
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # If paragraph is small enough, add it to current chunk
            if len(current_chunk) + len(paragraph) <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # Save current chunk if it exists
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Handle large paragraphs
                if len(paragraph) > self.chunk_size:
                    # Split large paragraph by sentences
                    sentence_chunks = self._chunk_by_sentences(paragraph)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk text by sentences when paragraphs are too large.
        """
        sentences = self.sentence_endings.split(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence = sentence.strip() + ". "
            
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Handle very long sentences
                if len(sentence) > self.chunk_size:
                    # Split by words as last resort
                    word_chunks = self._chunk_by_words(sentence)
                    chunks.extend(word_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_words(self, text: str) -> List[str]:
        """
        Chunk text by words when sentences are too large.
        """
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 <= self.chunk_size:
                current_chunk += word + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = word + " "
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _simple_chunk(self, text: str) -> List[str]:
        """
        Simple chunking by character count with word boundaries.
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Find word boundary
            while end > start and text[end] not in ' \n\t':
                end -= 1
            
            if end == start:  # No word boundary found
                end = start + self.chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Apply overlap
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks
    
    def estimate_chunks(self, text: str) -> int:
        """
        Estimate number of chunks without actual chunking.
        """
        if not text:
            return 0
        
        # Simple estimation based on text length
        estimated_chunks = max(1, len(text) // self.chunk_size)
        
        # Adjust for semantic boundaries if enabled
        if self.use_semantic_chunking:
            # Count section headers
            sections = len(self.section_headers.findall(text))
            if sections > 0:
                estimated_chunks = max(estimated_chunks, sections)
            
            # Count paragraphs
            paragraphs = len(self.paragraph_breaks.split(text))
            if paragraphs > estimated_chunks:
                estimated_chunks = min(estimated_chunks * 2, paragraphs)
        
        return estimated_chunks


class AdaptiveChunker:
    """
    Adaptive chunking that adjusts chunk size based on content type and complexity.
    """
    
    def __init__(self, config: ChunkingConfig):
        self.base_chunker = SemanticChunker(config)
        self.config = config
        
        # Content type patterns
        self.code_patterns = re.compile(r'```|def |class |function|import |from ')
        self.list_patterns = re.compile(r'^\s*[-*+]\s+', re.MULTILINE)
        self.table_patterns = re.compile(r'\|.*\|')
        
    def chunk(self, text: str, source: str = "unknown", 
              content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Adaptively chunk text based on detected content type.
        """
        if content_type is None:
            content_type = self._detect_content_type(text)
        
        # Adjust chunking parameters based on content type
        original_chunk_size = self.base_chunker.chunk_size
        
        try:
            if content_type == 'code':
                # Smaller chunks for code to preserve function boundaries
                self.base_chunker.chunk_size = min(800, original_chunk_size)
            elif content_type == 'list':
                # Medium chunks for lists to keep related items together
                self.base_chunker.chunk_size = min(1200, original_chunk_size)
            elif content_type == 'table':
                # Larger chunks for tables to preserve structure
                self.base_chunker.chunk_size = max(1500, original_chunk_size)
            
            chunks = self.base_chunker.chunk(text, source)
            
            # Add content type metadata
            for chunk in chunks:
                chunk['metadata']['content_type'] = content_type
                chunk['metadata']['adaptive_chunk_size'] = self.base_chunker.chunk_size
            
            return chunks
            
        finally:
            # Restore original chunk size
            self.base_chunker.chunk_size = original_chunk_size
    
    def _detect_content_type(self, text: str) -> str:
        """
        Detect the primary content type of the text.
        """
        # Count pattern matches
        code_matches = len(self.code_patterns.findall(text))
        list_matches = len(self.list_patterns.findall(text))
        table_matches = len(self.table_patterns.findall(text))
        
        # Simple heuristic based on pattern density
        text_length = len(text)
        if text_length == 0:
            return 'text'
        
        code_density = code_matches / (text_length / 1000)  # matches per 1000 chars
        list_density = list_matches / (text_length / 1000)
        table_density = table_matches / (text_length / 1000)
        
        # Determine primary content type
        if code_density > 2:
            return 'code'
        elif list_density > 5:
            return 'list'
        elif table_density > 3:
            return 'table'
        else:
            return 'text'