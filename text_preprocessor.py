#!/usr/bin/env python3
"""
Advanced Text Preprocessing Script for Review Data
Uses Pandas and NLTK to perform comprehensive text preprocessing including:
- Lowercasing
- Punctuation removal
- Stopword removal
- Lemmatization
- Adds cleaned_review column to CSV files
"""

import pandas as pd
import nltk
import re
import string
import os
import sys
from pathlib import Path
import argparse
from datetime import datetime

# Download required NLTK data
try:
    import nltk
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    print("NLTK data downloaded successfully")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


class ReviewTextPreprocessor:
    """Advanced text preprocessing for review data using NLTK."""
    
    def __init__(self, language='english'):
        """
        Initialize the preprocessor.
        
        Args:
            language (str): Language for stopwords (default: 'english')
        """
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add custom stopwords for reviews
        self.custom_stopwords = {
            'product', 'item', 'purchase', 'buy', 'bought', 'seller',
            'amazon', 'ebay', 'walmart', 'store', 'shipping', 'delivery',
            'price', 'cost', 'money', 'dollar', 'expensive', 'cheap',
            'review', 'reviewer', 'rating', 'star', 'stars',
            'recommend', 'recommended', 'would', 'could', 'should',
            'one', 'two', 'three', 'four', 'five', 'first', 'second',
            'time', 'day', 'week', 'month', 'year', 'ago'
        }
        
        self.stop_words.update(self.custom_stopwords)
        
        print(f"Preprocessor initialized with {len(self.stop_words)} stopwords")
    
    def get_wordnet_pos(self, word):
        """
        Map POS tag to first character used by WordNetLemmatizer.
        
        Args:
            word (str): Word to get POS tag for
            
        Returns:
            str: WordNet POS tag
        """
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)
    
    def preprocess_text(self, text):
        """
        Perform comprehensive text preprocessing.
        
        Args:
            text (str): Raw review text
            
        Returns:
            str: Preprocessed text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Step 1: Convert to lowercase
        text = text.lower()
        
        # Step 2: Remove URLs, email addresses, and mentions
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        
        # Step 3: Remove numbers (but keep words with numbers)
        text = re.sub(r'\b\d+\b', '', text)
        
        # Step 4: Remove extra punctuation but keep sentence structure
        text = re.sub(r'[^\w\s\.\!\?]', ' ', text)
        
        # Step 5: Tokenize
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback tokenization if NLTK fails
            tokens = text.split()
        
        # Step 6: Remove punctuation tokens and single characters
        tokens = [token for token in tokens if token not in string.punctuation and len(token) > 1]
        
        # Step 7: Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Step 8: Lemmatization with POS tagging
        processed_tokens = []
        for token in tokens:
            try:
                pos_tag = self.get_wordnet_pos(token)
                lemmatized = self.lemmatizer.lemmatize(token, pos_tag)
                if len(lemmatized) > 1:  # Keep only meaningful words
                    processed_tokens.append(lemmatized)
            except:
                # Fallback without POS tagging
                lemmatized = self.lemmatizer.lemmatize(token)
                if len(lemmatized) > 1:
                    processed_tokens.append(lemmatized)
        
        # Step 9: Join tokens back to text
        processed_text = ' '.join(processed_tokens)
        
        # Step 10: Final cleanup - remove extra spaces
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text
    
    def preprocess_dataframe(self, df, text_column='review_text', output_column='cleaned_review'):
        """
        Preprocess review text in a pandas DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing review data
            text_column (str): Name of column containing review text
            output_column (str): Name of new column for processed text
            
        Returns:
            pd.DataFrame: DataFrame with added cleaned_review column
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        print(f"Processing {len(df)} reviews...")
        
        # Apply preprocessing to each review
        df[output_column] = df[text_column].apply(self.preprocess_text)
        
        # Calculate statistics
        original_lengths = df[text_column].str.len().fillna(0)
        processed_lengths = df[output_column].str.len().fillna(0)
        
        avg_reduction = (original_lengths.mean() - processed_lengths.mean()) / original_lengths.mean() * 100
        
        print(f"Preprocessing completed:")
        print(f"   • Average text reduction: {avg_reduction:.1f}%")
        print(f"   • Original avg length: {original_lengths.mean():.0f} chars")
        print(f"   • Processed avg length: {processed_lengths.mean():.0f} chars")
        
        return df


def find_csv_files(directory="scraped_data"):
    """
    Find CSV files in the specified directory.
    
    Args:
        directory (str): Directory to search for CSV files
        
    Returns:
        list: List of CSV file paths
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    csv_files = list(directory.glob("cleaned_reviews_*.csv"))
    return sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)


def process_csv_file(input_file, output_file=None, text_column='review_text'):
    """
    Process a single CSV file with review data.
    
    Args:
        input_file (str or Path): Path to input CSV file
        output_file (str or Path, optional): Path to output CSV file
        text_column (str): Name of column containing review text
        
    Returns:
        str: Path to the processed file
    """
    input_file = Path(input_file)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Set default output file name
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = input_file.parent / f"processed_reviews_{timestamp}.csv"
    
    print(f"Processing file: {input_file.name}")
    
    # Load CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")
    
    # Check if required column exists
    if text_column not in df.columns:
        print(f"Column '{text_column}' not found. Available columns: {list(df.columns)}")
        return None
    
    # Initialize preprocessor
    preprocessor = ReviewTextPreprocessor()
    
    # Process the data
    processed_df = preprocessor.preprocess_dataframe(df, text_column)
    
    # Save processed data
    processed_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved processed data to: {output_file}")
    
    # Display sample results
    print("\nSample results:")
    print("-" * 80)
    for i in range(min(3, len(processed_df))):
        original = processed_df.iloc[i][text_column]
        processed = processed_df.iloc[i]['cleaned_review']
        
        print(f"Original {i+1}: {original[:100]}...")
        print(f"Processed {i+1}: {processed[:100]}...")
        print("-" * 40)
    
    return str(output_file)


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Advanced text preprocessing for review data using Pandas and NLTK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_preprocessor.py --auto
  python text_preprocessor.py --file scraped_data/cleaned_reviews_20240115.csv
  python text_preprocessor.py --file reviews.csv --output processed_reviews.csv
  python text_preprocessor.py --file reviews.csv --column review_text
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Specific CSV file to process'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (optional)'
    )
    
    parser.add_argument(
        '--column', '-c',
        type=str,
        default='review_text',
        help='Name of column containing review text (default: review_text)'
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='Automatically process the latest CSV file in scraped_data/'
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=str,
        default='scraped_data',
        help='Directory to search for CSV files (default: scraped_data)'
    )
    
    args = parser.parse_args()
    
    print("Advanced Review Text Preprocessor")
    print("=" * 50)
    
    if args.auto:
        # Auto mode - process latest CSV file
        csv_files = find_csv_files(args.directory)
        
        if not csv_files:
            print(f" No CSV files found in {args.directory}/")
            print(" Run the scraper first to generate review data")
            return
        
        latest_file = csv_files[0]
        print(f"Auto-processing latest file: {latest_file.name}")
        
        try:
            output_file = process_csv_file(latest_file, text_column=args.column)
            print(f"\nProcessing completed successfully!")
            print(f"Output file: {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
    
    elif args.file:
        # Process specific file
        try:
            output_file = process_csv_file(args.file, args.output, args.column)
            print(f"\nProcessing completed successfully!")
            print(f"Output file: {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode
        csv_files = find_csv_files(args.directory)
        
        if not csv_files:
            print(f"No CSV files found in {args.directory}/")
            print("Run the scraper first to generate review data")
            return
        
        print(f"\nFound {len(csv_files)} CSV files:")
        for i, file_path in enumerate(csv_files, 1):
            file_size = file_path.stat().st_size / 1024  # KB
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            print(f"  {i}. {file_path.name} ({file_size:.1f} KB, {mod_time.strftime('%Y-%m-%d %H:%M')})")
        
        try:
            choice = int(input(f"\nSelect file to process (1-{len(csv_files)}): "))
            if 1 <= choice <= len(csv_files):
                selected_file = csv_files[choice - 1]
                output_file = process_csv_file(selected_file, text_column=args.column)
                print(f"\nProcessing completed successfully!")
                print(f"Output file: {output_file}")
            else:
                print("Invalid selection")
        except (ValueError, KeyboardInterrupt):
            print("\nProcessing cancelled")


if __name__ == "__main__":
    main()