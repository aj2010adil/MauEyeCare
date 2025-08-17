# MauEyeCare - AI Eye Care System

## 🚀 Quick Start

### Option 1: Windows Users (Easiest)
1. Double-click `start_app.bat`
2. Wait for installation to complete
3. Open browser to `http://localhost:8507`

### Option 2: Python Users
```bash
python run_app.py
```

### Option 3: Manual Start
```bash
pip install streamlit pandas fpdf2 requests python-docx opencv-python-headless Pillow numpy beautifulsoup4
python -m streamlit run main_app.py --server.port 8507
```

## 📋 Features

### ✅ Working Features
- **👥 Patient Registration** - Complete patient information management
- **👓 Spectacle Gallery** - Browse 41+ spectacles with filters
- **💊 Medicine Gallery** - Browse 18+ medicines with categories
- **📸 AI Camera Analysis** - Face shape analysis for spectacle recommendations
- **📋 Patient History** - Search and manage patient records
- **📄 Prescription Generator** - Generate PDF prescriptions
- **📦 Inventory Management** - Automatic inventory updates
- **🔍 Advanced Filters** - Filter by category, price, brand
- **💰 Indian Pricing** - All prices in ₹ (Rupees)

### 🎯 Key Capabilities
1. **Patient Management**: Register patients with complete eye care details
2. **AI Recommendations**: Camera-based face analysis for spectacle matching
3. **Inventory Control**: Real-time inventory tracking and updates
4. **Prescription Generation**: Professional PDF prescriptions
5. **Product Catalog**: Comprehensive spectacle and medicine databases
6. **Search & Filter**: Advanced filtering for products and patients

## 📊 Database Stats
- **👓 Spectacles**: 41 items (Luxury, Mid-Range, Budget categories)
- **💊 Medicines**: 18 items (Prescription & OTC)
- **🏥 Patients**: Unlimited patient records
- **📦 Inventory**: Auto-managed stock levels

## 🔧 System Requirements
- Python 3.8+
- Windows/Linux/Mac
- Internet connection (for AI features)
- Camera (optional, for face analysis)

## 📱 Usage Flow
1. **Register Patient** → Enter patient details and eye prescription
2. **Camera Analysis** → Capture photo for AI face shape analysis
3. **Browse Products** → Select spectacles and medicines
4. **Generate Prescription** → Create PDF with selected items
5. **Inventory Update** → System automatically updates stock

## 🆘 Support
- **Phone**: +91 92356-47410
- **Email**: tech@maueyecare.com

## 📁 File Structure
```
src/
├── main_app.py          # Main application (SINGLE FILE TO RUN)
├── start_app.bat        # Windows launcher
├── run_app.py          # Python launcher
├── db.py               # Database functions
├── modules/            # Feature modules
│   ├── pdf_utils.py
│   ├── inventory_utils.py
│   ├── comprehensive_spectacle_database.py
│   ├── comprehensive_medicine_database.py
│   └── ...
└── eyecare.db          # SQLite database
```

## 🎉 Ready to Use!
The system is fully functional with all core features working. Simply run the application and start managing your eye care practice!