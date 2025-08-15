# MauEyeCare Main App - Final Version
import streamlit as st
import pandas as pd
from io import BytesIO
import sys, os
import requests
import datetime
sys.path.append(os.path.dirname(__file__))
import db
from modules.pdf_utils import generate_pdf
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.enhanced_docx_utils import generate_professional_prescription_docx
from modules.ai_doctor_tools import analyze_symptoms_ai

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

def main():
    st.title("👁️ Mau Eye Care Optical Center")
    st.markdown("*Advanced Eye Care & Prescription Management System*")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Prescription & Patient", "📦 Inventory Management", "📊 Patient History", "🤖 AI Doctor Assistant"])

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
            
            # RX Table
            st.markdown("**Rx Table** (Fill for OD and OS)")
            rx_table = {}
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+2.00", "+2.50", "+3.00", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-2.00", "-2.50", "-3.00"]
            
            for eye in ['OD', 'OS']:
                st.markdown(f"**{eye}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    sphere = st.selectbox(f"Sphere {eye}", sphere_options, key=f"sphere_{eye}")
                with col2:
                    cylinder = st.selectbox(f"Cylinder {eye}", ["", "-0.25", "-0.50", "-0.75", "-1.00"], key=f"cylinder_{eye}")
                with col3:
                    axis = st.selectbox(f"Axis {eye}", ["", "90", "180", "45", "135"], key=f"axis_{eye}")
                rx_table[eye] = {"Sphere": sphere, "Cylinder": cylinder, "Axis": axis}
            
            # Medicine Selection with dosages
            st.markdown("**Medicine Selection & Dosages**")
            inventory_db = get_inventory_dict()
            med_options = list(inventory_db.keys())
            selected_meds = st.multiselect("Choose medicines/spectacles", med_options, key="form_meds")
            prescription = {}
            dosages = {}
            
            for med in selected_meds:
                max_qty = inventory_db[med]
                col_qty, col_dose, col_timing = st.columns(3)
                
                with col_qty:
                    qty = st.number_input(f"Qty {med} (Stock: {max_qty})", min_value=1, max_value=max_qty, value=1, key=f"form_qty_{med}")
                    prescription[med] = qty
                
                with col_dose:
                    if 'drop' in med.lower():
                        dosage = st.selectbox(f"Dosage {med}", ["1 drop", "2 drops", "3 drops"], key=f"dose_{med}")
                    else:
                        dosage = st.selectbox(f"Dosage {med}", ["1 tablet", "2 tablets", "1/2 tablet"], key=f"dose_{med}")
                
                with col_timing:
                    timing = st.selectbox(f"Timing {med}", ["Once daily", "Twice daily", "Thrice daily", "As needed"], key=f"timing_{med}")
                
                dosages[med] = {'dosage': dosage, 'timing': timing}
            
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
                st.session_state['dosages'] = dosages
                st.session_state['rx_table'] = rx_table
                st.session_state['show_pdf'] = True

        # Show PDF generation after form submission
        if st.session_state.get('show_pdf', False):
            patient_id = st.session_state['patient_id']
            patient_name = st.session_state['patient_name']
            age = st.session_state['age']
            gender = st.session_state['gender']
            advice = st.session_state['advice']
            prescription = st.session_state['prescription']
            dosages = st.session_state.get('dosages', {})
            rx_table = st.session_state.get('rx_table', {})
            
            st.success(f"Patient saved: {patient_name}")
            
            st.markdown("---")
            st.subheader("📝 Generate Prescription")
            
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_file = generate_pdf(prescription, '', '', "Dr Danish", patient_name, age, gender, advice, rx_table, [])
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_file,
                    file_name=f"prescription_{patient_name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                docx_file = generate_professional_prescription_docx(
                    prescription, "Dr Danish", patient_name, age, gender, advice, rx_table, [], dosages
                )
                st.download_button(
                    label="📄 Download DOCX",
                    data=docx_file,
                    file_name=f"RX_{patient_name.replace(' ', '_')}_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # --- Inventory Tab ---
    with tab2:
        st.header("📦 Professional Inventory Management")
        
        # Current inventory with professional display
        inventory_db = get_inventory_dict()
        
        # Create professional inventory table
        if inventory_db:
            df = pd.DataFrame(list(inventory_db.items()), columns=["Item", "Stock"])
            df['Status'] = df['Stock'].apply(lambda x: 'Out of Stock' if x == 0 else 'Low Stock' if x < 5 else 'In Stock')
            df['Action'] = df['Stock'].apply(lambda x: 'Reorder Now' if x == 0 else 'Reorder Soon' if x < 5 else 'No Action')
            
            # Color code the status
            def color_status(val):
                if val == 'Out of Stock':
                    return 'background-color: #ffebee'
                elif val == 'Low Stock':
                    return 'background-color: #fff3e0'
                else:
                    return 'background-color: #e8f5e8'
            
            styled_df = df.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True)
        
        # Professional inventory management
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add New Items")
            
            # Categorized item addition
            category = st.selectbox("Category", ["Eye Drops", "Tablets", "Ointments", "Spectacles", "Equipment", "Other"])
            
            if category == "Eye Drops":
                item_options = ["Artificial Tears", "Antibiotic Drops", "Anti-inflammatory Drops", "Glaucoma Drops", "Custom"]
            elif category == "Spectacles":
                item_options = ["Single Vision", "Bifocal", "Progressive", "Reading Glasses", "Sunglasses", "Custom"]
            else:
                item_options = ["Custom"]
            
            if "Custom" in item_options:
                selected_item = st.selectbox("Select Item", item_options)
                if selected_item == "Custom":
                    new_item = st.text_input("Enter custom item name")
                else:
                    new_item = selected_item
            else:
                new_item = st.selectbox("Select Item", item_options)
            
            new_qty = st.number_input("Quantity to Add", min_value=1, value=10)
            
            if st.button("Add to Inventory", type="primary"):
                if new_item:
                    add_or_update_inventory(new_item, new_qty)
                    st.success(f"Added {new_qty} of {new_item}")
                    st.rerun()
        
        with col2:
            st.subheader("Quick Actions")
            
            if st.button("📊 Generate Inventory Report"):
                from modules.enhanced_docx_utils import generate_inventory_report_docx
                
                report_docx = generate_inventory_report_docx(inventory_db)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                
                st.download_button(
                    label="📄 Download Report",
                    data=report_docx,
                    file_name=f"Inventory_Report_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

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

    # --- AI Doctor Assistant Tab ---
    with tab4:
        st.header("🤖 AI Doctor Assistant")
        st.markdown("*AI-powered tools for enhanced diagnosis and patient care*")
        
        # AI Spectacle Selection
        st.subheader("🔍 AI Spectacle Selection")
        
        if 'patient_name' in st.session_state:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            rx_table = st.session_state.get('rx_table', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Patient:** {patient_name}")
                st.write(f"**Age:** {age} | **Gender:** {gender}")
                
                # Extract prescription details
                od_sphere = rx_table.get('OD', {}).get('Sphere', '')
                os_sphere = rx_table.get('OS', {}).get('Sphere', '')
                
                if od_sphere or os_sphere:
                    st.write(f"**Prescription:** OD: {od_sphere}, OS: {os_sphere}")
                
                if st.button("🤖 Get AI Spectacle Recommendations", type="primary"):
                    with st.spinner("AI analyzing best spectacle options..."):
                        # Create spectacle recommendation prompt
                        prescription_info = f"OD: {od_sphere}, OS: {os_sphere}" if (od_sphere or os_sphere) else "No prescription data"
                        
                        prompt = f"""Patient: {patient_name}, Age: {age}, Gender: {gender}
                        Prescription: {prescription_info}
                        
                        Recommend the best spectacle options including:
                        1. Frame materials (metal, plastic, titanium)
                        2. Lens types (single vision, bifocal, progressive)
                        3. Lens coatings (anti-glare, blue light, photochromic)
                        4. Frame styles suitable for age and gender
                        5. Special considerations for prescription strength
                        
                        Provide specific product recommendations."""
                        
                        analysis = analyze_symptoms_ai(prompt, age, gender, "Spectacle selection")
                        st.session_state['spectacle_recommendations'] = analysis
            
            with col2:
                if 'spectacle_recommendations' in st.session_state:
                    st.markdown("**AI Spectacle Recommendations:**")
                    st.write(st.session_state['spectacle_recommendations'])
                    
                    # Add to inventory button
                    if st.button("➕ Add Recommended Items to Inventory"):
                        # Add some common spectacle types to inventory
                        spectacle_items = [
                            "Progressive Lenses",
                            "Anti-Glare Coating",
                            "Blue Light Filter",
                            "Titanium Frames",
                            "Plastic Frames"
                        ]
                        
                        for item in spectacle_items:
                            add_or_update_inventory(item, 5)
                        
                        st.success("Recommended spectacle items added to inventory!")
        else:
            st.info("Please select a patient first to get AI spectacle recommendations.")
        
        st.markdown("---")
        
        # Camera-based face analysis
        st.subheader("📸 Face Analysis & Frame Recommendation")
        
        uploaded_file = st.file_uploader("Upload patient photo for face analysis", type=['jpg', 'jpeg', 'png'])
        if uploaded_file is not None:
            from PIL import Image
            image = Image.open(uploaded_file)
            st.image(image, caption="Patient Photo", width=300)
            
            if st.button("🔍 Analyze Face Shape"):
                try:
                    from modules.camera_utils import analyze_face_shape, get_spectacle_recommendations
                    face_shape, basic_recs = analyze_face_shape(image)
                    
                    if "error" not in face_shape.lower():
                        st.success(f"Face Shape: {face_shape}")
                        
                        if 'patient_name' in st.session_state:
                            age = st.session_state.get('age', 30)
                            gender = st.session_state.get('gender', 'Male')
                            detailed_recs = get_spectacle_recommendations(face_shape, age, gender)
                            
                            st.write(f"**Recommended Frames:** {', '.join(detailed_recs['recommended_frames'])}")
                            st.write(f"**Avoid:** {', '.join(detailed_recs['avoid_frames'])}")
                            st.write(f"**Colors:** {', '.join(detailed_recs['color_suggestions'])}")
                        else:
                            for rec in basic_recs:
                                st.write(f"• {rec}")
                    else:
                        st.error(face_shape)
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.info("Install opencv-python for face analysis: pip install opencv-python")

if __name__ == "__main__":
    main()