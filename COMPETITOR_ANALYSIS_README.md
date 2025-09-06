# Competitor Analysis Module

## Overview

The Competitor Analysis module allows you to compare product reviews across different competitors, providing valuable business intelligence on how your product stacks up against the competition in terms of ratings, sentiment, and specific product aspects.

## Features

- **Multi-Product Comparison**: Compare reviews across multiple products or competitors
- **Rating Analysis**: Compare average ratings and rating distributions
- **Sentiment Comparison**: Analyze sentiment distribution differences
- **Aspect-Based Comparison**: Compare sentiment for specific product aspects
- **Visualization**: Generate comparative charts and graphs
- **Reporting**: Create comprehensive comparison reports

## Requirements

```
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.5.0
```

## Usage

### Basic Usage

```python
from competitor_analysis import CompetitorAnalysis

# Initialize the analyzer
analyzer = CompetitorAnalysis()

# Add your product's review data
analyzer.add_competitor("Our Product", "scraped_data/our_product_reviews.csv", "our_product")

# Add competitor review data
analyzer.add_competitor("Competitor A", "scraped_data/competitor_a_reviews.csv")
analyzer.add_competitor("Competitor B", "scraped_data/competitor_b_reviews.csv")

# Run comparisons
analyzer.compare_ratings()
analyzer.compare_sentiment()
analyzer.compare_aspects()

# Generate report
report_path = analyzer.generate_comparison_report()
print(f"Report generated: {report_path}")

# Export data for dashboard
data_path = analyzer.export_comparison_data()
print(f"Data exported: {data_path}")
```

### Using the Helper Function

```python
from competitor_analysis import run_competitor_analysis

# Define the main product and competitors
main_file = "scraped_data/our_product_reviews.csv"
competitor_files = {
    "Competitor A": "scraped_data/competitor_a_reviews.csv",
    "Competitor B": "scraped_data/competitor_b_reviews.csv"
}

# Run the analysis
analyzer, report_path = run_competitor_analysis(main_file, competitor_files)
```

## Data Format

The module works with CSV files containing review data. The files should contain columns for:

- Review text (containing words like "text", "review", "comment", or "content" in the column name)
- Rating (containing words like "rating", "score", or "stars" in the column name)
- Date (containing words like "date", "time", or "posted" in the column name)
- Sentiment (optional, containing words like "sentiment", "polarity", or "emotion" in the column name)

The module will automatically detect these columns based on their names.

## Output

### Comparison Report

The module generates a text-based comparison report with sections for:

- Competitors overview
- Rating comparison
- Sentiment comparison
- Aspect comparison

### Visualizations

The module creates several visualization files in the output directory:

1. **Average Rating Comparison**: Bar chart comparing average ratings
2. **Rating Distribution Comparison**: Grouped bar chart showing rating distributions
3. **Sentiment Distribution Comparison**: Stacked bar chart of sentiment percentages
4. **Aspect Mention Count Comparison**: Bar chart of aspect mention frequencies
5. **Aspect Sentiment Comparison**: Bar chart of average sentiment by aspect
6. **Aspect Sentiment Heatmap**: Color-coded visualization of aspect sentiment

Both static (PNG) and interactive (HTML) versions are generated.

## Advanced Usage

### Selective Comparison

```python
# Compare only specific competitors
selected_competitors = ["our_product", "competitor_a"]
analyzer.compare_ratings(competitors=selected_competitors)
analyzer.compare_sentiment(competitors=selected_competitors)
```

### Customizing Aspect Comparison

```python
# Compare only the top 10 aspects
analyzer.compare_aspects(top_n=10)
```

### Custom Output Locations

```python
# Specify custom output paths
report_path = analyzer.generate_comparison_report("custom_reports/comparison_report.txt")
data_path = analyzer.export_comparison_data("custom_data/comparison_data.json")
```

## Integration with Other Modules

The Competitor Analysis module integrates with:

- **Aspect-Based Sentiment Analysis**: For detailed aspect-level comparison
- **Interactive Dashboard**: To display comparative visualizations
- **Business Intelligence Reports**: To incorporate competitive insights

## Command Line Usage

You can also run the competitor analysis from the command line:

```bash
python competitor_analysis.py
```

This will look for review data in the `scraped_data` directory and generate a report.

## Troubleshooting

- **Column detection issues**: If the module can't detect your columns, rename them to include the expected keywords
- **Missing aspect comparison**: Ensure the aspect_sentiment_analyzer module is available
- **Visualization errors**: Check that matplotlib and plotly are properly installed

## Example

For a complete example, see the code at the bottom of `competitor_analysis.py`.