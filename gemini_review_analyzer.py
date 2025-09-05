#!/usr/bin/env python3
"""
AI Summarization & Sentiment Analysis Engine

This is the most powerful feature that takes your project from a data collector to a
decision-making tool. After scraping all the reviews for a product, this script feeds
the entire collection of raw text into Google Gemini AI model to generate structured
JSON analysis with:

- overall_sentiment_score: An integer from 0-100
- key_positives: Array of top 3-5 things customers consistently loved
- key_negatives: Array of top 3-5 complaints or issues
- feature_requests: Array of features customers wish the product had
- executive_summary: A short, professional paragraph summarizing overall opinion
"""

import pandas as pd
import time
import json
import os
from typing import List, Dict, Optional
import warnings
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Import Google Generative AI
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    from google.generativeai.generative_models import GenerativeModel
except ImportError as e:
    print(f"Error importing Google Generative AI: {e}")
    print("Please install it with: pip install google-generativeai")
    exit(1)

# Configure Gemini API from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables")
    print("Please set your API key in the .env file")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Generation configuration for JSON output
generation_config = GenerationConfig(
    temperature=0.3,  # Lower temperature for more consistent JSON
    top_p=0.8,
    top_k=40,
    max_output_tokens=4096,
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

def create_structured_analysis_prompt(all_reviews: str, product_name: str = "this product") -> str:
    """Create the 'magic' prompt for structured AI analysis."""
    prompt = f"""You are an expert market research analyst. I have provided you with hundreds of customer reviews for {product_name}. Your task is to analyze them and provide a structured JSON summary with the following keys:

- overall_sentiment_score: An integer from 0-100 (0=very negative, 50=neutral, 100=very positive)
- key_positives: An array of the top 3-5 things customers consistently loved
- key_negatives: An array of the top 3-5 complaints or issues  
- feature_requests: An array of features customers wish the product had
- executive_summary: A short, professional paragraph summarizing the overall customer opinion

Here are the customer reviews to analyze:

{all_reviews}

Please respond with ONLY valid JSON in the exact format specified above. Do not include any additional text or explanations outside the JSON structure."""
    
    return prompt

def combine_all_reviews(df: pd.DataFrame) -> tuple[str, str]:
    """Combine all review texts into a single large string for AI analysis."""
    # Get product name from the first review (if available)
    product_name = "this product"
    if 'product_name' in df.columns and not df['product_name'].empty:
        product_name = df['product_name'].iloc[0]
    
    # Combine all cleaned reviews into one string
    all_reviews = []
    for _, row in df.iterrows():
        review_text = row.get('cleaned_review', row.get('review_text', ''))
        rating = row.get('rating', 'N/A')
        if pd.notna(review_text) and review_text.strip():
            all_reviews.append(f"Rating: {rating}/5 - {review_text.strip()}")
    
    combined_reviews = "\n\n".join(all_reviews)
    print(f"Combined {len(all_reviews)} reviews into analysis string")
    
    return combined_reviews, product_name

def analyze_with_ai_engine(all_reviews: str, product_name: str) -> Dict:
    """Send all reviews to Gemini AI and get structured JSON analysis."""
    # Create the structured analysis prompt
    prompt = create_structured_analysis_prompt(all_reviews, product_name)
    
    # Initialize the model
    model = GenerativeModel(
        model_name="gemini-1.5-flash",
    )
    
    print("Sending reviews to AI Summarization Engine...")
    
    # Send request to Gemini API
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Parse the JSON response
        json_text = response.text.strip()
        
        # Clean up the response in case there are markdown code blocks
        if json_text.startswith('```json'):
            json_text = json_text[7:]
        if json_text.startswith('```'):
            json_text = json_text[3:]
        if json_text.endswith('```'):
            json_text = json_text[:-3]
        
        # Parse JSON
        analysis_result = json.loads(json_text.strip())
        
        # Validate the required fields
        required_fields = ['overall_sentiment_score', 'key_positives', 'key_negatives', 'feature_requests', 'executive_summary']
        for field in required_fields:
            if field not in analysis_result:
                raise ValueError(f"Missing required field: {field}")
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response.text}")
        return {
            "error": "Failed to parse AI response as JSON",
            "raw_response": response.text,
            "overall_sentiment_score": 50,
            "key_positives": ["Error in analysis"],
            "key_negatives": ["Failed to process reviews"],
            "feature_requests": [],
            "executive_summary": "Analysis failed due to JSON parsing error."
        }
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return {
            "error": f"API call failed: {str(e)}",
            "overall_sentiment_score": 50,
            "key_positives": ["Error in analysis"],
            "key_negatives": ["Failed to process reviews"],
            "feature_requests": [],
            "executive_summary": "Analysis failed due to API error."
        }

def save_structured_analysis(analysis_result: Dict, product_name: str, total_reviews: int) -> str:
    """Save the structured analysis result to JSON file."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"scraped_data/ai_analysis_structured_{timestamp}.json"
    
    # Add metadata to the analysis
    full_result = {
        "analysis_metadata": {
            "product_name": product_name,
            "total_reviews_analyzed": total_reviews,
            "analysis_timestamp": timestamp,
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analyzer_version": "AI Summarization & Sentiment Analysis Engine v2.0"
        },
        "structured_analysis": analysis_result
    }
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_result, f, indent=2, ensure_ascii=False)
    
    print(f"Structured analysis saved to: {output_file}")
    return output_file

def create_executive_summary_report(analysis_result: Dict, product_name: str, total_reviews: int) -> str:
    """Create a human-readable executive summary report."""
    report = "AI SUMMARIZATION & SENTIMENT ANALYSIS REPORT\n"
    report += "=" * 55 + "\n\n"
    
    report += f"Product: {product_name}\n"
    report += f"Total Reviews Analyzed: {total_reviews:,}\n"
    report += f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Overall Sentiment Score
    sentiment_score = analysis_result.get('overall_sentiment_score', 0)
    report += f"OVERALL SENTIMENT SCORE: {sentiment_score}/100\n"
    
    if sentiment_score >= 80:
        sentiment_label = "VERY POSITIVE 😊"
    elif sentiment_score >= 60:
        sentiment_label = "POSITIVE 👍"
    elif sentiment_score >= 40:
        sentiment_label = "NEUTRAL 😐"
    elif sentiment_score >= 20:
        sentiment_label = "NEGATIVE 👎"
    else:
        sentiment_label = "VERY NEGATIVE 😞"
    
    report += f"Sentiment Level: {sentiment_label}\n\n"
    
    # Key Positives
    report += "KEY POSITIVES (What Customers Love):\n"
    report += "-" * 40 + "\n"
    key_positives = analysis_result.get('key_positives', [])
    for i, positive in enumerate(key_positives, 1):
        report += f"{i}. {positive}\n"
    report += "\n"
    
    # Key Negatives
    report += "KEY NEGATIVES (Customer Complaints):\n"
    report += "-" * 40 + "\n"
    key_negatives = analysis_result.get('key_negatives', [])
    for i, negative in enumerate(key_negatives, 1):
        report += f"{i}. {negative}\n"
    report += "\n"
    
    # Feature Requests
    report += "FEATURE REQUESTS (What Customers Want):\n"
    report += "-" * 40 + "\n"
    feature_requests = analysis_result.get('feature_requests', [])
    if feature_requests:
        for i, request in enumerate(feature_requests, 1):
            report += f"{i}. {request}\n"
    else:
        report += "No specific feature requests identified.\n"
    report += "\n"
    
    # Executive Summary
    report += "EXECUTIVE SUMMARY:\n"
    report += "-" * 20 + "\n"
    executive_summary = analysis_result.get('executive_summary', 'No summary available.')
    report += f"{executive_summary}\n\n"
    
    report += "=" * 55 + "\n"
    report += "Report generated by AI Summarization & Sentiment Analysis Engine\n"
    
    return report

def save_executive_report(report: str) -> str:
    """Save the executive summary report to a text file."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"scraped_data/ai_executive_report_{timestamp}.txt"
    
    # Save to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Executive report saved to: {output_file}")
    return output_file

def main():
    """Main function to run the AI Summarization & Sentiment Analysis Engine."""
    print("AI SUMMARIZATION & SENTIMENT ANALYSIS ENGINE")
    print("=" * 55)
    print("Transforming your data from collection to decision-making tool")
    print("=" * 55)
    
    try:
        # Load reviews data
        df = load_reviews_data()
        
        # Step 1: Combine all review texts into a single large string
        print("\n[STEP 1] Combining all review texts into analysis string...")
        all_reviews, product_name = combine_all_reviews(df)
        
        # Step 2: Create sophisticated prompt and send to AI
        print("\n[STEP 2] Creating sophisticated prompt for AI analysis...")
        print("[STEP 3] Feeding reviews into powerful GenAI model (Google Gemini)...")
        analysis_result = analyze_with_ai_engine(all_reviews, product_name)
        
        # Step 3: Save AI's structured JSON response
        print("\n[STEP 4] Saving AI's structured JSON response...")
        json_file = save_structured_analysis(analysis_result, product_name, len(df))
        
        # Step 4: Create executive summary report
        print("\n[STEP 5] Creating executive summary report...")
        executive_report = create_executive_summary_report(analysis_result, product_name, len(df))
        txt_file = save_executive_report(executive_report)
        
        # Display results
        print("\n" + "=" * 55)
        print("AI ANALYSIS COMPLETE - DECISION-READY INSIGHTS")
        print("=" * 55)
        print(f"Generated files:")
        print(f"  \u2713 {json_file}")
        print(f"  \u2713 {txt_file}")
        
        print("\n" + "-" * 55)
        print("QUICK PREVIEW OF YOUR STRUCTURED ANALYSIS:")
        print("-" * 55)
        
        if 'error' not in analysis_result:
            print(f"Overall Sentiment Score: {analysis_result.get('overall_sentiment_score', 0)}/100")
            print(f"\nTop Positives ({len(analysis_result.get('key_positives', []))}):") 
            for i, pos in enumerate(analysis_result.get('key_positives', [])[:3], 1):
                print(f"  {i}. {pos}")
            
            print(f"\nTop Negatives ({len(analysis_result.get('key_negatives', []))}):") 
            for i, neg in enumerate(analysis_result.get('key_negatives', [])[:3], 1):
                print(f"  {i}. {neg}")
            
            feature_requests = analysis_result.get('feature_requests', [])
            if feature_requests:
                print(f"\nFeature Requests ({len(feature_requests)}):")
                for i, req in enumerate(feature_requests[:2], 1):
                    print(f"  {i}. {req}")
            
            print(f"\nExecutive Summary:")
            summary = analysis_result.get('executive_summary', '')[:200]
            print(f"  {summary}{'...' if len(analysis_result.get('executive_summary', '')) > 200 else ''}")
        else:
            print(f"\u26a0\ufe0f  Analysis encountered an issue: {analysis_result.get('error', 'Unknown error')}")
            
        print("\n" + "=" * 55)
        print("\u2728 Your product reviews have been transformed into actionable business intelligence!")
        
    except Exception as e:
        print(f"\u274c Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()