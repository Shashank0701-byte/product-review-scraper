# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import re
import csv
from datetime import datetime
from itemadapter import ItemAdapter
from html import unescape
import html.parser
from .text_cleaner import TextCleaner


class ReviewScraperPipeline:
    """Pipeline for processing and saving scraped review items."""
    
    def __init__(self):
        self.items = []
        self.output_dir = "scraped_data"
        self.csv_file = None
        self.csv_writer = None
        
    def open_spider(self, spider):
        """Initialize the pipeline when spider opens."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        spider.logger.info(f"Pipeline initialized. Output directory: {self.output_dir}")
        
        # Setup CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{self.output_dir}/cleaned_reviews_{timestamp}.csv"
        
        self.csv_file = open(csv_filename, 'w', newline='', encoding='utf-8')
        
        # CSV columns as specified
        fieldnames = ['product_name', 'review_text', 'rating', 'review_date', 'reviewer_name']
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()
        
        spider.logger.info(f"CSV file created: {csv_filename}")
        
    def process_item(self, item, spider):
        """Process each scraped item with comprehensive cleaning."""
        adapter = ItemAdapter(item)
        
        # Add timestamp when item was scraped
        adapter['scraped_at'] = datetime.now().isoformat()
        
        # Clean and validate data
        cleaned_item = self._clean_item(adapter)
        
        # Add to items list for JSON output
        self.items.append(dict(adapter))
        
        # Write cleaned data to CSV
        if cleaned_item and self.csv_writer:
            self.csv_writer.writerow(cleaned_item)
            if self.csv_file:
                self.csv_file.flush()  # Ensure data is written immediately
        
        spider.logger.info(f"Processed and cleaned review from {adapter.get('reviewer_name', 'Unknown')}")
        return item
    
    def close_spider(self, spider):
        """Save all items to JSON file and close CSV when spider closes."""
        # Close CSV file
        if self.csv_file:
            self.csv_file.close()
            spider.logger.info(f"CSV file closed with {len(self.items)} cleaned reviews")
        
        if self.items:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{self.output_dir}/reviews_{timestamp}.json"
            
            # Save to JSON file
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            
            spider.logger.info(f"Saved {len(self.items)} reviews to {json_filename}")
            
            # Also save summary
            self._save_summary(spider, json_filename)
        else:
            spider.logger.warning("No items were scraped!")
    
    def _clean_item(self, adapter):
        """Clean and normalize item data with comprehensive text cleaning."""
        # Clean text fields with HTML removal, emoji removal, and whitespace normalization
        text_fields = ['product_name', 'review_text', 'reviewer_name', 'review_title']
        cleaned_data = {}
        
        for field in text_fields:
            if adapter.get(field):
                cleaned_text = self._clean_text(adapter[field])
                adapter[field] = cleaned_text
                
                # Add to cleaned data for CSV (only include specified columns)
                if field in ['product_name', 'review_text', 'reviewer_name']:
                    cleaned_data[field] = cleaned_text
        
        # Clean rating using TextCleaner
        rating = None
        if adapter.get('rating'):
            rating = TextCleaner.clean_rating(adapter['rating'])
            adapter['rating'] = rating
            cleaned_data['rating'] = rating
        
        # Clean review date using TextCleaner
        review_date = None
        if adapter.get('review_date'):
            cleaned_date = TextCleaner.clean_date(adapter['review_date'])
            adapter['review_date'] = cleaned_date
            cleaned_data['review_date'] = cleaned_date
        
        # Clean helpful votes
        if adapter.get('helpful_votes'):
            try:
                votes_text = str(adapter['helpful_votes'])
                votes_text = TextCleaner.remove_html_tags(votes_text)
                votes_num = int(''.join(c for c in votes_text if c.isdigit()))
                adapter['helpful_votes'] = votes_num
            except (ValueError, TypeError):
                adapter['helpful_votes'] = 0
        
        # Return cleaned data for CSV (only required columns)
        if all(key in cleaned_data for key in ['product_name', 'review_text', 'reviewer_name']):
            return {
                'product_name': cleaned_data.get('product_name', ''),
                'review_text': cleaned_data.get('review_text', ''),
                'rating': cleaned_data.get('rating', ''),
                'review_date': cleaned_data.get('review_date', ''),
                'reviewer_name': cleaned_data.get('reviewer_name', '')
            }
        return None
    
    def _clean_text(self, text):
        """Use the dedicated TextCleaner for comprehensive cleaning."""
        return TextCleaner.clean_review_text(text)
    
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