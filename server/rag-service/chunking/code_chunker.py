import re
from typing import List, Dict, Any
from .base import BaseChunker

class CodeChunker(BaseChunker):
    """
    Specialized chunker for code documents that preserves:
    - Function/class definitions
    - Code blocks
    - Comments and docstrings
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        super().__init__(chunk_size, chunk_overlap)
        
        # Language-specific patterns
        self.language_patterns = {
            # Python patterns
            "python": {
                "import": r'^import\s+.+$|^from\s+.+\s+import\s+.+$',
                "class": r'^class\s+\w+',
                "function": r'^def\s+\w+',
                "docstring": r'""".*?"""|\'\'\'.+?\'\'\'',
                "comment": r'^\s*#.*$'
            },
            # JavaScript patterns
            "javascript": {
                "import": r'^import\s+.+$|^const\s+.+\s+=\s+require\(.+\)$',
                "class": r'^class\s+\w+',
                "function": r'^function\s+\w+|^\s*\w+\s*=\s*function|^\s*(const|let|var)\s+\w+\s*=\s*\(',
                "comment": r'\/\/.*$|\/\*[\s\S]*?\*\/'
            },
            # Java patterns
            "java": {
                "import": r'^import\s+.+;$',
                "class": r'^public\s+class\s+\w+|^class\s+\w+',
                "function": r'^(public|private|protected)?\s+(static\s+)?\w+\s+\w+\s*\(',
                "comment": r'\/\/.*$|\/\*[\s\S]*?\*\/'
            }
        }
    
    def split_text(self, text: str) -> List[str]:
        """
        Split code into chunks preserving logical units.
        
        Strategy:
        1. Detect programming language if possible
        2. Split code into logical units (functions, classes, etc.)
        3. Keep imports/includes together
        4. Preserve comments with associated code
        5. Handle indentation and code blocks
        """
        # Try to detect language
        language = self._detect_language(text)
        
        # Get language-specific patterns or use defaults
        patterns = self.language_patterns.get(language, self.language_patterns["python"])
        
        # Split code into lines
        lines = text.split('\n')
        
        # Group lines into logical units (classes, functions, blocks)
        code_units = []
        current_unit = []
        current_indent = 0
        in_block = False
        
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip() and not current_unit:
                continue
            
            # Check for structural elements
            is_import = bool(re.match(patterns["import"], line.strip(), re.MULTILINE)) if "import" in patterns else False
            is_class = bool(re.match(patterns["class"], line.strip(), re.MULTILINE)) if "class" in patterns else False
            is_function = bool(re.match(patterns["function"], line.strip(), re.MULTILINE)) if "function" in patterns else False
            is_comment = bool(re.match(patterns["comment"], line, re.MULTILINE)) if "comment" in patterns else False
            
            # Calculate line indentation
            line_indent = len(line) - len(line.lstrip())
            
            # Logic for when to start a new unit
            start_new_unit = False
            
            # Start new unit for structural elements if not in a block
            if not in_block and (is_import or is_class or is_function) and not is_comment:
                if current_unit:
                    start_new_unit = True
            
            # Check indentation changes to detect block endings
            elif current_unit and not in_block and line_indent <= current_indent and not is_comment:
                # Only end block if not an empty line
                if line.strip():
                    start_new_unit = True
            
            # Handle block endings
            if in_block and line_indent <= current_indent and i > 0:
                in_block = False
                
                # Check if the next line should start a new unit
                if is_class or is_function:
                    start_new_unit = True
            
            # Store completed unit and start new one if needed
            if start_new_unit:
                code_units.append('\n'.join(current_unit))
                current_unit = []
            
            # Add line to current unit
            current_unit.append(line)
            
            # Update tracking state
            if is_class or is_function:
                current_indent = line_indent
                in_block = True
        
        # Add the last unit
        if current_unit:
            code_units.append('\n'.join(current_unit))
        
        # Combine units into chunks that respect chunk_size
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Always include imports in first chunk
        imports = []
        for i, unit in enumerate(code_units):
            if re.match(patterns.get("import", ""), unit.strip(), re.MULTILINE):
                imports.append(unit)
                code_units[i] = None  # Mark as used
        
        # Filter out used units
        code_units = [u for u in code_units if u is not None]
        
        # Start with imports
        if imports:
            current_chunk = imports
            current_size = sum(len(imp) for imp in imports)
        
        # Process remaining units
        for unit in code_units:
            unit_size = len(unit)
            
            # Unit fits in current chunk
            if current_size + unit_size <= self.chunk_size:
                current_chunk.append(unit)
                current_size += unit_size
            
            # Unit doesn't fit, start new chunk
            elif unit_size <= self.chunk_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [unit]
                current_size = unit_size
            
            # Unit is too large, needs splitting
            else:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                
                # Split large unit into smaller chunks
                unit_lines = unit.split('\n')
                sub_chunk = []
                sub_size = 0
                
                for line in unit_lines:
                    line_size = len(line) + 1  # +1 for newline
                    
                    if sub_size + line_size <= self.chunk_size:
                        sub_chunk.append(line)
                        sub_size += line_size
                    else:
                        chunks.append('\n'.join(sub_chunk))
                        sub_chunk = [line]
                        sub_size = line_size
                
                if sub_chunk:
                    current_chunk = ['\n'.join(sub_chunk)]
                    current_size = sub_size
                else:
                    current_chunk = []
                    current_size = 0
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        # Add overlaps between chunks to maintain context
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks_with_overlap = [chunks[0]]
            
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i-1]
                current_chunk = chunks[i]
                
                # Get overlap from end of previous chunk
                if len(prev_chunk) > self.chunk_overlap:
                    overlap = prev_chunk[-self.chunk_overlap:]
                    
                    # Try to start at code unit boundary
                    code_boundary = overlap.find('\n\n')
                    if code_boundary != -1:
                        overlap = overlap[code_boundary+2:]
                    
                    # Add overlap to current chunk
                    chunks_with_overlap.append(f"{overlap}\n\n{current_chunk}")
                else:
                    chunks_with_overlap.append(current_chunk)
            
            return chunks_with_overlap
        
        return chunks
    
    def get_chunk_metadata(self, chunk: str, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata for code chunks.
        
        For code chunks, we include:
        - Detected language
        - Classes/functions defined
        - Line count
        - Original document metadata
        """
        # Detect language
        language = self._detect_language(chunk)
        
        # Get language patterns
        patterns = self.language_patterns.get(language, self.language_patterns["python"])
        
        # Extract defined classes and functions
        classes = []
        functions = []
        lines = chunk.split('\n')
        
        for line in lines:
            if "class" in patterns and re.match(patterns["class"], line.strip(), re.MULTILINE):
                # Extract class name
                class_match = re.search(r'class\s+(\w+)', line)
                if class_match:
                    classes.append(class_match.group(1))
            
            if "function" in patterns and re.match(patterns["function"], line.strip(), re.MULTILINE):
                # Extract function name (language specific)
                if language == "python":
                    func_match = re.search(r'def\s+(\w+)', line)
                    if func_match:
                        functions.append(func_match.group(1))
                elif language == "javascript":
                    # Multiple function declaration patterns
                    func_match = re.search(r'function\s+(\w+)|(\w+)\s*=\s*function|(?:const|let|var)\s+(\w+)\s*=\s*\(', line)
                    if func_match:
                        name = next((g for g in func_match.groups() if g), None)
                        if name:
                            functions.append(name)
                elif language == "java":
                    func_match = re.search(r'(?:public|private|protected)?\s+(?:static\s+)?\w+\s+(\w+)\s*\(', line)
                    if func_match:
                        functions.append(func_match.group(1))
        
        # Create metadata
        metadata = doc_metadata.copy()
        metadata.update({
            "language": language,
            "classes": classes,
            "functions": functions,
            "line_count": len(lines),
            "chunk_type": "code",
            "preview": '\n'.join(lines[:3]) + "..." if len(lines) > 3 else chunk
        })
        
        return metadata
    
    def _detect_language(self, code: str) -> str:
        """Attempt to detect programming language from code."""
        # Check for file extension in metadata if available
        
        # Check for language-specific patterns
        patterns = {
            "python": [
                r'import\s+[a-zA-Z_][a-zA-Z0-9_]*',
                r'from\s+[a-zA-Z_][a-zA-Z0-9_]*\s+import',
                r'def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(', 
                r'class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*:', 
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]'
            ],
            "javascript": [
                r'const\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=', 
                r'let\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=', 
                r'var\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=', 
                r'function\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(', 
                r'import\s+{[^}]*}\s+from\s+[\'"]'
            ],
            "java": [
                r'public\s+class\s+[a-zA-Z_$][a-zA-Z0-9_$]*', 
                r'private\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(', 
                r'public\s+static\s+void\s+main',
                r'import\s+java\.'
            ]
        }
        
        scores = {lang: 0 for lang in patterns}
        
        for lang, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, code):
                    scores[lang] += 1
        
        # Get language with highest score
        max_score = max(scores.values())
        if max_score > 0:
            for lang, score in scores.items():
                if score == max_score:
                    return lang
        
        # Default to python if no patterns match
        return "python"