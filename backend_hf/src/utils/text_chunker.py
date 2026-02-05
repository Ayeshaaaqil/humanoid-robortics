import re
from typing import List, Dict, Any


class TextChunker:
    """
    Utility for chunking text content while preserving document structure.
    """
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_by_headings(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text based on document headings to maintain semantic meaning.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of chunks with metadata
        """
        # Split the text by markdown headings
        # This regex finds markdown headings (##, ###, etc.)
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        lines = text.split('\n')
        
        chunks = []
        current_chunk = ""
        current_heading = "Introduction"
        prev_heading = ""
        
        for line in lines:
            if re.match(heading_pattern, line.strip()):
                # We found a heading
                match = re.match(heading_pattern, line.strip())
                if match:
                    # Save the current chunk before starting a new one
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "metadata": {
                                "heading": current_heading,
                                "prev_heading": prev_heading
                            }
                        })
                    
                    # Update headings
                    prev_heading = current_heading
                    current_heading = match.group(2)
                    current_chunk = line + "\n"
            else:
                # Add line to current chunk
                if len(current_chunk + line + "\n") < self.max_chunk_size:
                    current_chunk += line + "\n"
                else:
                    # Current chunk is too large, save it and start a new one
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "metadata": {
                                "heading": current_heading,
                                "prev_heading": prev_heading
                            }
                        })
                    
                    # Start new chunk with some overlap if possible
                    if len(line) > self.overlap:
                        overlap_text = line[-self.overlap:] + "\n"
                        current_chunk = overlap_text
                    else:
                        current_chunk = line + "\n"
        
        # Add the final chunk if it has content
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "heading": current_heading,
                    "prev_heading": prev_heading
                }
            })
        
        return chunks
    
    def chunk_by_size(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text by size with overlap.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            # If we're at the end, take the remaining text
            if end >= len(text):
                chunk = text[start:]
            else:
                # Find the nearest sentence boundary within the chunk
                chunk = text[start:end]
                
                # Try to break at sentence boundary
                last_period = chunk.rfind('. ')
                if last_period > 0 and last_period > self.max_chunk_size // 2:
                    end = start + last_period + 2
                    chunk = text[start:end]
            
            chunks.append({
                "content": chunk.strip(),
                "metadata": {
                    "start_pos": start,
                    "end_pos": end
                }
            })
            
            # Move start position with overlap
            if end >= len(text):
                break
            start = end - self.overlap if self.overlap < end else end
        
        return chunks