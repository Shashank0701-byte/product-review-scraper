# Business Intelligence Report Generator

This directory contains a Python script that generates comprehensive business intelligence reports combining all analysis results into a single PDF document with actionable insights.

## Features

The business intelligence report generator combines:

1. **Rating Statistics** - Average rating, distribution, and detailed metrics
2. **Sentiment Analysis** - VADER sentiment distribution (Positive, Neutral, Negative)
3. **AI-Powered Themes** - Key themes extracted from Google Gemini analysis
4. **Business Insights** - Executive summary, pros, cons, and recommendations
5. **Professional PDF Output** - Formatted report with all key information

## Report Sections

The generated PDF report includes:

1. **Executive Summary** - High-level overview of findings
2. **Rating Statistics** - Detailed numerical analysis
3. **Sentiment Analysis** - Distribution of customer sentiment
4. **Product Strengths (Pros)** - Key positive themes from AI analysis
5. **Areas for Improvement (Cons)** - Key negative themes from AI analysis
6. **Business Recommendations** - Actionable insights for improvement

## Requirements

The report generator requires the following Python packages:
- pandas
- fpdf2
- matplotlib
- seaborn

Install requirements with:
```bash
pip install pandas fpdf2 matplotlib seaborn
```

## Usage

Run the report generator from the project root directory:

```bash
python business_intelligence_report.py
```

The script will automatically:
1. Load the most recent processed reviews data
2. Incorporate VADER sentiment analysis results
3. Include Google Gemini AI theme analysis
4. Generate a comprehensive PDF report
5. Save the report to `scraped_data/business_intelligence_report_TIMESTAMP.pdf`

## Output

The script generates a professional PDF report with:
- Executive summary of key findings
- Detailed rating statistics
- Sentiment distribution analysis
- AI-extracted key themes
- Business recommendations
- Professional formatting and layout

## Customization

To customize the report:

1. **Modify Sections**: Edit the section creation methods in the class
2. **Add Visualizations**: Include charts and graphs in the PDF
3. **Change Layout**: Adjust fonts, spacing, and formatting in the PDF generation
4. **Add Data Sources**: Include additional data sources in the analysis

## Sample Report Structure

```
Product Review Business Intelligence Report
==========================================

Executive Summary
- Average rating and key metrics
- Overall sentiment overview
- AI insights summary

Rating Statistics
- Average: 4.2/5.0
- Distribution: 5-star (45%), 4-star (35%), etc.

Sentiment Analysis
- Positive: 75% (45 reviews)
- Neutral: 15% (9 reviews)
- Negative: 10% (6 reviews)

Product Strengths (Pros)
- Performance and speed
- Build quality
- Feature set

Areas for Improvement (Cons)
- Pricing concerns
- Specific feature issues

Business Recommendations
- Maintain quality focus
- Address pricing perception
- Leverage positive feedback
```

## Integration with Other Tools

The report generator integrates with:
- VADER sentiment analysis results
- Google Gemini AI theme analysis
- All processed review data
- Existing visualization files

This creates a comprehensive business intelligence solution that transforms raw review data into actionable business insights.