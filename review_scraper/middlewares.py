# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from itemadapter import is_item, ItemAdapter
import random
import time


class ReviewScraperSpiderMiddleware:
    """Spider middleware for the review scraper."""
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info(f'Spider opened: {spider.name}')


class ReviewScraperDownloaderMiddleware:
    """Downloader middleware for the review scraper."""
    
    def __init__(self):
        # List of User-Agent strings to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Rotate User-Agent
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        
        # Add some common headers
        request.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return None

    def process_response(self, request, response, spider):
        # Check for common anti-bot responses
        if response.status in [403, 429, 503]:
            spider.logger.warning(f"Received {response.status} status code. Possible anti-bot measures.")
            
        # Log successful responses
        if response.status == 200:
            spider.logger.debug(f"Successfully fetched: {response.url}")
            
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.error(f"Exception processing {request.url}: {exception}")
        return None

    def spider_opened(self, spider):
        spider.logger.info(f'Downloader middleware opened for spider: {spider.name}')


class RandomDelayMiddleware:
    """Add random delays between requests to appear more human-like."""
    
    def __init__(self, delay_range=(1, 3)):
        self.delay_range = delay_range
    
    @classmethod
    def from_crawler(cls, crawler):
        delay_range = crawler.settings.get('RANDOM_DELAY_RANGE', (1, 3))
        return cls(delay_range)
    
    def process_request(self, request, spider):
        delay = random.uniform(*self.delay_range)
        spider.logger.debug(f"Random delay: {delay:.2f} seconds")
        time.sleep(delay)
        return None