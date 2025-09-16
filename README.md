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
4. Deploy

## 📋 Features

- **👥 Patient Management** - Professional patient registration with Google Sheets integration
- **👓 Spectacle Gallery** - Dynamic spectacle inventory from Google Sheets
- **📦 Inventory Management** - Real-time Google Sheets inventory tracking
- **📄 Prescription Generation** - Professional prescription generation and export
- **📊 Hospital Analytics** - Marketing and operational analytics
- **🖼️ Image Management** - Local spectacle image storage and management

## 🔧 Configuration

### Google Sheets Integration
**Default Sheet ID:** `1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ`

**Required Sheets:**
- **Medicines** - Medicine inventory with columns: name, category, type, price, quantity, prescription_required, indication, dosage
- **Spectacles** - Spectacle inventory with columns: name, brand, model, category, price, lens_price, material, shape, image_path
- **Patients** - Patient records with registration and visit data
- **Prescriptions** - Prescription history and details
- **Analytics** - Hospital analytics for marketing and operations

**Setup:**
1. Copy the Google Sheet template
2. Make it publicly viewable (Anyone with link can view)
3. Update sheet ID in code if using custom sheet

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

1. **Register Patient** - Add patient information with Google Sheets integration
2. **Browse Spectacle Gallery** - View spectacles from Google Sheets inventory
3. **Generate Prescription** - Create professional prescriptions with export options
4. **Manage Inventory** - Real-time Google Sheets inventory management
5. **View Analytics** - Hospital performance and marketing analytics
6. **Upload Images** - Manage spectacle images locally

## 🔒 Data Management

- Google Sheets for real-time data synchronization
- Local image storage for spectacle photos
- CSV export capabilities for data backup
- Professional patient data handling
- Multi-user collaborative access via Google Sheets

## 📞 Support

For technical support or questions:
- Email: tech@maueyecare.com
- Phone: +91 92356-47410

## 📄 License

Professional Eye Care Management System - All rights reserved.