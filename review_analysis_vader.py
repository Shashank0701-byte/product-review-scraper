#!/usr/bin/env python3
"""
Product Review Analysis Script with VADER Sentiment Analysis

This script analyzes product reviews data to provide insights on:
1. Average rating calculation
2. Rating distribution visualization (bar chart)
3. VADER sentiment analysis with pie chart distribution
4. Word cloud of most common positive vs negative words
5. Timeline chart showing how average rating changed over time
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
import os
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    """Load the reviews data from CSV file."""
    # Find the most recent processed reviews file
    data_dir = 'scraped_data'
    files = [f for f in os.listdir(data_dir) if f.startswith('processed_reviews') and f.endswith('.csv')]
    
    if not files:
        raise FileNotFoundError("No processed reviews CSV file found in scraped_data directory")
    
    # Get the most recent file
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path)
    
    print("Dataset loaded successfully!")
    print(f"Shape: {df.shape}")
    print("\nColumns:")
    for col in df.columns:
        print(f"  - {col}")
    
    return df

def calculate_average_rating(df):
    """Calculate and display average rating statistics."""
    print("\n" + "="*50)
    print("1. AVERAGE RATING CALCULATION")
    print("="*50)
    
    # Calculate average rating
    avg_rating = df['rating'].mean()
    print(f"Average Rating: {avg_rating:.2f} out of 5.0")
    
    # Additional rating statistics
    print(f"\nRating Statistics:")
    print(f"  - Minimum: {df['rating'].min()}")
    print(f"  - Maximum: {df['rating'].max()}")
    print(f"  - Median: {df['rating'].median()}")
    print(f"  - Standard Deviation: {df['rating'].std():.2f}")
    
    return avg_rating

def apply_vader_sentiment_analysis(df):
    """Apply VADER sentiment analysis to cleaned reviews."""
    print("\n" + "="*50)
    print("2. VADER SENTIMENT ANALYSIS")
    print("="*50)
    
    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Apply VADER sentiment analysis to cleaned reviews
    def get_sentiment_label(text):
        if pd.isna(text) or not isinstance(text, str) or len(text.strip()) == 0:
            return 'Neutral'
        
        # Get sentiment scores
        scores = analyzer.polarity_scores(text)
        compound_score = scores['compound']
        
        # Classify sentiment based on compound score
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    # Apply sentiment analysis to each review
    df['vader_sentiment'] = df['cleaned_review'].apply(get_sentiment_label)
    
    # Display sentiment distribution
    sentiment_counts = df['vader_sentiment'].value_counts()
    print("VADER Sentiment Distribution:")
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {sentiment}: {count} reviews ({percentage:.1f}%)")
    
    return df

def visualize_vader_sentiment_distribution(df):
    """Create and save VADER sentiment distribution pie chart."""
    print("\n" + "="*50)
    print("3. VADER SENTIMENT DISTRIBUTION VISUALIZATION")
    print("="*50)
    
    # Count sentiments
    sentiment_counts = df['vader_sentiment'].value_counts()
    
    # Define colors for each sentiment
    colors = ['#90EE90', '#FFA500', '#FF7F7F']  # Green for Positive, Orange for Neutral, Red for Negative
    
    # Create pie chart
    plt.figure(figsize=(8, 8))
    
    # Create explode array dynamically based on number of segments
    explode = [0.05] * len(sentiment_counts)
    
    plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', 
            colors=colors[:len(sentiment_counts)], startangle=90, explode=explode)
    
    # Customize the plot
    plt.title('VADER Sentiment Analysis Distribution', fontsize=16, pad=20)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('scraped_data/vader_sentiment_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("VADER sentiment distribution chart saved as: scraped_data/vader_sentiment_distribution.png")

def visualize_rating_distribution(df, avg_rating):
    """Create and save rating distribution bar chart."""
    print("\n" + "="*50)
    print("4. RATING DISTRIBUTION VISUALIZATION")
    print("="*50)
    
    # Create rating distribution bar chart
    plt.figure(figsize=(10, 6))
    
    # Count ratings
    rating_counts = df['rating'].value_counts().sort_index()
    
    # Create bar chart
    bars = plt.bar(rating_counts.index, rating_counts.values, 
                   color=['#ff9999','#66b3ff','#99ff99','#ffcc99','#ff99cc'])
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{int(height)}', ha='center', va='bottom')
    
    # Customize the plot
    plt.title('Distribution of Product Ratings', fontsize=16, pad=20)
    plt.xlabel('Rating (Stars)', fontsize=12)
    plt.ylabel('Number of Reviews', fontsize=12)
    plt.xticks(rating_counts.index)
    plt.grid(axis='y', alpha=0.3)
    
    # Add average line
    plt.axvline(avg_rating, color='red', linestyle='--', linewidth=2, 
                label=f'Average Rating: {avg_rating:.2f}')
    plt.legend()
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('scraped_data/rating_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Rating distribution chart saved as: scraped_data/rating_distribution.png")
    
    # Print distribution percentages
    print("\nRating Distribution (%):")
    for rating in sorted(df['rating'].unique()):
        count = (df['rating'] == rating).sum()
        percentage = (count / len(df)) * 100
        print(f"  {rating} stars: {count} reviews ({percentage:.1f}%)")

def analyze_sentiment(df):
    """Categorize reviews by sentiment and create word clouds."""
    print("\n" + "="*50)
    print("5. SENTIMENT ANALYSIS & WORD CLOUDS")
    print("="*50)
    
    # Categorize reviews as positive or negative based on rating
    df['rating_sentiment'] = df['rating'].apply(lambda x: 'positive' if x >= 4 else ('neutral' if x == 3 else 'negative'))
    
    # Separate positive and negative reviews
    positive_reviews = df[df['rating_sentiment'] == 'positive']
    negative_reviews = df[df['rating_sentiment'] == 'negative']
    
    print(f"Positive reviews (4-5 stars): {len(positive_reviews)}")
    print(f"Negative reviews (1-2 stars): {len(negative_reviews)}")
    print(f"Neutral reviews (3 stars): {len(df[df['rating_sentiment'] == 'neutral'])}")
    
    return positive_reviews, negative_reviews

def create_wordcloud(text, title, filename):
    """Create and save a word cloud."""
    if not text or len(text.strip()) == 0:
        print(f"No text available for {title}")
        return
    
    wordcloud = WordCloud(width=800, height=400, background_color='white', 
                         colormap='viridis', max_words=100).generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Word cloud saved as: {filename}")

def create_wordclouds(positive_reviews, negative_reviews):
    """Create word clouds for positive and negative reviews."""
    # Combine all cleaned reviews for positive and negative sentiments
    positive_text = ' '.join(positive_reviews['cleaned_review'].dropna().astype(str))
    negative_text = ' '.join(negative_reviews['cleaned_review'].dropna().astype(str))
    
    # Create word clouds
    create_wordcloud(positive_text, 'Most Common Words in Positive Reviews (4-5 stars)', 
                     'scraped_data/positive_wordcloud.png')
    create_wordcloud(negative_text, 'Most Common Words in Negative Reviews (1-2 stars)', 
                     'scraped_data/negative_wordcloud.png')

def analyze_rating_trend(df):
    """Analyze and visualize how average rating changed over time."""
    print("\n" + "="*50)
    print("6. RATING TREND OVER TIME")
    print("="*50)
    
    # Convert review_date to datetime
    df['review_date'] = pd.to_datetime(df['review_date'])
    
    # Extract month-year for grouping
    df['month_year'] = df['review_date'].dt.to_period('M')
    
    # Calculate average rating by month
    monthly_avg = df.groupby('month_year')['rating'].agg(['mean', 'count']).reset_index()
    monthly_avg['month_year'] = monthly_avg['month_year'].astype(str)
    
    # Display the timeline data
    print("Monthly Average Ratings:")
    print(monthly_avg)
    
    # Create timeline chart
    plt.figure(figsize=(12, 6))
    
    # Plot average ratings over time
    plt.plot(monthly_avg['month_year'], monthly_avg['mean'], marker='o', linewidth=2, markersize=8)
    
    # Add overall average line
    overall_avg = df['rating'].mean()
    plt.axhline(y=overall_avg, color='red', linestyle='--', alpha=0.7, 
                label=f'Overall Average: {overall_avg:.2f}')
    
    # Customize the plot
    plt.title('Average Rating Trend Over Time', fontsize=16, pad=20)
    plt.xlabel('Review Date (Month-Year)', fontsize=12)
    plt.ylabel('Average Rating (Stars)', fontsize=12)
    plt.ylim(0, 5.5)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on points
    for i, row in monthly_avg.iterrows():
        plt.annotate(f'{row["mean"]:.2f}', 
                     (row['month_year'], row['mean']), 
                     textcoords="offset points", 
                     xytext=(0,10), 
                     ha='center')
    
    plt.tight_layout()
    plt.savefig('scraped_data/rating_trend.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Rating trend chart saved as: scraped_data/rating_trend.png")

def compare_sentiment_methods(df):
    """Compare rating-based sentiment vs VADER sentiment."""
    print("\n" + "="*50)
    print("7. SENTIMENT ANALYSIS COMPARISON")
    print("="*50)
    
    # Create crosstab comparison
    comparison = pd.crosstab(df['rating_sentiment'], df['vader_sentiment'], margins=True)
    print("Comparison of Rating-based vs VADER Sentiment:")
    print(comparison)
    
    return comparison

def main():
    """Main function to run the complete analysis."""
    print("PRODUCT REVIEW ANALYSIS WITH VADER SENTIMENT")
    print("="*50)
    
    try:
        # Load data
        df = load_data()
        
        # 1. Calculate average rating
        avg_rating = calculate_average_rating(df)
        
        # 2. Apply VADER sentiment analysis
        df = apply_vader_sentiment_analysis(df)
        
        # 3. Visualize VADER sentiment distribution
        visualize_vader_sentiment_distribution(df)
        
        # 4. Visualize rating distribution
        visualize_rating_distribution(df, avg_rating)
        
        # 5. Analyze sentiment and create word clouds
        positive_reviews, negative_reviews = analyze_sentiment(df)
        create_wordclouds(positive_reviews, negative_reviews)
        
        # 6. Analyze rating trend over time
        analyze_rating_trend(df)
        
        # 7. Compare sentiment methods
        compare_sentiment_methods(df)
        
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        print("Generated visualizations have been saved in the scraped_data directory:")
        print("  - vader_sentiment_distribution.png")
        print("  - rating_distribution.png")
        print("  - positive_wordcloud.png")
        print("  - negative_wordcloud.png")
        print("  - rating_trend.png")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()