from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

class BaseChunker(ABC):
    """Base class for document chunking strategies."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the chunker with configurable parameters.
        
        Args:
            chunk_size: Target size of each chunk in tokens/chars
            chunk_overlap: Number of tokens/chars to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(f"rag_service.chunking.{self.__class__.__name__}")
    
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks according to the chunking strategy.
        
        Args:
            text: The text to split into chunks
            
        Returns:
            List of text chunks
        """
        pass
    
    @abstractmethod
    def get_chunk_metadata(self, chunk: str, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract or generate metadata for a specific chunk.
        
        Args:
            chunk: The text chunk
            doc_metadata: The metadata of the original document
            
        Returns:
            Metadata dict for the chunk
        """
        pass
    
    def process_document(self, 
                        text: str, 
                        metadata: Dict[str, Any],
                        doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Process a document by splitting it into chunks and adding metadata.
        
        Args:
            text: The document text
            metadata: The document metadata
            doc_id: Optional document ID
            
        Returns:
            List of chunks with metadata
        """
        chunks = self.split_text(text)
        
        self.logger.info(f"Split document into {len(chunks)} chunks (avg size: {sum(len(c) for c in chunks) / max(1, len(chunks)):.1f} chars)")
        
        # Prepare document-level metadata
        doc_metadata = metadata.copy()
        if doc_id:
            doc_metadata["doc_id"] = doc_id
        
        # Process each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Skip empty chunks
            if not chunk.strip():
                continue
                
            # Create chunk with metadata
            chunk_metadata = self.get_chunk_metadata(chunk, doc_metadata)
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            processed_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return processed_chunks