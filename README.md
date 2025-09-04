# Product Review Scraper

A powerful Scrapy-based web scraper that extracts product reviews from various e-commerce websites. The spider can automatically detect the website type and extract review data including product name, review text, ratings, dates, and reviewer information.

## Features

🔍 **Multi-Site Support**: Works with Amazon, eBay, Walmart, Target, Best Buy, Alibaba/AliExpress, and generic e-commerce sites  
📄 **Comprehensive Data**: Extracts product name, review text, rating, review date, reviewer name, and additional metadata  
🔄 **Automatic Pagination**: Follows pagination links to scrape the specified number of reviews  
💾 **Multiple Formats**: Save results in JSON, CSV, or XML format  
⚙️ **Configurable**: Set maximum number of reviews to scrape  
🛡️ **Respectful Scraping**: Built-in delays and throttling to avoid overwhelming servers  

## Installation

1. **Clone or download this project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Method 1: Using the Runner Script (Recommended)

```bash
# Basic usage - scrape 200 reviews (default)
python run_scraper.py --url "https://www.amazon.com/dp/PRODUCT_ID"

# Scrape more reviews
python run_scraper.py --url "https://www.amazon.com/dp/PRODUCT_ID" --max-reviews 500

# Save in CSV format
python run_scraper.py --url "https://www.amazon.com/dp/PRODUCT_ID" --format csv

# Validate URL without scraping
python run_scraper.py --url "https://www.amazon.com/dp/PRODUCT_ID" --validate-only
```

### Method 2: Using Scrapy Directly

```bash
# Navigate to project directory
cd "Product Review Scraper"

# Run the spider
scrapy crawl reviews -a url="PRODUCT_URL" -a max_reviews=200

# Save to specific format
scrapy crawl reviews -a url="PRODUCT_URL" -o reviews.csv
```

## Supported Websites

| Website | Support Level | Notes |
|---------|---------------|-------|
| Amazon | ✅ Full | All Amazon domains (amazon.com, amazon.co.uk, etc.) |
| eBay | ✅ Full | All eBay domains |
| Walmart | ✅ Full | walmart.com |
| Target | ✅ Good | target.com |
| Best Buy | ✅ Good | bestbuy.com |
| Alibaba/AliExpress | ✅ Good | alibaba.com, aliexpress.com |
| Generic Sites | ⚠️ Basic | Uses common CSS selectors |

## Output Data Structure

The scraper extracts the following fields for each review:

```json
{
  "product_name": "Product Name",
  "product_url": "https://example.com/product",
  "review_text": "This is a great product...",
  "rating": 5.0,
  "review_date": "January 15, 2024",
  "reviewer_name": "John Doe",
  "review_id": "unique_review_id",
  "helpful_votes": 10,
  "verified_purchase": true,
  "review_title": "Great product!",
  "scraped_at": "2024-01-15T14:30:00",
  "page_number": 1
}
```

## Output Files

Results are saved in the `scraped_data/` directory:

- **reviews_TIMESTAMP.json**: Main review data
- **reviews_TIMESTAMP_summary.json**: Scraping statistics and summary

## Configuration

### Spider Settings

You can modify settings in `review_scraper/settings.py`:

- **DOWNLOAD_DELAY**: Delay between requests (default: 1 second)
- **AUTOTHROTTLE_ENABLED**: Automatic throttling (default: True)
- **ROBOTSTXT_OBEY**: Respect robots.txt (default: False)

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | Product URL to scrape | Required |
| `--max-reviews` | Maximum reviews to scrape | 200 |
| `--format` | Output format (json/csv/xml) | json |
| `--validate-only` | Only validate URL | False |

## Examples

### Amazon Product
```bash
python run_scraper.py --url "https://www.amazon.com/dp/B08N5WRWNW" --max-reviews 300
```

### eBay Listing
```bash
python run_scraper.py --url "https://www.ebay.com/itm/123456789" --format csv
```

### Walmart Product
```bash
python run_scraper.py --url "https://www.walmart.com/ip/product-id" --max-reviews 150
```

## Project Structure

```
Product Review Scraper/
├── review_scraper/
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── product_reviews.py    # Main spider
│   ├── __init__.py
│   ├── items.py                  # Data structure definitions
│   ├── pipelines.py              # Data processing pipeline
│   └── settings.py               # Scrapy settings
├── scraped_data/                 # Output directory
├── run_scraper.py                # Utility runner script
├── requirements.txt              # Dependencies
├── scrapy.cfg                    # Scrapy configuration
└── README.md                     # This file
```

## Advanced Usage

### Custom Selectors

For unsupported sites, the spider uses generic selectors. You can extend the spider by adding site-specific selectors in `product_reviews.py`.

### Batch Processing

To scrape multiple products, create a script that calls the runner:

```python
urls = [
    "https://www.amazon.com/dp/PRODUCT1",
    "https://www.amazon.com/dp/PRODUCT2",
    # ... more URLs
]

for url in urls:
    subprocess.run(["python", "run_scraper.py", "--url", url])
```

## Troubleshooting

### Common Issues

1. **No reviews found**: 
   - Check if the URL is correct
   - Some sites may have changed their HTML structure
   - Try with a different product that has reviews

2. **Scraping blocked**:
   - Increase DOWNLOAD_DELAY in settings.py
   - Use rotating proxies (advanced)
   - Check if site requires login

3. **Import errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Run from the correct directory

### Debug Mode

Run with verbose logging:
```bash
scrapy crawl reviews -a url="PRODUCT_URL" -L DEBUG
```

## Legal and Ethical Considerations

⚠️ **Important**: Always ensure you comply with:
- Website Terms of Service
- Local laws and regulations
- Respectful scraping practices (delays, robots.txt)
- Data privacy requirements

This tool is for educational and research purposes. Users are responsible for ensuring their usage complies with applicable laws and website terms.

## Contributing

Feel free to contribute by:
- Adding support for new e-commerce sites
- Improving existing selectors
- Adding new features
- Fixing bugs

## License

This project is for educational purposes. Please respect website terms of service and applicable laws when using this tool.