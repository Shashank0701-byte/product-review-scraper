#!/usr/bin/env python3
"""
Test script for text cleaning functionality.
Demonstrates how the text cleaner handles various types of messy review data.
"""

import sys
import os

# Add the review_scraper package to the path
sys.path.insert(0, os.path.dirname(__file__))

from review_scraper.text_cleaner import TextCleaner, clean_review_data


def test_html_removal():
    """Test HTML tag removal."""
    print("🧪 Testing HTML Removal:")
    test_cases = [
        '<p>This is a <strong>great</strong> product!</p>',
        'Amazing quality! <br>Highly recommended. <div>5 stars</div>',
        '<script>alert("xss")</script>Love this item!',
        'Good <!-- comment --> value for money',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        cleaned = TextCleaner.remove_html_tags(test_case)
        print(f"  {i}. '{test_case}' → '{cleaned}'")


def test_emoji_removal():
    """Test emoji removal."""
    print("\n😀 Testing Emoji Removal:")
    test_cases = [
        'Love this product! 😍👍',
        'Great quality 🌟🌟🌟🌟🌟',
        'Fast shipping 🚚💨',
        'Perfect! 👌✨🎉',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        cleaned = TextCleaner.remove_emojis(test_case)
        print(f"  {i}. '{test_case}' → '{cleaned}'")


def test_whitespace_normalization():
    """Test whitespace normalization."""
    print("\n📏 Testing Whitespace Normalization:")
    test_cases = [
        '  Too   many    spaces  ',
        'Line\nbreaks\tand\ttabs',
        '   \n\n\t  Mixed whitespace  \t\n  ',
        'Normal text with some extra  spaces',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        cleaned = TextCleaner.normalize_whitespace(test_case)
        print(f"  {i}. '{repr(test_case)}' → '{cleaned}'")


def test_rating_extraction():
    """Test rating extraction and normalization."""
    print("\n⭐ Testing Rating Extraction:")
    test_cases = [
        '4.5 out of 5 stars',
        '5/5',
        '<span>3 stars</span>',
        '8/10',
        '4.2 stars ⭐⭐⭐⭐',
        'Rating: 5.0',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        rating = TextCleaner.clean_rating(test_case)
        print(f"  {i}. '{test_case}' → {rating}")


def test_comprehensive_cleaning():
    """Test comprehensive text cleaning."""
    print("\n🧽 Testing Comprehensive Cleaning:")
    test_cases = [
        '<p>This product is <strong>amazing</strong>! 😍</p>\n\n   Highly recommended!',
        'Review: Great   quality    item 👍<br>Fast shipping 🚚',
        '<div>Perfect! ⭐⭐⭐⭐⭐</div> <!-- 5 stars --> Love it!',
        '   <script>bad</script>Excellent value   for   money.   \n\n',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        cleaned = TextCleaner.clean_review_text(test_case)
        print(f"  {i}. '{test_case}'")
        print(f"     → '{cleaned}'")


def test_review_data_cleaning():
    """Test cleaning of complete review data."""
    print("\n📋 Testing Complete Review Data Cleaning:")
    
    sample_review = {
        'product_name': '<h1>  Amazing   Product  </h1>',
        'review_text': '<p>This is a <strong>fantastic</strong> product! 😍</p>\n\nHighly recommended! 👍',
        'reviewer_name': '  John   Doe  ',
        'rating': '4.5 out of 5 stars ⭐',
        'review_date': 'Reviewed on January 15, 2024',
        'helpful_votes': '25 people found this helpful',
    }
    
    print("Original data:")
    for key, value in sample_review.items():
        print(f"  {key}: '{value}'")
    
    cleaned_review = clean_review_data(sample_review)
    
    print("\nCleaned data:")
    for key, value in cleaned_review.items():
        print(f"  {key}: '{value}'")


def main():
    """Run all tests."""
    print("🧪 Text Cleaning Functionality Tests")
    print("=" * 50)
    
    test_html_removal()
    test_emoji_removal() 
    test_whitespace_normalization()
    test_rating_extraction()
    test_comprehensive_cleaning()
    test_review_data_cleaning()
    
    print("\n✅ All tests completed!")
    print("\nThe text cleaner is ready to handle:")
    print("  • HTML tags and entities")
    print("  • Emojis and special characters") 
    print("  • Extra whitespace and formatting")
    print("  • Rating extraction and normalization")
    print("  • Review artifacts and common patterns")


if __name__ == "__main__":
    main()