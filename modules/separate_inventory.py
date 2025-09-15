#!/usr/bin/env python3
"""
Separate Inventory Management for Spectacles and Medicines
"""

import json
import os

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

def add_medicine_inventory(item_name, quantity):
    """Add or update medicine inventory"""
    inventory = load_medicine_inventory()
    inventory[item_name] = quantity
    save_medicine_inventory(inventory)

def get_medicine_list():
    """Get list of available medicines from inventory"""
    inventory = load_medicine_inventory()
    return {name: stock for name, stock in inventory.items() if stock > 0}

def reduce_medicine_stock(item_name, quantity):
    """Reduce medicine stock"""
    inventory = load_medicine_inventory()
    if item_name in inventory:
        inventory[item_name] = max(0, inventory[item_name] - quantity)
        save_medicine_inventory(inventory)

def reduce_spectacle_stock(item_name, quantity):
    """Reduce spectacle stock"""
    inventory = load_spectacle_inventory()
    if item_name in inventory:
        inventory[item_name] = max(0, inventory[item_name] - quantity)
        save_spectacle_inventory(inventory)