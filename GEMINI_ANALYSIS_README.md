# Google Gemini Product Review Analyzer

This directory contains a Python script that sends batches of product reviews to Google Gemini API for advanced analysis, generating structured summaries with Top Positive Themes, Top Negative Themes, and Overall Customer Opinion.

## Features

The Gemini review analyzer script performs the following:

1. **Batch Processing** - Sends reviews to Gemini API in batches (default: 20 reviews per request)
2. **Structured Analysis** - Requests specific analysis sections:
   - Top Positive Themes
   - Top Negative Themes
   - Overall Customer Opinion
3. **Rate Limit Compliance** - Includes delays between API calls to respect rate limits
4. **Comprehensive Output** - Generates both JSON and text summary reports
5. **Error Handling** - Gracefully handles API errors and connection issues

## Requirements

The analyzer script requires the following Python packages:
- pandas
- google-generativeai

Install requirements with:
```bash
pip install pandas google-generativeai
```

## Setup

1. Ensure you have a Google Gemini API key
2. The script is preconfigured with the provided API key, but in production you should:
   - Use environment variables: `export GEMINI_API_KEY="your_api_key"`
   - Or store in a secure configuration file

## Usage

Run the analyzer script from the project root directory:

```bash
python gemini_review_analyzer.py
```

The script will automatically:
1. Load the most recent processed reviews CSV file from `scraped_data/`
2. Process reviews in batches of 20
3. Send each batch to Google Gemini API for analysis
4. Generate and save comprehensive reports to `scraped_data/`

## Output Files

The script generates two types of output files in the `scraped_data/` directory:

1. **JSON Analysis File** - Contains detailed analysis for each batch:
   - `gemini_review_analyses_TIMESTAMP.json`

2. **Text Summary Report** - Combined analysis in readable format:
   - `gemini_analysis_summary_TIMESTAMP.txt`

## Sample Output Structure

### JSON Analysis
```json
[
  {
    "batch_number": 1,
    "review_count": 20,
    "reviews_range": "1-20",
    "analysis": "Gemini's detailed analysis of the reviews..."
  }
]
```

### Text Summary Report
```
GOOGLE GEMINI PRODUCT REVIEW ANALYSIS SUMMARY
==================================================

Total Batches Processed: 3
Total Reviews Analyzed: 50

BATCH ANALYSES:
--------------------

Batch 1 (Reviews 1-20):
1. Top Positive Themes
   - Theme 1: Description
   - Theme 2: Description

2. Top Negative Themes
   - Theme 1: Description
   - Theme 2: Description

3. Overall Customer Opinion
   Summary of customer sentiment...
```

## Customization

To customize the analysis:

1. **Batch Size**: Modify the `batch_size` parameter in `process_reviews_in_batches()`
2. **Prompt**: Edit the `create_gemini_prompt()` function to change the analysis request
3. **Model**: Change the model in `analyze_reviews_with_gemini()` (e.g., "gemini-1.5-pro")
4. **Generation Config**: Adjust parameters in `generation_config`

## Rate Limits and Costs

Google Gemini API has rate limits and usage costs:
- Free tier available with limited requests
- Paid usage beyond free tier
- Script includes 2-second delays between batches to respect rate limits

## Error Handling

The script includes error handling for:
- API connection issues
- Rate limiting
- Invalid responses
- File I/O errors

If errors occur, they will be logged and the script will continue processing remaining batches.