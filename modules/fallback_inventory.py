"""
Fallback inventory manager for cloud compatibility
"""
import db
import pandas as pd

class FallbackInventoryManager:
    """Simple fallback inventory manager"""
    
    def __init__(self):
        self.medicine_db = {}
        self.spectacle_db = {}
    
    def get_all_medicines(self, include_external=True):
        """Get basic medicines from database"""
        try:
            local_inventory = db.get_inventory()
            medicines = {}
            
            for item, stock in local_inventory:
                medicines[item] = {
                    "current_stock": stock,
                    "price": 100,  # Default price
                    "category": "Medicine",
                    "type": "Unknown",
                    "source": "local"
                }
            
            return medicines
        except:
            return {}
    
    def search_medicines(self, search_term):
        """Search medicines"""
        all_medicines = self.get_all_medicines()
        results = {}
        
        search_lower = search_term.lower()
        for med_name, med_data in all_medicines.items():
            if search_lower in med_name.lower():
                results[med_name] = med_data
        
        return results
    
    def get_medicines_by_condition(self, condition, age=30):
        """Get basic medicine recommendations"""
        return {
            "local_recommendations": {},
            "mcp_recommendations": []
        }
    
    def purchase_medicine_external(self, medicine_name, quantity, source):
        """Simulate external purchase"""
        return {
            "status": "success",
            "tracking_id": "DEMO123",
            "estimated_delivery": "2-3 days"
        }
    
    def get_low_stock_items(self, threshold=5):
        """Get low stock items"""
        try:
            inventory = db.get_inventory()
            return [(item, stock) for item, stock in inventory if stock <= threshold]
        except:
            return []
    
    def get_inventory_value(self):
        """Calculate inventory value"""
        try:
            all_medicines = self.get_all_medicines(include_external=False)
            total_value = 0
            
            for med_name, med_data in all_medicines.items():
                stock = med_data.get("current_stock", 0)
                price = med_data.get("price", 0)
                total_value += stock * price
            
            return total_value
        except:
            return 0
    
    def generate_inventory_report(self):
        """Generate basic inventory report"""
        try:
            all_medicines = self.get_all_medicines()
            report_data = []
            
            for med_name, med_data in all_medicines.items():
                report_data.append({
                    "Item": med_name,
                    "Category": med_data.get("category", "Medicine"),
                    "Type": med_data.get("type", "Unknown"),
                    "Current Stock": med_data.get("current_stock", 0),
                    "Price": f"₹{med_data.get('price', 0)}",
                    "Value": f"₹{med_data.get('current_stock', 0) * med_data.get('price', 0)}",
                    "Source": med_data.get("source", "Local"),
                    "Status": "In Stock" if med_data.get("current_stock", 0) > 0 else "Out of Stock"
                })
            
            return pd.DataFrame(report_data)
        except:
            return pd.DataFrame()

# Create fallback instance
fallback_inventory = FallbackInventoryManager()