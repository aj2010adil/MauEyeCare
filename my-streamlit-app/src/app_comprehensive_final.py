# MauEyeCare Comprehensive Final App - Complete System with Indian Pricing
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
try:
    from modules.enhanced_docx_utils import generate_professional_prescription_docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    def generate_professional_prescription_docx(*args, **kwargs):
        return b"DOCX generation not available - please install python-docx"
from modules.ai_doctor_tools import analyze_symptoms_ai
from modules.comprehensive_spectacle_database import (
    COMPREHENSIVE_SPECTACLE_DATABASE, 
    get_spectacles_sorted_by_price,
    get_spectacles_by_category,
    get_spectacles_by_price_range,
    search_spectacles_by_criteria,
    get_recommendations_by_face_shape_inr
)
from modules.patient_spectacle_overlay import (
    create_patient_with_spectacles_overlay,
    create_comprehensive_analysis_page,
    generate_pricing_table_inr
)
from modules.simple_camera import show_camera_with_preview, analyze_captured_photo

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

def populate_comprehensive_inventory():
    """Populate inventory with comprehensive spectacle database"""
    for item_name, item_data in COMPREHENSIVE_SPECTACLE_DATABASE.items():
        import random
        stock = random.randint(2, 20)
        add_or_update_inventory(item_name, stock)

def main():
    st.set_page_config(page_title="MauEyeCare", page_icon="👁️", layout="wide")
    
    st.title("👁️ MauEyeCare Optical Center")
    st.markdown("*Complete AI-Powered Eye Care & Spectacle Recommendation System*")
    st.markdown("**🇮🇳 Indian Pricing in ₹ | Comprehensive Collection from Budget to Luxury**")

    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Load Comprehensive Spectacle Database"):
            with st.spinner("Loading comprehensive spectacle database..."):
                populate_comprehensive_inventory()
            st.success(f"Loaded {len(COMPREHENSIVE_SPECTACLE_DATABASE)} spectacles!")
        
        st.markdown("---")
        st.markdown("**📊 Database Stats:**")
        st.metric("Total Spectacles", len(COMPREHENSIVE_SPECTACLE_DATABASE))
        
        # Price range stats
        budget_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] <= 5000])
        mid_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if 5000 < s['price'] <= 15000])
        luxury_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] > 15000])
        
        st.metric("Budget (≤₹5,000)", budget_count)
        st.metric("Mid-Range (₹5,001-15,000)", mid_count)
        st.metric("Luxury (>₹15,000)", luxury_count)
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Gender: {st.session_state.get('gender', 'N/A')}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Patient & Prescription", 
        "📦 Comprehensive Inventory", 
        "📊 Patient History", 
        "🤖 AI Camera Analysis",
        "📄 Spectacle Analysis Report"
    ])

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
                if DOCX_AVAILABLE:
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
                else:
                    st.info("📄 DOCX generation not available - PDF download available above")

    # --- Comprehensive Inventory Tab ---
    with tab2:
        st.header("📦 Comprehensive Spectacle Inventory")
        st.markdown("*Complete collection: Indian brands, International luxury, Budget to Premium*")
        
        # Advanced filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            category_filter = st.selectbox("Category", 
                ["All", "Luxury", "Mid-Range", "Indian", "Budget", "Progressive", "Kids", "Safety", "Reading", "Computer"])
        
        with col2:
            price_range_filter = st.selectbox("Price Range", 
                ["All", "Budget (≤₹5,000)", "Mid-Range (₹5,001-15,000)", "Luxury (>₹15,000)"])
        
        with col3:
            brand_filter = st.selectbox("Brand", 
                ["All"] + sorted(list(set([spec['brand'] for spec in COMPREHENSIVE_SPECTACLE_DATABASE.values()]))))
        
        with col4:
            sort_order = st.selectbox("Sort by Price", ["Low to High", "High to Low"])
        
        # Apply filters
        filtered_specs = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
        
        if category_filter != "All":
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['category'] == category_filter}
        
        if brand_filter != "All":
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['brand'] == brand_filter}
        
        if price_range_filter != "All":
            if "Budget" in price_range_filter:
                filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] <= 5000}
            elif "Mid-Range" in price_range_filter:
                filtered_specs = {k: v for k, v in filtered_specs.items() if 5000 < v['price'] <= 15000}
            elif "Luxury" in price_range_filter:
                filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] > 15000}
        
        # Sort by price
        if sort_order == "Low to High":
            filtered_specs = dict(sorted(filtered_specs.items(), key=lambda x: x[1]['price']))
        else:
            filtered_specs = dict(sorted(filtered_specs.items(), key=lambda x: x[1]['price'], reverse=True))
        
        # Display inventory
        if filtered_specs:
            inventory_data = []
            
            for spec_name, spec_data in filtered_specs.items():
                total_price = spec_data['price'] + spec_data['lens_price']
                inventory_data.append({
                    "Brand": spec_data['brand'],
                    "Model": spec_data['model'],
                    "Category": spec_data['category'],
                    "Material": spec_data['material'],
                    "Shape": spec_data['shape'],
                    "Frame Price": f"₹{spec_data['price']:,}",
                    "Lens Price": f"₹{spec_data['lens_price']:,}",
                    "Total Price": f"₹{total_price:,}",
                    "Source": spec_data['source'],
                    "Delivery": f"{spec_data['delivery_days']} days",
                    "Collected": spec_data['collected_date'],
                    "Status": spec_data['availability']
                })
            
            df = pd.DataFrame(inventory_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Models", len(df))
            with col2:
                avg_frame_price = df['Frame Price'].str.replace('₹', '').str.replace(',', '').astype(int).mean()
                st.metric("Avg Frame Price", f"₹{avg_frame_price:,.0f}")
            with col3:
                min_price = df['Total Price'].str.replace('₹', '').str.replace(',', '').astype(int).min()
                st.metric("Cheapest", f"₹{min_price:,}")
            with col4:
                max_price = df['Total Price'].str.replace('₹', '').str.replace(',', '').astype(int).max()
                st.metric("Most Expensive", f"₹{max_price:,}")
            with col5:
                brands_count = len(df['Brand'].unique())
                st.metric("Brands", brands_count)

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
        st.markdown("*Advanced face analysis with comprehensive spectacle matching*")
        
        # Check if patient is selected
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            
            st.success(f"👤 **Current Patient:** {patient_name} | Age: {age} | Gender: {gender}")
            
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
                    st.info("• Price range suggestions (₹)")
                    st.info("• Indian & International brands")
            
            # Camera capture
            st.markdown("### 📷 Capture Patient Photo")
            captured_image = show_camera_with_preview()
            
            if captured_image is not None:
                st.session_state['analysis_photo'] = captured_image
                
                # Immediate analysis
                st.markdown("### 🤖 AI Face Analysis")
                
                with st.spinner("🔍 AI analyzing face shape and matching spectacles..."):
                    analysis_result = analyze_captured_photo(captured_image, patient_name, age, gender)
                
                st.session_state['analysis_result'] = analysis_result
                
                if analysis_result['status'] == 'success':
                    # Display analysis results
                    st.success("🎉 Face Analysis Complete!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Face Shape", analysis_result["face_shape"])
                    
                    with col2:
                        st.metric("Confidence", f"{analysis_result['confidence']:.1f}%")
                    
                    with col3:
                        st.metric("Recommendations", len(analysis_result["recommended_spectacles"]))
                    
                    with col4:
                        st.metric("Face Coverage", f"{analysis_result['face_area_percentage']:.1f}%")
                    
                    # Analysis explanation
                    st.info(f"💡 **Analysis:** {analysis_result['reasoning']}")
                    
                    # Frame recommendations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Best Frame Shapes:**")
                        for shape in analysis_result['best_shapes']:
                            st.success(f"• {shape}")
                    
                    with col2:
                        st.markdown("**❌ Avoid Frame Shapes:**")
                        for shape in analysis_result['avoid_shapes']:
                            st.warning(f"• {shape}")
                    
                    # Get comprehensive recommendations
                    comprehensive_recs = get_recommendations_by_face_shape_inr(
                        analysis_result['face_shape'], age, gender
                    )
                    
                    st.session_state['comprehensive_recommendations'] = list(comprehensive_recs.keys())[:8]
                    
                    # Generate comprehensive report button
                    if st.button("📋 Generate Complete Analysis Report", type="primary"):
                        st.session_state['generate_report'] = True
                        st.rerun()
                
                else:
                    st.error(f"❌ Analysis Failed: {analysis_result['message']}")
        
        else:
            st.warning("⚠️ **Patient Required**")
            st.info("Please go to the **'Patient & Prescription'** tab first and enter patient information.")

    # --- Spectacle Analysis Report Tab ---
    with tab5:
        st.header("📄 Comprehensive Spectacle Analysis Report")
        
        if ('analysis_photo' in st.session_state and 
            'analysis_result' in st.session_state and 
            'comprehensive_recommendations' in st.session_state):
            
            analysis_result = st.session_state['analysis_result']
            recommendations = st.session_state['comprehensive_recommendations']
            patient_photo = st.session_state['analysis_photo']
            
            if analysis_result['status'] == 'success':
                st.success(f"📊 Analysis Report for {analysis_result['patient_name']}")
                
                # Generate pricing table
                pricing_table = generate_pricing_table_inr(recommendations, "Single Vision")
                
                if pricing_table:
                    # Display pricing table
                    st.markdown("### 💰 Comprehensive Pricing Table (₹)")
                    df_pricing = pd.DataFrame(pricing_table)
                    st.dataframe(df_pricing, use_container_width=True)
                    
                    # Create patient with spectacles overlay
                    st.markdown("### 👤 Patient Wearing Recommended Spectacles")
                    
                    with st.spinner("🎨 Creating patient spectacle overlays..."):
                        overlaid_images = create_patient_with_spectacles_overlay(
                            patient_photo, 
                            recommendations[:6], 
                            analysis_result.get('face_coordinates')
                        )
                    
                    # Display overlaid images in grid
                    cols = st.columns(3)
                    for i, overlay_data in enumerate(overlaid_images):
                        with cols[i % 3]:
                            st.image(overlay_data['image'], 
                                   caption=f"{overlay_data['spec_data']['brand']} {overlay_data['spec_data']['model']}", 
                                   width=200)
                            
                            total_price = overlay_data['spec_data']['price'] + overlay_data['spec_data']['lens_price']
                            st.write(f"**₹{total_price:,}**")
                            st.write(f"{overlay_data['spec_data']['material']} | {overlay_data['spec_data']['shape']}")
                    
                    # Generate comprehensive report
                    st.markdown("### 📋 Complete Analysis Report")
                    
                    if st.button("🎨 Generate Visual Report", type="primary"):
                        with st.spinner("Creating comprehensive visual report..."):
                            comprehensive_report = create_comprehensive_analysis_page(
                                patient_photo, analysis_result, recommendations
                            )
                        
                        st.image(comprehensive_report, caption="Complete Analysis Report", use_column_width=True)
                        
                        # Download options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Download visual report
                            img_buffer = BytesIO()
                            comprehensive_report.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                            
                            st.download_button(
                                label="📄 Download Visual Report",
                                data=img_buffer.getvalue(),
                                file_name=f"Spectacle_Analysis_{analysis_result['patient_name'].replace(' ', '_')}_{timestamp}.png",
                                mime="image/png"
                            )
                        
                        with col2:
                            # Download pricing CSV
                            csv_buffer = StringIO()
                            df_pricing.to_csv(csv_buffer, index=False)
                            
                            st.download_button(
                                label="📊 Download Pricing CSV",
                                data=csv_buffer.getvalue(),
                                file_name=f"Spectacle_Pricing_{analysis_result['patient_name'].replace(' ', '_')}_{timestamp}.csv",
                                mime="text/csv"
                            )
                        
                        with col3:
                            # Add to inventory
                            if st.button("🛒 Add All to Inventory"):
                                added_count = 0
                                for spec_name in recommendations:
                                    add_or_update_inventory(spec_name, 5)
                                    added_count += 1
                                
                                st.success(f"✅ Added {added_count} spectacles to inventory!")
                        
                        st.balloons()
                
                else:
                    st.error("❌ Failed to generate pricing table")
            
            else:
                st.error("❌ No valid analysis results available")
        
        else:
            st.info("📸 Please complete the camera analysis first to generate the report.")
            st.markdown("**Steps:**")
            st.markdown("1. Go to 'Patient & Prescription' tab and save patient info")
            st.markdown("2. Go to 'AI Camera Analysis' tab and capture photo")
            st.markdown("3. Return here to view the comprehensive report")

if __name__ == "__main__":
    main()