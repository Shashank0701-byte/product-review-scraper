#!/usr/bin/env python3
"""
Test script for the review analysis scheduler components
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import apscheduler
        import smtplib
        import ssl
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        print("✅ All email modules imported successfully")
    except ImportError as e:
        print(f"❌ Email module import error: {e}")
        return False
    
    try:
        import subprocess
        import json
        from datetime import datetime
        print("✅ All standard library modules imported successfully")
    except ImportError as e:
        print(f"❌ Standard library import error: {e}")
        return False
        
    return True

def test_file_access():
    """Test access to required files."""
    required_files = [
        'run_scraper.py',
        'gemini_review_analyzer.py',
        'business_intelligence_report.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Found required file: {file}")
        else:
            print(f"❌ Missing required file: {file}")
            return False
    
    return True

def test_scheduler_imports():
    """Test that APScheduler components can be imported."""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
        print("✅ APScheduler components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ APScheduler import error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Review Analysis Scheduler Components")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_file_access()
    all_passed &= test_scheduler_imports()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! The scheduler should work correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)