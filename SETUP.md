# MauEyeCare Setup Instructions

## Prerequisites
- Python 3.8 or higher installed
- pip package manager

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup.py
```

### 3. Start the Application
```bash
streamlit run main_app.py
```

Or use the launcher:
```bash
python run_app.py
```

## Manual Setup (if automated setup fails)

### 1. Install Dependencies Manually
```bash
pip install streamlit>=1.28.0
pip install pandas>=1.5.0
pip install numpy>=1.21.0
pip install Pillow>=9.0.0
pip install requests>=2.28.0
pip install openpyxl>=3.0.0
pip install opencv-python-headless>=4.8.0
pip install python-docx>=0.8.11
pip install fpdf2>=2.8.0
pip install reportlab>=3.6.0
pip install beautifulsoup4>=4.11.0
```

### 2. Initialize Database
```python
import db
db.init_db()
```

### 3. Test Application
```bash
streamlit run main_app.py
```

## Features Verification

After setup, verify these features work:

1. **Patient Registration** - Add a test patient
2. **Medicine Gallery** - Browse medicines with filters
3. **Spectacle Gallery** - Browse spectacles with filters
4. **Inventory Management** - Load database and check inventory
5. **Prescription Generation** - Generate and download prescriptions

## Troubleshooting

### Common Issues:

1. **Import Errors**: Install missing packages individually
2. **Database Errors**: Delete `eyecare.db` and restart
3. **Port Issues**: Use `streamlit run main_app.py --server.port 8502`

### Key Enhancements Implemented:

1. **Extended Sphere Ranges**: -20.00 to +20.00 with 0.25 increments
2. **Custom Input Options**: Doctors can enter any prescription values
3. **Medicine Gallery Integration**: Direct medicine selection in prescription
4. **Internal/External Classification**: Proper medicine categorization
5. **Detailed Medicine Management**: Dosage, duration, custom additions
6. **Enhanced Prescription Output**: Professional format with complete details

## Demo Mode

The application works in demo mode without external API configurations:
- WhatsApp integration uses demo mode
- Google Drive uses demo mode
- All core features work offline

## Production Setup

For production use:
1. Configure WhatsApp Business API tokens
2. Set up Google Drive API credentials
3. Configure proper database backup
4. Set up SSL certificates for HTTPS

## Support

For issues, check:
1. Python version (3.8+)
2. All dependencies installed
3. Database permissions
4. Port availability (8501)