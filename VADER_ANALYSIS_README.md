# Product Review Analysis with VADER Sentiment Analysis

This directory contains an enhanced Python script that analyzes product review data with VADER sentiment analysis and generates comprehensive visualizations to provide insights on customer sentiment and product performance.

## Features

The enhanced analysis script performs the following:

1. **Average Rating Calculation** - Computes overall average rating and statistics
2. **VADER Sentiment Analysis** - Applies VADER sentiment analysis to cleaned reviews
3. **VADER Sentiment Distribution Visualization** - Creates pie chart showing sentiment distribution
4. **Rating Distribution Visualization** - Creates bar chart showing rating distribution
5. **Sentiment Analysis with Word Clouds** - Generates word clouds for positive vs negative reviews
6. **Rating Trend Over Time** - Shows how average rating changed over time
7. **Sentiment Method Comparison** - Compares rating-based sentiment vs VADER sentiment

## Generated Visualizations

The following visualizations are automatically generated and saved in the `scraped_data/` directory:

- `vader_sentiment_distribution.png` - Pie chart of VADER sentiment distribution
- `rating_distribution.png` - Bar chart of rating distribution
- `positive_wordcloud.png` - Word cloud of most common words in positive reviews
- `negative_wordcloud.png` - Word cloud of most common words in negative reviews (if any)
- `rating_trend.png` - Timeline chart showing average rating changes over time

## Requirements

The analysis script requires the following Python packages:
- pandas
- matplotlib
- seaborn
- wordcloud
- numpy
- vaderSentiment

Install requirements with:
```bash
pip install pandas matplotlib seaborn wordcloud numpy vaderSentiment
```

## Usage

Run the enhanced analysis script from the project root directory:

```bash
python review_analysis_vader.py
```

The script will automatically:
1. Load the most recent processed reviews CSV file from `scraped_data/`
2. Apply VADER sentiment analysis to each cleaned review
3. Perform all analysis steps
4. Generate and save visualizations to `scraped_data/`
5. Display results in the console

## Sample Output

### VADER Sentiment Analysis
```
VADER Sentiment Distribution:
  Positive: 5 reviews (100.0%)
```

### VADER Sentiment Distribution
![VADER Sentiment Distribution](scraped_data/vader_sentiment_distribution.png)

### Rating Distribution
![Rating Distribution](scraped_data/rating_distribution.png)

### Word Clouds
![Positive Word Cloud](scraped_data/positive_wordcloud.png)

### Rating Trend Over Time
![Rating Trend](scraped_data/rating_trend.png)

## How VADER Sentiment Analysis Works

VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media. It provides sentiment scores based on:

- **Positive Score**: Proportion of text that is positive
- **Negative Score**: Proportion of text that is negative
- **Neutral Score**: Proportion of text that is neutral
- **Compound Score**: Normalized score between -1 (most negative) and +1 (most positive)

The script classifies reviews as:
- **Positive**: Compound score ≥ 0.05
- **Negative**: Compound score ≤ -0.05
- **Neutral**: Compound score between -0.05 and 0.05

## Customization

To analyze a specific CSV file, modify the `load_data()` function in `review_analysis_vader.py` to specify the file path directly.

For different sentiment thresholds, modify the `get_sentiment_label()` function where reviews are categorized based on compound scores.