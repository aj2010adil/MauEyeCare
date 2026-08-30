#!/usr/bin/env python3
"""
MauEyeCare - Streamlined Professional Eye Care Hospital Management System
"""

import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime, timezone, timedelta
import json
import io
import base64
import urllib.parse

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Core imports
from modules.google_sheets_api import google_sheets_api
from modules.whatsapp_utils import send_via_whatsapp_web, format_clinical_whatsapp_message, format_followup_reminder_message
from modules.followup_manager import followup_manager, parse_relative_interval

def generate_qr_base64(data_url: str) -> str:
    """Generate base64 encoded PNG QR code for clean offline printing"""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=3,
            border=1,
        )
        qr.add_data(data_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return ""

@st.cache_data(ttl=60)
def get_sheet_data():
    """Load data from Google Sheets"""
    try:
        medicines = google_sheets_api.read_sheet("Medicines")
        spectacles = google_sheets_api.read_sheet("Spectacles")
        patients = google_sheets_api.read_sheet("Patients")
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
    
    st.title("🏥 Computer and AI assisted Refraction and Contact Lens Center - Mau Eye Care - Professional Eye Care Hospital")
    st.markdown("*Streamlined Hospital Management System*")

    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")

        if st.button("🔄 Sync Google Sheets"):
            with st.spinner("Syncing with Google Sheets..."):
                get_sheet_data.clear()
                medicines, spectacles, patients = get_sheet_data()
                st.success(f"✅ Synced: {len(medicines)} medicines, {len(spectacles)} spectacles, {len(patients)} patients!")

        # Google Sheets status
        test_result = google_sheets_api.test_connection()
        if test_result['success']:
            st.success("✅ Google Sheets Connected")
        else:
            st.error("❌ Google Sheets Not Connected")
            st.caption("Check credentials.json")

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


    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Patient Registration",
        "📤 Prescription Generator",
        "📊 Analytics",
        "📅 Follow-Up CRM"
    ])

    # --- Patient Registration Tab ---
    with tab1:
        if 'form_reset_counter' not in st.session_state:
            st.session_state.form_reset_counter = 0

        col_header1, col_header2 = st.columns([4, 1])
        with col_header1:
            st.header("👥 Patient Registration")
        with col_header2:
            if st.button("🆕 Start New Patient", use_container_width=True):
                st.session_state.form_reset_counter += 1
                keys_to_clear = [
                    'patient_name', 'patient_mobile', 'age', 'gender', 'address', 'city', 'state', 'pincode',
                    'occupation', 'referral_source', 'patient_issue', 'advice', 'new_patient',
                    'selected_medicines_list', 'medicine_details', 'selected_spectacles', 'spectacle_instructions',
                    'rx_table', 'consultation_fee', 'additional_charges', 'patient_complaint', 'patient_diagnosis',
                    'ipd', 'next_review'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

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
                selected_name = st.selectbox("Patient Name", name_options, key=f"name_dropdown_{st.session_state.form_reset_counter}")

                if selected_name == "-- Enter Custom Name --":
                    patient_name = st.text_input("Enter Full Name", placeholder="Type patient full name", key=f"custom_name_{st.session_state.form_reset_counter}")
                else:
                    patient_name = selected_name
                    st.info(f"Selected: {selected_name}")

                age = st.number_input("Age", min_value=0, max_value=120, value=30, key=f"age_{st.session_state.form_reset_counter}")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key=f"gender_{st.session_state.form_reset_counter}")

                # Address fields for demographics with defaults
                address = st.text_input("Address", placeholder="Street address", key=f"address_{st.session_state.form_reset_counter}")
                col_city, col_state = st.columns(2)
                with col_city:
                    city = st.text_input("City", value="Mubarkpur, Azamgarh", placeholder="City name", key=f"city_{st.session_state.form_reset_counter}")
                with col_state:
                    state = st.selectbox("State", [
                        "Uttar Pradesh", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
                        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
                        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
                        "Telangana", "Tripura", "Uttarakhand", "West Bengal", "Delhi"
                    ], key=f"state_{st.session_state.form_reset_counter}")
                pincode = st.text_input("Pincode", value="276404", placeholder="6-digit pincode", key=f"pincode_{st.session_state.form_reset_counter}")

            with col2:
                # Combined dropdown + custom input for mobile
                mobile_options = ["-- Enter Custom Mobile --"] + patient_mobiles[:15]
                selected_mobile = st.selectbox("Mobile Number", mobile_options, key=f"mobile_dropdown_{st.session_state.form_reset_counter}")

                if selected_mobile == "-- Enter Custom Mobile --":
                    contact = st.text_input("Enter Mobile Number", placeholder="Type mobile number", key=f"custom_mobile_{st.session_state.form_reset_counter}")
                else:
                    contact = selected_mobile
                    st.info(f"Selected: {selected_mobile}")

                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Headache", "Eye Strain", "Watering", "Itching", "Burning Sensation", "Foreign Body Sensation", "Light Sensitivity", "Discharge", "Swelling", "Routine Checkup", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options, key=f"issue_{st.session_state.form_reset_counter}")
                if patient_issue == "Other":
                    custom_issue = st.text_area("Specify Issue/Complaint", placeholder="Describe the patient's complaint in detail", key=f"custom_issue_{st.session_state.form_reset_counter}")
                    patient_issue = custom_issue if custom_issue else "Other"

                advice_options = [
                    "Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", 
                    "Glaucoma Screening", "Diabetic Eye Exam", "Contact Lens Consultation", 
                    "Vision Therapy", "Cataract Surgery (Phaco)", "Cataract Surgery (SICS)", 
                    "Cataract Surgery (ECCE)", "Follow-up in 1 month", "Follow-up in 3 months", 
                    "Follow-up in 6 months", "Refer to Specialist", "Eye Protection Advised", 
                    "Computer Vision Syndrome Care", "Other"
                ]
                advice = st.selectbox("Advice/Notes", advice_options, key=f"advice_{st.session_state.form_reset_counter}")
                if advice == "Other":
                    custom_advice = st.text_area("Specify Advice/Notes", placeholder="Enter detailed advice or notes for the patient", key=f"custom_advice_{st.session_state.form_reset_counter}")
                    advice = custom_advice if custom_advice else "Other"

                # Professional details for analytics
                occupation = st.text_input("Occupation", placeholder="Patient's occupation", key=f"occupation_{st.session_state.form_reset_counter}")
                referral_source = st.selectbox("How did you hear about us?", [
                    "", "Google Search", "Social Media", "Friend/Family", "Doctor Referral",
                    "Advertisement", "Walk-in", "Previous Patient", "Other"
                ], key=f"referral_{st.session_state.form_reset_counter}")

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
                            prescriptions = google_sheets_api.read_sheet("Prescriptions")
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
                success = google_sheets_api.add_patient(patient_record)
                if success:
                    if not is_duplicate:
                        st.info("✅ **New patient added to Google Sheets!**")
                    else:
                        st.info("✅ **Return visit recorded in Google Sheets!**")
                else:
                    st.warning("⚠️ Google Sheets sync failed.")

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
                # Ensure list exists in session state
                if 'selected_medicines_list' not in st.session_state:
                    st.session_state['selected_medicines_list'] = []

                def add_selected_medicine():
                    med = st.session_state.med_dropdown
                    if med:
                        if med not in st.session_state['selected_medicines_list']:
                            st.session_state['selected_medicines_list'].append(med)
                    st.session_state.med_dropdown = None

                def add_custom_medicine():
                    med = st.session_state.custom_med
                    if med:
                        if med not in st.session_state['selected_medicines_list']:
                            st.session_state['selected_medicines_list'].append(med)
                    st.session_state.custom_med = ""

                med_names = list(medicine_options.keys())

                selected_med_dropdown = st.selectbox(
                    "Select Medicine from Inventory:",
                    med_names,
                    index=None,
                    placeholder="-- Select Medicine --",
                    key="med_dropdown",
                    on_change=add_selected_medicine
                )

                # Allow custom medicine entry
                custom_medicine = st.text_input(
                    "Or enter custom medicine (Press Enter to add):",
                    placeholder="Type medicine name if not in dropdown",
                    key="custom_med",
                    on_change=add_custom_medicine
                )

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
                # Ensure list exists
                if 'selected_spectacles' not in st.session_state:
                    st.session_state['selected_spectacles'] = []

                def add_selected_spectacle():
                    spec = st.session_state.spec_dropdown
                    if spec:
                        if spec not in st.session_state['selected_spectacles']:
                            st.session_state['selected_spectacles'].append(spec)
                    st.session_state.spec_dropdown = None

                def add_custom_spectacle():
                    spec = st.session_state.custom_spec
                    if spec:
                        if spec not in st.session_state['selected_spectacles']:
                            st.session_state['selected_spectacles'].append(spec)
                    st.session_state.custom_spec = ""

                spec_names = list(spectacle_options.keys())

                st.selectbox(
                    "Select Spectacle from Inventory:",
                    spec_names,
                    index=None,
                    placeholder="-- Select Spectacle --",
                    key="spec_dropdown",
                    on_change=add_selected_spectacle
                )

                # Allow custom spectacle entry
                st.text_input(
                    "Or enter custom spectacle (Press Enter to add):",
                    placeholder="Type spectacle name if not in dropdown",
                    key="custom_spec",
                    on_change=add_custom_spectacle
                )

                # Show selected spectacles
                if st.session_state.get('selected_spectacles'):
                    st.markdown("**Selected Spectacles:**")
                    for i, spec_name in enumerate(st.session_state['selected_spectacles']):
                        col_s1, col_s2 = st.columns([4, 1])
                        with col_s1:
                            if spec_name in spectacle_options:
                                spec_data = spectacle_options[spec_name]
                                st.info(f"**{spec_name}** — ₹{spec_data.get('price', 0)} | Stock: {spec_data.get('quantity', 0)}")
                            else:
                                st.info(f"**{spec_name}** — Custom spectacle")
                        with col_s2:
                            if st.button("🗑️ Remove", key=f"remove_spec_{i}"):
                                st.session_state['selected_spectacles'].remove(spec_name)
                                st.rerun()

                if st.session_state.get('selected_spectacles'):
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
                vision_options = [
                    "", "6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60", 
                    "5/60", "4/60", "3/60", "2/60", "1/60",
                    "CF 6m", "CF 5m", "CF 4m", "CF 3m", "CF 2m", "CF 1m",
                    "CF (Counting Fingers)", "HM (Hand Movement)", "PL (Perception of Light)", "NPL (No Perception of Light)"
                ]
                od_vision = st.selectbox("OD Distance Vision", vision_options, key="od_distance_vision")
                near_vision_options = ["", "N6", "N8", "N10", "N12", "N18", "N24", "N36", "N48"]
                od_near_vision = st.selectbox("OD Near Vision", near_vision_options, key="od_near_vision")

            with col_vision2:
                st.markdown("**OS (Left Eye) Vision**")
                os_vision = st.selectbox("OS Distance Vision", vision_options, key="os_distance_vision")
                os_near_vision = st.selectbox("OS Near Vision", near_vision_options, key="os_near_vision")

            # Standard prescription values for suggestions
            # Sphere: -20.00 to +20.00 in 0.25 steps
            _sphere_neg = ["-{:.2f}".format(i/4) for i in range(1, 81)][::-1]
            _sphere_pos = ["+{:.2f}".format(i/4) for i in range(1, 81)]
            sphere_options = [""] + _sphere_neg + _sphere_pos
            # Cylinder: -8.00 to +8.00 in 0.25 steps
            _cyl_neg = ["-{:.2f}".format(i/4) for i in range(1, 33)][::-1]
            _cyl_pos = ["+{:.2f}".format(i/4) for i in range(1, 33)]
            cylinder_options = [""] + _cyl_neg + _cyl_pos
            axis_options = [""] + [str(i) for i in range(0, 185, 5)]
            near_add_options = ["", "+1.00", "+1.25", "+1.50", "+1.75", "+2.00", "+2.25", "+2.50", "+2.75", "+3.00", "+3.25", "+3.50", "+3.75", "+4.00"]

            # Get last prescription for returning patient
            last_rx = {}
            if not st.session_state.get('new_patient', True):
                try:
                    prescriptions = google_sheets_api.read_sheet("Prescriptions")
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

            # Optical Parameters & Clinical Follow-up
            st.markdown("#### 📏 Optical Parameters & Follow-up")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                ipd_input = st.text_input("Pupillary Distance (IPD in mm)", value=last_rx.get('IPD', ''), placeholder="e.g. 62 mm or 64 mm", key=f"ipd_{st.session_state.form_reset_counter}")
            with col_opt2:
                review_options = ["After 1 Week", "After 15 Days", "After 1 Month", "After 3 Months", "After 6 Months", "1 Year / Annual Checkup", "SOS / As Needed", "Custom"]
                selected_review = st.selectbox("Next Review / Follow-up", review_options, index=2, key=f"review_sel_{st.session_state.form_reset_counter}")
                if selected_review == "Custom":
                    custom_review = st.text_input("Enter Custom Review Note", placeholder="e.g. After 10 days with test report", key=f"review_cust_{st.session_state.form_reset_counter}")
                    next_review_val = custom_review if custom_review else "As advised"
                else:
                    next_review_val = selected_review

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
                "OS": {"Sphere": os_sphere, "Cylinder": os_cylinder, "Axis": os_axis, "ADD": os_add, "Vision": os_vision, "Near": os_near_vision},
                "IPD": ipd_input
            }
            st.session_state['rx_table'] = rx_table
            st.session_state['ipd'] = ipd_input
            st.session_state['next_review'] = next_review_val
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

                    if medicine_details:
                        with st.spinner("Updating medicine stock in Google Sheets..."):
                            for med_name, details in medicine_details.items():
                                if details.get('in_inventory', False):
                                    new_qty = details['current_stock'] - details['quantity']
                                    if new_qty < 0:
                                        new_qty = 0
                                    success = google_sheets_api.update_medicine_quantity(med_name, new_qty)
                                    if success:
                                        stock_updates.append(f"{med_name}: {details['current_stock']} → {new_qty}")
                                    else:
                                        stock_errors.append(f"{med_name}: Error updating")

                            if stock_updates:
                                st.success(f"✅ Stock updated: {', '.join(stock_updates)}")
                            if stock_errors:
                                st.error(f"❌ Stock update errors: {', '.join(stock_errors)}")

                    # Create compact single A4 prescription HTML
                    current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                    rx_table = st.session_state.get('rx_table', {})
                    od_data = rx_table.get('OD', {})
                    os_data = rx_table.get('OS', {})
                    ipd_val = st.session_state.get('ipd') or rx_table.get('IPD', '')
                    next_review_val = st.session_state.get('next_review') or 'After 1 Month'
                    patient_mobile = st.session_state.get('patient_mobile', '')
                    
                    # Generate Google Review QR Code (Base64 PNG for 100% offline printing)
                    google_review_url = "https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur"
                    review_qr_b64 = generate_qr_base64(google_review_url)
                    
                    qr_html_snippet = f"""
        <div class="qr-box">
            <img src="data:image/png;base64,{review_qr_b64}" width="50" height="50" alt="Review QR" style="display:block; margin:0 auto;" />
            <div style="font-size: 6.5pt; font-weight: bold; margin-top: 1px;">⭐ Scan to Review</div>
        </div>""" if review_qr_b64 else ""

                    ipd_html_snippet = f"""<div style="font-size: 9pt; margin-top: 4px; font-weight: bold;">• Pupillary Distance (IPD): {ipd_val} mm</div>""" if ipd_val else ""

                    prescription_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mau Eye Care Prescription - {patient_name}</title>
    <style>
        @page {{ margin: 0.3in; size: A4; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; font-size: 10pt; line-height: 1.2; color: #000; background: #fff; }}
        .no-print {{ text-align: center; margin-bottom: 8px; }}
        .print-btn {{ background: #000; color: #fff; border: 1.5px solid #000; padding: 6px 16px; font-size: 10pt; font-weight: bold; border-radius: 4px; cursor: pointer; }}
        .print-btn:hover {{ background: #333; }}
        .header {{ background: #fff; color: #000; padding: 8px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border: 2px solid #000; border-radius: 4px; }}
        .header-left, .header-right {{ flex: 1; }}
        .header-center {{ text-align: center; flex: 2; padding: 0 3px; }}
        .header-left {{ text-align: left; }}
        .header-right {{ text-align: right; }}
        .header h1 {{ margin: 0; font-size: 18pt; font-weight: 800; letter-spacing: 0.5px; color: #000; }}
        .header h2 {{ margin: 1px 0; font-size: 11pt; font-weight: bold; color: #000; }}
        .header p {{ margin: 1px 0; font-size: 8pt; color: #000; }}
        .urdu {{ font-family: 'Noto Nastaliq Urdu', 'Arial Unicode MS', sans-serif; }}
        .patient-info {{ background: #fff; border: 1.5px solid #000; border-left: 5px solid #000; padding: 8px 10px; margin: 6px 0; font-size: 10pt; border-radius: 3px; color: #000; }}
        .patient-info h3 {{ margin: 0 0 4px 0; font-size: 11pt; color: #000; border-bottom: 1px solid #000; padding-bottom: 2px; }}
        .patient-info p {{ margin: 2px 0; color: #000; }}
        .content {{ display: flex; gap: 8px; }}
        .left-section {{ flex: 1; }}
        .right-section {{ flex: 1; }}
        .section {{ background: #fff; padding: 8px; margin: 5px 0; border: 1.5px solid #000; border-radius: 3px; color: #000; }}
        .section h3 {{ margin: 0 0 6px 0; font-size: 11pt; color: #000; border-bottom: 1.5px solid #000; padding-bottom: 3px; }}
        .item {{ background: #fff; padding: 6px; margin: 3px 0; border-radius: 2px; border: 1px solid #000; border-left: 3px solid #000; font-size: 10pt; color: #000; }}
        .vision-table {{ width: 100%; border-collapse: collapse; margin: 6px 0; }}
        .vision-table th, .vision-table td {{ border: 1px solid #000; padding: 4px; text-align: center; font-size: 9.5pt; color: #000; }}
        .vision-table th {{ background: #f0f0f0; color: #000; font-weight: bold; }}
        .medicine-item {{ background: #fff; padding: 6px; margin: 3px 0; font-size: 9.5pt; border: 1px solid #666; border-left: 4px solid #000; border-radius: 2px; line-height: 1.3; color: #000; }}
        .spectacle-item {{ background: #fff; padding: 6px; margin: 3px 0; font-size: 9.5pt; border: 1px solid #666; border-left: 4px solid #000; border-radius: 2px; line-height: 1.3; color: #000; }}
        .review-box {{ margin-top: 6px; padding: 5px 8px; border: 1px solid #000; font-size: 9.5pt; background: #fff; }}
        .signature {{ text-align: right; margin-top: 8px; font-size: 10pt; font-weight: bold; padding-top: 8px; border-top: 1px dashed #000; color: #000; }}
        .footer-container {{ display: flex; justify-content: space-between; align-items: center; border-top: 1.5px solid #000; margin-top: 8px; padding-top: 4px; }}
        .footer-text {{ flex: 1; text-align: left; font-size: 8pt; color: #000; line-height: 1.2; }}
        .qr-box {{ text-align: center; margin-left: 8px; flex-shrink: 0; }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="print-btn" onclick="window.print()">🖨️ Click to Print Prescription (Ctrl + P)</button>
    </div>

    <div class="header">
        <div class="header-left">
            <h2>Dr. Danish</h2>
            <p>B.Sc. Optometry</p>
            <p>Optometrist & Eye Specialist</p>
            <p>Reg. No.: UPS 2908</p>
        </div>
        <div class="header-center">
            <p style="font-size: 8pt; margin: 0.5px 0;">Computer and AI assisted Refraction and Contact Lens Center</p>
            <h1>Mau Eye Care</h1>
            <p style="margin: 1px 0; font-size: 8pt;">Pura Khizir,(Near Mubarakpur Marraige Hall,Nai Pani ki tanki), Roadways Mubarakpur ,Azamgarh (U.P.)</p>
            <p style="margin: 1px 0; font-size: 8pt;"> Mon-Sat: 10 AM-5 PM| Sunday Closed |</p> 
            <p style="margin: 1px 0; font-size: 8pt;"> 📞9235647410 |Appointment:8299461251 |📧 mau.eye.care.404@gmail.com</p>
        </div>
        <div class="header-right">
            <h2 class="urdu" style="font-size: 18pt;">ڈاکٹر دانش</h2>
            <p class="urdu" style="font-size: 12pt;">بی ایس سی آپٹومیٹری</p>
            <p class="urdu" style="font-size: 12pt;">آنکھوں کے ماہر</p>
        </div>
    </div>

    <div class="patient-info">
        <h3>👤 Patient Information</h3>
        <p><strong>Name:</strong> {patient_name} | <strong>Age:</strong> {st.session_state.get('age', 'N/A')} | <strong>Gender:</strong> {st.session_state.get('gender', 'N/A')} | <strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')} | <strong>Date:</strong> {current_time.strftime('%d/%m/%Y')}</p>
        <p><strong>Address:</strong> {st.session_state.get('address', '')}, {st.session_state.get('city', '')}, {st.session_state.get('state', '')} - {st.session_state.get('pincode', '')}</p>
        <p><strong>Complaint:</strong> {st.session_state.get('patient_complaint') or st.session_state.get('patient_issue') or 'N/A'}</p>
        <p><strong>Advice:</strong> {st.session_state.get('advice') or 'N/A'}</p>
        <p><strong>Diagnosis:</strong> {st.session_state.get('patient_diagnosis', 'N/A')}</p>
    </div>

    <div class="content">
        <div class="left-section">
            <div class="section">
                <h3>👁️ Eye Prescription</h3>
                <table class="vision-table">
                    <tr>
                        <th>Eye</th>
                        <th>SPH</th>
                        <th>CYL</th>
                        <th>AXIS</th>
                        <th>ADD</th>
                    </tr>
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
                {ipd_html_snippet}
                
                <h3 style="margin-top: 8px;">👁️ Vision Testing</h3>
                <table class="vision-table">
                    <tr>
                        <th>Eye</th>
                        <th>Distance</th>
                        <th>Near</th>
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

                    # Add spectacles section
                    if selected_spectacles:
                        prescription_html += """
            <div class="section">
                <h3>👓 Recommended Spectacles</h3>"""

                        for spec_name in selected_spectacles:
                            prescription_html += f"""
                <div class="spectacle-item">
                    <strong>{spec_name}</strong>
                </div>"""

                        # Add spectacle instructions
                        spectacle_instructions = st.session_state.get('spectacle_instructions', '')
                        if spectacle_instructions:
                            prescription_html += f"""
                <div class="spectacle-item">
                    <strong>Care Instructions:</strong><br>
                    {spectacle_instructions.replace(chr(10), '<br>').replace('•', '&bull;')}
                </div>"""

                        prescription_html += """
            </div>"""

                    # Close left section and start right section
                    prescription_html += """
        </div>
        <div class="right-section">"""

                    # Add medicines section
                    if medicine_details:
                        prescription_html += """
            <div class="section">
                <h3>💊 Prescribed Medicines</h3>"""

                        for med_name, details in medicine_details.items():
                            prescription_html += f"""
                <div class="medicine-item">
                    <strong>{med_name}</strong><br>
                    Qty: {details['quantity']} | {details.get('dosage', 'As directed')}<br>
                    {details.get('timing', 'As directed')}
                </div>"""

                        prescription_html += """
            </div>"""

                    # Add follow-up review note
                    prescription_html += f"""
            <div class="review-box">
                🗓️ <strong>Next Review / Follow-up:</strong> {next_review_val}
            </div>"""

                    # Close content and add signature/footer
                    prescription_html += f"""
        </div>
    </div>

    <div class="signature">
        <p style="margin: 4px 0; font-size: 9pt;">Doctor Signature: ___________________________</p>
    </div>
    
    <div class="footer-container">
        <div class="footer-text">
            <p style="margin: 1px 0;"><strong>Services:</strong> Refraction • Glasses • Contact Lens • Eye Screening • Treatment</p>
            <p style="margin: 2px 0; font-size: 7.5pt;">⭐ <em>Rate your experience on Google: Search <strong>Mau Eye Care Mubarakpur</strong></em></p>
        </div>
        {qr_html_snippet}
    </div>
</body>
</html>"""

                    # Create detailed receipt HTML (monochrome optimized with Print & Review QR)
                    receipt_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mau Eye Care Receipt - {patient_name}</title>
    <style>
        @page {{ margin: 0.3in; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 8px; font-size: 10pt; line-height: 1.3; color: #000; background: #fff; }}
        .no-print {{ text-align: center; margin-bottom: 8px; }}
        .print-btn {{ background: #000; color: #fff; border: 1.5px solid #000; padding: 6px 14px; font-size: 9.5pt; font-weight: bold; border-radius: 4px; cursor: pointer; }}
        .header {{ text-align: center; border: 1.5px solid #000; padding: 8px; margin-bottom: 10px; border-radius: 3px; }}
        .header h2 {{ margin: 2px 0; font-size: 13pt; color: #000; }}
        .header p {{ margin: 2px 0; font-size: 8.5pt; color: #000; }}
        h3 {{ margin: 6px 0 4px 0; font-size: 10.5pt; color: #000; border-bottom: 1px solid #000; padding-bottom: 2px; }}
        .receipt-item {{ background: #fff; padding: 6px; margin: 4px 0; border: 1px solid #666; border-left: 4px solid #000; font-size: 9.5pt; border-radius: 2px; color: #000; }}
        .receipt-item strong {{ font-size: 10pt; }}
        .receipt-item br + * {{ margin-top: 2px; }}
        .total {{ border: 2px solid #000; padding: 8px; font-weight: bold; text-align: center; margin: 8px 0; border-radius: 3px; background: #f0f0f0; }}
        .total h2 {{ margin: 4px 0; font-size: 13pt; color: #000; }}
        .footer-container {{ display: flex; justify-content: space-between; align-items: center; border-top: 1.5px solid #000; margin-top: 10px; padding-top: 4px; }}
        .footer-text {{ flex: 1; text-align: left; font-size: 8pt; color: #000; }}
        .qr-box {{ text-align: center; margin-left: 8px; flex-shrink: 0; }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="print-btn" onclick="window.print()">🖨️ Click to Print Receipt</button>
    </div>

    <div class="header">
        <h2>Mau Eye Care - Official Receipt</h2>
        <p><strong>Patient:</strong> {patient_name} | <strong>Mobile:</strong> {st.session_state.get('patient_mobile', 'N/A')} | <strong>Date:</strong> {current_time.strftime('%d/%m/%Y %I:%M %p')}</p>
    </div>
    
    <h3>Medicine Details:</h3>"""

                    total_med_cost = 0
                    if medicine_details:
                        for med_name, details in medicine_details.items():
                            total_med_cost += details['total_cost']
                            receipt_html += f"""
    <div class="receipt-item">
        <strong>{med_name}</strong> • Qty: {details['quantity']} @ ₹{details['price']} = ₹{details['total_cost']}<br>
        <span style="font-size: 9pt;">{details.get('dosage', 'As directed')} • {details.get('timing', 'As directed')}</span>
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

    <div class="footer-container">
        <div class="footer-text">
            <p style="margin: 1px 0;"><strong>Thank you for choosing Mau Eye Care!</strong></p>
            <p style="margin: 2px 0; font-size: 7.5pt;">⭐ <em>Rate your experience on Google: Search <strong>Mau Eye Care Mubarakpur</strong></em></p>
        </div>
        {qr_html_snippet}
    </div>
</body>
</html>"""

                    # Prepare Clinical WhatsApp Message
                    whatsapp_msg = format_clinical_whatsapp_message(
                        patient_name=patient_name,
                        date_str=current_time.strftime('%d/%m/%Y'),
                        rx_table=rx_table,
                        ipd=ipd_val,
                        spectacles=selected_spectacles,
                        medicines=medicine_details,
                        advice=st.session_state.get('advice'),
                        next_review=next_review_val
                    )
                    clean_phone = patient_mobile.replace("+", "").replace(" ", "").replace("-", "") if patient_mobile else ""
                    encoded_msg = urllib.parse.quote(whatsapp_msg)
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}" if clean_phone else f"https://wa.me/?text={encoded_msg}"

                    # Download & Sharing action buttons
                    timestamp = current_time.strftime("%Y%m%d_%H%M")
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    
                    with col_dl1:
                        st.download_button(
                            "💾 Download Prescription",
                            data=prescription_html.encode('utf-8'),
                            file_name=f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        st.download_button(
                            "💾 Download Receipt",
                            data=receipt_html.encode('utf-8'),
                            file_name=f"Receipt_{patient_name.replace(' ', '_')}_{timestamp}.html",
                            mime="text/html",
                            type="secondary",
                            use_container_width=True
                        )

                    with col_dl3:
                        st.link_button(
                            "📲 Share on WhatsApp",
                            whatsapp_url,
                            type="primary",
                            use_container_width=True
                        )

                    with st.expander("💬 View / Copy WhatsApp Prescription Message"):
                        st.text_area("WhatsApp Clinical Summary", whatsapp_msg, height=160)

                    st.success("✅ Prescription & Receipt generated successfully!")

                    # Automatically log follow-up in CRM
                    try:
                        followup_manager.add_followup(
                            patient_name=patient_name,
                            mobile=patient_mobile,
                            consultation_date=current_time.strftime('%Y-%m-%d'),
                            review_interval=next_review_val,
                            diagnosis=st.session_state.get('patient_diagnosis') or st.session_state.get('patient_complaint') or '',
                            advice=st.session_state.get('advice') or ''
                        )
                    except Exception:
                        pass

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
                            'selected_spectacles', 'medicine_details', 'selected_medicines_list', 'rx_table', 'prescription_generated',
                            'patient_complaint', 'patient_diagnosis', 'complaint', 'diagnosis', 'od_distance_vision', 'od_near_vision',
                            'os_distance_vision', 'os_near_vision', 'spectacle_instructions', 'new_patient',
                            'ipd', 'next_review',
                            'name_dropdown', 'custom_name', 'mobile_dropdown', 'custom_mobile', 'custom_issue', 'custom_advice'
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
                test_result = google_sheets_api.test_connection()
                if not test_result['success']:
                    st.error("❌ Google Sheets not authenticated. Please check credentials.json.")
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

    # --- Follow-Up CRM Tab ---
    with tab4:
        st.header("📅 Patient Follow-Up & Recall CRM")
        st.markdown("*Automated review tracking, patient recall scheduling, and 1-click WhatsApp reminders.*")

        # Automatically sync past patient records into CRM queue if needed
        try:
            _, _, existing_patients_list = get_sheet_data()
            if existing_patients_list:
                followup_manager.auto_import_from_patients(existing_patients_list)
        except Exception:
            pass

        # Top summary KPIs
        categorized = followup_manager.get_categorized_followups()
        
        col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
        with col_kpi1:
            st.metric("🔴 Overdue", len(categorized['overdue']))
        with col_kpi2:
            st.metric("🟡 Due Today", len(categorized['due_today']))
        with col_kpi3:
            st.metric("🟢 This Week", len(categorized['upcoming_week']))
        with col_kpi4:
            st.metric("🔵 Next 30 Days", len(categorized['upcoming_month']))
        with col_kpi5:
            st.metric("✅ Completed", len(categorized['completed']))

        st.markdown("---")

        # Filters and Search
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search by Patient Name or Mobile", placeholder="Type patient name or mobile number...").strip().lower()
        with col_f2:
            queue_filter = st.selectbox(
                "Filter Queue",
                [
                    "Due Today (🟡)",
                    "Overdue (🔴)",
                    "Upcoming This Week (🟢)",
                    "Upcoming Next 30 Days (🔵)",
                    "All Active Follow-ups",
                    "Completed / Visited (✅)",
                    "SOS / As Needed"
                ]
            )
        with col_f3:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh CRM Queue", use_container_width=True):
                st.rerun()

        # Determine which list to show
        if "Due Today" in queue_filter:
            display_list = categorized['due_today']
        elif "Overdue" in queue_filter:
            display_list = categorized['overdue']
        elif "This Week" in queue_filter:
            display_list = categorized['upcoming_week']
        elif "Next 30 Days" in queue_filter:
            display_list = categorized['upcoming_month']
        elif "Completed" in queue_filter:
            display_list = categorized['completed']
        elif "SOS" in queue_filter:
            display_list = categorized['sos']
        else:
            display_list = categorized['overdue'] + categorized['due_today'] + categorized['upcoming_week'] + categorized['upcoming_month']

        # Apply search query
        if search_query:
            display_list = [
                item for item in display_list 
                if search_query in item.get('patient_name', '').lower() or search_query in item.get('mobile', '').lower()
            ]

        # Display Queue Count
        st.subheader(f"📋 Follow-Up Queue ({len(display_list)} Patients)")

        if not display_list:
            st.info("🎉 No patients currently in this follow-up category!")
        else:
            for idx, item in enumerate(display_list):
                fu_id = item.get('id', f'fu_{idx}')
                p_name = item.get('patient_name', 'Unknown')
                p_mobile = item.get('mobile', '')
                target_date_str = item.get('target_date', '')
                consult_date_str = item.get('consultation_date', '')
                status = item.get('status', 'Pending')
                reminders_count = item.get('reminders_count', 0)
                diff_days = item.get('diff_days', 0)
                diagnosis = item.get('diagnosis', 'Routine Eye Review')
                advice = item.get('advice', '')
                review_interval = item.get('review_interval', 'Routine Review')

                # Determine badge styling
                if status == "Completed":
                    badge = "✅ COMPLETED / VISITED"
                elif diff_days < 0:
                    badge = f"🔴 OVERDUE BY {-diff_days} DAYS"
                elif diff_days == 0:
                    badge = "🟡 DUE TODAY"
                else:
                    badge = f"🟢 DUE IN {diff_days} DAYS"

                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 2])
                    
                    with col_info:
                        st.markdown(f"### 👤 **{p_name}** &nbsp;&nbsp; `{badge}`")
                        info_cols = st.columns(3)
                        with info_cols[0]:
                            st.write(f"📞 **Mobile:** {p_mobile or 'N/A'}")
                        with info_cols[1]:
                            st.write(f"📅 **Consultation:** {consult_date_str}")
                        with info_cols[2]:
                            st.write(f"🗓️ **Scheduled:** {target_date_str or 'SOS'}")
                            
                        if diagnosis or advice:
                            st.caption(f"🩺 **Clinical Note:** {diagnosis} | *Advice:* {advice}")
                        if reminders_count > 0:
                            st.caption(f"📲 *Reminders Sent:* {reminders_count} times (Last: {item.get('last_reminder_sent_at', '')})")

                    with col_actions:
                        st.markdown("**Actions:**")
                        action_col1, action_col2 = st.columns(2)
                        
                        # WhatsApp Reminder Button
                        reminder_text = format_followup_reminder_message(
                            patient_name=p_name,
                            target_date_str=target_date_str,
                            reason=f"{diagnosis} (Interval: {review_interval})"
                        )
                        clean_mobile = p_mobile.replace("+", "").replace(" ", "").replace("-", "") if p_mobile else ""
                        wa_url = send_via_whatsapp_web(clean_mobile, reminder_text) if clean_mobile else f"https://wa.me/?text={urllib.parse.quote(reminder_text)}"
                        
                        with action_col1:
                            st.link_button("📲 Send Reminder", wa_url, use_container_width=True, type="primary")
                            if st.button("📝 Log Sent", key=f"log_sent_{fu_id}", use_container_width=True):
                                followup_manager.mark_reminder_sent(fu_id)
                                st.success("✅ Logged!")
                                st.rerun()

                        with action_col2:
                            if status != "Completed":
                                if st.button("✅ Mark Visited", key=f"done_{fu_id}", use_container_width=True):
                                    followup_manager.mark_completed(fu_id)
                                    st.success(f"✅ Marked {p_name} as Visited!")
                                    st.rerun()
                            
                            # Reschedule popover
                            with st.popover("🗓️ Reschedule"):
                                resched_choice = st.selectbox(
                                    "New Target Interval",
                                    ["After 1 Week", "After 15 Days", "After 1 Month", "After 3 Months", "After 6 Months", "1 Year"],
                                    key=f"resched_sel_{fu_id}"
                                )
                                if st.button("Confirm Reschedule", key=f"resched_btn_{fu_id}"):
                                    followup_manager.reschedule(fu_id, resched_choice)
                                    st.success("🗓️ Rescheduled!")
                                    st.rerun()

        # Manual Follow-Up Creation Form
        st.markdown("---")
        with st.expander("➕ Schedule Manual Follow-Up for Walk-in Patient"):
            with st.form("manual_followup_form"):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_name = st.text_input("Patient Name*", placeholder="Full Name")
                    m_mobile = st.text_input("Mobile Number*", placeholder="10-digit mobile")
                    m_diag = st.text_input("Diagnosis / Complaint", placeholder="e.g. Dry eye review, Refraction change")
                with col_m2:
                    m_interval = st.selectbox(
                        "Review Interval",
                        ["After 1 Week", "After 15 Days", "After 1 Month", "After 3 Months", "After 6 Months", "1 Year / Annual Checkup"]
                    )
                    m_advice = st.text_area("Doctor's Advice / Notes", placeholder="Special instructions for the patient")
                    
                if st.form_submit_button("➕ Schedule Follow-Up", type="primary"):
                    if m_name:
                        followup_manager.add_followup(
                            patient_name=m_name,
                            mobile=m_mobile,
                            consultation_date=datetime.now().strftime('%Y-%m-%d'),
                            review_interval=m_interval,
                            diagnosis=m_diag,
                            advice=m_advice
                        )
                        st.success(f"✅ Follow-up scheduled for {m_name} ({m_interval})!")
                        st.rerun()
                    else:
                        st.error("Please enter patient name.")

if __name__ == "__main__":
    main()
