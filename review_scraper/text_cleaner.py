"""
Text cleaning utilities for the review scraper.
Provides comprehensive text cleaning functions for removing HTML, emojis, and normalizing text.
"""

import re
import html
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    """HTML tag stripper using HTMLParser for robust HTML removal."""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)


class TextCleaner:
    """Comprehensive text cleaning utilities."""
    
    @staticmethod
    def clean_review_text(text):
        """
        Main cleaning function that applies all cleaning steps.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Step 1: Remove HTML tags
        text = TextCleaner.remove_html_tags(text)
        
        # Step 2: Unescape HTML entities
        text = html.unescape(text)
        
        # Step 3: Remove emojis and special unicode characters
        text = TextCleaner.remove_emojis(text)
        
        # Step 4: Normalize whitespace
        text = TextCleaner.normalize_whitespace(text)
        
        # Step 5: Remove common review artifacts
        text = TextCleaner.remove_review_artifacts(text)
        
        return text.strip()
    
    @staticmethod
    def remove_html_tags(text):
        """
        Remove HTML tags from text using both regex and HTMLParser.
        
        Args:
            text (str): Text containing HTML tags
            
        Returns:
            str: Text with HTML tags removed
        """
        # First pass: Use HTMLParser for robust HTML removal
        try:
            stripper = MLStripper()
            stripper.feed(text)
            text = stripper.get_data()
        except:
            # Fallback to regex if HTMLParser fails
            pass
        
        # Second pass: Regex cleanup for remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove script and style content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        return text
    
    @staticmethod
    def remove_emojis(text):
        """
        Remove emojis and special unicode characters.
        
        Args:
            text (str): Text containing emojis
            
        Returns:
            str: Text with emojis removed
        """
        # Comprehensive emoji pattern
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub('', text)
    
    @staticmethod
    def normalize_whitespace(text):
        """
        Normalize whitespace - remove extra spaces, tabs, newlines.
        
        Args:
            text (str): Text with irregular whitespace
            
        Returns:
            str: Text with normalized whitespace
        """
        # Replace multiple whitespace characters with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_review_artifacts(text):
        """
        Remove common review platform artifacts and formatting.
        
        Args:
            text (str): Review text with potential artifacts
            
        Returns:
            str: Cleaned review text
        """
        # Remove common review prefixes/suffixes
        patterns_to_remove = [
            r'^(Review:|Rating:|Verified Purchase:)\s*',
            r'\s*(Read more|Show less|See more|\.\.\.read more)$',
            r'\s*\[.*?\]\s*',  # Remove text in brackets
            r'\s*\(.*?\)\s*$',  # Remove text in parentheses at end
            r'^.*?says:\s*',   # Remove "User says:" patterns
            r'^\d+\s*(stars?|\/5|out of 5)\s*',  # Remove rating indicators
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def clean_rating(rating_text):
        """
        Extract and normalize rating from text.
        
        Args:
            rating_text (str): Raw rating text
            
        Returns:
            float or None: Normalized rating (0-5 scale) or None if not found
        """
        if not rating_text:
            return None
        
        # Remove HTML tags first
        rating_text = TextCleaner.remove_html_tags(str(rating_text))
        
        # Extract numerical rating using various patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:out of|\/|\sof\s)\s*5',  # "4.5 out of 5"
            r'(\d+(?:\.\d+)?)\s*\/\s*5',                    # "4.5/5"
            r'(\d+(?:\.\d+)?)\s*stars?',                    # "4.5 stars"
            r'(\d+(?:\.\d+)?)\s*\/\s*10',                   # "8/10" (convert to 5-scale)
            r'(\d+(?:\.\d+)?)',                             # Any number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, rating_text, re.IGNORECASE)
            if match:
                try:
                    rating = float(match.group(1))
                    
                    # Convert 10-scale to 5-scale if needed
                    if '/10' in rating_text or rating > 5:
                        rating = rating / 2
                    
                    # Ensure rating is within 0-5 range
                    rating = max(0, min(5, rating))
                    return rating
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def clean_date(date_text):
        """
        Clean and normalize date text.
        
        Args:
            date_text (str): Raw date text
            
        Returns:
            str: Cleaned date text
        """
        if not date_text:
            return ""
        
        # Remove HTML and normalize
        date_text = TextCleaner.remove_html_tags(str(date_text))
        date_text = TextCleaner.normalize_whitespace(date_text)
        
        # Remove common prefixes
        date_text = re.sub(r'^(Reviewed|Posted|Date:|On)\s*:?\s*', '', date_text, flags=re.IGNORECASE)
        
        return date_text.strip()


def clean_review_data(review_item):
    """
    Convenience function to clean all fields in a review item.
    
    Args:
        review_item (dict): Dictionary containing review data
        
    Returns:
        dict: Dictionary with cleaned review data
    """
    cleaner = TextCleaner()
    
    cleaned = {}
    
    # Clean text fields
    text_fields = ['product_name', 'review_text', 'reviewer_name', 'review_title']
    for field in text_fields:
        if field in review_item and review_item[field]:
            cleaned[field] = cleaner.clean_review_text(review_item[field])
    
    # Clean rating
    if 'rating' in review_item:
        cleaned['rating'] = cleaner.clean_rating(review_item['rating'])
    
    # Clean date
    if 'review_date' in review_item:
        cleaned['review_date'] = cleaner.clean_date(review_item['review_date'])
    
    # Copy other fields as-is
    for field, value in review_item.items():
        if field not in cleaned:
            cleaned[field] = value
    
    return cleaned