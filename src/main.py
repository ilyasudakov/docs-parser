from scraper.web_scraper import WebScraper
from processor.text_processor import TextProcessor
from vectorizer.embedder import TextEmbedder
from storage.vector_store import VectorStore
from typing import List
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.scraper = WebScraper()
        self.processor = TextProcessor()
        self.embedder = TextEmbedder()
        self.vector_store = VectorStore()

    def process_url(self, url: str):
        """Process a single URL through the entire pipeline."""
        try:
            # Step 1: Scrape the webpage
            logger.info(f"Scraping URL: {url}")
            raw_file_path = self.scraper.scrape(url)

            # Step 2: Process text into chunks
            logger.info("Processing text into chunks")
            chunks = self.processor.process_file(raw_file_path)

            # Step 3: Generate embeddings
            logger.info("Generating embeddings")
            embeddings, metadata = self.embedder.process_chunks(chunks)

            # Step 4: Store vectors
            logger.info("Storing vectors")
            self.vector_store.add_vectors(embeddings, metadata)
            self.vector_store.save()

            logger.info("Processing completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return False

    def process_urls(self, urls: List[str]):
        """Process multiple URLs."""
        results = []
        for url in urls:
            success = self.process_url(url)
            results.append({"url": url, "success": success})
        return results

    def search_similar(self, query_text: str, k: int = 5):
        """Search for similar content using a text query."""
        # Generate embedding for the query
        query_vector = self.embedder.embed_text(query_text)

        # Search in the vector store
        results = self.vector_store.search(query_vector, k=k)
        return results


def main():
    # Example usage
    processor = DocumentProcessor()

    # Example URLs to process
    urls = [
        "https://developers.google.com/google-ads/api/docs/sunset-dates"
    ]

    # Process URLs
    results = processor.process_urls(urls)

    # Print results
    for result in results:
        status = "Success" if result["success"] else "Failed"
        print(f"Processing {result['url']}: {status}")

    # Example search
    query = "What is the sunset date for the Google Ads API v17.1?"
    similar_results = processor.search_similar(query)

    print("\nSearch Results:")
    for result in similar_results:
        print(f"URL: {result['metadata']['source_url']}")
        print(f"Distance: {result['distance']}")
        print("---")


if __name__ == "__main__":
    main()
