#!/usr/bin/env python3
"""
Setup script for MauEyeCare application
"""
import os
import sys
import subprocess
import sqlite3

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Initialize the database"""
    print("\n🗄️ Setting up database...")
    try:
        import db
        db.init_db()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    required_modules = [
        'streamlit',
        'pandas',
        'numpy',
        'PIL',
        'requests',
        'openpyxl'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All required modules imported successfully!")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'modules',
        '.streamlit'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/")
        else:
            print(f"✅ {directory}/ exists")

def create_streamlit_config():
    """Create Streamlit configuration"""
    print("\n⚙️ Creating Streamlit configuration...")
    
    config_dir = '.streamlit'
    config_file = os.path.join(config_dir, 'config.toml')
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_content = """[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F8FF"
textColor = "#262730"
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print("✅ Streamlit configuration created")

def run_basic_test():
    """Run a basic test of the application"""
    print("\n🧪 Running basic application test...")
    
    try:
        # Test database
        import db
        patients = db.get_patients()
        print(f"✅ Database test passed - {len(patients)} patients found")
        
        # Test modules
        from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
        from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
        
        print(f"✅ Spectacle database loaded - {len(COMPREHENSIVE_SPECTACLE_DATABASE)} items")
        print(f"✅ Medicine database loaded - {len(COMPREHENSIVE_MEDICINE_DATABASE)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 MauEyeCare Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Create Streamlit config
    create_streamlit_config()
    
    # Run basic test
    if not run_basic_test():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: Run_MauEyeCare.bat (or double click it in Windows)")
    print("2. Or run: streamlit run main_app_streamlined.py")
    print("3. Open your browser to the displayed URL")
    print("\n💡 Tips:")
    print("- Use 'Load Complete Database' in sidebar to populate inventory")
    print("- Register a patient first before using other features")
    print("- Check the README.md for more information")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)