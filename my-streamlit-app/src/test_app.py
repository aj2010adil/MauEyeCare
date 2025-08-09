"""
Test script for MauEyeCare functionality
"""
import db
from modules.pdf_utils import generate_pdf
from modules.inventory_utils import get_inventory_dict

def test_database():
    """Test database operations"""
    print("Testing database...")
    
    # Initialize database
    db.init_db()
    print("[OK] Database initialized")
    
    # Test patient operations
    patient_id = db.add_patient("Test Patient", 30, "Male", "1234567890")
    print(f"[OK] Patient added with ID: {patient_id}")
    
    patients = db.get_patients()
    print(f"[OK] Retrieved {len(patients)} patients")
    
    return patient_id

def test_inventory():
    """Test inventory operations"""
    print("\nTesting inventory...")
    
    inventory = get_inventory_dict()
    print(f"[OK] Retrieved inventory with {len(inventory)} items")
    
    # Show first 3 items
    for i, (item, qty) in enumerate(list(inventory.items())[:3]):
        print(f"  - {item}: {qty}")
    
    return inventory

def test_pdf_generation():
    """Test PDF generation"""
    print("\nTesting PDF generation...")
    
    try:
        pdf_data = generate_pdf(
            prescription={"Test Medicine": 1},
            dosage="Test dosage",
            eye_test="Test eye test",
            doctor_name="Dr Test",
            patient_name="Test Patient",
            age=30,
            gender="Male",
            advice="Test advice",
            rx_table={"OD": {"Sphere": "+1.00", "Cylinder": "", "Axis": "", "Prism": ""}},
            recommendations=["Single Vision"]
        )
        print(f"[OK] PDF generated successfully ({len(pdf_data)} bytes)")
        return True
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return False

def test_medical_tests():
    """Test medical tests functionality"""
    print("\nTesting medical tests...")
    
    try:
        patient_id = 1  # Use first patient
        db.add_medical_tests(
            patient_id,
            "Normal (120/80)",
            "Normal (70-100)",
            "Normal",
            "Negative",
            "Normal",
            "Normal (10-21 mmHg)",
            "Normal",
            "Normal",
            "Patent"
        )
        print("[OK] Medical tests added")
        
        tests = db.get_medical_tests(patient_id)
        print(f"[OK] Retrieved {len(tests)} medical test records")
        return True
    except Exception as e:
        print(f"[ERROR] Medical tests failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("MauEyeCare Functionality Test")
    print("=" * 50)
    
    try:
        # Test core functionality
        patient_id = test_database()
        inventory = test_inventory()
        pdf_success = test_pdf_generation()
        medical_success = test_medical_tests()
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print(f"[OK] Database: Working")
        print(f"[OK] Inventory: {len(inventory)} items available")
        print(f"[{'OK' if pdf_success else 'ERROR'}] PDF Generation: {'Working' if pdf_success else 'Failed'}")
        print(f"[{'OK' if medical_success else 'ERROR'}] Medical Tests: {'Working' if medical_success else 'Failed'}")
        print("=" * 50)
        
        if pdf_success and medical_success:
            print("SUCCESS: All core functionality is working!")
            print("Ready to run Streamlit app")
        else:
            print("WARNING: Some features need attention")
            
    except Exception as e:
        print(f"FAILED: Test failed: {e}")

if __name__ == "__main__":
    main()