# 🚀 MauEyeCare Deployment Setup Guide

## 🔐 Security Configuration for Public GitHub Repository

### 1. Streamlit Cloud Secrets Setup

When deploying to Streamlit Cloud, add these secrets in your app settings:

```toml
# In Streamlit Cloud App Settings > Secrets
GOOGLE_DRIVE_TOKEN = "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
GROK_API_KEY = "your_grok_api_key_here"
```

### 2. Local Development Setup

For local development, create `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml (already created and gitignored)
GOOGLE_DRIVE_TOKEN = "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
GROK_API_KEY = "your_grok_api_key_here"
```

### 3. Environment Variables (Alternative)

Set environment variables for local development:

```bash
# Windows
set GOOGLE_DRIVE_TOKEN=AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg
set GROK_API_KEY=your_grok_api_key_here

# Linux/Mac
export GOOGLE_DRIVE_TOKEN=AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg
export GROK_API_KEY=your_grok_api_key_here
```

## 🛡️ Security Features Implemented

✅ **API Key Protection**: Keys stored in Streamlit secrets, not in code
✅ **Gitignore Configuration**: Sensitive files excluded from repository
✅ **Fallback System**: Multiple secure methods for key access
✅ **Development Safety**: Local secrets file gitignored

## 📋 Deployment Checklist

- [ ] Add secrets to Streamlit Cloud app settings
- [ ] Verify `.streamlit/secrets.toml` is gitignored
- [ ] Test Google Drive integration locally
- [ ] Deploy to Streamlit Cloud
- [ ] Verify Google Drive upload functionality

## 🔧 Google Drive API Setup

1. **Enable Google Drive API** in Google Cloud Console
2. **Create Service Account** or use OAuth2
3. **Generate API Key** (already provided)
4. **Set Permissions** for Drive access

## 🚨 Important Security Notes

- **Never commit API keys** to public repositories
- **Use Streamlit secrets** for production deployment
- **Rotate keys regularly** for security
- **Monitor API usage** in Google Cloud Console

## 📞 Support

For deployment issues, contact the development team or refer to Streamlit Cloud documentation.