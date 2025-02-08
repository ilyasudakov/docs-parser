# Web Page Parser and Vector Storage

A Python-based tool for scraping web pages, extracting content, and storing it in vector format for efficient similarity search and retrieval.

## Features

- Web page scraping with robust error handling
- Text extraction and preprocessing
- Vector embedding generation
- Efficient vector storage and retrieval
- Configurable processing pipeline
- Cursor IDE integration with code formatting and linting
- AI-assisted development with custom Cursor rules

## Project Structure

```
docs_parser/
├── src/
│   ├── scraper/         # Web scraping logic
│   ├── processor/       # Text processing
│   ├── vectorizer/      # Vector embedding
│   └── storage/         # Vector storage
├── config/             # Configuration files
├── data/               # Storage for scraped data
│   ├── raw/            # Raw HTML/text
│   └── processed/      # Processed vectors
├── tests/             # Test cases
├── .cursorignore      # Cursor ignore patterns
├── .cursor.json       # Cursor IDE configuration
├── .cursorrules       # Cursor AI rules
└── requirements.txt   # Dependencies
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install development dependencies:
   ```bash
   pip install black flake8 pylint mypy
   ```

## Development

This project is configured for development with Cursor IDE, providing:

- Automatic code formatting with Black
- Type checking with mypy
- Linting with pylint and flake8
- Code completion and IntelliSense
- Integrated search excluding build artifacts
- Consistent code style enforcement
- AI-assisted development with custom rules

### Cursor Configuration

The project includes three Cursor-specific configuration files:

- `.cursor.json`: IDE settings, formatting rules, and Python tooling configuration
- `.cursorignore`: Patterns for files to exclude from indexing
- `.cursorrules`: AI-assisted development rules and patterns

#### Cursor Rules

The `.cursorrules` file defines patterns and rules for AI-assisted development:

- **Code Generation**: Templates for new files and documentation
- **Code Analysis**: Patterns for security, performance, and style checks
- **Completion**: Custom code snippets and autocompletion patterns
- **Context**: Project-specific terminology and file organization
- **Types**: Custom type aliases and type checking rules
- **Testing**: Required test categories and coverage thresholds

### Code Style

The project enforces:

- Line length: 100 characters
- Indentation: 4 spaces
- Black code formatting
- Type hints for function parameters and returns
- Docstrings for all public functions and classes
- Google-style docstring format

### Testing Requirements

The project requires:

- Unit tests with 80% coverage
- Integration tests with 70% coverage
- Test cases for:
  - Happy path scenarios
  - Error handling
  - Edge cases

## Usage

[Documentation will be added as the project develops]

## Dependencies

- Python 3.8+
- See requirements.txt for full list

## License

MIT License
