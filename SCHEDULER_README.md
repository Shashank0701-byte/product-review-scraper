# Product Review Analysis Scheduler

This scheduler automates the entire product review analysis workflow using APScheduler.

## Features

1. **Weekly Review Scraping**: Automatically scrapes new reviews from the configured product URL
2. **AI Analysis**: Runs Gemini AI analysis on the scraped reviews
3. **Report Generation**: Creates comprehensive business intelligence reports
4. **Email Notifications**: Optionally sends the latest report via email

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Product URL**:
   Edit the [review_analysis_scheduler.py](file:///D:/Python%20Projeccts/Product%20Review%20Scraper/review_analysis_scheduler.py) file and update the `PRODUCT_URL` variable with your target product URL.

3. **Email Configuration** (Optional):
   When you first run the scheduler, it will create an `email_config.json` template file. Update this file with your email settings:
   ```json
   {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "your_email@gmail.com",
       "sender_password": "your_app_password",
       "recipient_email": "recipient@example.com"
   }
   ```

## Usage

### Run the Scheduler

```bash
python review_analysis_scheduler.py
```

The scheduler will:
1. Immediately run a full analysis cycle
2. Schedule weekly runs every Sunday at 2:00 AM

### Manual Execution

To run just the analysis workflow once without scheduling:
```bash
python review_analysis_scheduler.py
```

## How It Works

1. **Scraping**: Uses the existing `run_scraper.py` script to scrape reviews
2. **AI Analysis**: Executes `gemini_review_analyzer.py` for AI-powered theme analysis
3. **Report Generation**: Runs `business_intelligence_report.py` to create PDF reports
4. **Email Notification**: Sends the latest report via SMTP if configured

## Customization

### Schedule Timing
Edit the cron expression in [review_analysis_scheduler.py](file:///D:/Python%20Projeccts/Product%20Review%20Scraper/review_analysis_scheduler.py):
```python
# Currently set to run every Sunday at 2:00 AM
CronTrigger(day_of_week='sun', hour=2, minute=0)
```

### Product URL
Update the `PRODUCT_URL` variable in [review_analysis_scheduler.py](file:///D:/Python%20Projeccts/Product%20Review%20Scraper/review_analysis_scheduler.py) with your target product.

### Review Count
Adjust the `MAX_REVIEWS` variable to change how many reviews to scrape.

## Logging

All operations are logged to `scheduler.log` with timestamps for monitoring and debugging.

## Troubleshooting

1. **Email Issues**: Ensure your SMTP settings are correct and your password is an app password (not your regular password for Gmail)
2. **Scraping Issues**: Check that the product URL is accessible and the scraper works manually
3. **AI Analysis Issues**: Verify your Google Gemini API key is valid and properly configured