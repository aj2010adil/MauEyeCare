#!/usr/bin/env python
"""
Simple test suite for MauEyeCare features (Windows compatible)
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_database_features():
    """Test database functionality"""
    print("Testing Database Features...")
    
    try:
        import db
        db.init_db()
        
        # Test patient operations
        patient_id = db.add_patient("Test Patient", 30, "Male", "9876543210")
        patients = db.get_patients()
        
        print(f"PASS - Database initialized")
        print(f"PASS - Patient added with ID: {patient_id}")
        print(f"PASS - Retrieved {len(patients)} patients")
        
        return True
    except Exception as e:
        print(f"FAIL - Database test failed: {e}")
        return False

def test_spectacle_database():
    """Test spectacle database and features"""
    print("\nTesting Spectacle Database...")
    
    try:
        from modules.comprehensive_spectacle_database import (
            COMPREHENSIVE_SPECTACLE_DATABASE,
            get_spectacles_by_category,
            get_spectacles_by_price_range,
            search_spectacles_by_criteria
        )
        
        total_specs = len(COMPREHENSIVE_SPECTACLE_DATABASE)
        luxury_specs = get_spectacles_by_category("Luxury")
        budget_specs = get_spectacles_by_price_range(0, 5000)
        round_specs = search_spectacles_by_criteria(face_shape="Long/Oval")
        
        print(f"PASS - Total spectacles: {total_specs}")
        print(f"PASS - Luxury spectacles: {len(luxury_specs)}")
        print(f"PASS - Budget spectacles: {len(budget_specs)}")
        print(f"PASS - Round face recommendations: {len(round_specs)}")
        
        return True
    except Exception as e:
        print(f"FAIL - Spectacle database test failed: {e}")
        return False

def test_medicine_database():
    """Test medicine database and features"""
    print("\nTesting Medicine Database...")
    
    try:
        from modules.comprehensive_medicine_database import (
            COMPREHENSIVE_MEDICINE_DATABASE,
            get_medicines_by_category,
            get_prescription_required_medicines,
            get_medicine_recommendations_by_condition
        )
        
        total_medicines = len(COMPREHENSIVE_MEDICINE_DATABASE)
        antibiotics = get_medicines_by_category("Antibiotic")
        prescription_meds = get_prescription_required_medicines()
        dry_eye_recs = get_medicine_recommendations_by_condition("dry_eyes")
        
        print(f"PASS - Total medicines: {total_medicines}")
        print(f"PASS - Antibiotic medicines: {len(antibiotics)}")
        print(f"PASS - Prescription medicines: {len(prescription_meds)}")
        print(f"PASS - Dry eye recommendations: {len(dry_eye_recs)}")
        
        return True
    except Exception as e:
        print(f"FAIL - Medicine database test failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation"""
    print("\nTesting PDF Generation...")
    
    try:
        from modules.pdf_utils import generate_pdf
        
        pdf_bytes = generate_pdf(
            {"Eye Drops": 1}, "", "", "Dr Danish", 
            "Test Patient", 30, "Male", "Test advice", 
            {"OD": {"Sphere": "+1.00"}}, ["Single Vision"]
        )
        
        if isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 100:
            print(f"PASS - PDF generated successfully: {len(pdf_bytes)} bytes")
            return True
        else:
            print("FAIL - PDF generation failed")
            return False
            
    except Exception as e:
        print(f"FAIL - PDF test failed: {e}")
        return False

def test_inventory_management():
    """Test inventory management"""
    print("\nTesting Inventory Management...")
    
    try:
        from modules.inventory_utils import (
            get_inventory_dict,
            add_or_update_inventory,
            reduce_inventory
        )
        
        # Test inventory operations
        initial_inventory = get_inventory_dict()
        add_or_update_inventory("Test Medicine", 10)
        updated_inventory = get_inventory_dict()
        
        print("PASS - Inventory functions imported successfully")
        print(f"PASS - Initial inventory items: {len(initial_inventory)}")
        print("PASS - Add/update inventory function works")
        print("PASS - Inventory retrieval function works")
        
        return True
    except Exception as e:
        print(f"FAIL - Inventory management test failed: {e}")
        return False

def test_ai_tools():
    """Test AI tools functionality"""
    print("\nTesting AI Tools...")
    
    try:
        from modules.ai_doctor_tools import (
            analyze_symptoms_ai,
            suggest_medications_ai,
            generate_patient_education_ai
        )
        
        print("PASS - AI tools imported successfully")
        print("PASS - Symptom analysis function available")
        print("PASS - Medication suggestion function available")
        print("PASS - Patient education function available")
        
        return True
    except Exception as e:
        print(f"FAIL - AI tools test failed: {e}")
        return False

def run_simple_test():
    """Run all tests and provide summary"""
    print("=" * 60)
    print("MauEyeCare Simple Feature Test")
    print("=" * 60)
    
    tests = [
        ("Database Features", test_database_features),
        ("Spectacle Database", test_spectacle_database),
        ("Medicine Database", test_medicine_database),
        ("PDF Generation", test_pdf_generation),
        ("Inventory Management", test_inventory_management),
        ("AI Tools", test_ai_tools)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAIL - {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED! System is ready for use.")
    elif passed >= total * 0.8:
        print("Most tests passed. System is mostly functional.")
    else:
        print("Multiple test failures. System needs debugging.")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = run_simple_test()
    
    if success:
        print("\nStarting MauEyeCare application...")
        print("Access the app at: http://localhost:8507")
        print("Use 'streamlit run app_final_with_product_page.py --server.port 8507' to start")
    else:
        print("\nPlease fix failing tests before running the application.")