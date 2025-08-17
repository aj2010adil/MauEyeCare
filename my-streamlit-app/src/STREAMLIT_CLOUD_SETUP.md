# 🚀 Streamlit Cloud Deployment Guide for MauEyeCare

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Google Cloud Account** - For Google Drive API
4. **WhatsApp Business Account** - For WhatsApp API (optional)

## 🔧 Step 1: Google Drive API Setup

### 1.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Drive API**

### 1.2 Create Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:8080`
   - `https://your-app-name.streamlit.app`
5. Download the JSON file

### 1.3 Get Access Token
Run this Python script locally to get your tokens:

```python
import requests
import json

# Your OAuth 2.0 credentials from downloaded JSON
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8080"

# Step 1: Get authorization URL
auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=https://www.googleapis.com/auth/drive.file&response_type=code&access_type=offline"

print("1. Open this URL in your browser:")
print(auth_url)
print("\n2. After authorization, copy the 'code' parameter from the redirect URL")

# Step 2: Exchange code for tokens
auth_code = input("\n3. Enter the authorization code: ")

token_url = "https://oauth2.googleapis.com/token"
token_data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': auth_code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI
}

response = requests.post(token_url, data=token_data)
tokens = response.json()

print("\n4. Your tokens:")
print(f"ACCESS_TOKEN: {tokens.get('access_token')}")
print(f"REFRESH_TOKEN: {tokens.get('refresh_token')}")
```

## 🔧 Step 2: Streamlit Cloud Configuration

### 2.1 Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file path: `my-streamlit-app/src/main_app.py`
5. Click **Deploy**

### 2.2 Add Secrets in Streamlit Cloud
1. In your Streamlit Cloud dashboard, click on your app
2. Go to **Settings** → **Secrets**
3. Add the following secrets:

```toml
# Google Drive API Configuration
GOOGLE_DRIVE_TOKEN = "ya29.a0AcM612x..."  # Your actual access token
GOOGLE_CLIENT_ID = "123456789-abc.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-abc123..."
GOOGLE_REFRESH_TOKEN = "1//04abc123..."

# WhatsApp Business API Configuration (Optional)
WHATSAPP_ACCESS_TOKEN = "EAABwz..."  # Your WhatsApp access token
WHATSAPP_PHONE_NUMBER_ID = "123456789"

# Application Settings
DOCTOR_NAME = "Dr. Danish"
CLINIC_NAME = "MauEyeCare Optical Center"
CLINIC_PHONE = "+91 92356-47410"
CLINIC_EMAIL = "tech@maueyecare.com"
```

## 🔧 Step 3: WhatsApp Business API Setup (Optional)

### 3.1 Create Meta Developer Account
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app
3. Add **WhatsApp Business API** product

### 3.2 Get WhatsApp Credentials
1. Go to **WhatsApp** → **API Setup**
2. Copy your **Access Token**
3. Copy your **Phone Number ID**
4. Add these to Streamlit Cloud secrets

## 📁 Step 4: File Structure for Deployment

Ensure your repository has this structure:

```
your-repo/
├── my-streamlit-app/
│   ├── src/
│   │   ├── main_app.py                 # Main application
│   │   ├── modules/                    # All modules
│   │   ├── .streamlit/
│   │   │   └── config.toml            # Streamlit config
│   │   └── requirements.txt           # Dependencies
│   └── README.md
```

## 📦 Step 5: Requirements.txt

Make sure your `requirements.txt` includes:

```txt
streamlit>=1.28.0
pandas>=1.5.0
requests>=2.28.0
pillow>=9.0.0
numpy>=1.21.0
opencv-python-headless>=4.8.0
beautifulsoup4>=4.11.0
fpdf2>=2.8.0
python-docx>=0.8.11
```

## 🔧 Step 6: Environment Variables (Alternative)

If you prefer environment variables over secrets, you can also set:

```bash
# In your local environment or server
export GOOGLE_DRIVE_TOKEN="your_token_here"
export WHATSAPP_ACCESS_TOKEN="your_token_here"
```

## 🚀 Step 7: Deploy and Test

1. **Push to GitHub**: Commit all changes to your repository
2. **Deploy**: Streamlit Cloud will automatically deploy
3. **Test**: Access your app at `https://your-app-name.streamlit.app`
4. **Monitor**: Check logs in Streamlit Cloud dashboard

## 🔍 Troubleshooting

### Common Issues:

1. **"No secrets found" error**
   - Ensure secrets are added in Streamlit Cloud dashboard
   - Check secret names match exactly (case-sensitive)

2. **Google Drive API errors**
   - Verify API is enabled in Google Cloud Console
   - Check token expiration (refresh tokens if needed)
   - Ensure proper scopes are granted

3. **Import errors**
   - Check all dependencies in requirements.txt
   - Verify file paths are correct

4. **WhatsApp API errors**
   - Verify phone number is verified in Meta Developer Console
   - Check access token permissions

## 🔄 Token Refresh (Important)

Google Drive access tokens expire. Use this code to refresh:

```python
import requests

def refresh_google_token(refresh_token, client_id, client_secret):
    url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(url, data=data)
    return response.json().get('access_token')
```

## 📞 Support

- **Streamlit Cloud**: [docs.streamlit.io](https://docs.streamlit.io)
- **Google Drive API**: [developers.google.com/drive](https://developers.google.com/drive)
- **WhatsApp Business API**: [developers.facebook.com/docs/whatsapp](https://developers.facebook.com/docs/whatsapp)

## 🎉 Success!

Once deployed, your MauEyeCare application will be available at:
`https://your-app-name.streamlit.app`

Features available:
- ✅ Patient registration and management
- ✅ AI camera analysis
- ✅ Spectacle and medicine inventory
- ✅ Google Drive prescription sharing
- ✅ WhatsApp integration
- ✅ Professional inventory management