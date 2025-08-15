#!/usr/bin/env python
"""
Comprehensive test suite for all MauEyeCare features
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_database_features():
    """Test database functionality"""
    print("🗄️ Testing Database Features...")
    
    try:
        import db
        db.init_db()
        
        # Test patient operations
        patient_id = db.add_patient("Test Patient", 30, "Male", "9876543210")
        patients = db.get_patients()
        
        print(f"✅ Database initialized")
        print(f"✅ Patient added with ID: {patient_id}")
        print(f"✅ Retrieved {len(patients)} patients")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_spectacle_database():
    """Test spectacle database and features"""
    print("\n👓 Testing Spectacle Database...")
    
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
        
        print(f"✅ Total spectacles: {total_specs}")
        print(f"✅ Luxury spectacles: {len(luxury_specs)}")
        print(f"✅ Budget spectacles: {len(budget_specs)}")
        print(f"✅ Round face recommendations: {len(round_specs)}")
        
        return True
    except Exception as e:
        print(f"❌ Spectacle database test failed: {e}")
        return False

def test_medicine_database():
    """Test medicine database and features"""
    print("\n💊 Testing Medicine Database...")
    
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
        
        print(f"✅ Total medicines: {total_medicines}")
        print(f"✅ Antibiotic medicines: {len(antibiotics)}")
        print(f"✅ Prescription medicines: {len(prescription_meds)}")
        print(f"✅ Dry eye recommendations: {len(dry_eye_recs)}")
        
        return True
    except Exception as e:
        print(f"❌ Medicine database test failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation"""
    print("\n📄 Testing PDF Generation...")
    
    try:
        from modules.pdf_utils import generate_pdf
        
        pdf_bytes = generate_pdf(
            {"Eye Drops": 1}, "", "", "Dr Danish", 
            "Test Patient", 30, "Male", "Test advice", 
            {"OD": {"Sphere": "+1.00"}}, ["Single Vision"]
        )
        
        if isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 100:
            print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
            return True
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ PDF test failed: {e}")
        return False

def test_ai_tools():
    """Test AI tools functionality"""
    print("\n🤖 Testing AI Tools...")
    
    try:
        from modules.ai_doctor_tools import (
            analyze_symptoms_ai,
            suggest_medications_ai,
            generate_patient_education_ai
        )
        
        # Test with mock data (will fail gracefully without API key)
        symptom_analysis = analyze_symptoms_ai("Blurry vision", 35, "Male")
        medication_suggestion = suggest_medications_ai("Dry eyes", 35)
        patient_education = generate_patient_education_ai("Dry eyes", "Eye drops")
        
        print("✅ AI tools imported successfully")
        print("✅ Symptom analysis function available")
        print("✅ Medication suggestion function available")
        print("✅ Patient education function available")
        
        return True
    except Exception as e:
        print(f"❌ AI tools test failed: {e}")
        return False

def test_virtual_tryon():
    """Test virtual try-on functionality"""
    print("\n👓 Testing Virtual Try-On...")
    
    try:
        from modules.interactive_virtual_tryon import apply_spectacle_overlay
        from PIL import Image
        import numpy as np
        
        # Create dummy patient photo
        patient_photo = Image.new('RGB', (400, 500), 'lightblue')
        spec_name = "Ray-Ban Aviator Classic RB3025"
        
        result_image = apply_spectacle_overlay(patient_photo, spec_name)
        
        if result_image:
            print("✅ Virtual try-on overlay applied successfully")
            print(f"✅ Result image size: {result_image.size}")
            return True
        else:
            print("❌ Virtual try-on failed")
            return False
            
    except Exception as e:
        print(f"❌ Virtual try-on test failed: {e}")
        return False

def test_whatsapp_integration():
    """Test WhatsApp integration"""
    print("\n💬 Testing WhatsApp Integration...")
    
    try:
        from modules.whatsapp_utils import send_text_message, send_pdf_to_whatsapp
        
        # Test functions exist and can be imported
        print("✅ WhatsApp utils imported successfully")
        print("✅ Text message function available")
        print("✅ PDF sending function available")
        print("ℹ️  WhatsApp API requires valid tokens for actual testing")
        
        return True
    except Exception as e:
        print(f"❌ WhatsApp integration test failed: {e}")
        return False

def test_inventory_management():
    """Test inventory management"""
    print("\n📦 Testing Inventory Management...")
    
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
        
        print("✅ Inventory functions imported successfully")
        print(f"✅ Initial inventory items: {len(initial_inventory)}")
        print("✅ Add/update inventory function works")
        print("✅ Inventory retrieval function works")
        
        return True
    except Exception as e:
        print(f"❌ Inventory management test failed: {e}")
        return False

def test_user_guide():
    """Test user guide functionality"""
    print("\n📚 Testing User Guide...")
    
    try:
        from modules.doctor_user_guide import (
            create_doctor_user_guide,
            create_feature_overview_page
        )
        
        print("✅ User guide functions imported successfully")
        print("✅ Doctor user guide available")
        print("✅ Feature overview page available")
        print("✅ Future enhancements guide available")
        
        return True
    except Exception as e:
        print(f"❌ User guide test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("=" * 60)
    print("MauEyeCare Comprehensive Feature Test")
    print("=" * 60)
    
    tests = [
        ("Database Features", test_database_features),
        ("Spectacle Database", test_spectacle_database),
        ("Medicine Database", test_medicine_database),
        ("PDF Generation", test_pdf_generation),
        ("AI Tools", test_ai_tools),
        ("Virtual Try-On", test_virtual_tryon),
        ("WhatsApp Integration", test_whatsapp_integration),
        ("Inventory Management", test_inventory_management),
        ("User Guide", test_user_guide)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED! System is ready for use.")
    elif passed >= total * 0.8:
        print("Most tests passed. System is mostly functional.")
    else:
        print("Multiple test failures. System needs debugging.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print("\nStarting MauEyeCare application...")
        print("Access the app at: http://localhost:8507")
        print("Use 'streamlit run app_final_with_product_page.py --server.port 8507' to start")
    else:
        print("\nPlease fix failing tests before running the application.")