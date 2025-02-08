from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np
from datetime import datetime
from pathlib import Path
from src.vectorizer.embedder import TextEmbedder
from src.storage.vector_store import VectorStore


@dataclass
class APISource:
    """Represents an API data source with its current version."""
    name: str
    current_version: str
    description: str = ""


class APIVersionSearch:
    """Handles searching for API version related information across multiple sources."""

    def __init__(self):
        self.embedder = TextEmbedder()
        self.store = VectorStore()
        self.api_sources = [
            APISource(
                name="Google Ads",
                current_version="v17.1",
                description="Google Ads API"
            ),
            APISource(
                name="Facebook Ads",
                current_version="v18.0",
                description="Facebook Marketing API"
            )
        ]

        # Load the vector store
        self.store.load()

    def search_across_sources(self, k_per_source: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for information about each API source's current version.

        Args:
            k_per_source: Number of results to return per API source

        Returns:
            Dict mapping API source names to their search results
        """
        results = {}

        for source in self.api_sources:
            # Construct version-specific query with API name for better context
            query = f"What is the sunset date for the {
                source.name} API {source.current_version}?"
            query_vector = self.embedder.embed_text(query)

            # Search for similar content
            source_results = self.store.search(
                query_vector, k=k_per_source * 2)  # Get more results initially

            # Filter results to only include those matching the current API's URL pattern
            filtered_results = []
            url_patterns = {
                "Google Ads": "google-ads",
                "Facebook Ads": "facebook.com"
            }

            pattern = url_patterns.get(source.name)
            if pattern:
                for result in source_results:
                    source_url = result['metadata'].get('source_url', '')
                    if pattern in source_url.lower():
                        filtered_results.append(result)
                        if len(filtered_results) >= k_per_source:
                            break

            # Limit to requested number
            results[source.name] = filtered_results[:k_per_source]

        return results

    def save_best_results(self, results: Dict[str, List[Dict[str, Any]]], output_dir: str = "results"):
        """
        Save the best result for each API source to a text file.

        Args:
            results: Search results from search_across_sources
            output_dir: Directory to save results in
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"api_sunset_dates_{timestamp}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            for source in self.api_sources:
                source_results = results.get(source.name, [])
                f.write(f"\n{'='*50}\n")
                f.write(f"API Source: {source.name}\n")
                f.write(f"Current Version: {source.current_version}\n")
                f.write(f"{'='*50}\n\n")

                if source_results:
                    # Get the first (best) result
                    best_result = source_results[0]
                    f.write("Best Match:\n")
                    f.write(f"Text: {best_result['text']}\n")
                    f.write(f"Source URL: {best_result['metadata'].get(
                        'source_url', 'No source found')}\n")
                    # Convert distance to similarity
                    f.write(f"Similarity Score: {
                            1 - best_result['distance']:.4f}\n")
                else:
                    f.write("No results found.\n")

                f.write("\n")

        return output_file

    def format_results(self, results: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format the search results into a readable string.

        Args:
            results: Search results from search_across_sources

        Returns:
            Formatted string with search results
        """
        output = []

        for source in self.api_sources:
            source_results = results.get(source.name, [])

            output.append(f"\n=== {source.name} API ({
                          source.current_version}) ===")

            if not source_results:
                output.append("No results found.")
                continue

            for i, result in enumerate(source_results, 1):
                output.append(f"\nResult {i}:")
                output.append(f"Text: {result.get('text', 'No text found')}")
                output.append(f"Source URL: {result['metadata'].get(
                    'source_url', 'No source found')}")
                output.append(f"Distance: {result['distance']}")
                output.append("---")

        return "\n".join(output)
