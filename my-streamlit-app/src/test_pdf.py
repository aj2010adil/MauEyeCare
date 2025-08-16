#!/usr/bin/env python
"""Test PDF generation to ensure it works correctly"""

from modules.pdf_utils import generate_pdf

def test_pdf_generation():
    """Test basic PDF generation"""
    print("Testing PDF generation...")
    
    # Sample data
    prescription = {"Eye Drops": 2, "Reading Glasses": 1}
    dosage = "2 drops twice daily"
    eye_test = "Vision 20/20"
    doctor_name = "Dr Danish"
    patient_name = "Test Patient"
    age = 35
    gender = "Male"
    advice = "Regular checkup recommended"
    rx_table = {
        "OD": {"Sphere": "+1.00", "Cylinder": "-0.50", "Axis": "90"},
        "OS": {"Sphere": "+1.25", "Cylinder": "-0.25", "Axis": "180"}
    }
    recommendations = ["Single Vision", "AR Coat"]
    
    try:
        pdf_bytes = generate_pdf(
            prescription, dosage, eye_test, doctor_name, 
            patient_name, age, gender, advice, rx_table, recommendations
        )
        
        if isinstance(pdf_bytes, (bytes, bytearray)):
            print(f"SUCCESS: PDF generated - {len(pdf_bytes)} bytes")
            
            # Save test PDF
            with open("test_prescription.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("Test PDF saved as 'test_prescription.pdf'")
            
            # Basic validation
            if len(pdf_bytes) > 1000 and pdf_bytes[:4] == b'%PDF':
                print("PDF format validation: PASSED")
                return True
            else:
                print("PDF format validation: FAILED")
                return False
        else:
            print(f"FAILED: Invalid PDF format - {type(pdf_bytes)}")
            return False
            
    except Exception as e:
        print(f"ERROR: PDF generation failed - {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n✅ PDF generation test PASSED")
    else:
        print("\n❌ PDF generation test FAILED")