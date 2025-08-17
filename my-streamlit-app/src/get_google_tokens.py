#!/usr/bin/env python3
"""
Google Drive Token Generator for MauEyeCare
Run this script locally to get your Google Drive API tokens
"""

import requests
import webbrowser
from urllib.parse import urlparse, parse_qs

def get_google_drive_tokens():
    """Interactive script to get Google Drive API tokens"""
    
    print("=" * 60)
    print("Google Drive API Token Generator for MauEyeCare")
    print("=" * 60)
    
    # Step 1: Get client credentials
    print("\n1. First, you need to create OAuth 2.0 credentials:")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - Create a new project or select existing")
    print("   - Enable Google Drive API")
    print("   - Go to Credentials > Create Credentials > OAuth 2.0 Client IDs")
    print("   - Choose 'Web application'")
    print("   - Add redirect URI: http://localhost:8080")
    
    client_id = input("\n2. Enter your Client ID: ").strip()
    client_secret = input("3. Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Secret are required!")
        return
    
    # Step 2: Generate authorization URL
    redirect_uri = "http://localhost:8080"
    scope = "https://www.googleapis.com/auth/drive.file"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print(f"\n4. Opening authorization URL in browser...")
    print(f"   If it doesn't open automatically, copy this URL:")
    print(f"   {auth_url}")
    
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    print("\n5. After authorization, you'll be redirected to a URL like:")
    print("   http://localhost:8080/?code=4/0AX4XfWh...")
    
    redirect_url = input("\n6. Paste the complete redirect URL here: ").strip()
    
    # Extract authorization code
    try:
        parsed_url = urlparse(redirect_url)
        auth_code = parse_qs(parsed_url.query)['code'][0]
    except:
        auth_code = input("7. Or just paste the authorization code: ").strip()
    
    if not auth_code:
        print("❌ Authorization code is required!")
        return
    
    # Step 3: Exchange code for tokens
    print("\n8. Exchanging authorization code for tokens...")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        print("\n✅ SUCCESS! Your Google Drive API tokens:")
        print("=" * 60)
        print(f"ACCESS_TOKEN = \"{tokens.get('access_token')}\"")
        print(f"REFRESH_TOKEN = \"{tokens.get('refresh_token')}\"")
        print(f"CLIENT_ID = \"{client_id}\"")
        print(f"CLIENT_SECRET = \"{client_secret}\"")
        print("=" * 60)
        
        print("\n📋 For Streamlit Cloud:")
        print("Add these to your app's secrets (Settings > Secrets):")
        print()
        print("GOOGLE_DRIVE_TOKEN = \"" + tokens.get('access_token') + "\"")
        print("GOOGLE_CLIENT_ID = \"" + client_id + "\"")
        print("GOOGLE_CLIENT_SECRET = \"" + client_secret + "\"")
        print("GOOGLE_REFRESH_TOKEN = \"" + tokens.get('refresh_token') + "\"")
        
        print("\n📁 For local development:")
        print("Add these to .streamlit/secrets.toml:")
        
        secrets_content = f"""
# Google Drive API Configuration
GOOGLE_DRIVE_TOKEN = "{tokens.get('access_token')}"
GOOGLE_CLIENT_ID = "{client_id}"
GOOGLE_CLIENT_SECRET = "{client_secret}"
GOOGLE_REFRESH_TOKEN = "{tokens.get('refresh_token')}"

# WhatsApp Business API Configuration (Optional)
WHATSAPP_ACCESS_TOKEN = "your_whatsapp_access_token_here"
WHATSAPP_PHONE_NUMBER_ID = "your_whatsapp_phone_number_id_here"
"""
        
        # Save to secrets file
        try:
            import os
            os.makedirs('.streamlit', exist_ok=True)
            
            with open('.streamlit/secrets.toml', 'w') as f:
                f.write(secrets_content)
            
            print("\n✅ Secrets saved to .streamlit/secrets.toml")
        except Exception as e:
            print(f"\n⚠️ Could not save secrets file: {e}")
            print("Please create .streamlit/secrets.toml manually with the above content")
        
        print("\n🎉 Setup complete! You can now run MauEyeCare with Google Drive integration.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error getting tokens: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

def test_tokens():
    """Test the generated tokens"""
    
    try:
        with open('.streamlit/secrets.toml', 'r') as f:
            content = f.read()
            
        # Extract token (simple parsing)
        for line in content.split('\n'):
            if 'GOOGLE_DRIVE_TOKEN' in line and '=' in line:
                token = line.split('=')[1].strip().strip('"')
                break
        else:
            print("❌ No token found in secrets.toml")
            return
        
        print(f"\n🧪 Testing token: {token[:20]}...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://www.googleapis.com/drive/v3/about?fields=user',
            headers=headers
        )
        
        if response.status_code == 200:
            user_info = response.json()
            email = user_info.get('user', {}).get('emailAddress', 'Unknown')
            print(f"✅ Token is valid! Connected as: {email}")
        else:
            print(f"❌ Token test failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing token: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Generate new Google Drive tokens")
    print("2. Test existing tokens")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        get_google_drive_tokens()
    elif choice == "2":
        test_tokens()
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")