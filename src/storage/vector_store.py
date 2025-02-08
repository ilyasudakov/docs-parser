import faiss
import numpy as np
from typing import List, Dict, Any
import json
from pathlib import Path
from ..config.config import STORAGE_CONFIG


class VectorStore:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or STORAGE_CONFIG
        self.index = None
        self.metadata = []

    def initialize_index(self, dimension: int):
        """Initialize a new FAISS index."""
        self.index = faiss.IndexFlatL2(dimension)

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add vectors and their metadata to the store."""
        if self.index is None:
            self.initialize_index(vectors.shape[1])

        # Add vectors to FAISS index
        self.index.add(vectors)

        # Debug print metadata being added
        print("Debug - Adding metadata samples:")
        for item in metadata[:2]:  # Print first 2 items
            print(f"Metadata item: {item}")

        # Store metadata
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors and return their metadata."""
        if self.index is None:
            raise ValueError("Index not initialized")

        # Reshape query vector if needed
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        # Search in the index
        distances, indices = self.index.search(query_vector, k)

        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # FAISS returns -1 for not found
                metadata = self.metadata[idx]
                # Print metadata for debugging
                print(f"Debug - Metadata at idx {idx}: {metadata}")

                result = {
                    "text": metadata.get('text', 'No text found'),
                    "metadata": {
                        key: value for key, value in metadata.items()
                        if key != 'text'
                    },
                    "distance": float(distance)
                }
                results.append(result)

        return results

    def save(self):
        """Save the index and metadata to disk."""
        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, self.config["index_path"])

            # Save metadata
            with open(self.config["metadata_path"], 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        """Load the index and metadata from disk."""
        index_path = Path(self.config["index_path"])
        metadata_path = Path(self.config["metadata_path"])

        if index_path.exists() and metadata_path.exists():
            self.index = faiss.read_index(str(index_path))

            # Load metadata and chunks
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

            # Try to load text from chunks if available
            chunks_dir = Path(self.config.get(
                "chunks_dir", "src/data/processed/chunks"))
            if chunks_dir.exists():
                # Load all chunk files
                for chunk_file in chunks_dir.glob("*.json"):
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        chunks = json.load(f)
                        # Update metadata with text from chunks
                        for chunk in chunks:
                            # Find matching metadata by source_url and chunk_index
                            for meta in self.metadata:
                                if (meta.get('source_url') == chunk['metadata']['source_url'] and
                                        meta.get('chunk_index') == chunk['metadata']['chunk_index']):
                                    meta['text'] = chunk['text']
                                    break
        else:
            raise FileNotFoundError("Index or metadata files not found")
