#!/usr/bin/env python
"""Test Interactive Virtual Try-On Feature"""

import numpy as np
from PIL import Image
from modules.interactive_virtual_tryon import apply_spectacle_overlay

def test_virtual_tryon():
    """Test the virtual try-on functionality"""
    print("Testing Interactive Virtual Try-On...")
    
    # Create a dummy patient photo (face-like image)
    patient_photo = Image.new('RGB', (400, 500), 'lightblue')
    
    # Test spectacle overlay
    spec_name = "Ray-Ban Aviator Classic RB3025"
    
    try:
        result_image = apply_spectacle_overlay(patient_photo, spec_name)
        
        if result_image:
            print("✅ Virtual try-on overlay applied successfully")
            print(f"✅ Result image size: {result_image.size}")
            return True
        else:
            print("❌ Failed to apply spectacle overlay")
            return False
            
    except Exception as e:
        print(f"❌ Error in virtual try-on: {e}")
        return False

if __name__ == "__main__":
    success = test_virtual_tryon()
    if success:
        print("\n🎉 Interactive Virtual Try-On feature is working!")
    else:
        print("\n⚠️ Virtual Try-On feature needs debugging")