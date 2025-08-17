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
from modules.google_drive_integration import GoogleDriveIntegrator
from modules.whatsapp_utils import send_text_message
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
from modules.real_spectacle_images import load_spectacle_image
from modules.simple_camera import show_camera_with_preview, analyze_captured_photo

# Initialize database and integrations
db.init_db()
drive_integrator = GoogleDriveIntegrator()

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
        
        # WhatsApp & Google Drive Status
        st.markdown("---")
        st.markdown("**🔗 Integration Status:**")
        
        # Test WhatsApp
        from modules.whatsapp_utils import test_whatsapp_connection
        whatsapp_status = test_whatsapp_connection()
        
        if whatsapp_status['success']:
            if whatsapp_status.get('demo'):
                st.warning("📱 WhatsApp: Demo Mode")
            else:
                st.success("📱 WhatsApp: Connected")
        else:
            st.error("📱 WhatsApp: Not Configured")
        
        # Test Google Drive
        drive_status = drive_integrator.test_drive_connection()
        if drive_status['success']:
            st.success("☁️ Google Drive: Connected")
        else:
            st.error("☁️ Google Drive: Not Configured")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👥 Patient Registration", 
        "👓 Spectacle Gallery", 
        "💊 Medicine Gallery",
        "📸 AI Camera Analysis",
        "📋 Patient History",
        "📤 Prescription & Sharing",
        "🔧 Integration Setup"
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
            
            if st.button("📤 Generate & Share Prescription", type="primary"):
                if selected_spectacles or selected_medicines:
                    # Create prescription HTML
                    prescription_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MauEyeCare Prescription - {patient_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
        .header {{ text-align: center; color: #2E86AB; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .patient-info {{ background: white; padding: 20px; margin: 10px 0; border-radius: 10px; border-left: 5px solid #2E86AB; }}
        .prescription {{ background: white; padding: 20px; margin: 10px 0; border-radius: 10px; }}
        .item {{ background: #f0f8ff; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .total {{ background: #e8f5e8; padding: 15px; border-radius: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👁️ MauEyeCare Optical Center</h1>
        <p>Dr. Danish - Eye Care Specialist | Reg. No: UPS 2908</p>
        <p>📞 Phone: +91 92356-47410 | 📧 Email: tech@maueyecare.com</p>
    </div>
    
    <div class="patient-info">
        <h3>👤 Patient Information</h3>
        <p><strong>Name:</strong> {patient_name}</p>
        <p><strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')}</p>
        <p><strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')}</p>
        <p><strong>Issue:</strong> {st.session_state.get('patient_issue', 'N/A')}</p>
        <p><strong>Date:</strong> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>"""
                    
                    # Add eye prescription
                    rx_table = st.session_state.get('rx_table', {})
                    if rx_table and (rx_table.get('OD', {}).get('Sphere') or rx_table.get('OS', {}).get('Sphere')):
                        prescription_html += """
    <div class="prescription">
        <h3>👁️ Eye Prescription (RX)</h3>"""
                        
                        for eye in ['OD', 'OS']:
                            eye_data = rx_table.get(eye, {})
                            if eye_data.get('Sphere'):
                                eye_name = "Right Eye" if eye == "OD" else "Left Eye"
                                prescription_html += f"""
        <div class="item">
            <strong>{eye} ({eye_name}):</strong> 
            SPH {eye_data.get('Sphere', '')} 
            CYL {eye_data.get('Cylinder', '')} 
            AXIS {eye_data.get('Axis', '')}
        </div>"""
                        
                        prescription_html += "</div>"
                    
                    # Add selected spectacles
                    if selected_spectacles:
                        prescription_html += """
    <div class="prescription">
        <h3>👓 Recommended Spectacles</h3>"""
                        
                        total_spec_cost = 0
                        for spec_name in selected_spectacles:
                            if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                total_price = spec_data['price'] + spec_data['lens_price']
                                total_spec_cost += total_price
                                
                                prescription_html += f"""
        <div class="item">
            <strong>{spec_data['brand']} {spec_data['model']}</strong><br>
            Material: {spec_data['material']} | Shape: {spec_data['shape']}<br>
            Frame: ₹{spec_data['price']:,} + Lens: ₹{spec_data['lens_price']:,} = <strong>₹{total_price:,}</strong>
        </div>"""
                        
                        prescription_html += f"""
        <div class="total">Total Spectacle Cost: ₹{total_spec_cost:,}</div>
    </div>"""
                    
                    # Add selected medicines
                    if selected_medicines:
                        prescription_html += """
    <div class="prescription">
        <h3>💊 Prescribed Medicines</h3>"""
                        
                        total_med_cost = 0
                        for med_name, quantity in selected_medicines.items():
                            if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
                                med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
                                total_price = med_data['price'] * quantity
                                total_med_cost += total_price
                                
                                prescription_html += f"""
        <div class="item">
            <strong>{med_name}</strong><br>
            Category: {med_data['category']} | Quantity: {quantity}<br>
            Price: ₹{med_data['price']} x {quantity} = <strong>₹{total_price}</strong><br>
            Prescription Required: {'Yes' if med_data['prescription_required'] else 'No'}
        </div>"""
                        
                        prescription_html += f"""
        <div class="total">Total Medicine Cost: ₹{total_med_cost:,}</div>
    </div>"""
                    
                    # Add advice and footer
                    prescription_html += f"""
    <div class="prescription">
        <h3>📋 Doctor's Advice</h3>
        <p>{st.session_state.get('advice', 'Regular eye checkup recommended')}</p>
    </div>
    
    <div class="header">
        <p><strong>Dr. Danish</strong><br>Eye Care Specialist<br>MauEyeCare Optical Center</p>
        <p>📞 For queries: +91 92356-47410</p>
    </div>
</body>
</html>"""
                    
                    # Upload to Google Drive
                    with st.spinner("📤 Uploading prescription to Google Drive..."):
                        drive_integrator = GoogleDriveIntegrator()
                        result = drive_integrator.upload_prescription_to_drive(
                            prescription_html, 
                            patient_name
                        )
                    
                    if result['success']:
                        st.success("✅ Prescription uploaded to Google Drive successfully!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"📁 **File:** {result['filename']}")
                            st.markdown(f"🔗 **[View Prescription]({result['link']})**")
                        
                        with col2:
                            st.info(f"📂 **Folder:** {result['folder_name']}")
                            st.markdown(f"📂 **[Open Folder]({result['folder_link']})**")
                        
                        # Send to patient via WhatsApp
                        patient_mobile = st.session_state.get('patient_mobile')
                        if patient_mobile:
                            st.markdown("---")
                            st.subheader("📱 Send to Patient")
                            
                            # WhatsApp message
                            whatsapp_message = f"""Hi {patient_name},

Your prescription from MauEyeCare is ready! 👁️

📄 View your prescription: {result['link']}

📞 For any queries, call: +91 92356-47410

Thank you for choosing MauEyeCare!
- Dr. Danish"""
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("📱 Send via WhatsApp API", type="primary"):
                                    try:
                                        # Format mobile number
                                        mobile = patient_mobile.replace("+91", "").replace(" ", "").replace("-", "")
                                        if not mobile.startswith("91"):
                                            mobile = "91" + mobile
                                        
                                        # Send WhatsApp message
                                        whatsapp_result = send_text_message(mobile, whatsapp_message)
                                        
                                        if whatsapp_result.get('success'):
                                            if whatsapp_result.get('demo'):
                                                st.info(f"📱 Demo Mode: {whatsapp_result.get('details')}")
                                            else:
                                                st.success(f"✅ WhatsApp sent to +91 {patient_mobile}")
                                        else:
                                            st.error(f"❌ WhatsApp failed: {whatsapp_result.get('error', 'Unknown error')}")
                                            
                                    except Exception as e:
                                        st.error(f"❌ WhatsApp error: {str(e)}")
                                
                                # Alternative WhatsApp Web method
                                if st.button("🌐 Open WhatsApp Web"):
                                    from modules.whatsapp_utils import send_via_whatsapp_web
                                    
                                    whatsapp_url = send_via_whatsapp_web(patient_mobile, whatsapp_message)
                                    st.markdown(f"**[Click here to send via WhatsApp Web]({whatsapp_url})**")
                                    st.info("📱 This will open WhatsApp Web in your browser")
                            
                            with col2:
                                # Copy message button
                                st.text_area("📋 Copy this message to send manually:", 
                                           value=whatsapp_message, 
                                           height=120)
                                
                                # Direct link
                                st.text_input("🔗 Prescription Link:", 
                                            value=result['link'], 
                                            help="Copy this link to share directly")
                        
                        else:
                            st.warning("📱 Patient mobile number required for WhatsApp")
                        
                        # Update inventory
                        st.markdown("---")
                        with st.spinner("📦 Updating inventory..."):
                            for med_name, quantity in selected_medicines.items():
                                reduce_inventory(med_name, quantity)
                            
                            for spec_name in selected_spectacles:
                                reduce_inventory(spec_name, 1)
                        
                        st.success("📦 Inventory updated automatically")
                        
                        # Clear selections
                        if st.button("🔄 Clear Selections & Start New Prescription"):
                            if 'selected_spectacles' in st.session_state:
                                del st.session_state['selected_spectacles']
                            if 'selected_medicines' in st.session_state:
                                del st.session_state['selected_medicines']
                            st.rerun()
                    
                    else:
                        st.error(f"❌ Upload failed: {result['error']}")
                        st.info("💡 Please check your Google Drive configuration")
                    
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine")
        else:
            st.warning("⚠️ Please select a patient first")

    # --- Integration Setup Tab ---
    with tab7:
        from integration_config import show_integration_setup
        show_integration_setup()

if __name__ == "__main__":
    main()