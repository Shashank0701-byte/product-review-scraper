#!/usr/bin/env python3
"""
Product Review Analysis Scheduler

This script uses APScheduler to automate the entire product review analysis workflow:
1. Scrape new reviews weekly
2. Update the dataset
3. Rerun AI summarization
4. Regenerate the business intelligence report
5. Optionally send the updated PDF report via email
"""

import os
import sys
import time
import subprocess
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import json

# Configuration
PRODUCT_URL = "https://www.amazon.com/dp/B08N5WRWNW"  # Example URL, change as needed
MAX_REVIEWS = 500
EMAIL_CONFIG_FILE = "email_config.json"
LOG_FILE = "scheduler.log"

def log_message(message):
    """Log messages to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    # Print to console
    print(log_entry)
    
    # Write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def load_email_config():
    """Load email configuration from JSON file."""
    try:
        with open(EMAIL_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_message(f"Email config file {EMAIL_CONFIG_FILE} not found. Email notifications will be disabled.")
        return None
    except Exception as e:
        log_message(f"Error loading email config: {e}")
        return None

def scrape_new_reviews():
    """Scrape new reviews using the existing scraper."""
    log_message("Starting review scraping process...")
    
    try:
        # Run the scraper script
        cmd = [
            sys.executable, 'run_scraper.py',
            '--url', PRODUCT_URL,
            '--max-reviews', str(MAX_REVIEWS),
            '--format', 'csv'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            log_message("Review scraping completed successfully")
            return True
        else:
            log_message(f"Error in review scraping: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"Exception during review scraping: {e}")
        return False

def run_ai_analysis():
    """Run AI analysis on the scraped reviews."""
    log_message("Starting AI analysis process...")
    
    try:
        # Run the Gemini analyzer
        cmd = [sys.executable, 'gemini_review_analyzer.py']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            log_message("AI analysis completed successfully")
            return True
        else:
            log_message(f"Error in AI analysis: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"Exception during AI analysis: {e}")
        return False

def generate_business_report():
    """Generate the business intelligence report."""
    log_message("Generating business intelligence report...")
    
    try:
        # Run the business intelligence report generator
        cmd = [sys.executable, 'business_intelligence_report.py']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            log_message("Business report generated successfully")
            return True
        else:
            log_message(f"Error generating business report: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"Exception during report generation: {e}")
        return False

def find_latest_report():
    """Find the most recent business intelligence report."""
    try:
        files = [f for f in os.listdir('scraped_data') if f.startswith('business_intelligence_report') and f.endswith('.pdf')]
        if not files:
            return None
            
        files.sort(reverse=True)
        return os.path.join('scraped_data', files[0])
    except Exception as e:
        log_message(f"Error finding latest report: {e}")
        return None

def send_email_notification():
    """Send email with the latest report attached."""
    email_config = load_email_config()
    if not email_config:
        log_message("Email configuration not available. Skipping email notification.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['recipient_email']
        msg['Subject'] = f"Weekly Product Review Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"

        # Email body
        body = f"""
        Weekly Product Review Analysis Report
        
        This is an automated report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
        Please find the attached business intelligence report with the latest analysis.
        
        Summary of operations:
        - New reviews scraped: {MAX_REVIEWS} (target)
        - AI analysis completed: Yes
        - Report generated: Yes
        
        For any questions or concerns, please contact the system administrator.
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # Attach report
        report_path = find_latest_report()
        if report_path:
            with open(report_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_path)}'
            )
            msg.attach(part)

        # Create SMTP session
        context = ssl.create_default_context()
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls(context=context)
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], msg.as_string())
        
        log_message(f"Email sent successfully to {email_config['recipient_email']}")
        return True
        
    except Exception as e:
        log_message(f"Error sending email: {e}")
        return False

def weekly_analysis_job():
    """Main job that runs the complete analysis workflow."""
    log_message("=== STARTING WEEKLY PRODUCT REVIEW ANALYSIS ===")
    
    start_time = time.time()
    
    # Step 1: Scrape new reviews
    if not scrape_new_reviews():
        log_message("Failed to scrape new reviews. Stopping workflow.")
        return
    
    # Step 2: Run AI analysis
    if not run_ai_analysis():
        log_message("Failed to run AI analysis. Stopping workflow.")
        return
    
    # Step 3: Generate business report
    if not generate_business_report():
        log_message("Failed to generate business report. Stopping workflow.")
        return
    
    # Step 4: Send email notification (optional)
    send_email_notification()
    
    end_time = time.time()
    duration = end_time - start_time
    
    log_message(f"=== WEEKLY ANALYSIS COMPLETED SUCCESSFULLY (Duration: {duration:.2f} seconds) ===")

def create_email_config_template():
    """Create a template email configuration file."""
    template = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@example.com"
    }
    
    with open(EMAIL_CONFIG_FILE, 'w') as f:
        json.dump(template, f, indent=4)
    
    print(f"Email configuration template created: {EMAIL_CONFIG_FILE}")
    print("Please update it with your actual email settings.")

def main():
    """Main function to set up and run the scheduler."""
    print("Product Review Analysis Scheduler")
    print("=" * 40)
    
    # Check if email config exists, create template if not
    if not os.path.exists(EMAIL_CONFIG_FILE):
        create_email_config_template()
    
    # For immediate testing, run the job once
    print("\nRunning initial analysis...")
    weekly_analysis_job()
    
    # Set up scheduler for weekly execution
    scheduler = BlockingScheduler()
    
    # Schedule job to run every Sunday at 2:00 AM
    scheduler.add_job(
        weekly_analysis_job,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='weekly_analysis',
        name='Weekly Product Review Analysis',
        replace_existing=True
    )
    
    log_message("Scheduler started. Next run will be on Sunday at 2:00 AM")
    log_message("Press Ctrl+C to exit")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log_message("Scheduler stopped by user")
        print("\nScheduler stopped.")

if __name__ == "__main__":
    main()