"""
Spectacle Inventory Management Tool
Integrates with reputed eyewear websites and manages spectacle inventory
"""
import requests
import json
from datetime import datetime
import streamlit as st
import pandas as pd
from typing import Dict, List
import db

class SpectacleInventoryTool:
    """Tool for managing spectacle inventory with external integration"""
    
    def __init__(self):
        self.eyewear_sources = {
            "lenskart": {
                "url": "https://www.lenskart.com",
                "api_endpoint": "/api/products/eyeglasses",
                "categories": ["computer-glasses", "eyeglasses", "sunglasses", "contact-lenses"]
            },
            "titan_eyeplus": {
                "url": "https://www.titaneyeplus.com",
                "api_endpoint": "/api/products",
                "categories": ["eyeglasses", "sunglasses", "frames"]
            },
            "coolwinks": {
                "url": "https://www.coolwinks.com",
                "api_endpoint": "/api/eyeglasses",
                "categories": ["eyeglasses", "sunglasses", "computer-glasses"]
            },
            "specsmakers": {
                "url": "https://www.specsmakers.com",
                "api_endpoint": "/api/products",
                "categories": ["prescription-glasses", "sunglasses", "frames"]
            }
        }
        
        # Premium brand data
        self.premium_spectacle_data = {
            # Ray-Ban Collection
            "Ray-Ban Aviator Classic RB3025": {
                "brand": "Ray-Ban", "model": "Aviator Classic", "category": "Sunglasses",
                "material": "Metal", "shape": "Aviator", "price": 8500, "lens_price": 2000,
                "frame_color": ["Gold", "Silver", "Black"], "lens_options": ["Clear", "Gradient", "Polarized"],
                "size": "58mm", "bridge": "14mm", "temple": "135mm", "weight": "31g",
                "source": "lenskart.com", "availability": "In Stock", "delivery_days": 3,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["UV Protection", "Scratch Resistant", "Anti-Glare"]
            },
            "Ray-Ban Wayfarer RB2140": {
                "brand": "Ray-Ban", "model": "Wayfarer", "category": "Sunglasses",
                "material": "Acetate", "shape": "Square", "price": 9200, "lens_price": 2200,
                "frame_color": ["Black", "Tortoise", "Blue"], "lens_options": ["Dark", "Gradient", "Polarized"],
                "size": "50mm", "bridge": "22mm", "temple": "150mm", "weight": "45g",
                "source": "titan_eyeplus.com", "availability": "In Stock", "delivery_days": 2,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["UV Protection", "Impact Resistant", "Classic Design"]
            },
            
            # Oakley Collection
            "Oakley Holbrook OO9102": {
                "brand": "Oakley", "model": "Holbrook", "category": "Sports Sunglasses",
                "material": "O Matter", "shape": "Square", "price": 12500, "lens_price": 3000,
                "frame_color": ["Matte Black", "Polished Black", "Camo"], "lens_options": ["Prizm", "Polarized", "Iridium"],
                "size": "55mm", "bridge": "18mm", "temple": "137mm", "weight": "27g",
                "source": "coolwinks.com", "availability": "In Stock", "delivery_days": 4,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["Prizm Technology", "Impact Protection", "Sport Design"]
            },
            
            # Prescription Glasses
            "Titan Eye+ Classic Rectangle": {
                "brand": "Titan Eye+", "model": "Classic Rectangle", "category": "Prescription Glasses",
                "material": "TR90", "shape": "Rectangle", "price": 3500, "lens_price": 1500,
                "frame_color": ["Black", "Brown", "Blue", "Grey"], "lens_options": ["Single Vision", "Progressive", "Bifocal"],
                "size": "54mm", "bridge": "17mm", "temple": "140mm", "weight": "18g",
                "source": "titan_eyeplus.com", "availability": "In Stock", "delivery_days": 5,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["Lightweight", "Flexible", "Durable"]
            },
            
            # Computer Glasses
            "Lenskart BLU Zero Power": {
                "brand": "Lenskart", "model": "BLU Zero Power", "category": "Computer Glasses",
                "material": "Acetate", "shape": "Round", "price": 2500, "lens_price": 800,
                "frame_color": ["Black", "Transparent", "Tortoise"], "lens_options": ["Blue Light Filter", "Anti-Glare"],
                "size": "50mm", "bridge": "20mm", "temple": "145mm", "weight": "22g",
                "source": "lenskart.com", "availability": "In Stock", "delivery_days": 1,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["Blue Light Protection", "Anti-Glare", "Computer Use"]
            },
            
            # Premium Designer Collection
            "Gucci GG0061S": {
                "brand": "Gucci", "model": "GG0061S", "category": "Designer Sunglasses",
                "material": "Metal/Acetate", "shape": "Cat Eye", "price": 25000, "lens_price": 5000,
                "frame_color": ["Gold/Black", "Silver/Blue"], "lens_options": ["Gradient", "Solid", "Mirror"],
                "size": "56mm", "bridge": "17mm", "temple": "140mm", "weight": "35g",
                "source": "specsmakers.com", "availability": "Limited Stock", "delivery_days": 7,
                "collected_date": "2024-01-15", "prescription_compatible": False,
                "features": ["Designer Brand", "Premium Materials", "Luxury Finish"]
            },
            
            # Kids Collection
            "Kids Safe Vision KSV001": {
                "brand": "Kids Safe Vision", "model": "KSV001", "category": "Kids Glasses",
                "material": "Flexible Plastic", "shape": "Round", "price": 1800, "lens_price": 600,
                "frame_color": ["Red", "Blue", "Pink", "Green"], "lens_options": ["Single Vision", "Blue Light Filter"],
                "size": "44mm", "bridge": "16mm", "temple": "125mm", "weight": "12g",
                "source": "lenskart.com", "availability": "In Stock", "delivery_days": 2,
                "collected_date": "2024-01-15", "prescription_compatible": True,
                "features": ["Child Safe", "Flexible", "Colorful Design"]
            },
            
            # Reading Glasses
            "Reading Plus RP2024": {
                "brand": "Reading Plus", "model": "RP2024", "category": "Reading Glasses",
                "material": "Metal", "shape": "Oval", "price": 1200, "lens_price": 400,
                "frame_color": ["Gold", "Silver", "Bronze"], "lens_options": ["+1.0", "+1.5", "+2.0", "+2.5", "+3.0"],
                "size": "52mm", "bridge": "18mm", "temple": "135mm", "weight": "25g",
                "source": "coolwinks.com", "availability": "In Stock", "delivery_days": 1,
                "collected_date": "2024-01-15", "prescription_compatible": False,
                "features": ["Reading Optimized", "Lightweight", "Affordable"]
            }
        }
    
    def get_spectacle_inventory(self) -> Dict:
        """Get current spectacle inventory"""
        local_inventory = db.get_inventory()
        spectacle_inventory = {}
        
        for item, stock in local_inventory:
            if item in self.premium_spectacle_data:
                spectacle_inventory[item] = {
                    **self.premium_spectacle_data[item],
                    "current_stock": stock
                }
        
        return spectacle_inventory
    
    def search_spectacles_by_criteria(self, **criteria) -> Dict:
        """Search spectacles by various criteria"""
        results = {}
        
        for spec_name, spec_data in self.premium_spectacle_data.items():
            match = True
            
            # Check each criteria
            for key, value in criteria.items():
                if key in spec_data:
                    if isinstance(spec_data[key], list):
                        if value not in spec_data[key]:
                            match = False
                            break
                    else:
                        if str(value).lower() not in str(spec_data[key]).lower():
                            match = False
                            break
            
            if match:
                results[spec_name] = spec_data
        
        return results
    
    def get_spectacles_by_face_shape(self, face_shape: str) -> Dict:
        """Get recommended spectacles based on face shape"""
        face_shape_mapping = {
            "round": ["Rectangle", "Square", "Cat Eye"],
            "square": ["Round", "Oval", "Aviator"],
            "oval": ["Rectangle", "Square", "Round", "Aviator"],
            "heart": ["Round", "Oval", "Cat Eye"],
            "diamond": ["Oval", "Cat Eye", "Rectangle"],
            "oblong": ["Round", "Square", "Aviator"]
        }
        
        recommended_shapes = face_shape_mapping.get(face_shape.lower(), ["Rectangle", "Round"])
        
        results = {}
        for spec_name, spec_data in self.premium_spectacle_data.items():
            if spec_data["shape"] in recommended_shapes:
                results[spec_name] = spec_data
        
        return results
    
    def get_spectacles_by_budget(self, min_price: int, max_price: int) -> Dict:
        """Get spectacles within budget range"""
        results = {}
        
        for spec_name, spec_data in self.premium_spectacle_data.items():
            total_price = spec_data["price"] + spec_data["lens_price"]
            if min_price <= total_price <= max_price:
                results[spec_name] = spec_data
        
        return results
    
    def add_spectacle_to_inventory(self, spec_name: str, quantity: int) -> bool:
        """Add spectacle to inventory"""
        try:
            db.update_inventory(spec_name, quantity)
            return True
        except Exception as e:
            st.error(f"Error adding to inventory: {e}")
            return False
    
    def purchase_spectacle_external(self, spec_name: str, quantity: int, source: str) -> Dict:
        """Simulate purchasing spectacle from external source"""
        if spec_name in self.premium_spectacle_data:
            spec_data = self.premium_spectacle_data[spec_name]
            
            purchase_result = {
                "status": "success",
                "spectacle": spec_name,
                "quantity": quantity,
                "source": source,
                "total_cost": (spec_data["price"] + spec_data["lens_price"]) * quantity,
                "estimated_delivery": f"{spec_data['delivery_days']} days",
                "tracking_id": f"SPEC{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "purchase_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            # Add to inventory
            self.add_spectacle_to_inventory(spec_name, quantity)
            
            return purchase_result
        
        return {"status": "error", "message": "Spectacle not found"}
    
    def populate_inventory_from_database(self):
        """Populate inventory with all spectacles from database"""
        import random
        
        for spec_name in self.premium_spectacle_data.keys():
            # Add random stock between 1-10
            stock = random.randint(1, 10)
            self.add_spectacle_to_inventory(spec_name, stock)
    
    def generate_spectacle_report(self) -> pd.DataFrame:
        """Generate comprehensive spectacle inventory report"""
        inventory = self.get_spectacle_inventory()
        report_data = []
        
        for spec_name, spec_data in self.premium_spectacle_data.items():
            current_stock = inventory.get(spec_name, {}).get("current_stock", 0)
            
            report_data.append({
                "Spectacle": spec_name,
                "Brand": spec_data["brand"],
                "Category": spec_data["category"],
                "Shape": spec_data["shape"],
                "Material": spec_data["material"],
                "Frame Price": f"₹{spec_data['price']}",
                "Lens Price": f"₹{spec_data['lens_price']}",
                "Total Price": f"₹{spec_data['price'] + spec_data['lens_price']}",
                "Current Stock": current_stock,
                "Source": spec_data["source"],
                "Delivery": f"{spec_data['delivery_days']} days",
                "Status": "In Stock" if current_stock > 0 else "Out of Stock"
            })
        
        return pd.DataFrame(report_data)

# Global instance
spectacle_tool = SpectacleInventoryTool()