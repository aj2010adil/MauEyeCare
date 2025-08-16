#!/usr/bin/env python
"""
Streamlit app with camera integration for face analysis
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys, os
sys.path.append(os.path.dirname(__file__))

from modules.camera_face_analysis import capture_webcam_photo, analyze_face_with_ai, get_face_shape_basic, create_spectacle_shopping_list
from modules.inventory_utils import add_or_update_inventory
import db

def camera_spectacle_app():
    """Camera-based spectacle recommendation app"""
    
    st.title("📸 AI Spectacle Recommendation System")
    st.markdown("*Capture patient photo and get AI-powered spectacle recommendations*")
    
    # Patient info input
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Patient Name", value="John Doe")
        age = st.number_input("Age", min_value=5, max_value=100, value=35)
    
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        prescription_strength = st.selectbox("Prescription Strength", ["No prescription", "Mild (-1 to +1)", "Moderate (-3 to +3)", "Strong (>3)"])
    
    st.markdown("---")
    
    # Camera capture section
    st.subheader("📷 Capture Patient Photo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Option 1: Use Webcam**")
        
        if st.button("📸 Capture Photo", type="primary", key="capture_btn"):
            with st.spinner("Accessing camera..."):
                image, message = capture_webcam_photo()
                
            if image is not None:
                st.success(message)
                st.session_state['captured_image'] = image
                st.session_state['image_source'] = 'camera'
            else:
                st.error(message)
                st.info("💡 **Troubleshooting:**")
                st.info("• Make sure camera is connected")
                st.info("• Allow camera permissions in browser")
                st.info("• Try uploading a photo instead")
    
    with col2:
        st.markdown("**Option 2: Upload Photo**")
        
        uploaded_file = st.file_uploader(
            "Choose patient photo", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear front-facing photo of the patient"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            st.session_state['captured_image'] = image_array
            st.session_state['image_source'] = 'upload'
            st.success("Photo uploaded successfully!")
    
    # Display captured/uploaded image
    if 'captured_image' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Patient Photo Analysis")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(st.session_state['captured_image'], caption=f"Patient: {patient_name}", width=300)
            
            # Analysis buttons
            if st.button("🔍 Basic Face Analysis", key="basic_analysis"):
                with st.spinner("Analyzing face shape..."):
                    face_shape, recommendations = get_face_shape_basic(st.session_state['captured_image'])
                    st.session_state['basic_analysis'] = {
                        'face_shape': face_shape,
                        'recommendations': recommendations
                    }
            
            if st.button("🤖 AI-Powered Analysis", type="primary", key="ai_analysis"):
                with st.spinner("AI analyzing face and generating recommendations..."):
                    ai_recommendations = analyze_face_with_ai(
                        st.session_state['captured_image'], 
                        patient_name, 
                        age, 
                        gender
                    )
                    st.session_state['ai_recommendations'] = ai_recommendations
        
        with col2:
            # Display basic analysis results
            if 'basic_analysis' in st.session_state:
                st.markdown("### 🔍 Basic Face Analysis")
                analysis = st.session_state['basic_analysis']
                
                st.success(f"**Face Shape:** {analysis['face_shape']}")
                
                st.markdown("**Recommendations:**")
                for rec in analysis['recommendations']:
                    if rec.startswith('✓'):
                        st.success(rec)
                    elif rec.startswith('✗'):
                        st.warning(rec)
                    else:
                        st.info(rec)
            
            # Display AI analysis results
            if 'ai_recommendations' in st.session_state:
                st.markdown("### 🤖 AI-Powered Recommendations")
                
                if "error" not in st.session_state['ai_recommendations'].lower():
                    st.success("AI analysis completed!")
                    
                    # Display recommendations in expandable sections
                    with st.expander("📋 Full AI Recommendations", expanded=True):
                        st.write(st.session_state['ai_recommendations'])
                    
                    # Extract shopping list
                    shopping_items = create_spectacle_shopping_list(st.session_state['ai_recommendations'])
                    
                    if shopping_items:
                        st.markdown("### 🛒 Recommended Items for Inventory")
                        
                        for item in shopping_items:
                            col_item, col_btn = st.columns([3, 1])
                            with col_item:
                                st.write(f"• {item}")
                            with col_btn:
                                if st.button("➕", key=f"add_{item}", help=f"Add {item} to inventory"):
                                    add_or_update_inventory(item, 5)
                                    st.success(f"Added {item}!")
                        
                        # Bulk add button
                        if st.button("🛒 Add All Recommended Items to Inventory", type="primary"):
                            for item in shopping_items:
                                add_or_update_inventory(item, 5)
                            st.success(f"Added {len(shopping_items)} recommended items to inventory!")
                            st.balloons()
                else:
                    st.error("AI Analysis Error:")
                    st.error(st.session_state['ai_recommendations'])
    
    # Instructions section
    st.markdown("---")
    st.subheader("📖 How to Use")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📸 Photo Capture Tips:**
        - Ensure good lighting
        - Patient should face camera directly
        - Remove existing glasses if possible
        - Keep face centered in frame
        - Avoid shadows on face
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI Analysis Features:**
        - Face shape detection
        - Frame style recommendations
        - Color and material suggestions
        - Age-appropriate styles
        - Professional vs casual options
        """)

if __name__ == "__main__":
    # Initialize database
    db.init_db()
    
    # Run the camera app
    camera_spectacle_app()