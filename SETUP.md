# MauEyeCare Setup Guide

## 🚀 Streamlit Cloud Deployment

### 1. Repository Setup
- Ensure `main_app.py` is at repository root
- Push all files to GitHub repository

### 2. Streamlit Cloud Configuration
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set **Main file path**: `main_app.py`
5. Deploy

### 3. Optional Integrations

#### Google Drive (for prescription sharing)
Add to Streamlit Cloud Secrets:
```toml
[google_drive]
client_id = "641133812410-phlnghc1fau2gjt3e7m73sm5ec7n0s6v.apps.googleusercontent.com"
client_secret = "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"
refresh_token = "YOUR_REFRESH_TOKEN"  # Get from OAuth flow
folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"
```

#### WhatsApp Business API (for patient communication)
```toml
[whatsapp]
access_token = "YOUR_WHATSAPP_TOKEN"
phone_number_id = "YOUR_PHONE_NUMBER_ID"
```

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run main_app.py
```

## ✅ Features Available Without Setup

The app works fully without any API keys:
- ✅ Patient registration and management
- ✅ Spectacle and medicine galleries
- ✅ Prescription generation with download
- ✅ Inventory management
- ✅ Demo mode for all integrations

## 📞 Support

Email: tech@maueyecare.com | Phone: +91 92356-47410