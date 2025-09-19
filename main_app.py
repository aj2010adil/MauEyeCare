#!/usr/bin/env python3
"""
MauEyeCare - Professional Eye Care Hospital Management System
Google Sheets Integration for Real-time Data Management
"""

import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime, timezone, timedelta
import json
from io import BytesIO

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Core imports
from modules.google_sheets_manager import sheets_manager
from modules.image_manager import image_manager
from modules.local_data_manager import local_data_manager
from modules.google_sheets_api import google_sheets_api
from modules.sync_manager import sync_manager
from modules.oauth_sheets_api import oauth_sheets_api
from modules.patient_manager import patient_manager

# Lazy imports for better performance
@st.cache_data
def get_spectacle_database():
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    return COMPREHENSIVE_SPECTACLE_DATABASE

@st.cache_data
def get_medicine_database():
    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
    return COMPREHENSIVE_MEDICINE_DATABASE

@st.cache_data
def get_sheet_data():
    """Load data from Google Sheets"""
    try:
        medicines = sheets_manager.get_medicines()
        spectacles = sheets_manager.get_spectacles()
        patients = sheets_manager.get_patients()
        return medicines, spectacles, patients
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {str(e)}")
        return [], [], []

def main():
    st.set_page_config(
        page_title="MauEyeCare", 
        page_icon="👁️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 MauEyeCare - Professional Eye Care Hospital")
    st.markdown("*Google Sheets Integrated Hospital Management System*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Sync Google Sheets"):
            with st.spinner("Syncing with Google Sheets..."):
                try:
                    get_sheet_data.clear()
                    medicines, spectacles, patients = get_sheet_data()
                    st.success(f"✅ Synced: {len(medicines)} medicines, {len(spectacles)} spectacles, {len(patients)} patients!")
                except Exception as e:
                    st.error(f"❌ Sync failed: {str(e)}")
        
        if st.button("📦 Load Sample Inventory"):
            with st.spinner("Loading sample inventory..."):
                try:
                    from modules.separate_inventory import initialize_sample_inventory
                    initialize_sample_inventory()
                    st.success("✅ Sample inventory loaded!")
                except Exception as e:
                    st.error(f"❌ Failed to load inventory: {str(e)}")
        
        # Show pending data status
        pending_patients = len(st.session_state.get('pending_patients', []))
        pending_prescriptions = len(st.session_state.get('pending_prescriptions', []))
        
        if pending_patients > 0 or pending_prescriptions > 0:
            st.warning(f"⚠️ {pending_patients} patients, {pending_prescriptions} prescriptions pending sync")
            if st.button("📤 Sync to Google Sheets"):
                if oauth_sheets_api.is_authenticated():
                    with st.spinner("Syncing to Google Sheets..."):
                        success_count = 0
                        # Sync patients
                        for patient in st.session_state.get('pending_patients', []):
                            result = oauth_sheets_api.add_patient(patient)
                            if result['success']:
                                success_count += 1
                        
                        # Sync prescriptions
                        for prescription in st.session_state.get('pending_prescriptions', []):
                            result = oauth_sheets_api.add_prescription(prescription)
                            if result['success']:
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"✅ Synced {success_count} records!")
                            # Clear synced data
                            st.session_state['pending_patients'] = []
                            st.session_state['pending_prescriptions'] = []
                            st.rerun()
                        else:
                            st.error("❌ Sync failed!")
                else:
                    st.error("❌ Please authenticate first!")
        
        st.markdown("---")
        st.markdown("**📊 Database Stats:**")
        
        col1, col2 = st.columns(2)
        with col1:
            # Show Google Sheets data first
            try:
                medicines, spectacles, _ = get_sheet_data()
                st.metric("👓 Google Sheets Spectacles", len(spectacles))
                st.metric("💊 Google Sheets Medicines", len(medicines))
            except:
                st.metric("👓 Local Spectacles", len(get_spectacle_database()))
                st.metric("💊 Local Medicines", len(get_medicine_database()))
                st.caption("Google Sheets: Not connected")
        
        with col2:
            try:
                medicines, spectacles, patients = get_sheet_data()
                total_items = len(medicines) + len(spectacles)
                st.metric("📦 Google Sheets Items", total_items)
                st.caption(f"{len(medicines)} medicines + {len(spectacles)} spectacles")
                
                # Show Google Sheets patients + pending patients
                pending_patients = len(st.session_state.get('pending_patients', []))
                total_patients = len(patients) + pending_patients
                st.metric("👥 Total Patients", total_patients)
                if pending_patients > 0:
                    st.caption(f"{len(patients)} in Google Sheets + {pending_patients} pending")
                else:
                    st.caption(f"{len(patients)} in Google Sheets")
            except Exception as e:
                pending_patients = len(st.session_state.get('pending_patients', []))
                st.metric("📦 Google Sheets Items", 0)
                st.metric("👥 Total Patients", pending_patients)
                st.caption("Google Sheets: Connection Error")
                if pending_patients > 0:
                    st.caption(f"Local: {pending_patients} pending patients")
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Gender: {st.session_state.get('gender', 'N/A')}")
        
        # OAuth Authentication Status
        st.markdown("---")
        st.markdown("**🔐 Authentication Status:**")
        
        if oauth_sheets_api.is_authenticated():
            st.success("✅ OAuth: Authenticated")
            st.info("📝 Real-time writing enabled")
        else:
            st.warning("⚠️ OAuth: Not authenticated")
            auth_url = oauth_sheets_api.get_auth_url()
            if auth_url:
                st.markdown(f"**[🔐 Authenticate with Google]({auth_url})**")
                st.caption("Click to enable real-time sync")
            else:
                st.error("❌ OAuth not configured")
                st.caption("Add Google OAuth credentials to secrets.toml")
        
        # Google Sheets Status
        st.markdown("**📊 Google Sheets Status:**")
        
        # Test connection using sync manager
        connection_result = sync_manager.test_google_sheets_connection()
        if connection_result['success']:
            st.success("✅ Reading: Connected")
            st.info(f"Sheet ID: ...{google_sheets_api.sheet_id[-8:]}")
        else:
            st.error("❌ Reading: Connection Error")
        
        # Show inventory status
        try:
            from modules.separate_inventory import get_medicine_list, get_spectacle_list
            medicines = get_medicine_list()
            spectacles = get_spectacle_list()
            if medicines or spectacles:
                st.info(f"📦 Local inventory: {len(medicines)} medicines, {len(spectacles)} spectacles")
        except:
            pass

    # Handle OAuth callback
    query_params = st.experimental_get_query_params()
    if 'code' in query_params and oauth_sheets_api.client_id:
        code = query_params['code'][0]
        state = query_params.get('state', [None])[0]
        
        with st.spinner("Authenticating with Google..."):
            result = oauth_sheets_api.exchange_code_for_token(code, state)
            if result['success']:
                st.success("✅ Authentication successful! Real-time sync enabled.")
                st.experimental_set_query_params()
                st.rerun()
            else:
                st.error(f"❌ Authentication failed: {result['error']}")
                st.info("💡 Check your OAuth credentials in secrets.toml")
                # Clear query params on error
                st.experimental_set_query_params()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👥 Patient Registration", 
        "👓 Spectacle Gallery", 
        "📋 Patient History",
        "📤 Prescription Generator",
        "📊 Hospital Analytics",
        "📊 Google Sheets Setup",
        "🔄 Data Sync"
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
                email = st.text_input("Email (Optional)", placeholder="Enter email address")
                address = st.text_area("Address", placeholder="Enter full address", height=60)
                city = st.text_input("City", placeholder="Enter city")
                state = st.selectbox("State", ["Uttar Pradesh", "Bihar", "Jharkhand", "West Bengal", "Delhi", "Maharashtra", "Gujarat", "Rajasthan", "Punjab", "Haryana", "Madhya Pradesh", "Other"])
                pincode = st.text_input("Pincode", placeholder="Enter pincode")
                
            # Move issue and advice to new row
            col_issue1, col_issue2 = st.columns(2)
            
            with col_issue1:
                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                
            with col_issue2:
                advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Glaucoma Screening", "Diabetic Eye Exam", "Other"]
                advice = st.selectbox("Advice/Notes", advice_options)
            
            # Eye Care Demographics Section
            st.markdown("**👁️ Eye Care Demographics & History**")
            
            col_demo1, col_demo2, col_demo3 = st.columns(3)
            
            with col_demo1:
                occupation = st.selectbox("Occupation", [
                    "Student", "Office Worker", "Driver", "Teacher", "Doctor", "Engineer", 
                    "Farmer", "Homemaker", "Retired", "Other"
                ])
                screen_time = st.selectbox("Daily Screen Time", [
                    "<2 hours", "2-4 hours", "4-6 hours", "6-8 hours", ">8 hours"
                ])
            
            with col_demo2:
                family_history = st.selectbox("Family Eye History", [
                    "None", "Diabetes", "Glaucoma", "Cataract", "Myopia", "Other"
                ])
                previous_surgery = st.selectbox("Previous Eye Surgery", [
                    "None", "Cataract", "LASIK", "Retinal", "Glaucoma", "Other"
                ])
            
            with col_demo3:
                diabetes = st.selectbox("Diabetes Status", ["No", "Type 1", "Type 2", "Pre-diabetic"])
                hypertension = st.selectbox("Blood Pressure", ["Normal", "High", "Low", "Controlled"])
            
            # Additional Eye Care Fields
            col_eye1, col_eye2 = st.columns(2)
            
            with col_eye1:
                last_eye_exam = st.selectbox("Last Eye Exam", [
                    "<6 months", "6-12 months", "1-2 years", ">2 years", "Never"
                ])
                current_glasses = st.selectbox("Current Glasses/Contacts", [
                    "None", "Reading Glasses", "Distance Glasses", "Bifocals", "Contact Lenses"
                ])
            
            with col_eye2:
                eye_strain = st.selectbox("Eye Strain Frequency", [
                    "Never", "Rarely", "Sometimes", "Often", "Always"
                ])
                referral_source = st.selectbox("How did you hear about us?", [
                    "Walk-in", "Friend/Family", "Doctor Referral", "Online", "Advertisement", "Other"
                ])
            
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
                    od_sphere = st.text_input("Custom Sphere OD (e.g., +2.75, -1.25)", key="custom_sphere_od", help="Enter any value like +2.75, -1.25, etc.")
                
                od_cylinder_mode = st.radio("Cylinder OD Input", ["Select from list", "Custom value"], key="od_cylinder_mode")
                if od_cylinder_mode == "Select from list":
                    od_cylinder = st.selectbox("Cylinder OD", cylinder_options, key="cylinder_od")
                else:
                    od_cylinder = st.text_input("Custom Cylinder OD (e.g., -0.75)", key="custom_cylinder_od", help="Enter any cylinder value")
                
                od_axis_mode = st.radio("Axis OD Input", ["Select from list", "Custom value"], key="od_axis_mode")
                if od_axis_mode == "Select from list":
                    od_axis = st.selectbox("Axis OD", axis_options, key="axis_od")
                else:
                    od_axis = st.text_input("Custom Axis OD (0-180)", key="custom_axis_od", help="Enter axis value between 0-180")
            
            with col_os:
                st.markdown("**OS (Left Eye)**")
                os_sphere_mode = st.radio("Sphere OS Input", ["Select from list", "Custom value"], key="os_sphere_mode")
                if os_sphere_mode == "Select from list":
                    os_sphere = st.selectbox("Sphere OS", sphere_options, key="sphere_os")
                else:
                    os_sphere = st.text_input("Custom Sphere OS (e.g., +2.75, -1.25)", key="custom_sphere_os", help="Enter any value like +2.75, -1.25, etc.")
                
                os_cylinder_mode = st.radio("Cylinder OS Input", ["Select from list", "Custom value"], key="os_cylinder_mode")
                if os_cylinder_mode == "Select from list":
                    os_cylinder = st.selectbox("Cylinder OS", cylinder_options, key="cylinder_os")
                else:
                    os_cylinder = st.text_input("Custom Cylinder OS (e.g., -0.75)", key="custom_cylinder_os", help="Enter any cylinder value")
                
                os_axis_mode = st.radio("Axis OS Input", ["Select from list", "Custom value"], key="os_axis_mode")
                if os_axis_mode == "Select from list":
                    os_axis = st.selectbox("Axis OS", axis_options, key="axis_os")
                else:
                    os_axis = st.text_input("Custom Axis OS (0-180)", key="custom_axis_os", help="Enter axis value between 0-180")
            
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
            
            # Load medicines from multiple sources
            filtered_rx_medicines = {}
            
            # 1. Load from separate inventory (primary)
            try:
                from modules.separate_inventory import load_medicine_inventory
                medicine_inventory = load_medicine_inventory()
                for med_name, med_data in medicine_inventory.items():
                    if isinstance(med_data, dict):
                        filtered_rx_medicines[med_name] = {
                            'category': med_data.get('category', 'Medicine'),
                            'type': med_data.get('type', 'Medicine'),
                            'price': med_data.get('price', 100),
                            'prescription_required': True,
                            'indication': 'As prescribed',
                            'dosage': 'As prescribed',
                            'quantity': med_data.get('quantity', 0)
                        }
                    else:
                        filtered_rx_medicines[med_name] = {
                            'category': 'Medicine',
                            'type': 'Medicine',
                            'price': 100,
                            'prescription_required': True,
                            'indication': 'As prescribed',
                            'dosage': 'As prescribed',
                            'quantity': med_data if isinstance(med_data, int) else 0
                        }
            except:
                pass
            
            # 2. Load from Google Sheets (secondary)
            try:
                medicines, _, _ = get_sheet_data()
                for med in medicines:
                    if isinstance(med, dict) and 'name' in med and med['name'] not in filtered_rx_medicines:
                        filtered_rx_medicines[med['name']] = {
                            'category': med.get('category', 'General'),
                            'type': med.get('type', 'Medicine'),
                            'price': med.get('price', 100),
                            'prescription_required': med.get('prescription_required', True),
                            'indication': med.get('indication', 'As prescribed'),
                            'dosage': med.get('dosage', 'As prescribed'),
                            'quantity': med.get('quantity', 0)
                        }
            except:
                pass
            
            # 3. Fallback to comprehensive database
            if not filtered_rx_medicines:
                COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
                filtered_rx_medicines = COMPREHENSIVE_MEDICINE_DATABASE.copy()
            
            # 4. Add custom medicines from session
            if 'custom_medicines' in st.session_state:
                filtered_rx_medicines.update(st.session_state['custom_medicines'])
            
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
                
                # Pagination for medicines
                medicines_per_page = 50
                total_medicines = len(filtered_rx_medicines)
                
                if total_medicines > medicines_per_page:
                    page = st.selectbox(f"Page (Total: {total_medicines} medicines)", 
                                       range(1, (total_medicines // medicines_per_page) + 2),
                                       key="medicine_page")
                    start_idx = (page - 1) * medicines_per_page
                    end_idx = start_idx + medicines_per_page
                    display_medicines = dict(list(filtered_rx_medicines.items())[start_idx:end_idx])
                    st.info(f"Showing medicines {start_idx + 1}-{min(end_idx, total_medicines)} of {total_medicines}")
                else:
                    display_medicines = filtered_rx_medicines
                
                selected_rx_medicines = st.multiselect(
                    f"Select medicines ({len(display_medicines)} shown of {total_medicines} total):",
                    options=list(display_medicines.keys()),
                    default=[k for k in st.session_state.get('selected_medicines', {}).keys() if k in display_medicines],
                    key="rx_medicine_multiselect"
                )
                
                # Enhanced medicine details with doctor controls
                if selected_rx_medicines:
                    st.markdown("**💊 Medicine Prescription Details:**")
                    medicine_details = {}
                    
                    for med_name in selected_rx_medicines:
                        med_data = display_medicines.get(med_name, {})
                        
                        with st.expander(f"📋 {med_name} - ₹{med_data.get('price', 100)}"):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                qty = st.number_input("Quantity", min_value=1, max_value=20, value=1, key=f"qty_{hash(med_name)}")
                            
                            with col2:
                                dosage_options = [
                                    "1 drop in each eye", "2 drops in each eye", "1 drop twice daily",
                                    "1 tablet daily", "1 tablet twice daily", "1 capsule daily",
                                    "Apply thin layer", "As needed"
                                ]
                                dosage = st.selectbox("Dosage", ["Custom"] + dosage_options, key=f"dosage_{hash(med_name)}")
                                if dosage == "Custom":
                                    dosage = st.text_input("Custom Dosage", value=med_data.get('dosage', ''), key=f"custom_dosage_{hash(med_name)}")
                            
                            with col3:
                                timing_options = ["Morning", "Evening", "Morning & Evening", "After meals", "Before meals", "As needed"]
                                timing = st.selectbox("Timing", timing_options, key=f"timing_{hash(med_name)}")
                            
                            with col4:
                                duration = st.selectbox("Duration", 
                                    ["3 days", "5 days", "7 days", "10 days", "14 days", "1 month", "Custom"], 
                                    key=f"duration_{hash(med_name)}")
                                if duration == "Custom":
                                    duration = st.text_input("Custom Duration", key=f"custom_duration_{hash(med_name)}")
                            
                            # Doctor's notes
                            notes = st.text_area("Doctor's Notes (Optional)", 
                                placeholder="Special instructions, warnings, or additional notes...",
                                key=f"notes_{hash(med_name)}", height=60)
                            
                            # Medicine info
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.info(f"**Type:** {med_data.get('type', 'Medicine')} | **Category:** {med_data.get('category', 'General')}")
                            with col_info2:
                                st.info(f"**Indication:** {med_data.get('indication', 'As prescribed')}")
                            
                            medicine_details[med_name] = {
                                'quantity': qty,
                                'dosage': dosage,
                                'timing': timing,
                                'duration': duration,
                                'notes': notes,
                                'price': med_data.get('price', 100),
                                'total_cost': med_data.get('price', 100) * qty
                            }
                    
                    # Store medicine details in session
                    st.session_state['selected_medicines'] = {med: medicine_details[med]['quantity'] for med in medicine_details}
                    st.session_state['medicine_details'] = medicine_details
                    
                    # Show total medicine cost and summary
                    total_med_cost = sum([details['total_cost'] for details in medicine_details.values()])
                    st.success(f"**Total Medicine Cost: ₹{total_med_cost:,}**")
                    
                    # Quick summary with stock updates
                    with st.expander("📋 Prescription Summary & Stock Status"):
                        for med_name, details in medicine_details.items():
                            st.write(f"• **{med_name}**: {details['dosage']} | {details.get('timing', '')} | {details['duration']}")
                            if details.get('notes'):
                                st.write(f"  📝 *{details['notes']}*")
                            
                            # Get current stock from inventory
                            current_stock = filtered_rx_medicines.get(med_name, {}).get('quantity', 0)
                            new_stock = current_stock - details['quantity']
                            
                            # Show stock alerts
                            if new_stock <= 0:
                                st.error(f"  ❌ OUT OF STOCK after prescription! (Current: {current_stock})")
                            elif new_stock < 5:
                                st.warning(f"  ⚠️ LOW STOCK: {new_stock} remaining (Current: {current_stock})")
                            else:
                                st.success(f"  ✅ Stock OK: {new_stock} remaining (Current: {current_stock})")
            

            
            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis}
            }
            
            submitted = st.form_submit_button("💾 Register Patient", type="primary")
            
            if submitted and patient_name:
                # Create patient record with all demographics
                patient_record = {
                    'name': patient_name,
                    'age': age,
                    'gender': gender,
                    'mobile': contact,
                    'email': email,
                    'address': address,
                    'city': city,
                    'state': state,
                    'pincode': pincode,
                    'issue': patient_issue,
                    'advice': advice,
                    'occupation': occupation,
                    'screen_time': screen_time,
                    'family_history': family_history,
                    'diabetes': diabetes,
                    'hypertension': hypertension,
                    'last_eye_exam': last_eye_exam,
                    'current_glasses': current_glasses,
                    'eye_strain': eye_strain,
                    'referral_source': referral_source
                }
                
                # Register patient using patient manager
                result = patient_manager.register_patient(patient_record)
                
                if result['success']:
                    if result['new_patient']:
                        st.success(f"✅ **New Patient Registered!** {patient_name} - Visit #1")
                        st.balloons()
                    else:
                        st.success(f"🔄 **Return Visit Recorded!** {patient_name} - Visit #{result['visits']}")
                    
                    # Show patient summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Patient ID", result['patient_id'])
                    with col2:
                        st.metric("Total Visits", result['visits'])
                    with col3:
                        st.metric("Status", "New" if result['new_patient'] else "Return")
                    
                    if oauth_sheets_api.is_authenticated():
                        st.info("✅ **Real-time sync enabled** - Data saved to Google Sheets instantly!")
                    else:
                        st.info("📊 **Data saved locally** - Authenticate for real-time sync")
                else:
                    st.error(f"❌ Registration failed: {result['error']}")
                
                # Track visit data for analytics
                current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                visit_data = {
                    'patient_id': st.session_state.get('patient_id'),
                    'visit_date': current_time.isoformat(),
                    'issue': patient_issue,
                    'advice': advice,
                    'rx_data': rx_table,
                    'age_group': 'Child' if age < 18 else 'Adult' if age < 60 else 'Senior',
                    'visit_type': 'New' if result.get('new_patient') else 'Return',
                    'referral_source': referral_source,
                    'season': current_time.strftime('%B'),
                    'occupation': occupation,
                    'screen_time': screen_time,
                    'family_history': family_history,
                    'diabetes': diabetes,
                    'hypertension': hypertension,
                    'last_eye_exam': last_eye_exam,
                    'current_glasses': current_glasses,
                    'eye_strain': eye_strain
                }
                
                # Store visit data in session for analytics
                if 'visit_analytics' not in st.session_state:
                    st.session_state['visit_analytics'] = []
                st.session_state['visit_analytics'].append(visit_data)
                
                # Store RX table for prescription generation
                st.session_state['rx_table'] = rx_table
                
                st.info("🎯 Ready for prescription! Go to 'Spectacle Gallery' or 'Prescription Generator' tab.")
        
        # Patient Process Management
        st.markdown("---")
        st.subheader("🔄 Patient Process Control")
        
        current_patient = patient_manager.get_patient_summary()
        if current_patient:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Current Patient:** {current_patient['name']}")
            with col2:
                st.info(f"**Visit #{current_patient['visits']}** ({'New' if current_patient['is_new'] else 'Return'})")
            with col3:
                if st.button("✅ Complete & Next Patient", type="primary"):
                    patient_manager.complete_patient_process()
                    st.success("✅ Patient process completed! Ready for next patient.")
                    st.rerun()
        
        # Custom Medicine Addition (Outside Form)
        st.markdown("---")
        st.markdown("### ➕ Add Custom Medicine")
        st.info("📝 Add medicines not in our database")
        
        with st.expander("Add Custom Medicine"):
            col_custom1, col_custom2, col_custom3 = st.columns(3)
            
            with col_custom1:
                custom_med_name = st.text_input("Medicine Name", key="custom_med_name_outside")
                custom_med_type = st.selectbox("Type", ["Eye Drops", "Tablet", "Capsule", "Ointment", "Gel", "Injection"], key="custom_med_type_outside")
            
            with col_custom2:
                custom_med_usage = st.selectbox("Usage", ["Internal", "External"], key="custom_med_usage_outside")
                custom_med_price = st.number_input("Price (₹)", min_value=0, value=100, key="custom_med_price_outside")
            
            with col_custom3:
                custom_med_dosage = st.text_input("Dosage Instructions", key="custom_med_dosage_outside")
                custom_med_qty = st.number_input("Quantity", min_value=1, value=1, key="custom_med_qty_outside")
            
            if st.button("➕ Add Custom Medicine", key="add_custom_med_outside"):
                if custom_med_name:
                    try:
                        from modules.separate_inventory import add_medicine_inventory
                        add_medicine_inventory(custom_med_name, custom_med_qty, custom_med_price, custom_med_usage, custom_med_type)
                        st.success(f"✅ Added: {custom_med_name} (Qty: {custom_med_qty}, ₹{custom_med_price})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to add medicine: {str(e)}")
                else:
                    st.warning("⚠️ Please enter medicine name")
        
        # Quick Patient Actions
        if current_patient:
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👓 Select Spectacles", use_container_width=True):
                    st.info("👓 Switch to 'Spectacle Gallery' tab")
            
            with col2:
                if st.button("📤 Generate Prescription", use_container_width=True):
                    st.info("📤 Switch to 'Prescription Generator' tab")
            
            with col3:
                if st.button("🔄 New Patient", use_container_width=True):
                    patient_manager.complete_patient_process()
                    st.rerun()

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
        
        # Load spectacles from Google Sheets first
        try:
            _, spectacles, _ = get_sheet_data()
            if spectacles:
                # Convert Google Sheets spectacles to database format
                filtered_specs = {}
                for spec in spectacles:
                    if isinstance(spec, dict) and 'name' in spec:
                        filtered_specs[spec['name']] = {
                            'brand': spec.get('brand', 'Generic'),
                            'model': spec.get('model', 'Standard'),
                            'category': spec.get('category', 'Mid-Range'),
                            'price': spec.get('price', 5000),
                            'lens_price': spec.get('lens_price', 2000),
                            'material': spec.get('material', 'Plastic'),
                            'shape': spec.get('shape', 'Square'),
                            'quantity': spec.get('quantity', 0)
                        }
                st.success(f"✅ Loaded {len(filtered_specs)} spectacles from Google Sheets")
            else:
                # Fallback to local database
                filtered_specs = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
                st.info("📦 Using local spectacle database")
        except Exception as e:
            # Fallback to local database
            filtered_specs = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
            st.warning(f"⚠️ Google Sheets error, using local database: {str(e)}")
        
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
                
                # Show stock status
                stock = spec_data.get('quantity', 0)
                if stock == 0:
                    st.error("❌ OUT OF STOCK")
                elif stock < 5:
                    st.warning(f"⚠️ LOW STOCK: {stock}")
                else:
                    st.success(f"✅ In Stock: {stock}")
                
                # Add to prescription button
                if st.button(f"➕ Add to Prescription", key=f"add_spec_{i}", disabled=(stock == 0)):
                    if 'selected_spectacles' not in st.session_state:
                        st.session_state['selected_spectacles'] = []
                    
                    if spec_name not in st.session_state['selected_spectacles']:
                        st.session_state['selected_spectacles'].append(spec_name)
                        st.success(f"Added {spec_data['brand']} {spec_data['model']}")
                        
                        # Update inventory count locally
                        if 'inventory_updates' not in st.session_state:
                            st.session_state['inventory_updates'] = {}
                        st.session_state['inventory_updates'][spec_name] = stock - 1
                        
                        # Show low stock warning
                        if stock - 1 < 5:
                            st.warning(f"⚠️ LOW STOCK ALERT: {spec_name} now has {stock - 1} units left!")
                    else:
                        st.warning("Already added to prescription")



    # --- Patient History Tab ---
    with tab3:
        st.header("📋 Patient History & Records")
        
        try:
            patients = sheets_manager.get_patients()
            # Convert to list format for compatibility
            if patients and isinstance(patients[0], dict):
                patients = [[p.get('id', i), p.get('name', ''), p.get('age', 0), p.get('gender', ''), p.get('mobile', ''), p.get('registration_date', '')] for i, p in enumerate(patients)]
        except:
            patients = []
        
        col1, col2 = st.columns(2)
        with col1:
            search_mobile = st.text_input("🔍 Search by Mobile Number")
        with col2:
            search_name = st.text_input("🔍 Search by Name")
        
        filtered = [p for p in patients if (search_mobile in str(p[4])) and (search_name.lower() in str(p[1]).lower())]
        
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
    with tab4:
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
                    # Load from Google Sheets first
                    try:
                        _, spectacles, _ = get_sheet_data()
                        spectacle_data = {}
                        for spec in spectacles:
                            if isinstance(spec, dict) and 'name' in spec:
                                spectacle_data[spec['name']] = spec
                    except:
                        spectacle_data = {}
                    
                    # Fallback to local database
                    if not spectacle_data:
                        COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
                        spectacle_data = COMPREHENSIVE_SPECTACLE_DATABASE
                    
                    for spec_name in selected_spectacles:
                        if spec_name in spectacle_data:
                            spec_data = spectacle_data[spec_name]
                            if isinstance(spec_data, dict):
                                total_price = spec_data.get('price', 5000) + spec_data.get('lens_price', 2000)
                                current_stock = spec_data.get('quantity', 0)
                                st.write(f"• {spec_data.get('brand', 'Generic')} {spec_data.get('model', 'Standard')} - ₹{total_price:,}")
                                
                                # Show stock status
                                if current_stock <= 1:
                                    st.error(f"  ❌ Will be OUT OF STOCK after sale!")
                                elif current_stock <= 5:
                                    st.warning(f"  ⚠️ LOW STOCK: {current_stock - 1} will remain")
                                else:
                                    st.success(f"  ✅ Stock OK: {current_stock - 1} will remain")
                else:
                    st.info("No spectacles selected")
            
            with col2:
                st.markdown("### 💊 Selected Medicines")
                medicine_details = st.session_state.get('medicine_details', {})
                
                if medicine_details:
                    for med_name, details in medicine_details.items():
                        st.write(f"• {med_name} (Qty: {details['quantity']}) - ₹{details['total_cost']}")
                        st.write(f"  Dosage: {details['dosage']} | Duration: {details['duration']}")
                else:
                    st.info("No medicines selected")
            
            # Generate prescription
            st.markdown("---")
            
            if st.button("📤 Generate Prescription", type="primary"):
                if selected_spectacles or medicine_details:
                    # Update inventory for used items
                    inventory_updated = False
                    try:
                        from modules.separate_inventory import reduce_spectacle_stock, reduce_medicine_stock
                        
                        # Update spectacle inventory
                        for spec_name in selected_spectacles:
                            reduce_spectacle_stock(spec_name, 1)
                        
                        # Update medicine inventory
                        for med_name, details in medicine_details.items():
                            reduce_medicine_stock(med_name, details['quantity'])
                        
                        inventory_updated = True
                        
                        # Also update Google Sheets inventory if OAuth available
                        if oauth_sheets_api.is_authenticated():
                            for spec_name in selected_spectacles:
                                oauth_sheets_api.update_inventory(spec_name, -1, "spectacle")
                            for med_name, details in medicine_details.items():
                                oauth_sheets_api.update_inventory(med_name, -details['quantity'], "medicine")
                        
                    except ImportError:
                        st.warning("⚠️ Inventory module not available - stock not updated")
                    
                    if inventory_updated:
                        st.success("✅ Inventory updated successfully!")
                    
                    # Add prescription record
                    prescription_data = {
                        'patient_name': patient_name,
                        'patient_mobile': st.session_state.get('patient_mobile', ''),
                        'spectacles': selected_spectacles,
                        'medicines': medicine_details,
                        'rx_table': st.session_state.get('rx_table', {}),
                        'total_cost': sum([details['total_cost'] for details in medicine_details.values()])
                    }
                    
                    # Save prescription using OAuth if available
                    if oauth_sheets_api.is_authenticated():
                        oauth_sheets_api.add_prescription(prescription_data)
                    else:
                        # Store locally for later sync
                        if 'pending_prescriptions' not in st.session_state:
                            st.session_state['pending_prescriptions'] = []
                        st.session_state['pending_prescriptions'].append(prescription_data)
                    # Create professional HTML prescription
                    current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                    prescription_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MauEyeCare Prescription - {patient_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, rgba(46, 134, 171, 0.95) 0%, rgba(30, 95, 139, 0.95) 100%); }}
        .prescription-container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ text-align: center; background: #2E86AB; color: white; padding: 40px 30px; }}
        .logo {{ width: 80px; height: 80px; background: white; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px; color: #2E86AB; }}
        .clinic-name {{ font-size: 36px; font-weight: 900; margin: 15px 0; }}
        .doctor-info {{ font-size: 18px; margin: 8px 0; font-weight: 600; }}
        .patient-info {{ background: #f8f9ff; padding: 25px; border-left: 5px solid #2E86AB; }}
        .prescription {{ background: white; padding: 25px; border-bottom: 1px solid #eee; }}
        .item {{ background: linear-gradient(135deg, #f0f8ff, #e6f3ff); padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #2E86AB; }}
        .total {{ background: linear-gradient(135deg, #e8f5e8, #d4f4d4); padding: 20px; border-radius: 10px; font-weight: bold; text-align: center; margin: 15px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-top: 2px solid #2E86AB; }}
        .section-title {{ color: #2E86AB; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #2E86AB; padding-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="prescription-container">
        <div class="header">
            <div class="logo">👁️</div>
            <div class="clinic-name">MauEyeCare Optical Center</div>
            <div class="doctor-info">Dr. Danish - Eye Care Specialist</div>
            <div class="doctor-info">Registration No: UPS 2908</div>
            <div class="doctor-info">📞 +91 92356-47410 | 📧 maueyecare@gmail.com</div>
        </div>
    
        <div class="patient-info">
            <div class="section-title">👤 Patient Information</div>
            <p><strong>Name:</strong> {patient_name}</p>
            <p><strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')}</p>
            <p><strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')}</p>
            <p><strong>Address:</strong> {st.session_state.get('patient_address', 'N/A')}</p>
            <p><strong>City:</strong> {st.session_state.get('patient_city', 'N/A')}, {st.session_state.get('patient_state', 'N/A')} - {st.session_state.get('patient_pincode', 'N/A')}</p>
            <p><strong>Date:</strong> {current_time.strftime('%d/%m/%Y %I:%M %p IST')}</p>
        </div>"""
                    
                    # Add eye prescription if available
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
                    
                    # Add spectacles
                    if selected_spectacles:
                        prescription_html += """
        <div class="prescription">
            <div class="section-title">👓 Recommended Spectacles</div>"""
                        
                        total_spec_cost = 0
                        COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
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
                    
                    # Add medicines
                    if medicine_details:
                        prescription_html += """
        <div class="prescription">
            <div class="section-title">💊 Prescribed Medicines</div>"""
                        
                        total_med_cost = 0
                        for med_name, details in medicine_details.items():
                            total_med_cost += details['total_cost']
                            prescription_html += f"""
        <div class="item">
            <strong>{med_name}</strong><br>
            Quantity: {details['quantity']} | Dosage: {details['dosage']}<br>
            Duration: {details['duration']}<br>
            Price: ₹{details['price']} x {details['quantity']} = <strong>₹{details['total_cost']}</strong>
        </div>"""
                        
                        prescription_html += f"""
        <div class="total">Total Medicine Cost: ₹{total_med_cost:,}</div>
    </div>"""
                    
                    # Add footer
                    prescription_html += f"""
        <div class="footer">
            <p><strong>Dr. Danish</strong> - Eye Care Specialist</p>
            <p>MauEyeCare Optical Center</p>
            <p>📞 +91 92356-47410 | 📧 maueyecare@gmail.com</p>
        </div>
    </div>
</body>
</html>"""
                    
                    # Download and sharing options
                    timestamp = current_time.strftime("%Y%m%d_%H%M")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            "💾 Download HTML Prescription",
                            data=prescription_html.encode('utf-8'),
                            file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col2:
                        # WhatsApp sharing
                        patient_mobile = st.session_state.get('patient_mobile')
                        if patient_mobile and st.button("📱 Share via WhatsApp", use_container_width=True):
                            from modules.whatsapp_utils import format_prescription_message, send_via_whatsapp_web
                            
                            # Create a simple prescription link (demo)
                            prescription_link = f"https://maueyecare.streamlit.app/prescription/{timestamp}"
                            message = format_prescription_message(patient_name, prescription_link)
                            whatsapp_url = send_via_whatsapp_web(patient_mobile, message)
                            
                            st.markdown(f"**[🌐 Send via WhatsApp Web]({whatsapp_url})**")
                            st.success("📱 WhatsApp message ready!")
                    
                    st.success("✅ Professional prescription generated!")
                    
                    # Clear selections for next prescription
                    if st.button("🔄 New Prescription", type="secondary"):
                        keys_to_clear = ['selected_spectacles', 'selected_medicines', 'medicine_details']
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.success("🎆 Ready for new prescription!")
                        st.rerun()
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine")
        else:
            st.warning("⚠️ Please select a patient first")

    # --- Hospital Analytics Tab ---
    with tab5:
        st.header("📊 Hospital Analytics")
        
        # Load analytics from local data manager
        analytics_data = local_data_manager.load_json_data('analytics.json', [])
        visit_data = st.session_state.get('visit_analytics', [])
        all_data = visit_data + analytics_data if analytics_data else visit_data
        
        if analytics_data:
            st.success(f"✅ Loaded {len(analytics_data)} analytics records from synced data")
        else:
            st.info("📊 Using local visit data only")
        
        if all_data:
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_visits = len(all_data)
                st.metric("Total Visits", total_visits)
            
            with col2:
                new_patients = len([v for v in all_data if v.get('visit_type') == 'New'])
                st.metric("New Patients", new_patients)
            
            with col3:
                return_visits = len([v for v in all_data if v.get('visit_type') == 'Return'])
                st.metric("Return Visits", return_visits)
            
            with col4:
                if all_data:
                    ages = [v.get('patient_age', 30) if isinstance(v.get('patient_age'), int) else 30 for v in all_data]
                    avg_age = sum(ages) / len(ages)
                    st.metric("Avg Age", f"{avg_age:.1f}")
                else:
                    st.metric("Avg Age", "0")
            
            # Visit Analysis
            st.subheader("📈 Visit Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Most Common Issues:**")
                issues = [v.get('issue', 'Unknown') for v in all_data if v.get('issue')]
                issue_counts = {}
                for issue in issues:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
                for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {issue}: {count} patients")
            
            with col2:
                st.markdown("**Age Distribution:**")
                age_groups = [v.get('age_group', 'Adult') for v in all_data if v.get('age_group')]
                age_counts = {}
                for group in age_groups:
                    age_counts[group] = age_counts.get(group, 0) + 1
                
                for group, count in age_counts.items():
                    st.write(f"• {group}: {count} patients")
            
            # Eye Care Demographics Analysis
            st.subheader("👁️ Eye Care Demographics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Occupation Analysis:**")
                occupations = [v.get('occupation', 'Unknown') for v in visit_data]
                occ_counts = {}
                for occ in occupations:
                    occ_counts[occ] = occ_counts.get(occ, 0) + 1
                
                for occ, count in sorted(occ_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    st.write(f"• {occ}: {count}")
            
            with col2:
                st.markdown("**Screen Time Impact:**")
                screen_times = [v.get('screen_time', 'Unknown') for v in visit_data]
                screen_counts = {}
                for screen in screen_times:
                    screen_counts[screen] = screen_counts.get(screen, 0) + 1
                
                for screen, count in sorted(screen_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    st.write(f"• {screen}: {count}")
            
            with col3:
                st.markdown("**Family History:**")
                family_hist = [v.get('family_history', 'None') for v in visit_data]
                family_counts = {}
                for hist in family_hist:
                    family_counts[hist] = family_counts.get(hist, 0) + 1
                
                for hist, count in sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    st.write(f"• {hist}: {count}")
            
            # Patient Retention
            st.subheader("🔄 Patient Retention")
            
            col1, col2 = st.columns(2)
            
            with col1:
                retention_rate = (return_visits / total_visits * 100) if total_visits > 0 else 0
                st.metric("Retention Rate", f"{retention_rate:.1f}%")
                
                if retention_rate > 30:
                    st.success("✅ Good patient retention!")
                else:
                    st.warning("⚠️ Focus on patient follow-up")
            
            with col2:
                st.markdown("**Growth Insights:**")
                if new_patients > return_visits:
                    st.info("📈 Strong new patient acquisition")
                    st.write("• Focus on retention programs")
                    st.write("• Implement follow-up reminders")
                else:
                    st.info("🔄 Good patient loyalty")
                    st.write("• Expand marketing reach")
                    st.write("• Referral programs")
            
            # Export Analytics
            st.markdown("---")
            st.subheader("📤 Export Analytics")
            
            if st.button("💾 Download Analytics Report"):
                # Create analytics report
                current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                report_data = {
                    'report_date': current_time.isoformat(),
                    'total_visits': total_visits,
                    'new_patients': new_patients,
                    'return_visits': return_visits,
                    'retention_rate': retention_rate,
                    'avg_age': avg_age,
                    'common_issues': issue_counts,
                    'age_distribution': age_counts,
                    'occupation_analysis': {occ: occ_counts.get(occ, 0) for occ in set(occupations)},
                    'screen_time_analysis': {screen: screen_counts.get(screen, 0) for screen in set(screen_times)},
                    'family_history_analysis': {hist: family_counts.get(hist, 0) for hist in set(family_hist)},
                    'visit_details': visit_data
                }
                
                report_json = json.dumps(report_data, indent=2)
                timestamp = current_time.strftime("%Y%m%d_%H%M")
                
                st.download_button(
                    "💾 Download JSON Report",
                    data=report_json.encode('utf-8'),
                    file_name=f"hospital_analytics_{timestamp}.json",
                    mime="application/json"
                )
        
        else:
            st.info("📈 No visit data yet. Register patients to see analytics.")
            st.markdown("**Analytics will track:**")
            st.markdown("• Patient demographics and trends")
            st.markdown("• Common eye issues and treatments")
            st.markdown("• Return visit patterns")
            st.markdown("• Patient retention rates")
            st.markdown("• Age distribution analysis")
    
    # --- Google Sheets Setup Tab ---
    with tab6:
        st.header("📊 Google Sheets Integration Setup")
        st.markdown("*Professional Eye Care Hospital Data Management*")
        
        # Connection Status
        st.subheader("🔗 Connection Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            try:
                medicines, spectacles, patients = get_sheet_data()
                if medicines or spectacles or patients:
                    st.success("✅ Google Sheets Connected")
                    st.info(f"Sheet ID: ...{sheets_manager.sheet_id[-8:]}")
                else:
                    st.warning("⚠️ No Data Found")
            except Exception as e:
                st.error("❌ Connection Failed")
                st.caption(f"Error: {str(e)[:50]}...")
        
        with col2:
            if st.button("🔄 Test Connection"):
                with st.spinner("Testing Google Sheets connection..."):
                    try:
                        test_data = sheets_manager.get_medicines()
                        if test_data:
                            st.success(f"✅ Connected! Found {len(test_data)} medicines")
                        else:
                            st.warning("⚠️ Connected but no data found")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
        
        with col3:
            if st.button("📥 Sync All Data"):
                with st.spinner("Syncing all data from Google Sheets..."):
                    get_sheet_data.clear()
                    medicines, spectacles, patients = get_sheet_data()
                    st.success(f"✅ Synced: {len(medicines)} medicines, {len(spectacles)} spectacles, {len(patients)} patients")
        
        st.markdown("---")
        
        # Sheet Configuration
        st.subheader("⚙️ Sheet Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Current Sheet ID:**")
            current_sheet_id = getattr(sheets_manager, 'sheet_id', '1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ')
            st.code(current_sheet_id)
            
            new_sheet_id = st.text_input(
                "🔄 Update Sheet ID (Optional):",
                placeholder="Enter new Google Sheet ID",
                help="Leave empty to use default sheet"
            )
            
            if st.button("💾 Update Sheet ID") and new_sheet_id:
                try:
                    sheets_manager.sheet_id = new_sheet_id
                    st.success("✅ Sheet ID updated successfully!")
                    st.info("🔄 Please test connection to verify")
                except Exception as e:
                    st.error(f"❌ Failed to update: {str(e)}")
        
        with col2:
            st.markdown("**📊 Required Tabs (Same Spreadsheet):**")
            required_sheets = [
                "📋 Medicines - Tab for medicine inventory",
                "👓 Spectacles - Tab for spectacle inventory", 
                "👥 Patients - Tab for patient records with demographics",
                "📄 Prescriptions - Tab for prescription history",
                "📈 Analytics - Tab for hospital analytics data"
            ]
            
            for sheet in required_sheets:
                st.info(sheet)
        
        st.markdown("---")
        
        # Data Templates
        st.subheader("📋 Tab Templates & Setup")
        st.info("📊 Each template below should be copied to a separate tab in your Google Sheet")
        
        tab_med, tab_spec, tab_pat, tab_presc, tab_anal = st.tabs(["💊 Medicines", "👓 Spectacles", "👥 Patients", "📄 Prescriptions", "📈 Analytics"])
        
        with tab_med:
            st.markdown("**Medicines Tab Template:**")
            st.info("📋 Create a tab named 'Medicines' with this data")
            medicine_template = pd.DataFrame({
                'name': ['Refresh Tears Eye Drops', 'Tobramycin Eye Drops', 'Prednisolone Eye Drops'],
                'category': ['Lubricant', 'Antibiotic', 'Steroid'],
                'type': ['Eye Drops', 'Eye Drops', 'Eye Drops'],
                'price': [150, 200, 180],
                'quantity': [50, 30, 25],
                'prescription_required': [False, True, True],
                'indication': ['Dry eyes', 'Bacterial infection', 'Inflammation'],
                'dosage': ['1-2 drops as needed', '1 drop 4 times daily', '1 drop twice daily']
            })
            
            st.dataframe(medicine_template, use_container_width=True)
            
            csv_med = medicine_template.to_csv(index=False)
            st.download_button(
                "📥 Download Medicines Tab Template",
                csv_med,
                "medicines_tab_template.csv",
                "text/csv",
                use_container_width=True
            )
        
        with tab_spec:
            st.markdown("**Spectacles Tab Template:**")
            st.info("👓 Create a tab named 'Spectacles' with this data")
            spectacle_template = pd.DataFrame({
                'name': ['Ray-Ban Aviator Classic', 'Oakley Holbrook', 'Titan Rimless'],
                'brand': ['Ray-Ban', 'Oakley', 'Titan'],
                'model': ['Aviator Classic', 'Holbrook', 'Rimless'],
                'category': ['Luxury', 'Mid-Range', 'Budget'],
                'price': [8000, 12000, 3500],
                'lens_price': [2000, 2500, 1500],
                'material': ['Metal', 'Plastic', 'Metal'],
                'shape': ['Aviator', 'Square', 'Rimless'],
                'image_path': ['images/rayban_aviator.jpg', 'images/oakley_holbrook.jpg', 'images/titan_rimless.jpg']
            })
            
            st.dataframe(spectacle_template, use_container_width=True)
            
            csv_spec = spectacle_template.to_csv(index=False)
            st.download_button(
                "📥 Download Spectacles Tab Template",
                csv_spec,
                "spectacles_tab_template.csv",
                "text/csv",
                use_container_width=True
            )
        
        with tab_pat:
            st.markdown("**Patients Tab Template:**")
            st.info("👥 Create a tab named 'Patients' with this data")
            patient_template = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['John Doe', 'Jane Smith', 'Raj Kumar'],
                'age': [35, 28, 45],
                'gender': ['Male', 'Female', 'Male'],
                'mobile': ['9876543210', '9876543211', '9876543212'],
                'registration_date': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'issue': ['Blurry Vision', 'Eye Pain', 'Dry Eyes'],
                'advice': ['Spectacle Prescription', 'Eye Drops', 'Regular Checkup'],
                'occupation': ['Office Worker', 'Teacher', 'Driver'],
                'screen_time': ['6-8 hours', '4-6 hours', '2-4 hours'],
                'family_history': ['Diabetes', 'None', 'Myopia'],
                'diabetes': ['No', 'Type 2', 'No'],
                'hypertension': ['Normal', 'High', 'Controlled'],
                'last_eye_exam': ['1-2 years', '<6 months', '>2 years'],
                'current_glasses': ['Distance Glasses', 'Reading Glasses', 'None'],
                'eye_strain': ['Often', 'Sometimes', 'Always'],
                'referral_source': ['Online', 'Doctor Referral', 'Friend/Family']
            })
            
            st.dataframe(patient_template, use_container_width=True)
            
            csv_pat = patient_template.to_csv(index=False)
            st.download_button(
                "📥 Download Patients Tab Template",
                csv_pat,
                "patients_tab_template.csv",
                "text/csv",
                use_container_width=True
            )
            
            # Generate prescription
            st.markdown("---")
            
            if st.button("📤 Generate & Share Prescription", type="primary"):
                medicine_details = st.session_state.get('medicine_details', {})
                selected_spectacles = st.session_state.get('selected_spectacles', [])
                selected_medicines = st.session_state.get('selected_medicines', {})
                if selected_spectacles or selected_medicines or medicine_details:
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
        <p><strong>Date & Time:</strong> {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y %I:%M %p IST')}</p>
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
                    if medicine_details or selected_medicines:
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
                                    COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
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
                            COMPREHENSIVE_MEDICINE_DATABASE = get_medicine_database()
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
                            st.info(f"**Upload Time:** {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y %H:%M IST')}")
                        
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
                        
                        # Download options
                        st.markdown("---")
                        st.markdown("### 💾 Download Options")
                        
                        col_dl1, col_dl2 = st.columns(2)
                        
                        with col_dl1:
                            # HTML Download
                            timestamp = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y%m%d_%H%M")
                            html_filename = f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html"
                            
                            st.download_button(
                                label="💾 Download HTML",
                                data=prescription_html.encode('utf-8'),
                                file_name=html_filename,
                                mime="text/html",
                                use_container_width=True
                            )
                        
                        with col_dl2:
                            # Simple text version
                            text_prescription = f"""MauEyeCare Prescription

Patient: {patient_name}
Date: {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y')}

Prescribed Items:
{'-'*30}
"""
                            
                            if selected_spectacles:
                                text_prescription += "\nSpectacles:\n"
                                for spec_name in selected_spectacles:
                                    text_prescription += f"- {spec_name}\n"
                            
                            if medicine_details:
                                text_prescription += "\nMedicines:\n"
                                for med_name, details in medicine_details.items():
                                    text_prescription += f"- {med_name} (Qty: {details['quantity']})\n"
                            
                            text_prescription += f"\nDr. Danish\nMauEyeCare Optical Center"
                            
                            st.download_button(
                                label="📝 Download Text",
                                data=text_prescription.encode('utf-8'),
                                file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        

                        
                        # Patient Communication
                        patient_mobile = st.session_state.get('patient_mobile')
                        if patient_mobile:
                            st.markdown("---")
                            st.markdown("### 📱 Share Prescription")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("📱 Send WhatsApp", type="primary"):
                                    from modules.whatsapp_utils import send_prescription_link
                                    result_wa = send_prescription_link(patient_name, patient_mobile, result['link'])
                                    
                                    if result_wa['api_result']['success']:
                                        st.success("✅ WhatsApp message prepared!")
                                        st.info("📱 Demo mode - message ready to send")
                                    
                                    st.markdown(f"**[🌐 Send via WhatsApp Web]({result_wa['web_url']})**")
                            
                            with col2:
                                st.text_input("📋 Copy link to share:", value=result['link'])
                        else:
                            st.markdown("### 🔗 Prescription Link")
                            st.text_input("Share this link:", value=result['link'])
                        
                        # Inventory updates are handled automatically in prescription generation
                        
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
                            timestamp = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y%m%d_%H%M")
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
Date: {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%m/%Y')}

Prescribed Items:
{'-'*30}
"""
                            
                            COMPREHENSIVE_SPECTACLE_DATABASE = get_spectacle_database()
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
        
        st.markdown("---")
        
        # Setup Instructions
        st.subheader("📖 Setup Instructions")
        
        with st.expander("🚀 Quick Setup Guide", expanded=False):
            st.markdown("""
            **Step 1: Create Google Sheet**
            1. Go to [Google Sheets](https://sheets.google.com)
            2. Create a new spreadsheet
            3. Name it "MauEyeCare Hospital Data"
            
            **Step 2: Create Required Tabs**
            1. Create 5 separate tabs: Medicines, Spectacles, Patients, Prescriptions, Analytics
            2. Right-click on sheet tab at bottom and select "Insert sheet"
            3. Download templates above and copy data to respective tabs
            4. Make sure column headers match exactly
            
            **Step 3: Make Spreadsheet Public**
            1. Click "Share" button in Google Sheets
            2. Change access to "Anyone with the link can view"
            3. Copy the spreadsheet ID from URL
            
            **Step 4: Update Application**
            1. Paste sheet ID in the "Update Sheet ID" field above
            2. Click "Update Sheet ID"
            3. Test connection to verify
            
            **Spreadsheet ID Location:**
            From URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
            
            **Tab Structure:**
            - Each tab should be named exactly: Medicines, Spectacles, Patients, Prescriptions, Analytics
            - Tab names are case-sensitive
            - Use templates provided above for each tab
            """)
        
        # Data Management
        st.subheader("📊 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📤 Export Data**")
            
            # Export pending patients
            pending_patients = st.session_state.get('pending_patients', [])
            if pending_patients:
                df_patients = pd.DataFrame(pending_patients)
                csv_patients = df_patients.to_csv(index=False)
                st.download_button(
                    f"📥 Export {len(pending_patients)} New Patients",
                    csv_patients,
                    f"new_patients_for_google_sheets_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    help="Download and manually add to Google Sheets Patients tab"
                )
                st.success(f"📊 {len(pending_patients)} patients ready for Google Sheets")
                
                # Instructions for manual upload
                with st.expander("📖 How to add to Google Sheets"):
                    st.markdown("""
                    **Steps to sync patients:**
                    1. Download the CSV file above
                    2. Open your Google Sheet
                    3. Go to the "Patients" tab
                    4. Copy and paste the data (skip headers if already present)
                    5. Save the sheet
                    6. Come back and click "Clear Synced Data" below
                    """)
                
                if st.button("🗑️ Clear Synced Data", help="Clear after manually adding to Google Sheets"):
                    st.session_state['pending_patients'] = []
                    st.success("✅ Pending patients cleared!")
                    st.rerun()
            else:
                st.info("📊 No new patients to sync")
                st.caption("Register patients to see them here")
            
            # Export analytics
            visit_data = st.session_state.get('visit_analytics', [])
            if visit_data:
                df_analytics = pd.DataFrame(visit_data)
                csv_analytics = df_analytics.to_csv(index=False)
                st.download_button(
                    f"📥 Export {len(visit_data)} Visits",
                    csv_analytics,
                    f"visit_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.info("No analytics data")
        
        with col2:
            st.markdown("**🔄 Sync Status**")
            
            # Show sync statistics
            try:
                medicines, spectacles, patients = get_sheet_data()
                st.metric("💊 Google Sheets Medicines", len(medicines))
                st.metric("👓 Google Sheets Spectacles", len(spectacles))
                st.metric("👥 Google Sheets Patients", len(patients))
                
                # Show pending data
                pending_patients = len(st.session_state.get('pending_patients', []))
                pending_analytics = len(st.session_state.get('visit_analytics', []))
                
                if pending_patients > 0:
                    st.warning(f"⚠️ {pending_patients} patients pending sync")
                if pending_analytics > 0:
                    st.info(f"📈 {pending_analytics} analytics records")
                    
            except Exception as e:
                st.error("Connection failed")
                st.caption(f"Error: {str(e)[:30]}...")
                
                # Show local data when Google Sheets fails
                pending_patients = len(st.session_state.get('pending_patients', []))
                st.metric("💾 Local Patients", pending_patients)
        
        with col3:
            st.markdown("**⚙️ Advanced Options**")
            
            if st.button("🗑️ Clear Cache"):
                get_sheet_data.clear()
                st.success("✅ Cache cleared")
            
            if st.button("🔄 Reset Session"):
                for key in ['pending_patients', 'visit_analytics', 'selected_spectacles', 'selected_medicines']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Session reset")
        
        st.markdown("---")
        
        # Troubleshooting
        st.subheader("🔧 Troubleshooting")
        
        with st.expander("❓ Common Issues & Solutions"):
            st.markdown("""
            **Issue: "Connection Failed"**
            - Check if Google Sheet is publicly accessible
            - Verify Sheet ID is correct
            - Ensure spreadsheet has required tabs (Medicines, Spectacles, Patients, Prescriptions, Analytics)
            
            **Issue: "No Data Found"**
            - Check if tabs have data in correct format
            - Verify column headers match template exactly
            - Ensure each tab is named correctly (Medicines, Spectacles, etc.)
            - Make sure data starts from row 2 (row 1 should be headers)
            
            **Issue: "Sync Problems"**
            - This app only reads from Google Sheets (no automatic writing)
            - Use Export Data section to download CSV files
            - Manually copy data to your Google Sheets
            - This ensures data security and prevents accidental overwrites
            
            **Issue: "Template Not Working"**
            - Download fresh templates from above
            - Copy data exactly as shown
            - Don't modify column names or order
            """)
        
        # Professional Support
        st.markdown("---")
        st.subheader("🏥 Professional Support")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📞 Technical Support:**")
            st.info("📧 Email: tech@maueyecare.com")
            st.info("📱 Phone: +91 92356-47410")
            st.info("🕘 Hours: Mon-Sat 9AM-8PM")
        
        with col2:
            st.markdown("**🏥 Eye Care Consultation:**")
            st.info("👨‍⚕️ Dr. Danish - Eye Specialist")
            st.info("📍 Azamgarh, Uttar Pradesh")
            st.info("🩺 Registration: UPS 2908")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔗 Open Google Sheets", use_container_width=True):
                sheet_url = f"https://docs.google.com/spreadsheets/d/{current_sheet_id}/edit"
                st.markdown(f"**[📊 Open Sheet]({sheet_url})**")
        
        with col2:
            if st.button("📋 Copy Sheet ID", use_container_width=True):
                st.code(current_sheet_id)
                st.success("Sheet ID ready to copy!")
        
        with col3:
            if st.button("📖 View Documentation", use_container_width=True):
                st.info("📚 Check README.md for detailed setup guide")
        
        with col4:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                st.info("🏥 Use sidebar to navigate to other sections")
        
        with tab_presc:
            st.markdown("**Prescriptions Tab Template:**")
            st.info("📄 Create a tab named 'Prescriptions' with this data")
            prescription_template = pd.DataFrame({
                'id': [1, 2, 3],
                'patient_id': [1, 2, 3],
                'patient_name': ['John Doe', 'Jane Smith', 'Raj Kumar'],
                'prescription_date': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'spectacles': ['Ray-Ban Aviator', '', 'Titan Rimless'],
                'medicines': ['Refresh Tears', 'Tobramycin Drops', 'Prednisolone'],
                'od_sphere': ['-1.25', '+0.75', '-2.00'],
                'od_cylinder': ['-0.50', '', '-0.25'],
                'od_axis': ['90', '', '180'],
                'os_sphere': ['-1.50', '+0.50', '-1.75'],
                'os_cylinder': ['-0.25', '', ''],
                'os_axis': ['85', '', ''],
                'total_cost': [8500, 200, 4200]
            })
            
            st.dataframe(prescription_template, use_container_width=True)
            
            csv_presc = prescription_template.to_csv(index=False)
            st.download_button(
                "📥 Download Prescriptions Tab Template",
                csv_presc,
                "prescriptions_tab_template.csv",
                "text/csv",
                use_container_width=True
            )
        
        with tab_anal:
            st.markdown("**Analytics Tab Template:**")
            st.info("📈 Create a tab named 'Analytics' with this data")
            analytics_template = pd.DataFrame({
                'date': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'total_patients': [5, 8, 12],
                'new_patients': [3, 5, 7],
                'return_patients': [2, 3, 5],
                'revenue': [15000, 22000, 18000],
                'common_issue': ['Blurry Vision', 'Eye Pain', 'Dry Eyes'],
                'avg_age': [35, 42, 38],
                'referral_source': ['Online', 'Doctor', 'Family'],
                'screen_time_high': [3, 4, 6],
                'diabetes_patients': [1, 2, 2],
                'family_history_cases': [2, 3, 4]
            })
            
            st.dataframe(analytics_template, use_container_width=True)
            
            csv_anal = analytics_template.to_csv(index=False)
            st.download_button(
                "📥 Download Analytics Tab Template",
                csv_anal,
                "analytics_tab_template.csv",
                "text/csv",
                use_container_width=True
            )

        st.header("📦 Inventory Management")
        
        try:
            from modules.separate_inventory import load_medicine_inventory, load_spectacle_inventory
            med_inventory = load_medicine_inventory()
            spec_inventory = load_spectacle_inventory()
            
            # Combine inventories with proper stock extraction
            inventory = {}
            for name, data in med_inventory.items():
                inventory[name] = data.get('quantity', 0) if isinstance(data, dict) else data
            for name, data in spec_inventory.items():
                inventory[name] = data.get('quantity', 0) if isinstance(data, dict) else data
            
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
                # Manual Update with separate inventories
                st.markdown("**✏️ Manual Update**")
                item_type = st.radio("Item Type:", ["Medicine", "Spectacle"], key="item_type_manual")
                item_name = st.text_input("Item Name", placeholder="Enter item name")
                quantity = st.number_input("Quantity", min_value=0, value=1)
                
                if item_type == "Medicine":
                    price = st.number_input("Price (₹)", min_value=0, value=100)
                    category = st.selectbox("Category", ["Antibiotic", "Steroid", "Lubricant", "Antihistamine", "NSAID", "Vitamin", "Supplement", "Other"])
                    med_type = st.selectbox("Type", ["Eye Drops", "Tablet", "Capsule", "Ointment", "Gel", "Syrup", "Injection"])
                else:
                    price = st.number_input("Price (₹)", min_value=0, value=5000)
                    brand = st.text_input("Brand", value="Generic")
                    model = st.text_input("Model", value="Standard")
                    frame_type = st.selectbox("Frame Type", ["Full Rim", "Half Rim", "Rimless", "Cat Eye", "Aviator", "Round", "Square"])
                    material = st.selectbox("Material", ["Plastic", "Metal", "Titanium", "Acetate", "TR90", "Stainless Steel"])
                    color = st.selectbox("Color", ["Black", "Brown", "Silver", "Gold", "Blue", "Red", "Clear", "Tortoise"])
                    size = st.selectbox("Size", ["Small", "Medium", "Large", "XL"])
                    image_url = st.text_input("Image URL (Optional)", placeholder="https://example.com/image.jpg")
                
                if st.button("💾 Update Stock"):
                    if item_name:
                        from modules.separate_inventory import add_medicine_inventory, add_spectacle_inventory
                        if item_type == "Medicine":
                            add_medicine_inventory(item_name, quantity, price, category, med_type)
                            st.success(f"✅ Updated medicine: {item_name} = {quantity} units (₹{price}, {category}, {med_type})")
                        else:
                            add_spectacle_inventory(item_name, quantity, price, brand, model, frame_type, material, color, size, image_url)
                            st.success(f"✅ Updated spectacle: {item_name} = {quantity} units (₹{price}, {brand} {model})")
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
                            
                            # Expected columns: Item, Stock (Price, Category, Type optional)
                            if 'Item' in df.columns and 'Stock' in df.columns:
                                imported_count = 0
                                for _, row in df.iterrows():
                                    item = str(row['Item']).strip()
                                    stock = int(row['Stock']) if pd.notna(row['Stock']) else 0
                                    price = int(row.get('Price', 100)) if pd.notna(row.get('Price')) else 100
                                    category = str(row.get('Category', 'General')).strip() if pd.notna(row.get('Category')) else 'General'
                                    item_type = str(row.get('Type', 'Item')).strip() if pd.notna(row.get('Type')) else 'Item'
                                    
                                    # Determine if it's a medicine based on keywords or category
                                    medicine_keywords = ['drop', 'tablet', 'capsule', 'ointment', 'gel', 'syrup', 'injection']
                                    is_medicine = (any(keyword in item.lower() for keyword in medicine_keywords) or 
                                                 category.lower() in ['antibiotic', 'steroid', 'lubricant', 'antihistamine', 'nsaid', 'vitamin', 'supplement'])
                                    
                                    if is_medicine:
                                        from modules.separate_inventory import add_medicine_inventory
                                        add_medicine_inventory(item, stock, price, category, item_type)
                                    else:
                                        from modules.separate_inventory import add_spectacle_inventory
                                        brand = str(row.get('Brand', 'Generic')).strip() if pd.notna(row.get('Brand')) else 'Generic'
                                        model = str(row.get('Model', 'Standard')).strip() if pd.notna(row.get('Model')) else 'Standard'
                                        frame_type = str(row.get('Frame_Type', 'Full Rim')).strip() if pd.notna(row.get('Frame_Type')) else 'Full Rim'
                                        material = str(row.get('Material', 'Plastic')).strip() if pd.notna(row.get('Material')) else 'Plastic'
                                        color = str(row.get('Color', 'Black')).strip() if pd.notna(row.get('Color')) else 'Black'
                                        size = str(row.get('Size', 'Medium')).strip() if pd.notna(row.get('Size')) else 'Medium'
                                        image_url = str(row.get('Image_URL', '')).strip() if pd.notna(row.get('Image_URL')) else ''
                                        add_spectacle_inventory(item, stock, price, brand, model, frame_type, material, color, size, image_url)
                                    
                                    imported_count += 1
                                
                                st.success(f"✅ {imported_count} items imported successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Excel must have 'Item' and 'Stock' columns (Price, Category, Type are optional)")
                        except Exception as e:
                            st.error(f"❌ Import failed: {str(e)}")
                
                # Sample format with enhanced fields
                sample_data = pd.DataFrame({
                    'Item': ['Ray-Ban Aviator', 'Refresh Tears Eye Drops', 'Oakley Holbrook'],
                    'Stock': [15, 25, 10],
                    'Price': [5000, 150, 8000],
                    'Brand': ['Ray-Ban', 'Refresh', 'Oakley'],
                    'Model': ['Aviator Classic', 'Eye Drops', 'Holbrook'],
                    'Frame_Type': ['Aviator', 'N/A', 'Square'],
                    'Material': ['Metal', 'N/A', 'Plastic'],
                    'Color': ['Gold', 'Clear', 'Black'],
                    'Size': ['Medium', 'N/A', 'Large'],
                    'QR_Code': ['SP0001', 'MD0001', 'SP0002'],
                    'Image_URL': ['https://example.com/rayban.jpg', '', 'https://example.com/oakley.jpg'],
                    'Category': ['Spectacle', 'Medicine', 'Spectacle'],
                    'Type': ['Sunglasses', 'Eye Drops', 'Sunglasses']
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
                    # Create enhanced dataframe with medicine details
                    from modules.separate_inventory import load_medicine_inventory, load_spectacle_inventory
                    med_inventory = load_medicine_inventory()
                    spec_inventory = load_spectacle_inventory()
                    
                    export_data = []
                    
                    # Process medicine inventory
                    for item, data in med_inventory.items():
                        if isinstance(data, dict):
                            stock = data.get('quantity', 0)
                            row = {
                                "Item": item, 
                                "Stock": stock, 
                                "Price": data.get('price', 100),
                                "Category": data.get('category', 'Medicine'),
                                "Type": data.get('type', 'Medicine'),
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        else:
                            stock = data if isinstance(data, int) else 0
                            row = {
                                "Item": item, 
                                "Stock": stock, 
                                "Price": 100,
                                "Category": "Medicine",
                                "Type": "Medicine",
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        export_data.append(row)
                    
                    # Process spectacle inventory
                    for item, stock in spec_inventory.items():
                        row = {
                            "Item": item, 
                            "Stock": stock, 
                            "Price": 5000,
                            "Category": "Spectacle",
                            "Type": "Eyewear",
                            "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                        }
                        export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                    
                    # Excel export with proper buffer handling
                    try:
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Inventory', index=False)
                        output.seek(0)
                        
                        timestamp = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')
                        st.download_button(
                            "📤 Download Excel",
                            data=output.getvalue(),
                            file_name=f"inventory_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Excel export failed: {str(e)}")
                        # Fallback to CSV
                        csv = df.to_csv(index=False)
                        timestamp = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')
                        st.download_button(
                            "📤 Download CSV (Fallback)",
                            csv,
                            f"inventory_{timestamp}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                
                # CSV Export (always works)
                if inventory:
                    # Create enhanced dataframe with medicine details
                    from modules.separate_inventory import load_medicine_inventory, load_spectacle_inventory
                    med_inventory = load_medicine_inventory()
                    spec_inventory = load_spectacle_inventory()
                    
                    export_data = []
                    
                    # Process medicine inventory
                    for item, data in med_inventory.items():
                        if isinstance(data, dict):
                            stock = data.get('quantity', 0)
                            row = {
                                "Item": item, 
                                "Stock": stock, 
                                "Price": data.get('price', 100),
                                "Category": data.get('category', 'Medicine'),
                                "Type": data.get('type', 'Medicine'),
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        else:
                            stock = data if isinstance(data, int) else 0
                            row = {
                                "Item": item, 
                                "Stock": stock, 
                                "Price": 100,
                                "Category": "Medicine",
                                "Type": "Medicine",
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        export_data.append(row)
                    
                    # Process spectacle inventory with detailed fields
                    for item, data in spec_inventory.items():
                        if isinstance(data, dict):
                            stock = data.get('quantity', 0)
                            row = {
                                "Item": item,
                                "Stock": stock,
                                "Price": data.get('price', 5000),
                                "Brand": data.get('brand', 'Generic'),
                                "Model": data.get('model', 'Standard'),
                                "Frame_Type": data.get('frame_type', 'Full Rim'),
                                "Material": data.get('material', 'Plastic'),
                                "Color": data.get('color', 'Black'),
                                "Size": data.get('size', 'Medium'),
                                "QR_Code": data.get('qr_code', 'N/A'),
                                "Image_URL": data.get('image_url', ''),
                                "Category": "Spectacle",
                                "Type": "Eyewear",
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        else:
                            stock = data if isinstance(data, int) else 0
                            row = {
                                "Item": item,
                                "Stock": stock,
                                "Price": 5000,
                                "Brand": "Generic",
                                "Model": "Standard",
                                "Frame_Type": "Full Rim",
                                "Material": "Plastic",
                                "Color": "Black",
                                "Size": "Medium",
                                "QR_Code": "N/A",
                                "Image_URL": "",
                                "Category": "Spectacle",
                                "Type": "Eyewear",
                                "Status": "OUT" if stock == 0 else "LOW" if stock < 5 else "OK"
                            }
                        export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    timestamp = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')
                    st.download_button(
                        "📤 Download CSV",
                        data=csv,
                        file_name=f"inventory_{timestamp}.csv",
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
                
                # Import inventory functions
                from modules.separate_inventory import load_medicine_inventory, load_spectacle_inventory
                
                # Display items with enhanced information
                med_inventory = load_medicine_inventory()
                spec_inventory = load_spectacle_inventory()
                
                for item, stock in list(filtered_items)[:30]:  # Show up to 30 items
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        # Show item details if available
                        if item in med_inventory and isinstance(med_inventory[item], dict):
                            med_data = med_inventory[item]
                            st.write(f"**{item}**")
                            st.caption(f"{med_data.get('type', 'Medicine')} | ₹{med_data.get('price', 100)} | {med_data.get('category', 'General')}")
                        elif item in spec_inventory and isinstance(spec_inventory[item], dict):
                            spec_data = spec_inventory[item]
                            st.write(f"**{item}**")
                            st.caption(f"{spec_data.get('brand', 'Generic')} {spec_data.get('model', 'Standard')} | ₹{spec_data.get('price', 5000)} | {spec_data.get('qr_code', 'N/A')}")
                        else:
                            st.write(item)
                    
                    with col2:
                        if stock == 0:
                            st.error(f"OUT: {stock}")
                        elif stock < 5:
                            st.warning(f"LOW: {stock}")
                        else:
                            st.success(f"OK: {stock}")
                    
                    with col3:
                        # Show price if available
                        if item in med_inventory and isinstance(med_inventory[item], dict):
                            price = med_inventory[item].get('price', 100)
                            st.caption(f"₹{price}")
                        elif item in spec_inventory and isinstance(spec_inventory[item], dict):
                            price = spec_inventory[item].get('price', 5000)
                            st.caption(f"₹{price}")
                        else:
                            st.caption('₹100')
                    
                    with col4:
                        # Quick update buttons
                        if st.button("➕", key=f"add_{item}", help="Add 1"):
                            if item in med_inventory:
                                from modules.separate_inventory import add_medicine_inventory
                                if isinstance(med_inventory[item], dict):
                                    med_data = med_inventory[item]
                                    add_medicine_inventory(item, stock + 1, med_data.get('price', 100), med_data.get('category', 'Medicine'), med_data.get('type', 'Tablet'))
                                else:
                                    add_medicine_inventory(item, stock + 1)
                            elif item in spec_inventory:
                                from modules.separate_inventory import add_spectacle_inventory
                                if isinstance(spec_inventory[item], dict):
                                    spec_data = spec_inventory[item]
                                    add_spectacle_inventory(item, stock + 1, spec_data.get('price', 5000), spec_data.get('brand', 'Generic'), spec_data.get('model', 'Standard'), spec_data.get('frame_type', 'Full Rim'), spec_data.get('material', 'Plastic'), spec_data.get('color', 'Black'), spec_data.get('size', 'Medium'), spec_data.get('image_url', ''))
                                else:
                                    add_spectacle_inventory(item, stock + 1)
                            st.rerun()
            else:
                st.info("📦 No inventory items. Click 'Load Complete Database' in sidebar or import Excel file.")
                
        except Exception as e:
            st.error("😱 Inventory system not available")
            st.info("Please load the database first using the sidebar button.")
    

        st.header("📊 Google Sheets Integration")
        
        sheets_manager.show_sheet_instructions()
        
        st.markdown("---")
        
        # Pending data sync
        st.subheader("🔄 Data Sync Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pending_patients = len(st.session_state.get('pending_patients', []))
            st.metric("Pending Patients", pending_patients)
            if pending_patients > 0:
                if st.button("📤 Export Patients CSV"):
                    df = pd.DataFrame(st.session_state['pending_patients'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Patients CSV",
                        csv,
                        "patients_export.csv",
                        "text/csv"
                    )
        
        with col2:
            pending_prescriptions = len(st.session_state.get('pending_prescriptions', []))
            st.metric("Pending Prescriptions", pending_prescriptions)
            if pending_prescriptions > 0:
                if st.button("📤 Export Prescriptions CSV"):
                    df = pd.DataFrame(st.session_state['pending_prescriptions'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Prescriptions CSV",
                        csv,
                        "prescriptions_export.csv",
                        "text/csv"
                    )
        
        with col3:
            custom_medicines = len(st.session_state.get('custom_medicines', []))
            st.metric("Custom Medicines", custom_medicines)
            if custom_medicines > 0:
                if st.button("📤 Export Medicines CSV"):
                    df = pd.DataFrame(st.session_state['custom_medicines'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Medicines CSV",
                        csv,
                        "medicines_export.csv",
                        "text/csv"
                    )
        
        st.markdown("---")
        
        # Image upload for spectacles
        st.subheader("🖼️ Spectacle Image Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Upload Spectacle Image**")
            spectacle_name = st.text_input("Spectacle Name", placeholder="Enter spectacle name")
            uploaded_image = image_manager.image_uploader_widget("spectacle_image", "Upload Spectacle Image")
            
            if uploaded_image and spectacle_name:
                if st.button("Save Spectacle Image"):
                    image_path = image_manager.upload_image(uploaded_image, "spectacle")
                    if image_path:
                        st.success(f"Image saved: {image_path}")
                        st.info("Add this path to your Google Sheets spectacle data")
        
        with col2:
            st.markdown("**Image Storage Info**")
            st.info("💾 Images are stored locally in 'uploaded_images' folder")
            st.info("🔗 Add image paths to Google Sheets for display")
            st.info("📊 Use relative paths like 'uploaded_images/spectacle_20241201_143022_image.jpg'")
        

        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💾 Patient Data Backup**")
            
            try:
                patients = sheets_manager.get_patients()
                # Convert to list format for compatibility
                if patients and isinstance(patients[0], dict):
                    patients = [[p.get('id', i), p.get('name', ''), p.get('age', 0), p.get('gender', ''), p.get('mobile', ''), p.get('registration_date', '')] for i, p in enumerate(patients)]
            except:
                patients = []
            
            if patients:
                # Create backup data
                backup_data = {
                    'backup_date': datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
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
                    f"patient_backup_{datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.json",
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
                                try:
                                    current_patients = sheets_manager.get_patients()
                                    for p in current_patients:
                                        if isinstance(p, dict):
                                            if p.get('name') == patient['name'] and p.get('mobile') == patient['mobile']:
                                                existing = True
                                                break
                                        else:
                                            if p[1] == patient['name'] and p[4] == patient['mobile']:
                                                existing = True
                                                break
                                except:
                                    current_patients = []
                                
                                if not existing or restore_mode == "Replace all":
                                    # Add to pending patients for Google Sheets sync
                                    if 'pending_patients' not in st.session_state:
                                        st.session_state['pending_patients'] = []
                                    st.session_state['pending_patients'].append({
                                        'name': patient['name'],
                                        'age': patient['age'],
                                        'gender': patient['gender'],
                                        'mobile': patient['mobile'],
                                        'registration_date': patient.get('registration_date', datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat())
                                    })
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
    
    # --- Data Sync Tab ---
    with tab7:
        st.header("🔄 Data Synchronization")
        st.markdown("*Manage data sync between local storage and Google Sheets*")
        
        # Show sync dashboard
        sync_manager.show_sync_dashboard()
        
        st.markdown("---")
        
        # Manual data export/import
        st.subheader("📤 Manual Data Export/Import")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📤 Export for Google Sheets**")
            
            # Export pending patients
            pending_patients = st.session_state.get('pending_patients', [])
            if pending_patients:
                import pandas as pd
                df_patients = pd.DataFrame(pending_patients)
                csv_patients = df_patients.to_csv(index=False)
                
                st.download_button(
                    f"📥 Export {len(pending_patients)} Patients",
                    csv_patients,
                    f"patients_for_google_sheets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    help="Download and manually add to Google Sheets Patients tab",
                    use_container_width=True
                )
                
                st.info(f"📊 {len(pending_patients)} patients ready for manual upload")
                
                # Clear after export
                if st.button("🗑️ Clear After Manual Upload"):
                    st.session_state['pending_patients'] = []
                    st.success("✅ Pending patients cleared!")
                    st.rerun()
            else:
                st.info("📊 No pending patients to export")
            
            # Export complete data
            if st.button("📦 Export Complete Data", use_container_width=True):
                excel_data = local_data_manager.export_complete_excel()
                if excel_data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                    st.download_button(
                        "📥 Download Complete Hospital Data",
                        data=excel_data,
                        file_name=f"maueyecare_complete_data_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ Complete data export ready!")
        
        with col2:
            st.markdown("**📥 Import from Google Sheets**")
            
            uploaded_file = st.file_uploader(
                "Upload CSV from Google Sheets",
                type=['csv'],
                help="Export data from Google Sheets and upload here"
            )
            
            if uploaded_file:
                import_type = st.selectbox(
                    "Data Type:",
                    ["Patients", "Medicines", "Spectacles", "Prescriptions", "Analytics"]
                )
                
                if st.button("📤 Import Data", type="primary"):
                    try:
                        import pandas as pd
                        df = pd.read_csv(uploaded_file)
                        
                        if import_type == "Patients":
                            # Import patients
                            imported_count = 0
                            for _, row in df.iterrows():
                                patient_data = {
                                    'id': row.get('id', ''),
                                    'name': row.get('name', ''),
                                    'age': row.get('age', 0),
                                    'gender': row.get('gender', ''),
                                    'mobile': row.get('mobile', ''),
                                    'email': row.get('email', ''),
                                    'address': row.get('address', ''),
                                    'city': row.get('city', ''),
                                    'state': row.get('state', ''),
                                    'pincode': row.get('pincode', ''),
                                    'registration_date': row.get('registration_date', ''),
                                    'issue': row.get('issue', ''),
                                    'advice': row.get('advice', '')
                                }
                                
                                # Add to pending patients
                                if 'pending_patients' not in st.session_state:
                                    st.session_state['pending_patients'] = []
                                st.session_state['pending_patients'].append(patient_data)
                                imported_count += 1
                            
                            st.success(f"✅ Imported {imported_count} patients successfully!")
                        
                        elif import_type == "Medicines":
                            # Import medicines to local database
                            imported_count = 0
                            medicines = local_data_manager.get_medicines()
                            
                            for _, row in df.iterrows():
                                med_name = row.get('name', '')
                                if med_name:
                                    medicines[med_name] = {
                                        'category': row.get('category', 'General'),
                                        'type': row.get('type', 'Medicine'),
                                        'price': row.get('price', 100),
                                        'quantity': row.get('quantity', 0),
                                        'prescription_required': row.get('prescription_required', True),
                                        'indication': row.get('indication', 'As prescribed'),
                                        'dosage': row.get('dosage', 'As prescribed'),
                                        'source': 'imported',
                                        'last_updated': datetime.now().isoformat()
                                    }
                                    imported_count += 1
                            
                            local_data_manager.save_json_data('medicines.json', medicines)
                            st.success(f"✅ Imported {imported_count} medicines successfully!")
                        
                        else:
                            st.info(f"📊 Import for {import_type} coming soon!")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Import failed: {str(e)}")
        
        st.markdown("---")
        
        # Sync troubleshooting
        st.subheader("🔧 Sync Troubleshooting")
        
        with st.expander("🔍 Common Sync Issues & Solutions"):
            st.markdown("""
            **Issue: "Connection Failed"**
            - Check internet connection
            - Verify Google Sheets API key is valid
            - Ensure Google Sheet is publicly accessible
            - Check if Sheet ID is correct
            
            **Issue: "Sync Partially Failed"**
            - Some data may have synced successfully
            - Check Google Sheets for partial data
            - Retry sync for remaining items
            - Use manual export/import as backup
            
            **Issue: "Data Not Appearing"**
            - Refresh the Google Sheet
            - Check if data was added to correct tab
            - Verify column headers match template
            - Clear cache and re-sync
            
            **Issue: "Duplicate Data"**
            - System prevents duplicate patients by name+mobile
            - Check for slight variations in names
            - Use manual cleanup if needed
            
            **Best Practices:**
            - Sync regularly to avoid large data batches
            - Always test connection before major operations
            - Keep local backups using export feature
            - Monitor sync status in sidebar
            """)
        
        # Advanced sync options
        st.subheader("⚙️ Advanced Sync Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear All Pending Data", help="Clear all local pending data"):
                st.warning("⚠️ This will clear all unsaved local data!")
                if st.button("Confirm Clear All", type="secondary"):
                    for key in ['pending_patients', 'pending_prescriptions', 'visit_analytics']:
                        if key in st.session_state:
                            st.session_state[key] = []
                    st.success("✅ All pending data cleared!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Reset Sync Status", help="Reset sync timestamps and status"):
                local_data_manager.save_json_data('last_sync.json', {})
                st.success("✅ Sync status reset!")
                st.rerun()
        
        with col3:
            if st.button("📊 Force Refresh Cache", help="Clear all cached data"):
                get_sheet_data.clear()
                st.success("✅ Cache cleared!")
                st.rerun()
    

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