#!/usr/bin/env python3
"""
Google Drive Token Generator for MauEyeCare
"""

import json
import webbrowser
from urllib.parse import urlencode
import requests

# Your credentials
CLIENT_ID = "641133812410-phlnghc1fau2gjt3e7m73sm5ec7n0s6v.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080"
SCOPES = "https://www.googleapis.com/auth/drive"

def main():
    print("MauEyeCare Google Drive Token Generator")
    print("=" * 50)
    
    # Generate authorization URL
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    print("\n1. Opening browser for Google authorization...")
    print(f"   URL: {auth_url}")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
    except:
        print("   Could not open browser automatically.")
        print("   Please copy and paste the URL above into your browser.")
    
    print(f"\n2. After authorization, you'll be redirected to:")
    print(f"   {REDIRECT_URI}?code=AUTHORIZATION_CODE")
    print(f"\n3. Copy the 'code' parameter and paste below:")
    
    auth_code = input("\nEnter authorization code: ").strip()
    
    if not auth_code:
        print("No authorization code provided!")
        return
    
    # Exchange code for tokens
    print("\n4. Getting tokens...")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'code': auth_code
    }
    
    try:
        response = requests.post(token_url, data=data)
        tokens = response.json()
        
        if 'error' in tokens:
            print(f"Error: {tokens['error']}")
            return
        
        refresh_token = tokens.get('refresh_token')
        
        print("\nSUCCESS! Your Streamlit Cloud secrets:")
        print("=" * 50)
        print("[google_drive]")
        print(f'client_id = "{CLIENT_ID}"')
        print(f'client_secret = "{CLIENT_SECRET}"')
        print(f'refresh_token = "{refresh_token}"')
        print('folder_id = "YOUR_FOLDER_ID_HERE"')
        
        print("\nNext steps:")
        print("1. Create 'MauEyeCare Prescriptions' folder in Google Drive")
        print("2. Get folder ID from URL and replace YOUR_FOLDER_ID_HERE")
        print("3. Add this to Streamlit Cloud secrets")
        
        # Save tokens
        config = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token
        }
        
        with open("tokens.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("\nTokens saved to tokens.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()