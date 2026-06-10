import unittest
from decimal import Decimal
from pathlib import Path

from ecommerce_scraper.parser import parse_next_page, parse_products, products_to_rows


FIXTURE = Path(__file__).parent / "fixtures" / "books_page.html"
SOURCE_URL = "https://books.toscrape.com/index.html"


class ParserTests(unittest.TestCase):
    def test_parse_products_extracts_clean_product_rows(self):
        html = FIXTURE.read_text(encoding="utf-8")

        products = parse_products(html, SOURCE_URL)

        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].title, "A Light in the Attic")
        self.assertEqual(products[0].price, Decimal("51.77"))
        self.assertEqual(products[0].rating, "Three")
        self.assertEqual(products[0].availability, "In stock")
        self.assertEqual(
            products[0].product_url,
            "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        )

    def test_products_to_rows_formats_price_for_csv_and_json(self):
        html = FIXTURE.read_text(encoding="utf-8")
        products = parse_products(html, SOURCE_URL)

        rows = products_to_rows(products)

        self.assertEqual(rows[0]["price"], "51.77")
        self.assertEqual(rows[0]["source_url"], SOURCE_URL)

    def test_parse_next_page_returns_absolute_url(self):
        html = FIXTURE.read_text(encoding="utf-8")

        next_page = parse_next_page(html, SOURCE_URL)

        self.assertEqual(next_page, "https://books.toscrape.com/catalogue/page-2.html")


if __name__ == "__main__":
    unittest.main()
