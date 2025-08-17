"""
Simple OAuth 2.0 Setup for Google Drive
Uses the provided credentials JSON format
"""
import requests
from urllib.parse import urlencode
import webbrowser
import json

# Your credentials from the JSON - Replace with your actual values
CREDENTIALS = {
    "client_id": "YOUR_GOOGLE_CLIENT_ID_HERE",
    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET_HERE",
    "project_id": "maueyecare"
}

def get_oauth_token():
    """Get OAuth token using installed app flow"""
    
    print("🔐 Google Drive OAuth Setup")
    print("=" * 40)
    
    # Step 1: Create authorization URL
    auth_params = {
        'client_id': CREDENTIALS['client_id'],
        'redirect_uri': 'https://maueyecare.streamlit.app',
        'scope': 'https://www.googleapis.com/auth/drive.file',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(auth_params)
    
    print("\n1. Opening Google authorization page...")
    print(f"URL: {auth_url}")
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened")
    except:
        print("⚠️ Please copy the URL above and open in browser")
    
    print("\n2. Steps to follow:")
    print("   - Sign in to your Google account")
    print("   - Click 'Allow' to authorize the app")
    print("   - You'll be redirected to: https://maueyecare.streamlit.app")
    print("   - Copy the 'code' parameter from the URL")
    print("   - Example: https://maueyecare.streamlit.app/?code=4/0AX4XfWh...")
    
    # Get authorization code
    print("\n3. Copy the code from the redirected URL:")
    print("   - Look for ?code=... in the URL")
    print("   - Copy everything after 'code=' (before any &)")
    auth_code = input("Paste authorization code: ").strip()
    
    # Step 2: Exchange code for tokens
    print("\n4. Getting tokens...")
    
    token_data = {
        'client_id': CREDENTIALS['client_id'],
        'client_secret': CREDENTIALS['client_secret'],
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'https://maueyecare.streamlit.app'
    }
    
    try:
        response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            
            print("\n✅ SUCCESS! Your OAuth tokens:")
            print("=" * 40)
            print(f"Access Token: {tokens.get('access_token', 'Not found')[:50]}...")
            print(f"Refresh Token: {tokens.get('refresh_token', 'Not found')}")
            
            print("\n📝 Update your .streamlit/secrets.toml:")
            print("=" * 40)
            print(f'GOOGLE_CLIENT_ID = "{CREDENTIALS["client_id"]}"')
            print(f'GOOGLE_CLIENT_SECRET = "{CREDENTIALS["client_secret"]}"')
            print(f'GOOGLE_REFRESH_TOKEN = "{tokens.get("refresh_token", "")}"')
            
            # Test the token
            print("\n🧪 Testing token...")
            test_response = requests.get(
                'https://www.googleapis.com/drive/v3/about?fields=user',
                headers={'Authorization': f'Bearer {tokens.get("access_token")}'}
            )
            
            if test_response.status_code == 200:
                user_info = test_response.json()
                print(f"✅ Token works! Connected as: {user_info.get('user', {}).get('displayName', 'Unknown')}")
            else:
                print(f"⚠️ Token test failed: {test_response.status_code}")
            
            return tokens
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_oauth_token()