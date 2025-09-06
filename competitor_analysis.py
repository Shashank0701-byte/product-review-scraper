#!/usr/bin/env python3
"""
Competitor Analysis Module

This module analyzes product reviews across different competitors to provide
comparative insights on sentiment, ratings, and product aspects.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import json
from datetime import datetime
import logging
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Try to import local modules
try:
    from aspect_sentiment_analyzer import AspectSentimentAnalyzer
except ImportError:
    print("Warning: aspect_sentiment_analyzer module not found. Some features may be disabled.")

class CompetitorAnalysis:
    """Analyzes and compares product reviews across different competitors."""
    
    def __init__(self):
        """
        Initialize the competitor analysis module.
        """
        self.logger = self._setup_logging()
        self.competitors = {}
        self.comparison_results = {}
        self.output_dir = "scraped_data"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _setup_logging(self):
        """Setup logging for the analyzer."""
        logger = logging.getLogger('CompetitorAnalysis')
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
    
    def add_competitor(self, name, data_file, competitor_id=None):
        """
        Add a competitor's review data for analysis.
        
        Args:
            name (str): Name of the competitor or product
            data_file (str): Path to the CSV file containing review data
            competitor_id (str, optional): Unique ID for the competitor. 
                                          If None, name will be used.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(data_file):
            self.logger.error(f"Data file not found: {data_file}")
            return False
        
        try:
            # Load the data
            df = pd.read_csv(data_file)
            
            # Identify key columns
            text_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                          ["text", "review", "comment", "content"])]
            if text_columns:
                text_column = text_columns[0]
            else:
                self.logger.warning(f"No text column found in {data_file}")
                text_column = None
                
            rating_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                             ["rating", "score", "stars"])]
            if rating_columns:
                rating_column = rating_columns[0]
                # Ensure ratings are numeric
                df[rating_column] = pd.to_numeric(df[rating_column], errors="coerce")
            else:
                self.logger.warning(f"No rating column found in {data_file}")
                rating_column = None
                
            date_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                           ["date", "time", "posted"])]
            if date_columns:
                date_column = date_columns[0]
                # Try to convert to datetime
                try:
                    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
                except:
                    self.logger.warning(f"Could not convert date column in {data_file}")
            else:
                date_column = None
                
            sentiment_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                               ["sentiment", "polarity", "emotion"])]
            if sentiment_columns:
                sentiment_column = sentiment_columns[0]
            else:
                sentiment_column = None
            
            # Generate competitor ID if not provided
            if competitor_id is None:
                competitor_id = re.sub(r'\W+', '_', name.lower())
            
            # Store the competitor data
            self.competitors[competitor_id] = {
                "name": name,
                "data_file": data_file,
                "data": df,
                "text_column": text_column,
                "rating_column": rating_column,
                "date_column": date_column,
                "sentiment_column": sentiment_column,
                "review_count": len(df)
            }
            
            self.logger.info(f"Added competitor: {name} with {len(df)} reviews")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding competitor {name}: {e}")
            return False
    
    def list_competitors(self):
        """
        List all added competitors.
        
        Returns:
            list: List of competitor information dictionaries
        """
        result = []
        for competitor_id, data in self.competitors.items():
            result.append({
                "id": competitor_id,
                "name": data["name"],
                "review_count": data["review_count"],
                "data_file": data["data_file"]
            })
        return result
    
    def remove_competitor(self, competitor_id):
        """
        Remove a competitor from the analysis.
        
        Args:
            competitor_id (str): ID of the competitor to remove
            
        Returns:
            bool: True if successful, False if competitor not found
        """
        if competitor_id in self.competitors:
            del self.competitors[competitor_id]
            self.logger.info(f"Removed competitor: {competitor_id}")
            return True
        else:
            self.logger.warning(f"Competitor not found: {competitor_id}")
            return False
    
    def compare_ratings(self, competitors=None):
        """
        Compare ratings across competitors.
        
        Args:
            competitors (list, optional): List of competitor IDs to compare.
                                         If None, all competitors are compared.
        
        Returns:
            dict: Comparison results
        """
        if not self.competitors:
            self.logger.error("No competitors added for comparison")
            return {}
        
        # Use all competitors if none specified
        if competitors is None:
            competitors = list(self.competitors.keys())
        
        # Filter to only include valid competitors
        valid_competitors = [c for c in competitors if c in self.competitors]
        
        if not valid_competitors:
            self.logger.error("No valid competitors specified for comparison")
            return {}
        
        self.logger.info(f"Comparing ratings for {len(valid_competitors)} competitors")
        
        # Collect rating data
        rating_data = {}
        for competitor_id in valid_competitors:
            comp_data = self.competitors[competitor_id]
            rating_column = comp_data["rating_column"]
            
            if rating_column is not None:
                ratings = comp_data["data"][rating_column].dropna()
                
                if len(ratings) > 0:
                    rating_data[competitor_id] = {
                        "name": comp_data["name"],
                        "ratings": ratings,
                        "avg_rating": ratings.mean(),
                        "median_rating": ratings.median(),
                        "rating_counts": ratings.value_counts().sort_index().to_dict(),
                        "rating_distribution": {
                            str(i): (ratings == i).sum() for i in sorted(ratings.unique())
                        }
                    }
        
        if not rating_data:
            self.logger.warning("No rating data available for comparison")
            return {}
        
        # Store results
        self.comparison_results["ratings"] = rating_data
        
        # Create comparison visualizations
        self._create_rating_comparison_charts(rating_data)
        
        return rating_data
    
    def _create_rating_comparison_charts(self, rating_data):
        """
        Create comparison charts for ratings.
        
        Args:
            rating_data (dict): Rating comparison data
        """
        if not rating_data:
            return
        
        # 1. Average Rating Comparison
        plt.figure(figsize=(10, 6))
        
        # Sort by average rating
        sorted_competitors = sorted(
            rating_data.items(),
            key=lambda x: x[1]["avg_rating"],
            reverse=True
        )
        
        names = [data["name"] for _, data in sorted_competitors]
        avg_ratings = [data["avg_rating"] for _, data in sorted_competitors]
        
        # Create bar chart
        bars = plt.bar(names, avg_ratings, color='skyblue')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.xlabel('Competitor')
        plt.ylabel('Average Rating')
        plt.title('Average Rating Comparison')
        plt.ylim(0, 5.5)  # Assuming 5-star rating scale
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save figure
        avg_rating_path = os.path.join(self.output_dir, 'competitor_avg_rating_comparison.png')
        plt.savefig(avg_rating_path)
        plt.close()
        
        # 2. Rating Distribution Comparison
        plt.figure(figsize=(12, 8))
        
        # Prepare data for grouped bar chart
        all_ratings = set()
        for comp_data in rating_data.values():
            all_ratings.update(comp_data["rating_distribution"].keys())
        
        all_ratings = sorted([float(r) for r in all_ratings])
        
        # Set width of bars
        bar_width = 0.8 / len(rating_data)
        
        # Set position of bars on x axis
        positions = np.arange(len(all_ratings))
        
        # Create grouped bar chart
        for i, (comp_id, comp_data) in enumerate(sorted_competitors):
            # Get counts for each rating
            counts = []
            for rating in all_ratings:
                rating_str = str(rating)
                if rating_str in comp_data["rating_distribution"]:
                    counts.append(comp_data["rating_distribution"][rating_str])
                else:
                    counts.append(0)
            
            # Calculate percentages
            total = sum(counts)
            percentages = [count / total * 100 if total > 0 else 0 for count in counts]
            
            # Plot bars
            plt.bar(
                positions + i * bar_width - (len(rating_data) - 1) * bar_width / 2,
                percentages,
                bar_width,
                label=comp_data["name"]
            )
        
        # Add labels and legend
        plt.xlabel('Rating')
        plt.ylabel('Percentage of Reviews (%)')
        plt.title('Rating Distribution Comparison')
        plt.xticks(positions, [str(r) for r in all_ratings])
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save figure
        dist_path = os.path.join(self.output_dir, 'competitor_rating_distribution.png')
        plt.savefig(dist_path)
        plt.close()
        
        # 3. Create interactive Plotly versions for dashboard
        # Average Rating Comparison
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[data["name"] for _, data in sorted_competitors],
            y=[data["avg_rating"] for _, data in sorted_competitors],
            text=[f"{data['avg_rating']:.2f}" for _, data in sorted_competitors],
            textposition='outside',
            marker_color='#5bc0de'
        ))
        
        fig.update_layout(
            title="Average Rating Comparison",
            xaxis_title="Competitor",
            yaxis_title="Average Rating",
            yaxis=dict(range=[0, 5.5]),
            template="plotly_white"
        )
        
        # Save as HTML
        avg_rating_html = os.path.join(self.output_dir, 'competitor_avg_rating_comparison.html')
        fig.write_html(avg_rating_html)
        
        # Rating Distribution Comparison
        fig = go.Figure()
        
        for comp_id, comp_data in sorted_competitors:
            # Get counts for each rating
            ratings = []
            counts = []
            
            for rating in sorted(comp_data["rating_counts"].keys()):
                ratings.append(str(rating))
                counts.append(comp_data["rating_counts"][rating])
            
            # Calculate percentages
            total = sum(counts)
            percentages = [count / total * 100 if total > 0 else 0 for count in counts]
            
            fig.add_trace(go.Bar(
                x=ratings,
                y=percentages,
                name=comp_data["name"],
                text=[f"{p:.1f}%" for p in percentages],
                textposition='auto'
            ))
        
        fig.update_layout(
            title="Rating Distribution Comparison",
            xaxis_title="Rating",
            yaxis_title="Percentage of Reviews (%)",
            barmode='group',
            template="plotly_white"
        )
        
        # Save as HTML
        dist_html = os.path.join(self.output_dir, 'competitor_rating_distribution.html')
        fig.write_html(dist_html)
    
    def compare_sentiment(self, competitors=None):
        """
        Compare sentiment across competitors.
        
        Args:
            competitors (list, optional): List of competitor IDs to compare.
                                         If None, all competitors are compared.
        
        Returns:
            dict: Comparison results
        """
        if not self.competitors:
            self.logger.error("No competitors added for comparison")
            return {}
        
        # Use all competitors if none specified
        if competitors is None:
            competitors = list(self.competitors.keys())
        
        # Filter to only include valid competitors
        valid_competitors = [c for c in competitors if c in self.competitors]
        
        if not valid_competitors:
            self.logger.error("No valid competitors specified for comparison")
            return {}
        
        self.logger.info(f"Comparing sentiment for {len(valid_competitors)} competitors")
        
        # Collect sentiment data
        sentiment_data = {}
        for competitor_id in valid_competitors:
            comp_data = self.competitors[competitor_id]
            sentiment_column = comp_data["sentiment_column"]
            rating_column = comp_data["rating_column"]
            
            if sentiment_column is not None:
                # Use existing sentiment column
                df = comp_data["data"]
                sentiments = df[sentiment_column].dropna()
                
                # Normalize sentiment values to positive/negative/neutral
                sentiment_map = {}
                for sentiment in sentiments.unique():
                    lower_sent = str(sentiment).lower()
                    if any(pos in lower_sent for pos in ["positive", "good", "great"]):
                        sentiment_map[sentiment] = "positive"
                    elif any(neg in lower_sent for neg in ["negative", "bad", "poor"]):
                        sentiment_map[sentiment] = "negative"
                    else:
                        sentiment_map[sentiment] = "neutral"
                
                df["normalized_sentiment"] = df[sentiment_column].map(sentiment_map)
                sentiment_counts = df["normalized_sentiment"].value_counts()
                
            elif rating_column is not None:
                # Derive sentiment from ratings
                df = comp_data["data"]
                df["derived_sentiment"] = df[rating_column].apply(self._get_sentiment_from_rating)
                sentiment_counts = df["derived_sentiment"].value_counts()
            else:
                self.logger.warning(f"No sentiment or rating data for {competitor_id}")
                continue
            
            # Calculate percentages
            total = sentiment_counts.sum()
            sentiment_pct = (sentiment_counts / total * 100).round(1)
            
            sentiment_data[competitor_id] = {
                "name": comp_data["name"],
                "sentiment_counts": sentiment_counts.to_dict(),
                "sentiment_percentages": sentiment_pct.to_dict()
            }
        
        if not sentiment_data:
            self.logger.warning("No sentiment data available for comparison")
            return {}
        
        # Store results
        self.comparison_results["sentiment"] = sentiment_data
        
        # Create comparison visualizations
        self._create_sentiment_comparison_charts(sentiment_data)
        
        return sentiment_data
    
    def _get_sentiment_from_rating(self, rating, max_rating=5):
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
    
    def _create_sentiment_comparison_charts(self, sentiment_data):
        """
        Create comparison charts for sentiment.
        
        Args:
            sentiment_data (dict): Sentiment comparison data
        """
        if not sentiment_data:
            return
        
        # 1. Sentiment Distribution Comparison
        plt.figure(figsize=(12, 8))
        
        # Prepare data
        competitors = list(sentiment_data.keys())
        comp_names = [sentiment_data[c]["name"] for c in competitors]
        
        # Get sentiment categories (should be positive, negative, neutral)
        all_sentiments = set()
        for comp_data in sentiment_data.values():
            all_sentiments.update(comp_data["sentiment_percentages"].keys())
        
        # Sort sentiments in logical order
        sentiment_order = ["positive", "neutral", "negative"]
        all_sentiments = [s for s in sentiment_order if s in all_sentiments]
        
        # Create data for stacked bar chart
        data = []
        for sentiment in all_sentiments:
            percentages = []
            for comp_id in competitors:
                comp_data = sentiment_data[comp_id]
                if sentiment in comp_data["sentiment_percentages"]:
                    percentages.append(comp_data["sentiment_percentages"][sentiment])
                else:
                    percentages.append(0)
            data.append(percentages)
        
        # Set colors
        colors = ['#5cb85c', '#5bc0de', '#d9534f']  # green, blue, red
        
        # Create stacked bar chart
        bottom = np.zeros(len(competitors))
        for i, d in enumerate(data):
            plt.bar(comp_names, d, bottom=bottom, label=all_sentiments[i].capitalize(), 
                   color=colors[i % len(colors)])
            bottom += d
        
        # Add labels and legend
        plt.xlabel('Competitor')
        plt.ylabel('Percentage (%)')
        plt.title('Sentiment Distribution Comparison')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save figure
        sent_path = os.path.join(self.output_dir, 'competitor_sentiment_comparison.png')
        plt.savefig(sent_path)
        plt.close()
        
        # 2. Create interactive Plotly version for dashboard
        fig = go.Figure()
        
        for i, sentiment in enumerate(all_sentiments):
            percentages = []
            for comp_id in competitors:
                comp_data = sentiment_data[comp_id]
                if sentiment in comp_data["sentiment_percentages"]:
                    percentages.append(comp_data["sentiment_percentages"][sentiment])
                else:
                    percentages.append(0)
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Bar(
                x=[sentiment_data[c]["name"] for c in competitors],
                y=percentages,
                name=sentiment.capitalize(),
                marker_color=color,
                text=[f"{p:.1f}%" for p in percentages],
                textposition='auto'
            ))
        
        fig.update_layout(
            title="Sentiment Distribution Comparison",
            xaxis_title="Competitor",
            yaxis_title="Percentage (%)",
            barmode='stack',
            template="plotly_white"
        )
        
        # Save as HTML
        sent_html = os.path.join(self.output_dir, 'competitor_sentiment_comparison.html')
        fig.write_html(sent_html)
    
    def compare_aspects(self, competitors=None, top_n=5):
        """
        Compare aspect-based sentiment across competitors.
        
        Args:
            competitors (list, optional): List of competitor IDs to compare.
                                         If None, all competitors are compared.
            top_n (int): Number of top aspects to compare
            
        Returns:
            dict: Comparison results
        """
        try:
            # Check if AspectSentimentAnalyzer is available
            from aspect_sentiment_analyzer import AspectSentimentAnalyzer
        except ImportError:
            self.logger.error("AspectSentimentAnalyzer module not available")
            return {}
        
        if not self.competitors:
            self.logger.error("No competitors added for comparison")
            return {}
        
        # Use all competitors if none specified
        if competitors is None:
            competitors = list(self.competitors.keys())
        
        # Filter to only include valid competitors
        valid_competitors = [c for c in competitors if c in self.competitors]
        
        if not valid_competitors:
            self.logger.error("No valid competitors specified for comparison")
            return {}
        
        self.logger.info(f"Comparing aspects for {len(valid_competitors)} competitors")
        
        # Define common aspects to look for
        common_aspects = [
            "quality", "price", "value", "shipping", "packaging", 
            "customer service", "durability", "design", "size", "color"
        ]
        
        # Collect aspect data for each competitor
        aspect_data = {}
        for competitor_id in valid_competitors:
            comp_data = self.competitors[competitor_id]
            text_column = comp_data["text_column"]
            
            if text_column is None:
                self.logger.warning(f"No text data for {competitor_id}")
                continue
            
            df = comp_data["data"]
            
            # Initialize analyzer
            analyzer = AspectSentimentAnalyzer(common_aspects)
            
            # Extract aspects and analyze sentiment
            analyzer.extract_aspects(df, text_column)
            analyzer.analyze_aspect_sentiment(df, text_column)
            
            # Get summary statistics
            summary_df = analyzer.get_aspect_summary()
            
            if summary_df.empty:
                self.logger.warning(f"No aspect data for {competitor_id}")
                continue
            
            # Store top aspects
            top_aspects = summary_df.head(top_n)
            
            aspect_data[competitor_id] = {
                "name": comp_data["name"],
                "aspects": top_aspects.to_dict(orient="records")
            }
        
        if not aspect_data:
            self.logger.warning("No aspect data available for comparison")
            return {}
        
        # Store results
        self.comparison_results["aspects"] = aspect_data
        
        # Create comparison visualizations
        self._create_aspect_comparison_charts(aspect_data)
        
        return aspect_data
    
    def _create_aspect_comparison_charts(self, aspect_data):
        """
        Create comparison charts for aspects.
        
        Args:
            aspect_data (dict): Aspect comparison data
        """
        if not aspect_data:
            return
        
        # 1. Top Aspects Comparison
        # Find common aspects across competitors
        all_aspects = set()
        for comp_id, comp_data in aspect_data.items():
            for aspect_record in comp_data["aspects"]:
                all_aspects.add(aspect_record["aspect"])
        
        # Limit to top 10 aspects for better visualization
        if len(all_aspects) > 10:
            # Count aspect mentions across all competitors
            aspect_counts = defaultdict(int)
            for comp_id, comp_data in aspect_data.items():
                for aspect_record in comp_data["aspects"]:
                    aspect_counts[aspect_record["aspect"]] += aspect_record["mention_count"]
            
            # Get top 10 aspects by total mentions
            all_aspects = sorted(aspect_counts.keys(), 
                                key=lambda x: aspect_counts[x], 
                                reverse=True)[:10]
        
        # Create comparison data
        comparison_data = []
        for aspect in all_aspects:
            for comp_id, comp_data in aspect_data.items():
                # Find aspect in competitor data
                aspect_record = None
                for record in comp_data["aspects"]:
                    if record["aspect"] == aspect:
                        aspect_record = record
                        break
                
                if aspect_record:
                    comparison_data.append({
                        "aspect": aspect,
                        "competitor": comp_data["name"],
                        "mention_count": aspect_record["mention_count"],
                        "avg_sentiment": aspect_record["avg_sentiment"],
                        "positive_pct": aspect_record["positive_pct"],
                        "neutral_pct": aspect_record["neutral_pct"],
                        "negative_pct": aspect_record["negative_pct"]
                    })
                else:
                    # Aspect not found for this competitor
                    comparison_data.append({
                        "aspect": aspect,
                        "competitor": comp_data["name"],
                        "mention_count": 0,
                        "avg_sentiment": 0,
                        "positive_pct": 0,
                        "neutral_pct": 0,
                        "negative_pct": 0
                    })
        
        # Convert to DataFrame for easier plotting
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create interactive Plotly charts
        # 1. Aspect Mention Count Comparison
        fig = px.bar(
            comparison_df,
            x="aspect",
            y="mention_count",
            color="competitor",
            barmode="group",
            title="Aspect Mention Count Comparison",
            labels={
                "aspect": "Product Aspect",
                "mention_count": "Number of Mentions",
                "competitor": "Competitor"
            }
        )
        
        fig.update_layout(template="plotly_white")
        
        # Save as HTML
        aspect_count_html = os.path.join(self.output_dir, 'competitor_aspect_count_comparison.html')
        fig.write_html(aspect_count_html)
        
        # 2. Aspect Sentiment Comparison
        fig = px.bar(
            comparison_df,
            x="aspect",
            y="avg_sentiment",
            color="competitor",
            barmode="group",
            title="Aspect Sentiment Comparison",
            labels={
                "aspect": "Product Aspect",
                "avg_sentiment": "Average Sentiment (-1 to +1)",
                "competitor": "Competitor"
            }
        )
        
        fig.update_layout(
            template="plotly_white",
            yaxis=dict(range=[-1, 1])
        )
        
        # Add a horizontal line at y=0
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=0,
            x1=len(all_aspects) - 0.5,
            y1=0,
            line=dict(color="gray", width=1, dash="dash")
        )
        
        # Save as HTML
        aspect_sentiment_html = os.path.join(self.output_dir, 'competitor_aspect_sentiment_comparison.html')
        fig.write_html(aspect_sentiment_html)
        
        # 3. Heatmap of aspect sentiment by competitor
        # Pivot the data for the heatmap
        pivot_df = comparison_df.pivot(index="competitor", columns="aspect", values="avg_sentiment")
        
        # Create heatmap
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Product Aspect", y="Competitor", color="Sentiment"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            title="Aspect Sentiment Heatmap"
        )
        
        fig.update_layout(template="plotly_white")
        
        # Save as HTML
        heatmap_html = os.path.join(self.output_dir, 'competitor_aspect_heatmap.html')
        fig.write_html(heatmap_html)
    
    def generate_comparison_report(self, output_file=None):
        """
        Generate a comprehensive comparison report.
        
        Args:
            output_file (str, optional): Path to save the report.
                                        If None, a default path is used.
        
        Returns:
            str: Path to the generated report
        """
        if not self.comparison_results:
            self.logger.error("No comparison results available")
            return None
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, "competitor_comparison_report.txt")
        
        # Generate report
        report = ["COMPETITOR ANALYSIS REPORT", "="*40, ""]
        
        # Overview section
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Competitors Analyzed: {len(self.competitors)}")
        report.append("")
        
        report.append("COMPETITORS OVERVIEW")
        report.append("-"*30)
        for comp_id, comp_data in self.competitors.items():
            report.append(f"{comp_data['name']}: {comp_data['review_count']} reviews")
        report.append("")
        
        # Rating comparison
        if "ratings" in self.comparison_results:
            report.append("RATING COMPARISON")
            report.append("-"*30)
            
            # Sort by average rating
            sorted_competitors = sorted(
                self.comparison_results["ratings"].items(),
                key=lambda x: x[1]["avg_rating"],
                reverse=True
            )
            
            for comp_id, comp_data in sorted_competitors:
                report.append(f"{comp_data['name']}: {comp_data['avg_rating']:.2f} average rating")
            
            report.append("")
            report.append("Rating Distribution:")
            
            # Find all unique ratings
            all_ratings = set()
            for comp_data in self.comparison_results["ratings"].values():
                all_ratings.update(comp_data["rating_distribution"].keys())
            
            # Create a table header
            header = "Competitor"
            for rating in sorted([float(r) for r in all_ratings]):
                header += f" | {rating:.1f}"
            report.append(header)
            report.append("-" * len(header))
            
            # Add data rows
            for comp_id, comp_data in sorted_competitors:
                row = comp_data["name"]
                for rating in sorted([float(r) for r in all_ratings]):
                    rating_str = str(rating)
                    if rating_str in comp_data["rating_distribution"]:
                        count = comp_data["rating_distribution"][rating_str]
                        total = sum(comp_data["rating_distribution"].values())
                        percentage = count / total * 100 if total > 0 else 0
                        row += f" | {percentage:.1f}%"
                    else:
                        row += " | 0.0%"
                report.append(row)
            
            report.append("")
        
        # Sentiment comparison
        if "sentiment" in self.comparison_results:
            report.append("SENTIMENT COMPARISON")
            report.append("-"*30)
            
            # Create a table
            header = "Competitor | Positive | Neutral | Negative"
            report.append(header)
            report.append("-" * len(header))
            
            for comp_id, comp_data in self.comparison_results["sentiment"].items():
                row = comp_data["name"]
                
                for sentiment in ["positive", "neutral", "negative"]:
                    if sentiment in comp_data["sentiment_percentages"]:
                        percentage = comp_data["sentiment_percentages"][sentiment]
                        row += f" | {percentage:.1f}%"
                    else:
                        row += " | 0.0%"
                
                report.append(row)
            
            report.append("")
        
        # Aspect comparison
        if "aspects" in self.comparison_results:
            report.append("ASPECT COMPARISON")
            report.append("-"*30)
            
            # Find common aspects across competitors
            all_aspects = set()
            for comp_data in self.comparison_results["aspects"].values():
                for aspect_record in comp_data["aspects"]:
                    all_aspects.add(aspect_record["aspect"])
            
            # Limit to top 10 aspects for better readability
            if len(all_aspects) > 10:
                # Count aspect mentions across all competitors
                aspect_counts = defaultdict(int)
                for comp_data in self.comparison_results["aspects"].values():
                    for aspect_record in comp_data["aspects"]:
                        aspect_counts[aspect_record["aspect"]] += aspect_record["mention_count"]
                
                # Get top 10 aspects by total mentions
                all_aspects = sorted(aspect_counts.keys(), 
                                    key=lambda x: aspect_counts[x], 
                                    reverse=True)[:10]
            
            # Report on each aspect
            for aspect in all_aspects:
                report.append(f"Aspect: {aspect}")
                
                for comp_id, comp_data in self.comparison_results["aspects"].items():
                    # Find aspect in competitor data
                    aspect_record = None
                    for record in comp_data["aspects"]:
                        if record["aspect"] == aspect:
                            aspect_record = record
                            break
                    
                    if aspect_record:
                        sentiment_label = "Positive" if aspect_record["avg_sentiment"] >= 0.05 else \
                                         "Negative" if aspect_record["avg_sentiment"] <= -0.05 else "Neutral"
                        
                        report.append(f"  {comp_data['name']}: {aspect_record['mention_count']} mentions, " + \
                                     f"{sentiment_label} ({aspect_record['avg_sentiment']:.2f}), " + \
                                     f"{aspect_record['positive_pct']:.1f}% positive, " + \
                                     f"{aspect_record['negative_pct']:.1f}% negative")
                    else:
                        report.append(f"  {comp_data['name']}: No mentions")
                
                report.append("")
        
        # Conclusion
        report.append("CONCLUSION")
        report.append("-"*30)
        report.append("This report provides a comparative analysis of product reviews across competitors.")
        report.append("Use the visualizations in the 'scraped_data' directory for a more detailed view.")
        
        # Write report to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        self.logger.info(f"Comparison report saved to {output_file}")
        return output_file
    
    def export_comparison_data(self, output_file=None):
        """
        Export comparison data to JSON for use in dashboards.
        
        Args:
            output_file (str, optional): Path to save the JSON data.
                                        If None, a default path is used.
        
        Returns:
            str: Path to the exported data
        """
        if not self.comparison_results:
            self.logger.error("No comparison results available")
            return None
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, "competitor_comparison_data.json")
        
        # Convert data to JSON-serializable format
        export_data = {
            "competitors": {},
            "comparison": {}
        }
        
        # Add competitor info
        for comp_id, comp_data in self.competitors.items():
            export_data["competitors"][comp_id] = {
                "name": comp_data["name"],
                "review_count": comp_data["review_count"],
                "data_file": comp_data["data_file"]
            }
        
        # Add comparison results
        for comparison_type, comparison_data in self.comparison_results.items():
            # Convert any numpy or pandas types to native Python types
            export_data["comparison"][comparison_type] = self._convert_to_serializable(comparison_data)
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Comparison data exported to {output_file}")
        return output_file
    
    def _convert_to_serializable(self, obj):
        """Convert object to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return self._convert_to_serializable(obj.tolist())
        elif pd.isna(obj):
            return None
        else:
            return obj


def run_competitor_analysis(main_file, competitor_files=None):
    """
    Run competitor analysis on review data.
    
    Args:
        main_file (str): Path to the main product's review data
        competitor_files (dict, optional): Dictionary mapping competitor names to file paths
            Example: {"Competitor A": "path/to/competitor_a.csv"}
            If None, only the main product is analyzed
        
    Returns:
        tuple: (analyzer, report_path)
    """
    # Initialize analyzer
    analyzer = CompetitorAnalysis()
    
    # Add main product
    main_name = "Our Product"
    main_id = "our_product"
    
    if not os.path.exists(main_file):
        print(f"Main file not found: {main_file}")
        return analyzer, None
    
    analyzer.add_competitor(main_name, main_file, main_id)
    
    # Add competitors
    if competitor_files:
        for comp_name, comp_file in competitor_files.items():
            if os.path.exists(comp_file):
                analyzer.add_competitor(comp_name, comp_file)
            else:
                print(f"Competitor file not found: {comp_file}")
    
    # Run comparisons
    analyzer.compare_ratings()
    analyzer.compare_sentiment()
    
    # Try to run aspect comparison if possible
    try:
        analyzer.compare_aspects()
    except Exception as e:
        print(f"Error in aspect comparison: {e}")
    
    # Generate report
    report_path = analyzer.generate_comparison_report()
    
    # Export data for dashboard
    analyzer.export_comparison_data()
    
    return analyzer, report_path


if __name__ == "__main__":
    # Example usage
    main_file = "scraped_data/processed_reviews.csv"
    
    # Check if the file exists, otherwise look for alternatives
    if not os.path.exists(main_file):
        data_dir = "scraped_data"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) 
                    if (f.startswith("processed_") or f.startswith("cleaned_")) 
                    and f.endswith(".csv")]
            
            if files:
                main_file = os.path.join(data_dir, files[0])
    
    # Run analysis with just the main product
    analyzer, report_path = run_competitor_analysis(main_file)
    
    if report_path:
        print(f"Analysis complete. Report saved to {report_path}")
    else:
        print("Analysis failed. Check the logs for details.")