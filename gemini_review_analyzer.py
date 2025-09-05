#!/usr/bin/env python3
"""
Product Review Analysis with Google Gemini API

This script sends batches of product reviews to Google Gemini API for advanced analysis,
generating structured summaries with Top Positive Themes, Top Negative Themes, 
and Overall Customer Opinion.
"""

import pandas as pd
import time
import json
import os
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Import Google Generative AI
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    from google.generativeai.generative_models import GenerativeModel
except ImportError as e:
    print(f"Error importing Google Generative AI: {e}")
    print("Please install it with: pip install google-generativeai")
    exit(1)

# Configure Gemini API
# Note: In production, use environment variables or a secure config file
GEMINI_API_KEY = "AIzaSyC0fnFRqB7dkXBsh07Sw3LQLfMCDt8q2lc"
genai.configure(api_key=GEMINI_API_KEY)

# Generation configuration
generation_config = GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    top_k=64,
    max_output_tokens=8192,
)

def load_reviews_data() -> pd.DataFrame:
    """Load the most recent processed reviews data."""
    # Find the most recent processed reviews file
    data_dir = 'scraped_data'
    files = [f for f in os.listdir(data_dir) if f.startswith('processed_reviews') and f.endswith('.csv')]
    
    if not files:
        raise FileNotFoundError("No processed reviews CSV file found in scraped_data directory")
    
    # Get the most recent file
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"Loading reviews data from: {file_path}")
    df = pd.read_csv(file_path)
    
    print(f"Loaded {len(df)} reviews")
    return df

def create_gemini_prompt(reviews_batch: List[Dict]) -> str:
    """Create a prompt for Gemini API with the batch of reviews."""
    prompt = """Analyze the following product reviews and provide a structured summary with these three sections:

1. Top Positive Themes
2. Top Negative Themes
3. Overall Customer Opinion

Reviews:
"""
    
    for i, review in enumerate(reviews_batch, 1):
        prompt += f"\nReview {i}:\n"
        prompt += f"Rating: {review.get('rating', 'N/A')}\n"
        prompt += f"Review Text: {review.get('cleaned_review', review.get('review_text', 'N/A'))}\n"
        prompt += "---\n"
    
    prompt += """

Please provide your analysis in a clear, structured format with specific themes and insights from the reviews.
Focus on the most frequently mentioned positive and negative aspects.
Summarize the overall customer sentiment and opinion about the product.
"""
    
    return prompt

def analyze_reviews_with_gemini(reviews_batch: List[Dict]) -> str:
    """Send a batch of reviews to Gemini API and get analysis."""
    # Create the prompt
    prompt = create_gemini_prompt(reviews_batch)
    
    # Initialize the model
    model = GenerativeModel(
        model_name="gemini-1.5-flash",
    )
    
    # Send request to Gemini API
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return f"Error: Could not analyze reviews - {str(e)}"

def process_reviews_in_batches(df: pd.DataFrame, batch_size: int = 20) -> List[Dict]:
    """Process all reviews in batches and collect Gemini analyses."""
    reviews_data = df.to_dict('records')
    analyses = []
    
    print(f"Processing {len(reviews_data)} reviews in batches of {batch_size}")
    
    # Process reviews in batches
    for i in range(0, len(reviews_data), batch_size):
        batch = reviews_data[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(reviews_data) + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} reviews)")
        
        # Analyze batch with Gemini
        analysis = analyze_reviews_with_gemini(batch)
        analyses.append({
            'batch_number': batch_num,
            'review_count': len(batch),
            'reviews_range': f"{i+1}-{min(i+len(batch), len(reviews_data))}",
            'analysis': analysis
        })
        
        # Add delay to respect API rate limits
        if i + batch_size < len(reviews_data):
            print("Waiting 2 seconds before next batch...")
            time.sleep(2)
    
    return analyses

def save_analyses(analyses: List[Dict], output_file: Optional[str] = None):
    """Save the analyses to a JSON file."""
    if output_file is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"scraped_data/gemini_review_analyses_{timestamp}.json"
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False)
    
    print(f"Analyses saved to: {output_file}")
    return output_file

def create_summary_report(analyses: List[Dict]) -> str:
    """Create a summary report combining all batch analyses."""
    report = "GOOGLE GEMINI PRODUCT REVIEW ANALYSIS SUMMARY\n"
    report += "=" * 50 + "\n\n"
    
    report += f"Total Batches Processed: {len(analyses)}\n"
    report += f"Total Reviews Analyzed: {sum(a['review_count'] for a in analyses)}\n\n"
    
    report += "BATCH ANALYSES:\n"
    report += "-" * 20 + "\n\n"
    
    for analysis in analyses:
        report += f"Batch {analysis['batch_number']} (Reviews {analysis['reviews_range']}):\n"
        report += analysis['analysis'] + "\n\n"
        report += "-" * 50 + "\n\n"
    
    return report

def save_summary_report(report: str, output_file: Optional[str] = None):
    """Save the summary report to a text file."""
    if output_file is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"scraped_data/gemini_analysis_summary_{timestamp}.txt"
    
    # Save to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Summary report saved to: {output_file}")
    return output_file

def main():
    """Main function to run the Gemini review analysis."""
    print("GOOGLE GEMINI PRODUCT REVIEW ANALYZER")
    print("=" * 50)
    
    try:
        # Load reviews data
        df = load_reviews_data()
        
        # Process reviews in batches
        analyses = process_reviews_in_batches(df, batch_size=20)
        
        # Save individual analyses
        json_file = save_analyses(analyses)
        
        # Create and save summary report
        summary_report = create_summary_report(analyses)
        txt_file = save_summary_report(summary_report)
        
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"Generated files:")
        print(f"  - {json_file}")
        print(f"  - {txt_file}")
        print("\nSample of the analysis:")
        print("-" * 30)
        if analyses:
            print(analyses[0]['analysis'][:500] + "...")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()