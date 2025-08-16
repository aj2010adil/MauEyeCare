"""
MauEyeCare System Startup Script
Initializes the database, starts market data scheduler, and launches the Streamlit app
"""
import subprocess
import threading
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import db
from market_updater import market_updater

def initialize_database():
    """Initialize the database with tables"""
    print("Initializing database...")
    db.init_db()
    print("Database initialized successfully!")

def start_market_scheduler():
    """Start the market data scheduler in a separate thread"""
    print("Starting market data scheduler...")
    
    def run_scheduler():
        try:
            # Run initial update
            market_updater.update_inventory_from_market()
            market_updater.check_low_stock_alerts()
            
            # Start the scheduler (this will run indefinitely)
            market_updater.start_scheduler()
        except Exception as e:
            print(f"Market scheduler error: {e}")
    
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Market data scheduler started in background!")

def start_streamlit_app():
    """Start the Streamlit application"""
    print("Starting Streamlit application...")
    
    # Change to src directory
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    os.chdir(src_dir)
    
    # Start Streamlit
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])

def check_uv_installation():
    """Check if UV is being used and dependencies are installed"""
    if os.path.exists('pyproject.toml'):
        print("UV project detected")
        try:
            # Check if uv.lock exists (indicates UV sync was run)
            if os.path.exists('uv.lock'):
                print("UV dependencies are synced")
            else:
                print("Run 'uv sync' to install dependencies")
                return False
        except Exception as e:
            print(f"UV check failed: {e}")
            return False
    return True

def main():
    """Main startup sequence"""
    print("=" * 50)
    print("MauEyeCare Optical Center System")
    print("=" * 50)
    
    try:
        # Step 0: Check UV installation
        if not check_uv_installation():
            print("Please run install.bat (Windows) or install.sh (Linux/Mac) first")
            return
        
        # Step 1: Initialize database
        initialize_database()
        
        # Step 2: Start market data scheduler
        start_market_scheduler()
        
        # Step 3: Wait a moment for scheduler to initialize
        time.sleep(2)
        
        # Step 4: Start Streamlit app
        start_streamlit_app()
        
    except KeyboardInterrupt:
        print("\nSystem shutdown requested...")
    except Exception as e:
        print(f"System startup error: {e}")
    finally:
        print("MauEyeCare system stopped.")

if __name__ == "__main__":
    main()