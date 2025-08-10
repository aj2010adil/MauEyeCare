# MauEyeCare Optical Center - Complete Documentation

## 📋 Project Overview

**MauEyeCare** is an AI-powered optical center management system built with Streamlit and LangGraph. It provides comprehensive patient management, prescription generation, inventory control, and automated market data integration for eye care professionals.

### 🎯 Key Features
- **Patient Management**: Complete patient records with medical history
- **Prescription System**: Digital prescription generation with PDF output
- **AI Agent Integration**: LangGraph-powered automation tools
- **Inventory Management**: Real-time stock tracking and market updates
- **Medical Tests Tracking**: Blood pressure, sugar, eye examinations
- **Market Data Sync**: Automated inventory updates from market sources

---

## 🏗️ System Architecture

```
MauEyeCare System
├── Frontend (Streamlit)
│   ├── Patient Management Interface
│   ├── Prescription Generation
│   ├── Inventory Dashboard
│   └── AI Agent Tools
├── Backend Services
│   ├── Database (SQLite)
│   ├── PDF Generation (FPDF2)
│   ├── LangGraph Agent System
│   └── Market Data Updater
├── AI Components
│   ├── LangGraph Workflow Engine
│   ├── Tool Executor System
│   ├── Market Data Fetcher
│   └── Prescription Validator
└── Data Storage
    ├── Patient Records
    ├── Medical Test History
    ├── Prescription Database
    └── Inventory Management
```

---

## 📁 Project Structure

```
MauEyeCare/
├── src/                          # Main application code
│   ├── app.py                    # Streamlit main application
│   ├── db.py                     # Database operations
│   ├── langgraph_agent.py        # LangGraph AI agent
│   ├── market_updater.py         # Market data synchronization
│   ├── test_app.py               # Core functionality tests
│   ├── test_langgraph.py         # LangGraph functionality tests
│   ├── run_app.py                # Application launcher
│   └── modules/
│       ├── pdf_utils.py          # PDF generation utilities
│       ├── ai_utils.py           # AI integration utilities
│       ├── inventory_utils.py    # Inventory management
│       └── fonts/                # Font files for PDF
├── pyproject.toml                # UV package configuration
├── requirements.txt              # Python dependencies
├── install.bat                   # Windows installer
├── install.sh                    # Linux/Mac installer
├── start_system.py               # System startup script
├── README.md                     # Quick start guide
├── SETUP.md                      # Detailed setup instructions
└── DOCUMENTATION.md              # This file
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Windows/Linux/Mac OS
- Internet connection for market data

### Quick Installation

#### Option 1: UV Package Manager (Recommended)
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

#### Option 2: Manual Installation
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
# OR
irm https://astral.sh/uv/install.ps1 | iex       # Windows

# Install dependencies
uv sync

# Run application
python src/run_app.py
```

#### Option 3: Traditional pip
```bash
pip install -r requirements.txt
python src/run_app.py
```

---

## 🚀 Running the Application

### Method 1: Using the Launcher
```bash
cd src/
python run_app.py
```

### Method 2: Direct Streamlit
```bash
cd src/
streamlit run app.py --server.port 8507
```

### Method 3: System Startup Script
```bash
python start_system.py
```

**Access the application at:** `http://localhost:8507`

---

## 📊 Database Schema

### Tables Structure

#### 1. Patients Table
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    contact TEXT
);
```

#### 2. Prescriptions Table
```sql
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_name TEXT,
    medicines TEXT,
    dosage TEXT,
    eye_test TEXT,
    issue TEXT,
    money_given REAL DEFAULT 0,
    money_pending REAL DEFAULT 0,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
```

#### 3. Medical Tests Table
```sql
CREATE TABLE medical_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    blood_pressure TEXT,
    blood_sugar TEXT,
    complete_blood_test TEXT,
    viral_marker TEXT,
    fundus_examination TEXT,
    iop TEXT,
    retinoscopy_dry TEXT,
    retinoscopy_wet TEXT,
    syringing TEXT,
    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
```

#### 4. Inventory Table
```sql
CREATE TABLE inventory (
    medicine TEXT PRIMARY KEY,
    quantity INTEGER
);
```

---

## 🤖 LangGraph AI Agent System

### Agent Architecture

The LangGraph agent consists of 4 specialized tools:

#### 1. PDF Generator Tool
- **Purpose**: Automated prescription PDF creation
- **Input**: Patient data, prescription details
- **Output**: PDF generation status
- **Usage**: `agent.generate_patient_pdf(patient_data)`

#### 2. Market Data Fetcher Tool
- **Purpose**: Retrieve latest market data for medicines/spectacles
- **Input**: Query string (spectacles/medicines)
- **Output**: JSON market data
- **Usage**: `agent.execute_task("fetch latest market data")`

#### 3. Inventory Manager Tool
- **Purpose**: Update inventory and check stock levels
- **Input**: Action type and item data
- **Output**: Inventory update status
- **Usage**: `agent.update_inventory_from_market()`

#### 4. Patient Data Reader Tool
- **Purpose**: Access patient history and medical records
- **Input**: Patient ID
- **Output**: Patient summary data
- **Usage**: `agent.get_patient_summary(patient_id)`

### Agent Workflow
```python
# Agent State Management
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_task: str
    results: dict

# Workflow Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.add_conditional_edges("action", should_continue, {
    "continue": "agent",
    "end": END
})
```

---

## 📋 User Interface Components

### Tab 1: Prescription & Patient
- **Patient Information Form**
  - Personal details (name, age, gender, contact)
  - Patient issue/complaint (dropdown selection)
  - Advice/notes (eye care terminology dropdown)
  
- **Rx Table (OD/OS)**
  - Sphere, Cylinder, Axis (dropdown options)
  - Near vision, Glass type, Glass tint
  - Prism (manual input)
  
- **Medical Tests**
  - Blood pressure, Blood sugar
  - Complete blood test, Viral markers
  
- **Special Investigations**
  - Fundus examination, IOP measurement
  - Retinoscopy (dry/wet), Syringing
  
- **Medicine Selection**
  - Multi-select from inventory
  - Quantity input with stock validation
  
- **AI Verification**
  - Prescription appropriateness check
  - Age/condition matching validation

### Tab 2: Inventory Management
- **Current Inventory Display**
  - Item list with quantities
  - Stock level indicators
  
- **Add/Update Items**
  - Medicine addition form
  - Spectacle inventory management
  
- **Market Data Integration**
  - Auto-update from market sources
  - Low stock alerts
  - Market trend analysis

### Tab 3: Patient History
- **Patient Search**
  - Search by mobile number
  - Search by name
  
- **History Display**
  - Medical test history with change tracking
  - Prescription history
  - Payment tracking (money given/pending)

### Tab 4: AI Agent Tools
- **Task Executor**
  - Natural language task input
  - Predefined task selection
  - Context-aware execution
  
- **Quick Actions**
  - Auto-generate PDF
  - Smart inventory update
  - Stock analysis
  
- **Agent Status**
  - Tool availability
  - System status monitoring

---

## 🔧 API Integration

### Market Data API Structure
```python
# Simulated market data format
market_data = {
    "spectacles": [
        {
            "name": "Ray-Ban Aviator Classic",
            "price": 155,
            "stock": 30,
            "trending": True
        }
    ],
    "medicines": [
        {
            "name": "Latanoprost Eye Drops 0.005%",
            "price": 28,
            "stock": 55,
            "trending": True
        }
    ]
}
```

### AI Verification API
```python
# Grok API integration for prescription validation
def verify_prescription(patient_data):
    prompt = f"""
    Patient: {patient_name}, Age: {age}
    Issue: {patient_issue}
    Advice: {advice}
    Medicines: {medicines}
    Verify prescription appropriateness in one concise line.
    """
    # API call to Grok/OpenAI compatible endpoint
```

---

## 📄 PDF Generation System

### PDF Structure
1. **Header Section**
   - Hospital branding
   - Contact information
   - Doctor credentials

2. **Patient Information**
   - Personal details
   - Medical history summary

3. **Prescription Details**
   - Rx table (OD/OS specifications)
   - Medicine list with quantities
   - Dosage instructions

4. **Recommendations**
   - Spectacle recommendations
   - Follow-up instructions

5. **Footer**
   - Hospital information
   - Legal disclaimers

### Font Support
- **Unicode Support**: DejaVu Sans, Arial Unicode
- **Fallback**: ASCII characters for compatibility
- **Multilingual**: English primary, Hindi/Urdu support

---

## 🔄 Automated Processes

### Market Data Synchronization
- **Frequency**: Every 6 hours
- **Process**: Fetch → Validate → Update inventory
- **Monitoring**: Stock level alerts

### Low Stock Alerts
- **Frequency**: Every 2 hours
- **Threshold**: Items with quantity < 10
- **Action**: Generate alert notifications

### Database Maintenance
- **Backup**: Automatic SQLite file backup
- **Cleanup**: Old record archival
- **Optimization**: Index maintenance

---

## 🧪 Testing Framework

### Core Functionality Tests
```bash
cd src/
python test_app.py
```
**Tests Include:**
- Database operations
- PDF generation
- Inventory management
- Medical tests functionality

### LangGraph Agent Tests
```bash
cd src/
python test_langgraph.py
```
**Tests Include:**
- Agent task execution
- Tool functionality
- Market data integration
- Error handling

---

## 🔒 Security Considerations

### Data Protection
- **Patient Data**: Encrypted storage
- **API Keys**: Environment variable storage
- **Database**: SQLite with file permissions

### Access Control
- **Session Management**: Streamlit session state
- **Input Validation**: Form data sanitization
- **Error Handling**: Graceful failure management

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install missing dependencies
pip install langgraph langchain langchain-core
```

#### 2. Database Connection Issues
```bash
# Solution: Check database path and permissions
ls -la eyecare.db
```

#### 3. PDF Generation Errors
```bash
# Solution: Install/upgrade FPDF2
pip uninstall pypdf && pip install --upgrade fpdf2
```

#### 4. Unicode Encoding Issues
```bash
# Solution: Set environment variable
set PYTHONIOENCODING=utf-8  # Windows
export PYTHONIOENCODING=utf-8  # Linux/Mac
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Patient ID, date fields
- **Query Optimization**: Limit result sets
- **Connection Pooling**: Reuse connections

### Memory Management
- **PDF Generation**: Stream processing
- **Large Datasets**: Pagination
- **Cache Management**: Session state cleanup

### Network Optimization
- **API Calls**: Async processing
- **Market Data**: Batch updates
- **Error Retry**: Exponential backoff

---

## 🔮 Future Enhancements

### Planned Features
1. **Multi-language Support**: Complete UI translation
2. **Cloud Integration**: AWS/Azure deployment
3. **Mobile App**: React Native companion
4. **Advanced Analytics**: Business intelligence dashboard
5. **Telemedicine**: Video consultation integration

### Technical Improvements
1. **Database Migration**: PostgreSQL support
2. **Microservices**: Service decomposition
3. **Container Deployment**: Docker/Kubernetes
4. **Real-time Updates**: WebSocket integration
5. **Advanced AI**: Custom model training

---

## 📞 Support & Maintenance

### Development Team
- **Lead Developer**: System architecture and AI integration
- **Database Administrator**: Data management and optimization
- **UI/UX Designer**: Interface design and user experience
- **QA Engineer**: Testing and quality assurance

### Maintenance Schedule
- **Daily**: System health monitoring
- **Weekly**: Database backup and cleanup
- **Monthly**: Security updates and patches
- **Quarterly**: Feature updates and enhancements

### Contact Information
- **Technical Support**: tech@maueyeycare.com
- **Bug Reports**: bugs@maueyeycare.com
- **Feature Requests**: features@maueyeycare.com

---

## 📜 License & Legal

### Software License
- **Type**: MIT License
- **Usage**: Commercial and personal use allowed
- **Attribution**: Required for redistribution

### Medical Disclaimer
- **Purpose**: Administrative tool only
- **Responsibility**: Healthcare decisions remain with licensed professionals
- **Compliance**: Local medical regulations must be followed

### Data Privacy
- **HIPAA Compliance**: Patient data protection
- **GDPR Compliance**: European data protection
- **Local Laws**: Regional privacy regulations

---

*Last Updated: August 2025*
*Version: 1.0.0*
*Documentation maintained by MauEyeCare Development Team*