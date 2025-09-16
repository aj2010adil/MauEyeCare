#!/usr/bin/env python3
"""
Image Manager for MauEyeCare
Handles image upload and storage for spectacles and other assets
"""

import streamlit as st
import base64
from PIL import Image
import io
import os
from datetime import datetime

class ImageManager:
    def __init__(self):
        self.upload_dir = "uploaded_images"
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def upload_image(self, uploaded_file, category="spectacle"):
        """Handle image upload and return file path"""
        if uploaded_file is not None:
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{category}_{timestamp}_{uploaded_file.name}"
                filepath = os.path.join(self.upload_dir, filename)
                
                # Save image
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                return filepath
            except Exception as e:
                st.error(f"Error uploading image: {str(e)}")
                return None
        return None
    
    def display_image(self, image_path, width=200):
        """Display image from file path"""
        try:
            if os.path.exists(image_path):
                st.image(image_path, width=width)
            else:
                st.info("Image not found")
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
    
    def get_image_base64(self, image_path):
        """Convert image to base64 for embedding"""
        try:
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        except:
            pass
        return None
    
    def image_uploader_widget(self, key, label="Upload Image"):
        """Reusable image uploader widget"""
        uploaded_file = st.file_uploader(
            label,
            type=['png', 'jpg', 'jpeg', 'gif'],
            key=key,
            help="Upload spectacle image (PNG, JPG, JPEG, GIF)"
        )
        
        if uploaded_file:
            # Show preview
            st.image(uploaded_file, width=200, caption="Preview")
            return uploaded_file
        return None

# Initialize global image manager
image_manager = ImageManager()