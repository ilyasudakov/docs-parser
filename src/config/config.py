from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"  # This will be src/data
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_DIR = PROCESSED_DIR / "chunks"
VECTORS_DIR = PROCESSED_DIR / "vectors"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, CHUNKS_DIR, VECTORS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Scraper settings
SCRAPER_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Processor settings
PROCESSOR_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "min_chunk_size": 50,
    "chunks_dir": str(CHUNKS_DIR)
}

# Vectorizer settings
VECTORIZER_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",
    "device": "cpu"
}

# Storage settings
STORAGE_CONFIG = {
    "index_path": str(VECTORS_DIR / "faiss_index"),
    "metadata_path": str(VECTORS_DIR / "metadata.json")
}
