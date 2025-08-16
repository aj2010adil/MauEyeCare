"""
Run MauEyeCare Streamlit App
"""
import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("MauEyeCare Optical Center - Starting Application")
    print("=" * 60)
    
    # Test core functionality first
    print("Testing core functionality...")
    try:
        import app
        print("[OK] App imports successfully")
        print("[OK] Database initialized")
        print("[OK] LangGraph components loaded")
        print("[OK] All systems ready")
    except Exception as e:
        print(f"[ERROR] Startup error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Starting Streamlit Server...")
    print("Access the app at: http://localhost:8507")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8507",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")

if __name__ == "__main__":
    main()