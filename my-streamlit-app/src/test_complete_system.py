#!/usr/bin/env python
"""Test the complete system before running"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_system():
    print("=== Testing MauEyeCare Complete System ===")
    
    try:
        # Test basic imports
        print("1. Testing basic imports...")
        import streamlit as st
        import pandas as pd
        import datetime
        import numpy as np
        from PIL import Image
        print("   ✓ Basic imports successful")
        
        # Test database
        print("2. Testing database...")
        import db
        db.init_db()
        patients = db.get_patients()
        print(f"   ✓ Database working: {len(patients)} patients")
        
        # Test config
        print("3. Testing config...")
        from config import CONFIG
        token = CONFIG.get('WHATSAPP_ACCESS_TOKEN')
        print(f"   ✓ Config loaded: {bool(token)}")
        
        # Test inventory
        print("4. Testing inventory...")
        from modules.inventory_utils import get_inventory_dict
        inventory = get_inventory_dict()
        print(f"   ✓ Inventory loaded: {len(inventory)} items")
        
        # Test real spectacle data
        print("5. Testing real spectacle data...")
        from modules.real_spectacle_data import REAL_SPECTACLE_INVENTORY, get_recommendations_by_face_shape
        print(f"   ✓ Real spectacle data: {len(REAL_SPECTACLE_INVENTORY)} items")
        
        # Test face shape recommendations
        recs = get_recommendations_by_face_shape("Wide/Round", 30, "Male")
        print(f"   ✓ Face recommendations working: {len(recs['face_shape_recs']['best_frames'])} frames")
        
        # Test DOCX generation
        print("6. Testing DOCX generation...")
        from modules.enhanced_docx_utils import generate_professional_prescription_docx
        docx_data = generate_professional_prescription_docx(
            {'Ray-Ban Aviator Classic RB3025': 1}, 'Dr Danish', 'Test Patient', 30, 'Male', 
            'Test advice', {}, [], {'Ray-Ban Aviator Classic RB3025': {'dosage': '1 pair', 'timing': 'Daily use'}}
        )
        print(f"   ✓ DOCX generated: {len(docx_data)} bytes")
        
        # Test camera module
        print("7. Testing camera module...")
        from modules.advanced_camera import FaceDetectionCamera, analyze_face_with_detection
        print("   ✓ Camera module loaded")
        
        # Test AI tools
        print("8. Testing AI tools...")
        from modules.ai_doctor_tools import analyze_symptoms_ai
        print("   ✓ AI tools loaded")
        
        print("\n🎉 ALL TESTS PASSED! System ready to run.")
        print("\nTo start the application, run:")
        print("python -m streamlit run app_complete.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_system()