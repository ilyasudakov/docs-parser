import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import validators
from pathlib import Path
import json
import hashlib
from datetime import datetime
import logging
from ..config.config import SCRAPER_CONFIG, RAW_DIR


class WebScraper:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or SCRAPER_CONFIG
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.config["user_agent"]})

    def validate_url(self, url: str) -> bool:
        """Validate if the given URL is properly formatted."""
        return validators.url(url) is True

    def generate_filename(self, url: str) -> str:
        """Generate a unique filename for the URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.json"

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch the web page content with retry mechanism."""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        headers = self.session.headers.copy()

        # Add special handling for Facebook URLs
        if "facebook.com" in url or "developers.facebook.com" in url:
            headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            })

        for attempt in range(self.config["max_retries"]):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config["timeout"],
                    headers=headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == self.config["max_retries"] - 1:
                    logging.error(f"Failed to fetch {url}: {str(e)}")
                    raise
                continue

    def extract_text(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        # Get text and clean it
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)

    def save_content(self, url: str, content: str) -> Path:
        """Save the scraped content with metadata."""
        filename = self.generate_filename(url)
        filepath = RAW_DIR / filename

        data = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def scrape(self, url: str) -> Path:
        """Main method to scrape a URL and save its content."""
        html_content = self.fetch_page(url)
        text_content = self.extract_text(html_content)
        return self.save_content(url, text_content)
