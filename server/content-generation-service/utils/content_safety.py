import re
import os
from typing import Dict, List, Tuple, Optional

class ContentSafetyFilter:
    """Filter for ensuring content safety."""
    
    def __init__(self):
        self.enabled = os.getenv("CONTENT_SAFETY_ENABLED", "true").lower() == "true"
        
        # Basic list of problematic patterns
        self.unsafe_patterns = [
            r"\b(porn|explicit sex|nude|naked)\b",
            r"\b(terrorist|bomb-making|radicalization)\b",
            r"\b(hack|crack|steal|illegal download)\b",
            r"\bhate\s*(speech|group|crime)\b",
            r"\b(phish|scam|fraud|identity theft)\b"
        ]
        
        # Load custom patterns if available
        custom_patterns_file = os.getenv("UNSAFE_PATTERNS_FILE")
        if custom_patterns_file and os.path.exists(custom_patterns_file):
            try:
                with open(custom_patterns_file, 'r') as f:
                    additional_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    self.unsafe_patterns.extend(additional_patterns)
            except Exception as e:
                print(f"Error loading custom unsafe patterns: {e}")
    
    def check_safety(self, content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check content safety.
        
        Returns:
            Tuple[bool, List[Dict]]: (is_safe, issues)
            - is_safe: True if content passes safety check
            - issues: List of detected issues with pattern and matches
        """
        if not self.enabled:
            return True, []
            
        issues = []
        
        # Check for unsafe patterns
        for pattern in self.unsafe_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            matches_list = list(matches)
            
            if matches_list:
                issues.append({
                    "pattern": pattern,
                    "matches": [content[m.start():m.end()] for m in matches_list],
                    "count": len(matches_list)
                })
        
        # Content is safe if no issues found
        is_safe = len(issues) == 0
        
        return is_safe, issues
    
    def redact_unsafe_content(self, content: str) -> Tuple[str, int]:
        """
        Redact unsafe content by replacing matches with [REDACTED].
        
        Returns:
            Tuple[str, int]: (redacted_content, redaction_count)
        """
        if not self.enabled:
            return content, 0
            
        redaction_count = 0
        redacted_content = content
        
        for pattern in self.unsafe_patterns:
            def redact_match(match):
                nonlocal redaction_count
                redaction_count += 1
                return "[REDACTED]"
                
            redacted_content = re.sub(pattern, redact_match, redacted_content, flags=re.IGNORECASE)
        
        return redacted_content, redaction_count