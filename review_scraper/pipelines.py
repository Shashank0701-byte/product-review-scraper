# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from datetime import datetime
from itemadapter import ItemAdapter


class ReviewScraperPipeline:
    """Pipeline for processing and saving scraped review items."""
    
    def __init__(self):
        self.items = []
        self.output_dir = "scraped_data"
        
    def open_spider(self, spider):
        """Initialize the pipeline when spider opens."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        spider.logger.info(f"Pipeline initialized. Output directory: {self.output_dir}")
        
    def process_item(self, item, spider):
        """Process each scraped item."""
        adapter = ItemAdapter(item)
        
        # Add timestamp when item was scraped
        adapter['scraped_at'] = datetime.now().isoformat()
        
        # Clean and validate data
        self._clean_item(adapter)
        
        # Add to items list
        self.items.append(dict(adapter))
        
        spider.logger.info(f"Processed review from {adapter.get('reviewer_name', 'Unknown')}")
        return item
    
    def close_spider(self, spider):
        """Save all items to JSON file when spider closes."""
        if self.items:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/reviews_{timestamp}.json"
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            
            spider.logger.info(f"Saved {len(self.items)} reviews to {filename}")
            
            # Also save summary
            self._save_summary(spider, filename)
        else:
            spider.logger.warning("No items were scraped!")
    
    def _clean_item(self, adapter):
        """Clean and normalize item data."""
        # Clean text fields
        text_fields = ['product_name', 'review_text', 'reviewer_name', 'review_title']
        for field in text_fields:
            if adapter.get(field):
                # Remove extra whitespace and newlines
                adapter[field] = ' '.join(adapter[field].strip().split())
        
        # Clean rating - ensure it's a number
        if adapter.get('rating'):
            try:
                # Extract number from rating text
                rating_text = str(adapter['rating'])
                rating_num = float(''.join(c for c in rating_text if c.isdigit() or c == '.'))
                adapter['rating'] = rating_num
            except (ValueError, TypeError):
                adapter['rating'] = None
        
        # Clean helpful votes
        if adapter.get('helpful_votes'):
            try:
                votes_text = str(adapter['helpful_votes'])
                votes_num = int(''.join(c for c in votes_text if c.isdigit()))
                adapter['helpful_votes'] = votes_num
            except (ValueError, TypeError):
                adapter['helpful_votes'] = 0
    
    def _save_summary(self, spider, filename):
        """Save a summary of the scraping session."""
        summary = {
            "scraping_session": {
                "total_reviews": len(self.items),
                "start_url": getattr(spider, 'start_urls', ['Unknown'])[0],
                "spider_name": spider.name,
                "timestamp": datetime.now().isoformat(),
                "output_file": filename
            },
            "statistics": {
                "average_rating": self._calculate_average_rating(),
                "rating_distribution": self._get_rating_distribution(),
                "total_pages_scraped": len(set(item.get('page_number', 1) for item in self.items))
            }
        }
        
        summary_filename = filename.replace('.json', '_summary.json')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        spider.logger.info(f"Summary saved to {summary_filename}")
    
    def _calculate_average_rating(self):
        """Calculate average rating from all reviews."""
        ratings = [item.get('rating') for item in self.items if item.get('rating')]
        if ratings:
            return round(sum(ratings) / len(ratings), 2)
        return None
    
    def _get_rating_distribution(self):
        """Get distribution of ratings."""
        distribution = {}
        for item in self.items:
            rating = item.get('rating')
            if rating:
                rating = int(rating)
                distribution[rating] = distribution.get(rating, 0) + 1
        return distribution