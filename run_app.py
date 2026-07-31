#!/usr/bin/env python3
"""
Test runner for MauEyeCare application
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    print("Starting MauEyeCare application...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main_app_streamlined.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    print("🚀 MauEyeCare Application Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    target_app = "main_app_streamlined.py" if os.path.exists("main_app_streamlined.py") else "main_app.py"
    if not os.path.exists(target_app):
        print("❌ Application entry point not found. Please run this script from the MauEyeCare directory.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Cannot proceed without dependencies. Please install manually:")
        print("pip install -r requirements.txt")
        return
    
    print("\n🎯 Starting application...")
    print("📱 The app will open in your default browser")
    print("🔧 Use Ctrl+C to stop the application")
    print("-" * 40)
    
    # Run the app
    run_streamlit_app()

if __name__ == "__main__":
    main()