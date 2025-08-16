# 🔐 Google Drive OAuth 2.0 Setup Guide

## ⚠️ Current Issue:
You're using an **API Key** (`AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg`), but Google Drive file uploads require **OAuth 2.0** authentication.

## 🚀 Quick Setup Steps:

### **Step 1: Google Cloud Console Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create new one)
3. Enable **Google Drive API**
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
5. Choose **Web application**
6. Add authorized redirect URI: `http://localhost:8501` (for Streamlit)

### **Step 2: Get OAuth Credentials**
After creating OAuth client, you'll get:
- **Client ID**: `123456789-abcdef.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdef123456`

### **Step 3: Get Refresh Token**
Run this Python script to get refresh token:

```python
import requests
from urllib.parse import urlencode

# Your OAuth credentials
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8501"

# Step 1: Get authorization URL
auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode({
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'https://www.googleapis.com/auth/drive.file',
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent'
})

print("1. Visit this URL:")
print(auth_url)
print("\n2. Authorize the app and copy the 'code' from the redirect URL")

# Step 2: Exchange code for tokens
auth_code = input("\n3. Enter the authorization code: ")

token_url = "https://oauth2.googleapis.com/token"
data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': auth_code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI
}

response = requests.post(token_url, data=data)
tokens = response.json()

print("\n4. Your tokens:")
print(f"Access Token: {tokens.get('access_token')}")
print(f"Refresh Token: {tokens.get('refresh_token')}")
```

### **Step 4: Update Secrets**
Add to `.streamlit/secrets.toml`:
```toml
GOOGLE_CLIENT_ID = "your_client_id_here"
GOOGLE_CLIENT_SECRET = "your_client_secret_here"  
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

## 🎯 Alternative: Simple Solution

### **Make Folder Public for API Key Upload:**
1. Right-click your Google Drive folder
2. **Share** > **Anyone with the link**
3. Change permission to **Editor**
4. This allows API key uploads without OAuth

### **Or Use Service Account:**
1. Create Service Account in Google Cloud Console
2. Download JSON key file
3. Share folder with service account email
4. Use service account for uploads

## 🔧 Current Status:
- ❌ **API Key**: Limited to read-only operations
- ✅ **OAuth 2.0**: Full upload/edit permissions
- ✅ **Service Account**: Full permissions without user interaction

Choose OAuth 2.0 for the best user experience!