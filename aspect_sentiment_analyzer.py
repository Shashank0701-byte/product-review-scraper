#!/usr/bin/env python3
"""
Aspect-Based Sentiment Analysis Module

This module analyzes product reviews to extract sentiment for specific product aspects/features.
It identifies common product aspects in reviews and determines the sentiment (positive/negative/neutral)
for each aspect, providing more granular insights than overall sentiment analysis.
"""

import pandas as pd
import numpy as np
import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from collections import defaultdict
import logging

# Download required NLTK resources
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load('en_core_web_sm')

class AspectSentimentAnalyzer:
    """Analyzes sentiment for specific product aspects in reviews."""
    
    def __init__(self, common_aspects=None):
        """
        Initialize the analyzer.
        
        Args:
            common_aspects (list, optional): List of predefined aspects to look for.
                If None, aspects will be extracted automatically.
        """
        self.sid = SentimentIntensityAnalyzer()
        self.common_aspects = common_aspects or []
        self.aspect_patterns = self._compile_aspect_patterns()
        self.results = defaultdict(list)
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the analyzer."""
        logger = logging.getLogger('AspectSentimentAnalyzer')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _compile_aspect_patterns(self):
        """Compile regex patterns for predefined aspects."""
        patterns = {}
        for aspect in self.common_aspects:
            # Create pattern for each aspect (handle plurals and variations)
            pattern = r'\b' + aspect + r'(s|es)?\b'
            patterns[aspect] = re.compile(pattern, re.IGNORECASE)
        return patterns
    
    def extract_aspects(self, reviews_df, text_column='review_text', min_count=3):
        """
        Extract common product aspects from reviews using NLP.
        
        Args:
            reviews_df (DataFrame): DataFrame containing reviews
            text_column (str): Column name containing review text
            min_count (int): Minimum count to consider an aspect common
            
        Returns:
            list: Common aspects found in reviews
        """
        self.logger.info("Extracting product aspects from reviews...")
        
        # Combine all reviews into a single text for processing
        all_reviews = " ".join(reviews_df[text_column].dropna().astype(str).tolist())
        
        # Process with spaCy
        doc = nlp(all_reviews)
        
        # Extract noun phrases and count frequencies
        noun_phrases = defaultdict(int)
        
        # Extract noun chunks (noun phrases)
        for chunk in doc.noun_chunks:
            # Keep only noun phrases with 1-3 words
            if 1 <= len(chunk.text.split()) <= 3:
                # Lemmatize to group similar terms
                lemmatized = " ".join([token.lemma_ for token in chunk if not token.is_stop])
                if lemmatized.strip():
                    noun_phrases[lemmatized.lower()] += 1
        
        # Filter for common aspects
        common_aspects = [aspect for aspect, count in noun_phrases.items() 
                         if count >= min_count and len(aspect) > 1]
        
        # Add to predefined aspects if not already included
        for aspect in common_aspects:
            if aspect not in self.common_aspects:
                self.common_aspects.append(aspect)
                self.aspect_patterns[aspect] = re.compile(r'\b' + aspect + r'(s|es)?\b', re.IGNORECASE)
        
        self.logger.info(f"Extracted {len(common_aspects)} common aspects")
        return common_aspects
    
    def find_aspect_sentences(self, review_text, aspect):
        """
        Find sentences in a review that mention a specific aspect.
        
        Args:
            review_text (str): The review text
            aspect (str): The aspect to look for
            
        Returns:
            list: Sentences mentioning the aspect
        """
        if not isinstance(review_text, str):
            return []
        
        # Split review into sentences
        sentences = nltk.sent_tokenize(review_text)
        
        # Find sentences containing the aspect
        aspect_pattern = self.aspect_patterns.get(aspect)
        if not aspect_pattern:
            aspect_pattern = re.compile(r'\b' + aspect + r'(s|es)?\b', re.IGNORECASE)
        
        return [sentence for sentence in sentences if aspect_pattern.search(sentence)]
    
    def analyze_aspect_sentiment(self, reviews_df, text_column='review_text'):
        """
        Analyze sentiment for each aspect in each review.
        
        Args:
            reviews_df (DataFrame): DataFrame containing reviews
            text_column (str): Column name containing review text
            
        Returns:
            dict: Sentiment scores for each aspect
        """
        self.logger.info("Analyzing sentiment for each aspect...")
        
        # Reset results
        self.results = defaultdict(list)
        
        # If no aspects defined yet, extract them
        if not self.common_aspects:
            self.extract_aspects(reviews_df, text_column)
        
        # Analyze each review
        for idx, row in reviews_df.iterrows():
            review_text = row[text_column]
            if not isinstance(review_text, str) or not review_text.strip():
                continue
                
            # For each aspect, find relevant sentences and analyze sentiment
            for aspect in self.common_aspects:
                aspect_sentences = self.find_aspect_sentences(review_text, aspect)
                
                if aspect_sentences:
                    # Calculate sentiment for each sentence mentioning the aspect
                    for sentence in aspect_sentences:
                        sentiment_scores = self.sid.polarity_scores(sentence)
                        compound_score = sentiment_scores['compound']
                        
                        # Store result with review metadata
                        self.results[aspect].append({
                            'review_id': idx,
                            'sentence': sentence,
                            'sentiment_score': compound_score,
                            'sentiment': 'positive' if compound_score >= 0.05 else 
                                        'negative' if compound_score <= -0.05 else 'neutral'
                        })
        
        self.logger.info(f"Completed sentiment analysis for {len(self.results)} aspects")
        return self.results
    
    def get_aspect_summary(self):
        """
        Get summary statistics for each aspect.
        
        Returns:
            DataFrame: Summary statistics for each aspect
        """
        summary_data = []
        
        for aspect, mentions in self.results.items():
            if not mentions:
                continue
                
            # Calculate statistics
            scores = [m['sentiment_score'] for m in mentions]
            sentiments = [m['sentiment'] for m in mentions]
            
            # Count sentiment categories
            positive_count = sentiments.count('positive')
            neutral_count = sentiments.count('neutral')
            negative_count = sentiments.count('negative')
            total_count = len(sentiments)
            
            # Calculate percentages
            positive_pct = (positive_count / total_count) * 100 if total_count > 0 else 0
            neutral_pct = (neutral_count / total_count) * 100 if total_count > 0 else 0
            negative_pct = (negative_count / total_count) * 100 if total_count > 0 else 0
            
            # Calculate average sentiment
            avg_sentiment = sum(scores) / len(scores) if scores else 0
            
            summary_data.append({
                'aspect': aspect,
                'mention_count': total_count,
                'positive_count': positive_count,
                'neutral_count': neutral_count,
                'negative_count': negative_count,
                'positive_pct': positive_pct,
                'neutral_pct': neutral_pct,
                'negative_pct': negative_pct,
                'avg_sentiment': avg_sentiment
            })
        
        # Create DataFrame and sort by mention count
        summary_df = pd.DataFrame(summary_data)
        if not summary_df.empty:
            summary_df = summary_df.sort_values('mention_count', ascending=False)
        
        return summary_df
    
    def visualize_aspect_sentiment(self, output_dir='scraped_data'):
        """
        Create visualizations for aspect-based sentiment analysis.
        
        Args:
            output_dir (str): Directory to save visualizations
            
        Returns:
            dict: Paths to saved visualization files
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        summary_df = self.get_aspect_summary()
        if summary_df.empty:
            self.logger.warning("No aspect data available for visualization")
            return {}
            
        # Limit to top 10 aspects by mention count for better visualization
        plot_df = summary_df.head(10).copy()
        
        # 1. Aspect Sentiment Distribution
        plt.figure(figsize=(12, 8))
        
        # Create data for stacked bar chart
        aspects = plot_df['aspect']
        positive = plot_df['positive_count']
        neutral = plot_df['neutral_count']
        negative = plot_df['negative_count']
        
        # Create stacked bar chart
        bar_width = 0.8
        plt.barh(aspects, positive, bar_width, label='Positive', color='#5cb85c')
        plt.barh(aspects, neutral, bar_width, left=positive, label='Neutral', color='#5bc0de')
        plt.barh(aspects, negative, bar_width, 
                left=positive+neutral, label='Negative', color='#d9534f')
        
        plt.xlabel('Number of Mentions')
        plt.ylabel('Product Aspects')
        plt.title('Sentiment Distribution by Product Aspect', fontsize=14)
        plt.legend(loc='lower right')
        plt.tight_layout()
        
        # Save figure
        aspect_dist_path = os.path.join(output_dir, 'aspect_sentiment_distribution.png')
        plt.savefig(aspect_dist_path)
        plt.close()
        
        # 2. Aspect Sentiment Heatmap
        plt.figure(figsize=(10, 8))
        
        # Create heatmap data
        heatmap_data = plot_df[['aspect', 'positive_pct', 'neutral_pct', 'negative_pct']]
        heatmap_data = heatmap_data.set_index('aspect')
        
        # Create heatmap
        sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', fmt='.1f', 
                   linewidths=.5, cbar_kws={'label': 'Percentage (%)'}, vmin=0, vmax=100)
        
        plt.title('Sentiment Percentage by Product Aspect', fontsize=14)
        plt.tight_layout()
        
        # Save figure
        heatmap_path = os.path.join(output_dir, 'aspect_sentiment_heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()
        
        # 3. Average Sentiment by Aspect
        plt.figure(figsize=(10, 6))
        
        # Sort by average sentiment
        plot_df_sorted = plot_df.sort_values('avg_sentiment')
        
        # Create bar chart with color gradient based on sentiment
        bars = plt.barh(plot_df_sorted['aspect'], plot_df_sorted['avg_sentiment'])
        
        # Color bars based on sentiment value
        for i, bar in enumerate(bars):
            sentiment = plot_df_sorted['avg_sentiment'].iloc[i]
            if sentiment >= 0.05:
                bar.set_color('#5cb85c')  # Green for positive
            elif sentiment <= -0.05:
                bar.set_color('#d9534f')  # Red for negative
            else:
                bar.set_color('#5bc0de')  # Blue for neutral
        
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
        plt.xlabel('Average Sentiment Score (-1 to +1)')
        plt.ylabel('Product Aspects')
        plt.title('Average Sentiment Score by Product Aspect', fontsize=14)
        plt.tight_layout()
        
        # Save figure
        avg_sentiment_path = os.path.join(output_dir, 'aspect_average_sentiment.png')
        plt.savefig(avg_sentiment_path)
        plt.close()
        
        return {
            'distribution': aspect_dist_path,
            'heatmap': heatmap_path,
            'average_sentiment': avg_sentiment_path
        }
    
    def get_aspect_examples(self, aspect, sentiment='positive', limit=5):
        """
        Get example sentences for a specific aspect and sentiment.
        
        Args:
            aspect (str): The aspect to get examples for
            sentiment (str): The sentiment category ('positive', 'negative', or 'neutral')
            limit (int): Maximum number of examples to return
            
        Returns:
            list: Example sentences
        """
        if aspect not in self.results:
            return []
            
        # Filter by sentiment
        filtered = [m for m in self.results[aspect] if m['sentiment'] == sentiment]
        
        # Sort by absolute sentiment score (strongest first)
        sorted_mentions = sorted(filtered, 
                                key=lambda x: abs(x['sentiment_score']), 
                                reverse=True)
        
        # Return sentences
        return [m['sentence'] for m in sorted_mentions[:limit]]
    
    def generate_aspect_report(self):
        """
        Generate a comprehensive text report of the aspect-based sentiment analysis.
        
        Returns:
            str: Formatted text report
        """
        summary_df = self.get_aspect_summary()
        if summary_df.empty:
            return "No aspect data available for reporting."
            
        # Generate report
        report = ["ASPECT-BASED SENTIMENT ANALYSIS REPORT", "="*40, ""]
        
        # Overview section
        report.append(f"Total Aspects Analyzed: {len(summary_df)}")
        report.append(f"Total Aspect Mentions: {summary_df['mention_count'].sum()}")
        report.append("")
        
        # Top aspects by mention
        report.append("TOP ASPECTS BY MENTION COUNT")
        report.append("-"*30)
        for idx, row in summary_df.head(10).iterrows():
            aspect = row['aspect']
            count = row['mention_count']
            avg_sent = row['avg_sentiment']
            sentiment_label = "Positive" if avg_sent >= 0.05 else "Negative" if avg_sent <= -0.05 else "Neutral"
            report.append(f"{aspect}: {count} mentions - Overall: {sentiment_label} ({avg_sent:.2f})")
        report.append("")
        
        # Most positive aspects
        positive_df = summary_df[summary_df['mention_count'] >= 3].sort_values('avg_sentiment', ascending=False)
        report.append("MOST POSITIVE ASPECTS")
        report.append("-"*30)
        for idx, row in positive_df.head(5).iterrows():
            aspect = row['aspect']
            score = row['avg_sentiment']
            pos_pct = row['positive_pct']
            report.append(f"{aspect}: Score {score:.2f} ({pos_pct:.1f}% positive mentions)")
            
            # Add example positive sentences
            examples = self.get_aspect_examples(aspect, 'positive', 2)
            for i, example in enumerate(examples, 1):
                report.append(f"  Example {i}: \"{example}\"")
        report.append("")
        
        # Most negative aspects
        negative_df = summary_df[summary_df['mention_count'] >= 3].sort_values('avg_sentiment')
        report.append("MOST NEGATIVE ASPECTS")
        report.append("-"*30)
        for idx, row in negative_df.head(5).iterrows():
            aspect = row['aspect']
            score = row['avg_sentiment']
            neg_pct = row['negative_pct']
            report.append(f"{aspect}: Score {score:.2f} ({neg_pct:.1f}% negative mentions)")
            
            # Add example negative sentences
            examples = self.get_aspect_examples(aspect, 'negative', 2)
            for i, example in enumerate(examples, 1):
                report.append(f"  Example {i}: \"{example}\"")
        
        return "\n".join(report)


def run_aspect_analysis(input_file=None, output_dir='scraped_data'):
    """
    Run aspect-based sentiment analysis on review data.
    
    Args:
        input_file (str, optional): Path to input CSV file. If None, uses most recent.
        output_dir (str): Directory to save output files
        
    Returns:
        tuple: (summary_df, visualization_paths, report_path)
    """
    # Find input file if not specified
    if input_file is None:
        data_dir = 'scraped_data'
        files = [f for f in os.listdir(data_dir) 
                if (f.startswith('processed_reviews') or f.startswith('cleaned_reviews')) 
                and f.endswith('.csv')]
        
        if not files:
            raise FileNotFoundError("No review CSV files found in scraped_data directory")
        
        # Get the most recent file
        files.sort(reverse=True)
        input_file = os.path.join(data_dir, files[0])
    
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    
    # Determine text column name (different files might use different column names)
    text_column = None
    for possible_name in ['processed_text', 'cleaned_text', 'review_text', 'text']:
        if possible_name in df.columns:
            text_column = possible_name
            break
    
    if text_column is None:
        raise ValueError("Could not find review text column in the CSV file")
    
    # Initialize analyzer with common product aspects
    # These are common aspects that might not be detected automatically
    common_aspects = [
        "quality", "price", "value", "shipping", "packaging", 
        "customer service", "durability", "design", "size", "color"
    ]
    
    analyzer = AspectSentimentAnalyzer(common_aspects)
    
    # Extract additional aspects from the reviews
    analyzer.extract_aspects(df, text_column)
    
    # Analyze sentiment for each aspect
    analyzer.analyze_aspect_sentiment(df, text_column)
    
    # Get summary statistics
    summary_df = analyzer.get_aspect_summary()
    
    # Create visualizations
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    viz_paths = analyzer.visualize_aspect_sentiment(output_dir)
    
    # Generate report
    report = analyzer.generate_aspect_report()
    report_path = os.path.join(output_dir, 'aspect_sentiment_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analysis complete. Results saved to {output_dir}")
    print(f"Report saved to {report_path}")
    
    return summary_df, viz_paths, report_path


if __name__ == "__main__":
    run_aspect_analysis()