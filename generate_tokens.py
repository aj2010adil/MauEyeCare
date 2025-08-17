#!/usr/bin/env python3
"""
Google Drive Token Generator for MauEyeCare
Run this script to get your refresh token
"""

import json
import webbrowser
from urllib.parse import urlencode, parse_qs
import requests

# Your credentials
CLIENT_ID = "641133812410-phlnghc1fau2gjt3e7m73sm5ec7n0s6v.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080"
SCOPES = "https://www.googleapis.com/auth/drive"

def get_auth_url():
    """Generate authorization URL"""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return auth_url

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for tokens"""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'code': auth_code
    }
    
    response = requests.post(token_url, data=data)
    return response.json()

def main():
    print("🔑 MauEyeCare Google Drive Token Generator")
    print("=" * 50)
    
    # Step 1: Get authorization URL
    auth_url = get_auth_url()
    print(f"\n1. Opening browser to authorize access...")
    print(f"   URL: {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Step 2: Get authorization code
    print(f"\n2. After authorization, you'll be redirected to:")
    print(f"   {REDIRECT_URI}?code=AUTHORIZATION_CODE")
    print(f"\n3. Copy the 'code' parameter from the URL and paste it below:")
    
    auth_code = input("\nEnter authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided!")
        return
    
    # Step 3: Exchange code for tokens
    print("\n4. Exchanging code for tokens...")
    
    try:
        tokens = exchange_code_for_tokens(auth_code)
        
        if 'error' in tokens:
            print(f"❌ Error: {tokens['error']}")
            print(f"   Description: {tokens.get('error_description', 'Unknown error')}")
            return
        
        # Step 4: Display results
        print("\n✅ SUCCESS! Here are your tokens:")
        print("=" * 50)
        
        refresh_token = tokens.get('refresh_token')
        access_token = tokens.get('access_token')
        
        print(f"🔑 Refresh Token: {refresh_token}")
        print(f"🔓 Access Token: {access_token}")
        
        # Step 5: Create Streamlit secrets format
        print("\n📝 Streamlit Cloud Secrets Configuration:")
        print("=" * 50)
        print("[google_drive]")
        print(f'client_id = "{CLIENT_ID}"')
        print(f'client_secret = "{CLIENT_SECRET}"')
        print(f'refresh_token = "{refresh_token}"')
        print('folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"')
        
        print("\n📋 Next Steps:")
        print("1. Create a folder in Google Drive named 'MauEyeCare Prescriptions'")
        print("2. Copy the folder ID from the URL")
        print("3. Replace 'YOUR_GOOGLE_DRIVE_FOLDER_ID' with the actual folder ID")
        print("4. Add this configuration to Streamlit Cloud secrets")
        
        # Save to file
        config = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
            "access_token": access_token
        }
        
        with open("google_tokens.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Tokens saved to: google_tokens.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()