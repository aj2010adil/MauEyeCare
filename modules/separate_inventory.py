#!/usr/bin/env python3
"""
Separate Inventory Management for MauEyeCare
Handles medicine and spectacle inventory with detailed tracking
"""

import json
import os
from datetime import datetime

INVENTORY_DIR = "inventory_data"
MEDICINE_FILE = os.path.join(INVENTORY_DIR, "medicines.json")
SPECTACLE_FILE = os.path.join(INVENTORY_DIR, "spectacles.json")

def ensure_inventory_dir():
    """Ensure inventory directory exists"""
    if not os.path.exists(INVENTORY_DIR):
        os.makedirs(INVENTORY_DIR)

def load_medicine_inventory():
    """Load medicine inventory from file"""
    ensure_inventory_dir()
    try:
        if os.path.exists(MEDICINE_FILE):
            with open(MEDICINE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_medicine_inventory(inventory):
    """Save medicine inventory to file"""
    ensure_inventory_dir()
    try:
        with open(MEDICINE_FILE, 'w') as f:
            json.dump(inventory, f, indent=2)
        return True
    except:
        return False

def load_spectacle_inventory():
    """Load spectacle inventory from file"""
    ensure_inventory_dir()
    try:
        if os.path.exists(SPECTACLE_FILE):
            with open(SPECTACLE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_spectacle_inventory(inventory):
    """Save spectacle inventory to file"""
    ensure_inventory_dir()
    try:
        with open(SPECTACLE_FILE, 'w') as f:
            json.dump(inventory, f, indent=2)
        return True
    except:
        return False

def add_medicine_inventory(name, quantity, price=100, category="Medicine", med_type="Tablet"):
    """Add or update medicine in inventory"""
    inventory = load_medicine_inventory()
    inventory[name] = {
        'quantity': quantity,
        'price': price,
        'category': category,
        'type': med_type,
        'last_updated': datetime.now().isoformat()
    }
    return save_medicine_inventory(inventory)

def add_spectacle_inventory(name, quantity, price=5000, brand="Generic", model="Standard", 
                          frame_type="Full Rim", material="Plastic", color="Black", 
                          size="Medium", image_url=""):
    """Add or update spectacle in inventory"""
    inventory = load_spectacle_inventory()
    inventory[name] = {
        'quantity': quantity,
        'price': price,
        'brand': brand,
        'model': model,
        'frame_type': frame_type,
        'material': material,
        'color': color,
        'size': size,
        'image_url': image_url,
        'qr_code': f"SP{len(inventory)+1:04d}",
        'last_updated': datetime.now().isoformat()
    }
    return save_spectacle_inventory(inventory)

def reduce_medicine_stock(name, quantity):
    """Reduce medicine stock by quantity"""
    inventory = load_medicine_inventory()
    if name in inventory:
        if isinstance(inventory[name], dict):
            current_qty = inventory[name].get('quantity', 0)
            inventory[name]['quantity'] = max(0, current_qty - quantity)
        else:
            # Handle old format
            current_qty = inventory[name] if isinstance(inventory[name], int) else 0
            inventory[name] = max(0, current_qty - quantity)
        
        inventory[name]['last_updated'] = datetime.now().isoformat()
        return save_medicine_inventory(inventory)
    return False

def reduce_spectacle_stock(name, quantity):
    """Reduce spectacle stock by quantity"""
    inventory = load_spectacle_inventory()
    if name in inventory:
        if isinstance(inventory[name], dict):
            current_qty = inventory[name].get('quantity', 0)
            inventory[name]['quantity'] = max(0, current_qty - quantity)
        else:
            # Handle old format
            current_qty = inventory[name] if isinstance(inventory[name], int) else 0
            inventory[name] = max(0, current_qty - quantity)
        
        if isinstance(inventory[name], dict):
            inventory[name]['last_updated'] = datetime.now().isoformat()
        return save_spectacle_inventory(inventory)
    return False

def get_medicine_list():
    """Get list of medicines with stock"""
    inventory = load_medicine_inventory()
    medicine_list = {}
    for name, data in inventory.items():
        if isinstance(data, dict):
            medicine_list[name] = data.get('quantity', 0)
        else:
            medicine_list[name] = data if isinstance(data, int) else 0
    return medicine_list

def get_spectacle_list():
    """Get list of spectacles with stock"""
    inventory = load_spectacle_inventory()
    spectacle_list = {}
    for name, data in inventory.items():
        if isinstance(data, dict):
            spectacle_list[name] = data.get('quantity', 0)
        else:
            spectacle_list[name] = data if isinstance(data, int) else 0
    return spectacle_list

def initialize_sample_inventory():
    """Initialize with sample inventory data"""
    # Sample medicines
    medicines = {
        "Refresh Tears Eye Drops": {
            "quantity": 50,
            "price": 150,
            "category": "Lubricant",
            "type": "Eye Drops",
            "last_updated": datetime.now().isoformat()
        },
        "Tobramycin Eye Drops": {
            "quantity": 30,
            "price": 200,
            "category": "Antibiotic", 
            "type": "Eye Drops",
            "last_updated": datetime.now().isoformat()
        },
        "Prednisolone Eye Drops": {
            "quantity": 25,
            "price": 180,
            "category": "Steroid",
            "type": "Eye Drops", 
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Sample spectacles
    spectacles = {
        "Ray-Ban Aviator Classic": {
            "quantity": 15,
            "price": 8000,
            "brand": "Ray-Ban",
            "model": "Aviator Classic",
            "frame_type": "Aviator",
            "material": "Metal",
            "color": "Gold",
            "size": "Medium",
            "qr_code": "SP0001",
            "image_url": "",
            "last_updated": datetime.now().isoformat()
        },
        "Oakley Holbrook": {
            "quantity": 10,
            "price": 12000,
            "brand": "Oakley", 
            "model": "Holbrook",
            "frame_type": "Square",
            "material": "Plastic",
            "color": "Black",
            "size": "Large",
            "qr_code": "SP0002",
            "image_url": "",
            "last_updated": datetime.now().isoformat()
        }
    }
    
    save_medicine_inventory(medicines)
    save_spectacle_inventory(spectacles)
    return True