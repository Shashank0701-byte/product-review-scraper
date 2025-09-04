#!/usr/bin/env python3
"""
Example usage of the Product Review Scraper
This script demonstrates how to use the scraper with different configurations.
"""

import subprocess
import time
import os
from datetime import datetime


def run_example_scraping():
    """Run example scraping sessions with different configurations."""
    
    print("🔍 Product Review Scraper - Example Usage")
    print("=" * 60)
    
    # Example URLs for different sites
    examples = [
        {
            "name": "Amazon Product (Small dataset)",
            "url": "https://www.amazon.com/dp/B08N5WRWNW",
            "max_reviews": 50,
            "format": "json"
        },
        {
            "name": "eBay Product (CSV output)",
            "url": "https://www.ebay.com/itm/123456789",  # Replace with real URL
            "max_reviews": 30,
            "format": "csv"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📋 Example {i}: {example['name']}")
        print(f"URL: {example['url']}")
        print(f"Max Reviews: {example['max_reviews']}")
        print(f"Format: {example['format']}")
        
        # Validate URL first
        print("\n🔍 Validating URL...")
        validate_cmd = [
            "python", "run_scraper.py",
            "--validate-only",
            "--url", example['url']
        ]
        
        try:
            result = subprocess.run(validate_cmd, capture_output=True, text=True, check=True)
            print("✅ URL validation successful")
        except subprocess.CalledProcessError as e:
            print(f"❌ URL validation failed: {e.stderr}")
            continue
        
        # Ask user if they want to run this example
        user_input = input(f"\n🤔 Run Example {i}? (y/n/skip all): ").lower().strip()
        
        if user_input == 'skip all':
            break
        elif user_input != 'y':
            print("⏭️ Skipping this example")
            continue
        
        # Run the scraper
        print(f"\n🚀 Running scraper for Example {i}...")
        scrape_cmd = [
            "python", "run_scraper.py",
            "--url", example['url'],
            "--max-reviews", str(example['max_reviews']),
            "--format", example['format']
        ]
        
        start_time = time.time()
        try:
            result = subprocess.run(scrape_cmd, check=True)
            duration = time.time() - start_time
            print(f"✅ Example {i} completed in {duration:.1f} seconds")
        except subprocess.CalledProcessError as e:
            print(f"❌ Example {i} failed: {e}")
        
        print("-" * 60)
    
    print("\n🎉 Example session completed!")
    print("📁 Check the 'scraped_data' folder for results")


def show_help():
    """Show help information about the scraper."""
    print("\n📚 Product Review Scraper Help")
    print("=" * 60)
    
    print("\n🔧 Basic Usage:")
    print("python run_scraper.py --url 'PRODUCT_URL'")
    
    print("\n🔧 Advanced Usage:")
    print("python run_scraper.py --url 'PRODUCT_URL' --max-reviews 500 --format csv")
    
    print("\n🌐 Supported Sites:")
    sites = [
        "Amazon (amazon.com, amazon.co.uk, etc.)",
        "eBay (ebay.com, ebay.co.uk, etc.)",
        "Walmart (walmart.com)",
        "Target (target.com)",
        "Best Buy (bestbuy.com)",
        "Alibaba/AliExpress",
        "Generic e-commerce sites"
    ]
    
    for site in sites:
        print(f"  ✅ {site}")
    
    print("\n📄 Output Data:")
    fields = [
        "Product name and URL",
        "Review text and title",
        "Rating (numerical)",
        "Review date",
        "Reviewer name",
        "Helpful votes count",
        "Verified purchase status",
        "Scraping metadata"
    ]
    
    for field in fields:
        print(f"  📊 {field}")
    
    print("\n⚙️ Configuration Options:")
    options = [
        "--max-reviews: Number of reviews to scrape (default: 200)",
        "--format: Output format - json, csv, or xml (default: json)",
        "--validate-only: Just validate URL without scraping"
    ]
    
    for option in options:
        print(f"  🔧 {option}")


def main():
    """Main function."""
    print("🕷️ Product Review Scraper")
    print("A powerful tool for extracting product reviews from e-commerce sites")
    print("=" * 70)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Run example scraping sessions")
        print("2. Show help and usage information")
        print("3. Custom scraping (enter your own URL)")
        print("4. Exit")
        
        choice = input("\n👉 Enter your choice (1-4): ").strip()
        
        if choice == '1':
            run_example_scraping()
        elif choice == '2':
            show_help()
        elif choice == '3':
            url = input("\n🔗 Enter product URL: ").strip()
            if url:
                max_reviews = input("📄 Max reviews (default 200): ").strip() or "200"
                format_choice = input("📋 Format (json/csv/xml, default json): ").strip() or "json"
                
                cmd = [
                    "python", "run_scraper.py",
                    "--url", url,
                    "--max-reviews", max_reviews,
                    "--format", format_choice
                ]
                
                try:
                    subprocess.run(cmd, check=True)
                    print("✅ Scraping completed!")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Scraping failed: {e}")
            else:
                print("❌ No URL provided")
        elif choice == '4':
            print("\n👋 Thanks for using Product Review Scraper!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()