import faiss
import numpy as np
from typing import List, Dict, Any
import json
from pathlib import Path
from config.config import STORAGE_CONFIG

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
                result = {
                    "metadata": self.metadata[idx],
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
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            raise FileNotFoundError("Index or metadata files not found") 