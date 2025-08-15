#!/usr/bin/env python
"""Simple test without unicode"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    print("Testing imports...")
    import streamlit as st
    import pandas as pd
    import datetime
    import db
    from modules.pdf_utils import generate_pdf
    from modules.inventory_utils import get_inventory_dict
    from modules.enhanced_docx_utils import generate_professional_prescription_docx
    from config import CONFIG
    
    print("All imports successful")
    
    print("Testing config...")
    token = CONFIG.get('WHATSAPP_ACCESS_TOKEN')
    print(f"Config loaded: {bool(token)}")
    
    print("Testing database...")
    db.init_db()
    patients = db.get_patients()
    print(f"Database working: {len(patients)} patients")
    
    print("Testing inventory...")
    inventory = get_inventory_dict()
    print(f"Inventory loaded: {len(inventory)} items")
    
    print("Testing DOCX generation...")
    docx_data = generate_professional_prescription_docx(
        {'Eye Drops': 1}, 'Dr Danish', 'Test Patient', 30, 'Male', 
        'Test advice', {}, [], {'Eye Drops': {'dosage': '1 drop', 'timing': 'Twice daily'}}
    )
    print(f"DOCX generated: {len(docx_data)} bytes")
    
    print("SUCCESS: All tests passed! App should run without errors.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()