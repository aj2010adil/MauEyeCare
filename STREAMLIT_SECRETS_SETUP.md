# Streamlit Cloud Secrets Configuration

## Required Secrets for MauEyeCare Application

Add these secrets in your Streamlit Cloud app settings under **"Secrets"** tab:

### 1. Google Drive API Configuration

```toml
[google_drive]
client_id = "your-google-client-id.apps.googleusercontent.com"
client_secret = "your-google-client-secret"
refresh_token = "your-refresh-token"
folder_id = "your-google-drive-folder-id"

# Optional: Service Account (Alternative to OAuth)
service_account_key = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
'''
```

### 2. WhatsApp Business API Configuration

```toml
[whatsapp]
access_token = "your-whatsapp-business-api-token"
phone_number_id = "your-phone-number-id"
verify_token = "your-webhook-verify-token"
app_secret = "your-app-secret"
```

### 3. Application Configuration

```toml
[app]
debug_mode = false
demo_mode = false
environment = "production"
```

## How to Get These Values:

### Google Drive API Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Use the `get_google_tokens.py` script to get refresh token

### WhatsApp Business API Setup:
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a WhatsApp Business app
3. Get access token and phone number ID
4. Set up webhook (optional)

### Folder ID:
1. Create a folder in Google Drive named "MauEyeCare Prescriptions"
2. Copy the folder ID from the URL
3. Share the folder with your service account email (if using service account)

## Example Complete Secrets Configuration:

```toml
[google_drive]
client_id = "123456789-abcdef.apps.googleusercontent.com"
client_secret = "GOCSPX-abcdef123456"
refresh_token = "1//04abcdef123456"
folder_id = "1BcDeFgHiJkLmNoPqRsTuVwXyZ"

[whatsapp]
access_token = "EAABwzLixnjYBO..."
phone_number_id = "123456789012345"
verify_token = "maueyecare_webhook_token"
app_secret = "abcdef123456789"

[app]
debug_mode = false
demo_mode = false
environment = "production"
```

## Testing Configuration:

After adding secrets, the app will automatically test connections on startup and show status in the sidebar:
- ✅ Green: Working correctly
- ⚠️ Yellow: Demo mode (fallback)
- ❌ Red: Not configured or error

## Troubleshooting:

1. **Google Drive not working**: Check if API is enabled and tokens are valid
2. **WhatsApp not working**: Verify access token and phone number ID
3. **Secrets not loading**: Ensure proper TOML format and no extra spaces
4. **Demo mode**: App falls back to demo mode if real APIs aren't configured

## Security Notes:

- Never commit secrets to your repository
- Use Streamlit Cloud's secure secrets management
- Rotate tokens regularly
- Use service accounts for production Google Drive access