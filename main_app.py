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
from datetime import timezone, timedelta
from io import BytesIO

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Core imports - optimized for speed
import db

# Lazy imports for better performance
@st.cache_data
def get_spectacle_database():
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    return COMPREHENSIVE_SPECTACLE_DATABASE

@st.cache_data
def get_medicine_database():
    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
    return COMPREHENSIVE_MEDICINE_DATABASE

# Initialize database
db.init_db()

@st.cache_data
def populate_inventory():
    """Populate inventory with spectacles and medicines - cached for speed"""
    from modules.inventory_utils import add_or_update_inventory
    import random
    
    COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
    COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
    
    # Add spectacles (limited for speed)
    for i, (item_name, item_data) in enumerate(COMPREHENSIVE_SPECTACLE_DATABASE.items()):
        if i >= 50:  # Limit to first 50 for speed
            break
        stock = random.randint(5, 25)
        add_or_update_inventory(item_name, stock)
    
    # Add medicines (limited for speed)
    for i, (item_name, item_data) in enumerate(COMPREHENSIVE_MEDICINE_DATABASE.items()):
        if i >= 50:  # Limit to first 50 for speed
            break
        stock = random.randint(10, 50)
        add_or_update_inventory(item_name, stock)
    
    return True

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
            with st.spinner("Loading database (optimized)..."):
                populate_inventory()
            st.success(f"✅ Loaded 50 spectacles and 50 medicines for faster performance!")
        
        st.markdown("---")
        st.markdown("**📊 Database Stats:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👓 Spectacles", len(get_spectacle_database()))
            st.metric("💊 Medicines", len(get_medicine_database()))
        
        with col2:
            try:
                from modules.inventory_utils import get_inventory_dict
                inventory = get_inventory_dict()
                st.metric("📦 Inventory Items", len(inventory))
            except:
                st.metric("📦 Inventory Items", 0)
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
        
        # Test WhatsApp (lazy loaded)
        try:
            from modules.whatsapp_utils import test_whatsapp_connection
            whatsapp_status = test_whatsapp_connection()
        except ImportError:
            whatsapp_status = {'success': False, 'demo': True}
        
        if whatsapp_status['success']:
            if whatsapp_status.get('demo'):
                st.warning("📱 WhatsApp: Demo Mode")
            else:
                st.success("📱 WhatsApp: Connected")
        else:
            st.error("📱 WhatsApp: Not Configured")
        
        # Test Google Drive (lazy loaded)
        try:
            from modules.google_drive_integration import drive_integrator
            drive_status = drive_integrator.test_drive_connection()
            if drive_status['success']:
                if drive_status.get('demo'):
                    st.warning("☁️ Google Drive: Demo Mode")
                else:
                    st.success("☁️ Google Drive: Connected")
            else:
                st.error("☁️ Google Drive: Not Configured")
        except Exception as e:
            st.error(f"☁️ Google Drive: Error - {str(e)}")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "👥 Patient Registration", 
        "👓 Spectacle Gallery", 
        "💊 Medicine Gallery",
        "📸 AI Camera Analysis",
        "📋 Patient History",
        "📤 Prescription & Sharing",
        "📦 Inventory Management",
        "🔧 Clinic Settings",
        "📊 Analytics"
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
            
            # Generate comprehensive sphere options (-20.00 to +20.00 with 0.25 increments)
            sphere_options = [""]
            for i in range(-2000, 2025, 25):  # -20.00 to +20.00 in 0.25 steps
                value = i / 100
                if value > 0:
                    sphere_options.append(f"+{value:.2f}")
                elif value < 0:
                    sphere_options.append(f"{value:.2f}")
            
            # Generate comprehensive cylinder options
            cylinder_options = [""]
            for i in range(-1000, 25, 25):  # -10.00 to 0.00 in 0.25 steps
                value = i / 100
                if value != 0:
                    cylinder_options.append(f"{value:.2f}")
            
            # Generate axis options (0 to 180)
            axis_options = [""] + [str(i) for i in range(0, 181, 5)]
            
            col_od, col_os = st.columns(2)
            
            with col_od:
                st.markdown("**OD (Right Eye)**")
                od_sphere_mode = st.radio("Sphere OD Input", ["Select from list", "Custom value"], key="od_sphere_mode")
                if od_sphere_mode == "Select from list":
                    od_sphere = st.selectbox("Sphere OD", sphere_options, key="sphere_od")
                else:
                    od_sphere = st.text_input("Custom Sphere OD (e.g., +2.75, -1.25)", key="custom_sphere_od")
                
                od_cylinder_mode = st.radio("Cylinder OD Input", ["Select from list", "Custom value"], key="od_cylinder_mode")
                if od_cylinder_mode == "Select from list":
                    od_cylinder = st.selectbox("Cylinder OD", cylinder_options, key="cylinder_od")
                else:
                    od_cylinder = st.text_input("Custom Cylinder OD (e.g., -0.75)", key="custom_cylinder_od")
                
                od_axis_mode = st.radio("Axis OD Input", ["Select from list", "Custom value"], key="od_axis_mode")
                if od_axis_mode == "Select from list":
                    od_axis = st.selectbox("Axis OD", axis_options, key="axis_od")
                else:
                    od_axis = st.text_input("Custom Axis OD (0-180)", key="custom_axis_od")
            
            with col_os:
                st.markdown("**OS (Left Eye)**")
                os_sphere_mode = st.radio("Sphere OS Input", ["Select from list", "Custom value"], key="os_sphere_mode")
                if os_sphere_mode == "Select from list":
                    os_sphere = st.selectbox("Sphere OS", sphere_options, key="sphere_os")
                else:
                    os_sphere = st.text_input("Custom Sphere OS (e.g., +2.75, -1.25)", key="custom_sphere_os")
                
                os_cylinder_mode = st.radio("Cylinder OS Input", ["Select from list", "Custom value"], key="os_cylinder_mode")
                if os_cylinder_mode == "Select from list":
                    os_cylinder = st.selectbox("Cylinder OS", cylinder_options, key="cylinder_os")
                else:
                    os_cylinder = st.text_input("Custom Cylinder OS (e.g., -0.75)", key="custom_cylinder_os")
                
                os_axis_mode = st.radio("Axis OS Input", ["Select from list", "Custom value"], key="os_axis_mode")
                if os_axis_mode == "Select from list":
                    os_axis = st.selectbox("Axis OS", axis_options, key="axis_os")
                else:
                    os_axis = st.text_input("Custom Axis OS (0-180)", key="custom_axis_os")
            
            # Medicine Selection in Prescription
            st.markdown("**💊 Medicine Selection**")
            
            # Medicine filters for prescription
            col_med1, col_med2, col_med3 = st.columns(3)
            
            with col_med1:
                med_usage = st.selectbox("Usage Type", ["All", "Internal", "External"], key="rx_med_usage")
            
            with col_med2:
                med_category = st.selectbox("Category", 
                    ["All", "Antibiotic", "Steroid", "Glaucoma", "Lubricant", "Antihistamine", "NSAID", "Analgesic", "Vitamin", "Supplement"], 
                    key="rx_med_category")
            
            with col_med3:
                prescription_req = st.selectbox("Prescription Required", ["All", "Yes", "No"], key="rx_prescription_req")
            
            # Filter medicines for prescription
            COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
            filtered_rx_medicines = COMPREHENSIVE_MEDICINE_DATABASE.copy()
            
            # Apply filters
            if med_usage == "External":
                external_keywords = ['drop', 'ointment', 'gel', 'cream', 'solution']
                filtered_rx_medicines = {k: v for k, v in filtered_rx_medicines.items() 
                                       if any(keyword in k.lower() for keyword in external_keywords)}
            elif med_usage == "Internal":
                external_keywords = ['drop', 'ointment', 'gel', 'cream', 'solution']
                filtered_rx_medicines = {k: v for k, v in filtered_rx_medicines.items() 
                                       if not any(keyword in k.lower() for keyword in external_keywords)}
            
            if med_category != "All":
                filtered_rx_medicines = {k: v for k, v in filtered_rx_medicines.items() if v['category'] == med_category}
            
            if prescription_req == "Yes":
                filtered_rx_medicines = {k: v for k, v in filtered_rx_medicines.items() if v['prescription_required'] == True}
            elif prescription_req == "No":
                filtered_rx_medicines = {k: v for k, v in filtered_rx_medicines.items() if v['prescription_required'] == False}
            
            # Display filtered medicines for selection
            if filtered_rx_medicines:
                st.markdown(f"**Available Medicines ({len(filtered_rx_medicines)} found):**")
                
                # Multi-select for medicines
                selected_rx_medicines = st.multiselect(
                    "Select medicines for prescription:",
                    options=list(filtered_rx_medicines.keys()),
                    default=st.session_state.get('selected_medicines', {}).keys() if 'selected_medicines' in st.session_state else [],
                    key="rx_medicine_multiselect"
                )
                
                # Quantity and dosage for selected medicines
                if selected_rx_medicines:
                    st.markdown("**Medicine Details:**")
                    medicine_details = {}
                    
                    for med_name in selected_rx_medicines:
                        if med_name in filtered_rx_medicines:
                            med_data = filtered_rx_medicines[med_name]
                            
                            with st.expander(f"📋 {med_name} - ₹{med_data['price']}"):
                                col_qty, col_dosage, col_duration = st.columns(3)
                                
                                with col_qty:
                                    qty = st.number_input(f"Quantity", min_value=1, max_value=10, value=1, key=f"qty_{med_name}")
                                
                                with col_dosage:
                                    custom_dosage = st.text_input(f"Custom Dosage", 
                                                                 value=med_data.get('dosage', ''), 
                                                                 key=f"dosage_{med_name}")
                                
                                with col_duration:
                                    duration = st.selectbox(f"Duration", 
                                                          ["3 days", "5 days", "7 days", "10 days", "14 days", "1 month", "Custom"], 
                                                          key=f"duration_{med_name}")
                                    if duration == "Custom":
                                        custom_duration = st.text_input(f"Custom Duration", key=f"custom_duration_{med_name}")
                                        duration = custom_duration if custom_duration else "As needed"
                                
                                # Display medicine info
                                st.info(f"**Type:** {med_data['type']} | **Category:** {med_data['category']} | **Prescription Required:** {'Yes' if med_data['prescription_required'] else 'No'}")
                                st.info(f"**Indication:** {med_data['indication']}")
                                
                                medicine_details[med_name] = {
                                    'quantity': qty,
                                    'dosage': custom_dosage,
                                    'duration': duration,
                                    'price': med_data['price'],
                                    'total_cost': med_data['price'] * qty
                                }
                    
                    # Store medicine details in session
                    st.session_state['selected_medicines'] = {med: medicine_details[med]['quantity'] for med in medicine_details}
                    st.session_state['medicine_details'] = medicine_details
                    
                    # Show total medicine cost
                    total_med_cost = sum([details['total_cost'] for details in medicine_details.values()])
                    st.success(f"**Total Medicine Cost: ₹{total_med_cost:,}**")
            
            # Custom Medicine Addition
            st.markdown("**➕ Add Custom Medicine**")
            with st.expander("Add medicine not in database"):
                col_custom1, col_custom2, col_custom3 = st.columns(3)
                
                with col_custom1:
                    custom_med_name = st.text_input("Medicine Name", key="custom_med_name")
                    custom_med_type = st.selectbox("Type", ["Eye Drops", "Tablet", "Capsule", "Ointment", "Gel", "Injection"], key="custom_med_type")
                
                with col_custom2:
                    custom_med_usage = st.selectbox("Usage", ["Internal", "External"], key="custom_med_usage")
                    custom_med_price = st.number_input("Price (₹)", min_value=0, value=100, key="custom_med_price")
                
                with col_custom3:
                    custom_med_dosage = st.text_input("Dosage Instructions", key="custom_med_dosage")
                    custom_med_qty = st.number_input("Quantity", min_value=1, value=1, key="custom_med_qty")
                
                if st.button("➕ Add Custom Medicine", key="add_custom_med"):
                    if custom_med_name:
                        if 'selected_medicines' not in st.session_state:
                            st.session_state['selected_medicines'] = {}
                        if 'medicine_details' not in st.session_state:
                            st.session_state['medicine_details'] = {}
                        
                        st.session_state['selected_medicines'][custom_med_name] = custom_med_qty
                        st.session_state['medicine_details'][custom_med_name] = {
                            'quantity': custom_med_qty,
                            'dosage': custom_med_dosage,
                            'duration': 'As prescribed',
                            'price': custom_med_price,
                            'total_cost': custom_med_price * custom_med_qty,
                            'type': custom_med_type,
                            'usage': custom_med_usage,
                            'custom': True
                        }
                        st.success(f"✅ Added custom medicine: {custom_med_name}")
            
            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis}
            }
            
            submitted = st.form_submit_button("💾 Save Patient", type="primary")
            
            if submitted and patient_name:
                # Save patient with visit tracking
                patients = db.get_patients()
                found = False
                for p in patients:
                    if p[1].lower() == patient_name.lower() and p[4] == contact:
                        patient_id = p[0]
                        found = True
                        break
                if not found:
                    patient_id = db.add_patient(patient_name, age, gender, contact)
                
                # Track visit data for analytics
                visit_data = {
                    'patient_id': patient_id,
                    'visit_date': datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                    'issue': patient_issue,
                    'advice': advice,
                    'rx_data': rx_table,
                    'age_group': 'Child' if age < 18 else 'Adult' if age < 60 else 'Senior',
                    'visit_type': 'Return' if found else 'New',
                    'referral_source': 'Direct',  # Can be enhanced later
                    'season': datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%B')
                }
                
                # Store visit data in session for analytics
                if 'visit_analytics' not in st.session_state:
                    st.session_state['visit_analytics'] = []
                st.session_state['visit_analytics'].append(visit_data)
                
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
                
                visit_type = "New Patient" if not found else "Return Visit"
                st.success(f"✅ {visit_type}: {patient_name} saved successfully!")
                
                # Show visit analytics
                if found:
                    st.info(f"🔄 **Return Visit** - Welcome back! Previous visits help us provide better care.")
                else:
                    st.info(f"🎆 **New Patient** - Welcome to MauEyeCare! We're excited to help with your eye care needs.")
                
                st.info("🎯 Now go to 'AI Camera Analysis' tab to capture photo and get recommendations!")

    # --- Spectacle Gallery Tab ---
    with tab2:
        st.header("👓 Spectacle Gallery")
        st.markdown(f"*Browse our collection of spectacles*")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox("Category", 
                ["All", "Luxury", "Mid-Range", "Indian", "Budget", "Progressive", "Kids", "Safety", "Reading"])
        
        with col2:
            price_range = st.selectbox("Price Range", 
                ["All", "Budget (≤₹5,000)", "Mid-Range (₹5,001-15,000)", "Luxury (>₹15,000)"])
        
        with col3:
            COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
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
        
        # Display gallery (limited for speed)
        st.markdown(f"### 🖼️ Spectacle Gallery ({min(len(filtered_specs), 12)} items shown)")
        
        cols = st.columns(4)
        
        for i, (spec_name, spec_data) in enumerate(list(filtered_specs.items())[:12]):
            with cols[i % 4]:
                # Load and display image
                try:
                    from modules.real_spectacle_images import load_spectacle_image
                    spec_image = load_spectacle_image(spec_name)
                    st.image(spec_image, width=180)
                except:
                    st.image("https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=180&h=120&fit=crop", width=180)
                
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
        st.markdown("*Browse our collection of medicines*")
        
        # Medicine filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            med_type = st.selectbox("Medicine Type", ["All", "Eye Related", "Other"])
        
        with col2:
            usage_type = st.selectbox("Usage Type", ["All", "Internal", "External"])
        
        with col3:
            med_category = st.selectbox("Category", 
                ["All", "Antibiotic", "Anti-inflammatory", "Lubricant", "Antihistamine", "Antiviral"])
        
        with col4:
            prescription_req = st.selectbox("Prescription", ["All", "Required", "Not Required"])
        
        # Apply medicine filters
        COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
        filtered_medicines = COMPREHENSIVE_MEDICINE_DATABASE.copy()
        
        # Filter by medicine type (eye related vs other)
        if med_type == "Eye Related":
            eye_keywords = ['eye', 'tear', 'vision', 'glaucoma', 'cataract', 'retina', 'conjunctiv', 'dry']
            filtered_medicines = {k: v for k, v in filtered_medicines.items() 
                                if any(keyword in k.lower() or keyword in v.get('category', '').lower() 
                                      for keyword in eye_keywords)}
        elif med_type == "Other":
            eye_keywords = ['eye', 'tear', 'vision', 'glaucoma', 'cataract', 'retina', 'conjunctiv', 'dry']
            filtered_medicines = {k: v for k, v in filtered_medicines.items() 
                                if not any(keyword in k.lower() or keyword in v.get('category', '').lower() 
                                          for keyword in eye_keywords)}
        
        # Filter by usage type
        if usage_type == "External":
            external_keywords = ['drop', 'ointment', 'gel', 'cream', 'solution']
            filtered_medicines = {k: v for k, v in filtered_medicines.items() 
                                if any(keyword in k.lower() for keyword in external_keywords)}
        elif usage_type == "Internal":
            external_keywords = ['drop', 'ointment', 'gel', 'cream', 'solution']
            filtered_medicines = {k: v for k, v in filtered_medicines.items() 
                                if not any(keyword in k.lower() for keyword in external_keywords)}
        
        if med_category != "All":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['category'] == med_category}
        
        if prescription_req == "Required":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['prescription_required'] == True}
        elif prescription_req == "Not Required":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['prescription_required'] == False}
        
        # Display medicine gallery (limited for speed)
        st.markdown(f"### 💊 Medicine Gallery ({min(len(filtered_medicines), 9)} items shown)")
        
        cols = st.columns(3)
        
        for i, (med_name, med_data) in enumerate(list(filtered_medicines.items())[:9]):
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
                # Lazy load camera module
                from modules.simple_camera import show_camera_with_preview, analyze_captured_photo
                captured_image = show_camera_with_preview()
                
                if captured_image is not None:
                    st.session_state['analysis_photo'] = captured_image
                    
                    # Analyze the photo
                    with st.spinner("🔍 AI analyzing face shape and matching spectacles..."):
                        from modules.simple_camera import analyze_captured_photo
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
                                COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
                                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                    try:
                                        from modules.real_spectacle_images import load_spectacle_image
                                        spec_image = load_spectacle_image(spec_name)
                                    except:
                                        spec_image = "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=200&h=150&fit=crop"
                                    
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
                    COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
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
                    COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, rgba(46, 134, 171, 0.95) 0%, rgba(30, 95, 139, 0.95) 100%); }}
        @media print {{ 
            body {{ background: white !important; color: black !important; }} 
            .prescription-container {{ box-shadow: none !important; border: 2px solid #2E86AB !important; }} 
            .header {{ background: white !important; color: #2E86AB !important; border: 3px solid #2E86AB !important; }}
            .logo {{ background: #2E86AB !important; color: white !important; }}
            .contact-info {{ background: #f0f8ff !important; color: #2E86AB !important; }}
        }}
        .prescription-container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ text-align: center; background: #2E86AB; color: white; padding: 40px 30px; border: 4px solid #1e5f8b; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 8px 25px rgba(46, 134, 171, 0.3); }}
        .logo {{ width: 80px; height: 80px; background: white; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px; border: 3px solid #1e5f8b; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
        .clinic-name {{ font-size: 36px; font-weight: 900; margin: 15px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); letter-spacing: 1px; }}
        .doctor-info {{ font-size: 18px; margin: 8px 0; font-weight: 600; }}
        .address {{ font-size: 16px; margin: 12px 0; line-height: 1.6; font-weight: 500; }}
        .contact-info {{ font-size: 17px; font-weight: 700; margin: 10px 0; background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 25px; display: inline-block; }}
        .patient-info {{ background: #f8f9ff; padding: 25px; margin: 0; border-left: 5px solid #2E86AB; }}
        .prescription {{ background: white; padding: 25px; margin: 0; border-bottom: 1px solid #eee; }}
        .prescription:last-child {{ border-bottom: none; }}
        .item {{ background: linear-gradient(135deg, #f0f8ff, #e6f3ff); padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #2E86AB; }}
        .total {{ background: linear-gradient(135deg, #e8f5e8, #d4f4d4); padding: 20px; border-radius: 10px; font-weight: bold; text-align: center; margin: 15px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-top: 2px solid #2E86AB; }}
        .section-title {{ color: #2E86AB; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #2E86AB; padding-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="prescription-container">
        <div class="header">
            <div class="logo"><img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjQiIGZpbGw9IiMyRTg2QUIiLz4KPHN2ZyB4PSIxNSIgeT0iMTUiIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+CjxwYXRoIGQ9Ik0xMiA0LjVDNyA0LjUgMi43MyA3Ljg0IDEgMTJjMS43MyA0LjE2IDYgNy41IDExIDcuNXM5LjI3LTMuMzQgMTEtNy41Yy0xLjczLTQuMTYtNi03LjUtMTEtNy41ek0xMiAxN2MtMi43NiAwLTUtMi4yNC01LTVzMi4yNC01IDUtNSA1IDIuMjQgNSA1LTIuMjQgNS01IDV6bTAtOGMtMS42NiAwLTMgMS4zNC0zIDNzMS4zNCAzIDMgMyAzLTEuMzQgMy0zLTEuMzQtMy0zLTN6Ii8+Cjwvc3ZnPgo8L3N2Zz4K" alt="MauEyeCare Logo" style="width: 50px; height: 50px;"></div>
            <div class="clinic-name">MauEyeCare Optical Center</div>
            <div class="doctor-info">Dr. Danish - Eye Care Specialist</div>
            <div class="doctor-info">Registration No: UPS 2908</div>
            <div class="address">
                Pura Sofi Bhonu Kuraishi Dasai Kuwa Mubarakpur<br>
                Azamgarh, Uttar Pradesh, India
            </div>
            <div class="contact-info">📞 +91 92356-47410 | 📧 maueyecare@gmail.com</div>
            <div class="contact-info">🕘 Mon-Sat: {st.session_state.get('clinic_timing', '9:00 AM - 8:00 PM')} | Sunday: Closed</div>
        </div>
    
        <div class="patient-info">
            <div class="section-title">👤 Patient Information</div>
        <p><strong>Name:</strong> {patient_name}</p>
        <p><strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')}</p>
        <p><strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')}</p>
        <p><strong>Issue:</strong> {st.session_state.get('patient_issue', 'N/A')}</p>
        <p><strong>Date & Time:</strong> {(datetime.datetime.now(timezone(timedelta(hours=5, minutes=30)))).strftime('%d/%m/%Y %I:%M %p IST')}</p>
    </div>"""
                    
                    # Add eye prescription
                    rx_table = st.session_state.get('rx_table', {})
                    if rx_table and (rx_table.get('OD', {}).get('Sphere') or rx_table.get('OS', {}).get('Sphere')):
                        prescription_html += """
        <div class="prescription">
            <div class="section-title">👁️ Eye Prescription (RX)</div>"""
                        
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
            <div class="section-title">👓 Recommended Spectacles</div>"""
                        
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
                    medicine_details = st.session_state.get('medicine_details', {})
                    if selected_medicines or medicine_details:
                        prescription_html += """
        <div class="prescription">
            <div class="section-title">💊 Prescribed Medicines</div>"""
                        
                        total_med_cost = 0
                        
                        # Handle detailed medicine information
                        if medicine_details:
                            for med_name, details in medicine_details.items():
                                total_med_cost += details['total_cost']
                                
                                # Check if it's a custom medicine
                                if details.get('custom', False):
                                    prescription_html += f"""
        <div class="item">
            <strong>{med_name}</strong> (Custom)<br>
            Type: {details.get('type', 'N/A')} | Usage: {details.get('usage', 'N/A')} | Quantity: {details['quantity']}<br>
            Dosage: {details['dosage']}<br>
            Duration: {details['duration']}<br>
            Price: ₹{details['price']} x {details['quantity']} = <strong>₹{details['total_cost']}</strong>
        </div>"""
                                else:
                                    # Regular medicine from database
                                    if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
                                        med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
                                        prescription_html += f"""
        <div class="item">
            <strong>{med_name}</strong><br>
            Category: {med_data['category']} | Type: {med_data['type']} | Quantity: {details['quantity']}<br>
            Dosage: {details['dosage']}<br>
            Duration: {details['duration']}<br>
            Indication: {med_data['indication']}<br>
            Price: ₹{details['price']} x {details['quantity']} = <strong>₹{details['total_cost']}</strong><br>
            Prescription Required: {'Yes' if med_data['prescription_required'] else 'No'}
        </div>"""
                        else:
                            # Fallback for old format
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
            <div class="section-title">📋 Doctor's Advice</div>
        <p>{st.session_state.get('advice', 'Regular eye checkup recommended')}</p>
    </div>
    
        <div class="footer">
            <p><strong>Dr. Danish</strong> - Eye Care Specialist</p>
            <p>MauEyeCare Optical Center</p>
            <p>Pura Sofi Bhonu Kuraishi Dasai Kuwa Mubarakpur, Azamgarh, UP</p>
            <p>📞 +91 92356-47410 | 📧 maueyecare@gmail.com</p>
            <p>🕘 Mon-Sat: {st.session_state.get('clinic_timing', '9:00 AM - 8:00 PM')} | Sunday: Closed</p>
            <p style="margin-top: 15px; font-size: 12px; color: #999;">Professional Eye Care Services | Complete AI-Powered Solutions</p>
        </div>
    </div>
</body>
</html>"""
                    
                    # Upload to Google Drive (lazy loaded)
                    with st.spinner("📤 Uploading prescription to Google Drive..."):
                        try:
                            from modules.google_drive_integration import drive_integrator
                            result = drive_integrator.upload_prescription_to_drive(
                                prescription_html, 
                                patient_name
                            )
                        except ImportError:
                            result = {'success': False, 'error': 'Google Drive module not available'}
                    
                    if result['success']:
                        # Success message with detailed info
                        st.success("✅ **Prescription uploaded to Google Drive successfully!**")
                        
                        # Professional file information display
                        st.markdown("### 📁 Prescription Details")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📄 File Information**")
                            st.info(f"**Filename:** {result['filename']}")
                            st.info(f"**File ID:** {result.get('file_id', 'N/A')}")
                            st.info(f"**Upload Time:** {datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y %H:%M IST')}")
                        
                        with col2:
                            st.markdown("**📂 Storage Location**")
                            st.info(f"**Folder:** {result['folder_name']}")
                            st.success("**Status:** Uploaded & Public")
                            if 'file_size' in result:
                                st.info(f"**File Size:** {result['file_size']} bytes")
                            st.info(f"**Patient:** {patient_name}")
                        
                        with col3:
                            st.markdown("**🔗 Access Links**")
                            st.markdown(f"**[📄 View Prescription]({result['link']})**")
                            st.markdown(f"**[📂 Open Folder]({result['folder_link']})**")
                            
                            # Copy link button
                            if st.button("📋 Copy Link", key="copy_prescription_link"):
                                st.code(result['link'], language=None)
                                st.success("Link copied! Share this with the patient.")
                        
                        # Always show download options regardless of Google Drive status
                        st.markdown("---")
                        st.markdown("### 💾 Download Prescription Files")
                        
                        col_dl1, col_dl2, col_dl3 = st.columns(3)
                        
                        with col_dl1:
                            # HTML Download
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                            timestamp = datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y%m%d_%H%M")
                            html_filename = f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html"
                            
                            st.download_button(
                                label="💾 Download HTML",
                                data=prescription_html.encode('utf-8'),
                                file_name=html_filename,
                                mime="text/html",
                                help="Download as HTML file",
                                use_container_width=True
                            )
                        
                        with col_dl2:
                            # Text Download
                            text_prescription = f"""MauEyeCare Prescription

Patient: {patient_name}
Age: {st.session_state.get('age', 'N/A')}
Gender: {st.session_state.get('gender', 'N/A')}
Mobile: {st.session_state.get('patient_mobile', 'N/A')}
Date: {datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y %H:%M IST')}

Prescribed Items:
{'-'*40}
"""
                            
                            if selected_spectacles:
                                text_prescription += "\nSPECTACLES:\n"
                                for spec_name in selected_spectacles:
                                    if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                        spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                        total_price = spec_data['price'] + spec_data['lens_price']
                                        text_prescription += f"- {spec_data['brand']} {spec_data['model']} - Rs.{total_price:,}\n"
                            
                            medicine_details = st.session_state.get('medicine_details', {})
                            if selected_medicines or medicine_details:
                                text_prescription += "\nMEDICINES:\n"
                                
                                if medicine_details:
                                    for med_name, details in medicine_details.items():
                                        text_prescription += f"- {med_name} (Qty: {details['quantity']}) - Rs.{details['total_cost']}\n"
                                        text_prescription += f"  Dosage: {details['dosage']}\n"
                                        text_prescription += f"  Duration: {details['duration']}\n"
                                else:
                                    for med_name, qty in selected_medicines.items():
                                        if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
                                            med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
                                            total_price = med_data['price'] * qty
                                            text_prescription += f"- {med_name} (Qty: {qty}) - Rs.{total_price}\n"
                            
                            # Add RX details if available
                            rx_table = st.session_state.get('rx_table', {})
                            if rx_table and (rx_table.get('OD', {}).get('Sphere') or rx_table.get('OS', {}).get('Sphere')):
                                text_prescription += "\nEYE PRESCRIPTION:\n"
                                for eye in ['OD', 'OS']:
                                    eye_data = rx_table.get(eye, {})
                                    if eye_data.get('Sphere'):
                                        eye_name = "Right Eye" if eye == "OD" else "Left Eye"
                                        text_prescription += f"{eye} ({eye_name}): SPH {eye_data.get('Sphere', '')} CYL {eye_data.get('Cylinder', '')} AXIS {eye_data.get('Axis', '')}\n"
                            
                            text_prescription += f"\n{'-'*40}\nDr. Danish\nEye Care Specialist\nMauEyeCare Optical Center\nPhone: +91 92356-47410\nEmail: maueyecare@gmail.com"
                            
                            st.download_button(
                                label="📝 Download Text",
                                data=text_prescription.encode('utf-8'),
                                file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.txt",
                                mime="text/plain",
                                help="Download as text file",
                                use_container_width=True
                            )
                        
                        with col_dl3:
                            # JSON Download (for data backup)
                            prescription_data = {
                                'patient_name': patient_name,
                                'patient_age': st.session_state.get('age'),
                                'patient_gender': st.session_state.get('gender'),
                                'patient_mobile': st.session_state.get('patient_mobile'),
                                'prescription_date': datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                                'doctor': 'Dr. Danish',
                                'clinic': 'MauEyeCare Optical Center',
                                'selected_spectacles': selected_spectacles,
                                'selected_medicines': selected_medicines,
                                'medicine_details': st.session_state.get('medicine_details', {}),
                                'rx_table': st.session_state.get('rx_table', {}),
                                'advice': st.session_state.get('advice', ''),
                                'patient_issue': st.session_state.get('patient_issue', ''),
                                'visit_analytics': st.session_state.get('visit_analytics', [])
                            }
                            
                            st.download_button(
                                label="📋 Download JSON",
                                data=json.dumps(prescription_data, indent=2).encode('utf-8'),
                                file_name=f"Prescription_Data_{patient_name.replace(' ', '_')}_{timestamp}.json",
                                mime="application/json",
                                help="Download as JSON data file",
                                use_container_width=True
                            )
                        
                        # Professional patient communication section
                        patient_mobile = st.session_state.get('patient_mobile')
                        if patient_mobile:
                            st.markdown("---")
                            st.markdown("### 📱 Patient Communication")
                            
                            # Patient info display
                            st.markdown(f"**👤 Patient:** {patient_name}")
                            st.markdown(f"**📞 Mobile:** +91 {patient_mobile}")
                            st.markdown(f"**🔗 Prescription Link:** {result['link']}")
                            
                            # Professional WhatsApp message
                            whatsapp_message = f"""🏥 *MauEyeCare Prescription Ready*

Dear {patient_name},

Your eye care prescription has been prepared by Dr. Danish.

📄 *View Prescription:* {result['link']}

📋 *Prescription Details:*
• Patient: {patient_name}
• Date: {datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y')}
• Doctor: Dr. Danish (Reg: UPS 2908)

📞 *For queries:* +91 92356-47410
📧 *Email:* maueyecare@gmail.com

*Thank you for choosing MauEyeCare!*

---
🏥 MauEyeCare Optical Center
👁️ Complete AI-Powered Eye Care"""
                            
                            # Professional communication options
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📱 WhatsApp API**")
                                if st.button("🚀 Send via API", type="primary", key="whatsapp_api"):
                                    with st.spinner("Sending WhatsApp message..."):
                                        try:
                                            # Format mobile number
                                            mobile = patient_mobile.replace("+91", "").replace(" ", "").replace("-", "")
                                            if not mobile.startswith("91"):
                                                mobile = "91" + mobile
                                            
                                            # Send WhatsApp message
                                            from modules.whatsapp_utils import send_text_message
                                            whatsapp_result = send_text_message(mobile, whatsapp_message)
                                            
                                            if whatsapp_result.get('success'):
                                                if whatsapp_result.get('demo'):
                                                    st.info(f"📱 **Demo Mode:** Message prepared for +91 {patient_mobile}")
                                                    st.success("✅ WhatsApp API integration working!")
                                                else:
                                                    st.success(f"✅ **Message sent** to +91 {patient_mobile}")
                                                    st.balloons()
                                            else:
                                                st.error(f"❌ **Send failed:** {whatsapp_result.get('error')}")
                                                
                                        except Exception as e:
                                            st.error(f"❌ **Error:** {str(e)}")
                            
                            with col2:
                                st.markdown("**🌐 WhatsApp Web**")
                                if st.button("🔗 Open Web App", key="whatsapp_web"):
                                    from modules.whatsapp_utils import send_via_whatsapp_web
                                    
                                    whatsapp_url = send_via_whatsapp_web(patient_mobile, whatsapp_message)
                                    st.markdown(f"**[🚀 Send via WhatsApp Web]({whatsapp_url})**")
                                    st.success("📱 WhatsApp Web will open in new tab")
                                    st.info("💡 Click the link above to send message")
                            
                            with col3:
                                st.markdown("**📲 SMS/Manual**")
                                if st.button("📋 Copy Message", key="copy_message"):
                                    st.text_area(
                                        "Copy this message:",
                                        value=whatsapp_message,
                                        height=150,
                                        help="Copy and send manually via SMS or any messaging app"
                                    )
                                    st.success("📋 Message ready to copy!")
                            
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
                            st.warning("⚠️ **Patient mobile number required for direct communication**")
                            st.info("💡 **Tip:** Add patient mobile number in the registration form to enable WhatsApp sharing")
                            
                            # Still show the prescription link for manual sharing
                            st.markdown("### 🔗 Manual Sharing")
                            st.text_input("Share this link with patient:", value=result['link'], help="Copy this link to share manually")
                        
                        # Professional inventory management
                        st.markdown("---")
                        st.markdown("### 📦 Inventory Management")
                        
                        with st.spinner("🔄 Updating inventory levels..."):
                            inventory_updates = []
                            
                            # Update medicine inventory
                            from modules.inventory_utils import get_inventory_dict, reduce_inventory
                            for med_name, quantity in selected_medicines.items():
                                old_stock = get_inventory_dict().get(med_name, 0)
                                reduce_inventory(med_name, quantity)
                                new_stock = get_inventory_dict().get(med_name, 0)
                                inventory_updates.append({
                                    'item': med_name,
                                    'type': 'Medicine',
                                    'quantity_used': quantity,
                                    'old_stock': old_stock,
                                    'new_stock': new_stock
                                })
                            
                            # Update spectacle inventory
                            for spec_name in selected_spectacles:
                                old_stock = get_inventory_dict().get(spec_name, 0)
                                reduce_inventory(spec_name, 1)
                                new_stock = get_inventory_dict().get(spec_name, 0)
                                inventory_updates.append({
                                    'item': spec_name,
                                    'type': 'Spectacle',
                                    'quantity_used': 1,
                                    'old_stock': old_stock,
                                    'new_stock': new_stock
                                })
                        
                        # Display inventory updates
                        if inventory_updates:
                            st.success("✅ **Inventory updated successfully!**")
                            
                            with st.expander("📈 View Inventory Changes"):
                                for update in inventory_updates:
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.write(f"**{update['type']}**")
                                        st.write(update['item'])
                                    
                                    with col2:
                                        st.metric("Used", update['quantity_used'])
                                    
                                    with col3:
                                        st.metric("Previous Stock", update['old_stock'])
                                    
                                    with col4:
                                        st.metric("Current Stock", update['new_stock'], 
                                                delta=update['new_stock'] - update['old_stock'])
                        else:
                            st.info("📈 No inventory changes (no items selected)")
                        
                        # Professional prescription completion
                        st.markdown("---")
                        st.markdown("### ✅ Prescription Complete")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 New Prescription", type="primary"):
                                # Clear all selections
                                keys_to_clear = ['selected_spectacles', 'selected_medicines', 'analysis_photo', 'analysis_result']
                                for key in keys_to_clear:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                st.success("🎆 Ready for new prescription!")
                                st.rerun()
                        
                        with col2:
                            if st.button("📋 Print Summary"):
                                st.info("🖨️ Print functionality coming soon!")
                        
                        with col3:
                            if st.button("📊 View Reports"):
                                st.info("📊 Reporting dashboard coming soon!")
                        
                        # Success message
                        st.success("🎉 **Prescription successfully generated and shared with patient!**")
                        st.balloons()
                    
                    else:
                        # Professional error handling
                        st.error("❌ **Google Drive Upload Failed**")
                        
                        with st.expander("🔍 Error Details"):
                            st.error(f"**Error:** {result.get('error', 'Unknown error')}")
                            st.info(f"**Details:** {result.get('details', 'No additional details')}")
                            
                            # Troubleshooting suggestions
                            st.markdown("**🔧 Troubleshooting:**")
                            st.markdown("- Check Google Drive API configuration")
                            st.markdown("- Verify access token is valid")
                            st.markdown("- Ensure folder permissions are correct")
                            st.markdown("- Check internet connection")
                        
                        # Always show download options when Google Drive fails
                        st.markdown("### 💾 Download Options (Google Drive Alternative)")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Save as HTML file
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                            filename = f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html"
                            
                            st.download_button(
                                label="💾 Download HTML Prescription",
                                data=prescription_html.encode('utf-8'),
                                file_name=filename,
                                mime="text/html",
                                help="Download prescription as HTML file to share manually",
                                type="primary"
                            )
                        
                        with col2:
                            # Text version
                            text_prescription = f"""MauEyeCare Prescription

Patient: {patient_name}
Age: {st.session_state.get('age', 'N/A')}
Date: {datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y')}

Prescribed Items:
{'-'*30}
"""
                            
                            for spec_name in selected_spectacles:
                                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                    text_prescription += f"Spectacle: {spec_data['brand']} {spec_data['model']}\n"
                            
                            for med_name, qty in selected_medicines.items():
                                text_prescription += f"Medicine: {med_name} (Qty: {qty})\n"
                            
                            text_prescription += f"\nDr. Danish\nMauEyeCare Optical Center"
                            
                            st.download_button(
                                label="📝 Download Text Version",
                                data=text_prescription.encode('utf-8'),
                                file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.txt",
                                mime="text/plain",
                                help="Download prescription as text file"
                            )
                        
                        with col2:
                            # Manual upload instructions
                            if st.button("📝 Manual Upload Guide"):
                                st.info("""
                                **Manual Upload Steps:**
                                1. Download the HTML file above
                                2. Go to Google Drive
                                3. Upload to 'MauEyeCare Prescriptions' folder
                                4. Share the file publicly
                                5. Copy the share link
                                6. Send link to patient
                                """)
                    
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine")
        else:
            st.warning("⚠️ Please select a patient first")

    # --- Inventory Management Tab ---
    with tab7:
        st.header("📦 Inventory Management")
        
        try:
            from modules.inventory_utils import get_inventory_dict, add_or_update_inventory
            inventory = get_inventory_dict()
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", len(inventory))
            with col2:
                total_stock = sum(inventory.values()) if inventory else 0
                st.metric("Total Stock", total_stock)
            with col3:
                low_stock = len([k for k, v in inventory.items() if v < 5]) if inventory else 0
                st.metric("Low Stock", low_stock)
            
            # Inventory Management Options
            st.subheader("🔧 Inventory Operations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Manual Update
                st.markdown("**✏️ Manual Update**")
                item_name = st.text_input("Item Name", placeholder="Enter item name")
                
                update_mode = st.radio(
                    "Update Mode:",
                    ["Set quantity", "Add quantity"],
                    key="manual_mode"
                )
                
                quantity = st.number_input("Quantity", min_value=0, value=1)
                
                if st.button("💾 Update Stock"):
                    if item_name:
                        if update_mode == "Add quantity":
                            current_stock = get_inventory_dict().get(item_name, 0)
                            new_stock = current_stock + quantity
                            add_or_update_inventory(item_name, new_stock)
                            st.success(f"✅ Added {quantity} to {item_name}: {new_stock} total")
                        else:
                            add_or_update_inventory(item_name, quantity)
                            st.success(f"✅ Set {item_name}: {quantity} units")
                        st.rerun()
            
            with col2:
                # Excel Import
                st.markdown("**📄 Excel Import**")
                uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls', 'csv'])
                
                if uploaded_file:
                    # Import mode selection
                    import_mode = st.radio(
                        "Import Mode:",
                        ["Add to existing", "Overwrite all"],
                        help="Add: Keep existing + add new items | Overwrite: Replace entire inventory"
                    )
                    
                    if st.button("📤 Import Data"):
                        try:
                            if uploaded_file.name.endswith('.csv'):
                                df = pd.read_csv(uploaded_file)
                            else:
                                df = pd.read_excel(uploaded_file)
                            
                            # Expected columns: Item, Stock
                            if 'Item' in df.columns and 'Stock' in df.columns:
                                # Clear inventory if overwrite mode
                                if import_mode == "Overwrite all":
                                    # Clear existing inventory by setting all to 0
                                    current_inventory = get_inventory_dict()
                                    for item in list(current_inventory.keys()):
                                        from modules.inventory_utils import reduce_inventory
                                        # Reduce to 0 by reducing current stock
                                        current_stock = current_inventory[item]
                                        if current_stock > 0:
                                            reduce_inventory(item, current_stock)
                                    st.info("🗑️ Cleared existing inventory")
                                
                                imported_count = 0
                                for _, row in df.iterrows():
                                    item = str(row['Item']).strip()
                                    stock = int(row['Stock']) if pd.notna(row['Stock']) else 0
                                    
                                    if import_mode == "Add to existing":
                                        # Add to existing stock
                                        current_stock = get_inventory_dict().get(item, 0)
                                        add_or_update_inventory(item, stock)  # This adds to existing
                                    else:
                                        # Set new stock (inventory already cleared)
                                        add_or_update_inventory(item, stock)
                                    
                                    imported_count += 1
                                
                                mode_text = "added to" if import_mode == "Add to existing" else "imported (overwrite)"
                                st.success(f"✅ {imported_count} items {mode_text} inventory successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Excel must have 'Item' and 'Stock' columns")
                        except Exception as e:
                            st.error(f"❌ Import failed: {str(e)}")
                
                # Sample format
                sample_data = pd.DataFrame({
                    'Item': ['Ray-Ban Aviator', 'Refresh Tears', 'Oakley Holbrook'],
                    'Stock': [15, 25, 10]
                })
                csv = sample_data.to_csv(index=False)
                st.download_button(
                    "📄 Download Sample",
                    csv,
                    "inventory_sample.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Excel Export
                st.markdown("**📤 Excel Export**")
                
                if inventory:
                    df = pd.DataFrame([
                        {"Item": item, "Stock": stock, "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"}
                        for item, stock in inventory.items()
                    ])
                    
                    # Excel export with proper buffer handling
                    try:
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Inventory', index=False)
                        output.seek(0)
                        
                        st.download_button(
                            "📤 Download Excel",
                            data=output.getvalue(),
                            file_name=f"inventory_{datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Excel export failed: {str(e)}")
                        # Fallback to CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📤 Download CSV (Fallback)",
                            csv,
                            f"inventory_{datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                
                # CSV Export (always works)
                if inventory:
                    df = pd.DataFrame([
                        {"Item": item, "Stock": stock, "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"}
                        for item, stock in inventory.items()
                    ])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📤 Download CSV",
                        data=csv,
                        file_name=f"inventory_{datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            st.markdown("---")
            
            # Current Stock Display
            if inventory:
                st.subheader("📋 Current Stock")
                
                # Search filter
                search_term = st.text_input("🔍 Search items", placeholder="Type to filter items...")
                
                filtered_items = inventory.items()
                if search_term:
                    filtered_items = [(k, v) for k, v in inventory.items() if search_term.lower() in k.lower()]
                
                # Display items
                for item, stock in list(filtered_items)[:30]:  # Show up to 30 items
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(item)
                    with col2:
                        if stock == 0:
                            st.error(f"OUT: {stock}")
                        elif stock < 5:
                            st.warning(f"LOW: {stock}")
                        else:
                            st.success(f"OK: {stock}")
                    with col3:
                        # Quick update buttons
                        if st.button("➕", key=f"add_{item}", help="Add 1"):
                            add_or_update_inventory(item, stock + 1)
                            st.rerun()
            else:
                st.info("📦 No inventory items. Click 'Load Complete Database' in sidebar or import Excel file.")
                
        except Exception as e:
            st.error("😱 Inventory system not available")
            st.info("Please load the database first using the sidebar button.")
    
    # --- Integration Setup Tab ---
    with tab8:
        st.header("🔧 Clinic Settings")
        
        # Data Backup & Security
        st.subheader("🔒 Data Security & Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💾 Patient Data Backup**")
            
            patients = db.get_patients()
            if patients:
                # Create backup data
                backup_data = {
                    'backup_date': datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                    'total_patients': len(patients),
                    'patients': [],
                    'visit_analytics': st.session_state.get('visit_analytics', [])
                }
                
                for p in patients:
                    patient_data = {
                        'id': p[0],
                        'name': p[1],
                        'age': p[2],
                        'gender': p[3],
                        'mobile': p[4],
                        'registration_date': p[5] if len(p) > 5 else None
                    }
                    backup_data['patients'].append(patient_data)
                
                backup_json = json.dumps(backup_data, indent=2)
                
                st.download_button(
                    "💾 Download Patient Backup",
                    backup_json,
                    f"patient_backup_{datetime.datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.json",
                    "application/json",
                    help="Secure backup of all patient data",
                    use_container_width=True
                )
                
                st.info(f"📊 {len(patients)} patients in database")
            else:
                st.info("📊 No patient data to backup")
        
        with col2:
            st.markdown("**📤 Restore Patient Data**")
            
            backup_file = st.file_uploader("Upload Patient Backup", type=['json'])
            
            if backup_file:
                restore_mode = st.radio(
                    "Restore Mode:",
                    ["Add to existing", "Replace all"],
                    help="Add: Keep current + restore backup | Replace: Delete current + restore backup"
                )
                
                if st.button("🔄 Restore Data", type="primary"):
                    try:
                        backup_data = json.load(backup_file)
                        
                        if 'patients' in backup_data:
                            restored_count = 0
                            
                            # Clear existing if replace mode
                            if restore_mode == "Replace all":
                                st.warning("⚠️ This will delete all current patient data!")
                                if st.button("Confirm Replace All", type="secondary"):
                                    # Note: In production, you'd implement patient deletion
                                    st.info("🗑️ Current data cleared (simulated)")
                            
                            # Restore patients
                            for patient in backup_data['patients']:
                                # Check if patient exists (by name and mobile)
                                existing = False
                                current_patients = db.get_patients()
                                for p in current_patients:
                                    if p[1] == patient['name'] and p[4] == patient['mobile']:
                                        existing = True
                                        break
                                
                                if not existing or restore_mode == "Replace all":
                                    db.add_patient(
                                        patient['name'],
                                        patient['age'],
                                        patient['gender'],
                                        patient['mobile']
                                    )
                                    restored_count += 1
                            
                            # Restore analytics if available
                            if 'visit_analytics' in backup_data:
                                st.session_state['visit_analytics'] = backup_data['visit_analytics']
                            
                            st.success(f"✅ Restored {restored_count} patients successfully!")
                            st.info(f"📅 Backup from: {backup_data.get('backup_date', 'Unknown')}")
                            st.rerun()
                        else:
                            st.error("❌ Invalid backup file format")
                    except Exception as e:
                        st.error(f"❌ Restore failed: {str(e)}")
        
        st.markdown("---")
        
        # Auto-backup settings
        st.subheader("⚙️ Auto-Backup Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_backup = st.checkbox(
                "Enable Auto-Backup",
                value=st.session_state.get('auto_backup_enabled', False),
                help="Automatically backup patient data"
            )
            st.session_state['auto_backup_enabled'] = auto_backup
            
            if auto_backup:
                backup_frequency = st.selectbox(
                    "Backup Frequency",
                    ["Daily", "Weekly", "Monthly"],
                    index=st.session_state.get('backup_frequency_index', 1)
                )
                st.session_state['backup_frequency'] = backup_frequency
                st.session_state['backup_frequency_index'] = ["Daily", "Weekly", "Monthly"].index(backup_frequency)
        
        with col2:
            st.markdown("**🔒 Security Features:**")
            st.info("✅ Data stored locally in SQLite")
            st.info("✅ JSON backup with timestamps")
            st.info("✅ Manual backup/restore")
            st.info("✅ Duplicate prevention")
            
            if st.session_state.get('auto_backup_enabled'):
                st.success(f"✅ Auto-backup: {st.session_state.get('backup_frequency', 'Weekly')}")
        
        st.markdown("---")
        
        # Clinic Timing Settings
        st.subheader("🕘 Clinic Timing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_timing = st.session_state.get('clinic_timing', '9:00 AM - 8:00 PM')
            new_timing = st.text_input("Clinic Hours (Mon-Sat)", value=current_timing, 
                                     placeholder="e.g., 9:00 AM - 8:00 PM")
            
            if st.button("💾 Update Timing"):
                st.session_state['clinic_timing'] = new_timing
                st.success(f"✅ Clinic timing updated to: {new_timing}")
                st.info("📝 This will appear on all prescriptions")
        
        with col2:
            st.markdown("**Current Schedule:**")
            st.info(f"Mon-Sat: {st.session_state.get('clinic_timing', '9:00 AM - 8:00 PM')}")
            st.info("Sunday: Closed")
            
            # Quick timing presets
            st.markdown("**Quick Presets:**")
            if st.button("Morning Clinic (9 AM - 1 PM)"):
                st.session_state['clinic_timing'] = '9:00 AM - 1:00 PM'
                st.success("✅ Updated to morning hours")
            
            if st.button("Full Day (9 AM - 8 PM)"):
                st.session_state['clinic_timing'] = '9:00 AM - 8:00 PM'
                st.success("✅ Updated to full day hours")
            
            if st.button("Evening Clinic (5 PM - 9 PM)"):
                st.session_state['clinic_timing'] = '5:00 PM - 9:00 PM'
                st.success("✅ Updated to evening hours")
        
        st.markdown("---")
        
        # Integration Settings
        try:
            from integration_config import show_integration_setup
            show_integration_setup()
        except ImportError:
            st.subheader("🔗 Integration Setup")
            st.info("Integration setup module not available. App works in demo mode.")
            st.markdown("### Available Features:")
            st.markdown("- ✅ Patient management")
            st.markdown("- ✅ Inventory management")
            st.markdown("- ✅ Prescription generation")
            st.markdown("- ✅ Download options")
    
    # --- Analytics Tab ---
    with tab9:
        st.header("📊 Professional Analytics")
        
        visit_data = st.session_state.get('visit_analytics', [])
        
        if visit_data:
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_visits = len(visit_data)
                st.metric("Total Visits", total_visits)
            
            with col2:
                new_patients = len([v for v in visit_data if v['visit_type'] == 'New'])
                st.metric("New Patients", new_patients)
            
            with col3:
                return_rate = len([v for v in visit_data if v['visit_type'] == 'Return'])
                st.metric("Return Visits", return_rate)
            
            with col4:
                avg_age = sum([int(v.get('age', 30)) for v in visit_data]) / len(visit_data) if visit_data else 0
                st.metric("Avg Age", f"{avg_age:.1f}")
            
            # Visit Trends
            st.subheader("📈 Visit Analysis")
            
            # Common Issues
            issues = [v['issue'] for v in visit_data]
            issue_counts = {}
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Most Common Issues:**")
                for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {issue}: {count} patients")
            
            with col2:
                st.markdown("**Age Distribution:**")
                age_groups = [v['age_group'] for v in visit_data]
                age_counts = {}
                for group in age_groups:
                    age_counts[group] = age_counts.get(group, 0) + 1
                
                for group, count in age_counts.items():
                    st.write(f"• {group}: {count} patients")
            
            # Marketing Insights
            st.subheader("💼 Marketing Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Patient Retention:**")
                retention_rate = (return_rate / total_visits * 100) if total_visits > 0 else 0
                st.metric("Retention Rate", f"{retention_rate:.1f}%")
                
                if retention_rate > 30:
                    st.success("✅ Good patient retention!")
                else:
                    st.warning("⚠️ Focus on patient follow-up")
            
            with col2:
                st.markdown("**Growth Opportunities:**")
                if new_patients > return_rate:
                    st.info("📈 Strong new patient acquisition")
                    st.write("• Focus on retention programs")
                    st.write("• Implement follow-up reminders")
                else:
                    st.info("🔄 Good patient loyalty")
                    st.write("• Expand marketing reach")
                    st.write("• Referral programs")
        
        else:
            st.info("📈 No visit data yet. Register patients to see analytics.")
            st.markdown("**Analytics will track:**")
            st.markdown("• Patient demographics and trends")
            st.markdown("• Common eye issues and treatments")
            st.markdown("• Return visit patterns")
            st.markdown("• Marketing effectiveness")
            st.markdown("• Seasonal patterns")
            st.markdown("• Revenue analysis")

if __name__ == "__main__":
    main()