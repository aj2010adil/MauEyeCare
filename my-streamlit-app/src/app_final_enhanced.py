# MauEyeCare Final Enhanced App - Complete System
import streamlit as st
import pandas as pd
from io import BytesIO
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
    create_spectacle_overlay_image, 
    generate_pricing_table_data,
    get_face_shape_analysis_with_spectacles,
    create_comprehensive_report_image
)
from modules.advanced_camera import FaceDetectionCamera

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

    # Sidebar for inventory management
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

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Patient & Prescription", "📦 Spectacle Inventory", "📊 Patient History", "🤖 AI Spectacle Assistant"])

    # --- Patient & Prescription Tab ---
    with tab1:
        st.header("👥 Patient Information & Prescription")
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                contact = st.text_input("Mobile Number")
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
            med_options = [item for item in inventory_db.keys() if 'drop' in item.lower() or 'tablet' in item.lower() or 'ointment' in item.lower()]
            selected_meds = st.multiselect("Choose medicines", med_options, key="form_meds")
            
            prescription = {}
            dosages = {}
            
            for med in selected_meds:
                col_qty, col_dose, col_timing = st.columns(3)
                max_qty = inventory_db[med]
                
                with col_qty:
                    qty = st.number_input(f"Qty {med}", min_value=1, max_value=max_qty, value=1, key=f"qty_{med}")
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

    # --- AI Spectacle Assistant Tab ---
    with tab4:
        st.header("🤖 AI Spectacle Assistant")
        st.markdown("*Advanced face analysis with real-time spectacle recommendations*")
        
        # Camera Section
        st.subheader("📸 Professional Face Capture & Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Guided Camera Capture**")
            st.info("📋 **Instructions:**\n• Position face in center\n• Look directly at camera\n• Ensure good lighting\n• Remove existing glasses")
            
            if st.button("📷 Start Professional Camera Capture", type="primary"):
                try:
                    camera = FaceDetectionCamera()
                    
                    with st.spinner("🔍 Initializing AI-powered camera system..."):
                        captured_image, message = camera.capture_with_guidance()
                    
                    if captured_image is not None:
                        st.success(f"✅ {message}")
                        st.session_state['captured_photo'] = captured_image
                        st.image(captured_image, caption="📸 Captured Photo", width=400)
                        
                        # Immediate analysis
                        if 'patient_name' in st.session_state:
                            with st.spinner("🤖 AI analyzing face shape and matching spectacles..."):
                                analysis_result = get_face_shape_analysis_with_spectacles(
                                    captured_image,
                                    st.session_state['patient_name'],
                                    st.session_state.get('age', 30),
                                    st.session_state.get('gender', 'Male')
                                )
                                st.session_state['face_analysis'] = analysis_result
                        else:
                            st.warning("⚠️ Please select a patient first for personalized analysis")
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"🚫 Camera system error: {str(e)}")
                    st.info("💡 Ensure camera permissions are granted and opencv-python is installed")
        
        with col2:
            st.markdown("**📁 Upload Photo Alternative**")
            uploaded_file = st.file_uploader(
                "Upload clear front-facing photo", 
                type=['jpg', 'jpeg', 'png'],
                help="Upload a high-quality photo with good lighting"
            )
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                st.session_state['captured_photo'] = image_array
                st.image(image, caption="📁 Uploaded Photo", width=400)
                
                # Analysis for uploaded photo
                if 'patient_name' in st.session_state:
                    with st.spinner("🤖 AI analyzing uploaded photo..."):
                        analysis_result = get_face_shape_analysis_with_spectacles(
                            image_array,
                            st.session_state['patient_name'],
                            st.session_state.get('age', 30),
                            st.session_state.get('gender', 'Male')
                        )
                        st.session_state['face_analysis'] = analysis_result
        
        # Analysis Results & Recommendations
        if 'captured_photo' in st.session_state and 'face_analysis' in st.session_state:
            st.markdown("---")
            st.subheader("🎯 AI Analysis Results & Spectacle Recommendations")
            
            analysis = st.session_state['face_analysis']
            
            if analysis['status'] == 'success':
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**📊 Face Analysis:**")
                    st.success(f"**Face Shape:** {analysis['face_shape']}")
                    st.info(f"**Confidence:** {analysis['confidence']}%")
                    st.write(f"**Best Shapes:** {', '.join(analysis['best_shapes'])}")
                    st.write(f"**Avoid Shapes:** {', '.join(analysis['avoid_shapes'])}")
                    st.write(f"**Analysis Date:** {analysis['analysis_date']}")
                
                with col2:
                    st.markdown("**🔍 Recommended Spectacles:**")
                    
                    if analysis['recommended_spectacles']:
                        # Generate pricing table
                        rx_table = st.session_state.get('rx_table', {})
                        prescription_type = "Single Vision"
                        
                        # Determine prescription type
                        od_sphere = rx_table.get('OD', {}).get('Sphere', '')
                        os_sphere = rx_table.get('OS', {}).get('Sphere', '')
                        
                        if st.session_state.get('age', 30) > 40:
                            prescription_type = "Progressive"
                        elif od_sphere or os_sphere:
                            prescription_type = "Single Vision"
                        
                        pricing_table = generate_pricing_table_data(
                            analysis['recommended_spectacles'], 
                            prescription_type
                        )
                        
                        # Display pricing table
                        if pricing_table:
                            df_pricing = pd.DataFrame(pricing_table)
                            st.dataframe(df_pricing, use_container_width=True)
                            
                            # Generate comprehensive report
                            if st.button("📋 Generate Complete Analysis Report", type="primary"):
                                with st.spinner("🎨 Creating comprehensive analysis report..."):
                                    comprehensive_report = create_comprehensive_report_image(
                                        st.session_state['captured_photo'],
                                        analysis,
                                        pricing_table
                                    )
                                    
                                    st.image(comprehensive_report, caption="📋 Complete Analysis Report", use_column_width=True)
                                    
                                    # Download report
                                    img_buffer = BytesIO()
                                    comprehensive_report.save(img_buffer, format='PNG')
                                    img_buffer.seek(0)
                                    
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                                    patient_name = st.session_state.get('patient_name', 'Patient')
                                    
                                    st.download_button(
                                        label="📄 Download Complete Report",
                                        data=img_buffer.getvalue(),
                                        file_name=f"Spectacle_Analysis_{patient_name.replace(' ', '_')}_{timestamp}.png",
                                        mime="image/png"
                                    )
                                    
                                    st.balloons()
                            
                            # Add recommended items to inventory
                            if st.button("🛒 Add All Recommended Spectacles to Inventory"):
                                added_count = 0
                                for spec_name in analysis['recommended_spectacles']:
                                    if spec_name in ENHANCED_SPECTACLE_DATA:
                                        add_or_update_inventory(spec_name, 5)
                                        added_count += 1
                                
                                st.success(f"✅ Added {added_count} recommended spectacles to inventory!")
                                st.balloons()
                    else:
                        st.warning("⚠️ No suitable spectacles found for this face shape")
            else:
                st.error(f"❌ Analysis failed: {analysis['message']}")
        
        elif 'captured_photo' in st.session_state:
            st.info("ℹ️ Please select a patient first to get personalized spectacle recommendations")
        
        else:
            st.info("📸 Capture or upload a patient photo to begin AI analysis")

if __name__ == "__main__":
    main()