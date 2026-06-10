from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin


@dataclass(frozen=True)
class Product:
    title: str
    price: Decimal
    rating: str
    availability: str
    product_url: str
    source_url: str

    def to_dict(self) -> dict[str, str]:
        row = asdict(self)
        row["price"] = f"{self.price:.2f}"
        return row


def parse_products(html: str, source_url: str) -> list[Product]:
    parser = ProductHTMLParser(source_url)
    parser.feed(html)
    return parser.products


def parse_next_page(html: str, source_url: str) -> str | None:
    parser = ProductHTMLParser(source_url)
    parser.feed(html)
    return parser.next_page_url


def products_to_rows(products: Iterable[Product]) -> list[dict[str, str]]:
    return [product.to_dict() for product in products]


def _parse_price(value: str) -> Decimal:
    normalized = value.replace("£", "").replace("$", "").replace(",", "").strip()
    return Decimal(normalized)


class ProductHTMLParser(HTMLParser):
    def __init__(self, source_url: str):
        super().__init__()
        self.source_url = source_url
        self.products: list[Product] = []
        self.next_page_url: str | None = None
        self._current: dict[str, str] | None = None
        self._capture_price = False
        self._capture_availability = False
        self._in_next_item = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        classes = set(attributes.get("class", "").split())

        if tag == "article" and "product_pod" in classes:
            self._current = {
                "title": "",
                "price": "",
                "rating": "Unknown",
                "availability": "",
                "product_url": "",
            }
            return

        if self._current is not None and tag == "p" and "star-rating" in classes:
            self._current["rating"] = next((item for item in classes if item != "star-rating"), "Unknown")
            return

        if self._current is not None and tag == "a" and attributes.get("title"):
            self._current["title"] = attributes["title"].strip()
            self._current["product_url"] = urljoin(self.source_url, attributes.get("href", ""))
            return

        if self._current is not None and tag == "p" and "price_color" in classes:
            self._capture_price = True
            return

        if self._current is not None and tag == "p" and "availability" in classes:
            self._capture_availability = True
            return

        if tag == "li" and "next" in classes:
            self._in_next_item = True
            return

        if self._in_next_item and tag == "a" and attributes.get("href"):
            self.next_page_url = urljoin(self.source_url, attributes["href"])

    def handle_data(self, data: str) -> None:
        if self._current is None:
            return

        text = data.strip()
        if not text:
            return

        if self._capture_price:
            self._current["price"] += text
        elif self._capture_availability:
            self._current["availability"] += f" {text}" if self._current["availability"] else text

    def handle_endtag(self, tag: str) -> None:
        if tag == "p":
            self._capture_price = False
            self._capture_availability = False

        if tag == "article" and self._current is not None:
            if self._current["title"] and self._current["price"]:
                self.products.append(
                    Product(
                        title=self._current["title"],
                        price=_parse_price(self._current["price"]),
                        rating=self._current["rating"],
                        availability=self._current["availability"] or "Unknown",
                        product_url=self._current["product_url"],
                        source_url=self.source_url,
                    )
                )
            self._current = None

        if tag == "li":
            self._in_next_item = False
