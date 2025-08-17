#!/usr/bin/env python3
"""
MauEyeCare - Complete AI-Powered Eye Care System
Main Application File
"""

import streamlit as st
import pandas as pd
import sys, os
import datetime
import numpy as np
from PIL import Image
import json

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Core imports
import db
from modules.pdf_utils import generate_pdf
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
from modules.real_spectacle_images import load_spectacle_image
from modules.simple_camera import show_camera_with_preview, analyze_captured_photo

# Initialize database
db.init_db()

def populate_inventory():
    """Populate inventory with spectacles and medicines"""
    # Add spectacles
    for item_name, item_data in COMPREHENSIVE_SPECTACLE_DATABASE.items():
        import random
        stock = random.randint(5, 25)
        add_or_update_inventory(item_name, stock)
    
    # Add medicines
    for item_name, item_data in COMPREHENSIVE_MEDICINE_DATABASE.items():
        import random
        stock = random.randint(10, 50)
        add_or_update_inventory(item_name, stock)

def main():
    st.set_page_config(
        page_title="MauEyeCare", 
        page_icon="👁️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("👁️ MauEyeCare - AI Eye Care System")
    st.markdown("*Complete AI-Powered Eye Care with Inventory Management*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Load Complete Database"):
            with st.spinner("Loading complete database..."):
                populate_inventory()
            st.success(f"✅ Loaded {len(COMPREHENSIVE_SPECTACLE_DATABASE)} spectacles and {len(COMPREHENSIVE_MEDICINE_DATABASE)} medicines!")
        
        st.markdown("---")
        st.markdown("**📊 Database Stats:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👓 Spectacles", len(COMPREHENSIVE_SPECTACLE_DATABASE))
            st.metric("💊 Medicines", len(COMPREHENSIVE_MEDICINE_DATABASE))
        
        with col2:
            inventory = get_inventory_dict()
            st.metric("📦 Inventory Items", len(inventory))
            patients = db.get_patients()
            st.metric("👥 Patients", len(patients))
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Gender: {st.session_state.get('gender', 'N/A')}")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Patient Registration", 
        "👓 Spectacle Gallery", 
        "💊 Medicine Gallery",
        "📸 AI Camera Analysis",
        "📋 Patient History",
        "📄 Prescription Generator"
    ])

    # --- Patient Registration Tab ---
    with tab1:
        st.header("👥 Patient Registration & Information")
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", placeholder="Enter first name")
                last_name = st.text_input("Last Name", placeholder="Enter last name")
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                contact = st.text_input("Mobile Number", placeholder="Enter mobile number")
                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Other"]
                advice = st.selectbox("Advice/Notes", advice_options)
            
            patient_name = f"{first_name} {last_name}".strip()
            
            # Eye Prescription Section
            st.markdown("**👁️ Eye Prescription (RX)**")
            
            col_od, col_os = st.columns(2)
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+2.00", "+2.50", "+3.00", 
                            "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-2.00", "-2.50", "-3.00"]
            
            with col_od:
                st.markdown("**OD (Right Eye)**")
                od_sphere = st.selectbox("Sphere OD", sphere_options, key="sphere_od")
                od_cylinder = st.selectbox("Cylinder OD", ["", "-0.25", "-0.50", "-0.75", "-1.00"], key="cylinder_od")
                od_axis = st.selectbox("Axis OD", ["", "90", "180", "45", "135"], key="axis_od")
            
            with col_os:
                st.markdown("**OS (Left Eye)**")
                os_sphere = st.selectbox("Sphere OS", sphere_options, key="sphere_os")
                os_cylinder = st.selectbox("Cylinder OS", ["", "-0.25", "-0.50", "-0.75", "-1.00"], key="cylinder_os")
                os_axis = st.selectbox("Axis OS", ["", "90", "180", "45", "135"], key="axis_os")
            
            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis}
            }
            
            submitted = st.form_submit_button("💾 Save Patient", type="primary")
            
            if submitted and patient_name:
                # Save patient
                patients = db.get_patients()
                found = False
                for p in patients:
                    if p[1].lower() == patient_name.lower() and p[4] == contact:
                        patient_id = p[0]
                        found = True
                        break
                if not found:
                    patient_id = db.add_patient(patient_name, age, gender, contact)
                
                # Store in session
                st.session_state.update({
                    'patient_id': patient_id,
                    'patient_name': patient_name,
                    'patient_mobile': contact,
                    'age': age,
                    'gender': gender,
                    'advice': advice,
                    'patient_issue': patient_issue,
                    'rx_table': rx_table
                })
                
                st.success(f"✅ Patient {patient_name} saved successfully!")
                st.info("🎯 Now go to 'AI Camera Analysis' tab to capture photo and get recommendations!")

    # --- Spectacle Gallery Tab ---
    with tab2:
        st.header("👓 Spectacle Gallery")
        st.markdown(f"*Browse our collection of {len(COMPREHENSIVE_SPECTACLE_DATABASE)} spectacles*")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox("Category", 
                ["All", "Luxury", "Mid-Range", "Indian", "Budget", "Progressive", "Kids", "Safety", "Reading"])
        
        with col2:
            price_range = st.selectbox("Price Range", 
                ["All", "Budget (≤₹5,000)", "Mid-Range (₹5,001-15,000)", "Luxury (>₹15,000)"])
        
        with col3:
            brands = sorted(list(set([spec['brand'] for spec in COMPREHENSIVE_SPECTACLE_DATABASE.values()])))
            brand_filter = st.selectbox("Brand", ["All"] + brands)
        
        # Apply filters
        filtered_specs = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
        
        if category_filter != "All":
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['category'] == category_filter}
        
        if brand_filter != "All":
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['brand'] == brand_filter}
        
        if price_range != "All":
            if "Budget" in price_range:
                filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] <= 5000}
            elif "Mid-Range" in price_range:
                filtered_specs = {k: v for k, v in filtered_specs.items() if 5000 < v['price'] <= 15000}
            elif "Luxury" in price_range:
                filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] > 15000}
        
        # Display gallery
        st.markdown(f"### 🖼️ Spectacle Gallery ({len(filtered_specs)} items)")
        
        cols = st.columns(4)
        
        for i, (spec_name, spec_data) in enumerate(list(filtered_specs.items())[:16]):
            with cols[i % 4]:
                # Load and display image
                spec_image = load_spectacle_image(spec_name)
                st.image(spec_image, width=180)
                
                # Product info
                st.markdown(f"**{spec_data['brand']}**")
                st.markdown(f"{spec_data['model']}")
                
                total_price = spec_data['price'] + spec_data['lens_price']
                st.markdown(f"**₹{total_price:,}**")
                st.markdown(f"{spec_data['material']} | {spec_data['shape']}")
                
                # Add to prescription button
                if st.button(f"➕ Add to Prescription", key=f"add_spec_{i}"):
                    if 'selected_spectacles' not in st.session_state:
                        st.session_state['selected_spectacles'] = []
                    
                    if spec_name not in st.session_state['selected_spectacles']:
                        st.session_state['selected_spectacles'].append(spec_name)
                        st.success(f"Added {spec_data['brand']} {spec_data['model']}")
                    else:
                        st.warning("Already added to prescription")

    # --- Medicine Gallery Tab ---
    with tab3:
        st.header("💊 Medicine Gallery")
        st.markdown(f"*Browse our collection of {len(COMPREHENSIVE_MEDICINE_DATABASE)} medicines*")
        
        # Medicine filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            med_category = st.selectbox("Medicine Category", 
                ["All", "Antibiotic", "Anti-inflammatory", "Lubricant", "Antihistamine", "Antiviral"])
        
        with col2:
            prescription_req = st.selectbox("Prescription Required", ["All", "Yes", "No"])
        
        with col3:
            condition_filter = st.selectbox("Condition", 
                ["All", "dry_eyes", "infection", "allergy", "inflammation", "glaucoma"])
        
        # Apply medicine filters
        filtered_medicines = COMPREHENSIVE_MEDICINE_DATABASE.copy()
        
        if med_category != "All":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['category'] == med_category}
        
        if prescription_req != "All":
            req_bool = prescription_req == "Yes"
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['prescription_required'] == req_bool}
        
        if condition_filter != "All":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() 
                                if condition_filter in v.get('conditions', [])}
        
        # Display medicine gallery
        st.markdown(f"### 💊 Medicine Gallery ({len(filtered_medicines)} items)")
        
        cols = st.columns(3)
        
        for i, (med_name, med_data) in enumerate(list(filtered_medicines.items())[:12]):
            with cols[i % 3]:
                st.markdown(f"**{med_name}**")
                st.markdown(f"Category: {med_data['category']}")
                st.markdown(f"Price: ₹{med_data['price']}")
                st.markdown(f"Prescription: {'Required' if med_data['prescription_required'] else 'Not Required'}")
                
                if st.button(f"➕ Add to Prescription", key=f"add_med_{i}"):
                    if 'selected_medicines' not in st.session_state:
                        st.session_state['selected_medicines'] = {}
                    
                    if med_name in st.session_state['selected_medicines']:
                        st.session_state['selected_medicines'][med_name] += 1
                    else:
                        st.session_state['selected_medicines'][med_name] = 1
                    
                    st.success(f"Added {med_name}")

    # --- AI Camera Analysis Tab ---
    with tab4:
        st.header("📸 AI Camera Analysis")
        
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            
            st.success(f"👤 **Current Patient:** {patient_name} | Age: {age} | Gender: {gender}")
            
            st.markdown("### 📷 Face Analysis for Spectacle Recommendations")
            st.info("📸 **Click below to start camera and capture photo for AI analysis**")
            
            if st.button("📸 Start Camera Analysis", type="primary"):
                st.markdown("### 🤖 AI Face Analysis Camera")
                captured_image = show_camera_with_preview()
                
                if captured_image is not None:
                    st.session_state['analysis_photo'] = captured_image
                    
                    # Analyze the photo
                    with st.spinner("🔍 AI analyzing face shape and matching spectacles..."):
                        analysis_result = analyze_captured_photo(captured_image, patient_name, age, gender)
                    
                    st.session_state['analysis_result'] = analysis_result
                    
                    if analysis_result['status'] == 'success':
                        st.success("🎉 Face Analysis Complete!")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Face Shape", analysis_result["face_shape"])
                        
                        with col2:
                            st.metric("Confidence", f"{analysis_result['confidence']:.1f}%")
                        
                        with col3:
                            st.metric("Recommendations", len(analysis_result["recommended_spectacles"]))
                        
                        # Show recommended spectacles
                        st.markdown("### 👓 Recommended Spectacles")
                        
                        cols = st.columns(3)
                        
                        for i, spec_name in enumerate(analysis_result["recommended_spectacles"][:6]):
                            with cols[i % 3]:
                                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                    spec_image = load_spectacle_image(spec_name)
                                    
                                    st.image(spec_image, width=200)
                                    st.markdown(f"**{spec_data['brand']} {spec_data['model']}**")
                                    
                                    total_price = spec_data['price'] + spec_data['lens_price']
                                    st.markdown(f"**₹{total_price:,}**")
                                    
                                    if st.button(f"➕ Add to Prescription", key=f"rec_add_{i}"):
                                        if 'selected_spectacles' not in st.session_state:
                                            st.session_state['selected_spectacles'] = []
                                        
                                        if spec_name not in st.session_state['selected_spectacles']:
                                            st.session_state['selected_spectacles'].append(spec_name)
                                            st.success(f"Added {spec_data['brand']} {spec_data['model']}")
                    else:
                        st.error(f"❌ Analysis Failed: {analysis_result['message']}")
        else:
            st.warning("⚠️ **Patient Required**")
            st.info("Please go to the **'Patient Registration'** tab first and enter patient information.")

    # --- Patient History Tab ---
    with tab5:
        st.header("📋 Patient History & Records")
        
        patients = db.get_patients()
        
        col1, col2 = st.columns(2)
        with col1:
            search_mobile = st.text_input("🔍 Search by Mobile Number")
        with col2:
            search_name = st.text_input("🔍 Search by Name")
        
        filtered = [p for p in patients if (search_mobile in p[4]) and (search_name.lower() in p[1].lower())]
        
        st.write(f"📊 Found {len(filtered)} patient(s)")
        
        for p in filtered:
            with st.expander(f"👤 {p[1]} | Age: {p[2]} | Mobile: {p[4]}"):
                st.write(f"**Patient ID:** {p[0]}")
                st.write(f"**Gender:** {p[3]}")
                st.write(f"**Registration Date:** {p[5] if len(p) > 5 else 'N/A'}")
                
                if st.button(f"Select Patient", key=f"select_{p[0]}"):
                    st.session_state.update({
                        'patient_id': p[0],
                        'patient_name': p[1],
                        'age': p[2],
                        'gender': p[3],
                        'patient_mobile': p[4]
                    })
                    st.success(f"Selected patient: {p[1]}")

    # --- Prescription Generator Tab ---
    with tab6:
        st.header("📄 Prescription Generator")
        
        if 'patient_name' in st.session_state:
            patient_name = st.session_state['patient_name']
            
            st.success(f"👤 **Patient:** {patient_name}")
            
            # Show selected items
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👓 Selected Spectacles")
                selected_spectacles = st.session_state.get('selected_spectacles', [])
                
                if selected_spectacles:
                    for spec_name in selected_spectacles:
                        if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                            spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                            total_price = spec_data['price'] + spec_data['lens_price']
                            st.write(f"• {spec_data['brand']} {spec_data['model']} - ₹{total_price:,}")
                else:
                    st.info("No spectacles selected")
            
            with col2:
                st.markdown("### 💊 Selected Medicines")
                selected_medicines = st.session_state.get('selected_medicines', {})
                
                if selected_medicines:
                    for med_name, quantity in selected_medicines.items():
                        if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
                            med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
                            total_price = med_data['price'] * quantity
                            st.write(f"• {med_name} (Qty: {quantity}) - ₹{total_price}")
                else:
                    st.info("No medicines selected")
            
            # Generate prescription
            st.markdown("---")
            
            if st.button("📄 Generate Prescription PDF", type="primary"):
                if selected_spectacles or selected_medicines:
                    # Generate PDF
                    pdf_bytes = generate_pdf(
                        selected_medicines, 
                        "", "", "Dr Danish", 
                        patient_name, 
                        st.session_state.get('age', 30), 
                        st.session_state.get('gender', 'Male'), 
                        st.session_state.get('advice', 'Eye Care'), 
                        st.session_state.get('rx_table', {}), 
                        selected_spectacles
                    )
                    
                    # Download button
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.pdf"
                    
                    st.download_button(
                        label="📄 Download Prescription PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    
                    st.success("✅ Prescription generated successfully!")
                    
                    # Update inventory
                    for med_name, quantity in selected_medicines.items():
                        reduce_inventory(med_name, quantity)
                    
                    for spec_name in selected_spectacles:
                        reduce_inventory(spec_name, 1)
                    
                    st.info("📦 Inventory updated automatically")
                    
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine")
        else:
            st.warning("⚠️ Please select a patient first")

if __name__ == "__main__":
    main()