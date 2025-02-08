from typing import List, Dict, Any
import json
from pathlib import Path
from ..config.config import PROCESSOR_CONFIG
from tqdm import tqdm
import logging
import hashlib

logger = logging.getLogger(__name__)


class TextProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or PROCESSOR_CONFIG
        self.chunks_dir = Path(self.config["chunks_dir"])
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

    def generate_file_id(self, url: str) -> str:
        """Generate a unique file ID for the URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def get_chunks_path(self, url: str) -> Path:
        """Get the path for saving processed chunks."""
        file_id = self.generate_file_id(url)
        return self.chunks_dir / f"{file_id}_chunks.json"

    def load_cached_chunks(self, url: str) -> List[Dict[str, Any]]:
        """Try to load previously processed chunks."""
        chunks_path = self.get_chunks_path(url)
        if chunks_path.exists():
            logger.info(f"Loading cached chunks from {chunks_path}")
            with open(chunks_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_chunks(self, url: str, chunks: List[Dict[str, Any]]):
        """Save processed chunks to disk."""
        chunks_path = self.get_chunks_path(url)
        logger.info(f"Saving processed chunks to {chunks_path}")
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        sentences = []
        current_sentence = []

        # First, split into sentences for more efficient processing
        logger.info("Splitting text into sentences...")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            words = line.split()
            for word in words:
                current_sentence.append(word)
                if word.endswith(('.', '!', '?')):
                    sentences.append(' '.join(current_sentence))
                    current_sentence = []

        if current_sentence:
            sentences.append(' '.join(current_sentence))

        # Then create chunks from sentences
        logger.info("Creating chunks from sentences...")
        current_chunk = []
        current_size = 0

        for sentence in tqdm(sentences, desc="Processing chunks"):
            sentence_size = len(sentence)

            if current_size + sentence_size > self.config["chunk_size"]:
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if len(chunk_text) >= self.config["min_chunk_size"]:
                        chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0

            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 for space

        # Add the last chunk if it exists
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.config["min_chunk_size"]:
                chunks.append(chunk_text)

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def clean_chunk(self, chunk: str) -> str:
        """Clean and normalize a text chunk."""
        # Remove excessive whitespace
        chunk = ' '.join(chunk.split())

        # Remove very short lines
        lines = [line for line in chunk.splitlines() if len(line.strip()) > 10]
        chunk = ' '.join(lines)

        return chunk

    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a saved web page file into chunks with metadata."""
        logger.info(f"Processing file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Try to load cached chunks first
        cached_chunks = self.load_cached_chunks(data['url'])
        if cached_chunks is not None:
            logger.info("Using cached chunks")
            return cached_chunks

        text = data['content']
        chunks = self.chunk_text(text)

        logger.info("Cleaning chunks...")
        processed_chunks = []
        for i, chunk in enumerate(tqdm(chunks, desc="Cleaning chunks")):
            cleaned_chunk = self.clean_chunk(chunk)
            if cleaned_chunk:  # Only add non-empty chunks
                chunk_data = {
                    "text": cleaned_chunk,
                    "metadata": {
                        "source_url": data['url'],
                        "chunk_index": i,
                        "timestamp": data['timestamp']
                    }
                }
                processed_chunks.append(chunk_data)

        # Save processed chunks
        self.save_chunks(data['url'], processed_chunks)

        logger.info(f"Processed {len(processed_chunks)} chunks")
        return processed_chunks
