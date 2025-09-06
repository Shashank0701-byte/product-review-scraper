# Incremental Scraping Module

## Overview

The Incremental Scraping module improves efficiency by only fetching new reviews since the last scrape, rather than re-scraping all reviews each time. It tracks the most recent review date/ID and uses that information to only request new content, saving time and resources while keeping your review data up-to-date.

## Features

- **Efficient Updates**: Only scrape new reviews since the last run
- **State Tracking**: Maintains information about previous scrapes
- **Smart Merging**: Combines new reviews with existing data, avoiding duplicates
- **Multiple Site Support**: Works with various e-commerce platforms
- **Command Line Interface**: Easy to use from scripts or command line
- **Conflict Resolution**: Handles duplicate reviews intelligently

## Requirements

```
scrapy>=2.5.0
pandas>=1.3.0
```

## Usage

### Basic Usage

```python
from incremental_scraper import IncrementalScraper

# Initialize the scraper
scraper = IncrementalScraper()

# Run an incremental scrape
success, output_file, stats = scraper.run_incremental_scrape(
    url="https://www.amazon.com/dp/B08L5TNJHG",
    output_file="scraped_data/product_reviews.csv"
)

if success:
    print(f"Scrape completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Stats: {stats}")
else:
    print("Scrape failed.")
```

### Using the Helper Function

```python
from incremental_scraper import run_incremental_scrape

# Run an incremental scrape
success, output_file, stats = run_incremental_scrape(
    url="https://www.amazon.com/dp/B08L5TNJHG",
    output_file="scraped_data/product_reviews.csv",
    scrapy_project_dir="scrapy_project",
    spider_name="amazon"
)
```

## How It Works

1. **State Tracking**: The module maintains a state file (`scraper_state.json`) that records information about the most recent review for each product URL.

2. **URL Identification**: Each URL is converted to a unique key based on the domain and product ID.

3. **Incremental Parameters**: When running a scrape, the module adds parameters like `since_date` or `since_id` to tell the spider to only fetch new reviews.

4. **Smart Merging**: After scraping, new reviews are merged with existing data, with duplicate detection to avoid redundancy.

5. **State Update**: After a successful scrape, the state file is updated with information about the most recent review.

## Command Line Usage

You can run the incremental scraper directly from the command line:

```bash
python incremental_scraper.py "https://www.amazon.com/dp/B08L5TNJHG" --output scraped_data/product_reviews.csv
```

Command line options:

```
positional arguments:
  url                   URL of the product to scrape

optional arguments:
  --output OUTPUT, -o OUTPUT
                        Output file path
  --project-dir PROJECT_DIR, -p PROJECT_DIR
                        Scrapy project directory
  --spider SPIDER, -s SPIDER
                        Spider name
```

## Integration with Scrapy Spiders

To fully utilize incremental scraping, your Scrapy spiders should support the following parameters:

- `since_date`: Only fetch reviews posted after this date (format: YYYY-MM-DD)
- `since_id`: Only fetch reviews with an ID that comes after this one

Example spider implementation:

```python
class ProductReviewSpider(scrapy.Spider):
    name = "product_reviews"
    
    def __init__(self, url=None, output=None, since_date=None, since_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.output = output
        self.since_date = since_date
        self.since_id = since_id
    
    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)
    
    def parse(self, response):
        # Use self.since_date and self.since_id to filter reviews
        # ...
```

## Advanced Usage

### Custom State File Location

```python
# Specify a custom state file location
scraper = IncrementalScraper(data_dir="custom_data", state_file="custom_state.json")
```

### Manual State Management

```python
# Get information about the last scrape
last_scrape = scraper.get_last_scrape_info(url)
print(f"Last scrape: {last_scrape}")

# Manually update scrape information
scraper.update_scrape_info(url, {
    "latest_date": "2023-05-15T10:30:00",
    "review_id": "ABC123",
    "total_reviews": 150
})
```

### Manual Review Merging

```python
# Merge reviews from two files
success, merged_file, stats = scraper.merge_new_reviews(
    existing_file="old_reviews.csv",
    new_file="new_reviews.csv",
    output_file="merged_reviews.csv"
)
```

## Troubleshooting

- **Spider doesn't respect incremental parameters**: Ensure your Scrapy spider properly handles the `since_date` and `since_id` parameters
- **Duplicate reviews**: Check if your review data has reliable unique identifiers
- **State file issues**: If the state file becomes corrupted, delete it to start fresh
- **Merging problems**: Ensure your CSV files have consistent column structures

## Limitations

- The effectiveness of incremental scraping depends on the e-commerce site's structure and how it presents review data
- Some sites may not provide a reliable way to fetch only new reviews
- Date-based incremental scraping may miss reviews if they're not strictly ordered by date

## Example

For a complete example, see the code at the bottom of `incremental_scraper.py`.