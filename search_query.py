from src.vectorizer.embedder import TextEmbedder
from src.storage.vector_store import VectorStore

# Initialize components
embedder = TextEmbedder()
store = VectorStore()

# Load existing vectors
store.load()

# Convert question to vector
query = 'What is the sunset date for the Google Ads API v17.1?'
query_vector = embedder.embed_text(query)

# Search for similar content
results = store.search(query_vector, k=5)

# Display results
for i, result in enumerate(results, 1):
    print(f'\nResult {i}:')
    print('Text:', result['metadata'].get('text', 'No text found'))
    print('Source URL:', result['metadata'].get(
        'source_url', 'No source found'))
    print('Distance:', result['distance'])
    print('---')
