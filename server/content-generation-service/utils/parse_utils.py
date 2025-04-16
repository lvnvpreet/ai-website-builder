import re
import json
from typing import Dict, List, Any, Optional, Tuple

class ResponseParser:
    """Utilities to parse LLM responses into structured format."""
    
    @staticmethod
    def parse_sections(content: str) -> Dict[str, str]:
        """
        Parse markdown content into sections based on headings.
        
        Returns:
            Dict mapping section titles to content
        """
        # Split by heading markers
        sections = {}
        current_section = "introduction"
        current_content = []
        
        for line in content.split('\n'):
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                
                # Start new section
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                
                # Use heading text as section key, normalized
                section_key = heading_text.lower().replace(' ', '_')
                current_section = section_key
                
                # Add the heading line to the new section
                current_content.append(line)
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def extract_metadata(content: str) -> Dict[str, Any]:
        """
        Extract metadata from content like keywords, title suggestions, etc.
        
        Returns:
            Dict with extracted metadata
        """
        metadata = {}
        
        # Extract title (first h1 heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        # Extract keywords (if present in a specific format)
        keywords_match = re.search(r'(?:keywords|tags):\s*(.+?)(?:\n|$)', content, re.IGNORECASE | re.MULTILINE)
        if keywords_match:
            keywords = [k.strip() for k in keywords_match.group(1).split(',')]
            metadata["keywords"] = keywords
        
        # Extract description (first paragraph after title)
        if title_match:
            title_pos = content.find(title_match.group(0))
            after_title = content[title_pos + len(title_match.group(0)):].strip()
            first_para_match = re.search(r'^(.+?)(?:\n\n|\n#|$)', after_title, re.DOTALL)
            if first_para_match:
                metadata["description"] = first_para_match.group(1).strip()
        
        return metadata
    
    @staticmethod
    def parse_page_structure(content: str) -> Dict[str, Any]:
        """
        Parse content into structured page data with sections.
        
        Returns:
            Dict with page structure information
        """
        # Extract basic metadata
        metadata = ResponseParser.extract_metadata(content)
        
        # Parse into sections
        sections = ResponseParser.parse_sections(content)
        
        # Create section objects with ID and title
        structured_sections = []
        for section_id, section_content in sections.items():
            # Extract section title from the first heading
            title_match = re.search(r'^(#{1,6})\s+(.+)$', section_content, re.MULTILINE)
            title = title_match.group(2).strip() if title_match else section_id.replace('_', ' ').title()
            
            structured_sections.append({
                "id": section_id,
                "title": title,
                "content": section_content
            })
        
        # Build final structure
        page_structure = {
            "title": metadata.get("title", "Untitled Page"),
            "description": metadata.get("description", ""),
            "keywords": metadata.get("keywords", []),
            "sections": structured_sections
        }
        
        return page_structure
    
    @staticmethod
    def format_as_section_content(page_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format parsed page structure into SectionContent objects.
        
        Returns:
            List of section content objects ready for API response
        """
        sections = []
        
        for section in page_structure.get("sections", []):
            # Calculate simple SEO score based on content length and structure
            content = section.get("content", "")
            word_count = len(content.split())
            has_lists = bool(re.search(r'^\s*[-*]\s+', content, re.MULTILINE))
            has_paragraphs = len(content.split('\n\n')) > 1
            
            # Simple scoring algorithm
            seo_score = min(0.5 + (word_count / 1000) + (0.1 if has_lists else 0) + (0.1 if has_paragraphs else 0), 1.0)
            
            sections.append({
                "id": section.get("id", ""),
                "title": section.get("title", ""),
                "content": content,
                "seoScore": round(seo_score, 2)
            })
        
        return sections