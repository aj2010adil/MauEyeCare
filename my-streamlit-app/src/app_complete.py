# MauEyeCare Complete App - With Real Data & Advanced Camera
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
from modules.real_spectacle_data import REAL_SPECTACLE_INVENTORY, get_recommendations_by_face_shape, search_frames_by_criteria
from modules.advanced_camera import FaceDetectionCamera, create_combined_photo_display, analyze_face_with_detection

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

def populate_real_inventory():
    """Populate inventory with real spectacle data"""
    for item_name, item_data in REAL_SPECTACLE_INVENTORY.items():
        # Add with random stock between 5-20
        import random
        stock = random.randint(5, 20)
        add_or_update_inventory(item_name, stock)

def main():
    st.title("👁️ MauEyeCare Optical Center")
    st.markdown("*Advanced Eye Care & Prescription Management System with Real Spectacle Data*")

    # Initialize real inventory on first run
    if st.sidebar.button("🔄 Load Real Spectacle Inventory"):
        with st.spinner("Loading real spectacle data from popular brands..."):
            populate_real_inventory()
        st.success(f"Loaded {len(REAL_SPECTACLE_INVENTORY)} real spectacle items!")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Prescription & Patient", "📦 Professional Inventory", "📊 Patient History", "🤖 AI Spectacle Assistant"])

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

    # --- Professional Inventory Tab ---
    with tab2:
        st.header("📦 Professional Spectacle Inventory")
        st.markdown("*Real data from Ray-Ban, Oakley, Warby Parker, Gucci, and more*")
        
        # Inventory filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox("Filter by Category", 
                ["All", "Sunglasses", "Prescription", "Luxury", "Budget", "Progressive", "Kids", "Safety"])
        
        with col2:
            price_filter = st.selectbox("Filter by Price Range", 
                ["All", "Budget (<$50)", "Mid-range ($50-$200)", "Premium (>$200)"])
        
        with col3:
            material_filter = st.selectbox("Filter by Material", 
                ["All", "Metal", "Acetate", "Plastic", "Titanium", "O-Matter"])
        
        # Get filtered inventory
        inventory_db = get_inventory_dict()
        
        # Create enhanced inventory display
        if inventory_db:
            inventory_data = []
            for item_name, stock in inventory_db.items():
                if item_name in REAL_SPECTACLE_INVENTORY:
                    item_info = REAL_SPECTACLE_INVENTORY[item_name]
                    inventory_data.append({
                        "Item": item_name,
                        "Stock": stock,
                        "Price": f"${item_info['price']}",
                        "Category": item_info['category'],
                        "Material": item_info['material'],
                        "Shape": item_info['shape'],
                        "Status": 'Out of Stock' if stock == 0 else 'Low Stock' if stock < 5 else 'In Stock'
                    })
                else:
                    inventory_data.append({
                        "Item": item_name,
                        "Stock": stock,
                        "Price": "N/A",
                        "Category": "Custom",
                        "Material": "N/A",
                        "Shape": "N/A",
                        "Status": 'Out of Stock' if stock == 0 else 'Low Stock' if stock < 5 else 'In Stock'
                    })
            
            df = pd.DataFrame(inventory_data)
            
            # Apply filters
            if category_filter != "All":
                df = df[df['Category'] == category_filter]
            
            if price_filter != "All":
                if price_filter == "Budget (<$50)":
                    df = df[df['Price'].str.replace('$', '').str.replace('N/A', '0').astype(float) < 50]
                elif price_filter == "Mid-range ($50-$200)":
                    prices = df['Price'].str.replace('$', '').str.replace('N/A', '0').astype(float)
                    df = df[(prices >= 50) & (prices <= 200)]
                elif price_filter == "Premium (>$200)":
                    df = df[df['Price'].str.replace('$', '').str.replace('N/A', '0').astype(float) > 200]
            
            if material_filter != "All":
                df = df[df['Material'].str.contains(material_filter, na=False)]
            
            # Display filtered inventory
            st.dataframe(df, use_container_width=True)
            
            # Inventory statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Items", len(df))
            with col2:
                st.metric("In Stock", len(df[df['Status'] == 'In Stock']))
            with col3:
                st.metric("Low Stock", len(df[df['Status'] == 'Low Stock']))
            with col4:
                st.metric("Out of Stock", len(df[df['Status'] == 'Out of Stock']))

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

    # --- AI Spectacle Assistant Tab ---
    with tab4:
        st.header("🤖 AI Spectacle Assistant")
        st.markdown("*Advanced face analysis with real spectacle recommendations*")
        
        # Advanced Camera System
        st.subheader("📸 Professional Face Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Guided Camera Capture**")
            st.info("📋 **Instructions:**\n• Position face in the green oval\n• Look directly at camera\n• Ensure good lighting\n• Remove existing glasses")
            
            if st.button("📷 Start Guided Camera Capture", type="primary"):
                try:
                    camera = FaceDetectionCamera()
                    
                    with st.spinner("Initializing camera with face detection..."):
                        captured_image, message = camera.capture_with_guidance()
                    
                    if captured_image is not None:
                        st.success(message)
                        st.session_state['professional_photo'] = captured_image
                        
                        # Analyze face immediately
                        face_analysis = analyze_face_with_detection(captured_image)
                        st.session_state['face_analysis_pro'] = face_analysis
                        
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"Camera system error: {str(e)}")
                    st.info("Ensure opencv-python is installed and camera permissions are granted")
        
        with col2:
            st.markdown("**Upload Photo Alternative**")
            uploaded_file = st.file_uploader("Upload clear front-facing photo", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                st.session_state['professional_photo'] = image_array
                
                # Analyze uploaded photo
                face_analysis = analyze_face_with_detection(image_array)
                st.session_state['face_analysis_pro'] = face_analysis
                
                st.image(image, caption="Uploaded Photo", width=300)
        
        # Professional Analysis Results
        if 'professional_photo' in st.session_state and 'face_analysis_pro' in st.session_state:
            st.markdown("---")
            st.subheader("🔍 Professional Analysis Results")
            
            analysis = st.session_state['face_analysis_pro']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(st.session_state['professional_photo'], caption="Analyzed Photo", width=400)
                
                # Analysis metrics
                st.metric("Face Shape", analysis['shape'])
                st.metric("Detection Confidence", f"{analysis['confidence']:.1f}%")
                
                if analysis['face_coords']:
                    x, y, w, h = analysis['face_coords']
                    st.metric("Face Area", f"{w}x{h} pixels")
            
            with col2:
                if 'patient_name' in st.session_state:
                    patient_name = st.session_state['patient_name']
                    age = st.session_state.get('age', 30)
                    gender = st.session_state.get('gender', 'Male')
                    
                    # Get prescription strength
                    rx_table = st.session_state.get('rx_table', {})
                    od_sphere = rx_table.get('OD', {}).get('Sphere', '')
                    os_sphere = rx_table.get('OS', {}).get('Sphere', '')
                    
                    prescription_strength = "No prescription"
                    if od_sphere or os_sphere:
                        max_power = max([abs(float(s.replace('+', '').replace('-', ''))) for s in [od_sphere, os_sphere] if s], default=0)
                        if max_power > 3:
                            prescription_strength = "Strong"
                        elif max_power > 1:
                            prescription_strength = "Moderate"
                        else:
                            prescription_strength = "Mild"
                    
                    # Get professional recommendations
                    recommendations = get_recommendations_by_face_shape(
                        analysis['shape'], age, gender, prescription_strength
                    )
                    
                    st.markdown("**🎯 Personalized Recommendations:**")
                    
                    # Best frames for face shape
                    st.markdown("**Best Frames for Your Face:**")
                    best_frames = recommendations['face_shape_recs']['best_frames']
                    
                    for frame in best_frames:
                        if frame in REAL_SPECTACLE_INVENTORY:
                            frame_info = REAL_SPECTACLE_INVENTORY[frame]
                            col_frame, col_price, col_add = st.columns([3, 1, 1])
                            
                            with col_frame:
                                st.write(f"• **{frame}**")
                                st.caption(f"{frame_info['material']} | {frame_info['category']}")
                            
                            with col_price:
                                st.write(f"${frame_info['price']}")
                            
                            with col_add:
                                if st.button("➕", key=f"add_rec_{frame}", help=f"Add {frame}"):
                                    add_or_update_inventory(frame, 5)
                                    st.success("Added!")
                    
                    # Age and gender considerations
                    st.markdown("**Age & Style Considerations:**")
                    for consideration in recommendations['age_considerations']:
                        st.write(f"• {consideration}")
                    
                    st.markdown("**Gender Preferences:**")
                    for preference in recommendations['gender_preferences']:
                        st.write(f"• {preference}")
                    
                    # Prescription notes
                    if prescription_strength != "No prescription":
                        st.markdown("**Prescription Considerations:**")
                        for note in recommendations['prescription_notes']:
                            st.write(f"• {note}")
                    
                    # Combined photo display
                    if st.button("🖼️ Generate Combined Analysis Report"):
                        combined_image = create_combined_photo_display(
                            st.session_state['professional_photo'],
                            analysis,
                            best_frames
                        )
                        
                        st.image(combined_image, caption="Professional Analysis Report", use_column_width=True)
                        
                        # Download combined report
                        img_buffer = BytesIO()
                        combined_image.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                        st.download_button(
                            label="📄 Download Analysis Report",
                            data=img_buffer.getvalue(),
                            file_name=f"Face_Analysis_{patient_name.replace(' ', '_')}_{timestamp}.png",
                            mime="image/png"
                        )
                
                else:
                    st.info("Please select a patient first for personalized recommendations")
        
        # Spectacle Search Tool
        st.markdown("---")
        st.subheader("🔍 Advanced Spectacle Search")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_category = st.selectbox("Category", ["", "Sunglasses", "Prescription", "Luxury", "Budget"])
        
        with col2:
            search_material = st.selectbox("Material", ["", "Metal", "Acetate", "Plastic", "Titanium"])
        
        with col3:
            search_price = st.selectbox("Price Range", ["", "Budget", "Mid-range", "Premium"])
        
        if st.button("🔍 Search Spectacles"):
            search_results = search_frames_by_criteria("", search_material, search_price, search_category)
            
            if search_results:
                st.write(f"Found {len(search_results)} matching spectacles:")
                
                for frame_name, frame_info in list(search_results.items())[:10]:  # Show top 10
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{frame_name}**")
                        st.caption(f"{frame_info['material']} | {frame_info['shape']}")
                    
                    with col2:
                        st.write(f"${frame_info['price']}")
                    
                    with col3:
                        st.write(frame_info['category'])
                    
                    with col4:
                        if st.button("➕", key=f"search_add_{frame_name}", help=f"Add {frame_name}"):
                            add_or_update_inventory(frame_name, 5)
                            st.success("Added!")
            else:
                st.info("No spectacles found matching your criteria")

if __name__ == "__main__":
    main()