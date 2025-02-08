from .scraper.web_scraper import WebScraper
from .processor.text_processor import TextProcessor
from .vectorizer.embedder import TextEmbedder
from .storage.vector_store import VectorStore
from typing import List
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        logger.info("Initializing document processor...")
        self.scraper = WebScraper()
        self.processor = TextProcessor()
        self.embedder = TextEmbedder()
        self.vector_store = VectorStore()
        logger.info("Document processor initialized")

    def process_url(self, url: str):
        """Process a single URL through the entire pipeline."""
        try:
            logger.info(f"Starting processing pipeline for URL: {url}")

            # Step 1: Scrape the webpage
            logger.info("Step 1/4: Scraping webpage...")
            raw_file_path = self.scraper.scrape(url)

            # Step 2: Process text into chunks
            logger.info("Step 2/4: Processing text into chunks...")
            chunks = self.processor.process_file(raw_file_path)

            # Step 3: Generate embeddings
            logger.info("Step 3/4: Generating embeddings...")
            embeddings, metadata = self.embedder.process_chunks(chunks)

            # Step 4: Store vectors
            logger.info("Step 4/4: Storing vectors...")
            self.vector_store.add_vectors(embeddings, metadata)
            self.vector_store.save()

            logger.info("Pipeline completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing URL {
                         url}: {str(e)}", exc_info=True)
            return False

    def process_urls(self, urls: List[str]):
        """Process multiple URLs."""
        results = []
        logger.info(f"Processing {len(urls)} URLs...")

        for url in tqdm(urls, desc="Processing URLs"):
            success = self.process_url(url)
            results.append({"url": url, "success": success})

        successful = sum(1 for r in results if r["success"])
        logger.info(f"Processed {len(urls)} URLs. Success: {
                    successful}, Failed: {len(urls) - successful}")
        return results

    def search_similar(self, query_text: str, k: int = 5):
        """Search for similar content using a text query."""
        logger.info(f"Searching for: {query_text}")

        # Generate embedding for the query
        query_vector = self.embedder.embed_text(query_text)

        # Search in the vector store
        results = self.vector_store.search(query_vector, k=k)
        logger.info(f"Found {len(results)} results")
        return results


def main():
    try:
        # Example usage
        processor = DocumentProcessor()

        # Example URLs to process
        urls = [
            "https://developers.google.com/google-ads/api/docs/sunset-dates"
        ]

        # Process URLs
        results = processor.process_urls(urls)

        # Print results
        print("\nProcessing Results:")
        for result in results:
            status = "✓ Success" if result["success"] else "✗ Failed"
            print(f"{status} - {result['url']}")

        # Example search
        print("\nPerforming search...")
        query = "What is the sunset date for the Google Ads API v17.1?"
        similar_results = processor.search_similar(query)

        print("\nSearch Results:")
        for i, result in enumerate(similar_results, 1):
            print(f"\nResult {i}:")
            print(f"URL: {result['metadata']['source_url']}")
            print(f"Distance: {result['distance']:.4f}")
            print("---")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error("An error occurred:", exc_info=True)


if __name__ == "__main__":
    main()
