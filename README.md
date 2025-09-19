# MauEyeCare - Professional Eye Care Hospital Management

Google Sheets integrated hospital management system for professional eye care with real-time inventory, patient management, and analytics.

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements.txt
streamlit run main_app.py
```

### Streamlit Cloud Deployment
1. Fork this repository
2. Connect to Streamlit Cloud
3. Set **Main file path**: `main_app.py`
4. Configure secrets (see Security Setup below)
5. Deploy

### Security Setup
1. Copy `.streamlit/secrets.toml` template
2. Add your Google OAuth credentials
3. Never commit secrets to GitHub

## 📋 Features

- **👥 Patient Management** - Professional patient registration with duplicate detection
- **👓 Spectacle Gallery** - Dynamic spectacle inventory with real-time stock tracking
- **📦 Inventory Management** - Automatic stock updates after prescriptions
- **📄 Prescription Generation** - Professional HTML prescriptions with WhatsApp sharing
- **📊 Hospital Analytics** - Marketing and operational analytics
- **🔐 OAuth Integration** - Secure Google Sheets real-time sync
- **📱 WhatsApp Integration** - Share prescriptions directly to patients

## 🔧 Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins
6. Copy credentials to `.streamlit/secrets.toml`

### Google Sheets Integration
**Default Sheet ID:** `1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ`

**Required Sheets:**
- **Medicines** - Medicine inventory with automatic stock tracking
- **Spectacles** - Spectacle inventory with real-time updates
- **Patients** - Patient records with visit tracking
- **Prescriptions** - Prescription history with OAuth sync
- **Analytics** - Hospital analytics for insights

**Setup:**
1. Copy the Google Sheet template
2. Make it publicly viewable (Anyone with link can view)
3. Authenticate with OAuth for real-time sync

## 📁 Project Structure

```
MauEyeCare/
├── main_app.py                    # Main application entry point
├── requirements.txt               # Python dependencies
├── modules/                       # Application modules
│   ├── google_sheets_manager.py   # Google Sheets integration
│   ├── image_manager.py           # Image upload and management
│   ├── comprehensive_spectacle_database.py
│   └── comprehensive_medicine_database.py
├── uploaded_images/               # Local image storage
└── README.md                      # This file
```

## 🎯 Usage

1. **Load Sample Inventory** - Click "Load Sample Inventory" in sidebar
2. **Register Patient** - Add patient with comprehensive demographics
3. **Select Medicines** - Choose from inventory with automatic stock alerts
4. **Browse Spectacles** - View spectacles with real-time stock status
5. **Generate Prescription** - Create HTML prescriptions with WhatsApp sharing
6. **Track Analytics** - Monitor patient trends and retention
7. **Sync Data** - Real-time Google Sheets integration with OAuth

## 🔒 Data Management

- **Real-time Sync** - OAuth-enabled Google Sheets integration
- **Inventory Tracking** - Automatic stock updates after prescriptions
- **Duplicate Prevention** - Smart patient registration with visit tracking
- **WhatsApp Integration** - Direct prescription sharing to patients
- **Professional Security** - Secrets management and secure authentication
- **Local Backup** - Automatic inventory management with JSON storage

## 📞 Support

For technical support or questions:
- Email: tech@maueyecare.com
- Phone: +91 92356-47410

## 📄 License

Professional Eye Care Management System - All rights reserved.