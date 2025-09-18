#!/usr/bin/env python3
"""
Test Google Sheets Connection
Simple script to test if Google Sheets API is working
"""

import requests
import pandas as pd
from datetime import datetime

def test_google_sheets_connection():
    """Test connection to Google Sheets"""
    
    # Configuration
    API_KEY = "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
    SHEET_ID = "1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ"
    
    print("🔍 Testing Google Sheets Connection...")
    print(f"📊 Sheet ID: {SHEET_ID}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print("-" * 50)
    
    # Test sheets to check
    test_sheets = ["Medicines", "Spectacles", "Patients", "Prescriptions", "Analytics"]
    
    results = {}
    
    for sheet_name in test_sheets:
        try:
            print(f"📋 Testing {sheet_name} sheet...")
            
            # Method 1: Using Google Sheets API v4
            api_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_name}!A:Z?key={API_KEY}"
            
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                
                if values:
                    headers = values[0] if values else []
                    data_rows = values[1:] if len(values) > 1 else []
                    
                    print(f"  ✅ Success: {len(data_rows)} rows, {len(headers)} columns")
                    print(f"  📝 Headers: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
                    
                    results[sheet_name] = {
                        'status': 'success',
                        'rows': len(data_rows),
                        'columns': len(headers),
                        'headers': headers
                    }
                else:
                    print(f"  ⚠️  Sheet exists but no data found")
                    results[sheet_name] = {
                        'status': 'empty',
                        'rows': 0,
                        'columns': 0,
                        'headers': []
                    }
            
            elif response.status_code == 400:
                print(f"  ❌ Sheet '{sheet_name}' not found or invalid range")
                results[sheet_name] = {
                    'status': 'not_found',
                    'error': 'Sheet not found'
                }
            
            elif response.status_code == 403:
                print(f"  ❌ Access denied - check API key and sheet permissions")
                results[sheet_name] = {
                    'status': 'access_denied',
                    'error': 'Access denied'
                }
            
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
                results[sheet_name] = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                }
        
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results[sheet_name] = {
                'status': 'exception',
                'error': str(e)
            }
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    successful_sheets = [name for name, result in results.items() if result['status'] == 'success']
    empty_sheets = [name for name, result in results.items() if result['status'] == 'empty']
    failed_sheets = [name for name, result in results.items() if result['status'] not in ['success', 'empty']]
    
    print(f"✅ Successful: {len(successful_sheets)} sheets")
    for sheet in successful_sheets:
        result = results[sheet]
        print(f"   • {sheet}: {result['rows']} rows, {result['columns']} columns")
    
    if empty_sheets:
        print(f"⚠️  Empty: {len(empty_sheets)} sheets")
        for sheet in empty_sheets:
            print(f"   • {sheet}: Sheet exists but no data")
    
    if failed_sheets:
        print(f"❌ Failed: {len(failed_sheets)} sheets")
        for sheet in failed_sheets:
            result = results[sheet]
            print(f"   • {sheet}: {result.get('error', 'Unknown error')}")
    
    print()
    
    # Overall status
    if len(successful_sheets) >= 2:  # At least 2 sheets working
        print("🎉 OVERALL STATUS: GOOD - Google Sheets integration is working!")
        print("💡 You can read data from Google Sheets successfully")
        
        if failed_sheets:
            print("📝 NOTE: Some sheets need to be created or fixed")
            print("🔧 Create missing sheets using the templates in the app")
    
    elif len(successful_sheets) + len(empty_sheets) >= 2:
        print("⚠️  OVERALL STATUS: PARTIAL - Connection works but sheets need data")
        print("📝 Create the required sheets and add sample data")
    
    else:
        print("❌ OVERALL STATUS: FAILED - Google Sheets integration not working")
        print("🔧 Check:")
        print("   • API key is valid")
        print("   • Sheet ID is correct")
        print("   • Sheet is publicly accessible")
        print("   • Required sheets exist")
    
    print()
    print("🔗 Sheet URL: https://docs.google.com/spreadsheets/d/" + SHEET_ID)
    print("📅 Test completed:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return results

if __name__ == "__main__":
    test_google_sheets_connection()