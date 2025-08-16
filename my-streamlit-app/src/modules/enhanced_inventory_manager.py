"""
Enhanced Inventory Manager with MCP Integration
Manages both medicines and spectacles with real-time updates
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db
from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
from modules.mcp_medicine_integration import mcp_integrator
import streamlit as st
from datetime import datetime
import pandas as pd

class EnhancedInventoryManager:
    """Enhanced inventory manager with MCP integration"""
    
    def __init__(self):
        self.medicine_db = COMPREHENSIVE_MEDICINE_DATABASE
        self.spectacle_db = COMPREHENSIVE_SPECTACLE_DATABASE
        self.mcp = mcp_integrator
    
    def get_all_medicines(self, include_external=True):
        """Get all medicines from local and external sources"""
        local_inventory = db.get_inventory()
        local_medicines = {row[0]: {"stock": row[1], "source": "local"} for row in local_inventory}
        
        # Add comprehensive database medicines
        all_medicines = {}
        for med_name, med_data in self.medicine_db.items():
            stock = local_medicines.get(med_name, {}).get("stock", 0)
            all_medicines[med_name] = {
                **med_data,
                "current_stock": stock,
                "source": "comprehensive_db"
            }
        
        # Add external medicines if MCP is enabled
        if include_external:
            external_inventory = self.mcp.get_real_time_inventory()
            for category, medicines in external_inventory.items():
                for med_name, med_data in medicines.items():
                    if med_name not in all_medicines:
                        all_medicines[med_name] = {
                            "price": med_data["price"],
                            "category": category.replace("_", " ").title(),
                            "type": "External",
                            "current_stock": 0,
                            "external_stock": med_data["stock"],
                            "source": med_data["source"],
                            "availability": "Available for Purchase"
                        }
        
        return all_medicines
    
    def get_medicines_by_condition(self, condition, age=30):
        """Get medicines recommended for specific eye condition"""
        # Get MCP recommendations
        mcp_recommendations = self.mcp.search_medicines_by_condition(condition, age)
        
        # Get local database recommendations
        local_recommendations = {}
        condition_keywords = {
            "dry_eyes": ["artificial", "tears", "lubricant", "carboxymethyl"],
            "infection": ["antibiotic", "moxifloxacin", "tobramycin", "ciprofloxacin"],
            "allergy": ["antihistamine", "olopatadine", "ketotifen"],
            "glaucoma": ["latanoprost", "timolol", "brimonidine"],
            "inflammation": ["prednisolone", "dexamethasone", "steroid"]
        }
        
        keywords = condition_keywords.get(condition.lower(), [])
        for med_name, med_data in self.medicine_db.items():
            if any(keyword in med_name.lower() or keyword in med_data.get("indication", "").lower() 
                   for keyword in keywords):
                local_recommendations[med_name] = med_data
        
        return {
            "local_recommendations": local_recommendations,
            "mcp_recommendations": mcp_recommendations
        }
    
    def search_medicines(self, search_term):
        """Search medicines by name or indication"""
        all_medicines = self.get_all_medicines()
        results = {}
        
        search_lower = search_term.lower()
        for med_name, med_data in all_medicines.items():
            if (search_lower in med_name.lower() or 
                search_lower in med_data.get("indication", "").lower() or
                search_lower in med_data.get("category", "").lower()):
                results[med_name] = med_data
        
        return results
    
    def get_spectacle_inventory(self):
        """Get spectacle inventory with enhanced data"""
        local_inventory = db.get_inventory()
        local_spectacles = {row[0]: row[1] for row in local_inventory}
        
        enhanced_spectacles = {}
        for spec_name, spec_data in self.spectacle_db.items():
            stock = local_spectacles.get(spec_name, 0)
            enhanced_spectacles[spec_name] = {
                **spec_data,
                "current_stock": stock
            }
        
        return enhanced_spectacles
    
    def purchase_medicine_external(self, medicine_name, quantity, source):
        """Purchase medicine from external source and add to inventory"""
        purchase_result = self.mcp.purchase_and_add_to_inventory(medicine_name, quantity, source)
        
        if purchase_result["status"] == "success":
            # Add to local inventory
            db.update_inventory(medicine_name, quantity)
            
            # Log purchase
            self._log_purchase(purchase_result)
        
        return purchase_result
    
    def _log_purchase(self, purchase_data):
        """Log purchase transaction"""
        # In a real implementation, this would log to a purchases table
        pass
    
    def get_low_stock_items(self, threshold=5):
        """Get items with low stock"""
        inventory = db.get_inventory()
        return [(item, stock) for item, stock in inventory if stock <= threshold]
    
    def get_inventory_value(self):
        """Calculate total inventory value"""
        all_medicines = self.get_all_medicines(include_external=False)
        total_value = 0
        
        for med_name, med_data in all_medicines.items():
            stock = med_data.get("current_stock", 0)
            price = med_data.get("price", 0)
            total_value += stock * price
        
        return total_value
    
    def generate_inventory_report(self):
        """Generate comprehensive inventory report"""
        all_medicines = self.get_all_medicines()
        spectacles = self.get_spectacle_inventory()
        
        report_data = []
        
        # Add medicines to report
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
        
        # Add spectacles to report
        for spec_name, spec_data in spectacles.items():
            report_data.append({
                "Item": spec_name,
                "Category": "Spectacles",
                "Type": spec_data.get("category", "Eyewear"),
                "Current Stock": spec_data.get("current_stock", 0),
                "Price": f"₹{spec_data.get('price', 0)}",
                "Value": f"₹{spec_data.get('current_stock', 0) * spec_data.get('price', 0)}",
                "Source": spec_data.get("source", "Local"),
                "Status": "In Stock" if spec_data.get("current_stock", 0) > 0 else "Out of Stock"
            })
        
        return pd.DataFrame(report_data)

# Global instance
enhanced_inventory = EnhancedInventoryManager()