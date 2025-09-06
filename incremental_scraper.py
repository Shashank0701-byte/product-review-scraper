#!/usr/bin/env python3
"""
Incremental Scraping Module

This module enables efficient scraping by only fetching new reviews since the last scrape,
rather than re-scraping all reviews each time. It tracks the most recent review date/ID
and uses that information to only request new content.
"""

import os
import json
import pandas as pd
import logging
import hashlib
from datetime import datetime, timedelta
import subprocess
import sys
import re

class IncrementalScraper:
    """Manages incremental scraping of product reviews."""
    
    def __init__(self, data_dir="scraped_data", state_file="scraper_state.json"):
        """
        Initialize the incremental scraper.
        
        Args:
            data_dir (str): Directory where scraped data is stored
            state_file (str): File to store scraper state information
        """
        self.logger = self._setup_logging()
        self.data_dir = data_dir
        self.state_file_path = os.path.join(data_dir, state_file)
        self.state = self._load_state()
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def _setup_logging(self):
        """Setup logging for the scraper."""
        logger = logging.getLogger('IncrementalScraper')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('incremental_scraper.log')
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def _load_state(self):
        """Load scraper state from file."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading state file: {e}")
                return {}
        else:
            self.logger.info("No state file found, creating new state")
            return {}
    
    def _save_state(self):
        """Save scraper state to file."""
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump(self.state, f, indent=2)
            self.logger.info(f"State saved to {self.state_file_path}")
        except Exception as e:
            self.logger.error(f"Error saving state file: {e}")
    
    def _generate_site_key(self, url):
        """Generate a unique key for a site based on URL."""
        # Extract domain and product ID if possible
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        domain = domain_match.group(1) if domain_match else "unknown"
        
        # Try to extract product ID from URL
        product_id = None
        
        # Amazon pattern
        if "amazon" in domain:
            amazon_pattern = r'/(?:dp|gp/product|asin)/([A-Z0-9]{10})'
            match = re.search(amazon_pattern, url)
            if match:
                product_id = match.group(1)
        
        # Best Buy pattern
        elif "bestbuy" in domain:
            bestbuy_pattern = r'/(?:site|shop)/([^/]+/[^/]+/[^/.]+)'
            match = re.search(bestbuy_pattern, url)
            if match:
                product_id = match.group(1)
        
        # Walmart pattern
        elif "walmart" in domain:
            walmart_pattern = r'/ip/[^/]+/(\d+)'
            match = re.search(walmart_pattern, url)
            if match:
                product_id = match.group(1)
        
        # Target pattern
        elif "target" in domain:
            target_pattern = r'/p/[^/]+/-/A-(\d+)'
            match = re.search(target_pattern, url)
            if match:
                product_id = match.group(1)
        
        # If we couldn't extract a product ID, hash the entire URL
        if not product_id:
            return hashlib.md5(url.encode()).hexdigest()
        
        # Otherwise, combine domain and product ID
        return f"{domain}_{product_id}"
    
    def get_last_scrape_info(self, url):
        """
        Get information about the last scrape for a specific URL.
        
        Args:
            url (str): The product URL
            
        Returns:
            dict: Information about the last scrape, or None if no previous scrape
        """
        site_key = self._generate_site_key(url)
        
        if site_key in self.state:
            return self.state[site_key]
        else:
            return None
    
    def update_scrape_info(self, url, scrape_info):
        """
        Update the stored information about a scrape.
        
        Args:
            url (str): The product URL
            scrape_info (dict): Information about the scrape
        """
        site_key = self._generate_site_key(url)
        self.state[site_key] = scrape_info
        self._save_state()
    
    def _get_latest_review_info(self, data_file):
        """
        Extract information about the latest review from a data file.
        
        Args:
            data_file (str): Path to the CSV file containing review data
            
        Returns:
            dict: Information about the latest review, or None if no reviews
        """
        if not os.path.exists(data_file):
            self.logger.warning(f"Data file not found: {data_file}")
            return None
        
        try:
            df = pd.read_csv(data_file)
            
            if df.empty:
                self.logger.warning(f"Data file is empty: {data_file}")
                return None
            
            # Identify date column
            date_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                          ["date", "time", "posted"])]
            if date_columns:
                date_column = date_columns[0]
                
                # Try to convert to datetime
                try:
                    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
                    
                    # Sort by date and get the latest review
                    df = df.sort_values(by=date_column, ascending=False)
                    latest_review = df.iloc[0]
                    
                    # Extract review ID if available
                    id_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                               ["id", "review_id", "reviewid"])]
                    review_id = None
                    if id_columns:
                        review_id = latest_review[id_columns[0]]
                    
                    return {
                        "latest_date": latest_review[date_column].isoformat(),
                        "review_id": review_id,
                        "total_reviews": len(df)
                    }
                except Exception as e:
                    self.logger.warning(f"Error processing date column: {e}")
            
            # If no date column or date processing failed, use review ID if available
            id_columns = [col for col in df.columns if any(x in col.lower() for x in 
                                                         ["id", "review_id", "reviewid"])]
            if id_columns:
                review_id = df[id_columns[0]].iloc[0]
                return {
                    "review_id": review_id,
                    "total_reviews": len(df)
                }
            
            # If no date or ID column, just return the count
            return {"total_reviews": len(df)}
            
        except Exception as e:
            self.logger.error(f"Error extracting latest review info: {e}")
            return None
    
    def merge_new_reviews(self, existing_file, new_file, output_file=None):
        """
        Merge newly scraped reviews with existing reviews, removing duplicates.
        
        Args:
            existing_file (str): Path to the existing review data file
            new_file (str): Path to the newly scraped review data file
            output_file (str, optional): Path to save the merged data.
                                        If None, existing_file is overwritten.
                                        
        Returns:
            tuple: (success, merged_file_path, stats)
        """
        if output_file is None:
            output_file = existing_file
        
        if not os.path.exists(existing_file):
            self.logger.warning(f"Existing file not found: {existing_file}")
            if os.path.exists(new_file):
                # Just use the new file
                try:
                    df_new = pd.read_csv(new_file)
                    df_new.to_csv(output_file, index=False)
                    return True, output_file, {"existing": 0, "new": len(df_new), "merged": len(df_new)}
                except Exception as e:
                    self.logger.error(f"Error copying new file: {e}")
                    return False, None, {}
            else:
                self.logger.error(f"Neither existing nor new file exists")
                return False, None, {}
        
        if not os.path.exists(new_file):
            self.logger.warning(f"New file not found: {new_file}")
            return True, existing_file, {"existing": 0, "new": 0, "merged": 0}
        
        try:
            # Load both datasets
            df_existing = pd.read_csv(existing_file)
            df_new = pd.read_csv(new_file)
            
            existing_count = len(df_existing)
            new_count = len(df_new)
            
            if df_new.empty:
                self.logger.info(f"No new reviews to merge")
                return True, existing_file, {"existing": existing_count, "new": 0, "merged": existing_count}
            
            # Identify key columns for deduplication
            # Try to find review ID column
            id_columns = [col for col in df_existing.columns if any(x in col.lower() for x in 
                                                                ["id", "review_id", "reviewid"])]
            
            # If no ID column, try to use a combination of other columns
            if not id_columns:
                # Try to use reviewer name and date if available
                potential_keys = []
                
                reviewer_columns = [col for col in df_existing.columns if any(x in col.lower() for x in 
                                                                          ["reviewer", "author", "user"])]
                if reviewer_columns:
                    potential_keys.append(reviewer_columns[0])
                
                date_columns = [col for col in df_existing.columns if any(x in col.lower() for x in 
                                                                      ["date", "time", "posted"])]
                if date_columns:
                    potential_keys.append(date_columns[0])
                
                # If we have both reviewer and date, use them as a composite key
                if len(potential_keys) >= 2:
                    # Concatenate the columns to create a composite key
                    df_existing['_merge_key'] = df_existing[potential_keys].astype(str).agg('-'.join, axis=1)
                    df_new['_merge_key'] = df_new[potential_keys].astype(str).agg('-'.join, axis=1)
                    
                    # Use this as our deduplication key
                    dedup_key = '_merge_key'
                else:
                    # If we can't create a good key, just concatenate and accept duplicates
                    self.logger.warning("No suitable deduplication key found, may result in duplicates")
                    df_merged = pd.concat([df_existing, df_new], ignore_index=True)
                    df_merged.to_csv(output_file, index=False)
                    return True, output_file, {
                        "existing": existing_count, 
                        "new": new_count, 
                        "merged": len(df_merged)
                    }
            else:
                # Use the first ID column found
                dedup_key = id_columns[0]
            
            # Perform the merge with deduplication
            df_merged = pd.concat([df_existing, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(subset=[dedup_key], keep='first')
            
            # Save the merged data
            df_merged.to_csv(output_file, index=False)
            
            merged_count = len(df_merged)
            new_added = merged_count - existing_count
            
            self.logger.info(f"Merged {new_added} new reviews with {existing_count} existing reviews")
            
            return True, output_file, {
                "existing": existing_count, 
                "new": new_count, 
                "new_added": new_added,
                "merged": merged_count
            }
            
        except Exception as e:
            self.logger.error(f"Error merging reviews: {e}")
            return False, None, {}
    
    def run_incremental_scrape(self, url, output_file=None, scrapy_project_dir=None, spider_name=None):
        """
        Run an incremental scrape for a specific URL.
        
        Args:
            url (str): The product URL to scrape
            output_file (str, optional): Path to save the merged data.
                                        If None, a default path is used.
            scrapy_project_dir (str, optional): Path to the Scrapy project directory.
                                              If None, assumes current directory.
            spider_name (str, optional): Name of the Scrapy spider to use.
                                       If None, tries to determine automatically.
                                       
        Returns:
            tuple: (success, output_file_path, stats)
        """
        # Generate a site key for the URL
        site_key = self._generate_site_key(url)
        
        # Set default output file if not provided
        if output_file is None:
            output_file = os.path.join(self.data_dir, f"{site_key}_reviews.csv")
        
        # Get information about the last scrape
        last_scrape = self.get_last_scrape_info(url)
        
        # Determine the temporary file for new reviews
        temp_file = os.path.join(self.data_dir, f"{site_key}_new_reviews.csv")
        
        # Prepare scrape parameters
        scrape_params = {
            "url": url,
            "output": temp_file
        }
        
        # Add incremental parameters if we have last scrape info
        if last_scrape:
            if "latest_date" in last_scrape:
                # Convert ISO date string to datetime
                latest_date = datetime.fromisoformat(last_scrape["latest_date"])
                # Subtract a day to ensure overlap and avoid missing reviews
                latest_date = latest_date - timedelta(days=1)
                scrape_params["since_date"] = latest_date.strftime("%Y-%m-%d")
            
            if "review_id" in last_scrape and last_scrape["review_id"]:
                scrape_params["since_id"] = last_scrape["review_id"]
        
        # Determine the spider to use
        if spider_name is None:
            # Try to determine from URL
            if "amazon" in url.lower():
                spider_name = "amazon"
            elif "bestbuy" in url.lower():
                spider_name = "bestbuy"
            elif "walmart" in url.lower():
                spider_name = "walmart"
            elif "target" in url.lower():
                spider_name = "target"
            else:
                spider_name = "generic"
        
        # Build the Scrapy command
        if scrapy_project_dir:
            os.chdir(scrapy_project_dir)
        
        # Convert scrape_params to command line arguments
        cmd_args = ["scrapy", "crawl", spider_name, "-a"]
        
        # Build the arguments string
        args_str = ""
        for key, value in scrape_params.items():
            args_str += f"{key}={value},"
        args_str = args_str.rstrip(",")  # Remove trailing comma
        
        cmd_args.append(args_str)
        
        # Run the scraper
        self.logger.info(f"Running incremental scrape for {url}")
        self.logger.info(f"Command: {' '.join(cmd_args)}")
        
        try:
            result = subprocess.run(cmd_args, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Scraper failed with code {result.returncode}")
                self.logger.error(f"Error: {result.stderr}")
                return False, None, {}
            
            # Check if the temp file was created
            if not os.path.exists(temp_file):
                self.logger.error(f"Scraper did not create output file: {temp_file}")
                return False, None, {}
            
            # Merge with existing data if available
            if os.path.exists(output_file):
                success, merged_file, stats = self.merge_new_reviews(output_file, temp_file)
            else:
                # Just use the new file
                try:
                    df_new = pd.read_csv(temp_file)
                    df_new.to_csv(output_file, index=False)
                    success = True
                    merged_file = output_file
                    stats = {"existing": 0, "new": len(df_new), "merged": len(df_new)}
                except Exception as e:
                    self.logger.error(f"Error copying new file: {e}")
                    success = False
                    merged_file = None
                    stats = {}
            
            # Update scrape info
            if success:
                latest_info = self._get_latest_review_info(output_file)
                if latest_info:
                    latest_info["last_scrape_time"] = datetime.now().isoformat()
                    latest_info["last_scrape_url"] = url
                    self.update_scrape_info(url, latest_info)
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return success, merged_file, stats
            
        except Exception as e:
            self.logger.error(f"Error running incremental scrape: {e}")
            return False, None, {}


def run_incremental_scrape(url, output_file=None, scrapy_project_dir=None, spider_name=None):
    """
    Run an incremental scrape for a specific URL.
    
    Args:
        url (str): The product URL to scrape
        output_file (str, optional): Path to save the merged data.
                                    If None, a default path is used.
        scrapy_project_dir (str, optional): Path to the Scrapy project directory.
                                          If None, assumes current directory.
        spider_name (str, optional): Name of the Scrapy spider to use.
                                   If None, tries to determine automatically.
                                   
    Returns:
        tuple: (success, output_file_path, stats)
    """
    scraper = IncrementalScraper()
    return scraper.run_incremental_scrape(url, output_file, scrapy_project_dir, spider_name)


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Run incremental scraping for product reviews")
    parser.add_argument("url", help="URL of the product to scrape")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--project-dir", "-p", help="Scrapy project directory")
    parser.add_argument("--spider", "-s", help="Spider name")
    
    args = parser.parse_args()
    
    # Run the incremental scrape
    success, output_file, stats = run_incremental_scrape(
        args.url, 
        args.output, 
        args.project_dir, 
        args.spider
    )
    
    if success:
        print(f"Incremental scrape completed successfully")
        print(f"Output file: {output_file}")
        print(f"Stats: {stats}")
        sys.exit(0)
    else:
        print(f"Incremental scrape failed")
        sys.exit(1)