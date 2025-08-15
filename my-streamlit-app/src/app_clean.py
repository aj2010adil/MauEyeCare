# MauEyeCare Main App - Clean Version
import streamlit as st
import pandas as pd
import sys, os
import requests
sys.path.append(os.path.dirname(__file__))
import db
from modules.pdf_utils import generate_pdf
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.whatsapp_utils import send_pdf_to_whatsapp

# Load configuration
try:
    import perplexity_config
    grok_key = getattr(perplexity_config, "grok_key", None)
    whatsapp_token = getattr(perplexity_config, "WHATSAPP_ACCESS_TOKEN", None)
    whatsapp_phone_id = getattr(perplexity_config, "WHATSAPP_PHONE_NUMBER_ID", None)
    print(f"Config loaded - Token: {whatsapp_token[:10] if whatsapp_token else 'None'}... Phone ID: {whatsapp_phone_id}")
except Exception as e:
    print(f"Config error: {e}")
    grok_key = None
    whatsapp_token = None
    whatsapp_phone_id = None

db.init_db()

def main():
    st.title("🔍 Mau Eye Care Optical Center")
    st.markdown("*Advanced Eye Care & Prescription Management System*")

    tab1, tab2, tab3 = st.tabs(["📋 Prescription & Patient", "📦 Inventory Management", "📊 Patient History"])

    # --- Prescription & Patient Tab ---
    with tab1:
        st.header("👥 Patient Information & Prescription")
        
        with st.form("patient_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            patient_name = f"{first_name} {last_name}".strip()
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Mobile Number")
            
            issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Other"]
            patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
            if patient_issue == "Other":
                patient_issue = st.text_input("Specify Other Issue")
            
            advice_options = ["Spectacle Prescription", "Regular Eye Checkup", "Dry Eye Treatment", "Other"]
            advice = st.selectbox("Advice/Notes", advice_options)
            if advice == "Other":
                advice = st.text_input("Specify Other Advice")
            
            # Medicine Selection
            st.markdown("**Medicine Selection**")
            inventory_db = get_inventory_dict()
            med_options = list(inventory_db.keys())
            selected_meds = st.multiselect("Choose medicines/spectacles", med_options)
            prescription = {}
            for med in selected_meds:
                max_qty = inventory_db[med]
                qty = st.number_input(f"Quantity for {med} (Stock: {max_qty})", min_value=1, max_value=max_qty, value=1, key=f"qty_{med}")
                prescription[med] = qty
            
            submitted = st.form_submit_button("Save Patient")
            
            if submitted:
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
                st.session_state['patient_id'] = patient_id
                st.session_state['patient_name'] = patient_name
                st.session_state['patient_mobile'] = contact
                st.session_state['age'] = age
                st.session_state['gender'] = gender
                st.session_state['advice'] = advice
                st.session_state['patient_issue'] = patient_issue
                st.session_state['prescription'] = prescription
                st.session_state['show_pdf'] = True

        # Show PDF generation after form submission
        if st.session_state.get('show_pdf', False):
            patient_id = st.session_state['patient_id']
            patient_name = st.session_state['patient_name']
            patient_mobile = st.session_state['patient_mobile']
            age = st.session_state['age']
            gender = st.session_state['gender']
            advice = st.session_state['advice']
            prescription = st.session_state['prescription']
            
            st.success(f"Patient saved: {patient_name}")
            
            st.markdown("---")
            st.subheader("📝 Generate Prescription PDF")
            
            pdf_file = generate_pdf(
                prescription, '', '', "Dr Danish", patient_name, age, gender, advice, {}, []
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_file,
                    file_name=f"prescription_{patient_name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                if st.button("📱 Send via WhatsApp"):
                    if whatsapp_token and whatsapp_phone_id:
                        with st.spinner("Sending PDF via WhatsApp..."):
                            result = send_pdf_to_whatsapp(
                                patient_mobile, pdf_file, patient_name, whatsapp_token, whatsapp_phone_id
                            )
                            
                            if result["success"]:
                                st.success(f"✅ PDF sent to {patient_mobile}")
                            else:
                                if "OAuth" in result['message']:
                                    st.error("❌ WhatsApp token expired")
                                    st.info("Get new token from: https://developers.facebook.com")
                                else:
                                    st.error(f"❌ Failed: {result['message']}")
                    else:
                        st.error("WhatsApp not configured")
                        st.info(f"Token: {'✅' if whatsapp_token else '❌'} | Phone ID: {'✅' if whatsapp_phone_id else '❌'}")

    # --- Inventory Tab ---
    with tab2:
        st.header("📦 Inventory Management")
        inventory_db = get_inventory_dict()
        st.table(pd.DataFrame(list(inventory_db.items()), columns=["Item", "Quantity"]))

        st.subheader("Add Medicine/Spectacle")
        new_item = st.text_input("Item Name")
        new_qty = st.number_input("Quantity", min_value=1, value=1)
        if st.button("Add Item"):
            add_or_update_inventory(new_item, new_qty)
            st.success(f"Added {new_qty} of {new_item}")
            st.rerun()

    # --- Patient History Tab ---
    with tab3:
        st.header("🔍 Patient History")
        patients = db.get_patients()
        search_mobile = st.text_input("Search by Mobile Number")
        search_name = st.text_input("Search by Name")
        filtered = [p for p in patients if (search_mobile in p[4]) and (search_name.lower() in p[1].lower())]
        
        st.write(f"Found {len(filtered)} patient(s)")
        for p in filtered:
            st.markdown(f"**{p[1]}** | Age: {p[2]} | Mobile: {p[4]}")

if __name__ == "__main__":
    main()