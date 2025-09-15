# MauEyeCare - AI-Powered Eye Care System

Complete AI-powered eye care management system with patient registration, inventory management, and prescription generation.

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
4. Deploy

## 📋 Features

- **👥 Patient Management** - Registration with integrated medicine selection and prescription details
- **👓 Spectacle Gallery** - 1000+ spectacle database with filters
- **📸 AI Camera Analysis** - Face shape detection for spectacle recommendations
- **📦 Inventory Management** - Real-time stock tracking and alerts
- **📄 Prescription Generation** - Professional prescription with download options
- **☁️ Google Drive Integration** - Cloud storage for prescriptions
- **📱 WhatsApp Integration** - Patient communication

## 🔧 Configuration

### Optional: Google Drive Integration
Add to Streamlit Cloud secrets:
```toml
[google_drive]
client_id = "your-client-id"
client_secret = "your-client-secret"
refresh_token = "your-refresh-token"
folder_id = "your-folder-id"
```

### Optional: WhatsApp Integration
```toml
[whatsapp]
access_token = "your-whatsapp-token"
phone_number_id = "your-phone-number-id"
```

## 📁 Project Structure

```
MauEyeCare/
├── main_app.py              # Main application entry point
├── requirements.txt         # Python dependencies
├── db.py                   # Database operations
├── integration_config.py   # Integration setup
├── modules/                # Application modules
│   ├── comprehensive_spectacle_database.py
│   ├── comprehensive_medicine_database.py
│   ├── fast_inventory_manager.py
│   ├── google_drive_integration.py
│   ├── whatsapp_utils.py
│   └── ...
└── README.md               # This file
```

## 🎯 Usage

1. **Register Patient** - Add patient information, eye prescription, and select medicines with dosage details
2. **Browse Spectacle Gallery** - Select spectacles with AI recommendations
3. **AI Analysis** - Use camera for face shape detection (optional)
4. **Generate Prescription** - Create and share professional prescription with all details
5. **Manage Inventory** - Track stock levels and get alerts

## 🔒 Security

- All sensitive data stored securely in Streamlit secrets
- No credentials committed to repository
- Professional data handling and privacy protection

## 📞 Support

For technical support or questions:
- Email: tech@maueyecare.com
- Phone: +91 92356-47410

## 📄 License

Professional Eye Care Management System - All rights reserved.