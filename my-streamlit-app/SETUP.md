# MauEyeCare LangGraph Setup Guide

## Quick Installation with UV

### Windows
```cmd
install.bat
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

## Manual Installation

1. **Install UV (if not already installed)**
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install Dependencies with UV**
```bash
uv sync
```

3. **Start the Complete System**
```bash
python start_system.py
```

## Alternative (Traditional pip)
```bash
pip install -r requirements.txt
python start_system.py
```

## Features Added

### 🤖 LangGraph Agent System
- **PDF Generator Tool**: Automatically generates prescription PDFs
- **Market Data Fetcher**: Retrieves latest spectacles and medicines data
- **Inventory Manager**: Updates stock levels automatically
- **Patient Data Reader**: Accesses patient history and medical records

### 📊 Market Data Integration
- **Auto-Updates**: Inventory updates every 6 hours
- **Stock Alerts**: Low stock notifications every 2 hours
- **Market Trends**: Real-time trending items tracking
- **Price Analysis**: Automatic price range calculations

### 🛠️ Tools Available

1. **PDF Generation**
   - Automated prescription PDF creation
   - Patient data integration
   - Professional formatting

2. **Market Data**
   - Latest spectacles inventory
   - Medicine stock updates
   - Trending items identification

3. **Inventory Management**
   - Automatic stock updates
   - Low stock alerts
   - Market price tracking

4. **Database Maintenance**
   - Patient history tracking
   - Medical test records
   - Prescription management

## Usage

### AI Agent Tools Tab
- Execute custom tasks using natural language
- Quick actions for common operations
- Real-time agent status monitoring

### Market Integration
- Click "Update from Market" to sync latest data
- "Check Low Stock" for inventory alerts
- "Market Trends" for current market analysis

### Automated Features
- Background market data synchronization
- Automatic inventory updates
- Low stock notifications
- Database maintenance

## System Architecture

```
MauEyeCare System
├── LangGraph Agent (langgraph_agent.py)
│   ├── PDF Generator Tool
│   ├── Market Data Tool
│   ├── Inventory Manager Tool
│   └── Patient Data Tool
├── Market Updater (market_updater.py)
│   ├── Scheduled Updates
│   ├── Stock Monitoring
│   └── Trend Analysis
├── Database (db.py)
│   ├── Patient Records
│   ├── Medical Tests
│   ├── Prescriptions
│   └── Inventory
└── Streamlit App (app.py)
    ├── Patient Management
    ├── Prescription System
    ├── Inventory Control
    └── AI Agent Interface
```

## Configuration

### API Endpoints (Optional)
Edit `market_updater.py` to connect to real market data APIs:
```python
self.api_endpoints = {
    "spectacles": "https://your-spectacles-api.com",
    "medicines": "https://your-medicines-api.com"
}
```

### Scheduling
Modify update frequencies in `market_updater.py`:
```python
schedule.every(6).hours.do(self.update_inventory_from_market)  # Change 6 to desired hours
schedule.every(2).hours.do(self.check_low_stock_alerts)       # Change 2 to desired hours
```

## Troubleshooting

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Issues**: Delete `src/eyecare.db` and restart
3. **Agent Errors**: Check LangGraph and LangChain versions
4. **Market Data**: Verify internet connection for API calls