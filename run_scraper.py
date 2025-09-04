#!/usr/bin/env python3
"""
Product Review Scraper Runner
A utility script to easily run the review scraper with different configurations.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from urllib.parse import urlparse


def validate_url(url):
    """Validate if the provided URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def detect_site(url):
    """Detect which e-commerce site the URL belongs to."""
    url_lower = url.lower()
    
    if 'amazon.' in url_lower:
        return 'Amazon'
    elif 'ebay.' in url_lower:
        return 'eBay'
    elif 'alibaba.' in url_lower or 'aliexpress.' in url_lower:
        return 'Alibaba/AliExpress'
    elif 'walmart.' in url_lower:
        return 'Walmart'
    elif 'target.' in url_lower:
        return 'Target'
    elif 'bestbuy.' in url_lower:
        return 'Best Buy'
    else:
        return 'Generic/Unknown'


def run_scraper(url, max_reviews=200, output_format='json'):
    """Run the Scrapy spider with the given parameters."""
    
    # Validate URL
    if not validate_url(url):
        print(f"❌ Error: Invalid URL provided: {url}")
        return False
    
    # Detect site
    site = detect_site(url)
    print(f"🔍 Detected site: {site}")
    print(f"📄 Target reviews: {max_reviews}")
    print(f"🔗 Product URL: {url}")
    print("-" * 60)
    
    # Prepare scrapy command
    cmd = [
        'scrapy', 'crawl', 'reviews',
        '-a', f'url={url}',
        '-a', f'max_reviews={max_reviews}'
    ]
    
    # Add output format if specified
    if output_format and output_format != 'json':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"scraped_data/reviews_{timestamp}.{output_format}"
        cmd.extend(['-o', output_file])
    
    # Run the command
    try:
        print("🚀 Starting scraper...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Scraping completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running scraper: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Error: Scrapy not found. Please install it with: pip install scrapy")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Product Review Scraper - Extract reviews from e-commerce sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py --url "https://www.amazon.com/dp/B08N5WRWNW"
  python run_scraper.py --url "https://www.amazon.com/dp/B08N5WRWNW" --max-reviews 500
  python run_scraper.py --url "https://ebay.com/itm/123456789" --format csv

Supported Sites:
  - Amazon (amazon.com, amazon.co.uk, etc.)
  - eBay (ebay.com, ebay.co.uk, etc.)
  - Walmart (walmart.com)
  - Target (target.com)
  - Best Buy (bestbuy.com)
  - Alibaba/AliExpress
  - Generic sites (uses common selectors)
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        required=True,
        help='Product URL to scrape reviews from'
    )
    
    parser.add_argument(
        '--max-reviews', '-m',
        type=int,
        default=200,
        help='Maximum number of reviews to scrape (default: 200)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'xml'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='Only validate the URL without running the scraper'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not validate_url(args.url):
        print(f"❌ Error: Invalid URL provided: {args.url}")
        sys.exit(1)
    
    site = detect_site(args.url)
    print(f"🔍 URL validation: ✅ Valid")
    print(f"🔍 Detected site: {site}")
    
    if args.validate_only:
        print("✅ URL is valid and ready for scraping")
        return
    
    # Run the scraper
    success = run_scraper(
        url=args.url,
        max_reviews=args.max_reviews,
        output_format=args.format
    )
    
    if success:
        print("\n🎉 Scraping session completed!")
        print("📁 Check the 'scraped_data' folder for results")
    else:
        print("\n❌ Scraping failed. Check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()