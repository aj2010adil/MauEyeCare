#!/usr/bin/env python
"""
Simple test suite for MauEyeCare features
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_all_features():
    """Test all major features"""
    print("=" * 50)
    print("MauEyeCare Feature Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Database
    total_tests += 1
    try:
        import db
        db.init_db()
        patient_id = db.add_patient("Test Patient", 30, "Male", "9876543210")
        patients = db.get_patients()
        print(f"[PASS] Database - Added patient ID: {patient_id}, Total patients: {len(patients)}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Database - {e}")
    
    # Test 2: Spectacle Database
    total_tests += 1
    try:
        from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
        total_specs = len(COMPREHENSIVE_SPECTACLE_DATABASE)
        print(f"[PASS] Spectacle Database - {total_specs} spectacles loaded")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Spectacle Database - {e}")
    
    # Test 3: Medicine Database
    total_tests += 1
    try:
        from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
        total_meds = len(COMPREHENSIVE_MEDICINE_DATABASE)
        print(f"[PASS] Medicine Database - {total_meds} medicines loaded")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Medicine Database - {e}")
    
    # Test 4: PDF Generation
    total_tests += 1
    try:
        from modules.pdf_utils import generate_pdf
        pdf_bytes = generate_pdf(
            {"Eye Drops": 1}, "", "", "Dr Danish", 
            "Test Patient", 30, "Male", "Test advice", 
            {"OD": {"Sphere": "+1.00"}}, ["Single Vision"]
        )
        if isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 100:
            print(f"[PASS] PDF Generation - {len(pdf_bytes)} bytes generated")
            tests_passed += 1
        else:
            print("[FAIL] PDF Generation - Invalid output")
    except Exception as e:
        print(f"[FAIL] PDF Generation - {e}")
    
    # Test 5: Virtual Try-On
    total_tests += 1
    try:
        from modules.interactive_virtual_tryon import apply_spectacle_overlay
        from PIL import Image
        patient_photo = Image.new('RGB', (400, 500), 'lightblue')
        result = apply_spectacle_overlay(patient_photo, "Ray-Ban Aviator Classic RB3025")
        if result:
            print(f"[PASS] Virtual Try-On - Image size: {result.size}")
            tests_passed += 1
        else:
            print("[FAIL] Virtual Try-On - No result")
    except Exception as e:
        print(f"[FAIL] Virtual Try-On - {e}")
    
    # Test 6: AI Tools
    total_tests += 1
    try:
        from modules.ai_doctor_tools import analyze_symptoms_ai
        print("[PASS] AI Tools - Functions imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] AI Tools - {e}")
    
    # Test 7: WhatsApp Integration
    total_tests += 1
    try:
        from modules.whatsapp_utils import send_text_message
        print("[PASS] WhatsApp Integration - Functions imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] WhatsApp Integration - {e}")
    
    # Test 8: User Guide
    total_tests += 1
    try:
        from modules.doctor_user_guide import create_doctor_user_guide
        print("[PASS] User Guide - Functions imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] User Guide - {e}")
    
    # Summary
    print("=" * 50)
    print(f"TEST RESULTS: {tests_passed}/{total_tests} passed")
    print("=" * 50)
    
    if tests_passed == total_tests:
        print("ALL TESTS PASSED! System is ready.")
        return True
    elif tests_passed >= total_tests * 0.8:
        print("Most tests passed. System is mostly functional.")
        return True
    else:
        print("Multiple failures. System needs debugging.")
        return False

if __name__ == "__main__":
    success = test_all_features()
    
    if success:
        print("\nStarting application...")
        print("Run: streamlit run app_final_with_product_page.py --server.port 8507")
        print("Access at: http://localhost:8507")
    else:
        print("\nFix issues before running the application.")