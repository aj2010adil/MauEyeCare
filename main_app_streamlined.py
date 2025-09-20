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
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Mobile: {st.session_state.get('patient_mobile', 'N/A')}")

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
            patient_names = [p.get('name', '') for p in existing_patients if isinstance(p, dict)]
            patient_mobiles = [p.get('mobile', '') for p in existing_patients if isinstance(p, dict)]
        except:
            patient_names = []
            patient_mobiles = []
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                patient_name = st.text_input("Full Name", placeholder="Enter patient full name")
                if patient_names:
                    suggested_name = st.selectbox("Or select existing:", [""] + patient_names[:10], key="name_suggest")
                    if suggested_name:
                        patient_name = suggested_name
                
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                contact = st.text_input("Mobile Number", placeholder="Enter mobile number")
                if patient_mobiles:
                    suggested_mobile = st.selectbox("Or select existing:", [""] + patient_mobiles[:10], key="mobile_suggest")
                    if suggested_mobile:
                        contact = suggested_mobile
                
                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                
                advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Glaucoma Screening", "Diabetic Eye Exam", "Other"]
                advice = st.selectbox("Advice/Notes", advice_options)
            
            submitted = st.form_submit_button("💾 Register Patient", type="primary")
            
            if submitted and patient_name:
                # Check for duplicate based on name and mobile
                is_duplicate = False
                try:
                    for p in existing_patients:
                        if isinstance(p, dict):
                            if (p.get('name', '').lower() == patient_name.lower() and 
                                p.get('mobile', '') == contact):
                                is_duplicate = True
                                break
                except:
                    pass
                
                # Store patient info in session
                st.session_state.update({
                    'patient_name': patient_name,
                    'patient_mobile': contact,
                    'age': age,
                    'gender': gender,
                    'patient_issue': patient_issue,
                    'advice': advice,
                    'new_patient': not is_duplicate
                })
                
                if is_duplicate:
                    st.success(f"🔄 **Return Visit Recorded!** {patient_name}")
                else:
                    st.success(f"✅ **New Patient Registered!** {patient_name}")
                    st.balloons()
                
                # Add to Google Sheets if OAuth available
                if oauth_sheets_api.is_authenticated():
                    patient_record = {
                        'name': patient_name,
                        'age': age,
                        'gender': gender,
                        'mobile': contact,
                        'issue': patient_issue,
                        'advice': advice
                    }
                    oauth_sheets_api.add_patient(patient_record)
                    st.info("✅ **Real-time sync enabled** - Data saved to Google Sheets!")
                
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
                selected_medicines = st.multiselect(
                    "Select Medicines:",
                    options=list(medicine_options.keys()),
                    key="post_reg_medicines"
                )
                
                if selected_medicines:
                    medicine_details = {}
                    for med_name in selected_medicines:
                        med_data = medicine_options[med_name]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            qty = st.number_input(f"Quantity for {med_name}", min_value=1, value=1, key=f"qty_{med_name}")
                        with col2:
                            current_stock = med_data.get('quantity', 0)
                            if current_stock >= qty:
                                st.success(f"✅ Stock: {current_stock}")
                            else:
                                st.error(f"❌ Insufficient stock: {current_stock}")
                        with col3:
                            price = med_data.get('price', 100)
                            st.info(f"₹{price * qty}")
                        
                        medicine_details[med_name] = {
                            'quantity': qty,
                            'price': price,
                            'total_cost': price * qty,
                            'current_stock': current_stock
                        }
                    
                    st.session_state['medicine_details'] = medicine_details
                    
                    # Update quantities in Google Sheets after prescription
                    if st.button("📤 Update Stock & Generate Prescription"):
                        if oauth_sheets_api.is_authenticated():
                            for med_name, details in medicine_details.items():
                                oauth_sheets_api.update_medicine_quantity(med_name, details['quantity'])
                            st.success("✅ Medicine quantities updated in Google Sheets!")
                        st.info("🎯 Ready to generate prescription!")
            
            # Spectacle Selection Section
            st.markdown("### 👓 Spectacle Selection")
            
            try:
                _, spectacles, _ = get_sheet_data()
                spectacle_options = {spec['name']: spec for spec in spectacles if isinstance(spec, dict) and 'name' in spec}
            except:
                spectacle_options = {}
            
            if spectacle_options:
                selected_spectacle = st.selectbox(
                    "Select Spectacle:",
                    options=[""] + list(spectacle_options.keys()),
                    key="post_reg_spectacle"
                )
                
                if selected_spectacle:
                    spec_data = spectacle_options[selected_spectacle]
                    st.info(f"Price: ₹{spec_data.get('price', 0)} | Stock: {spec_data.get('quantity', 0)}")
                    st.session_state['selected_spectacles'] = [selected_spectacle]
            
            # Eye Prescription Section (separate from registration)
            st.markdown("### 👁️ Eye Prescription")
            
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
                od_sphere = st.text_input("Sphere OD", value=last_rx.get('OD', {}).get('Sphere', ''), key="od_sphere")
                od_cylinder = st.text_input("Cylinder OD", value=last_rx.get('OD', {}).get('Cylinder', ''), key="od_cylinder")
                od_axis = st.text_input("Axis OD", value=last_rx.get('OD', {}).get('Axis', ''), key="od_axis")
            
            with col_os:
                st.markdown("**OS (Left Eye)**")
                os_sphere = st.text_input("Sphere OS", value=last_rx.get('OS', {}).get('Sphere', ''), key="os_sphere")
                os_cylinder = st.text_input("Cylinder OS", value=last_rx.get('OS', {}).get('Cylinder', ''), key="os_cylinder")
                os_axis = st.text_input("Axis OS", value=last_rx.get('OS', {}).get('Axis', ''), key="os_axis")
            
            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis}
            }
            st.session_state['rx_table'] = rx_table

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
                    
                    # Clear selections for next prescription
                    if st.button("🔄 New Prescription"):
                        for key in ['selected_spectacles', 'medicine_details']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.success("🎆 Ready for new prescription!")
                        st.rerun()
                else:
                    st.warning("⚠️ Please select at least one spectacle or medicine")
        else:
            st.warning("⚠️ Please register a patient first")

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