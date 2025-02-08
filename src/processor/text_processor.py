from typing import List, Dict, Any
import json
from pathlib import Path
from config.config import PROCESSOR_CONFIG

class TextProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or PROCESSOR_CONFIG
        
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        text_length = len(text)
        start = 0
        
        while start < text_length:
            # Calculate end position for current chunk
            end = start + self.config["chunk_size"]
            
            # If this is not the last chunk, try to find a natural break point
            if end < text_length:
                # Look for the last period, question mark, or exclamation mark
                for break_char in ['. ', '? ', '! ']:
                    last_break = text[start:end].rfind(break_char)
                    if last_break != -1:
                        end = start + last_break + 2  # +2 to include the break character and space
                        break
            else:
                end = text_length
            
            # Get the chunk
            chunk = text[start:end].strip()
            
            # Only add chunks that meet the minimum size requirement
            if len(chunk) >= self.config["min_chunk_size"]:
                chunks.append(chunk)
            
            # Move the start position, accounting for overlap
            start = end - self.config["chunk_overlap"]
        
        return chunks
    
    def clean_chunk(self, chunk: str) -> str:
        """Clean and normalize a text chunk."""
        # Remove excessive whitespace
        chunk = ' '.join(chunk.split())
        
        # Basic cleaning rules can be added here
        return chunk
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a saved web page file into chunks with metadata."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data['content']
        chunks = self.chunk_text(text)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            cleaned_chunk = self.clean_chunk(chunk)
            chunk_data = {
                "text": cleaned_chunk,
                "metadata": {
                    "source_url": data['url'],
                    "chunk_index": i,
                    "timestamp": data['timestamp']
                }
            }
            processed_chunks.append(chunk_data)
        
        return processed_chunks 