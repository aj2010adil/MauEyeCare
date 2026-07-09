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


@st.cache_data
def get_frequency_ranked_data():
    """Return frequency-ranked suggestion lists for all dropdowns.

    Ranking logic:
    - Patient names  : ranked by visit count (same name = return visit = higher rank)
    - Patient mobiles: ranked alongside patient-name frequency
    - Medicines      : ranked by usage proxy (original_stock - current_stock desc),
                       then alphabetically so zero-usage items don't crowd the top
    - Spectacles     : same as medicines
    """
    try:
        medicines, spectacles, patients = get_sheet_data()
    except Exception:
        return [], [], [], {}, {}

    # --- Patient names ranked by visit frequency ---
    from collections import Counter
    name_counter = Counter()
    mobile_map = {}   # name -> latest mobile
    for p in patients:
        if not isinstance(p, dict):
            continue
        name = p.get('name', '').strip()
        mobile = p.get('mobile', '').strip()
        if name:
            name_counter[name] += 1
            if mobile:
                mobile_map[name] = mobile  # keep latest mobile for each name

    # Names sorted most-visited first
    ranked_names = [name for name, _ in name_counter.most_common()]

    # Mobiles ordered to match name frequency order, then any extras
    seen_mobiles = set()
    ranked_mobiles = []
    for name in ranked_names:
        mob = mobile_map.get(name, '')
        if mob and mob not in seen_mobiles:
            ranked_mobiles.append(mob)
            seen_mobiles.add(mob)
    # Add remaining mobiles not linked to a ranked name
    for p in patients:
        if isinstance(p, dict):
            mob = p.get('mobile', '').strip()
            if mob and mob not in seen_mobiles:
                ranked_mobiles.append(mob)
                seen_mobiles.add(mob)

    # --- Medicines ranked by usage (original_stock - current_stock proxy) ---
    def med_sort_key(m):
        try:
            qty = int(m.get('quantity', 0))
            # Lower current stock → more has been dispensed → higher rank
            # We negate so that lower stock sorts first (most used)
            return (-1 * (1000 - qty), m.get('name', '').lower())
        except Exception:
            return (0, m.get('name', '').lower())

    ranked_meds = [
        m['name'] for m in sorted(
            [m for m in medicines if isinstance(m, dict) and 'name' in m],
            key=med_sort_key
        )
    ]

    # --- Spectacles ranked the same way ---
    def spec_sort_key(s):
        try:
            qty = int(s.get('quantity', 0))
            return (-1 * (1000 - qty), s.get('name', '').lower())
        except Exception:
            return (0, s.get('name', '').lower())

    ranked_specs = [
        s['name'] for s in sorted(
            [s for s in spectacles if isinstance(s, dict) and 'name' in s],
            key=spec_sort_key
        )
    ]

    return ranked_names, ranked_mobiles, ranked_meds, ranked_specs


def smart_word_filter(query: str, candidates: list, max_results: int = 40) -> list:
    """Professional word-boundary search engine (VS Code / Spotlight style).

    Scoring tiers (higher wins — first match in list wins ties):
      900 : exact match
      800 : starts-with full query
      700 : all query chars match word-initials in order  (RS → Rahul Sharma)
      600 : first char matches first word; rest match subsequent words' starts or substrings
      500 : any single word starts with the full query
      400 : substring anywhere in the full text
      200 : fuzzy subsequence (all chars appear in order anywhere)
        0 : no match

    All matching is case-insensitive.
    Results are returned sorted best-first, then frequency order preserved.
    """
    if not query or not query.strip():
        return candidates[:max_results]

    q = query.strip().lower()
    scored = []

    for idx, item in enumerate(candidates):
        text = item.lower()
        words = text.split()
        q_chars = list(q)
        score = 0

        if text == q:
            score = 900
        elif text.startswith(q):
            score = 800
        elif len(q_chars) <= len(words) and all(
            words[i].startswith(q_chars[i]) for i in range(len(q_chars))
        ):
            # Word-initials match: RS → Rahul Sharma
            score = 700
        elif words and words[0].startswith(q_chars[0]):
            # First char matches first word; try matching rest against subsequent words
            remaining_chars = q_chars[1:]
            remaining_words = words[1:]
            if not remaining_chars:
                score = 600
            else:
                match_ok = True
                rem_w_idx = 0
                for rc in remaining_chars:
                    found = False
                    # Try word-initial first
                    while rem_w_idx < len(remaining_words):
                        if remaining_words[rem_w_idx].startswith(rc):
                            rem_w_idx += 1
                            found = True
                            break
                        # Try substring in this word
                        if rc in remaining_words[rem_w_idx]:
                            found = True
                            break
                        rem_w_idx += 1
                    if not found:
                        match_ok = False
                        break
                if match_ok:
                    score = 600
        
        if score == 0 and any(w.startswith(q) for w in words):
            score = 500

        if score == 0 and q in text:
            score = 400

        if score == 0:
            # Fuzzy subsequence
            pos = 0
            fuzzy_ok = True
            for ch in q:
                nxt = text.find(ch, pos)
                if nxt == -1:
                    fuzzy_ok = False
                    break
                pos = nxt + 1
            if fuzzy_ok:
                score = 200

        if score > 0:
            # Use negative idx so frequency order (earlier in list) breaks ties
            scored.append((-score, idx, item))

    scored.sort()
    return [item for _, _, item in scored[:max_results]]

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

        # Get existing patients for suggestions — frequency-ranked
        try:
            ranked_names, ranked_mobiles, _, _ = get_frequency_ranked_data()
            if not ranked_names:
                _, _, existing_patients_raw = get_sheet_data()
                ranked_names = list(dict.fromkeys(
                    p.get('name', '') for p in existing_patients_raw
                    if isinstance(p, dict) and p.get('name')
                ))
            if not ranked_mobiles:
                _, _, existing_patients_raw = get_sheet_data()
                ranked_mobiles = list(dict.fromkeys(
                    p.get('mobile', '') for p in existing_patients_raw
                    if isinstance(p, dict) and p.get('mobile')
                ))
        except Exception:
            ranked_names, ranked_mobiles = [], []
        existing_patients = []
        try:
            _, _, existing_patients = get_sheet_data()
        except Exception:
            existing_patients = []

        # ── Quick Patient Lookup (always visible, outside form for live smart-search) ──
        with st.expander("🔍 Find Existing Patient (smart search)", expanded=False):
            if not ranked_names:
                st.info("🔗 Connect Google Sheets to enable patient lookup. New patients: fill the form below.")
            else:
                st.caption("Type initials or any part of the name/mobile — e.g. 'RS' finds 'Rahul Sharma'")
                lcol, rcol = st.columns(2)

                with lcol:
                    name_q = st.text_input(
                        "Search by Name:",
                        placeholder="Type name or initials…",
                        key="lookup_name_q"
                    )
                    filtered_names = smart_word_filter(name_q, ranked_names) if name_q else ranked_names[:30]
                    if filtered_names:
                        chosen_name = st.selectbox(
                            f"Matching names ({len(filtered_names)} found):",
                            filtered_names,
                            index=None,
                            placeholder="Select to pre-fill form…",
                            key="lookup_name_select"
                        )
                    else:
                        st.info("No names match — will register as new patient.")
                        chosen_name = None

                with rcol:
                    mob_q = st.text_input(
                        "Search by Mobile:",
                        placeholder="Type mobile digits…",
                        key="lookup_mob_q"
                    )
                    filtered_mobs = smart_word_filter(mob_q, ranked_mobiles) if mob_q else ranked_mobiles[:30]
                    if filtered_mobs:
                        chosen_mob = st.selectbox(
                            f"Matching mobiles ({len(filtered_mobs)} found):",
                            filtered_mobs,
                            index=None,
                            placeholder="Select to pre-fill form…",
                            key="lookup_mob_select"
                        )
                    else:
                        st.info("No mobiles match.")
                        chosen_mob = None

                if st.button("✅ Pre-fill form with selected patient", key="prefill_btn"):
                    if chosen_name:
                        st.session_state['prefill_name'] = chosen_name
                    if chosen_mob:
                        st.session_state['prefill_mob'] = chosen_mob
                    # Auto-fill age/gender from existing records
                    for p in existing_patients:
                        if isinstance(p, dict) and p.get('name', '').strip() == (chosen_name or '').strip():
                            st.session_state['prefill_age'] = p.get('age', 30)
                            st.session_state['prefill_gender'] = p.get('gender', 'Male')
                            break
                    st.success(f"✅ Form pre-filled with: {chosen_name or ''} / {chosen_mob or ''}")
                    st.rerun()

        with st.form("patient_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Name field: prefill_name (from lookup) → patient_name (current session) → blank
                _default_name = (
                    st.session_state.get('prefill_name')
                    or st.session_state.get('patient_name', '')
                )
                patient_name = st.text_input(
                    "Patient Name",
                    value=_default_name,
                    placeholder="Full patient name",
                    key="form_patient_name"
                )

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
                # Mobile field: prefill_mob (from lookup) → patient_mobile (current session) → blank
                _default_mob = (
                    st.session_state.get('prefill_mob')
                    or st.session_state.get('patient_mobile', '')
                )
                contact = st.text_input(
                    "Mobile Number",
                    value=_default_mob,
                    placeholder="10-digit mobile number",
                    key="form_mobile"
                )

                issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Floaters", "Night Blindness", "Headache", "Eye Strain", "Watering", "Itching", "Burning Sensation", "Foreign Body Sensation", "Light Sensitivity", "Discharge", "Swelling", "Routine Checkup", "Other"]
                patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
                if patient_issue == "Other":
                    custom_issue = st.text_area("Specify Issue/Complaint", placeholder="Describe the patient's complaint in detail", key="custom_issue")
                    patient_issue = custom_issue if custom_issue else "Other"

                advice_options = [
                    "Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", 
                    "Glaucoma Screening", "Diabetic Eye Exam", "Contact Lens Consultation", 
                    "Vision Therapy", "Cataract Surgery (Phaco)", "Cataract Surgery (SICS)", 
                    "Cataract Surgery (ECCE)", "Follow-up in 1 month", "Follow-up in 3 months", 
                    "Follow-up in 6 months", "Refer to Specialist", "Eye Protection Advised", 
                    "Computer Vision Syndrome Care", "Other"
                ]
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

            # Load medicines — frequency ranked
            try:
                medicines, _, _ = get_sheet_data()
                medicine_options = {med['name']: med for med in medicines if isinstance(med, dict) and 'name' in med}
                _, _, ranked_med_names, _ = get_frequency_ranked_data()
                med_names = [n for n in ranked_med_names if n in medicine_options]
                for n in medicine_options:
                    if n not in med_names:
                        med_names.append(n)
            except Exception:
                medicine_options = {}
                med_names = []

            # ── Medicine selection (always visible) ─────────────────────────────────
            if 'med_selector_key' not in st.session_state:
                st.session_state['med_selector_key'] = 0
            _sel_key = st.session_state['med_selector_key']

            selected_med_dropdown = None  # default: no inventory selection

            if medicine_options and med_names:
                # Inventory connected — show smart search + filtered dropdown
                st.caption("💡 Smart search: type initials like 'EC' for 'EyeCare', or any word part — case-insensitive")
                med_search_q = st.text_input(
                    "🔍 Search Medicine:",
                    placeholder="e.g. 'eye', 'EC' (Eye Care), 'sod' (Sodium Chloride)…",
                    key=f"med_search_{_sel_key}"
                )
                filtered_med_names = smart_word_filter(med_search_q, med_names) if med_search_q else med_names
                if filtered_med_names:
                    selected_med_dropdown = st.selectbox(
                        f"Select from inventory ({len(filtered_med_names)} match{'es' if len(filtered_med_names) != 1 else ''}):",
                        filtered_med_names,
                        index=None,
                        placeholder="Choose from filtered results…",
                        key=f"med_dropdown_{_sel_key}"
                    )
                else:
                    st.warning("⚠️ No inventory medicines match your search.")
            else:
                st.info("📦 Inventory not connected — enter medicine name manually below.")

            # Custom entry is ALWAYS available
            custom_medicine = st.text_input(
                "Or enter custom medicine:" if medicine_options else "Enter medicine name:",
                placeholder="Type medicine name if not in inventory",
                key=f"custom_med_{_sel_key}"
            )

            # Determine final medicine selection
            if selected_med_dropdown is not None:
                final_medicine = selected_med_dropdown
            elif custom_medicine:
                final_medicine = custom_medicine
            else:
                final_medicine = None

            if final_medicine:
                if 'selected_medicines_list' not in st.session_state:
                    st.session_state['selected_medicines_list'] = []

                if st.button(f"➕ Add {final_medicine}", key=f"add_med_btn_{_sel_key}"):
                    if final_medicine not in st.session_state['selected_medicines_list']:
                        st.session_state['selected_medicines_list'].append(final_medicine)
                        st.success(f"✅ {final_medicine} added to prescription")
                    else:
                        st.warning(f"⚠️ {final_medicine} is already in the list")
                    # Reset widgets by bumping the counter key
                    st.session_state['med_selector_key'] += 1
                    st.rerun()

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
                _, _, _, ranked_spec_names = get_frequency_ranked_data()
                # Preserve rank order, only include items in inventory
                spec_names = [n for n in ranked_spec_names if n in spectacle_options]
                for n in spectacle_options:
                    if n not in spec_names:
                        spec_names.append(n)
            except Exception:
                spectacle_options = {}
                spec_names = []

            # ── Spectacle selection (always visible) ─────────────────────────────
            if 'spec_selector_key' not in st.session_state:
                st.session_state['spec_selector_key'] = 0
            _spec_key = st.session_state['spec_selector_key']

            selected_spec_dropdown = None  # default: no inventory selection

            if spectacle_options and spec_names:
                # Inventory connected — show smart search + filtered dropdown
                st.caption("💡 Smart search: type initials or any word part — case-insensitive, most-used shown first")
                spec_search_q = st.text_input(
                    "🔍 Search Spectacle:",
                    placeholder="e.g. 'pro', 'PC' (Polycarbonate), 'anti' (Anti-reflective)…",
                    key=f"spec_search_{_spec_key}"
                )
                filtered_spec_names = smart_word_filter(spec_search_q, spec_names) if spec_search_q else spec_names
                if filtered_spec_names:
                    selected_spec_dropdown = st.selectbox(
                        f"Select from inventory ({len(filtered_spec_names)} match{'es' if len(filtered_spec_names) != 1 else ''}):",
                        filtered_spec_names,
                        index=None,
                        placeholder="Choose from filtered results…",
                        key=f"spec_dropdown_{_spec_key}"
                    )
                    if selected_spec_dropdown and selected_spec_dropdown in spectacle_options:
                        spec_data = spectacle_options[selected_spec_dropdown]
                        st.info(f"Price: ₹{spec_data.get('price', 0)} | Stock: {spec_data.get('quantity', 0)}")
                else:
                    st.warning("⚠️ No inventory spectacles match your search.")
            else:
                st.info("📦 Inventory not connected — enter spectacle name manually below.")

            # Custom entry is ALWAYS available
            custom_spectacle = st.text_input(
                "Or enter custom spectacle:" if spectacle_options else "Enter spectacle name:",
                placeholder="Type spectacle name if not in inventory",
                key=f"custom_spec_{_spec_key}"
            )
            if custom_spectacle and not selected_spec_dropdown:
                st.info("📝 Custom spectacle — price will be determined manually")

            # Determine final spectacle selection
            if selected_spec_dropdown is not None:
                final_spectacle = selected_spec_dropdown
            elif custom_spectacle:
                final_spectacle = custom_spectacle
            else:
                final_spectacle = None

                if final_spectacle:
                    # Reset dropdown on selection save
                    if st.button(f"➕ Add {final_spectacle} to Prescription", key=f"add_spec_btn_{_spec_key}"):
                        st.session_state['selected_spectacles'] = [final_spectacle]
                        st.session_state['spec_selector_key'] += 1
                        st.rerun()

                    # Show already confirmed spectacle
                    if st.session_state.get('selected_spectacles'):
                        st.success(f"✅ Spectacle confirmed: {st.session_state['selected_spectacles'][0]}")

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

                    # Create compact single A4 prescription HTML
                    current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                    rx_table = st.session_state.get('rx_table', {})
                    od_data = rx_table.get('OD', {})
                    os_data = rx_table.get('OS', {})
                    
                    prescription_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mau Eye Care Prescription - {patient_name}</title>
    <style>
        @page {{ margin: 0.3in; size: A4; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; font-size: 10pt; line-height: 1.2; color: #333; }}
        .header {{ background: #1a4f66; color: white; padding: 8px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header-left, .header-right {{ flex: 1; }}
        .header-center {{ text-align: center; flex: 2; padding: 0 3px; }}
        .header-left {{ text-align: left; }}
        .header-right {{ text-align: right; }}
        .header h1 {{ margin: 0; font-size: 18pt; font-weight: 800; letter-spacing: 0.5px; }}
        .header h2 {{ margin: 1px 0; font-size: 11pt; font-weight: bold; }}
        .header p {{ margin: 1px 0; font-size: 8pt; opacity: 0.9; }}
        .urdu {{ font-family: 'Noto Nastaliq Urdu', 'Arial Unicode MS', sans-serif; }}
        .patient-info {{ background: #f4f6fc; border-left: 5px solid #2E86AB; padding: 8px 10px; margin: 6px 0; font-size: 10pt; border-radius: 3px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
        .patient-info h3 {{ margin: 0 0 4px 0; font-size: 11pt; color: #1a4f66; }}
        .patient-info p {{ margin: 2px 0; }}
        .content {{ display: flex; gap: 8px; }}
        .left-section {{ flex: 1; }}
        .right-section {{ flex: 1; }}
        .section {{ background: white; padding: 8px; margin: 5px 0; border: 1px solid #e0e6ed; border-radius: 3px; box-shadow: 0 1px 1px rgba(0,0,0,0.02); }}
        .section h3 {{ margin: 0 0 6px 0; font-size: 11pt; color: #2E86AB; border-bottom: 1px solid #f0f4f8; padding-bottom: 3px; }}
        .item {{ background: #f8fafc; padding: 6px; margin: 3px 0; border-radius: 2px; border-left: 3px solid #64748b; font-size: 10pt; }}
        .vision-table {{ width: 100%; border-collapse: collapse; margin: 6px 0; }}
        .vision-table th, .vision-table td {{ border: 1px solid #e2e8f0; padding: 4px; text-align: center; font-size: 9.5pt; }}
        .vision-table th {{ background: #f1f5f9; color: #334155; font-weight: bold; }}
        .medicine-item {{ background: #fffaf0; padding: 6px; margin: 3px 0; font-size: 9.5pt; border-left: 3px solid #f59e0b; border-radius: 2px; box-shadow: 0 1px 1px rgba(0,0,0,0.02); line-height: 1.3; }}
        .spectacle-item {{ background: #f0fdf4; padding: 6px; margin: 3px 0; font-size: 9.5pt; border-left: 3px solid #22c55e; border-radius: 2px; box-shadow: 0 1px 1px rgba(0,0,0,0.02); line-height: 1.3; }}
        .signature {{ text-align: right; margin-top: 8px; font-size: 10pt; font-weight: bold; padding-top: 8px; border-top: 1px dashed #cbd5e1; }}
        .footer {{ margin-top: 8px; padding-top: 6px; text-align: center; font-size: 8pt; color: #64748b; border-top: 1px solid #e2e8f0; line-height: 1.2; }}
    </style>
</head>
<body>
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
            <p style="margin: 1px 0; font-size: 8pt;"> Mon-Sat: 10 AM-5 PM | Sunday Closed |</p> 
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
        <div class="left-section">"""



                    # Add eye prescription section - always include
                    if True:  # Always show eye prescription section
                        prescription_html += f"""
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
                
                <h3>👁️ Vision Testing</h3>
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



                    # Close content and add signature/footer
                    prescription_html += """
        </div>
    </div>"""



                    prescription_html += """
    <div class="signature">
        <p style="margin: 4px 0; font-size: 9pt;">Doctor Signature: ___________________________</p>
    </div>
    
    <div class="footer">
        <p style="margin: 1px 0;"><strong>Services:</strong> Refraction • Glasses • Contact Lens • Eye Screening • Treatment</p>
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
        @page {{ margin: 0.3in; }}
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 8px; font-size: 10pt; line-height: 1.3; }}
        .header {{ text-align: center; background: #2E86AB; color: white; padding: 8px; margin-bottom: 10px; border-radius: 3px; }}
        .header h2 {{ margin: 2px 0; font-size: 12pt; }}
        .header p {{ margin: 2px 0; font-size: 9pt; }}
        h3 {{ margin: 6px 0 4px 0; font-size: 10pt; color: #2E86AB; }}
        .receipt-item {{ background: #f0f8ff; padding: 6px; margin: 4px 0; border-left: 3px solid #2E86AB; font-size: 9.5pt; border-radius: 2px; }}
        .receipt-item strong {{ font-size: 10pt; }}
        .receipt-item br + * {{ margin-top: 2px; }}
        .total {{ background: #e8f5e8; padding: 8px; font-weight: bold; text-align: center; margin: 8px 0; border-radius: 3px; }}
        .total h2 {{ margin: 4px 0; font-size: 12pt; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Mau Eye Care - Receipt</h2>
        <p>Patient: {patient_name} | Date: {current_time.strftime('%d/%m/%Y %I:%M %p')}</p>
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
                            'selected_spectacles', 'medicine_details', 'selected_medicines_list', 'rx_table', 'prescription_generated',
                            'patient_complaint', 'patient_diagnosis', 'complaint', 'diagnosis', 'od_distance_vision', 'od_near_vision',
                            'os_distance_vision', 'os_near_vision', 'spectacle_instructions', 'new_patient',
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
