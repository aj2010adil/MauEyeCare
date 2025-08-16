# 🚀 Deploy MauEyeCare to Streamlit Cloud

## Step-by-Step Deployment Guide

### 1. Prepare Repository
```bash
# Navigate to project directory
cd MauEyeCare/my-streamlit-app

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: MauEyeCare Optical Center"
```

### 2. Push to GitHub
```bash
# Create repository on GitHub: https://github.com/new
# Name: maueyecare

# Add remote and push
git remote add origin https://github.com/YOURUSERNAME/maueyecare.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Streamlit Cloud

#### Option A: Direct Deployment
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select repository: `YOURUSERNAME/maueyecare`
5. Set main file path: `src/app.py`
6. Click "Deploy!"

#### Option B: Custom Domain
1. Follow Option A steps
2. In app settings, add custom domain
3. Configure DNS records as instructed

### 4. Configuration Files Created
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies  
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Project documentation

### 5. Environment Variables (Optional)
If using API keys, add to Streamlit Cloud:
1. Go to app settings
2. Add secrets in `secrets.toml` format:
```toml
[secrets]
GROK_API_KEY = "your-key-here"
NGROK_AUTH_TOKEN = "your-token-here"
```

### 6. Expected Deployment URL
Your app will be available at:
`https://YOURUSERNAME-maueyecare-src-app-HASH.streamlit.app`

### 7. Custom Subdomain (Pro)
For custom URL like `maueyecare.streamlit.app`:
1. Upgrade to Streamlit Cloud Pro
2. Request custom subdomain
3. Configure in app settings

## 🔧 Troubleshooting

### Common Issues:
1. **Import Errors**: Check `requirements.txt`
2. **File Paths**: Use relative paths from `src/`
3. **Database**: SQLite auto-creates on first run
4. **Fonts**: PDF generation uses fallback fonts

### Performance Tips:
- Database operations are optimized
- PDF generation is cached
- Static files are minimal

## 📱 Post-Deployment

### Test Your Deployment:
1. ✅ Patient registration works
2. ✅ PDF generation functions
3. ✅ Inventory management active
4. ✅ AI agent tools respond
5. ✅ All tabs accessible

### Share Your App:
- **Public URL**: Share with anyone
- **Features**: Full optical center management
- **No login**: Direct access for users

## 🎉 Success!
Your MauEyeCare system is now live and accessible worldwide!