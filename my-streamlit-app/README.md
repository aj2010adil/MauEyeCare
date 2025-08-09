# 🔍 MauEyeCare Optical Center

AI-powered optical center management system with LangGraph integration.

## 🚀 Quick Start

### Windows
```cmd
install.bat
```

### Linux/Mac
```bash
chmod +x install.sh && ./install.sh
```

## ✨ Features

- **🤖 AI Agent**: LangGraph-powered automation
- **📊 Market Data**: Real-time inventory updates
- **📋 Patient Management**: Complete medical records
- **📝 PDF Generation**: Automated prescriptions
- **💊 Inventory Control**: Smart stock management

## 🛠️ Manual Setup

1. **Install UV**:
   ```bash
   # Windows
   irm https://astral.sh/uv/install.ps1 | iex
   
   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Run System**:
   ```bash
   python start_system.py
   ```

## 📁 Project Structure

```
MauEyeCare/
├── src/
│   ├── app.py              # Main Streamlit app
│   ├── db.py               # Database operations
│   ├── langgraph_agent.py  # AI agent with tools
│   ├── market_updater.py   # Market data sync
│   └── modules/
│       ├── pdf_utils.py    # PDF generation
│       ├── ai_utils.py     # AI utilities
│       └── inventory_utils.py # Inventory management
├── pyproject.toml          # UV dependencies
├── install.bat             # Windows installer
├── install.sh              # Linux/Mac installer
└── start_system.py         # System launcher
```

## 🔧 Configuration

- **Database**: SQLite (auto-created)
- **Market Updates**: Every 6 hours
- **Stock Alerts**: Every 2 hours
- **AI Model**: Configurable in `perplexity_config.py`

## 📖 Usage

1. **Patient Management**: Add patients, medical history
2. **Prescriptions**: Generate with AI verification
3. **Inventory**: Auto-sync with market data
4. **AI Tools**: Execute tasks via natural language

## 🆘 Support

- Check `SETUP.md` for detailed instructions
- Ensure UV is properly installed
- Verify internet connection for market data