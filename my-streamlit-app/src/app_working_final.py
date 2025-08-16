# MauEyeCare Working Final App - Fixed AI Analysis
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
# from modules.pdf_utils import generate_pdf  # Removed PDF option
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from modules.enhanced_docx_utils import generate_professional_prescription_docx
from modules.ai_doctor_tools import analyze_symptoms_ai
from modules.enhanced_spectacle_data import (
    ENHANCED_SPECTACLE_DATA, 
    generate_pricing_table_data,
    create_comprehensive_report_image
)
# from modules.fixed_camera_analysis import trigger_immediate_analysis_workflow  # Disabled due to cv2 dependency
from modules.enhanced_medicine_ui import render_medicine_selection_ui, render_prescription_summary
from modules.enhanced_inventory_manager import enhanced_inventory
from modules.mcp_medicine_integration import mcp_integrator
from modules.spectacle_inventory_tool import spectacle_tool
from modules.ai_inventory_agent import ai_agent

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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Load Enhanced Spectacle Database"):
                with st.spinner("Loading enhanced spectacle database..."):
                    populate_enhanced_inventory()
                st.success(f"Loaded {len(ENHANCED_SPECTACLE_DATA)} premium spectacles!")
        
        with col2:
            if st.button("🏦 Load Premium Collection"):
                with st.spinner("Loading premium spectacle collection..."):
                    spectacle_tool.populate_inventory_from_database()
                st.success(f"Loaded {len(spectacle_tool.premium_spectacle_data)} premium spectacles!")
        
        st.markdown("---")
        st.markdown("**📊 System Stats:**")
        inventory_count = len(get_inventory_dict())
        st.metric("Inventory Items", inventory_count)
        st.metric("Spectacle Database", len(ENHANCED_SPECTACLE_DATA))
        st.metric("Premium Collection", len(spectacle_tool.premium_spectacle_data))
        
        # AI Agent Status
        st.markdown("**🤖 AI Agent Status:**")
        st.success("✅ AI Assistant Active")
        
        if st.button("🔍 Run AI Analysis"):
            with st.spinner("AI analyzing inventory..."):
                ai_report = ai_agent.auto_inventory_management()
            
            st.success("✅ AI Analysis Complete")
            
            if ai_report["alerts"]:
                for alert in ai_report["alerts"]:
                    st.warning(f"⚠️ {alert}")
            
            if ai_report["recommendations"]:
                st.info(f"💡 {len(ai_report['recommendations'])} AI recommendations available")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Patient & Prescription", "📦 Spectacle Inventory", "💊 Medicine Management", "📊 Patient History", "🤖 AI Assistant", "🔧 Advanced Tools"])

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
            
            # Medicine selection placeholder
            st.markdown("**💊 Medicine Selection**")
            st.info("💡 Medicine selection available after saving patient details")
            
            prescription = st.session_state.get('prescription', {})
            dosages = st.session_state.get('dosages', {})
            
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
        
        # Enhanced Medicine Selection (Outside Form)
        if st.session_state.get('patient_name'):
            st.markdown("---")
            st.markdown("**💊 Enhanced Medicine Selection & Management**")
            
            # Use the new enhanced medicine UI
            prescription, dosages = render_medicine_selection_ui()
            
            # Update session state
            if prescription:
                st.session_state['prescription'] = prescription
                st.session_state['dosages'] = dosages
                
                # Display prescription summary
                total_cost = render_prescription_summary(prescription, dosages)
                st.info(f"💰 Total Prescription Cost: ₹{total_cost}")

        # DOCX Generation Only
        if st.session_state.get('show_pdf', False) and st.session_state.get('prescription'):
            st.markdown("---")
            st.subheader("📄 Generate Prescription Document")
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            docx_file = generate_professional_prescription_docx(
                st.session_state['prescription'], "Dr Danish", 
                st.session_state['patient_name'], st.session_state['age'], 
                st.session_state['gender'], st.session_state['advice'], 
                st.session_state['rx_table'], [], st.session_state.get('dosages', {})
            )
            st.download_button(
                label="📄 Download Prescription (DOCX)",
                data=docx_file,
                file_name=f"RX_{st.session_state['patient_name'].replace(' ', '_')}_{timestamp}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
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

    # --- Medicine Management Tab ---
    with tab3:
        st.header("💊 Comprehensive Medicine Management")
        st.markdown("*Integrated medicine database with real-time inventory and external purchasing*")
        
        # Medicine management interface
        med_tab1, med_tab2, med_tab3 = st.tabs(["📊 Current Inventory", "🔍 Medicine Database", "📈 Analytics"])
        
        with med_tab1:
            st.subheader("Current Medicine Inventory")
            
            # Get all medicines with current stock
            all_medicines = enhanced_inventory.get_all_medicines(include_external=False)
            
            if all_medicines:
                medicine_data = []
                for med_name, med_data in all_medicines.items():
                    if med_data.get("current_stock", 0) > 0:  # Only show items in stock
                        medicine_data.append({
                            "Medicine": med_name,
                            "Category": med_data.get("category", "N/A"),
                            "Type": med_data.get("type", "N/A"),
                            "Stock": med_data.get("current_stock", 0),
                            "Price": f"₹{med_data.get('price', 0)}",
                            "Value": f"₹{med_data.get('current_stock', 0) * med_data.get('price', 0)}",
                            "Indication": med_data.get("indication", "N/A")[:50] + "..." if len(med_data.get("indication", "")) > 50 else med_data.get("indication", "N/A")
                        })
                
                if medicine_data:
                    df_medicines = pd.DataFrame(medicine_data)
                    st.dataframe(df_medicines, use_container_width=True)
                    
                    # Quick stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Medicines in Stock", len(medicine_data))
                    with col2:
                        total_value = sum([med_data.get("current_stock", 0) * med_data.get("price", 0) for med_data in all_medicines.values()])
                        st.metric("Total Inventory Value", f"₹{total_value:,.0f}")
                    with col3:
                        low_stock_count = len([med for med in all_medicines.values() if med.get("current_stock", 0) <= 5 and med.get("current_stock", 0) > 0])
                        st.metric("Low Stock Items", low_stock_count)
                else:
                    st.info("No medicines currently in stock. Use the Medicine Selection tab to add medicines.")
            else:
                st.info("No medicine data available. Please load the medicine database.")
        
        with med_tab2:
            st.subheader("Complete Medicine Database")
            
            # Load comprehensive database
            if st.button("🔄 Load Complete Medicine Database", type="primary"):
                with st.spinner("Loading comprehensive medicine database..."):
                    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
                    
                    # Add all medicines to inventory with 0 stock (for reference)
                    for med_name in COMPREHENSIVE_MEDICINE_DATABASE.keys():
                        try:
                            db.update_inventory(med_name, 0)  # Add with 0 stock
                        except:
                            pass  # Skip if already exists
                
                st.success(f"✅ Loaded {len(COMPREHENSIVE_MEDICINE_DATABASE)} medicines into database!")
                st.rerun()
            
            # Display database statistics
            from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Database Medicines", len(COMPREHENSIVE_MEDICINE_DATABASE))
            with col2:
                categories = set([med.get("category", "Unknown") for med in COMPREHENSIVE_MEDICINE_DATABASE.values()])
                st.metric("Categories", len(categories))
            with col3:
                prescription_required = sum([1 for med in COMPREHENSIVE_MEDICINE_DATABASE.values() if med.get("prescription_required", False)])
                st.metric("Prescription Required", prescription_required)
            
            # Show sample medicines by category
            if COMPREHENSIVE_MEDICINE_DATABASE:
                st.markdown("**Sample Medicines by Category:**")
                categories = set([med.get("category", "Unknown") for med in COMPREHENSIVE_MEDICINE_DATABASE.values()])
                
                for category in sorted(categories):
                    with st.expander(f"📂 {category}"):
                        category_meds = {name: data for name, data in COMPREHENSIVE_MEDICINE_DATABASE.items() 
                                       if data.get("category") == category}
                        
                        # Show first 5 medicines in this category
                        for i, (med_name, med_data) in enumerate(list(category_meds.items())[:5]):
                            st.write(f"• **{med_name}** - ₹{med_data.get('price', 0)} - {med_data.get('indication', 'N/A')}")
                        
                        if len(category_meds) > 5:
                            st.write(f"... and {len(category_meds) - 5} more medicines")
        
        with med_tab3:
            st.subheader("Medicine Analytics & Insights")
            
            # MCP Integration Status
            st.markdown("**🌐 MCP Integration Status**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("✅ MCP Medicine Integration: Active")
                st.info("🔗 Connected Sources: 1mg, NetMeds, PharmEasy, Apollo")
            
            with col2:
                if st.button("🔄 Refresh External Inventory", type="secondary"):
                    with st.spinner("Fetching real-time inventory data..."):
                        external_inventory = mcp_integrator.get_real_time_inventory()
                    
                    st.success("✅ External inventory refreshed!")
                    
                    # Show external availability
                    total_external = sum([len(medicines) for medicines in external_inventory.values()])
                    st.metric("External Medicines Available", total_external)
            
            # Show analytics
            st.markdown("**📊 Inventory Analytics**")
            
            # Generate and display inventory report
            if st.button("📈 Generate Analytics Report"):
                report_df = enhanced_inventory.generate_inventory_report()
                
                if not report_df.empty:
                    # Category distribution
                    category_counts = report_df['Category'].value_counts()
                    st.bar_chart(category_counts)
                    
                    # Stock status
                    stock_status = report_df['Status'].value_counts()
                    st.write("**Stock Status Distribution:**")
                    for status, count in stock_status.items():
                        st.write(f"• {status}: {count} items")

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

    # --- AI Spectacle Assistant Tab ---
    with tab5:
        st.header("🤖 AI Spectacle Assistant")
        st.markdown("*Advanced face analysis with instant spectacle recommendations*")
        
        # Check if patient is selected
        if 'patient_name' in st.session_state and st.session_state['patient_name']:
            patient_name = st.session_state['patient_name']
            age = st.session_state.get('age', 30)
            gender = st.session_state.get('gender', 'Male')
            
            st.success(f"👤 Patient Selected: {patient_name} | Age: {age} | Gender: {gender}")
            
            # Face Analysis (Simplified)
            st.markdown("---")
            st.subheader("👓 Spectacle Recommendations")
            
            # Manual face shape selection
            face_shapes = ["Round", "Square", "Oval", "Heart", "Diamond", "Oblong"]
            selected_face_shape = st.selectbox("Select Face Shape", face_shapes)
            
            if st.button("🎯 Get Spectacle Recommendations", type="primary"):
                # Get recommendations based on face shape
                recommended_spectacles = spectacle_tool.get_spectacles_by_face_shape(selected_face_shape)
                
                if recommended_spectacles:
                    st.success(f"✅ Found {len(recommended_spectacles)} recommended spectacles for {selected_face_shape} face")
                    
                    for spec_name, spec_data in list(recommended_spectacles.items())[:5]:  # Show top 5
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.write(f"**{spec_name}**")
                                st.write(f"{spec_data['brand']} | {spec_data['category']}")
                            
                            with col2:
                                total_price = spec_data['price'] + spec_data['lens_price']
                                st.write(f"**₹{total_price}**")
                            
                            with col3:
                                st.write(f"Shape: {spec_data['shape']}")
                else:
                    st.info("No specific recommendations found. Please check the spectacle inventory.")


        
        else:
            st.warning("⚠️ Please select a patient first in the 'Patient & Prescription' tab.")
            st.info("💡 Go to the first tab and fill in patient information to enable recommendations.")

if __name__ == "__main__":
    main()