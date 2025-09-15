#!/usr/bin/env python3
"""
Separate Inventory Management for Spectacles and Medicines
"""

import json
import os
from datetime import datetime, timezone, timedelta

# Separate inventory files
SPECTACLE_INVENTORY_FILE = "spectacle_inventory.json"
MEDICINE_INVENTORY_FILE = "medicine_inventory.json"

def load_spectacle_inventory():
    """Load spectacle inventory from file"""
    try:
        if os.path.exists(SPECTACLE_INVENTORY_FILE):
            with open(SPECTACLE_INVENTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def load_medicine_inventory():
    """Load medicine inventory from file"""
    try:
        if os.path.exists(MEDICINE_INVENTORY_FILE):
            with open(MEDICINE_INVENTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_spectacle_inventory(inventory):
    """Save spectacle inventory to file"""
    try:
        with open(SPECTACLE_INVENTORY_FILE, 'w') as f:
            json.dump(inventory, f, indent=2)
    except:
        pass

def save_medicine_inventory(inventory):
    """Save medicine inventory to file"""
    try:
        with open(MEDICINE_INVENTORY_FILE, 'w') as f:
            json.dump(inventory, f, indent=2)
    except:
        pass

def add_spectacle_inventory(item_name, quantity):
    """Add or update spectacle inventory"""
    inventory = load_spectacle_inventory()
    inventory[item_name] = quantity
    save_spectacle_inventory(inventory)

def add_medicine_inventory(item_name, quantity, price=100, category="Medicine", medicine_type="Tablet"):
    """Add or update medicine inventory with detailed information"""
    inventory = load_medicine_inventory()
    inventory[item_name] = {
        'quantity': quantity,
        'price': price,
        'category': category,
        'type': medicine_type,
        'date_added': datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
        'last_updated': datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
    }
    save_medicine_inventory(inventory)

def get_medicine_list():
    """Get list of available medicines from inventory"""
    inventory = load_medicine_inventory()
    result = {}
    for name, data in inventory.items():
        if isinstance(data, dict):
            if data.get('quantity', 0) > 0:
                result[name] = data['quantity']
        elif isinstance(data, int) and data > 0:
            result[name] = data
    return result

def reduce_medicine_stock(item_name, quantity):
    """Reduce medicine stock"""
    inventory = load_medicine_inventory()
    if item_name in inventory:
        if isinstance(inventory[item_name], dict):
            inventory[item_name]['quantity'] = max(0, inventory[item_name]['quantity'] - quantity)
            inventory[item_name]['last_updated'] = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
        else:
            inventory[item_name] = max(0, inventory[item_name] - quantity)
        save_medicine_inventory(inventory)

def reduce_spectacle_stock(item_name, quantity):
    """Reduce spectacle stock"""
    inventory = load_spectacle_inventory()
    if item_name in inventory:
        inventory[item_name] = max(0, inventory[item_name] - quantity)
        save_spectacle_inventory(inventory)