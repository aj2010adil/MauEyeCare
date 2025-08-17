#!/usr/bin/env python3
"""
Google Drive Token Generator - Simple Version
Uses urn:ietf:wg:oauth:2.0:oob for desktop apps
"""

import json
import webbrowser
from urllib.parse import urlencode
import requests

# Your credentials
CLIENT_ID = "641133812410-phlnghc1fau2gjt3e7m73sm5ec7n0s6v.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # For desktop apps
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
    
    print("\n1. Copy this URL and open in browser:")
    print(f"{auth_url}")
    
    print("\n2. After authorization, Google will show you an authorization code")
    print("3. Copy that code and paste it below:")
    
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
            print(f"Description: {tokens.get('error_description', '')}")
            return
        
        refresh_token = tokens.get('refresh_token')
        
        if not refresh_token:
            print("No refresh token received. Try again with prompt=consent")
            return
        
        print("\nSUCCESS! Your Streamlit Cloud secrets:")
        print("=" * 50)
        print("[google_drive]")
        print(f'client_id = "{CLIENT_ID}"')
        print(f'client_secret = "{CLIENT_SECRET}"')
        print(f'refresh_token = "{refresh_token}"')
        print('folder_id = "1BcDeFgHiJkLmNoPqRsTuVwXyZ"  # Replace with your folder ID')
        
        print("\nNext steps:")
        print("1. Create 'MauEyeCare Prescriptions' folder in Google Drive")
        print("2. Get folder ID from URL (the long string after /folders/)")
        print("3. Replace the folder_id value above")
        print("4. Add this entire configuration to Streamlit Cloud secrets")
        
        # Save tokens
        config = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token
        }
        
        with open("google_tokens.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\nTokens saved to google_tokens.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()