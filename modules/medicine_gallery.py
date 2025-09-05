#!/usr/bin/env python
"""
Medicine Gallery and Management System - Similar to Spectacle Features
"""
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import datetime

def create_medicine_gallery_page():
    """Create comprehensive medicine gallery similar to spectacle gallery"""
    
    st.header("💊 Complete Medicine Gallery")
    st.markdown("*Browse our comprehensive medicine collection with detailed information*")
    
    from modules.comprehensive_medicine_database import (
        COMPREHENSIVE_MEDICINE_DATABASE,
        get_medicines_by_category,
        get_medicines_by_price_range,
        get_medicines_by_type,
        get_prescription_required_medicines,
        get_otc_medicines
    )
    
    # Advanced filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.selectbox("Category", 
            ["All", "Antibiotic", "Steroid", "Glaucoma", "Lubricant", "Antihistamine", "NSAID", "Analgesic", "Vitamin", "Supplement"])
    
    with col2:
        type_filter = st.selectbox("Type", 
            ["All", "Eye Drops", "Tablet", "Capsule", "Ointment"])
    
    with col3:
        prescription_filter = st.selectbox("Prescription", 
            ["All", "Prescription Required", "Over-the-Counter"])
    
    with col4:
        price_range_filter = st.selectbox("Price Range", 
            ["All", "Under ₹100", "₹100-300", "Above ₹300"])
    
    # Apply filters
    filtered_medicines = COMPREHENSIVE_MEDICINE_DATABASE.copy()
    
    if category_filter != "All":
        filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['category'] == category_filter}
    
    if type_filter != "All":
        filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['type'] == type_filter}
    
    if prescription_filter == "Prescription Required":
        filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['prescription_required']}
    elif prescription_filter == "Over-the-Counter":
        filtered_medicines = {k: v for k, v in filtered_medicines.items() if not v['prescription_required']}
    
    if price_range_filter != "All":
        if "Under" in price_range_filter:
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['price'] < 100}
        elif "100-300" in price_range_filter:
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if 100 <= v['price'] <= 300}
        elif "Above" in price_range_filter:
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v['price'] > 300}
    
    # Display gallery
    st.markdown(f"### 💊 Medicine Gallery ({len(filtered_medicines)} medicines found)")
    
    # Create medicine cards
    cols = st.columns(3)
    
    for i, (med_name, med_data) in enumerate(list(filtered_medicines.items())[:12]):
        with cols[i % 3]:
            # Create medicine card
            create_medicine_card(med_name, med_data, i)

def create_medicine_card(med_name, med_data, index):
    """Create individual medicine card"""
    
    # Medicine image placeholder (you can add real images later)
    med_image = create_medicine_image(med_data)
    st.image(med_image, width=200)
    
    # Medicine name
    st.markdown(f"**{med_name}**")
    
    # Price and basic info
    st.markdown(f"**₹{med_data['price']}** | {med_data['volume']}")
    
    # Category and type
    category_color = get_category_color(med_data['category'])
    st.markdown(f"<span style='background-color: {category_color}; padding: 2px 8px; border-radius: 10px; color: white; font-size: 12px;'>{med_data['category']}</span> | {med_data['type']}", unsafe_allow_html=True)
    
    # Prescription status
    if med_data['prescription_required']:
        st.markdown("🔒 **Prescription Required**")
    else:
        st.markdown("✅ **Over-the-Counter**")
    
    # Manufacturer
    st.markdown(f"*{med_data['manufacturer']}*")
    
    # View details button
    if st.button(f"📋 View Details", key=f"med_view_{index}"):
        st.session_state['selected_medicine'] = med_name
        st.rerun()

def create_medicine_image(med_data):
    """Create medicine image based on type and category"""
    
    # Create image based on medicine type
    img = Image.new('RGB', (200, 150), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Background color based on category
    bg_color = get_category_color(med_data['category'])
    draw.rectangle([0, 0, 200, 150], fill=bg_color)
    
    # Draw medicine type icon
    if med_data['type'] == 'Eye Drops':
        # Draw bottle shape
        draw.rectangle([70, 30, 130, 120], fill='white', outline='black', width=2)
        draw.rectangle([80, 20, 120, 35], fill='blue', outline='black', width=1)
        draw.text((85, 130), "EYE DROPS", fill='white', font=small_font)
    
    elif med_data['type'] in ['Tablet', 'Capsule']:
        # Draw pill shapes
        for i in range(3):
            for j in range(2):
                x = 60 + i * 30
                y = 50 + j * 30
                if med_data['type'] == 'Tablet':
                    draw.ellipse([x, y, x+20, y+20], fill='white', outline='black', width=1)
                else:
                    draw.rectangle([x, y, x+20, y+15], fill='white', outline='black', width=1)
        draw.text((75, 130), med_data['type'].upper(), fill='white', font=small_font)
    
    elif med_data['type'] == 'Ointment':
        # Draw tube shape
        draw.rectangle([60, 40, 140, 100], fill='white', outline='black', width=2)
        draw.rectangle([90, 30, 110, 45], fill='red', outline='black', width=1)
        draw.text((75, 130), "OINTMENT", fill='white', font=small_font)
    
    # Add price
    draw.text((10, 10), f"₹{med_data['price']}", fill='yellow', font=font)
    
    return img

def get_category_color(category):
    """Get color based on medicine category"""
    color_map = {
        'Antibiotic': '#FF6B6B',      # Red
        'Steroid': '#4ECDC4',         # Teal
        'Glaucoma': '#45B7D1',        # Blue
        'Lubricant': '#96CEB4',       # Green
        'Antihistamine': '#FFEAA7',   # Yellow
        'NSAID': '#DDA0DD',           # Plum
        'Analgesic': '#98D8C8',       # Mint
        'Vitamin': '#F7DC6F',         # Light Yellow
        'Supplement': '#BB8FCE'       # Light Purple
    }
    return color_map.get(category, '#95A5A6')  # Default gray

def create_medicine_details_page(med_name):
    """Create detailed medicine page similar to product pages"""
    
    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
    
    if med_name not in COMPREHENSIVE_MEDICINE_DATABASE:
        st.error("Medicine not found")
        return
    
    med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
    
    st.title(f"💊 {med_name}")
    st.markdown(f"*{med_data['manufacturer']} | {med_data['type']} | {med_data['volume']}*")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Medicine image
        med_image = create_medicine_image(med_data)
        st.image(med_image, width=300)
        
        # Key information
        st.markdown("### 📋 Key Information")
        
        info_data = {
            "Category": med_data['category'],
            "Type": med_data['type'],
            "Volume/Quantity": med_data['volume'],
            "Manufacturer": med_data['manufacturer'],
            "Prescription Required": "Yes" if med_data['prescription_required'] else "No",
            "Storage": med_data['storage'],
            "Expiry": f"{med_data['expiry_months']} months",
            "Generic Available": "Yes" if med_data['generic_available'] else "No"
        }
        
        for key, value in info_data.items():
            st.markdown(f"**{key}:** {value}")
    
    with col2:
        # Pricing
        st.markdown("### 💰 Pricing")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h2 style="color: #1f77b4; margin: 0;">₹{med_data['price']}</h2>
            <p style="margin: 5px 0;">{med_data['volume']}</p>
            <p style="color: #28a745; font-weight: bold;">✅ {med_data['availability']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clinical information
        st.markdown("### 🏥 Clinical Information")
        
        clinical_info = {
            "Indication": med_data['indication'],
            "Dosage": med_data['dosage'],
            "Side Effects": med_data['side_effects'],
            "Contraindications": med_data['contraindications']
        }
        
        for key, value in clinical_info.items():
            st.markdown(f"**{key}:** {value}")
        
        # Action buttons
        st.markdown("### 🛒 Actions")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🛒 Add to Prescription"):
                if 'selected_medicines' not in st.session_state:
                    st.session_state['selected_medicines'] = []
                if med_name not in st.session_state['selected_medicines']:
                    st.session_state['selected_medicines'].append(med_name)
                st.success("Added to prescription!")
        
        with col_btn2:
            if st.button("📋 Add to Inventory"):
                from modules.inventory_utils import add_or_update_inventory
                add_or_update_inventory(med_name, 10)  # Add 10 units
                st.success("Added to inventory!")
    
    # Detailed sections
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Description", "⚠️ Warnings", "🔬 Pharmacology", "💡 Tips"])
    
    with tab1:
        st.markdown("### Medicine Description")
        st.markdown(f"""
        **{med_name}** is a {med_data['category'].lower()} medication used for {med_data['indication'].lower()}.
        
        **Manufacturer:** {med_data['manufacturer']}
        
        **How it works:** This medication works by targeting specific pathways involved in {med_data['indication'].lower()}.
        
        **When to use:** {med_data['dosage']}
        """)
    
    with tab2:
        st.markdown("### Important Warnings")
        st.warning(f"**Contraindications:** {med_data['contraindications']}")
        st.info(f"**Side Effects:** {med_data['side_effects']}")
        
        if med_data['prescription_required']:
            st.error("🔒 **Prescription Required** - This medication requires a valid prescription from a licensed healthcare provider.")
    
    with tab3:
        st.markdown("### Pharmacological Information")
        st.markdown(f"""
        **Category:** {med_data['category']}
        
        **Formulation:** {med_data['type']}
        
        **Storage Requirements:** {med_data['storage']}
        
        **Shelf Life:** {med_data['expiry_months']} months from manufacture date
        """)
    
    with tab4:
        st.markdown("### Usage Tips")
        
        if med_data['type'] == 'Eye Drops':
            st.markdown("""
            **How to use eye drops:**
            1. Wash your hands thoroughly
            2. Tilt your head back and pull down lower eyelid
            3. Squeeze one drop into the pocket formed
            4. Close your eyes gently for 1-2 minutes
            5. Avoid touching the dropper tip to your eye
            """)
        elif med_data['type'] in ['Tablet', 'Capsule']:
            st.markdown("""
            **How to take tablets/capsules:**
            1. Take with a full glass of water
            2. Follow the prescribed dosage schedule
            3. Take with or without food as directed
            4. Do not crush or chew unless specified
            5. Complete the full course as prescribed
            """)
        
        st.info(f"💡 **Storage Tip:** Store at {med_data['storage']} conditions for optimal effectiveness.")

def create_medicine_comparison_page(medicine_names):
    """Create comparison page for multiple medicines"""
    
    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
    
    st.header("🔍 Medicine Comparison")
    
    if len(medicine_names) < 2:
        st.warning("Please select at least 2 medicines to compare")
        return
    
    # Create comparison table
    comparison_data = []
    
    for med_name in medicine_names:
        if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
            med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
            comparison_data.append({
                "Medicine": med_name,
                "Price (₹)": med_data['price'],
                "Category": med_data['category'],
                "Type": med_data['type'],
                "Volume": med_data['volume'],
                "Manufacturer": med_data['manufacturer'],
                "Prescription": "Yes" if med_data['prescription_required'] else "No",
                "Indication": med_data['indication'],
                "Dosage": med_data['dosage'],
                "Side Effects": med_data['side_effects']
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # Visual comparison
        st.markdown("### 📊 Price Comparison")
        
        cols = st.columns(len(medicine_names))
        
        for i, med_name in enumerate(medicine_names):
            with cols[i]:
                if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
                    med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
                    med_image = create_medicine_image(med_data)
                    
                    st.image(med_image, width=150)
                    st.markdown(f"**{med_data['manufacturer']}**")
                    st.markdown(f"**₹{med_data['price']}**")
                    
                    if st.button(f"Select {med_name.split('(')[0]}", key=f"select_{i}"):
                        st.success(f"Selected {med_name}!")

def create_medicine_recommendations_page():
    """Create medicine recommendations based on conditions"""
    
    st.header("🎯 Medicine Recommendations")
    st.markdown("*Get personalized medicine recommendations based on condition and patient profile*")
    
    from modules.comprehensive_medicine_database import get_medicine_recommendations_by_condition
    
    # Patient information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        condition = st.selectbox("Condition", [
            "dry_eyes", "bacterial_infection", "allergic_conjunctivitis", 
            "glaucoma", "inflammation"
        ])
    
    with col2:
        age = st.number_input("Patient Age", min_value=1, max_value=120, value=35)
    
    with col3:
        allergies = st.text_input("Known Allergies", placeholder="e.g., Penicillin")
    
    if st.button("🔍 Get Recommendations"):
        recommendations = get_medicine_recommendations_by_condition(condition, age)
        
        if recommendations:
            st.success(f"Found {len(recommendations)} recommended medicines for {condition.replace('_', ' ').title()}")
            
            cols = st.columns(3)
            
            for i, (med_name, med_data) in enumerate(recommendations.items()):
                with cols[i % 3]:
                    create_medicine_card(med_name, med_data, f"rec_{i}")
        else:
            st.warning("No specific recommendations found for this condition.")

def show_medicine_inventory_status():
    """Show current medicine inventory status"""
    
    st.header("📦 Medicine Inventory Status")
    
    from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
    from modules.inventory_utils import get_inventory_dict
    
    # Get current inventory
    current_inventory = get_inventory_dict()
    
    # Create inventory status
    inventory_status = []
    
    for med_name, med_data in COMPREHENSIVE_MEDICINE_DATABASE.items():
        current_stock = current_inventory.get(med_name, 0)
        
        # Determine status
        if current_stock == 0:
            status = "Out of Stock"
            status_color = "🔴"
        elif current_stock < 5:
            status = "Low Stock"
            status_color = "🟡"
        else:
            status = "In Stock"
            status_color = "🟢"
        
        inventory_status.append({
            "Medicine": med_name,
            "Current Stock": current_stock,
            "Status": f"{status_color} {status}",
            "Price (₹)": med_data['price'],
            "Category": med_data['category'],
            "Prescription Required": "Yes" if med_data['prescription_required'] else "No"
        })
    
    # Display inventory table
    df = pd.DataFrame(inventory_status)
    st.dataframe(df, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_medicines = len(inventory_status)
        st.metric("Total Medicines", total_medicines)
    
    with col2:
        in_stock = len([item for item in inventory_status if "In Stock" in item["Status"]])
        st.metric("In Stock", in_stock)
    
    with col3:
        low_stock = len([item for item in inventory_status if "Low Stock" in item["Status"]])
        st.metric("Low Stock", low_stock)
    
    with col4:
        out_of_stock = len([item for item in inventory_status if "Out of Stock" in item["Status"]])
        st.metric("Out of Stock", out_of_stock)