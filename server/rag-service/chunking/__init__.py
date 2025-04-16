from typing import Dict, Type, Optional, List
import logging
from .base import BaseChunker
from .text_chunker import TextChunker
from .document_chunker import DocumentChunker
from .code_chunker import CodeChunker

logger = logging.getLogger("rag_service.chunking")

# Register chunkers
_CHUNKERS: Dict[str, Type[BaseChunker]] = {
    "text": TextChunker,
    "document": DocumentChunker,
    "code": CodeChunker
}

def get_chunker(content_type: str, chunk_size: int = 500, chunk_overlap: int = 50) -> BaseChunker:
    """
    Get appropriate chunker for the content type.
    
    Args:
        content_type: Type of content to chunk (text, document, code)
        chunk_size: Target size of each chunk in tokens/chars
        chunk_overlap: Number of tokens/chars to overlap between chunks
        
    Returns:
        Appropriate chunker instance
    """
    content_type = content_type.lower()
    
    if content_type in _CHUNKERS:
        logger.info(f"Using {content_type} chunker with size={chunk_size}, overlap={chunk_overlap}")
        return _CHUNKERS[content_type](chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Use text chunker as default
    logger.warning(f"No chunker found for content type '{content_type}', using text chunker")
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

def get_available_chunkers() -> List[str]:
    """Get list of available chunker types."""
    return list(_CHUNKERS.keys())

def detect_content_type(content: str, metadata: Optional[Dict] = None) -> str:
    """
    Auto-detect the content type based on the content and metadata.
    
    Args:
        content: The text content to analyze
        metadata: Optional metadata about the content
        
    Returns:
        Detected content type ("text", "document", "code")
    """
    # Check metadata for content type hints
    if metadata:
        # Check for explicit content type
        if metadata.get("content_type"):
            content_type = metadata["content_type"].lower()
            if content_type in _CHUNKERS:
                return content_type
        
        # Check for file extension
        file_path = metadata.get("file_path", "")
        if file_path:
            if file_path.endswith((".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rb")):
                return "code"
            elif file_path.endswith((".md", ".txt", ".rst", ".docx", ".pdf")):
                return "document"
    
    # Analyze content
    # Check for code indicators
    code_patterns = [
        r'^\s*(import|from)\s+\w+',  # Python imports
        r'^\s*(def|class)\s+\w+',    # Python functions/classes
        r'^\s*(function|const|let|var)\s+\w+', # JavaScript
        r'^\s*(public|private|class)\s+\w+',  # Java/C#
    ]
    
    code_pattern_count = 0
    for pattern in code_patterns:
        if content.count(pattern) > 0:
            code_pattern_count += 1
    
    # Check for document structure
    has_headers = content.count('#') > 3  # Multiple headers suggest document
    has_paragraphs = content.count('\n\n') > 3  # Multiple paragraphs
    
    # Make decision based on indicators
    if code_pattern_count >= 2:
        return "code"
    elif has_headers and has_paragraphs:
        return "document"
    else:
        return "text"