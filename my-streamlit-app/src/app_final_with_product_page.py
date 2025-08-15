# MauEyeCare Final App with Professional Product Pages
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
from modules.real_spectacle_images import (
    display_spectacle_gallery,
    create_spectacle_comparison_table,
    show_spectacle_details_popup,
    create_virtual_try_on_display,
    download_spectacle_catalog,
    load_spectacle_image
)
from modules.professional_product_page import (
    create_professional_product_page,
    show_product_page_with_patient,
    create_product_comparison_page
)
from modules.interactive_virtual_tryon import (
    create_interactive_virtual_tryon_page,
    apply_spectacle_overlay,
    create_comparison_tryon
)
from modules.doctor_user_guide import (
    create_doctor_user_guide,
    create_feature_overview_page
)
from modules.medicine_gallery import (
    create_medicine_gallery_page,
    create_medicine_details_page,
    create_medicine_recommendations_page,
    show_medicine_inventory_status
)
try:
    from modules.web_scraper import scrape_fashioneyewear_rb3447, update_database_with_scraped_data
except ImportError:
    def scrape_fashioneyewear_rb3447():
        return None
    def update_database_with_scraped_data():
        return 0

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
    
    # Check if showing product page
    if 'selected_product' in st.session_state:
        patient_photo = st.session_state.get('analysis_photo', None)
        show_product_page_with_patient(st.session_state['selected_product'], patient_photo)
        return
    
    # Check if showing comparison page
    if st.session_state.get('show_comparison', False):
        comparison_products = st.session_state.get('comparison_products', [])
        create_product_comparison_page(comparison_products)
        
        if st.button("← Back to Main"):
            st.session_state['show_comparison'] = False
            st.rerun()
        return
    
    st.title("👁️ MauEyeCare Optical Center")
    st.markdown("*Complete AI-Powered Eye Care with Professional Product Pages*")
    st.markdown("**🇮🇳 Indian Pricing in ₹ | Real Images & Virtual Try-On**")

    # Sidebar
    with st.sidebar:
        st.header("🔧 System Controls")
        
        if st.button("🔄 Load Complete Database"):
            with st.spinner("Loading complete spectacle database..."):
                populate_comprehensive_inventory()
            st.success(f"Loaded {len(COMPREHENSIVE_SPECTACLE_DATABASE)} spectacles!")
        
        if st.button("🌐 Update from Web"):
            with st.spinner("Scraping latest data from websites..."):
                updated_count = update_database_with_scraped_data()
            st.success(f"Updated {updated_count} products from web!")
        
        st.markdown("---")
        st.markdown("**📊 Database Stats:**")
        
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.markdown("**👓 Spectacles:**")
            st.metric("Total", len(COMPREHENSIVE_SPECTACLE_DATABASE))
            
            # Price range stats
            budget_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] <= 5000])
            luxury_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] > 15000])
            
            st.metric("Budget", budget_count)
            st.metric("Luxury", luxury_count)
        
        with col_stat2:
            st.markdown("**💊 Medicines:**")
            
            try:
                from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
                st.metric("Total", len(COMPREHENSIVE_MEDICINE_DATABASE))
                
                # Medicine stats
                prescription_count = len([m for m in COMPREHENSIVE_MEDICINE_DATABASE.values() if m['prescription_required']])
                otc_count = len([m for m in COMPREHENSIVE_MEDICINE_DATABASE.values() if not m['prescription_required']])
                
                st.metric("Prescription", prescription_count)
                st.metric("OTC", otc_count)
            except:
                st.metric("Total", "Loading...")
        
        # Current patient info
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            st.markdown("---")
            st.markdown("**👤 Current Patient:**")
            st.success(f"**{st.session_state['patient_name']}**")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
            st.info(f"Gender: {st.session_state.get('gender', 'N/A')}")
        
        # Quick help section
        st.markdown("---")
        st.markdown("**🆘 Quick Help:**")
        
        if st.button("📚 User Guide"):
            st.session_state['show_user_guide'] = True
            st.rerun()
        
        if st.button("🔍 Feature List"):
            st.session_state['show_features'] = True
            st.rerun()
        
        st.markdown("📞 **Support:** +91 92356-47410")
        st.markdown("📧 **Email:** tech@maueyecare.com")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📋 Patient & Prescription", 
        "📦 Spectacle Gallery", 
        "💊 Medicine Gallery",
        "📊 Patient History", 
        "🤖 AI Camera Analysis",
        "📄 Analysis Report",
        "👓 Virtual Try-On",
        "🛍️ Professional Store",
        "🎯 Interactive Try-On",
        "📚 User Guide"
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
            
            # Medical Tests Section
            st.markdown("**🩺 Medical Tests**")
            col_test1, col_test2 = st.columns(2)
            
            with col_test1:
                blood_pressure = st.text_input("Blood Pressure", placeholder="e.g., 120/80")
                blood_sugar = st.text_input("Blood Sugar", placeholder="e.g., 95 mg/dL")
                complete_blood_test = st.text_input("Complete Blood Test", placeholder="Normal/Abnormal")
            
            with col_test2:
                viral_marker = st.text_input("Viral Marker", placeholder="Negative/Positive")
                fundus_examination = st.text_input("Fundus Examination", placeholder="Normal/Abnormal")
                iop = st.text_input("IOP (Intraocular Pressure)", placeholder="e.g., 15 mmHg")
            
            # Special Investigations
            st.markdown("**🔬 Special Investigations**")
            col_special1, col_special2 = st.columns(2)
            
            with col_special1:
                retinoscopy_dry = st.text_input("Retinoscopy (Dry)", placeholder="Results")
                retinoscopy_wet = st.text_input("Retinoscopy (Wet)", placeholder="Results")
            
            with col_special2:
                syringing = st.text_input("Syringing", placeholder="Patent/Blocked")
                other_tests = st.text_input("Other Tests", placeholder="Additional tests")
            
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
            
            # Store medical tests in session
            medical_tests = {
                "blood_pressure": blood_pressure,
                "blood_sugar": blood_sugar,
                "complete_blood_test": complete_blood_test,
                "viral_marker": viral_marker,
                "fundus_examination": fundus_examination,
                "iop": iop,
                "retinoscopy_dry": retinoscopy_dry,
                "retinoscopy_wet": retinoscopy_wet,
                "syringing": syringing,
                "other_tests": other_tests
            }
            
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
                    'rx_table': rx_table,
                    'medical_tests': medical_tests,
                    'show_pdf': True
                })
                
                st.success(f"✅ Patient {patient_name} saved successfully!")
                st.info("🎯 Now go to the 'AI Camera Analysis' tab to capture photo and get spectacle recommendations!")

    # --- Spectacle Gallery Tab ---
    with tab2:
        st.header("📦 Complete Spectacle Gallery")
        st.markdown("*Browse our complete collection with professional product pages*")
        
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
        
        # Display gallery with professional product page links
        st.markdown("### 🖼️ Professional Spectacle Gallery")
        
        cols = st.columns(4)
        
        for i, (spec_name, spec_data) in enumerate(list(filtered_specs.items())[:12]):
            with cols[i % 4]:
                # Load and display image
                spec_image = load_spectacle_image(spec_name)
                st.image(spec_image, width=200)
                
                # Product info
                st.markdown(f"**{spec_data['brand']} {spec_data['model']}**")
                total_price = spec_data['price'] + spec_data['lens_price']
                st.markdown(f"**₹{total_price:,}**")
                st.markdown(f"{spec_data['material']} | {spec_data['shape']}")
                
                # Professional product page button
                if st.button(f"👁️ View Details", key=f"view_{i}"):
                    st.session_state['selected_product'] = spec_name
                    st.rerun()

    # --- Medicine Gallery Tab ---
    with tab3:
        # Check if showing medicine details
        if 'selected_medicine' in st.session_state:
            create_medicine_details_page(st.session_state['selected_medicine'])
            
            if st.button("← Back to Medicine Gallery"):
                del st.session_state['selected_medicine']
                st.rerun()
        else:
            medicine_section = st.radio(
                "Select Section:",
                ["📦 Medicine Gallery", "🎯 Recommendations", "📊 Inventory Status"],
                horizontal=True
            )
            
            if medicine_section == "📦 Medicine Gallery":
                create_medicine_gallery_page()
            elif medicine_section == "🎯 Recommendations":
                create_medicine_recommendations_page()
            else:
                show_medicine_inventory_status()

    # --- Patient History Tab ---
    with tab4:
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
    with tab5:
        st.header("🤖 AI Camera Analysis & Spectacle Recommendations")
        st.markdown("*Advanced face analysis with professional product recommendations*")
        
        # Check if patient is selected
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            
            st.success(f"👤 **Current Patient:** {patient_name} | Age: {age} | Gender: {gender}")
            st.markdown("🔄 **Camera will open automatically below for instant AI analysis!**")
            
            # Camera capture - Auto-opens camera
            st.markdown("### 📷 AI Face Analysis Camera")
            st.info("🤖 **AI will automatically analyze your face shape and recommend the best spectacles!**")
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
                    
                    # Get comprehensive recommendations
                    comprehensive_recs = get_recommendations_by_face_shape_inr(
                        analysis_result['face_shape'], age, gender
                    )
                    
                    st.session_state['comprehensive_recommendations'] = list(comprehensive_recs.keys())[:8]
                    
                    # Show recommended spectacles with professional page links
                    st.markdown("### 👓 Recommended Spectacles")
                    
                    cols = st.columns(3)
                    
                    for i, spec_name in enumerate(st.session_state['comprehensive_recommendations'][:6]):
                        with cols[i % 3]:
                            if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                spec_image = load_spectacle_image(spec_name)
                                
                                st.image(spec_image, width=200)
                                st.markdown(f"**{spec_data['brand']} {spec_data['model']}**")
                                
                                total_price = spec_data['price'] + spec_data['lens_price']
                                st.markdown(f"**₹{total_price:,}**")
                                
                                if st.button(f"👁️ View Product Page", key=f"rec_view_{i}"):
                                    st.session_state['selected_product'] = spec_name
                                    st.rerun()
                
                else:
                    st.error(f"❌ Analysis Failed: {analysis_result['message']}")
        
        else:
            st.warning("⚠️ **Patient Required**")
            st.info("Please go to the **'Patient & Prescription'** tab first and enter patient information.")

    # --- Analysis Report Tab ---
    with tab6:
        st.header("📄 Comprehensive Analysis Report")
        
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
                    
                    # Show recommended spectacles with product page links
                    st.markdown("### 👓 Recommended Spectacles")
                    
                    cols = st.columns(3)
                    
                    for i, spec_name in enumerate(recommendations[:6]):
                        with cols[i % 3]:
                            if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                                spec_image = load_spectacle_image(spec_name)
                                
                                st.image(spec_image, width=200)
                                st.markdown(f"**{spec_data['brand']} {spec_data['model']}**")
                                
                                total_price = spec_data['price'] + spec_data['lens_price']
                                st.markdown(f"**₹{total_price:,}**")
                                
                                if st.button(f"🛍️ Shop Now", key=f"shop_{i}"):
                                    st.session_state['selected_product'] = spec_name
                                    st.rerun()
        
        else:
            st.info("📸 Please complete the camera analysis first to generate the report.")

    # --- Virtual Try-On Tab ---
    with tab7:
        st.header("👓 Virtual Try-On Experience")
        
        if ('analysis_photo' in st.session_state and 
            'comprehensive_recommendations' in st.session_state):
            
            patient_photo = st.session_state['analysis_photo']
            recommendations = st.session_state['comprehensive_recommendations']
            
            create_virtual_try_on_display(patient_photo, recommendations)
            
            # Professional product page links
            st.markdown("### 🛍️ Shop These Spectacles")
            
            cols = st.columns(3)
            
            for i, spec_name in enumerate(recommendations[:6]):
                with cols[i % 3]:
                    if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                        spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                        
                        if st.button(f"🛍️ {spec_data['brand']} {spec_data['model']}", key=f"tryshop_{i}"):
                            st.session_state['selected_product'] = spec_name
                            st.rerun()
        
        else:
            st.info("📸 Please complete the camera analysis first to enable virtual try-on.")

    # --- Professional Store Tab ---
    with tab8:
        st.header("🛍️ Professional Eyewear Store")
        st.markdown("*Premium shopping experience with detailed product pages*")
        
        # Featured products
        st.markdown("### ⭐ Featured Products")
        
        featured_products = [
            "Ray-Ban Aviator Classic RB3025",
            "Ray-Ban Wayfarer RB2140", 
            "Ray-Ban Round Metal RB3447",
            "Lenskart Air Classic Black"
        ]
        
        cols = st.columns(4)
        
        for i, spec_name in enumerate(featured_products):
            with cols[i]:
                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                    spec_image = load_spectacle_image(spec_name)
                    
                    st.image(spec_image, width=180)
                    st.markdown(f"**{spec_data['brand']}**")
                    st.markdown(f"{spec_data['model']}")
                    
                    total_price = spec_data['price'] + spec_data['lens_price']
                    st.markdown(f"**₹{total_price:,}**")
                    
                    if st.button(f"🛍️ Shop Now", key=f"featured_{i}"):
                        st.session_state['selected_product'] = spec_name
                        st.rerun()
        
        # Categories
        st.markdown("### 📂 Shop by Category")
        
        category_cols = st.columns(4)
        categories = ["Luxury", "Indian", "Budget", "Progressive"]
        
        for i, category in enumerate(categories):
            with category_cols[i]:
                category_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['category'] == category])
                
                if st.button(f"{category}\n({category_count} items)", key=f"cat_{i}"):
                    st.session_state['category_filter'] = category
                    st.rerun()
        
        # Latest arrivals
        st.markdown("### 🆕 Latest Arrivals")
        st.info("Check out our newest collection with the latest trends and technology!")
        
        # Web scraping update
        st.markdown("### 🌐 Live Product Updates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Update Ray-Ban RB3447 from Web"):
                with st.spinner("Fetching latest data from Fashion Eyewear..."):
                    scraped_data = scrape_fashioneyewear_rb3447()
                    if scraped_data:
                        st.success("✅ Updated Ray-Ban RB3447 with latest web data!")
                        st.json(scraped_data)
                    else:
                        st.error("❌ Failed to fetch data from web")
        
        with col2:
            if st.button("📊 View Product Analytics"):
                st.info("Product analytics and trends coming soon!")

    # --- Interactive Try-On Tab ---
    with tab9:
        create_interactive_virtual_tryon_page()

    # --- User Guide Tab ---
    with tab10:
        guide_type = st.radio(
            "Select Guide Type:",
            ["📚 Complete User Guide", "🔍 Feature Overview"],
            horizontal=True
        )
        
        if guide_type == "📚 Complete User Guide":
            create_doctor_user_guide()
        else:
            create_feature_overview_page()

if __name__ == "__main__":
    main()