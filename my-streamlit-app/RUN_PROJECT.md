# 🏃‍♂️ How to Run MauEyeCare Project

## 🎯 Simple 3-Step Process

### Step 1: Navigate to Project
```bash
cd MauEyeCare/my-streamlit-app/src
```

### Step 2: Run the Application
```bash
python run_app.py
```

### Step 3: Open in Browser
```
http://localhost:8507
```

**That's it! The application is now running.**

---

## 🔧 What Happens When You Run

### Automatic Startup Sequence
1. **System Check**: Verifies all components are working
2. **Database Init**: Creates/connects to SQLite database
3. **LangGraph Load**: Initializes AI agent system
4. **Streamlit Start**: Launches web interface
5. **Market Sync**: Starts background data updates

### Expected Console Output
```
============================================================
MauEyeCare Optical Center - Starting Application
============================================================
Testing core functionality...
[OK] App imports successfully
[OK] Database initialized
[OK] LangGraph components loaded
[OK] All systems ready

============================================================
Starting Streamlit Server...
Access the app at: http://localhost:8507
Press Ctrl+C to stop the server
============================================================

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8507
  Network URL: http://192.168.1.xxx:8507
```

---

## 🌟 What You'll See in the Browser

### Main Interface Tabs
1. **📋 Prescription & Patient** - Add patients, create prescriptions
2. **📦 Inventory Management** - Manage medicines and spectacles
3. **📊 Patient History** - View patient records and history
4. **🤖 AI Agent Tools** - Use LangGraph automation features

### Key Features Available
- ✅ Patient registration with medical history
- ✅ Digital prescription generation with PDF
- ✅ AI-powered prescription validation
- ✅ Real-time inventory management
- ✅ Automated market data updates
- ✅ Comprehensive patient tracking

---

## 🚨 If Something Goes Wrong

### Common Issues & Quick Fixes

#### 1. Port Already in Use
```bash
# Try different port
python -m streamlit run app.py --server.port 8508
```

#### 2. Missing Dependencies
```bash
# Install requirements
pip install -r requirements.txt
```

#### 3. Database Error
```bash
# Delete and recreate database
rm eyecare.db
python run_app.py
```

#### 4. LangGraph Not Working
```bash
# Install LangGraph
pip install langgraph langchain langchain-core
```

---

## 🧪 Test Before Using

### Quick Functionality Test
```bash
# Test core features
python test_app.py

# Test AI features
python test_langgraph.py
```

### Expected Test Results
```
SUCCESS: All core functionality is working!
SUCCESS: LangGraph functionality is working!
```

---

## 📱 First Time Usage Guide

### 1. Add Your First Patient
- Go to "Prescription & Patient" tab
- Fill patient form (name, age, gender, contact)
- Select issue and advice from dropdowns
- Click "Save/Select Patient"

### 2. Create Prescription
- Fill Rx table for both eyes (OD/OS)
- Add medical test results
- Select medicines from inventory
- Generate and download PDF

### 3. Try AI Features
- Go to "AI Agent Tools" tab
- Try "Generate PDF for patient"
- Use quick actions for automation

---

## 🔄 Alternative Running Methods

### Method 1: Direct Streamlit
```bash
cd src/
streamlit run app.py
```

### Method 2: With Market Scheduler
```bash
python start_system.py
```

### Method 3: Using Installers
```bash
# Windows
install.bat

# Linux/Mac
./install.sh
```

---

## 📊 System Status Indicators

### Green Lights (All Working) ✅
- Database connection established
- LangGraph agent loaded
- Market updater running
- PDF generation ready
- Inventory system active

### Yellow Warnings (Partial Function) ⚠️
- LangGraph not available (core features still work)
- Market data offline (manual inventory only)
- Font issues (ASCII fallback used)

### Red Errors (Needs Attention) ❌
- Database connection failed
- Critical import errors
- Port binding issues

---

## 🎉 Success Indicators

### You Know It's Working When:
1. **Browser Opens**: Streamlit interface loads
2. **Tabs Visible**: All 4 main tabs are accessible
3. **Database Ready**: Patient form accepts input
4. **PDF Works**: Can generate prescription PDFs
5. **AI Active**: Agent tools respond to commands

### Performance Metrics
- **Startup Time**: ~10-15 seconds
- **Page Load**: <2 seconds
- **PDF Generation**: <5 seconds
- **Database Queries**: <1 second
- **AI Tasks**: 5-10 seconds

---

## 🛑 How to Stop the Application

### Graceful Shutdown
```bash
# In terminal where app is running
Ctrl + C
```

### Force Stop (if needed)
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f streamlit
```

---

## 📞 Need Help?

### Documentation Files
- **DOCUMENTATION.md** - Complete system documentation
- **QUICK_START.md** - Detailed usage guide
- **SETUP.md** - Installation instructions
- **README.md** - Project overview

### Test Files
- **test_app.py** - Core functionality tests
- **test_langgraph.py** - AI features tests

### Support Resources
- Check troubleshooting sections in documentation
- Review test outputs for specific errors
- Verify system requirements are met

---

**🚀 Ready to Launch!**

Your MauEyeCare Optical Center management system is ready to use. The AI-powered features will help streamline your eye care practice with automated prescription generation, inventory management, and patient tracking.

*Start helping patients with better eye care! 👁️‍🗨️*