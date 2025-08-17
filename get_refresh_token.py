"""
Get Google OAuth 2.0 Refresh Token
Run this script to get the refresh token needed for Google Drive integration
"""
import requests
from urllib.parse import urlencode
import webbrowser

# Your OAuth credentials - Replace with your actual values
CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET_HERE"
REDIRECT_URI = "https://maueyecare.streamlit.app"

def get_refresh_token():
    """Get refresh token for Google Drive access"""
    
    # Step 1: Generate authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'https://www.googleapis.com/auth/drive.file',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(auth_params)
    
    print("🔐 Google OAuth 2.0 Setup")
    print("=" * 50)
    print("\n1. Opening authorization URL in browser...")
    print(f"   {auth_url}")
    
    # Try to open in browser
    try:
        webbrowser.open(auth_url)
        print("   ✅ Browser opened")
    except:
        print("   ⚠️ Please copy and paste the URL above into your browser")
    
    print("\n2. After authorizing:")
    print("   - You'll be redirected to: https://maueyecare.streamlit.app")
    print("   - Copy the 'code' parameter from the URL")
    print("   - Example: https://maueyecare.streamlit.app/?code=4/0AX4XfWh...")
    
    # Step 2: Get authorization code from user
    print("\n3. Copy the authorization code from the URL:")
    print("   - Look for ?code=... in the redirected URL")
    print("   - Copy everything after 'code='")
    auth_code = input("Authorization code: ").strip()
    
    # Step 3: Exchange code for tokens
    print("\n4. Exchanging code for tokens...")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            
            print("\n✅ Success! Your tokens:")
            print("=" * 50)
            print(f"Client ID: {CLIENT_ID}")
            print(f"Client Secret: {CLIENT_SECRET}")
            print(f"Refresh Token: {tokens.get('refresh_token')}")
            print(f"Access Token: {tokens.get('access_token')[:50]}...")
            
            print("\n📝 Add these to .streamlit/secrets.toml:")
            print("=" * 50)
            print(f'GOOGLE_CLIENT_ID = "{CLIENT_ID}"')
            print(f'GOOGLE_CLIENT_SECRET = "{CLIENT_SECRET}"')
            print(f'GOOGLE_REFRESH_TOKEN = "{tokens.get("refresh_token")}"')
            
            return tokens
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_refresh_token()