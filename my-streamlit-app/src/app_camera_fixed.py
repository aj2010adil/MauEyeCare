# MauEyeCare - Camera Fixed Final App
import streamlit as st
import pandas as pd
from io import BytesIO, StringIO
import sys, os
import requests
import datetime
import numpy as np
from PIL import Image
sys.path.append(os.path.dirname(__file__))
import db
from modules.pdf_utils import generate_pdf
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.enhanced_docx_utils import generate_professional_prescription_docx
from modules.ai_doctor_tools import analyze_symptoms_ai
from modules.enhanced_spectacle_data import (
    ENHANCED_SPECTACLE_DATA, 
    generate_pricing_table_data,
    create_comprehensive_report_image
)
from modules.simple_camera import complete_camera_analysis_workflow

db.init_db()

# Load configuration
try:
    from config import CONFIG
    grok_key = CONFIG.get('GROK_API_KEY')
    whatsapp_token = CONFIG.get('WHATSAPP_ACCESS_TOKEN')
    whatsapp_phone_id = CONFIG.get('WHATSAPP_PHONE_NUMBER_ID')
    print(f"Config loaded - Token: {whatsapp_token[:10] if whatsapp_token else 'None'}... Phone ID: {whatsapp_phone_id}")
except Exception as e:
    print(f"Config error: {e}")
    grok_key = None
    whatsapp_token = None
    whatsapp_phone_id = None

def populate_enhanced_inventory():
    """Populate inventory with enhanced spectacle data"""
    for item_name, item_data in ENHANCED_SPECTACLE_DATA.items():
        import random
        stock = random.randint(3, 15)
        add_or_update_inventory(item_name, stock)

def main():
    st.set_page_config(page_title="MauEyeCare", page_icon="👁️", layout="wide")
    
    st.title("👁️ MauEyeCare Optical Center")
    st.markdown("*AI-Powered Eye Care & Spectacle Recommendation System*")

    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Load Enhanced Spectacle Database"):
            with st.spinner("Loading enhanced spectacle database..."):
                populate_enhanced_inventory()
            st.success(f"Loaded {len(ENHANCED_SPECTACLE_DATA)} premium spectacles!")
        
        st.markdown("---")
        st.markdown("**📊 System Stats:**")
        inventory_count = len(get_inventory_dict())
        st.metric("Inventory Items", inventory_count)
        st.metric("Spectacle Database", len(ENHANCED_SPECTACLE_DATA))
        
        # Patient info display
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Gender: {st.session_state.get('gender', 'N/A')}")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Patient & Prescription", "📦 Spectacle Inventory", "📊 Patient History", "🤖 AI Camera Analysis"])

    # --- Patient & Prescription Tab ---
    with tab1:
        st.header("👥 Patient Information & Prescription")
        
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
            
            # RX Table
            st.markdown("**👁️ Prescription Details (RX Table)**")
            rx_table = {}
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+2.00", "+2.50", "+3.00", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-2.00", "-2.50", "-3.00"]
            
            col_od, col_os = st.columns(2)
            
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
            
            # Medicine Selection
            st.markdown("**💊 Medicine Selection & Dosages**")
            inventory_db = get_inventory_dict()
            med_options = [item for item in inventory_db.keys() if any(word in item.lower() for word in ['drop', 'tablet', 'ointment', 'artificial', 'antibiotic'])]
            selected_meds = st.multiselect("Choose medicines", med_options, key="form_meds")
            
            prescription = {}
            dosages = {}
            
            for med in selected_meds:
                col_qty, col_dose, col_timing = st.columns(3)
                max_qty = inventory_db.get(med, 0)
                
                with col_qty:
                    qty = st.number_input(f"Qty {med}", min_value=1, max_value=max(max_qty, 1), value=1, key=f"qty_{med}")
                    prescription[med] = qty
                
                with col_dose:
                    dosage = st.selectbox(f"Dosage", ["1 drop", "2 drops", "1 tablet"], key=f"dose_{med}")
                
                with col_timing:
                    timing = st.selectbox(f"Timing", ["Once daily", "Twice daily", "Thrice daily"], key=f"timing_{med}")
                
                dosages[med] = {'dosage': dosage, 'timing': timing}
            
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
                    'prescription': prescription,
                    'dosages': dosages,
                    'rx_table': rx_table,
                    'show_pdf': True
                })
                
                st.success(f"✅ Patient {patient_name} saved successfully!")
                st.info("🎯 Now go to the 'AI Camera Analysis' tab to capture photo and get spectacle recommendations!")

        # PDF Generation
        if st.session_state.get('show_pdf', False):
            st.markdown("---")
            st.subheader("📄 Generate Prescription Documents")
            
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_file = generate_pdf(
                    st.session_state['prescription'], '', '', "Dr Danish", 
                    st.session_state['patient_name'], st.session_state['age'], 
                    st.session_state['gender'], st.session_state['advice'], 
                    st.session_state['rx_table'], []
                )
                st.download_button(
                    label="📄 Download PDF Prescription",
                    data=pdf_file,
                    file_name=f"prescription_{st.session_state['patient_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                docx_file = generate_professional_prescription_docx(
                    st.session_state['prescription'], "Dr Danish", 
                    st.session_state['patient_name'], st.session_state['age'], 
                    st.session_state['gender'], st.session_state['advice'], 
                    st.session_state['rx_table'], [], st.session_state.get('dosages', {})
                )
                st.download_button(
                    label="📄 Download DOCX Prescription",
                    data=docx_file,
                    file_name=f"RX_{st.session_state['patient_name'].replace(' ', '_')}_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # --- Spectacle Inventory Tab ---
    with tab2:
        st.header("📦 Premium Spectacle Inventory")
        st.markdown("*Curated collection from Ray-Ban, Oakley, Warby Parker, Gucci & more*")
        
        # Enhanced inventory display
        inventory_db = get_inventory_dict()
        
        if inventory_db:
            enhanced_inventory = []
            
            for item_name, stock in inventory_db.items():
                if item_name in ENHANCED_SPECTACLE_DATA:
                    spec_data = ENHANCED_SPECTACLE_DATA[item_name]
                    enhanced_inventory.append({
                        "Brand": spec_data['brand'],
                        "Model": spec_data['model'],
                        "Category": spec_data['category'],
                        "Material": spec_data['material'],
                        "Shape": spec_data['shape'],
                        "Frame Price": f"${spec_data['price']}",
                        "Lens Price": f"${spec_data['lens_price']}",
                        "Stock": stock,
                        "Source": spec_data['source'],
                        "Collected": spec_data['collected_date'],
                        "Delivery": f"{spec_data['delivery_days']} days",
                        "Status": spec_data['availability']
                    })
            
            if enhanced_inventory:
                df = pd.DataFrame(enhanced_inventory)
                
                # Filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    brand_filter = st.selectbox("Filter by Brand", ["All"] + list(df['Brand'].unique()))
                
                with col2:
                    category_filter = st.selectbox("Filter by Category", ["All"] + list(df['Category'].unique()))
                
                with col3:
                    shape_filter = st.selectbox("Filter by Shape", ["All"] + list(df['Shape'].unique()))
                
                # Apply filters
                filtered_df = df.copy()
                if brand_filter != "All":
                    filtered_df = filtered_df[filtered_df['Brand'] == brand_filter]
                if category_filter != "All":
                    filtered_df = filtered_df[filtered_df['Category'] == category_filter]
                if shape_filter != "All":
                    filtered_df = filtered_df[filtered_df['Shape'] == shape_filter]
                
                st.dataframe(filtered_df, use_container_width=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Models", len(filtered_df))
                with col2:
                    avg_price = filtered_df['Frame Price'].str.replace('$', '').astype(float).mean()
                    st.metric("Avg Frame Price", f"${avg_price:.0f}")
                with col3:
                    total_stock = filtered_df['Stock'].sum()
                    st.metric("Total Stock", total_stock)
                with col4:
                    brands_count = len(filtered_df['Brand'].unique())
                    st.metric("Brands Available", brands_count)

    # --- Patient History Tab ---
    with tab3:
        st.header("🔍 Patient History & Records")
        
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

    # --- AI Camera Analysis Tab ---
    with tab4:
        st.header("🤖 AI Camera Analysis & Spectacle Recommendations")
        st.markdown("*Advanced face analysis with instant spectacle recommendations*")
        
        # Check if patient is selected
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            
            st.success(f"👤 **Current Patient:** {patient_name} | Age: {age} | Gender: {gender}")
            
            # Complete Camera Analysis Workflow
            st.markdown("---")
            
            # Instructions
            with st.expander("📋 Instructions for Best Results", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📸 Photo Guidelines:**")
                    st.info("• Face the camera directly")
                    st.info("• Ensure good lighting")
                    st.info("• Remove existing glasses")
                    st.info("• Keep face centered")
                    st.info("• Maintain neutral expression")
                
                with col2:
                    st.markdown("**🎯 What We Analyze:**")
                    st.info("• Face shape detection")
                    st.info("• Frame style matching")
                    st.info("• Age-appropriate recommendations")
                    st.info("• Price range suggestions")
                    st.info("• Brand compatibility")
            
            # Main Camera Analysis
            success = complete_camera_analysis_workflow(patient_name, age, gender)
            
            if not success:
                st.info("👆 Use the camera options above to capture your photo and get AI recommendations!")
        
        else:
            st.warning("⚠️ **Patient Required**")
            st.info("Please go to the **'Patient & Prescription'** tab first and enter patient information to use AI analysis features.")
            
            st.markdown("**🔄 Quick Steps:**")
            st.markdown("1. Go to 'Patient & Prescription' tab")
            st.markdown("2. Fill in patient details and save")
            st.markdown("3. Return to this tab for AI analysis")

if __name__ == "__main__":
    main()