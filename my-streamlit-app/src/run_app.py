#!/usr/bin/env python3
"""
MauEyeCare Application Launcher
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0", 
        "fpdf2>=2.8.0",
        "requests>=2.28.0",
        "python-docx>=0.8.11",
        "opencv-python-headless>=4.8.0",
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "beautifulsoup4>=4.11.0"
    ]
    
    print("Installing required packages...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to install {req}")
    
    print("Installation complete!")

def run_app():
    """Run the MauEyeCare application"""
    try:
        print("Starting MauEyeCare Application...")
        print("Access the app at: http://localhost:8507")
        print("Press Ctrl+C to stop the application")
        
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main_app.py", 
            "--server.port", "8507",
            "--server.headless", "true"
        ])
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("MauEyeCare - AI Eye Care System")
    print("=" * 60)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("Streamlit found")
    except ImportError:
        print("Installing dependencies...")
        install_requirements()
    
    # Run the application
    run_app()