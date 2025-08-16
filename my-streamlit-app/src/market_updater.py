"""
Market Data Updater for MauEyeCare
Automatically updates inventory with latest market data
"""
import requests
import json
import schedule
import time
from datetime import datetime
import db

class MarketDataUpdater:
    def __init__(self):
        self.api_endpoints = {
            "spectacles": "https://api.example.com/spectacles",  # Replace with real API
            "medicines": "https://api.example.com/medicines"     # Replace with real API
        }
    
    def fetch_market_data(self, category: str) -> list:
        """Fetch latest market data for spectacles or medicines"""
        # Simulated market data - replace with real API calls
        if category == "spectacles":
            return [
                {"name": "Ray-Ban Aviator Classic", "price": 155, "stock": 30, "trending": True},
                {"name": "Oakley Holbrook Polarized", "price": 125, "stock": 25, "trending": True},
                {"name": "Progressive Lens Premium", "price": 220, "stock": 18, "trending": False},
                {"name": "Blue Light Filter HD", "price": 85, "stock": 45, "trending": True},
                {"name": "Photochromic Transition", "price": 190, "stock": 22, "trending": False},
                {"name": "Anti-Glare Coating", "price": 65, "stock": 50, "trending": True},
                {"name": "Bifocal Reading Glasses", "price": 95, "stock": 35, "trending": False},
                {"name": "Sports Sunglasses", "price": 110, "stock": 28, "trending": True}
            ]
        elif category == "medicines":
            return [
                {"name": "Latanoprost Eye Drops 0.005%", "price": 28, "stock": 55, "trending": True},
                {"name": "Timolol Maleate 0.5%", "price": 18, "stock": 40, "trending": False},
                {"name": "Artificial Tears Preservative-Free", "price": 12, "stock": 120, "trending": True},
                {"name": "Moxifloxacin Eye Drops", "price": 35, "stock": 30, "trending": True},
                {"name": "Prednisolone Acetate 1%", "price": 25, "stock": 45, "trending": False},
                {"name": "Cyclopentolate Eye Drops", "price": 22, "stock": 25, "trending": False},
                {"name": "Brimonidine Tartrate", "price": 30, "stock": 35, "trending": True},
                {"name": "Dorzolamide Eye Drops", "price": 32, "stock": 28, "trending": False}
            ]
        return []
    
    def update_inventory_from_market(self):
        """Update inventory with latest market data"""
        try:
            print(f"[{datetime.now()}] Starting market data update...")
            
            # Fetch spectacles data
            spectacles_data = self.fetch_market_data("spectacles")
            for item in spectacles_data:
                db.update_inventory(item['name'], item['stock'])
            
            # Fetch medicines data
            medicines_data = self.fetch_market_data("medicines")
            for item in medicines_data:
                db.update_inventory(item['name'], item['stock'])
            
            total_updated = len(spectacles_data) + len(medicines_data)
            print(f"[{datetime.now()}] Updated {total_updated} items in inventory")
            
            # Log trending items
            trending_items = [item['name'] for item in spectacles_data + medicines_data if item.get('trending')]
            if trending_items:
                print(f"[{datetime.now()}] Trending items: {', '.join(trending_items[:5])}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] Error updating inventory: {str(e)}")
            return False
    
    def check_low_stock_alerts(self):
        """Check for low stock items and generate alerts"""
        try:
            inventory = db.get_inventory()
            low_stock_items = [(item[0], item[1]) for item in inventory if item[1] < 10]
            
            if low_stock_items:
                print(f"[{datetime.now()}] LOW STOCK ALERT:")
                for item_name, quantity in low_stock_items:
                    print(f"  - {item_name}: {quantity} remaining")
                
                # In a real implementation, send email/SMS alerts here
                return low_stock_items
            else:
                print(f"[{datetime.now()}] All items have sufficient stock")
                return []
                
        except Exception as e:
            print(f"[{datetime.now()}] Error checking stock: {str(e)}")
            return []
    
    def get_market_trends(self) -> dict:
        """Get current market trends for spectacles and medicines"""
        spectacles_data = self.fetch_market_data("spectacles")
        medicines_data = self.fetch_market_data("medicines")
        
        trends = {
            "trending_spectacles": [item for item in spectacles_data if item.get('trending')],
            "trending_medicines": [item for item in medicines_data if item.get('trending')],
            "price_ranges": {
                "spectacles": {
                    "min": min([item['price'] for item in spectacles_data]),
                    "max": max([item['price'] for item in spectacles_data]),
                    "avg": sum([item['price'] for item in spectacles_data]) / len(spectacles_data)
                },
                "medicines": {
                    "min": min([item['price'] for item in medicines_data]),
                    "max": max([item['price'] for item in medicines_data]),
                    "avg": sum([item['price'] for item in medicines_data]) / len(medicines_data)
                }
            }
        }
        
        return trends
    
    def start_scheduler(self):
        """Start the automated market data update scheduler"""
        # Schedule updates every 6 hours
        schedule.every(6).hours.do(self.update_inventory_from_market)
        
        # Schedule low stock checks every 2 hours
        schedule.every(2).hours.do(self.check_low_stock_alerts)
        
        print(f"[{datetime.now()}] Market data scheduler started")
        print("- Inventory updates: Every 6 hours")
        print("- Stock alerts: Every 2 hours")
        
        # Run initial update
        self.update_inventory_from_market()
        self.check_low_stock_alerts()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Global market updater instance
market_updater = MarketDataUpdater()

if __name__ == "__main__":
    # Run the scheduler
    market_updater.start_scheduler()