from __future__ import annotations

import argparse
from pathlib import Path

from ecommerce_scraper.exporter import export_csv, export_json
from ecommerce_scraper.parser import parse_products, products_to_rows
from ecommerce_scraper.scraper import DEFAULT_START_URL, scrape_products


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape product listings and export clean product data.")
    parser.add_argument("--url", default=DEFAULT_START_URL, help="Starting catalog URL.")
    parser.add_argument("--html-file", help="Parse a local HTML file instead of making a web request.")
    parser.add_argument("--pages", type=int, default=1, help="Maximum number of listing pages to scrape.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between page requests in seconds.")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output file format.")
    parser.add_argument("--output", default="data/products.csv", help="Output file path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.html_file:
        html_path = Path(args.html_file)
        html = html_path.read_text(encoding="utf-8")
        products = parse_products(html, args.url)
    else:
        products = scrape_products(start_url=args.url, max_pages=args.pages, delay=args.delay)

    rows = products_to_rows(products)
    output_path = Path(args.output)

    if args.format == "csv":
        export_csv(rows, output_path)
    else:
        export_json(rows, output_path)

    print(f"Saved {len(rows)} products to {output_path}")


if __name__ == "__main__":
    main()
