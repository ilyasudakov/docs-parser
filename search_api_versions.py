from src.api_version_search import APIVersionSearch


def main():
    # Initialize the API version search
    api_search = APIVersionSearch()

    # Search across all API sources
    results = api_search.search_across_sources(k_per_source=3)

    # Save best results to file
    output_file = api_search.save_best_results(results)
    print(f"\nResults have been saved to: {output_file}")

    # Format and display all results
    formatted_results = api_search.format_results(results)
    print("\nAll search results:")
    print(formatted_results)


if __name__ == "__main__":
    main()
