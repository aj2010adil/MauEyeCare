#!/usr/bin/env python3
"""
MauEyeCare - Streamlined Professional Eye Care Hospital Management System
"""

import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime, timezone, timedelta
import json

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Core imports
from modules.google_sheets_manager import sheets_manager
from modules.oauth_sheets_api import oauth_sheets_api

@st.cache_data
def get_sheet_data():
    """Load data from Google Sheets"""
    try:
        medicines = sheets_manager.get_medicines()
        spectacles = sheets_manager.get_spectacles()
        patients = sheets_manager.get_patients()
        return medicines, spectacles, patients
    except Exception as e:
        return [], [], []

def main():
    st.set_page_config(
        page_title="MauEyeCare", 
        page_icon="👁️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 MauEyeCare - Professional Eye Care Hospital")
    st.markdown("*Streamlined Hospital Management System*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Sync Google Sheets"):
            with st.spinner("Syncing with Google Sheets..."):
                get_sheet_data.clear()
                medicines, spectacles, patients = get_sheet_data()
                st.success(f"✅ Synced: {len(medicines)} medicines, {len(spectacles)} spectacles, {len(patients)} patients!")
        
        # OAuth status
        if oauth_sheets_api.is_authenticated():
            st.success("✅ Google Sheets Connected")
        else:
            st.error("❌ Google Sheets Not Connected")
            auth_url = oauth_sheets_api.get_auth_url()
            st.markdown(f"[🔗 Connect to Google Sheets]({auth_url})")
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Mobile: {st.session_state.get('patient_mobile', 'N/A')}")

    # Handle OAuth callback
    query_params = st.query_params
    if 'code' in query_params:
        code = query_params['code']
        state = query_params.get('state', '')
        
        with st.spinner("Authenticating with Google Sheets..."):
            result = oauth_sheets_api.exchange_code_for_token(code, state)
            if result['success']:
                st.success("✅ Google Sheets authentication successful!")
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"❌ Authentication failed: {result.get('error', 'Unknown error')}")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "👥 Patient Registration", 
        "📤 Prescription Generator",
        "📊 Analytics"
    ])

    # --- Patient Registration Tab ---
    with tab1:
        st.header("👥 Patient Registration")
        
        # Get existing patients for suggestions
        try:
            existing_patients = sheets_manager.get_patients()
            patient_names = [p.get('name', '') for p in existing_patients if isinstance(p, dict) and p.get('name')]
            patient_mobiles = [p.get('mobile', '') for p in existing_patients if isinstance(p, dict) and p.get('mobile')]
        except:
            patient_names = []
            patient_mobiles = []
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Combined dropdown + custom input for name
                name_options = ["-- Enter Custom Name --"] + patient_names[:15]
                selected_name = st.selectbox("Patient Name", name_options, key="name_dropdown")
                
                if selected_name == "-- Enter Custom Name --":
                    patient_name = st.text_input("Enter Full Name", placeholder="Type patient full name", key="custom_name")
                else:
                    patient_name = selected_name
                    st.info(f"Selected: {selected_name}")
                
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                
                # Address fields for demographics
                address = st.text_input("Address", placeholder="Street address")
                col_city, col_state = st.columns(2)
                with col_city:
                    city = st.text_input("City", placeholder="City name")
                with col_state:
                    state = st.selectbox("State", [
                        "", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
                        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
                        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
                        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
                        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi"
                    ])
                pincode = st.text_input("Pincode", placeholder="6-digit pincode")
            
            with col2:
                # Combined dropdown + custom input for mobile
                mobile_options = ["-- Enter Custom Mobile --"] + patient_mobiles[:15]
                selected_mobile = st.selectbox("Mobile Number", mobile_options, key="mobile_dropdown")
                
                if selected_mobile == "-- Enter Custom Mobile --":
                    contact = st.text_input("Enter Mobile Number", placeholder="Type mobile number", key="custom_mobile")
                else:
                    contact = selected_mobile
                    st.info(f"Selected: {selected_mobile}")
                
                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                
                advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Glaucoma Screening", "Diabetic Eye Exam", "Other"]
                advice = st.selectbox("Advice/Notes", advice_options)
                
                # Professional details for analytics
                occupation = st.text_input("Occupation", placeholder="Patient's occupation")
                referral_source = st.selectbox("How did you hear about us?", [
                    "", "Google Search", "Social Media", "Friend/Family", "Doctor Referral", 
                    "Advertisement", "Walk-in", "Previous Patient", "Other"
                ])
            
            submitted = st.form_submit_button("💾 Register Patient", type="primary")
            
            if submitted and patient_name:
                # Professional duplicate check based on name and mobile
                is_duplicate = False
                duplicate_patient = None
                try:
                    for p in existing_patients:
                        if isinstance(p, dict):
                            if (p.get('name', '').lower().strip() == patient_name.lower().strip() and 
                                p.get('mobile', '').strip() == contact.strip()):
                                is_duplicate = True
                                duplicate_patient = p
                                break
                except:
                    pass
                
                # Store patient info in session
                st.session_state.update({
                    'patient_name': patient_name,
                    'patient_mobile': contact,
                    'age': age,
                    'gender': gender,
                    'address': address,
                    'city': city,
                    'state': state,
                    'pincode': pincode,
                    'occupation': occupation,
                    'referral_source': referral_source,
                    'patient_issue': patient_issue,
                    'advice': advice,
                    'new_patient': not is_duplicate
                })
                
                if is_duplicate:
                    st.success(f"🔄 **Return Visit Recorded!** {patient_name}")
                else:
                    st.success(f"✅ **New Patient Registered!** {patient_name}")
                    st.balloons()
                
                # Professional Google Sheets integration
                if oauth_sheets_api.is_authenticated():
                    patient_record = {
                        'name': patient_name,
                        'age': age,
                        'gender': gender,
                        'mobile': contact,
                        'issue': patient_issue,
                        'advice': advice,
                        'email': '',
                        'address': address,
                        'city': city,
                        'state': state,
                        'pincode': pincode,
                        'occupation': occupation,
                        'referral_source': referral_source
                    }
                    result = oauth_sheets_api.add_patient(patient_record)
                    if result.get('success'):
                        if not is_duplicate:
                            st.info("✅ **New patient added to Google Sheets!**")
                        else:
                            st.info("✅ **Return visit recorded in Google Sheets!**")
                    else:
                        st.warning(f"⚠️ Google Sheets sync failed: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("⚠️ Google Sheets not connected - patient data not synced")
                
                st.rerun()
        
        # Post-registration: Medicine and Spectacle Selection
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.subheader(f"📋 Prescription for {st.session_state['patient_name']}")
            
            # Medicine Selection Section
            st.markdown("### 💊 Medicine Selection")
            
            # Load medicines from Google Sheets
            try:
                medicines, _, _ = get_sheet_data()
                medicine_options = {med['name']: med for med in medicines if isinstance(med, dict) and 'name' in med}
            except:
                medicine_options = {}
            
            if medicine_options:
                # Combined dropdown + custom medicine selection
                med_names = list(medicine_options.keys())
                med_dropdown_options = ["-- Select Medicine --"] + med_names
                
                selected_med_dropdown = st.selectbox(
                    "Select Medicine from Inventory:",
                    med_dropdown_options,
                    key="med_dropdown"
                )
                
                # Allow custom medicine entry
                custom_medicine = st.text_input(
                    "Or enter custom medicine:",
                    placeholder="Type medicine name if not in dropdown",
                    key="custom_med"
                )
                
                # Determine final medicine selection
                if selected_med_dropdown != "-- Select Medicine --":
                    final_medicine = selected_med_dropdown
                elif custom_medicine:
                    final_medicine = custom_medicine
                else:
                    final_medicine = None
                
                if final_medicine:
                    if 'selected_medicines_list' not in st.session_state:
                        st.session_state['selected_medicines_list'] = []
                    
                    if st.button(f"➕ Add {final_medicine}", key=f"add_{final_medicine}"):
                        if final_medicine not in st.session_state['selected_medicines_list']:
                            st.session_state['selected_medicines_list'].append(final_medicine)
                            st.success(f"Added {final_medicine}")
                
                # Show selected medicines with quantities
                if st.session_state.get('selected_medicines_list'):
                    st.markdown("**Selected Medicines:**")
                    medicine_details = {}
                    
                    for med_name in st.session_state['selected_medicines_list']:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                            
                            with col1:
                                st.write(f"**{med_name}**")
                            
                            with col2:
                                qty = st.number_input(
                                    "Qty",
                                    min_value=1,
                                    value=1,
                                    key=f"qty_{med_name}",
                                    label_visibility="collapsed"
                                )
                            
                            with col3:
                                if med_name in medicine_options:
                                    med_data = medicine_options[med_name]
                                    current_stock = int(med_data.get('quantity', 0))
                                    price = float(med_data.get('price', 100))
                                    
                                    if current_stock >= qty:
                                        st.success(f"Stock: {current_stock}")
                                    else:
                                        st.error(f"Low stock: {current_stock}")
                                    
                                    medicine_details[med_name] = {
                                        'quantity': qty,
                                        'price': price,
                                        'total_cost': price * qty,
                                        'current_stock': current_stock,
                                        'in_inventory': True
                                    }
                                else:
                                    st.info("Custom medicine")
                                    medicine_details[med_name] = {
                                        'quantity': qty,
                                        'price': 0,
                                        'total_cost': 0,
                                        'current_stock': 0,
                                        'in_inventory': False
                                    }
                            
                            with col4:
                                if st.button("🗑️", key=f"remove_{med_name}"):
                                    st.session_state['selected_medicines_list'].remove(med_name)
                                    st.rerun()
                    
                    st.session_state['medicine_details'] = medicine_details
                    
                    # Clear the cache to get fresh data
                    get_sheet_data.clear()
            
            # Spectacle Selection Section
            st.markdown("### 👓 Spectacle Selection")
            
            try:
                _, spectacles, _ = get_sheet_data()
                spectacle_options = {spec['name']: spec for spec in spectacles if isinstance(spec, dict) and 'name' in spec}
            except:
                spectacle_options = {}
            
            if spectacle_options:
                # Combined dropdown + custom spectacle selection
                spec_names = list(spectacle_options.keys())
                spec_dropdown_options = ["-- Select Spectacle --"] + spec_names
                
                selected_spec_dropdown = st.selectbox(
                    "Select Spectacle from Inventory:",
                    spec_dropdown_options,
                    key="spec_dropdown"
                )
                
                # Allow custom spectacle entry
                custom_spectacle = st.text_input(
                    "Or enter custom spectacle:",
                    placeholder="Type spectacle name if not in dropdown",
                    key="custom_spec"
                )
                
                # Determine final spectacle selection
                if selected_spec_dropdown != "-- Select Spectacle --":
                    final_spectacle = selected_spec_dropdown
                    if final_spectacle in spectacle_options:
                        spec_data = spectacle_options[final_spectacle]
                        st.info(f"Price: ₹{spec_data.get('price', 0)} | Stock: {spec_data.get('quantity', 0)}")
                elif custom_spectacle:
                    final_spectacle = custom_spectacle
                    st.info("Custom spectacle - Price will be determined manually")
                else:
                    final_spectacle = None
                
                if final_spectacle:
                    st.session_state['selected_spectacles'] = [final_spectacle]
            
            # Eye Prescription Section (separate from registration)
            st.markdown("### 👁️ Eye Prescription")
            
            # Standard prescription values for suggestions
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+1.75", "+2.00", "+2.25", "+2.50", "+3.00", "+3.50", "+4.00", "+5.00", "+6.00",
                            "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-1.75", "-2.00", "-2.25", "-2.50", "-3.00", "-3.50", "-4.00", "-5.00", "-6.00", "-8.00", "-10.00"]
            cylinder_options = ["", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-1.75", "-2.00", "-2.25", "-2.50", "-3.00", "-4.00", "-5.00"]
            axis_options = ["", "10", "15", "20", "30", "45", "60", "75", "90", "105", "120", "135", "150", "165", "180"]
            
            # Get last prescription for returning patient
            last_rx = {}
            if not st.session_state.get('new_patient', True):
                try:
                    prescriptions = sheets_manager.get_prescriptions()
                    patient_prescriptions = [p for p in prescriptions if p.get('patient_name') == st.session_state['patient_name']]
                    if patient_prescriptions:
                        last_prescription = patient_prescriptions[-1]
                        last_rx = json.loads(last_prescription.get('rx_table', '{}')) if last_prescription.get('rx_table') else {}
                except:
                    pass
            
            col_od, col_os = st.columns(2)
            
            with col_od:
                st.markdown("**OD (Right Eye)**")
                
                # Sphere OD with suggestions
                sphere_od_dropdown = st.selectbox("Sphere OD (Select)", sphere_options, 
                                                index=sphere_options.index(last_rx.get('OD', {}).get('Sphere', '')) if last_rx.get('OD', {}).get('Sphere', '') in sphere_options else 0,
                                                key="sphere_od_dropdown")
                sphere_od_custom = st.text_input("Or type custom Sphere OD", value="" if sphere_od_dropdown else last_rx.get('OD', {}).get('Sphere', ''), key="sphere_od_custom")
                od_sphere = sphere_od_custom if sphere_od_custom else sphere_od_dropdown
                
                # Cylinder OD with suggestions
                cylinder_od_dropdown = st.selectbox("Cylinder OD (Select)", cylinder_options,
                                                   index=cylinder_options.index(last_rx.get('OD', {}).get('Cylinder', '')) if last_rx.get('OD', {}).get('Cylinder', '') in cylinder_options else 0,
                                                   key="cylinder_od_dropdown")
                cylinder_od_custom = st.text_input("Or type custom Cylinder OD", value="" if cylinder_od_dropdown else last_rx.get('OD', {}).get('Cylinder', ''), key="cylinder_od_custom")
                od_cylinder = cylinder_od_custom if cylinder_od_custom else cylinder_od_dropdown
                
                # Axis OD with suggestions
                axis_od_dropdown = st.selectbox("Axis OD (Select)", axis_options,
                                               index=axis_options.index(last_rx.get('OD', {}).get('Axis', '')) if last_rx.get('OD', {}).get('Axis', '') in axis_options else 0,
                                               key="axis_od_dropdown")
                axis_od_custom = st.text_input("Or type custom Axis OD", value="" if axis_od_dropdown else last_rx.get('OD', {}).get('Axis', ''), key="axis_od_custom")
                od_axis = axis_od_custom if axis_od_custom else axis_od_dropdown
            
            with col_os:
                st.markdown("**OS (Left Eye)**")
                
                # Sphere OS with suggestions
                sphere_os_dropdown = st.selectbox("Sphere OS (Select)", sphere_options,
                                                 index=sphere_options.index(last_rx.get('OS', {}).get('Sphere', '')) if last_rx.get('OS', {}).get('Sphere', '') in sphere_options else 0,
                                                 key="sphere_os_dropdown")
                sphere_os_custom = st.text_input("Or type custom Sphere OS", value="" if sphere_os_dropdown else last_rx.get('OS', {}).get('Sphere', ''), key="sphere_os_custom")
                os_sphere = sphere_os_custom if sphere_os_custom else sphere_os_dropdown
                
                # Cylinder OS with suggestions
                cylinder_os_dropdown = st.selectbox("Cylinder OS (Select)", cylinder_options,
                                                   index=cylinder_options.index(last_rx.get('OS', {}).get('Cylinder', '')) if last_rx.get('OS', {}).get('Cylinder', '') in cylinder_options else 0,
                                                   key="cylinder_os_dropdown")
                cylinder_os_custom = st.text_input("Or type custom Cylinder OS", value="" if cylinder_os_dropdown else last_rx.get('OS', {}).get('Cylinder', ''), key="cylinder_os_custom")
                os_cylinder = cylinder_os_custom if cylinder_os_custom else cylinder_os_dropdown
                
                # Axis OS with suggestions
                axis_os_dropdown = st.selectbox("Axis OS (Select)", axis_options,
                                               index=axis_options.index(last_rx.get('OS', {}).get('Axis', '')) if last_rx.get('OS', {}).get('Axis', '') in axis_options else 0,
                                               key="axis_os_dropdown")
                axis_os_custom = st.text_input("Or type custom Axis OS", value="" if axis_os_dropdown else last_rx.get('OS', {}).get('Axis', ''), key="axis_os_custom")
                os_axis = axis_os_custom if axis_os_custom else axis_os_dropdown
            
            # Doctor fees section
            st.markdown("### 💰 Consultation Fees")
            col_fee1, col_fee2 = st.columns(2)
            with col_fee1:
                consultation_fee = st.number_input("Consultation Fee (₹)", min_value=0, value=500, step=50)
            with col_fee2:
                additional_charges = st.number_input("Additional Charges (₹)", min_value=0, value=0, step=50)
            
            total_consultation = consultation_fee + additional_charges
            if total_consultation > 0:
                st.info(f"Total Consultation: ₹{total_consultation}")
            
            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis}
            }
            st.session_state['rx_table'] = rx_table
            st.session_state['consultation_fee'] = consultation_fee
            st.session_state['additional_charges'] = additional_charges

    # --- Prescription Generator Tab ---
    with tab2:
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
                        st.write(f"• {spec_name}")
                else:
                    st.info("No spectacles selected")
            
            with col2:
                st.markdown("### 💊 Selected Medicines")
                medicine_details = st.session_state.get('medicine_details', {})
                if medicine_details:
                    for med_name, details in medicine_details.items():
                        st.write(f"• {med_name} (Qty: {details['quantity']}) - ₹{details['total_cost']}")
                else:
                    st.info("No medicines selected")
            
            # Generate prescription
            st.markdown("---")
            
            if st.button("📤 Generate Prescription", type="primary"):
                if selected_spectacles or medicine_details:
                    # Automatically update stock in Google Sheets BEFORE generating prescription
                    stock_updates = []
                    stock_errors = []
                    
                    if oauth_sheets_api.is_authenticated() and medicine_details:
                        with st.spinner("Updating medicine stock in Google Sheets..."):
                            for med_name, details in medicine_details.items():
                                if details.get('in_inventory', False):
                                    result = oauth_sheets_api.update_medicine_quantity(med_name, details['quantity'])
                                    if result.get('success'):
                                        stock_updates.append(f"{med_name}: {result.get('old_qty', 0)} → {result.get('new_qty', 0)}")
                                    else:
                                        stock_errors.append(f"{med_name}: {result.get('error', 'Unknown error')}")
                            
                            if stock_updates:
                                st.success(f"✅ Stock updated: {', '.join(stock_updates)}")
                            if stock_errors:
                                st.error(f"❌ Stock update errors: {', '.join(stock_errors)}")
                    elif medicine_details:
                        st.warning("⚠️ OAuth not authenticated - stock will not be updated automatically")
                    
                    # Create prescription HTML
                    current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                    prescription_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MauEyeCare Prescription - {patient_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; background: #2E86AB; color: white; padding: 20px; }}
        .patient-info {{ background: #f8f9ff; padding: 15px; margin: 10px 0; }}
        .prescription {{ padding: 15px; margin: 10px 0; }}
        .item {{ background: #f0f8ff; padding: 10px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MauEyeCare Optical Center</h1>
        <p>Dr. Danish - Eye Care Specialist</p>
        <p>📞 +91 92356-47410 | 📧 maueyecare@gmail.com</p>
    </div>
    
    <div class="patient-info">
        <h3>👤 Patient Information</h3>
        <p><strong>Name:</strong> {patient_name}</p>
        <p><strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')}</p>
        <p><strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')}</p>
        <p><strong>Date:</strong> {current_time.strftime('%d/%m/%Y %I:%M %p IST')}</p>
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
                    
                    # Add spectacles
                    if selected_spectacles:
                        prescription_html += """
    <div class="prescription">
        <h3>👓 Recommended Spectacles</h3>"""
                        
                        for spec_name in selected_spectacles:
                            prescription_html += f"""
        <div class="item">
            <strong>{spec_name}</strong>
        </div>"""
                        
                        prescription_html += "</div>"
                    
                    # Add medicines
                    if medicine_details:
                        prescription_html += """
    <div class="prescription">
        <h3>💊 Prescribed Medicines</h3>"""
                        
                        total_med_cost = 0
                        for med_name, details in medicine_details.items():
                            total_med_cost += details['total_cost']
                            prescription_html += f"""
        <div class="item">
            <strong>{med_name}</strong><br>
            Quantity: {details['quantity']}<br>
            Price: ₹{details['price']} x {details['quantity']} = <strong>₹{details['total_cost']}</strong>
        </div>"""
                        
                        prescription_html += f"""
        <div style="text-align: center; font-weight: bold; margin: 10px 0;">
            Total Medicine Cost: ₹{total_med_cost:,}
        </div>
    </div>"""
                    
                    # Add consultation fees
                    consultation_fee = st.session_state.get('consultation_fee', 0)
                    additional_charges = st.session_state.get('additional_charges', 0)
                    total_consultation = consultation_fee + additional_charges
                    
                    if total_consultation > 0:
                        prescription_html += f"""
    <div class="prescription">
        <h3>💰 Consultation Charges</h3>
        <div class="item">
            <strong>Consultation Fee:</strong> ₹{consultation_fee:,}<br>
            <strong>Additional Charges:</strong> ₹{additional_charges:,}<br>
            <hr>
            <strong>Total Consultation:</strong> ₹{total_consultation:,}
        </div>
    </div>"""
                    
                    # Calculate total bill
                    total_med_cost = sum(details['total_cost'] for details in medicine_details.values()) if medicine_details else 0
                    grand_total = total_med_cost + total_consultation
                    
                    if grand_total > 0:
                        prescription_html += f"""
    <div style="text-align: center; font-weight: bold; margin: 20px 0; background: #e8f5e8; padding: 15px;">
        <h3>Total Bill: ₹{grand_total:,}</h3>
    </div>"""
                    
                    # Add footer
                    prescription_html += """
    <div style="text-align: center; margin-top: 20px; color: #666;">
        <p><strong>Dr. Danish</strong> - Eye Care Specialist</p>
        <p>MauEyeCare Optical Center</p>
        <p>📞 +91 92356-47410 | 📧 maueyecare@gmail.com</p>
    </div>
</body>
</html>"""
                    
                    # Download prescription
                    timestamp = current_time.strftime("%Y%m%d_%H%M")
                    st.download_button(
                        "💾 Download HTML Prescription",
                        data=prescription_html.encode('utf-8'),
                        file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html",
                        mime="text/html",
                        type="primary"
                    )
                    
                    st.success("✅ Prescription generated successfully!")
                    
                    # Mark prescription as generated
                    st.session_state['prescription_generated'] = True
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine to generate prescription")
            
            # Show workflow options after prescription is generated
            if st.session_state.get('prescription_generated', False):
                st.markdown("---")
                st.markdown("### 🎯 Next Steps")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 New Prescription (Same Patient)", type="secondary"):
                        # Clear only prescription data, keep patient info
                        for key in ['selected_spectacles', 'medicine_details', 'selected_medicines_list', 'prescription_generated', 'consultation_fee', 'additional_charges']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.success("🎆 Ready for new prescription!")
                        st.rerun()
                
                with col2:
                    if st.button("👥 Start New Patient", type="primary"):
                        # Clear all patient and prescription data
                        keys_to_clear = [
                            'patient_name', 'patient_mobile', 'age', 'gender', 'address', 'city', 'state', 'pincode',
                            'occupation', 'referral_source', 'patient_issue', 'advice', 'consultation_fee', 'additional_charges',
                            'selected_spectacles', 'medicine_details', 'selected_medicines_list', 'rx_table', 'prescription_generated'
                        ]
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.success("🆕 Ready for new patient registration!")
                        st.rerun()
        else:
            st.info("👆 Please register a patient first in the Patient Registration tab")

    # --- Analytics Tab ---
    with tab3:
        st.header("📊 Hospital Analytics")
        
        # Simple analytics
        try:
            _, _, patients = get_sheet_data()
            if patients:
                st.metric("Total Patients", len(patients))
                
                # Patient demographics
                if isinstance(patients[0], dict):
                    ages = [p.get('age', 30) for p in patients if p.get('age')]
                    if ages:
                        avg_age = sum(ages) / len(ages)
                        st.metric("Average Age", f"{avg_age:.1f}")
                    
                    # Gender distribution
                    genders = [p.get('gender', 'Unknown') for p in patients]
                    gender_counts = {}
                    for gender in genders:
                        gender_counts[gender] = gender_counts.get(gender, 0) + 1
                    
                    st.subheader("Gender Distribution")
                    for gender, count in gender_counts.items():
                        st.write(f"• {gender}: {count} patients")
            else:
                st.info("No patient data available for analytics")
        except:
            st.info("Unable to load analytics data")

if __name__ == "__main__":
    main()