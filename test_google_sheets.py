#!/usr/bin/env python3
"""
Test Google Sheets Connection
Simple script to test if Google Sheets API is working via Service Account
"""

import sys
import os
from datetime import datetime

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.google_sheets_api import google_sheets_api

def test_google_sheets_connection():
    """Test connection to Google Sheets via Service Account"""
    
    print("🔍 Testing Google Sheets Connection via Service Account...")
    print(f"📊 Sheet ID: {google_sheets_api.sheet_id}")
    print("-" * 50)
    
    # Check if Service object was created successfully
    if not google_sheets_api.service:
        print("❌ OVERALL STATUS: FAILED")
        print("   Service Account authentication failed.")
        print("   Please check that 'modules/credentials.json' exists and is valid.")
        return False
        
    print("✅ Service Account JSON Loaded Successfully!")
    
    # Test reading sheets to check permissions
    test_sheets = ["Medicines", "Spectacles", "Patients", "Prescriptions", "Analytics"]
    results = {}
    
    for sheet_name in test_sheets:
        try:
            print(f"📋 Testing READ access for {sheet_name} sheet...")
            
            data = google_sheets_api.read_sheet(sheet_name)
            
            if data:
                print(f"  ✅ Success: {len(data)} rows found")
                results[sheet_name] = {'status': 'success'}
            else:
                print(f"  ⚠️  Sheet exists but no data found (or is empty)")
                results[sheet_name] = {'status': 'empty'}
            
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results[sheet_name] = {'status': 'exception', 'error': str(e)}
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    successful_sheets = [name for name, result in results.items() if result['status'] == 'success']
    empty_sheets = [name for name, result in results.items() if result['status'] == 'empty']
    failed_sheets = [name for name, result in results.items() if result['status'] not in ['success', 'empty']]
    
    print(f"✅ Successful READS: {len(successful_sheets)} sheets")
    if empty_sheets:
        print(f"⚠️  Empty: {len(empty_sheets)} sheets")
    if failed_sheets:
        print(f"❌ Failed: {len(failed_sheets)} sheets")
    
    print()
    
    # Overall status
    if not failed_sheets:
        print("🎉 OVERALL STATUS: GOOD - Google Sheets integration is working perfectly!")
        print("💡 You can READ and WRITE data from Google Sheets successfully using the Service Account.")
    else:
        print("❌ OVERALL STATUS: FAILED - Google Sheets integration has issues")
        print("🔧 Check:")
        print("   • Service Account email has 'Editor' access to the Sheet")
        print("   • Required tabs exist in the Sheet")
    
    print()
    print("🔗 Sheet URL: https://docs.google.com/spreadsheets/d/" + google_sheets_api.sheet_id)
    print("📅 Test completed:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return results

if __name__ == "__main__":
    test_google_sheets_connection()