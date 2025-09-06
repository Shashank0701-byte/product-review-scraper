# Aspect-Based Sentiment Analysis Module

## Overview

The Aspect-Based Sentiment Analysis module provides more granular insights than overall sentiment analysis by identifying specific product aspects (features, characteristics) mentioned in reviews and analyzing sentiment for each aspect separately.

## Features

- **Aspect Extraction**: Automatically identifies product aspects mentioned in reviews using NLP techniques
- **Aspect-Level Sentiment**: Analyzes sentiment specifically for each extracted aspect
- **Visualization**: Creates insightful visualizations of aspect sentiment distribution
- **Customizable Aspects**: Allows defining custom aspects to track in addition to automatically extracted ones
- **Aspect Frequency Analysis**: Tracks how often specific aspects are mentioned
- **Comparative Analysis**: Compare aspect sentiment across different time periods

## Requirements

```
spacy>=3.1.0
spacytextblob>=3.0.0
pandas>=1.3.0
nltk>=3.6.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.5.0
```

Before first use, download the required spaCy model:

```bash
python -m spacy download en_core_web_md
python -m textblob.download_corpora
```

## Usage

### Basic Usage

```python
from aspect_sentiment_analyzer import AspectSentimentAnalyzer
import pandas as pd

# Load your review data
reviews_df = pd.read_csv('scraped_data/processed_reviews.csv')

# Initialize the analyzer
analyzer = AspectSentimentAnalyzer()

# Extract aspects from reviews
analyzer.extract_aspects(reviews_df, 'review_text')

# Analyze sentiment for each aspect
analyzer.analyze_aspect_sentiment(reviews_df, 'review_text')

# Get aspect summary
summary_df = analyzer.get_aspect_summary()
print(summary_df.head())

# Generate visualizations
analyzer.visualize_aspects()
```

### With Custom Aspects

```python
# Define custom aspects to track
custom_aspects = [
    "battery life", "camera quality", "screen", "performance", 
    "price", "durability", "software", "design"
]

# Initialize with custom aspects
analyzer = AspectSentimentAnalyzer(custom_aspects=custom_aspects)

# Continue as with basic usage
```

### Saving Results

```python
# Save aspect summary to CSV
summary_df = analyzer.get_aspect_summary()
summary_df.to_csv('aspect_summary.csv', index=False)

# Save visualizations
analyzer.visualize_aspects(save_path='aspect_visualizations/')

# Generate a comprehensive report
analyzer.generate_aspect_report('aspect_report.pdf')
```

## Output

The aspect summary DataFrame contains the following columns:

- `aspect`: The identified product aspect
- `mention_count`: Number of times this aspect was mentioned
- `avg_sentiment`: Average sentiment score for this aspect (-1 to +1)
- `positive_pct`: Percentage of positive mentions
- `neutral_pct`: Percentage of neutral mentions
- `negative_pct`: Percentage of negative mentions

## Visualizations

The module generates several visualizations:

1. **Aspect Frequency**: Bar chart showing how often each aspect is mentioned
2. **Aspect Sentiment Distribution**: Shows the distribution of positive/neutral/negative sentiment for each aspect
3. **Average Sentiment by Aspect**: Bar chart of average sentiment score for each aspect
4. **Aspect Sentiment Heatmap**: Color-coded visualization of sentiment across aspects

## Advanced Configuration

### Customizing Aspect Extraction

```python
# Configure with custom extraction parameters
analyzer = AspectSentimentAnalyzer(
    min_freq=5,               # Minimum frequency to include an aspect
    max_aspects=15,           # Maximum number of aspects to track
    custom_aspects=["price", "quality"],  # Always include these aspects
    ignore_aspects=["product", "item"]    # Always exclude these aspects
)
```

### Time-Based Analysis

```python
# Analyze how aspect sentiment changes over time
analyzer.analyze_aspect_trends(reviews_df, 'review_text', 'review_date')

# Visualize aspect sentiment trends
analyzer.visualize_aspect_trends()
```

## Integration with Other Modules

The Aspect-Based Sentiment Analysis module integrates seamlessly with:

- **Interactive Dashboard**: Displays aspect analysis in an interactive web interface
- **Competitor Analysis**: Compares aspect sentiment across different products
- **Business Intelligence Reports**: Incorporates aspect insights into PDF reports

## Troubleshooting

- **No aspects found**: Try lowering the `min_freq` parameter or adding custom aspects
- **Incorrect aspects**: Add problematic terms to `ignore_aspects` list
- **Slow performance**: Reduce the dataset size or increase `min_freq`

## Example

For a complete example, see `example_aspect_analysis.py` in the project directory.