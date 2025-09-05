# Product Review Analysis

This directory contains a Python script that analyzes product review data and generates visualizations to provide insights on customer sentiment and product performance.

## Enhanced Version Available

An enhanced version with VADER sentiment analysis is also available:
- `review_analysis_vader.py` - Enhanced analysis with VADER sentiment
- `VADER_ANALYSIS_README.md` - Documentation for enhanced version

An advanced version using Google Gemini API for AI-powered analysis is also available:
- `gemini_review_analyzer.py` - AI-powered review analysis with Google Gemini
- `GEMINI_ANALYSIS_README.md` - Documentation for Gemini analysis

A comprehensive business intelligence report generator is also available:
- `business_intelligence_report.py` - Complete PDF report combining all analyses
- `BUSINESS_INTELLIGENCE_README.md` - Documentation for business intelligence reporting

## Features

The analysis script performs the following:

1. **Average Rating Calculation** - Computes overall average rating and statistics
2. **Rating Distribution Visualization** - Creates bar chart showing rating distribution
3. **Sentiment Analysis with Word Clouds** - Generates word clouds for positive vs negative reviews
4. **Rating Trend Over Time** - Shows how average rating changed over time

## Generated Visualizations

The following visualizations are automatically generated and saved in the `scraped_data/` directory:

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

Install requirements with:
```bash
pip install pandas matplotlib seaborn wordcloud numpy
```

## Usage

Run the analysis script from the project root directory:

```bash
python review_analysis.py
```

The script will automatically:
1. Load the most recent processed reviews CSV file from `scraped_data/`
2. Perform all analysis steps
3. Generate and save visualizations to `scraped_data/`
4. Display results in the console

## Sample Output

### Average Rating
```
Average Rating: 4.00 out of 5.0
```

### Rating Distribution
![Rating Distribution](scraped_data/rating_distribution.png)

### Word Clouds
![Positive Word Cloud](scraped_data/positive_wordcloud.png)

### Rating Trend Over Time
![Rating Trend](scraped_data/rating_trend.png)

## Customization

To analyze a specific CSV file, modify the `load_data()` function in `review_analysis.py` to specify the file path directly.

For different rating thresholds for sentiment analysis, modify the `analyze_sentiment()` function where reviews are categorized as positive/neutral/negative.