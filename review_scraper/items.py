# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewItem(scrapy.Item):
    """Item definition for product reviews."""
    
    # Product information
    product_name = scrapy.Field()
    product_url = scrapy.Field()
    
    # Review information
    review_text = scrapy.Field()
    rating = scrapy.Field()
    review_date = scrapy.Field()
    reviewer_name = scrapy.Field()
    
    # Additional metadata
    review_id = scrapy.Field()
    helpful_votes = scrapy.Field()
    verified_purchase = scrapy.Field()
    review_title = scrapy.Field()
    
    # Scraping metadata
    scraped_at = scrapy.Field()
    page_number = scrapy.Field()