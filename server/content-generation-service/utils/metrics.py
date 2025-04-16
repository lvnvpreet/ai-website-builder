import re
import math
from typing import Dict, List, Any

class ContentQualityMetrics:
    """Calculate quality metrics for generated content."""
    
    def __init__(self):
        # Metrics weights (can be adjusted)
        self.weights = {
            "readability": 0.3,
            "diversity": 0.2,
            "seo_friendliness": 0.25,
            "structure": 0.25
        }
    
    def calculate_metrics(self, content: str) -> Dict[str, Any]:
        """
        Calculate various quality metrics for the content.
        
        Returns:
            Dict with metrics and overall score
        """
        # Split content into paragraphs, sentences and words
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        sentences = self._split_into_sentences(content)
        words = self._split_into_words(content)
        
        # Calculate individual metrics
        readability_score = self._calculate_readability(sentences, words)
        diversity_score = self._calculate_diversity(words)
        seo_score = self._calculate_seo_friendliness(content)
        structure_score = self._calculate_structure(paragraphs)
        
        # Calculate overall score (weighted average)
        overall_score = (
            readability_score * self.weights["readability"] +
            diversity_score * self.weights["diversity"] +
            seo_score * self.weights["seo_friendliness"] +
            structure_score * self.weights["structure"]
        )
        
        # Return all metrics
        return {
            "overall_score": round(overall_score, 2),
            "readability": {
                "score": round(readability_score, 2),
                "avg_sentence_length": round(sum(len(self._split_into_words(s)) for s in sentences) / max(len(sentences), 1), 1),
                "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1)
            },
            "diversity": {
                "score": round(diversity_score, 2),
                "unique_word_ratio": round(len(set(w.lower() for w in words)) / max(len(words), 1), 2),
                "vocabulary_richness": len(set(w.lower() for w in words))
            },
            "seo_friendliness": {
                "score": round(seo_score, 2),
                "heading_count": len(re.findall(r'^#{1,6}\s', content, re.MULTILINE)),
                "paragraph_count": len(paragraphs)
            },
            "structure": {
                "score": round(structure_score, 2),
                "paragraph_count": len(paragraphs),
                "section_count": len(re.findall(r'^#{2,6}\s', content, re.MULTILINE))
            },
            "word_count": len(words),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs)
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - could be improved with NLP libraries
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def _split_into_words(self, text: str) -> List[str]:
        """Split text into words."""
        # Remove special characters and split by whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        words = re.split(r'\s+', text)
        return [w for w in words if w.strip()]
    
    def _calculate_readability(self, sentences: List[str], words: List[str]) -> float:
        """
        Calculate readability score (simplified).
        
        Score is based on sentence length and word length.
        Higher score means more readable.
        """
        if not sentences or not words:
            return 0.0
            
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Simplified readability formula
        # Gives higher score to texts with reasonable sentence length (10-20 words)
        # and reasonable word length (4-6 characters)
        sentence_score = 1.0 - min(abs(avg_sentence_length - 15) / 20, 1.0)
        word_score = 1.0 - min(abs(avg_word_length - 5) / 5, 1.0)
        
        return 0.6 * sentence_score + 0.4 * word_score
    
    def _calculate_diversity(self, words: List[str]) -> float:
        """
        Calculate vocabulary diversity.
        
        Score based on ratio of unique words and vocabulary richness.
        """
        if not words:
            return 0.0
            
        # Calculate unique word ratio
        unique_words = set(w.lower() for w in words)
        unique_ratio = len(unique_words) / len(words)
        
        # Adjust score based on text length
        # Longer texts naturally have lower unique ratios
        adjustment = 0.1 * math.log10(max(len(words), 10))
        diversity_score = min(unique_ratio + adjustment, 1.0)
        
        return diversity_score
    
    def _calculate_seo_friendliness(self, content: str) -> float:
        """
        Calculate SEO friendliness score.
        
        Based on headings, paragraph structure, etc.
        """
        # Count headings
        headings = re.findall(r'^#{1,6}\s', content, re.MULTILINE)
        heading_score = min(len(headings) / 5, 1.0)
        
        # Check for h1 (main heading)
        has_h1 = bool(re.search(r'^#\s', content, re.MULTILINE))
        h1_score = 1.0 if has_h1 else 0.5
        
        # Count paragraphs
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        paragraph_score = min(len(paragraphs) / 10, 1.0)
        
        # Calculate overall SEO score
        seo_score = 0.4 * heading_score + 0.2 * h1_score + 0.4 * paragraph_score
        
        return seo_score
    
    def _calculate_structure(self, paragraphs: List[str]) -> float:
        """
        Calculate structure quality score.
        
        Based on paragraph length, section balance, etc.
        """
        if not paragraphs:
            return 0.0
            
        # Calculate average paragraph length
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs)
        paragraph_score = 1.0 - min(abs(avg_paragraph_length - 300) / 500, 1.0)
        
        # Calculate paragraph count score (prefer 3+ paragraphs)
        paragraph_count_score = min(len(paragraphs) / 5, 1.0)
        
        # Combine scores
        structure_score = 0.6 * paragraph_score + 0.4 * paragraph_count_score
        
        return structure_score