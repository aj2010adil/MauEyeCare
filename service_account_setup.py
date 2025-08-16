"""
Service Account Setup for Google Drive
Simpler alternative to OAuth - no user authorization needed
"""
import json

def create_service_account_guide():
    """Guide to create service account for Google Drive"""
    
    print("🔧 Google Drive Service Account Setup")
    print("=" * 50)
    print("\nService Account is easier than OAuth - no user authorization needed!")
    
    print("\n📋 Steps to create Service Account:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Select project: maueyecare")
    print("3. Go to IAM & Admin > Service Accounts")
    print("4. Click 'Create Service Account'")
    print("5. Name: 'maueyecare-drive-service'")
    print("6. Click 'Create and Continue'")
    print("7. Skip roles (click 'Continue')")
    print("8. Click 'Done'")
    
    print("\n🔑 Get Service Account Key:")
    print("1. Click on the created service account")
    print("2. Go to 'Keys' tab")
    print("3. Click 'Add Key' > 'Create new key'")
    print("4. Choose 'JSON' format")
    print("5. Download the JSON file")
    
    print("\n📁 Share Google Drive Folder:")
    print("1. Open your Google Drive folder:")
    print("   https://drive.google.com/drive/folders/1S5-ts47Nc_vw56YfwV-AZvXyk1VJbLLO")
    print("2. Right-click > Share")
    print("3. Add the service account email (from JSON file)")
    print("4. Give 'Editor' permission")
    print("5. Click 'Send'")
    
    print("\n💾 Save JSON Key:")
    print("1. Save the downloaded JSON file as:")
    print("   d:\\MauEyeCare\\MauEyeCare\\MauEyeCare\\service-account-key.json")
    print("2. Add to .gitignore to keep it secure")
    
    print("\n✅ After setup, Google Drive uploads will work automatically!")
    print("No user authorization needed - just the service account key.")

if __name__ == "__main__":
    create_service_account_guide()