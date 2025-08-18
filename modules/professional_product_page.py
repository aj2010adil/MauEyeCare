#!/usr/bin/env python
"""
Professional product page similar to Fashion Eyewear with patient try-on
"""
import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import numpy as np
import cv2

def create_professional_product_page(spec_name, patient_photo=None):
    """Create a professional product page similar to Fashion Eyewear"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    from modules.real_spectacle_images import load_spectacle_image
    
    if spec_name not in COMPREHENSIVE_SPECTACLE_DATABASE:
        st.error("Spectacle not found in database")
        return
    
    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
    
    # Page header
    st.markdown(f"# {spec_data['brand']} {spec_data['model']}")
    st.markdown(f"*{spec_data['description']}*")
    
    # Main product section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Product images section
        st.markdown("### 📸 Product Images")
        
        # Load main product image
        main_image = load_spectacle_image(spec_name)
        st.image(main_image, caption=f"{spec_data['brand']} {spec_data['model']}", width=400)
        
        # Additional product views (if available)
        image_tabs = st.tabs(["Front View", "Side View", "Top View", "Details"])
        
        with image_tabs[0]:
            st.image(main_image, width=350)
        
        with image_tabs[1]:
            # Create side view (placeholder)
            side_view = create_side_view_image(main_image, spec_data)
            st.image(side_view, width=350)
        
        with image_tabs[2]:
            # Create top view (placeholder)
            top_view = create_top_view_image(main_image, spec_data)
            st.image(top_view, width=350)
        
        with image_tabs[3]:
            # Show detailed specifications
            display_detailed_specs(spec_data)
    
    with col2:
        # Product information and pricing
        st.markdown("### 💰 Pricing & Details")
        
        # Price display
        total_price = spec_data['price'] + spec_data['lens_price']
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h2 style="color: #1f77b4; margin: 0;">₹{total_price:,}</h2>
            <p style="margin: 5px 0;">Frame: ₹{spec_data['price']:,} + Lens: ₹{spec_data['lens_price']:,}</p>
            <p style="color: #28a745; font-weight: bold;">✅ {spec_data['availability']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Product specifications
        st.markdown("### 📋 Specifications")
        
        specs_col1, specs_col2 = st.columns(2)
        
        with specs_col1:
            st.markdown(f"**Brand:** {spec_data['brand']}")
            st.markdown(f"**Model:** {spec_data['model']}")
            st.markdown(f"**Shape:** {spec_data['shape']}")
            st.markdown(f"**Material:** {spec_data['material']}")
        
        with specs_col2:
            st.markdown(f"**Category:** {spec_data['category']}")
            st.markdown(f"**Delivery:** {spec_data['delivery_days']} days")
            st.markdown(f"**Source:** {spec_data['source']}")
            st.markdown(f"**Collected:** {spec_data['collected_date']}")
        
        # Size options (if available)
        st.markdown("### 📏 Size Options")
        size_options = ["Small (47mm)", "Medium (50mm)", "Large (53mm)"]
        selected_size = st.selectbox("Choose Size", size_options)
        
        # Color options
        st.markdown("### 🎨 Color Options")
        color_options = ["Gold/Green", "Black/Grey", "Silver/Blue"]
        selected_color = st.selectbox("Choose Color", color_options)
        
        # Lens options
        st.markdown("### 👁️ Lens Options")
        lens_options = ["Single Vision", "Progressive", "Bifocal", "Sunglasses"]
        selected_lens = st.selectbox("Choose Lens Type", lens_options)
        
        # Add to cart section
        st.markdown("### 🛒 Purchase Options")
        
        quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)
        
        col_cart1, col_cart2 = st.columns(2)
        
        with col_cart1:
            if st.button("🛒 Add to Cart", type="primary"):
                from modules.inventory_utils import add_or_update_inventory
                add_or_update_inventory(spec_name, quantity)
                st.success(f"Added {quantity} x {spec_data['brand']} {spec_data['model']} to cart!")
        
        with col_cart2:
            if st.button("❤️ Add to Wishlist"):
                st.success("Added to wishlist!")
    
    # Patient try-on section
    if patient_photo is not None:
        st.markdown("---")
        st.markdown("### 👤 Virtual Try-On")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Photo**")
            st.image(patient_photo, width=300)
        
        with col2:
            st.markdown("**With Spectacles**")
            try_on_image = create_virtual_try_on(patient_photo, spec_data, main_image)
            st.image(try_on_image, width=300)
        
        # Try-on feedback
        st.markdown("### 💭 How does it look?")
        feedback_col1, feedback_col2, feedback_col3 = st.columns(3)
        
        with feedback_col1:
            if st.button("👍 Looks Great!"):
                st.success("Great choice! This style suits you well.")
        
        with feedback_col2:
            if st.button("🤔 Not Sure"):
                st.info("Try different colors or sizes to find your perfect match.")
        
        with feedback_col3:
            if st.button("👎 Not for Me"):
                st.warning("No worries! Check out our other recommendations.")
    
    # Product reviews section
    st.markdown("---")
    st.markdown("### ⭐ Customer Reviews")
    
    display_customer_reviews(spec_data)
    
    # Related products
    st.markdown("---")
    st.markdown("### 🔗 You Might Also Like")
    
    display_related_products(spec_data)

def create_side_view_image(main_image, spec_data):
    """Create a side view representation of the spectacles"""
    
    # Create a side view placeholder
    side_img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(side_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw side view representation
    if spec_data['shape'] == 'Aviator':
        # Aviator side view
        draw.line([(50, 150), (350, 150)], fill='black', width=4)  # Temple
        draw.ellipse([80, 120, 150, 180], outline='black', width=3)  # Lens outline
        draw.text((160, 200), "Side View - Aviator Style", fill='black', font=font)
    
    elif spec_data['shape'] == 'Round':
        # Round side view
        draw.line([(50, 150), (350, 150)], fill='black', width=4)  # Temple
        draw.ellipse([80, 120, 150, 180], outline='black', width=3)  # Lens outline
        draw.text((160, 200), "Side View - Round Style", fill='black', font=font)
    
    else:
        # Default rectangular side view
        draw.line([(50, 150), (350, 150)], fill='black', width=4)  # Temple
        draw.rectangle([80, 130, 150, 170], outline='black', width=3)  # Lens outline
        draw.text((160, 200), "Side View - Classic Style", fill='black', font=font)
    
    # Add material info
    draw.text((50, 250), f"Material: {spec_data['material']}", fill='gray', font=font)
    
    return side_img

def create_top_view_image(main_image, spec_data):
    """Create a top view representation of the spectacles"""
    
    # Create a top view placeholder
    top_img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(top_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw top view representation
    # Left lens
    draw.ellipse([100, 120, 160, 180], outline='black', width=3)
    # Right lens
    draw.ellipse([240, 120, 300, 180], outline='black', width=3)
    # Bridge
    draw.line([(160, 150), (240, 150)], fill='black', width=3)
    # Temples
    draw.line([(100, 150), (50, 150)], fill='black', width=3)
    draw.line([(300, 150), (350, 150)], fill='black', width=3)
    
    draw.text((160, 200), "Top View", fill='black', font=font)
    draw.text((50, 250), f"Bridge Width: ~21mm", fill='gray', font=font)
    
    return top_img

def display_detailed_specs(spec_data):
    """Display detailed specifications"""
    
    st.markdown("**Detailed Specifications:**")
    
    # Create specifications table
    specs_data = {
        "Frame Width": "140mm (approx)",
        "Lens Width": "47-53mm",
        "Bridge Width": "21mm",
        "Temple Length": "140mm",
        "Frame Height": "44mm",
        "Weight": "25-30g",
        "UV Protection": "100% UV400",
        "Prescription Ready": "Yes",
        "Warranty": "24 months"
    }
    
    for spec, value in specs_data.items():
        st.markdown(f"• **{spec}:** {value}")

def create_virtual_try_on(patient_photo, spec_data, spectacle_image):
    """Create virtual try-on by overlaying spectacles on patient photo"""
    
    if isinstance(patient_photo, np.ndarray):
        patient_img = Image.fromarray(patient_photo)
    else:
        patient_img = patient_photo
    
    # Create a copy for try-on
    try_on_img = patient_img.copy()
    
    # Detect face for positioning
    patient_array = np.array(patient_img)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(patient_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Resize spectacle image to fit face
        spec_width = int(w * 0.8)
        spec_height = int(h * 0.3)
        
        # Resize spectacle image
        spectacle_resized = spectacle_image.resize((spec_width, spec_height))
        
        # Make spectacle background transparent (simple approach)
        spectacle_resized = spectacle_resized.convert("RGBA")
        
        # Position spectacles on face
        spec_x = x + (w - spec_width) // 2
        spec_y = y + int(h * 0.25)
        
        # Paste spectacles onto patient image
        try_on_img.paste(spectacle_resized, (spec_x, spec_y), spectacle_resized)
    
    return try_on_img

def display_customer_reviews(spec_data):
    """Display customer reviews section"""
    
    # Sample reviews (in a real app, these would come from a database)
    reviews = [
        {
            "name": "Rahul S.",
            "rating": 5,
            "review": "Excellent quality! The Ray-Ban RB3447 is exactly as described. Fast delivery and great customer service.",
            "date": "2024-01-10"
        },
        {
            "name": "Priya M.",
            "rating": 4,
            "review": "Love the classic round shape. Perfect for my face. Only wish it came in more color options.",
            "date": "2024-01-08"
        },
        {
            "name": "Amit K.",
            "rating": 5,
            "review": "Premium quality metal frame. Very comfortable to wear all day. Highly recommended!",
            "date": "2024-01-05"
        }
    ]
    
    # Display average rating
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
    st.markdown(f"**Average Rating: {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5) - {len(reviews)} reviews**")
    
    # Display individual reviews
    for review in reviews:
        with st.expander(f"{'⭐' * review['rating']} {review['name']} - {review['date']}"):
            st.write(review['review'])

def display_related_products(spec_data):
    """Display related products"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    from modules.real_spectacle_images import load_spectacle_image
    
    # Find related products (same brand or similar shape)
    related_products = []
    
    for name, data in COMPREHENSIVE_SPECTACLE_DATABASE.items():
        if (data['brand'] == spec_data['brand'] or data['shape'] == spec_data['shape']) and name != f"{spec_data['brand']} {spec_data['model']}":
            related_products.append(name)
    
    # Display up to 3 related products
    if related_products:
        cols = st.columns(min(3, len(related_products)))
        
        for i, related_name in enumerate(related_products[:3]):
            with cols[i]:
                related_data = COMPREHENSIVE_SPECTACLE_DATABASE[related_name]
                related_image = load_spectacle_image(related_name)
                
                st.image(related_image, width=150)
                st.markdown(f"**{related_data['brand']} {related_data['model']}**")
                
                total_price = related_data['price'] + related_data['lens_price']
                st.markdown(f"₹{total_price:,}")
                
                if st.button(f"View Details", key=f"related_{i}"):
                    st.session_state['selected_product'] = related_name
                    st.rerun()

def create_product_comparison_page(spec_names):
    """Create a comparison page for multiple spectacles"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    from modules.real_spectacle_images import load_spectacle_image
    
    st.markdown("# 🔍 Product Comparison")
    
    if len(spec_names) < 2:
        st.warning("Please select at least 2 products to compare")
        return
    
    # Create comparison table
    cols = st.columns(len(spec_names))
    
    for i, spec_name in enumerate(spec_names):
        with cols[i]:
            if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                
                # Product image
                spec_image = load_spectacle_image(spec_name)
                st.image(spec_image, width=200)
                
                # Product details
                st.markdown(f"### {spec_data['brand']} {spec_data['model']}")
                
                total_price = spec_data['price'] + spec_data['lens_price']
                st.markdown(f"**Price:** ₹{total_price:,}")
                st.markdown(f"**Shape:** {spec_data['shape']}")
                st.markdown(f"**Material:** {spec_data['material']}")
                st.markdown(f"**Category:** {spec_data['category']}")
                st.markdown(f"**Delivery:** {spec_data['delivery_days']} days")
                
                # Rating (placeholder)
                st.markdown("**Rating:** ⭐⭐⭐⭐⭐")
                
                if st.button(f"Choose This", key=f"choose_{i}"):
                    st.success(f"Selected {spec_data['brand']} {spec_data['model']}!")

def show_product_page_with_patient(spec_name, patient_photo=None):
    """Show complete product page with patient try-on"""
    
    # Check if product is selected
    if 'selected_product' in st.session_state:
        spec_name = st.session_state['selected_product']
    
    # Create the professional product page
    create_professional_product_page(spec_name, patient_photo)
    
    # Add navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Gallery"):
            if 'selected_product' in st.session_state:
                del st.session_state['selected_product']
            st.rerun()
    
    with col2:
        if st.button("🔍 Compare Products"):
            st.session_state['show_comparison'] = True
            st.rerun()
    
    with col3:
        if st.button("📞 Contact Us"):
            st.info("📞 Call: +91 92356-47410 | 📧 Email: info@maueyecare.com")