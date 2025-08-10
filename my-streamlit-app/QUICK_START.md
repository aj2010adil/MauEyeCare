# 🚀 MauEyeCare Quick Start Guide

## How to Run the Project

### ⚡ Fastest Method (Recommended)

1. **Open Terminal/Command Prompt**
   ```bash
   cd MauEyeCare/my-streamlit-app/src
   ```

2. **Run the Application**
   ```bash
   python run_app.py
   ```

3. **Access the Application**
   - Open browser: `http://localhost:8507`
   - The app will start automatically

### 🔧 Alternative Methods

#### Method 1: Direct Streamlit
```bash
cd src/
python -m streamlit run app.py --server.port 8507
```

#### Method 2: System Startup (with market scheduler)
```bash
python start_system.py
```

#### Method 3: Using Installers
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

---

## 🧪 Testing Before Running

### Test Core Functionality
```bash
cd src/
python test_app.py
```
**Expected Output:**
```
==================================================
MauEyeCare Functionality Test
==================================================
[OK] Database initialized
[OK] Patient added with ID: 1
[OK] Retrieved X patients
[OK] PDF generated successfully
[OK] Medical tests added
SUCCESS: All core functionality is working!
```

### Test LangGraph AI Features
```bash
cd src/
python test_langgraph.py
```
**Expected Output:**
```
==================================================
MauEyeCare LangGraph Test
==================================================
[OK] PDF generation task
[OK] Market data task
[OK] Inventory task
[OK] Market update: True
SUCCESS: LangGraph functionality is working!
```

---

## 📱 Using the Application

### 1. Patient Management
- **Add New Patient**: Fill patient form → Save/Select Patient
- **View History**: Patient History tab → Search by name/mobile

### 2. Create Prescription
- **Select Patient**: Use patient form
- **Fill Rx Details**: OD/OS specifications
- **Add Medicines**: Select from inventory
- **Generate PDF**: Download prescription

### 3. AI Agent Tools
- **Access**: AI Agent Tools tab
- **Execute Tasks**: Select task → Execute
- **Quick Actions**: Use preset buttons

### 4. Inventory Management
- **View Stock**: Inventory Management tab
- **Add Items**: Use add medicine/spectacle forms
- **Market Update**: Click "Update from Market"

---

## 🔍 Features Overview

### Core Features ✅
- ✅ Patient registration and management
- ✅ Prescription generation with PDF output
- ✅ Medical tests tracking (BP, sugar, eye tests)
- ✅ Inventory management with stock alerts
- ✅ Patient history with change tracking

### AI Features 🤖
- ✅ LangGraph agent with 4 specialized tools
- ✅ Automated PDF generation
- ✅ Market data synchronization
- ✅ Prescription validation
- ✅ Smart inventory updates

### Advanced Features 🚀
- ✅ Real-time stock monitoring
- ✅ Market trend analysis
- ✅ Multi-language PDF support
- ✅ Automated scheduling system
- ✅ Comprehensive patient records

---

## 🛠️ Troubleshooting

### If App Won't Start
1. **Check Python Version**: `python --version` (need 3.11+)
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Check Port**: Try different port `--server.port 8508`

### If Tests Fail
1. **Database Issues**: Delete `eyecare.db` and restart
2. **Import Errors**: Install missing packages
3. **Unicode Errors**: Set `PYTHONIOENCODING=utf-8`

### If LangGraph Not Working
1. **Install LangGraph**: `pip install langgraph langchain langchain-core`
2. **Check Imports**: Run `python -c "import langgraph; print('OK')"`
3. **Fallback Mode**: App works without LangGraph (limited features)

---

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10/Linux/macOS
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for market data

### Recommended Setup
- **OS**: Windows 11/Ubuntu 22.04/macOS 12+
- **Python**: 3.11 with UV package manager
- **RAM**: 8GB or more
- **Storage**: 2GB free space
- **Network**: Stable broadband connection

---

## 🎯 First Time Usage

### Step 1: Add Your First Patient
1. Go to "Prescription & Patient" tab
2. Fill patient details (name, age, gender, contact)
3. Select patient issue from dropdown
4. Choose advice from eye care options
5. Click "Save/Select Patient"

### Step 2: Create Prescription
1. Fill Rx table for OD/OS eyes
2. Add medical test results
3. Select medicines from inventory
4. Click "Generate PDF"
5. Download prescription

### Step 3: Try AI Features
1. Go to "AI Agent Tools" tab
2. Select "Generate PDF for patient"
3. Click "Execute Agent Task"
4. Try other AI tools

### Step 4: Manage Inventory
1. Go to "Inventory Management" tab
2. View current stock levels
3. Add new medicines/spectacles
4. Try "Update from Market"

---

## 📞 Need Help?

### Documentation
- **Full Documentation**: `DOCUMENTATION.md`
- **Setup Guide**: `SETUP.md`
- **README**: `README.md`

### Support
- **Technical Issues**: Check troubleshooting section
- **Feature Questions**: Review documentation
- **Bug Reports**: Check GitHub issues

### Community
- **Discussions**: GitHub discussions
- **Updates**: Follow project releases
- **Contributions**: Fork and submit PRs

---

**🎉 You're Ready to Go!**

The MauEyeCare system is now ready for use. Start by adding your first patient and exploring the features. The AI agent will help automate many tasks once you get familiar with the interface.

*Happy prescribing! 👨‍⚕️👩‍⚕️*