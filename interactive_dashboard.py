#!/usr/bin/env python3
"""
Interactive Dashboard for Product Review Analysis

This module creates an interactive web dashboard using Dash to visualize 
product review data and analysis results, making insights accessible to 
non-technical stakeholders.
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import glob
import json
from datetime import datetime
import re

# Import local modules (with error handling)
try:
    from aspect_sentiment_analyzer import AspectSentimentAnalyzer
except ImportError:
    print("Warning: aspect_sentiment_analyzer module not found. Some features may be disabled.")

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    title="Product Review Analysis Dashboard"
)

# Define colors
COLORS = {
    'positive': '#5cb85c',  # Green
    'neutral': '#5bc0de',   # Blue
    'negative': '#d9534f',  # Red
    'background': '#f9f9f9',
    'text': '#333333'
}

# Define the app layout
def serve_layout():
    # Get available data files
    data_files = get_available_data_files()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Product Review Analysis Dashboard", className="my-4 text-center")
            ])
        ]),
        
        # Data Selection Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Selection"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Data Source:"),
                                dcc.Dropdown(
                                    id="data-file-dropdown",
                                    options=[{"label": f, "value": f} for f in data_files],
                                    value=data_files[0] if data_files else None,
                                    clearable=False
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Select Analysis Type:"),
                                dcc.Dropdown(
                                    id="analysis-type-dropdown",
                                    options=[
                                        {"label": "Overall Sentiment", "value": "overall"},
                                        {"label": "Aspect-Based Sentiment", "value": "aspect"},
                                        {"label": "Rating Distribution", "value": "rating"},
                                        {"label": "Review Timeline", "value": "timeline"}
                                    ],
                                    value="overall",
                                    clearable=False
                                )
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div(id="data-info-container", className="mt-3")
                            ])
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Main Content Area
        dbc.Row([
            # Left Column - Charts
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(id="chart-title", children="Analysis Results")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-charts",
                            type="circle",
                            children=[
                                html.Div(id="charts-container")
                            ]
                        )
                    ])
                ], className="mb-4")
            ], md=8),
            
            # Right Column - Filters and Details
            dbc.Col([
                # Filters Card
                dbc.Card([
                    dbc.CardHeader("Filters"),
                    dbc.CardBody([
                        html.Div(id="filters-container", children=[
                            # Dynamic filters will be added here based on analysis type
                            html.P("Select an analysis type to see available filters.")
                        ])
                    ])
                ], className="mb-4"),
                
                # Details Card
                dbc.Card([
                    dbc.CardHeader("Details"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-details",
                            type="circle",
                            children=[
                                html.Div(id="details-container")
                            ]
                        )
                    ])
                ])
            ], md=4)
        ]),
        
        # Review Explorer Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Review Explorer"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Search Reviews:"),
                                dcc.Input(
                                    id="review-search-input",
                                    type="text",
                                    placeholder="Enter keywords...",
                                    className="form-control mb-2"
                                ),
                                dbc.Button("Search", id="review-search-button", color="primary", className="mb-3")
                            ], md=6),
                            dbc.Col([
                                html.Label("Filter by:"),
                                dcc.Dropdown(
                                    id="review-filter-dropdown",
                                    options=[
                                        {"label": "All Reviews", "value": "all"},
                                        {"label": "Positive Reviews", "value": "positive"},
                                        {"label": "Negative Reviews", "value": "negative"},
                                        {"label": "Neutral Reviews", "value": "neutral"},
                                        {"label": "High Ratings (4-5)", "value": "high_rating"},
                                        {"label": "Low Ratings (1-2)", "value": "low_rating"}
                                    ],
                                    value="all",
                                    clearable=False,
                                    className="mb-3"
                                )
                            ], md=6)
                        ]),
                        dcc.Loading(
                            id="loading-reviews",
                            type="circle",
                            children=[
                                html.Div(id="reviews-container", className="reviews-list")
                            ]
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P(
                    "Product Review Analysis Dashboard | Last updated: " + 
                    datetime.now().strftime("%Y-%m-%d"),
                    className="text-center text-muted"
                )
            ])
        ])
    ], fluid=True, style={"backgroundColor": COLORS["background"]})

# Set the app layout
app.layout = serve_layout

# Helper Functions
def get_available_data_files():
    """Get list of available data files in the scraped_data directory."""
    data_dir = "scraped_data"
    if not os.path.exists(data_dir):
        return []
    
    # Look for CSV files with review data
    patterns = [
        "*reviews*.csv",
        "*processed*.csv",
        "*cleaned*.csv"
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(data_dir, pattern)))
    
    # Return relative paths
    return [os.path.basename(f) for f in sorted(files, reverse=True)]

def load_data(file_name):
    """Load data from the selected file."""
    if not file_name:
        return None
    
    file_path = os.path.join("scraped_data", file_name)
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_csv(file_path)
        
        # Identify text column
        text_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                       ["text", "review", "comment", "content"])]
        if text_columns:
            text_column = text_columns[0]
        else:
            text_column = None
            
        # Identify rating column
        rating_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                         ["rating", "score", "stars"])]
        if rating_columns:
            rating_column = rating_columns[0]
            # Ensure ratings are numeric
            df[rating_column] = pd.to_numeric(df[rating_column], errors="coerce")
        else:
            rating_column = None
            
        # Identify date column
        date_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                       ["date", "time", "posted"])]
        if date_columns:
            date_column = date_columns[0]
            # Try to convert to datetime
            try:
                df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
            except:
                pass
        else:
            date_column = None
            
        # Identify sentiment column
        sentiment_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                           ["sentiment", "polarity", "emotion"])]
        if sentiment_columns:
            sentiment_column = sentiment_columns[0]
        else:
            sentiment_column = None
            
        return {
            "data": df,
            "text_column": text_column,
            "rating_column": rating_column,
            "date_column": date_column,
            "sentiment_column": sentiment_column
        }
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_sentiment_from_rating(rating, max_rating=5):
    """Convert numerical rating to sentiment category."""
    if pd.isna(rating):
        return "neutral"
    
    normalized_rating = rating / max_rating
    
    if normalized_rating >= 0.7:
        return "positive"
    elif normalized_rating <= 0.4:
        return "negative"
    else:
        return "neutral"

def create_review_card(review_data):
    """Create a card component for a single review."""
    # Extract review data
    review_text = review_data.get("text", "No text available")
    rating = review_data.get("rating", None)
    date = review_data.get("date", None)
    sentiment = review_data.get("sentiment", "neutral")
    
    # Determine card color based on sentiment
    if sentiment == "positive":
        card_color = "success"
    elif sentiment == "negative":
        card_color = "danger"
    else:
        card_color = "info"
    
    # Create rating stars if available
    rating_component = html.Div() if rating is None else html.Div([
        html.Span("★" * int(rating) + "☆" * (5 - int(rating)), 
                 className=f"text-{'warning' if rating >= 3 else 'secondary'}")
    ])
    
    # Format date if available
    date_str = "" if date is None else f" | {date}"
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                rating_component,
                html.Small(f"{sentiment.capitalize()}{date_str}", className="text-muted ml-2")
            ], className="d-flex justify-content-between")
        ]),
        dbc.CardBody([
            html.P(review_text[:300] + ("..." if len(review_text) > 300 else ""), 
                  className="card-text")
        ])
    ], className=f"mb-3 border-{card_color}")

# Callbacks
@callback(
    Output("data-info-container", "children"),
    Input("data-file-dropdown", "value")
)
def update_data_info(selected_file):
    """Update the data information panel."""
    if not selected_file:
        return html.P("No data file selected.")
    
    data_obj = load_data(selected_file)
    if not data_obj:
        return html.P("Error loading data file.")
    
    df = data_obj["data"]
    
    return html.Div([
        html.P(f"Loaded {len(df)} reviews from {selected_file}"),
        html.P(f"Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    ])

@callback(
    [Output("chart-title", "children"),
     Output("charts-container", "children"),
     Output("filters-container", "children")],
    [Input("data-file-dropdown", "value"),
     Input("analysis-type-dropdown", "value")]
)
def update_charts(selected_file, analysis_type):
    """Update the charts based on selected data and analysis type."""
    if not selected_file or not analysis_type:
        return "No Data Selected", html.P("Please select a data file and analysis type."), []
    
    data_obj = load_data(selected_file)
    if not data_obj:
        return "Error Loading Data", html.P("Error loading the selected data file."), []
    
    df = data_obj["data"]
    text_column = data_obj["text_column"]
    rating_column = data_obj["rating_column"]
    date_column = data_obj["date_column"]
    sentiment_column = data_obj["sentiment_column"]
    
    # Define filters based on analysis type
    filters = []
    
    if analysis_type == "overall":
        title = "Overall Sentiment Analysis"
        
        # Determine sentiment if not already in data
        if sentiment_column is None and rating_column is not None:
            df["derived_sentiment"] = df[rating_column].apply(get_sentiment_from_rating)
            sentiment_counts = df["derived_sentiment"].value_counts()
        elif sentiment_column is not None:
            sentiment_counts = df[sentiment_column].value_counts()
        else:
            return title, html.P("No sentiment or rating data available."), filters
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.4,
            marker=dict(
                colors=[COLORS.get(s.lower(), "#999999") for s in sentiment_counts.index]
            )
        )])
        
        fig.update_layout(
            title="Sentiment Distribution",
            legend_title="Sentiment",
            height=500
        )
        
        # Create bar chart for sentiment over time if date column exists
        time_chart = html.Div()
        if date_column is not None:
            # Ensure date column is datetime
            if pd.api.types.is_datetime64_any_dtype(df[date_column]):
                # Group by month and sentiment
                df["month"] = df[date_column].dt.to_period("M")
                if sentiment_column is not None:
                    time_data = df.groupby(["month", sentiment_column]).size().reset_index(name="count")
                    sentiment_col = sentiment_column
                else:
                    time_data = df.groupby(["month", "derived_sentiment"]).size().reset_index(name="count")
                    sentiment_col = "derived_sentiment"
                
                # Convert period to string for plotly
                time_data["month_str"] = time_data["month"].astype(str)
                
                # Create stacked bar chart
                time_fig = px.bar(
                    time_data,
                    x="month_str",
                    y="count",
                    color=sentiment_col,
                    title="Sentiment Trends Over Time",
                    color_discrete_map=COLORS
                )
                
                time_fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Number of Reviews",
                    legend_title="Sentiment",
                    height=400
                )
                
                time_chart = dcc.Graph(figure=time_fig, className="mt-4")
        
        # Add filters
        if date_column is not None:
            min_date = df[date_column].min().date()
            max_date = df[date_column].max().date()
            
            filters = [
                html.Label("Date Range:"),
                dcc.DatePickerRange(
                    id="date-range-picker",
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=min_date,
                    end_date=max_date,
                    className="mb-3"
                )
            ]
        
        charts = [
            dcc.Graph(figure=fig),
            time_chart
        ]
        
    elif analysis_type == "aspect":
        title = "Aspect-Based Sentiment Analysis"
        
        # Check if aspect sentiment data is available
        aspect_file = os.path.join("scraped_data", "aspect_sentiment_summary.csv")
        
        if os.path.exists(aspect_file):
            # Load pre-computed aspect sentiment data
            aspect_df = pd.read_csv(aspect_file)
            
            # Create horizontal bar chart for aspect sentiment
            fig = go.Figure()
            
            # Add traces for positive, neutral, negative
            aspects = aspect_df["aspect"].tolist()
            
            fig.add_trace(go.Bar(
                y=aspects,
                x=aspect_df["positive_count"],
                name="Positive",
                orientation="h",
                marker=dict(color=COLORS["positive"])
            ))
            
            fig.add_trace(go.Bar(
                y=aspects,
                x=aspect_df["neutral_count"],
                name="Neutral",
                orientation="h",
                marker=dict(color=COLORS["neutral"])
            ))
            
            fig.add_trace(go.Bar(
                y=aspects,
                x=aspect_df["negative_count"],
                name="Negative",
                orientation="h",
                marker=dict(color=COLORS["negative"])
            ))
            
            fig.update_layout(
                barmode="stack",
                title="Sentiment by Product Aspect",
                xaxis_title="Number of Mentions",
                yaxis_title="Product Aspect",
                height=600
            )
            
            # Create heatmap for sentiment percentages
            heatmap_data = aspect_df[["aspect", "positive_pct", "neutral_pct", "negative_pct"]]
            heatmap_data = heatmap_data.set_index("aspect")
            
            heatmap_fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=["Positive", "Neutral", "Negative"],
                y=heatmap_data.index,
                colorscale="RdYlGn",
                reversescale=True,
                text=[[f"{val:.1f}%" for val in row] for row in heatmap_data.values],
                texttemplate="%{text}",
                textfont={"size":10}
            ))
            
            heatmap_fig.update_layout(
                title="Sentiment Percentage by Product Aspect",
                height=500
            )
            
            # Add filters for aspects
            filters = [
                html.Label("Select Aspects:"),
                dcc.Dropdown(
                    id="aspect-dropdown",
                    options=[{"label": aspect, "value": aspect} for aspect in aspects],
                    value=aspects[:5],  # Default to top 5 aspects
                    multi=True,
                    className="mb-3"
                ),
                html.Label("Sort By:"),
                dcc.RadioItems(
                    id="aspect-sort",
                    options=[
                        {"label": "Mention Count", "value": "count"},
                        {"label": "Positive %", "value": "positive"},
                        {"label": "Negative %", "value": "negative"}
                    ],
                    value="count",
                    className="mb-3"
                )
            ]
            
            charts = [
                dcc.Graph(figure=fig),
                dcc.Graph(figure=heatmap_fig, className="mt-4")
            ]
            
        else:
            # No pre-computed data, offer to run analysis
            if text_column is not None:
                charts = [
                    html.P("No aspect-based sentiment analysis data found."),
                    html.P("Would you like to run the analysis now?"),
                    dbc.Button("Run Aspect Analysis", id="run-aspect-analysis", color="primary")
                ]
            else:
                charts = [html.P("No text data available for aspect-based sentiment analysis.")]
    
    elif analysis_type == "rating":
        title = "Rating Distribution Analysis"
        
        if rating_column is None:
            return title, html.P("No rating data available in the selected file."), []
        
        # Create histogram for ratings
        fig = px.histogram(
            df,
            x=rating_column,
            nbins=5,
            title="Rating Distribution",
            color_discrete_sequence=["#5bc0de"]
        )
        
        fig.update_layout(
            xaxis_title="Rating",
            yaxis_title="Number of Reviews",
            height=500
        )
        
        # Create box plot for ratings
        box_fig = px.box(
            df,
            y=rating_column,
            title="Rating Statistics",
            color_discrete_sequence=["#5bc0de"]
        )
        
        box_fig.update_layout(
            yaxis_title="Rating",
            height=300
        )
        
        # Add filters
        filters = [
            html.Label("Rating Range:"),
            dcc.RangeSlider(
                id="rating-range-slider",
                min=df[rating_column].min(),
                max=df[rating_column].max(),
                step=0.5,
                marks={i: str(i) for i in range(int(df[rating_column].min()), int(df[rating_column].max()) + 1)},
                value=[df[rating_column].min(), df[rating_column].max()],
                className="mb-3"
            )
        ]
        
        charts = [
            dcc.Graph(figure=fig),
            dcc.Graph(figure=box_fig, className="mt-4")
        ]
    
    elif analysis_type == "timeline":
        title = "Review Timeline Analysis"
        
        if date_column is None:
            return title, html.P("No date data available in the selected file."), []
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            try:
                df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
            except:
                return title, html.P("Could not convert date column to datetime format."), []
        
        # Group by date
        df["date_only"] = df[date_column].dt.date
        reviews_by_date = df.groupby("date_only").size().reset_index(name="count")
        
        # Create line chart for review count over time
        fig = px.line(
            reviews_by_date,
            x="date_only",
            y="count",
            title="Review Volume Over Time",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Reviews",
            height=500
        )
        
        # Create additional chart if rating column exists
        rating_time_chart = html.Div()
        if rating_column is not None:
            # Group by date and calculate average rating
            avg_rating_by_date = df.groupby("date_only")[rating_column].mean().reset_index()
            
            rating_fig = px.line(
                avg_rating_by_date,
                x="date_only",
                y=rating_column,
                title="Average Rating Over Time",
                markers=True
            )
            
            rating_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Average Rating",
                height=400
            )
            
            rating_time_chart = dcc.Graph(figure=rating_fig, className="mt-4")
        
        # Add filters
        min_date = df[date_column].min().date()
        max_date = df[date_column].max().date()
        
        filters = [
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id="timeline-date-range",
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                className="mb-3"
            ),
            html.Label("Aggregation Level:"),
            dcc.RadioItems(
                id="timeline-aggregation",
                options=[
                    {"label": "Daily", "value": "D"},
                    {"label": "Weekly", "value": "W"},
                    {"label": "Monthly", "value": "M"}
                ],
                value="D",
                className="mb-3"
            )
        ]
        
        charts = [
            dcc.Graph(figure=fig),
            rating_time_chart
        ]
    
    else:
        title = "Unknown Analysis Type"
        charts = [html.P("The selected analysis type is not recognized.")]
        filters = []
    
    return title, charts, filters

@callback(
    Output("details-container", "children"),
    [Input("data-file-dropdown", "value"),
     Input("analysis-type-dropdown", "value")]
)
def update_details(selected_file, analysis_type):
    """Update the details panel based on selected data and analysis type."""
    if not selected_file or not analysis_type:
        return html.P("Select a data file and analysis type to see details.")
    
    data_obj = load_data(selected_file)
    if not data_obj:
        return html.P("Error loading the selected data file.")
    
    df = data_obj["data"]
    text_column = data_obj["text_column"]
    rating_column = data_obj["rating_column"]
    
    if analysis_type == "overall":
        # Show overall statistics
        stats = []
        
        # Total reviews
        stats.append(html.P(f"Total Reviews: {len(df)}"))
        
        # Rating statistics if available
        if rating_column is not None:
            avg_rating = df[rating_column].mean()
            stats.append(html.P(f"Average Rating: {avg_rating:.2f} / 5"))
            stats.append(html.P(f"Rating Range: {df[rating_column].min()} - {df[rating_column].max()}"))
        
        # Text statistics if available
        if text_column is not None:
            # Calculate average review length
            df["review_length"] = df[text_column].astype(str).apply(len)
            avg_length = df["review_length"].mean()
            stats.append(html.P(f"Average Review Length: {avg_length:.0f} characters"))
        
        return html.Div([
            html.H5("Summary Statistics"),
            html.Div(stats),
            html.Hr(),
            html.H5("Key Insights"),
            html.Ul([
                html.Li("Click on chart segments to filter reviews"),
                html.Li("Use the date range filter to analyze trends over time"),
                html.Li("Check the Review Explorer below to read individual reviews")
            ])
        ])
    
    elif analysis_type == "aspect":
        # Show aspect analysis details
        aspect_file = os.path.join("scraped_data", "aspect_sentiment_report.txt")
        
        if os.path.exists(aspect_file):
            try:
                with open(aspect_file, "r", encoding="utf-8") as f:
                    report_text = f.read()
                
                # Format the report text
                formatted_report = []
                for line in report_text.split("\n"):
                    if line.strip() == "":
                        formatted_report.append(html.Br())
                    elif line.startswith("=") or line.startswith("-"):
                        formatted_report.append(html.Hr())
                    elif line.isupper() or line.startswith("ASPECT"):
                        formatted_report.append(html.H6(line))
                    else:
                        formatted_report.append(html.P(line))
                
                return html.Div(formatted_report)
            except Exception as e:
                return html.P(f"Error loading aspect report: {e}")
        else:
            return html.Div([
                html.P("No aspect analysis report found."),
                html.P("Run the aspect-based sentiment analysis to generate a detailed report.")
            ])
    
    elif analysis_type == "rating":
        # Show rating distribution details
        if rating_column is None:
            return html.P("No rating data available.")
        
        # Calculate rating distribution
        rating_counts = df[rating_column].value_counts().sort_index()
        rating_percentages = (rating_counts / rating_counts.sum() * 100).round(1)
        
        # Create rating distribution table
        rating_rows = []
        for rating, count in rating_counts.items():
            percentage = rating_percentages[rating]
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            rating_rows.append(html.Tr([
                html.Td(stars),
                html.Td(f"{count}"),
                html.Td(f"{percentage}%"),
                html.Td(
                    dbc.Progress(value=percentage, color="warning", className="mb-0")
                )
            ]))
        
        rating_table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Rating"),
                html.Th("Count"),
                html.Th("%"),
                html.Th("Distribution")
            ])),
            html.Tbody(rating_rows)
        ], bordered=True, hover=True, size="sm")
        
        return html.Div([
            html.H5("Rating Distribution"),
            rating_table,
            html.Hr(),
            html.H5("Rating Statistics"),
            html.P(f"Average Rating: {df[rating_column].mean():.2f}"),
            html.P(f"Median Rating: {df[rating_column].median():.1f}"),
            html.P(f"Mode Rating: {df[rating_column].mode()[0]}"),
            html.P(f"Standard Deviation: {df[rating_column].std():.2f}")
        ])
    
    elif analysis_type == "timeline":
        # Show timeline analysis details
        date_column = data_obj["date_column"]
        
        if date_column is None:
            return html.P("No date data available.")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            return html.P("Date column could not be converted to datetime format.")
        
        # Calculate time-based statistics
        earliest_date = df[date_column].min().date()
        latest_date = df[date_column].max().date()
        date_range = (latest_date - earliest_date).days
        
        # Group by month
        df["month"] = df[date_column].dt.to_period("M")
        reviews_by_month = df.groupby("month").size()
        
        # Find peak months
        peak_month = reviews_by_month.idxmax()
        peak_count = reviews_by_month.max()
        
        # Calculate average reviews per month
        avg_per_month = reviews_by_month.mean()
        
        return html.Div([
            html.H5("Timeline Statistics"),
            html.P(f"Date Range: {earliest_date} to {latest_date} ({date_range} days)"),
            html.P(f"Total Months: {len(reviews_by_month)}"),
            html.P(f"Peak Month: {peak_month} ({peak_count} reviews)"),
            html.P(f"Average Reviews per Month: {avg_per_month:.1f}"),
            html.Hr(),
            html.H5("Trend Analysis"),
            html.P("Use the timeline chart to identify:")
        ])
    
    else:
        return html.P("Select a valid analysis type to see details.")

@callback(
    Output("reviews-container", "children"),
    [Input("data-file-dropdown", "value"),
     Input("review-filter-dropdown", "value"),
     Input("review-search-button", "n_clicks")],
    [State("review-search-input", "value")]
)
def update_reviews(selected_file, filter_value, search_clicks, search_text):
    """Update the reviews list based on filters and search."""
    if not selected_file:
        return html.P("Select a data file to view reviews.")
    
    data_obj = load_data(selected_file)
    if not data_obj:
        return html.P("Error loading the selected data file.")
    
    df = data_obj["data"]
    text_column = data_obj["text_column"]
    rating_column = data_obj["rating_column"]
    date_column = data_obj["date_column"]
    sentiment_column = data_obj["sentiment_column"]
    
    if text_column is None:
        return html.P("No review text found in the selected file.")
    
    # Apply filters
    filtered_df = df.copy()
    
    # Filter by sentiment/rating
    if filter_value != "all":
        if filter_value == "positive" and sentiment_column is not None:
            filtered_df = filtered_df[filtered_df[sentiment_column].str.lower() == "positive"]
        elif filter_value == "negative" and sentiment_column is not None:
            filtered_df = filtered_df[filtered_df[sentiment_column].str.lower() == "negative"]
        elif filter_value == "neutral" and sentiment_column is not None:
            filtered_df = filtered_df[filtered_df[sentiment_column].str.lower() == "neutral"]
        elif filter_value == "high_rating" and rating_column is not None:
            filtered_df = filtered_df[filtered_df[rating_column] >= 4]
        elif filter_value == "low_rating" and rating_column is not None:
            filtered_df = filtered_df[filtered_df[rating_column] <= 2]
    
    # Apply search if button clicked and search text provided
    if search_clicks and search_text:
        search_pattern = re.compile(re.escape(search_text), re.IGNORECASE)
        filtered_df = filtered_df[filtered_df[text_column].astype(str).str.contains(search_pattern, regex=True)]
    
    # Limit to 10 reviews for display
    display_df = filtered_df.head(10)
    
    if len(display_df) == 0:
        return html.P("No reviews match the current filters.")
    
    # Create review cards
    review_cards = []
    for idx, row in display_df.iterrows():
        review_data = {
            "text": row[text_column] if pd.notna(row[text_column]) else "No text available",
            "rating": row[rating_column] if rating_column is not None and pd.notna(row[rating_column]) else None,
            "date": row[date_column].strftime("%Y-%m-%d") if date_column is not None and pd.notna(row[date_column]) else None,
            "sentiment": row[sentiment_column] if sentiment_column is not None and pd.notna(row[sentiment_column]) else 
                        get_sentiment_from_rating(row[rating_column]) if rating_column is not None and pd.notna(row[rating_column]) else "neutral"
        }
        
        review_cards.append(create_review_card(review_data))
    
    return html.Div([
        html.P(f"Showing {len(review_cards)} of {len(filtered_df)} matching reviews"),
        html.Div(review_cards)
    ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)