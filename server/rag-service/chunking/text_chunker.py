import re
from typing import List, Dict, Any
from .base import BaseChunker

class TextChunker(BaseChunker):
    """
    Chunker for generic text content that respects paragraph 
    and sentence boundaries.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        super().__init__(chunk_size, chunk_overlap)
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks respecting paragraph and sentence boundaries.
        
        Strategy:
        1. Split text into paragraphs
        2. For each paragraph, split into sentences if it's too long
        3. Combine sentences/paragraphs until target chunk size is reached
        4. Add overlap between chunks
        """
        # Clean the text by normalizing whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into paragraphs (preserving paragraph markers)
        paragraphs = re.split(r'(\n\s*\n|\r\n\s*\r\n)', text)
        
        # Initialize chunks
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            # Skip empty paragraphs
            if not para.strip():
                continue
                
            para_size = len(para)
            
            # If paragraph fits within chunk size, add it whole
            if para_size <= self.chunk_size:
                if current_size + para_size <= self.chunk_size:
                    current_chunk.append(para)
                    current_size += para_size
                else:
                    # Start a new chunk
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [para]
                    current_size = para_size
            else:
                # Paragraph too large, split into sentences
                sentences = self._split_into_sentences(para)
                
                for sentence in sentences:
                    sentence_size = len(sentence)
                    
                    # If sentence is too large for chunk_size, split it further
                    if sentence_size > self.chunk_size:
                        # Add current chunk if not empty
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                            current_size = 0
                        
                        # Split large sentence
                        sentence_chunks = self._split_large_sentence(sentence)
                        chunks.extend(sentence_chunks)
                    else:
                        # Normal sentence processing
                        if current_size + sentence_size <= self.chunk_size:
                            current_chunk.append(sentence)
                            current_size += sentence_size
                        else:
                            # Start a new chunk
                            chunks.append(' '.join(current_chunk))
                            current_chunk = [sentence]
                            current_size = sentence_size
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Add overlaps
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks_with_overlap = [chunks[0]]
            
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i-1]
                current_chunk = chunks[i]
                
                # Get overlap from end of previous chunk
                if len(prev_chunk) > self.chunk_overlap:
                    overlap = prev_chunk[-self.chunk_overlap:]
                    
                    # Find a word boundary to start the overlap
                    word_boundary = overlap.find(' ')
                    if word_boundary != -1:
                        overlap = overlap[word_boundary+1:]
                    
                    # Add overlap to current chunk
                    chunks_with_overlap.append(overlap + ' ' + current_chunk)
                else:
                    chunks_with_overlap.append(current_chunk)
            
            return chunks_with_overlap
        
        return chunks
    
    def get_chunk_metadata(self, chunk: str, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata for a chunk.
        
        For text chunks, we include:
        - First 100 chars as a preview
        - Word count
        - Character count
        - Source document metadata
        """
        # Get basic stats
        word_count = len(chunk.split())
        char_count = len(chunk)
        
        # Create metadata
        metadata = doc_metadata.copy()
        metadata.update({
            "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
            "word_count": word_count,
            "char_count": char_count,
            "chunk_type": "text"
        })
        
        return metadata
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex patterns."""
        # Use regex with lookbehind to keep the sentence delimiters
        sentence_delimiters = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_delimiters, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_large_sentence(self, sentence: str) -> List[str]:
        """Split a large sentence into smaller parts at word boundaries."""
        words = sentence.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            
            if current_size + word_size <= self.chunk_size:
                current_chunk.append(word)
                current_size += word_size
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks