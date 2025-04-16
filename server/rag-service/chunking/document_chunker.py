import re
from typing import List, Dict, Any
from .base import BaseChunker

class DocumentChunker(BaseChunker):
    """
    Chunker optimized for structured documents with headers, sections, etc.
    Preserves document structure during chunking.
    """
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        super().__init__(chunk_size, chunk_overlap)
    
    def split_text(self, text: str) -> List[str]:
        """
        Split document text into chunks, preserving section structure.
        
        Strategy:
        1. Identify section headers (markdown ## style or numbered sections)
        2. Split document into sections based on headers
        3. Process each section as a unit or split further if too large
        4. Maintain context by including section headers in chunks
        """
        # Identify section patterns (Markdown headings and numbered sections)
        section_pattern = r'(^#{1,5}\s+.+$|^\d+(\.\d+)*\s+.+$)'
        
        # Split text into lines
        lines = text.split('\n')
        
        # Group lines into sections
        sections = []
        current_section = []
        current_header = ""
        
        for line in lines:
            if re.match(section_pattern, line, re.MULTILINE):
                # Found a new section header
                if current_section:
                    # Store previous section with its header
                    sections.append({
                        "header": current_header,
                        "content": '\n'.join(current_section)
                    })
                
                current_header = line
                current_section = [line]  # Include header in content too
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                "header": current_header,
                "content": '\n'.join(current_section)
            })
        
        # Process sections into chunks
        chunks = []
        current_chunk = []
        current_size = 0
        last_header = ""
        
        for section in sections:
            section_content = section["content"]
            section_size = len(section_content)
            section_header = section["header"]
            
            # Small section that fits in current chunk
            if section_size + current_size <= self.chunk_size:
                current_chunk.append(section_content)
                current_size += section_size
                last_header = section_header if section_header else last_header
            
            # Section is too large for a single chunk
            elif section_size > self.chunk_size:
                # Add current chunk if not empty
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Split section into paragraphs
                paragraphs = re.split(r'\n\s*\n', section_content)
                
                # Always include header in first chunk
                current_chunk = [section_header] if section_header else []
                current_size = len(section_header) + 1 if section_header else 0
                
                for para in paragraphs:
                    para_size = len(para)
                    
                    # Paragraph fits in current chunk
                    if current_size + para_size <= self.chunk_size:
                        current_chunk.append(para)
                        current_size += para_size
                    
                    # Paragraph is too large, needs splitting
                    elif para_size > self.chunk_size:
                        # Add current chunk if not empty
                        if current_chunk:
                            chunks.append('\n'.join(current_chunk))
                            # Start new chunk with header context
                            current_chunk = [section_header] if section_header else []
                            current_size = len(section_header) + 1 if section_header else 0
                        
                        # Split paragraph into sentences
                        sentences = self._split_into_sentences(para)
                        
                        for sentence in sentences:
                            sentence_size = len(sentence)
                            
                            if current_size + sentence_size <= self.chunk_size:
                                current_chunk.append(sentence)
                                current_size += sentence_size
                            else:
                                # Start new chunk with context
                                chunks.append('\n'.join(current_chunk))
                                current_chunk = [section_header, sentence] if section_header else [sentence]
                                current_size = len(section_header) + len(sentence) + 1 if section_header else len(sentence)
                    
                    # Paragraph doesn't fit, start new chunk
                    else:
                        chunks.append('\n'.join(current_chunk))
                        # Start new chunk with header context
                        current_chunk = [section_header, para] if section_header else [para]
                        current_size = len(section_header) + len(para) + 1 if section_header else len(para)
                
                # Update last header
                last_header = section_header if section_header else last_header
            
            # Section doesn't fit in current chunk, start new one
            else:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [section_content]
                current_size = section_size
                last_header = section_header if section_header else last_header
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Add overlaps with context
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks_with_overlap = [chunks[0]]
            
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i-1]
                current_chunk = chunks[i]
                
                # Extract overlap from end of previous chunk
                if len(prev_chunk) > self.chunk_overlap:
                    overlap = prev_chunk[-self.chunk_overlap:]
                    
                    # Try to start at paragraph or sentence boundary
                    para_start = overlap.find('\n\n')
                    if para_start != -1:
                        overlap = overlap[para_start+2:]
                    else:
                        # Try sentence boundary
                        sentence_boundary = re.search(r'(?<=[.!?])\s+', overlap)
                        if sentence_boundary:
                            overlap = overlap[sentence_boundary.end():]
                    
                    # If already has a header, don't add overlap
                    if re.match(section_pattern, current_chunk.split('\n')[0], re.MULTILINE):
                        chunks_with_overlap.append(current_chunk)
                    else:
                        chunks_with_overlap.append(overlap + '\n\n' + current_chunk)
                else:
                    chunks_with_overlap.append(current_chunk)
            
            return chunks_with_overlap
        
        return chunks
    
    def get_chunk_metadata(self, chunk: str, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata for document chunks.
        
        For document chunks, we include:
        - Section heading if present
        - Hierarchical position in document
        - Word count
        - Original document metadata
        """
        # Extract section header if present
        section_pattern = r'(^#{1,5}\s+.+$|^\d+(\.\d+)*\s+.+$)'
        lines = chunk.split('\n')
        header = None
        
        for line in lines:
            if re.match(section_pattern, line, re.MULTILINE):
                header = line.strip()
                break
        
        # Get basic stats
        word_count = len(chunk.split())
        
        # Create metadata
        metadata = doc_metadata.copy()
        metadata.update({
            "section_header": header if header else "No header",
            "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
            "word_count": word_count,
            "chunk_type": "document"
        })
        
        return metadata
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex patterns."""
        # Use regex with lookbehind to keep the sentence delimiters
        sentence_delimiters = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_delimiters, text)
        return [s.strip() for s in sentences if s.strip()]