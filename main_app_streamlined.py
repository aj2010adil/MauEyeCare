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
    
    st.title("🏥 Mau Eye Care - Professional Eye Care Hospital")
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

        # Low stock alerts for doctor
        try:
            medicines, _, _ = get_sheet_data()
            low_stock_medicines = [m for m in medicines if isinstance(m, dict) and int(m.get('quantity', 0)) < 10]
            if low_stock_medicines:
                st.markdown("---")
                st.error(f"⚠️ **LOW STOCK ALERT** - {len(low_stock_medicines)} medicines need restocking!")
                with st.expander("View Low Stock Items"):
                    for med in low_stock_medicines:
                        stock_level = int(med.get('quantity', 0))
                        if stock_level == 0:
                            st.error(f"🚫 {med.get('name', 'Unknown')}: OUT OF STOCK")
                        else:
                            st.warning(f"⚠️ {med.get('name', 'Unknown')}: {stock_level} units left")
        except:
            pass

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
        existing_patients = []
        patient_names = []
        patient_mobiles = []
        try:
            _, _, existing_patients = get_sheet_data()
            if existing_patients:
                patient_names = [p.get('name', '') for p in existing_patients if isinstance(p, dict) and p.get('name')]
                patient_mobiles = [p.get('mobile', '') for p in existing_patients if isinstance(p, dict) and p.get('mobile')]
        except Exception as e:
            existing_patients = []
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

                # Address fields for demographics with defaults
                address = st.text_input("Address", placeholder="Street address")
                col_city, col_state = st.columns(2)
                with col_city:
                    city = st.text_input("City", value="Mubarkpur, Azamgarh", placeholder="City name")
                with col_state:
                    state = st.selectbox("State", [
                        "Uttar Pradesh", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
                        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
                        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
                        "Telangana", "Tripura", "Uttarakhand", "West Bengal", "Delhi"
                    ])
                pincode = st.text_input("Pincode", value="276404", placeholder="6-digit pincode")

            with col2:
                # Combined dropdown + custom input for mobile
                mobile_options = ["-- Enter Custom Mobile --"] + patient_mobiles[:15]
                selected_mobile = st.selectbox("Mobile Number", mobile_options, key="mobile_dropdown")

                if selected_mobile == "-- Enter Custom Mobile --":
                    contact = st.text_input("Enter Mobile Number", placeholder="Type mobile number", key="custom_mobile")
                else:
                    contact = selected_mobile
                    st.info(f"Selected: {selected_mobile}")

                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Headache", "Eye Strain", "Watering", "Itching", "Burning Sensation", "Foreign Body Sensation", "Light Sensitivity", "Discharge", "Swelling", "Routine Checkup", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                if patient_issue == "Other":
                    custom_issue = st.text_area("Specify Issue/Complaint", placeholder="Describe the patient's complaint in detail", key="custom_issue")
                    patient_issue = custom_issue if custom_issue else "Other"

                advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Glaucoma Screening", "Diabetic Eye Exam", "Contact Lens Consultation", "Vision Therapy", "Follow-up in 1 month", "Follow-up in 3 months", "Follow-up in 6 months", "Refer to Specialist", "Eye Protection Advised", "Computer Vision Syndrome Care", "Other"]
                advice = st.selectbox("Advice/Notes", advice_options)
                if advice == "Other":
                    custom_advice = st.text_area("Specify Advice/Notes", placeholder="Enter detailed advice or notes for the patient", key="custom_advice")
                    advice = custom_advice if custom_advice else "Other"

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

                    # Show last visit details for returning patient
                    st.markdown("---")
                    st.subheader("📅 Previous Visit History")

                    try:
                        # Get patient's previous visits
                        for p in existing_patients:
                            if isinstance(p, dict) and (p.get('name', '').lower().strip() == patient_name.lower().strip() and
                                                       p.get('mobile', '').strip() == contact.strip()):
                                col_hist1, col_hist2 = st.columns(2)
                                with col_hist1:
                                    st.info(f"**Last Issue:** {p.get('issue', 'N/A')}")
                                    st.info(f"**Previous Advice:** {p.get('advice', 'N/A')}")
                                with col_hist2:
                                    st.info(f"**Age at Last Visit:** {p.get('age', 'N/A')}")
                                    st.info(f"**Total Visits:** {p.get('visits', 1)}")
                                break

                        # Get last prescription if available
                        try:
                            prescriptions = sheets_manager.get_prescriptions()
                            patient_prescriptions = [pr for pr in prescriptions if isinstance(pr, dict) and pr.get('patient_name', '').lower() == patient_name.lower()]
                            if patient_prescriptions:
                                last_prescription = patient_prescriptions[-1]
                                st.markdown("**Last Prescription:**")
                                if last_prescription.get('spectacles'):
                                    st.write(f"👓 Spectacles: {last_prescription.get('spectacles', 'None')}")
                                if last_prescription.get('medicines'):
                                    st.write(f"💊 Medicines: {last_prescription.get('medicines', 'None')}")
                        except:
                            st.info("📄 No previous prescription found")
                    except:
                        st.info("📅 Unable to load visit history")
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

                # Show selected medicines with quantities and dosage
                if st.session_state.get('selected_medicines_list'):
                    st.markdown("**Selected Medicines with Dosage:**")
                    medicine_details = {}

                    for med_name in st.session_state['selected_medicines_list']:
                        with st.container():
                            st.markdown(f"**{med_name}**")
                            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

                            with col1:
                                qty = st.number_input("Quantity", min_value=1, value=1, key=f"qty_{med_name}")

                            with col2:
                                # Doctor customizable dosage
                                if med_name in medicine_options:
                                    med_data = medicine_options[med_name]
                                    med_type = med_data.get('type', 'tablet').lower()

                                    # Default dosage suggestions based on medicine type
                                    if 'drop' in med_type or 'eye' in med_type:
                                        default_dosage = "1 drop 4 times daily"
                                    elif 'tablet' in med_type or 'tab' in med_type:
                                        default_dosage = "1 tab 2 times daily"
                                    elif 'capsule' in med_type or 'cap' in med_type:
                                        default_dosage = "1 cap 2 times daily"
                                    elif 'syrup' in med_type:
                                        default_dosage = "5ml 3 times daily"
                                    elif 'ointment' in med_type:
                                        default_dosage = "Apply 2 times daily"
                                    else:
                                        default_dosage = "As directed"
                                else:
                                    default_dosage = "As directed"

                                dosage = st.text_input("Dosage", value=default_dosage, key=f"dosage_{med_name}")

                            with col3:
                                # Doctor customizable timing
                                if med_name in medicine_options:
                                    med_data = medicine_options[med_name]
                                    med_type = med_data.get('type', 'tablet').lower()

                                    if 'drop' in med_type or 'eye' in med_type:
                                        default_timing = "Morning, Afternoon, Evening, Night"
                                    elif 'tablet' in med_type or 'tab' in med_type:
                                        default_timing = "After meals (Morning & Evening)"
                                    else:
                                        default_timing = "As per doctor's advice"
                                else:
                                    default_timing = "As per doctor's advice"

                                timing = st.text_input("Timing", value=default_timing, key=f"timing_{med_name}")

                            with col4:
                                if st.button("🗑️ Remove", key=f"remove_{med_name}"):
                                    st.session_state['selected_medicines_list'].remove(med_name)
                                    st.rerun()

                            # Stock info (price hidden from display but tracked internally)
                            if med_name in medicine_options:
                                med_data = medicine_options[med_name]
                                current_stock = int(med_data.get('quantity', 0))
                                price = float(med_data.get('price', 100))

                                if current_stock >= qty:
                                    st.success(f"✅ Stock Available: {current_stock} units")
                                else:
                                    st.error(f"❌ Low Stock: {current_stock} units")

                                medicine_details[med_name] = {
                                    'quantity': qty,
                                    'price': price,
                                    'total_cost': price * qty,
                                    'current_stock': current_stock,
                                    'dosage': dosage,
                                    'timing': timing,
                                    'in_inventory': True
                                }
                            else:
                                st.info("📊 Custom medicine")
                                medicine_details[med_name] = {
                                    'quantity': qty,
                                    'price': 0,
                                    'total_cost': 0,
                                    'current_stock': 0,
                                    'dosage': dosage,
                                    'timing': timing,
                                    'in_inventory': False
                                }

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

                    # Add spectacle usage instructions for first-time users
                    st.markdown("**Spectacle Usage Instructions:**")
                    first_time_user = st.checkbox("First time spectacle user?", key="first_time_spec")

                    if first_time_user:
                        st.session_state['spectacle_instructions'] = """• Start by wearing glasses for 2-3 hours daily, gradually increase usage
• Clean lenses with microfiber cloth and lens cleaner only
• Store in protective case when not in use
• Avoid placing glasses lens-down on surfaces
• Initial mild headache or dizziness is normal for 2-3 days
• Return for adjustment if discomfort persists beyond a week"""
                    else:
                        custom_instructions = st.text_area("Custom spectacle instructions:",
                                                         placeholder="Enter specific care instructions",
                                                         key="custom_spec_instructions")
                        st.session_state['spectacle_instructions'] = custom_instructions or "Follow standard spectacle care guidelines"

            # Eye Prescription Section (separate from registration)
            st.markdown("### 👁️ Eye Prescription")

            # Complaint and Diagnosis Section
            st.markdown("#### 🩺 Clinical Assessment")
            col_clinical1, col_clinical2 = st.columns(2)

            with col_clinical1:
                complaint = st.text_area("Chief Complaint", placeholder="Enter patient's chief complaint", key="complaint")

            with col_clinical2:
                diagnosis = st.text_area("Diagnosis", placeholder="Enter diagnosis", key="diagnosis")

            # Vision Testing Section
            st.markdown("#### 📊 Vision Testing")
            col_vision1, col_vision2 = st.columns(2)

            with col_vision1:
                st.markdown("**OD (Right Eye) Vision**")
                vision_options = ["", "6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60", "CF (Counting Fingers)", "HM (Hand Movement)", "PL (Perception of Light)", "NPL (No Perception of Light)"]
                od_vision = st.selectbox("OD Distance Vision", vision_options, key="od_distance_vision")
                near_vision_options = ["", "N6", "N8", "N10", "N12", "N18", "N24", "N36", "N48"]
                od_near_vision = st.selectbox("OD Near Vision", near_vision_options, key="od_near_vision")

            with col_vision2:
                st.markdown("**OS (Left Eye) Vision**")
                os_vision = st.selectbox("OS Distance Vision", vision_options, key="os_distance_vision")
                os_near_vision = st.selectbox("OS Near Vision", near_vision_options, key="os_near_vision")

            # Standard prescription values for suggestions
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+1.75", "+2.00", "+2.25", "+2.50", "+3.00", "+3.50", "+4.00", "+5.00", "+6.00",
                            "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-1.75", "-2.00", "-2.25", "-2.50", "-3.00", "-3.50", "-4.00", "-5.00", "-6.00", "-8.00", "-10.00"]
            cylinder_options = ["", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-1.75", "-2.00", "-2.25", "-2.50", "-3.00", "-4.00", "-5.00"]
            axis_options = ["", "10", "15", "20", "30", "45", "60", "75", "90", "105", "120", "135", "150", "165", "180"]
            near_add_options = ["", "+1.00", "+1.25", "+1.50", "+1.75", "+2.00", "+2.25", "+2.50", "+2.75", "+3.00", "+3.25", "+3.50", "+3.75", "+4.00"]

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

            st.markdown("#### 🔍 Prescription Details")
            col_od, col_os, col_near = st.columns(3)

            with col_od:
                st.markdown("**OD (Right Eye)**")

                # Sphere OD with suggestions
                sphere_od_dropdown = st.selectbox("Sphere OD", sphere_options,
                                                index=sphere_options.index(last_rx.get('OD', {}).get('Sphere', '')) if last_rx.get('OD', {}).get('Sphere', '') in sphere_options else 0,
                                                key="sphere_od_dropdown")
                sphere_od_custom = st.text_input("Custom Sphere OD", value="" if sphere_od_dropdown else last_rx.get('OD', {}).get('Sphere', ''), key="sphere_od_custom")
                od_sphere = sphere_od_custom if sphere_od_custom else sphere_od_dropdown

                # Cylinder OD with suggestions
                cylinder_od_dropdown = st.selectbox("Cylinder OD", cylinder_options,
                                                   index=cylinder_options.index(last_rx.get('OD', {}).get('Cylinder', '')) if last_rx.get('OD', {}).get('Cylinder', '') in cylinder_options else 0,
                                                   key="cylinder_od_dropdown")
                cylinder_od_custom = st.text_input("Custom Cylinder OD", value="" if cylinder_od_dropdown else last_rx.get('OD', {}).get('Cylinder', ''), key="cylinder_od_custom")
                od_cylinder = cylinder_od_custom if cylinder_od_custom else cylinder_od_dropdown

                # Axis OD with suggestions
                axis_od_dropdown = st.selectbox("Axis OD", axis_options,
                                               index=axis_options.index(last_rx.get('OD', {}).get('Axis', '')) if last_rx.get('OD', {}).get('Axis', '') in axis_options else 0,
                                               key="axis_od_dropdown")
                axis_od_custom = st.text_input("Custom Axis OD", value="" if axis_od_dropdown else last_rx.get('OD', {}).get('Axis', ''), key="axis_od_custom")
                od_axis = axis_od_custom if axis_od_custom else axis_od_dropdown

            with col_os:
                st.markdown("**OS (Left Eye)**")

                # Sphere OS with suggestions
                sphere_os_dropdown = st.selectbox("Sphere OS", sphere_options,
                                                 index=sphere_options.index(last_rx.get('OS', {}).get('Sphere', '')) if last_rx.get('OS', {}).get('Sphere', '') in sphere_options else 0,
                                                 key="sphere_os_dropdown")
                sphere_os_custom = st.text_input("Custom Sphere OS", value="" if sphere_os_dropdown else last_rx.get('OS', {}).get('Sphere', ''), key="sphere_os_custom")
                os_sphere = sphere_os_custom if sphere_os_custom else sphere_os_dropdown

                # Cylinder OS with suggestions
                cylinder_os_dropdown = st.selectbox("Cylinder OS", cylinder_options,
                                                   index=cylinder_options.index(last_rx.get('OS', {}).get('Cylinder', '')) if last_rx.get('OS', {}).get('Cylinder', '') in cylinder_options else 0,
                                                   key="cylinder_os_dropdown")
                cylinder_os_custom = st.text_input("Custom Cylinder OS", value="" if cylinder_os_dropdown else last_rx.get('OS', {}).get('Cylinder', ''), key="cylinder_os_custom")
                os_cylinder = cylinder_os_custom if cylinder_os_custom else cylinder_os_dropdown

                # Axis OS with suggestions
                axis_os_dropdown = st.selectbox("Axis OS", axis_options,
                                               index=axis_options.index(last_rx.get('OS', {}).get('Axis', '')) if last_rx.get('OS', {}).get('Axis', '') in axis_options else 0,
                                               key="axis_os_dropdown")
                axis_os_custom = st.text_input("Custom Axis OS", value="" if axis_os_dropdown else last_rx.get('OS', {}).get('Axis', ''), key="axis_os_custom")
                os_axis = axis_os_custom if axis_os_custom else axis_os_dropdown

            with col_near:
                st.markdown("**Near Vision ADD**")

                # Near ADD for OD
                near_add_od_dropdown = st.selectbox("ADD OD", near_add_options,
                                                   index=near_add_options.index(last_rx.get('OD', {}).get('ADD', '')) if last_rx.get('OD', {}).get('ADD', '') in near_add_options else 0,
                                                   key="near_add_od_dropdown")
                near_add_od_custom = st.text_input("Custom ADD OD", value="" if near_add_od_dropdown else last_rx.get('OD', {}).get('ADD', ''), key="near_add_od_custom")
                od_add = near_add_od_custom if near_add_od_custom else near_add_od_dropdown

                # Near ADD for OS
                near_add_os_dropdown = st.selectbox("ADD OS", near_add_options,
                                                   index=near_add_options.index(last_rx.get('OS', {}).get('ADD', '')) if last_rx.get('OS', {}).get('ADD', '') in near_add_options else 0,
                                                   key="near_add_os_dropdown")
                near_add_os_custom = st.text_input("Custom ADD OS", value="" if near_add_os_dropdown else last_rx.get('OS', {}).get('ADD', ''), key="near_add_os_custom")
                os_add = near_add_os_custom if near_add_os_custom else near_add_os_dropdown

            # Doctor fees section
            st.markdown("### 💰 Consultation Fees")
            col_fee1, col_fee2 = st.columns(2)
            with col_fee1:
                consultation_fee = st.number_input("Consultation Fee (₹)", min_value=0, value=100, step=50)
            with col_fee2:
                additional_charges = st.number_input("Additional Charges (₹)", min_value=0, value=0, step=50)

            total_consultation = consultation_fee + additional_charges
            if total_consultation > 0:
                st.info(f"Total Consultation: ₹{total_consultation}")

            rx_table = {
                "OD": {"Sphere": od_sphere, "Cylinder": od_cylinder, "Axis": od_axis, "ADD": od_add, "Vision": od_vision, "Near": od_near_vision},
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis, "ADD": os_add, "Vision": os_vision, "Near": os_near_vision}
            }
            st.session_state['rx_table'] = rx_table
            st.session_state['consultation_fee'] = consultation_fee
            st.session_state['additional_charges'] = additional_charges
            st.session_state['patient_complaint'] = complaint
            st.session_state['patient_diagnosis'] = diagnosis

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

                    # Show spectacle instructions if any
                    if st.session_state.get('spectacle_instructions'):
                        st.markdown("**Usage Instructions:**")
                        st.info(st.session_state['spectacle_instructions'])
                else:
                    st.info("No spectacles selected")

            with col2:
                st.markdown("### 💊 Selected Medicines")
                medicine_details = st.session_state.get('medicine_details', {})
                if medicine_details:
                    for med_name, details in medicine_details.items():
                        st.write(f"• {med_name} - Qty: {details['quantity']} | Dosage: {details.get('dosage', 'As directed')} | Timing: {details.get('timing', 'As directed')} | ₹{details['total_cost']}")
                else:
                    st.info("No medicines selected")

                # Show total cost breakdown
                total_med_cost = sum(details['total_cost'] for details in medicine_details.values()) if medicine_details else 0
                consultation_fee = st.session_state.get('consultation_fee', 0)
                additional_charges = st.session_state.get('additional_charges', 0)

                if total_med_cost > 0 or consultation_fee > 0:
                    st.markdown("**Cost Breakdown:**")
                    if total_med_cost > 0:
                        st.write(f"• Medicines: ₹{total_med_cost:,}")
                    if consultation_fee > 0:
                        st.write(f"• Consultation: ₹{consultation_fee:,}")
                    if additional_charges > 0:
                        st.write(f"• Additional: ₹{additional_charges:,}")

                    grand_total = total_med_cost + consultation_fee + additional_charges
                    st.markdown(f"**Total: ₹{grand_total:,}**")

            # Generate prescription
            st.markdown("---")

            # Prescription Preview
            if st.button("🔍 Preview Prescription", type="secondary"):
                if selected_spectacles or medicine_details:
                    st.markdown("---")
                    st.subheader("🔍 Prescription Preview")

                    # Patient info preview
                    st.markdown(f"**Patient:** {patient_name} | **Age:** {st.session_state.get('age', 'N/A')} | **Mobile:** {st.session_state.get('patient_mobile', 'N/A')}")

                    # Eye prescription preview
                    rx_table = st.session_state.get('rx_table', {})
                    if rx_table and (rx_table.get('OD', {}).get('Sphere') or rx_table.get('OS', {}).get('Sphere')):
                        st.markdown("**Eye Prescription:**")
                        col_prev1, col_prev2 = st.columns(2)
                        with col_prev1:
                            od_data = rx_table.get('OD', {})
                            st.write(f"OD: SPH {od_data.get('Sphere', '')} CYL {od_data.get('Cylinder', '')} AXIS {od_data.get('Axis', '')} ADD {od_data.get('ADD', '')}")
                        with col_prev2:
                            os_data = rx_table.get('OS', {})
                            st.write(f"OS: SPH {os_data.get('Sphere', '')} CYL {os_data.get('Cylinder', '')} AXIS {os_data.get('Axis', '')} ADD {os_data.get('ADD', '')}")

                    # Vision testing preview
                    if rx_table and (rx_table.get('OD', {}).get('Vision') or rx_table.get('OS', {}).get('Vision')):
                        st.markdown("**Vision Testing:**")
                        col_vis1, col_vis2 = st.columns(2)
                        with col_vis1:
                            od_data = rx_table.get('OD', {})
                            st.write(f"OD: Distance {od_data.get('Vision', '')} | Near {od_data.get('Near', '')}")
                        with col_vis2:
                            os_data = rx_table.get('OS', {})
                            st.write(f"OS: Distance {os_data.get('Vision', '')} | Near {os_data.get('Near', '')}")

                    # Spectacles preview
                    if selected_spectacles:
                        st.markdown("**Spectacles:**")
                        for spec in selected_spectacles:
                            st.write(f"• {spec}")

                        # Show spectacle instructions
                        if st.session_state.get('spectacle_instructions'):
                            st.markdown("**Usage Instructions:**")
                            st.info(st.session_state['spectacle_instructions'])

                    # Medicines preview
                    if medicine_details:
                        st.markdown("**Medicines:**")
                        for med_name, details in medicine_details.items():
                            st.write(f"• {med_name} - Qty: {details['quantity']} | Dosage: {details.get('dosage', 'N/A')} | Timing: {details.get('timing', 'N/A')}")

                    # Show total cost breakdown
                    if total_med_cost > 0 or consultation_fee > 0:
                        st.markdown("**Cost Breakdown:**")
                        if total_med_cost > 0:
                            st.write(f"• Medicines: ₹{total_med_cost:,}")
                        if consultation_fee > 0:
                            st.write(f"• Consultation: ₹{consultation_fee:,}")
                        if additional_charges > 0:
                            st.write(f"• Additional: ₹{additional_charges:,}")

                        grand_total = total_med_cost + consultation_fee + additional_charges
                        st.markdown(f"**Total: ₹{grand_total:,}**")
                else:
                    st.warning("⚠️ Please select medicines or spectacles to preview")

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
    <title>Mau Eye Care Prescription - {patient_name}</title>
    <style>
        @page {{ margin: 0.4in; size: A4; }}
        body {{ 
            font-family: Arial, sans-serif; margin: 0; padding: 0; font-size: 11px; line-height: 1.2;
            background-image: url('file:///D:/Users/W7146644/WebstormProjects/MauEyeCare/mec.jpg');
            background-size: cover; background-position: center; background-repeat: no-repeat;
        }}
        .page {{ background: rgba(255,255,255,0.95); min-height: 100vh; padding: 10px; }}
        .header {{ background: rgba(46, 134, 171, 0.9); color: white; padding: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }}
        .header-left {{ text-align: left; flex: 1; }}
        .header-center {{ text-align: center; flex: 1; }}
        .header-right {{ text-align: right; flex: 1; }}
        .header h1 {{ margin: 3px 0; font-size: 16px; }}
        .header h2 {{ margin: 2px 0; font-size: 14px; font-weight: bold; }}
        .header p {{ margin: 1px 0; font-size: 10px; }}
        .urdu {{ font-family: 'Noto Nastaliq Urdu', 'Arial Unicode MS', sans-serif; }}
        .patient-info {{ background: rgba(248, 249, 255, 0.9); padding: 6px; margin: 4px 0; font-size: 10px; }}
        .patient-info h3 {{ margin: 3px 0; font-size: 12px; }}
        .two-column {{ display: flex; gap: 15px; }}
        .left-column {{ flex: 1; }}
        .right-column {{ flex: 1; }}
        .prescription {{ padding: 6px; margin: 4px 0; background: rgba(255,255,255,0.8); }}
        .prescription h3 {{ margin: 4px 0; font-size: 12px; }}
        .item {{ background: rgba(240, 248, 255, 0.9); padding: 4px; margin: 2px 0; font-size: 10px; }}
        .vision-table {{ width: 100%; border-collapse: collapse; margin: 5px 0; background: rgba(255,255,255,0.9); }}
        .vision-table th, .vision-table td {{ border: 1px solid #ccc; padding: 3px; text-align: center; font-size: 9px; }}
        .cost-summary {{ text-align: center; font-weight: bold; margin: 6px 0; background: rgba(232, 245, 232, 0.9); padding: 6px; font-size: 11px; }}
        .footer {{ text-align: center; margin-top: 8px; color: #666; font-size: 9px; background: rgba(255,255,255,0.8); padding: 5px; }}
        .services {{ background: rgba(255,255,255,0.9); padding: 8px; margin: 8px 0; }}
        .signature {{ background: rgba(255,255,255,0.9); padding: 8px; margin: 8px 0; text-align: right; }}
        @media print {{ .page {{ page-break-after: always; }} }}
    </style>
</head>
<body>
    <div class="page">
    <div class="header">
        <div class="header-left">
            <h2>Dr. Danish</h2>
            <p>B.Sc. Optometry</p>
            <p>Optometrist & Eye Specialist</p>
            <p>Reg. No.: UPS 2908</p>
            <p>📞 +91 92356-47410</p>
        </div>
        <div class="header-center">
            <h1>Mau Eye Care</h1>
            <p>Pura Sofi Bhonu Kuraishi Dasai Kuwa</p>
            <p>Mubarakpur, Azamgarh, Uttar Pradesh, India</p>
            <p>📧 mau.eye.care.404@gmail.com</p>
            <p>Mon-Sat: 10:00 AM - 4:00 PM | Sunday: Closed</p>
        </div>
        <div class="header-right">
            <h2 class="urdu">ڈاکٹر دانش</h2>
            <p class="urdu">بی ایس سی آپٹومیٹری</p>
            <p class="urdu">آنکھوں کے ماہر</p>
            <p class="urdu">رجسٹریشن نمبر: یو پی ایس ۲۹۰۸</p>
        </div>
    </div>

    <div class="patient-info">
        <h3>👤 Patient Information</h3>
        <p><strong>Name:</strong> {patient_name} | <strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')}</p>
        <p><strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')} | <strong>Date:</strong> {current_time.strftime('%d/%m/%Y %I:%M %p IST')}</p>
        <p><strong>Address:</strong> {st.session_state.get('address', '')}, {st.session_state.get('city', '')}, {st.session_state.get('state', '')} - {st.session_state.get('pincode', '')}</p>
        <p><strong>Complaint:</strong> {st.session_state.get('patient_complaint', 'N/A')} | <strong>Diagnosis:</strong> {st.session_state.get('patient_diagnosis', 'N/A')}</p>
    </div>"""

                    # Start two-column layout
                    prescription_html += """
    <div class="two-column">
        <div class="left-column">"""

                    # Add eye prescription
                    rx_table = st.session_state.get('rx_table', {})
                    if rx_table:
                        prescription_html += """
            <div class="prescription">
                <h3>👁️ Eye Prescription</h3>
                <table class="vision-table">
                    <tr>
                        <th>Eye</th>
                        <th>SPH</th>
                        <th>CYL</th>
                        <th>AXIS</th>
                        <th>ADD</th>
                    </tr>"""
                        
                        od_data = rx_table.get('OD', {})
                        os_data = rx_table.get('OS', {})
                        prescription_html += f"""
                    <tr>
                        <td><strong>OD</strong></td>
                        <td>{od_data.get('Sphere', '')}</td>
                        <td>{od_data.get('Cylinder', '')}</td>
                        <td>{od_data.get('Axis', '')}</td>
                        <td>{od_data.get('ADD', '')}</td>
                    </tr>
                    <tr>
                        <td><strong>OS</strong></td>
                        <td>{os_data.get('Sphere', '')}</td>
                        <td>{os_data.get('Cylinder', '')}</td>
                        <td>{os_data.get('Axis', '')}</td>
                        <td>{os_data.get('ADD', '')}</td>
                    </tr>
                </table>
                
                <h3>👁️ Vision Testing</h3>
                <table class="vision-table">
                    <tr>
                        <th>Eye</th>
                        <th>Distance Vision</th>
                        <th>Near Vision</th>
                    </tr>
                    <tr>
                        <td><strong>OD</strong></td>
                        <td>{od_data.get('Vision', '')}</td>
                        <td>{od_data.get('Near', '')}</td>
                    </tr>
                    <tr>
                        <td><strong>OS</strong></td>
                        <td>{os_data.get('Vision', '')}</td>
                        <td>{os_data.get('Near', '')}</td>
                    </tr>
                </table>
            </div>"""

                    # Add spectacles in left column
                    if selected_spectacles:
                        prescription_html += """
            <div class="prescription">
                <h3>👓 Recommended Spectacles</h3>"""

                        for spec_name in selected_spectacles:
                            prescription_html += f"""
                <div class="item">
                    <strong>{spec_name}</strong>
                </div>"""

                        # Add spectacle instructions
                        spectacle_instructions = st.session_state.get('spectacle_instructions', '')
                        if spectacle_instructions:
                            prescription_html += f"""
                <div class="item">
                    <strong>Care Instructions:</strong><br>
                    {spectacle_instructions.replace(chr(10), '<br>').replace('•', '&bull;')}
                </div>"""

                        prescription_html += "</div>"

                    # Close left column and start right column
                    prescription_html += """
        </div>
        <div class="right-column">"""

                    # Add medicines in right column
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
                    Qty: {details['quantity']} | {details.get('dosage', 'As directed')}<br>
                    {details.get('timing', 'As directed')}
                </div>"""

                        prescription_html += """
            </div>"""



                    # Close right column and two-column layout
                    prescription_html += """
        </div>
    </div>"""



                    # Add services and signature
                    prescription_html += """
    <div class="services">
        <h3>Our Services:</h3>
        <p>• Eye Examinations • Prescription Glasses • Contact Lens Fitting • Eye Disease Treatment • Vision Therapy</p>
    </div>
    
    <div class="signature">
        <p>Doctor Signature: ___________________________</p>
    </div>
    
    <div class="footer">
        <p><strong>Dr. Danish, B.Sc. Optometry</strong> - Optometrist & Eye Specialist | Reg. No.: UPS 2908</p>
        <p>Mau Eye Care | Mubarakpur, Azamgarh | 📞 +91 92356-47410 | 📧 mau.eye.care.404@gmail.com</p>
    </div>
    </div>
</body>
</html>"""

                    # Create detailed receipt HTML
                    receipt_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mau Eye Care Receipt - {patient_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; background: #2E86AB; color: white; padding: 10px; margin-bottom: 20px; }}
        .receipt-item {{ background: #f0f8ff; padding: 8px; margin: 5px 0; border-left: 4px solid #2E86AB; }}
        .total {{ background: #e8f5e8; padding: 10px; font-weight: bold; text-align: center; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Mau Eye Care - Payment Receipt</h2>
        <p>Patient: {patient_name} | Date: {current_time.strftime('%d/%m/%Y %I:%M %p')}</p>
    </div>
    
    <h3>Medicine Details:</h3>"""

                    total_med_cost = 0
                    if medicine_details:
                        for med_name, details in medicine_details.items():
                            total_med_cost += details['total_cost']
                            receipt_html += f"""
    <div class="receipt-item">
        <strong>{med_name}</strong><br>
        Quantity: {details['quantity']} | Unit Price: ₹{details['price']} | Total: ₹{details['total_cost']}<br>
        Dosage: {details.get('dosage', 'As directed')} | Timing: {details.get('timing', 'As directed')}
    </div>"""

                    consultation_fee = st.session_state.get('consultation_fee', 0)
                    additional_charges = st.session_state.get('additional_charges', 0)
                    total_consultation = consultation_fee + additional_charges

                    if total_consultation > 0:
                        receipt_html += f"""
    <h3>Consultation Charges:</h3>
    <div class="receipt-item">
        Consultation Fee: ₹{consultation_fee}<br>
        Additional Charges: ₹{additional_charges}<br>
        <strong>Consultation Total: ₹{total_consultation}</strong>
    </div>"""

                    grand_total = total_med_cost + total_consultation
                    receipt_html += f"""
    <div class="total">
        <h2>TOTAL AMOUNT: ₹{grand_total:,}</h2>
    </div>
</body>
</html>"""

                    # Download buttons
                    timestamp = current_time.strftime("%Y%m%d_%H%M")
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            "💾 Download Prescription",
                            data=prescription_html.encode('utf-8'),
                            file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html",
                            mime="text/html",
                            type="primary"
                        )
                    
                    with col_dl2:
                        st.download_button(
                            "💾 Download Receipt",
                            data=receipt_html.encode('utf-8'),
                            file_name=f"Receipt_{patient_name.replace(' ', '_')}_{timestamp}.html",
                            mime="text/html",
                            type="secondary"
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
        st.header("📊 Hospital Analytics & Business Intelligence")

        try:
            medicines, spectacles, patients = get_sheet_data()

            # Debug: Check if data is loaded
            if not medicines and not spectacles and not patients:
                st.warning("⚠️ No data loaded from Google Sheets. Checking connection...")
                if not oauth_sheets_api.is_authenticated():
                    st.error("❌ Google Sheets not authenticated. Please connect first.")
                    auth_url = oauth_sheets_api.get_auth_url()
                    st.markdown(f"[🔗 Connect to Google Sheets]({auth_url})")
                    return
                else:
                    st.info("🔄 Trying to refresh data...")
                    get_sheet_data.clear()
                    medicines, spectacles, patients = get_sheet_data()

            if patients and len(patients) > 0:
                # Key Performance Indicators
                st.subheader("🎯 Key Performance Indicators")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    total_patients = len(patients)
                    st.metric("Total Patients", total_patients)

                with col2:
                    # Calculate return patients
                    unique_patients = set()
                    return_visits = 0
                    for p in patients:
                        if isinstance(p, dict):
                            patient_key = f"{p.get('name', '')}-{p.get('mobile', '')}"
                            if patient_key in unique_patients:
                                return_visits += 1
                            else:
                                unique_patients.add(patient_key)

                    return_rate = (return_visits / total_patients * 100) if total_patients > 0 else 0
                    st.metric("Return Rate", f"{return_rate:.1f}%")

                with col3:
                    # Average age
                    ages = [int(p.get('age', 0)) for p in patients if isinstance(p, dict) and p.get('age')]
                    avg_age = sum(ages) / len(ages) if ages else 0
                    st.metric("Average Age", f"{avg_age:.1f} years")

                with col4:
                    # Revenue estimation (consultation fees)
                    avg_consultation = 500  # Default consultation fee
                    estimated_revenue = total_patients * avg_consultation
                    st.metric("Est. Revenue", f"₹{estimated_revenue:,}")

                # Demographics Analysis
                st.subheader("👥 Patient Demographics")

                col_demo1, col_demo2 = st.columns(2)

                with col_demo1:
                    st.markdown("**Gender Distribution**")
                    gender_counts = {}
                    for p in patients:
                        if isinstance(p, dict):
                            gender = p.get('gender', 'Unknown')
                            gender_counts[gender] = gender_counts.get(gender, 0) + 1

                    for gender, count in gender_counts.items():
                        percentage = (count / total_patients * 100) if total_patients > 0 else 0
                        st.write(f"• {gender}: {count} ({percentage:.1f}%)")

                with col_demo2:
                    st.markdown("**Age Groups**")
                    age_groups = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}

                    for age in ages:
                        if age <= 18:
                            age_groups["0-18"] += 1
                        elif age <= 35:
                            age_groups["19-35"] += 1
                        elif age <= 50:
                            age_groups["36-50"] += 1
                        elif age <= 65:
                            age_groups["51-65"] += 1
                        else:
                            age_groups["65+"] += 1

                    for age_group, count in age_groups.items():
                        percentage = (count / len(ages) * 100) if ages else 0
                        st.write(f"• {age_group}: {count} ({percentage:.1f}%)")

                # Geographic Analysis
                st.subheader("🗺️ Geographic Distribution")

                col_geo1, col_geo2 = st.columns(2)

                with col_geo1:
                    st.markdown("**Top Cities**")
                    city_counts = {}
                    for p in patients:
                        if isinstance(p, dict) and p.get('city'):
                            city = p.get('city', 'Unknown')
                            city_counts[city] = city_counts.get(city, 0) + 1

                    # Sort cities by count
                    sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    for city, count in sorted_cities:
                        percentage = (count / total_patients * 100) if total_patients > 0 else 0
                        st.write(f"• {city}: {count} ({percentage:.1f}%)")

                with col_geo2:
                    st.markdown("**Top States**")
                    state_counts = {}
                    for p in patients:
                        if isinstance(p, dict) and p.get('state'):
                            state = p.get('state', 'Unknown')
                            state_counts[state] = state_counts.get(state, 0) + 1

                    # Sort states by count
                    sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    for state, count in sorted_states:
                        percentage = (count / total_patients * 100) if total_patients > 0 else 0
                        st.write(f"• {state}: {count} ({percentage:.1f}%)")

                # Marketing Analysis
                st.subheader("📱 Marketing & Referral Analysis")

                col_market1, col_market2 = st.columns(2)

                with col_market1:
                    st.markdown("**Referral Sources**")
                    referral_counts = {}
                    for p in patients:
                        if isinstance(p, dict) and p.get('referral_source'):
                            source = p.get('referral_source', 'Unknown')
                            referral_counts[source] = referral_counts.get(source, 0) + 1

                    # Sort by effectiveness
                    sorted_referrals = sorted(referral_counts.items(), key=lambda x: x[1], reverse=True)
                    for source, count in sorted_referrals:
                        percentage = (count / total_patients * 100) if total_patients > 0 else 0
                        roi_indicator = "🟢" if percentage > 20 else "🟡" if percentage > 10 else "🔴"
                        st.write(f"{roi_indicator} {source}: {count} ({percentage:.1f}%)")

                with col_market2:
                    st.markdown("**Common Issues**")
                    issue_counts = {}
                    for p in patients:
                        if isinstance(p, dict) and p.get('issue'):
                            issue = p.get('issue', 'Unknown')
                            issue_counts[issue] = issue_counts.get(issue, 0) + 1

                    # Sort by frequency
                    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    for issue, count in sorted_issues:
                        percentage = (count / total_patients * 100) if total_patients > 0 else 0
                        st.write(f"• {issue}: {count} ({percentage:.1f}%)")

                # Business Intelligence Recommendations
                st.subheader("💡 Business Intelligence & Revenue Optimization")

                # Marketing recommendations
                if referral_counts:
                    top_referral = max(referral_counts.items(), key=lambda x: x[1])
                    st.success(f"🎯 **Top Performing Channel**: {top_referral[0]} ({top_referral[1]} patients)")
                    st.info("💰 **Recommendation**: Increase investment in this channel for better ROI")

                # Age group targeting
                if age_groups:
                    top_age_group = max(age_groups.items(), key=lambda x: x[1])
                    st.success(f"🎯 **Primary Target Demographic**: {top_age_group[0]} years ({top_age_group[1]} patients)")
                    st.info("📱 **Recommendation**: Focus marketing campaigns on this age group")

                # Geographic expansion
                if city_counts:
                    if len(city_counts) < 5:
                        st.warning("🗺️ **Geographic Opportunity**: Consider expanding to nearby cities")
                    else:
                        st.success("🌍 **Good Geographic Coverage**: Well-distributed patient base")

                # Revenue optimization
                st.markdown("**Revenue Enhancement Strategies:**")
                st.write("• 💰 Implement tiered consultation fees based on complexity")
                st.write("• 🔄 Focus on return patient retention programs")
                st.write("• 📱 Invest more in top-performing referral channels")
                st.write("• 🎯 Target marketing to primary demographic groups")
                st.write("• 👥 Develop referral incentive programs")

                # Inventory insights
                if medicines:
                    st.subheader("📊 Inventory Insights")
                    low_stock_medicines = [m for m in medicines if isinstance(m, dict) and int(m.get('quantity', 0)) < 10]
                    if low_stock_medicines:
                        st.warning(f"⚠️ **Low Stock Alert**: {len(low_stock_medicines)} medicines need restocking")
                        for med in low_stock_medicines[:3]:
                            st.write(f"• {med.get('name', 'Unknown')}: {med.get('quantity', 0)} units left")
                    else:
                        st.success("✅ **Inventory Status**: All medicines adequately stocked")

            else:
                st.info("📊 No patient data available for analytics. Start registering patients to see insights!")

                # Show sample insights for empty state
                st.markdown("### 💡 What you'll see with patient data:")
                st.write("• Patient demographics and age distribution")
                st.write("• Geographic coverage and expansion opportunities")
                st.write("• Marketing channel effectiveness")
                st.write("• Revenue optimization recommendations")
                st.write("• Return patient analysis")
                st.write("• Inventory management insights")

        except Exception as e:
            st.error(f"😞 Unable to load analytics: {str(e)}")
            st.info("Please ensure Google Sheets connection is working properly.")

            # Try alternative data loading
            try:
                st.info("🔄 Attempting alternative data loading...")
                from modules.google_sheets_manager import sheets_manager
                patients = sheets_manager.get_patients()
                medicines = sheets_manager.get_medicines()

                if patients:
                    st.success(f"✅ Loaded {len(patients)} patients via alternative method")
                    # Show basic analytics with alternative data
                    st.metric("Total Patients", len(patients))
                else:
                    st.warning("⚠️ No patient data available through any method")
            except Exception as e2:
                st.error(f"😞 Alternative loading also failed: {str(e2)}")

if __name__ == "__main__":
    main()