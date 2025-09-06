# Interactive Dashboard

## Overview

The Interactive Dashboard provides a web-based interface for exploring and visualizing product review data. It makes insights more accessible to non-technical stakeholders through interactive charts, filters, and data exploration tools.

## Features

- **Interactive Visualizations**: Dynamic charts that respond to user input
- **Multiple Analysis Views**: Overall sentiment, aspect-based sentiment, rating distribution, and more
- **Filtering Capabilities**: Filter data by date range, rating, sentiment, and other attributes
- **Review Explorer**: Search and browse individual reviews with highlighting
- **Responsive Design**: Works on desktop and tablet devices
- **Export Options**: Download visualizations and data in various formats
- **Real-time Updates**: Connect to live data sources for up-to-date insights

## Requirements

```
dash>=2.5.0
dash-bootstrap-components>=1.0.0
plotly>=5.5.0
pandas>=1.3.0
numpy>=1.20.0
```

## Usage

### Starting the Dashboard

```bash
python interactive_dashboard.py
```

This will start the dashboard server on http://localhost:8050 by default.

You can also specify a custom port:

```bash
python interactive_dashboard.py --port 8080
```

### Command Line Options

```
--port PORT         Port to run the dashboard server on (default: 8050)
--data-dir DIR      Directory containing review data files (default: scraped_data)
--debug             Run in debug mode with auto-reloading
--host HOST         Host to run the server on (default: 127.0.0.1)
```

## Dashboard Sections

### 1. Overview

The Overview section provides high-level metrics and trends:

- Total reviews count and average rating
- Sentiment distribution pie chart
- Rating distribution histogram
- Review volume over time

### 2. Sentiment Analysis

The Sentiment Analysis section offers deeper insights into review sentiment:

- Sentiment trends over time
- Sentiment breakdown by rating
- Word clouds for positive and negative reviews
- Key phrases by sentiment category

### 3. Aspect-Based Analysis

The Aspect-Based Analysis section shows sentiment for specific product aspects:

- Aspect mention frequency
- Sentiment distribution by aspect
- Aspect sentiment heatmap
- Aspect trends over time

### 4. Review Explorer

The Review Explorer allows users to search and browse individual reviews:

- Full-text search functionality
- Filters for date, rating, and sentiment
- Highlighting of key phrases and aspects
- Sorting options

### 5. Competitor Analysis

If competitor data is available, this section provides comparative insights:

- Rating comparison across competitors
- Sentiment distribution comparison
- Aspect sentiment comparison
- Review volume comparison

## Customization

### Loading Custom Data

The dashboard automatically loads CSV files from the specified data directory. To use custom data sources:

```python
# In interactive_dashboard.py
app = DashboardApp(
    data_sources=[
        {"name": "Custom Dataset", "path": "path/to/custom_data.csv"},
        {"name": "Another Dataset", "path": "path/to/another_data.csv"}
    ]
)
```

### Adding Custom Visualizations

You can extend the dashboard with custom visualizations by modifying the `interactive_dashboard.py` file:

1. Create a new layout component in the `_create_layout` method
2. Add your custom visualization function
3. Connect it to the appropriate callbacks

### Styling

The dashboard uses Bootstrap styling through `dash-bootstrap-components`. You can customize the appearance by:

1. Changing the theme in the `DashboardApp` initialization:
   ```python
   app = DashboardApp(theme="DARKLY")  # or any other Bootstrap theme
   ```

2. Adding custom CSS:
   ```python
   app = DashboardApp(custom_css="path/to/custom.css")
   ```

## Integration with Other Modules

The Interactive Dashboard integrates with other modules in the Product Review Scraper system:

- **Aspect-Based Sentiment Analysis**: Visualizes aspect-level sentiment data
- **Competitor Analysis**: Displays comparative insights across products
- **Incremental Scraping**: Can update with newly scraped data

## Deployment

### Local Network Deployment

To make the dashboard available on your local network:

```bash
python interactive_dashboard.py --host 0.0.0.0
```

Then access it from other devices using your computer's IP address.

### Production Deployment

For production deployment, we recommend using a WSGI server like Gunicorn:

```bash
gunicorn interactive_dashboard:server -b 0.0.0.0:8050
```

For more advanced deployment options, see the [Dash Deployment Guide](https://dash.plotly.com/deployment).

## Troubleshooting

- **Dashboard doesn't load**: Check that all dependencies are installed and the server is running
- **No data appears**: Verify that the data directory contains valid CSV files
- **Slow performance**: Consider reducing the dataset size or optimizing the data loading process
- **Visualization errors**: Check the browser console for JavaScript errors

## Example

For a complete example of dashboard customization, see `example_dashboard_customization.py` in the project directory.