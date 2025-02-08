from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from ..config.config import VECTORIZER_CONFIG


class TextEmbedder:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or VECTORIZER_CONFIG
        self.model = SentenceTransformer(
            self.config["model_name"],
            device=self.config["device"]
        )

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.model.encode(text)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        return self.model.encode(texts)

    def process_chunks(self, chunks: List[Dict[str, Any]]) -> tuple[np.ndarray, List[Dict[str, Any]]]:
        """Process a list of chunks into embeddings and metadata."""
        texts = [chunk["text"] for chunk in chunks]
        metadata = [chunk["metadata"] for chunk in chunks]

        embeddings = self.embed_batch(texts)
        return embeddings, metadata
