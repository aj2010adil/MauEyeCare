#!/usr/bin/env python3
"""
Test script for MauEyeCare application
Tests all major components without running Streamlit
"""

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL")
    except ImportError as e:
        print(f"❌ PIL: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        import db
        db.init_db()
        print("✅ Database initialized")
        
        # Test adding a patient
        patient_id = db.add_patient("Test Patient", 30, "Male", "1234567890")
        print(f"✅ Patient added with ID: {patient_id}")
        
        # Test getting patients
        patients = db.get_patients()
        print(f"✅ Retrieved {len(patients)} patients")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_modules():
    """Test application modules"""
    print("\n📦 Testing modules...")
    
    try:
        from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
        print(f"✅ Spectacle database loaded: {len(COMPREHENSIVE_SPECTACLE_DATABASE)} items")
    except Exception as e:
        print(f"❌ Spectacle database: {e}")
        return False
    
    try:
        from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
        print(f"✅ Medicine database loaded: {len(COMPREHENSIVE_MEDICINE_DATABASE)} items")
    except Exception as e:
        print(f"❌ Medicine database: {e}")
        return False
    
    try:
        from modules.inventory_utils import get_inventory_dict, add_or_update_inventory
        inventory = get_inventory_dict()
        print(f"✅ Inventory system working: {len(inventory)} items")
    except Exception as e:
        print(f"❌ Inventory system: {e}")
        return False
    
    try:
        from modules.whatsapp_utils import test_whatsapp_connection
        status = test_whatsapp_connection()
        print(f"✅ WhatsApp utils: {'Demo mode' if status.get('demo') else 'Connected'}")
    except Exception as e:
        print(f"❌ WhatsApp utils: {e}")
        return False
    
    try:
        from modules.google_drive_integration import drive_integrator
        status = drive_integrator.test_drive_connection()
        print(f"✅ Google Drive: {'Demo mode' if status.get('demo') else 'Connected'}")
    except Exception as e:
        print(f"❌ Google Drive: {e}")
        return False
    
    return True

def test_prescription_features():
    """Test prescription generation features"""
    print("\n📋 Testing prescription features...")
    
    try:
        # Test sphere range generation
        sphere_options = [""]
        for i in range(-2000, 2025, 25):
            value = i / 100
            if value > 0:
                sphere_options.append(f"+{value:.2f}")
            elif value < 0:
                sphere_options.append(f"{value:.2f}")
        
        print(f"✅ Sphere options generated: {len(sphere_options)} options (-20.00 to +20.00)")
        
        # Test cylinder options
        cylinder_options = [""]
        for i in range(-1000, 25, 25):
            value = i / 100
            if value != 0:
                cylinder_options.append(f"{value:.2f}")
        
        print(f"✅ Cylinder options generated: {len(cylinder_options)} options")
        
        # Test axis options
        axis_options = [""] + [str(i) for i in range(0, 181, 5)]
        print(f"✅ Axis options generated: {len(axis_options)} options (0-180)")
        
        return True
        
    except Exception as e:
        print(f"❌ Prescription features test failed: {e}")
        return False

def test_medicine_filtering():
    """Test medicine filtering functionality"""
    print("\n💊 Testing medicine filtering...")
    
    try:
        from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
        
        # Test external medicine filtering
        external_keywords = ['drop', 'ointment', 'gel', 'cream', 'solution']
        external_medicines = {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
                            if any(keyword in k.lower() for keyword in external_keywords)}
        print(f"✅ External medicines filtered: {len(external_medicines)} items")
        
        # Test internal medicine filtering
        internal_medicines = {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
                            if not any(keyword in k.lower() for keyword in external_keywords)}
        print(f"✅ Internal medicines filtered: {len(internal_medicines)} items")
        
        # Test category filtering
        categories = set(med['category'] for med in COMPREHENSIVE_MEDICINE_DATABASE.values())
        print(f"✅ Medicine categories available: {len(categories)} categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Medicine filtering test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 MauEyeCare Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Modules Test", test_modules),
        ("Prescription Features Test", test_prescription_features),
        ("Medicine Filtering Test", test_medicine_filtering)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("   streamlit run main_app.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)