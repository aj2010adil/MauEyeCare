# 🚀 Quick Setup Guide for MauEyeCare

## 🎯 Option 1: Local Development (Fastest)

### Step 1: Install Dependencies
```bash
pip install streamlit pandas requests pillow numpy opencv-python-headless beautifulsoup4 fpdf2 python-docx
```

### Step 2: Run Without Google Drive (Demo Mode)
```bash
cd my-streamlit-app/src
python -m streamlit run main_app.py --server.port 8501
```

**✅ This will work immediately with all features except Google Drive upload**

---

## 🌐 Option 2: Full Setup with Google Drive

### Step 1: Get Google Drive API Tokens
```bash
cd my-streamlit-app/src
python get_google_tokens.py
```

Follow the interactive prompts to:
1. Create Google Cloud project
2. Enable Google Drive API
3. Get OAuth credentials
4. Generate access tokens

### Step 2: Run with Full Features
```bash
python -m streamlit run main_app.py --server.port 8501
```

**✅ This includes Google Drive prescription sharing**

---

## ☁️ Option 3: Deploy to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "MauEyeCare application"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repository
3. Set main file: `my-streamlit-app/src/main_app.py`
4. Add secrets in Settings > Secrets:

```toml
GOOGLE_DRIVE_TOKEN = "your_token_here"
GOOGLE_CLIENT_ID = "your_client_id_here"
GOOGLE_CLIENT_SECRET = "your_client_secret_here"
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

**✅ Your app will be live at https://your-app-name.streamlit.app**

---

## 🎉 What Works Out of the Box

### ✅ Core Features (No Setup Required)
- **Patient Registration** - Complete patient management
- **Spectacle Gallery** - 41+ spectacles with filters
- **Medicine Gallery** - 18+ medicines with categories  
- **AI Camera Analysis** - Face shape analysis
- **Patient History** - Search and manage records
- **Inventory Management** - Professional stock management
- **Prescription Generation** - HTML prescriptions

### 🔧 Advanced Features (Requires Setup)
- **Google Drive Upload** - Cloud prescription storage
- **WhatsApp Integration** - Send prescriptions to patients
- **Real-time Sync** - Multi-device access

---

## 📱 Access Your Application

### Local Development
- **URL**: http://localhost:8501
- **Features**: All except Google Drive

### Streamlit Cloud
- **URL**: https://your-app-name.streamlit.app  
- **Features**: All features with proper setup

---

## 🆘 Need Help?

### Quick Fixes
1. **Import Errors**: Run `pip install -r requirements.txt`
2. **Port Issues**: Change port number `--server.port 8502`
3. **Google Drive Errors**: Use demo mode first, then setup tokens

### Support Files
- `STREAMLIT_CLOUD_SETUP.md` - Detailed cloud deployment
- `get_google_tokens.py` - Interactive token generator
- `.streamlit/secrets.toml` - Configuration template

---

## 🎯 Recommended Workflow

1. **Start Simple**: Run locally without Google Drive
2. **Test Features**: Try patient registration, inventory, prescriptions
3. **Add Google Drive**: Use token generator when ready
4. **Deploy to Cloud**: Push to Streamlit Cloud for production

**🚀 You can start using MauEyeCare in under 2 minutes!**