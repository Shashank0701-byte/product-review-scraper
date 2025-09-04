import scrapy
import re
import urllib.parse
from datetime import datetime
from review_scraper.items import ReviewItem


class ProductReviewsSpider(scrapy.Spider):
    """
    Universal product review spider that can handle multiple e-commerce sites.
    
    Usage:
        scrapy crawl reviews -a url="PRODUCT_URL" -a max_reviews=200
    """
    
    name = 'reviews'
    allowed_domains = []
    
    def __init__(self, url=None, max_reviews=200, *args, **kwargs):
        super(ProductReviewsSpider, self).__init__(*args, **kwargs)
        
        if not url:
            raise ValueError("URL parameter is required. Use: -a url='PRODUCT_URL'")
        
        self.start_urls = [url]
        self.max_reviews = int(max_reviews)
        self.reviews_scraped = 0
        self.current_page = 1
        
        # Extract domain for allowed_domains
        parsed_url = urllib.parse.urlparse(url)
        self.allowed_domains = [parsed_url.netloc]
        
        # Detect site type
        self.site_type = self._detect_site_type(url)
        self.logger.info(f"Detected site type: {self.site_type}")
        self.logger.info(f"Target: {self.max_reviews} reviews")
    
    def _detect_site_type(self, url):
        """Detect which e-commerce site we're scraping."""
        url_lower = url.lower()
        
        if 'amazon.' in url_lower:
            return 'amazon'
        elif 'ebay.' in url_lower:
            return 'ebay'
        elif 'alibaba.' in url_lower or 'aliexpress.' in url_lower:
            return 'alibaba'
        elif 'walmart.' in url_lower:
            return 'walmart'
        elif 'target.' in url_lower:
            return 'target'
        elif 'bestbuy.' in url_lower:
            return 'bestbuy'
        else:
            return 'generic'
    
    def parse(self, response):
        """Parse the product page and extract reviews."""
        self.logger.info(f"Parsing page: {response.url}")
        
        # Extract product name
        product_name = self._extract_product_name(response)
        self.logger.info(f"Product: {product_name}")
        
        # Extract reviews from current page
        reviews = self._extract_reviews(response, product_name)
        
        for review in reviews:
            if self.reviews_scraped < self.max_reviews:
                self.reviews_scraped += 1
                review['page_number'] = self.current_page
                yield review
            else:
                self.logger.info(f"Reached target of {self.max_reviews} reviews")
                return
        
        # Follow pagination if we need more reviews
        if self.reviews_scraped < self.max_reviews:
            next_page_url = self._get_next_page_url(response)
            if next_page_url:
                self.current_page += 1
                self.logger.info(f"Following pagination to page {self.current_page}: {next_page_url}")
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    meta={'product_name': product_name}
                )
            else:
                self.logger.info("No more pages found or pagination not detected")
    
    def _extract_product_name(self, response):
        """Extract product name based on site type."""
        if self.site_type == 'amazon':
            selectors = [
                '#productTitle::text',
                'h1.a-size-large::text',
                'h1 span::text'
            ]
        elif self.site_type == 'ebay':
            selectors = [
                'h1#x-title-label-lbl::text',
                'h1.x-title-label::text',
                'h1.notranslate::text'
            ]
        elif self.site_type == 'walmart':
            selectors = [
                'h1[data-automation-id="product-title"]::text',
                'h1.prod-ProductTitle::text'
            ]
        else:
            # Generic selectors
            selectors = [
                'h1::text',
                '.product-title::text',
                '.product-name::text',
                'title::text'
            ]
        
        for selector in selectors:
            name = response.css(selector).get()
            if name:
                return name.strip()
        
        return "Unknown Product"
    
    def _extract_reviews(self, response, product_name):
        """Extract reviews based on site type."""
        if self.site_type == 'amazon':
            return self._extract_amazon_reviews(response, product_name)
        elif self.site_type == 'ebay':
            return self._extract_ebay_reviews(response, product_name)
        elif self.site_type == 'walmart':
            return self._extract_walmart_reviews(response, product_name)
        else:
            return self._extract_generic_reviews(response, product_name)
    
    def _extract_amazon_reviews(self, response, product_name):
        """Extract reviews from Amazon."""
        reviews = []
        
        # Amazon review selectors
        review_containers = response.css('div[data-hook="review"]')
        
        for container in review_containers:
            review = ReviewItem()
            
            review['product_name'] = product_name
            review['product_url'] = response.url
            
            # Extract review data (get raw HTML/text for cleaning in pipeline)
            review['reviewer_name'] = container.css('span.a-profile-name::text').get()
            review['rating'] = container.css('i.a-icon-star span.a-icon-alt::text').get()
            review['review_title'] = container.css('a[data-hook="review-title"] span::text').get()
            # Get raw review text with potential HTML
            review['review_text'] = ' '.join(container.css('span[data-hook="review-body"] span::text, span[data-hook="review-body"] *::text').getall())
            review['review_date'] = container.css('span[data-hook="review-date"]::text').get()
            review['helpful_votes'] = container.css('span[data-hook="helpful-vote-statement"]::text').get()
            review['verified_purchase'] = container.css('span[data-hook="avp-badge"]::text').get()
            
            # Generate review ID
            review['review_id'] = container.css('::attr(id)').get()
            
            if review['review_text']:  # Only yield if we have review text
                reviews.append(review)
        
        return reviews
    
    def _extract_ebay_reviews(self, response, product_name):
        """Extract reviews from eBay."""
        reviews = []
        
        # eBay review selectors
        review_containers = response.css('div.reviews-item, div.ebay-review')
        
        for container in review_containers:
            review = ReviewItem()
            
            review['product_name'] = product_name
            review['product_url'] = response.url
            
            review['reviewer_name'] = container.css('.reviewer-name::text, .review-user-name::text').get()
            review['rating'] = container.css('.star-rating::attr(title), .rating::text').get()
            review['review_text'] = container.css('.review-text::text, .review-content::text').get()
            review['review_date'] = container.css('.review-date::text, .review-time::text').get()
            
            if review['review_text']:
                reviews.append(review)
        
        return reviews
    
    def _extract_walmart_reviews(self, response, product_name):
        """Extract reviews from Walmart."""
        reviews = []
        
        # Walmart review selectors
        review_containers = response.css('div[data-testid="reviews-section"] div.review-item')
        
        for container in review_containers:
            review = ReviewItem()
            
            review['product_name'] = product_name
            review['product_url'] = response.url
            
            review['reviewer_name'] = container.css('.reviewer-name::text').get()
            review['rating'] = container.css('.average-rating::attr(aria-label)').get()
            review['review_text'] = container.css('.review-text::text').get()
            review['review_date'] = container.css('.review-date::text').get()
            
            if review['review_text']:
                reviews.append(review)
        
        return reviews
    
    def _extract_generic_reviews(self, response, product_name):
        """Extract reviews using generic selectors."""
        reviews = []
        
        # Generic review selectors
        possible_containers = [
            '.review, .review-item, .user-review',
            '[class*="review"]',
            '[data-testid*="review"]'
        ]
        
        for container_selector in possible_containers:
            containers = response.css(container_selector)
            if containers:
                break
        else:
            containers = []
        
        for container in containers:
            review = ReviewItem()
            
            review['product_name'] = product_name
            review['product_url'] = response.url
            
            # Try different selectors for each field
            review['reviewer_name'] = self._try_selectors(container, [
                '.reviewer-name::text', '.review-author::text', '.user-name::text',
                '[class*="author"]::text', '[class*="name"]::text'
            ])
            
            review['rating'] = self._try_selectors(container, [
                '.rating::text', '.star-rating::text', '[class*="rating"]::text',
                '[class*="star"]::attr(title)', '[class*="score"]::text'
            ])
            
            review['review_text'] = self._try_selectors(container, [
                '.review-text::text', '.review-content::text', '.review-body::text',
                '[class*="text"]::text', '[class*="content"]::text', 'p::text'
            ])
            
            review['review_date'] = self._try_selectors(container, [
                '.review-date::text', '.date::text', '[class*="date"]::text',
                'time::text', '[datetime]::attr(datetime)'
            ])
            
            if review['review_text']:
                reviews.append(review)
        
        return reviews
    
    def _try_selectors(self, container, selectors):
        """Try multiple selectors and return first match."""
        for selector in selectors:
            result = container.css(selector).get()
            if result:
                return result.strip()
        return None
    
    def _get_next_page_url(self, response):
        """Get next page URL based on site type."""
        if self.site_type == 'amazon':
            return self._get_amazon_next_page(response)
        elif self.site_type == 'ebay':
            return self._get_ebay_next_page(response)
        elif self.site_type == 'walmart':
            return self._get_walmart_next_page(response)
        else:
            return self._get_generic_next_page(response)
    
    def _get_amazon_next_page(self, response):
        """Get next page URL for Amazon."""
        next_url = response.css('li.a-last a::attr(href)').get()
        if next_url:
            return urllib.parse.urljoin(response.url, next_url)
        return None
    
    def _get_ebay_next_page(self, response):
        """Get next page URL for eBay."""
        next_url = response.css('a.pagination-next::attr(href)').get()
        if next_url:
            return urllib.parse.urljoin(response.url, next_url)
        return None
    
    def _get_walmart_next_page(self, response):
        """Get next page URL for Walmart."""
        next_url = response.css('a[aria-label="Next page"]::attr(href)').get()
        if next_url:
            return urllib.parse.urljoin(response.url, next_url)
        return None
    
    def _get_generic_next_page(self, response):
        """Get next page URL using generic selectors."""
        selectors = [
            'a.next::attr(href)',
            'a[class*="next"]::attr(href)',
            'a[aria-label*="next"]::attr(href)',
            '.pagination a:last-child::attr(href)',
            'a:contains("Next")::attr(href)',
            'a:contains("→")::attr(href)'
        ]
        
        for selector in selectors:
            next_url = response.css(selector).get()
            if next_url:
                return urllib.parse.urljoin(response.url, next_url)
        
        return None