"""
inventory_utils.py
Inventory management utilities for MauEyeCare.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db

def get_inventory_dict():
    """Return inventory as a dict {item: quantity}."""
    return {row[0]: row[1] for row in db.get_inventory()}

def add_or_update_inventory(item, qty):
    """Add or update inventory item."""
    db.update_inventory(item, qty)

def reduce_inventory(item, qty):
    """Reduce inventory item quantity."""
    db.reduce_inventory(item, qty)
