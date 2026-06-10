from __future__ import annotations

import time
from collections.abc import Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ecommerce_scraper.parser import Product, parse_next_page, parse_products


DEFAULT_START_URL = "https://books.toscrape.com/"


class ScraperError(RuntimeError):
    """Raised when a page cannot be fetched."""


def scrape_products(start_url: str = DEFAULT_START_URL, max_pages: int = 1, delay: float = 1.0) -> list[Product]:
    products: list[Product] = []

    for page_html, page_url in iter_pages(start_url=start_url, max_pages=max_pages, delay=delay):
        products.extend(parse_products(page_html, page_url))

    return products


def iter_pages(start_url: str, max_pages: int, delay: float) -> Iterator[tuple[str, str]]:
    current_url: str | None = start_url
    pages_seen = 0

    while current_url and pages_seen < max_pages:
        html = fetch_page(current_url)
        yield html, current_url

        pages_seen += 1
        current_url = parse_next_page(html, current_url)

        if current_url and pages_seen < max_pages and delay > 0:
            time.sleep(delay)


def fetch_page(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "PortfolioProductScraper/1.0 (+https://github.com/your-username/ecommerce-product-scraper)"
        },
    )

    try:
        with urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as error:
        raise ScraperError(f"Request failed for {url}: HTTP {error.code}") from error
    except URLError as error:
        raise ScraperError(f"Request failed for {url}: {error.reason}") from error
