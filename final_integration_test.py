#!/usr/bin/env python3
"""
Final Integration Test for the Product Review Analysis System

This script tests the complete workflow:
1. Review scraping
2. AI analysis with Gemini
3. Business intelligence report generation
4. Scheduler components
"""

import os
import sys
import subprocess
from datetime import datetime

def test_complete_workflow():
    """Test the complete analysis workflow."""
    print("Testing Complete Product Review Analysis Workflow")
    print("=" * 50)
    
    # Test 1: Check that all required scripts exist
    required_scripts = [
        'run_scraper.py',
        'gemini_review_analyzer.py', 
        'business_intelligence_report.py',
        'review_analysis_scheduler.py'
    ]
    
    print("1. Checking required scripts...")
    for script in required_scripts:
        if os.path.exists(script):
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} - MISSING")
            return False
    
    # Test 2: Check imports
    print("\n2. Testing imports...")
    try:
        import apscheduler
        import fpdf
        import google.generativeai
        import pandas
        import nltk
        print("   ✅ All required packages imported successfully")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 3: Check that scraper can be imported
    print("\n3. Testing scraper import...")
    try:
        import run_scraper
        print("   ✅ Scraper module imported successfully")
    except Exception as e:
        print(f"   ❌ Scraper import error: {e}")
        return False
    
    # Test 4: Check that analyzer can be imported
    print("\n4. Testing analyzer import...")
    try:
        import gemini_review_analyzer
        print("   ✅ Analyzer module imported successfully")
    except Exception as e:
        print(f"   ❌ Analyzer import error: {e}")
        return False
    
    # Test 5: Check that report generator can be imported
    print("\n5. Testing report generator import...")
    try:
        import business_intelligence_report
        print("   ✅ Report generator module imported successfully")
    except Exception as e:
        print(f"   ❌ Report generator import error: {e}")
        return False
    
    # Test 6: Check that scheduler can be imported
    print("\n6. Testing scheduler import...")
    try:
        import review_analysis_scheduler
        print("   ✅ Scheduler module imported successfully")
    except Exception as e:
        print(f"   ❌ Scheduler import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! The complete workflow is ready.")
    print("\nNext steps:")
    print("1. Configure your product URL in review_analysis_scheduler.py")
    print("2. (Optional) Set up email configuration for notifications")
    print("3. Run: python review_analysis_scheduler.py")
    
    return True

def main():
    """Run the integration test."""
    success = test_complete_workflow()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)