#!/usr/bin/env python
"""
Interactive Virtual Try-On: Patient selects spectacles from gallery and sees them on captured face
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime

def create_interactive_virtual_tryon_page():
    """Create interactive virtual try-on page where patients can select spectacles"""
    
    st.header("👓 Interactive Virtual Try-On")
    st.markdown("*Select spectacles from our gallery and see how they look on your face!*")
    
    # Check if patient photo is available
    if 'analysis_photo' not in st.session_state:
        st.warning("📸 Please capture your photo first in the 'AI Camera Analysis' tab")
        return
    
    patient_photo = st.session_state['analysis_photo']
    
    # Display patient photo
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📷 Your Photo")
        st.image(patient_photo, width=300)
        
        # Patient info if available
        if 'patient_name' in st.session_state:
            st.success(f"👤 {st.session_state['patient_name']}")
            st.info(f"Age: {st.session_state.get('age', 'N/A')}")
    
    with col2:
        st.markdown("### 👓 Virtual Try-On Preview")
        
        # Initialize selected spectacle
        if 'selected_tryon_spectacle' not in st.session_state:
            st.session_state['selected_tryon_spectacle'] = None
        
        # Show try-on result
        if st.session_state['selected_tryon_spectacle']:
            tryon_image = apply_spectacle_overlay(
                patient_photo, 
                st.session_state['selected_tryon_spectacle']
            )
            st.image(tryon_image, width=400)
            
            # Show spectacle details
            from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
            spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[st.session_state['selected_tryon_spectacle']]
            
            total_price = spec_data['price'] + spec_data['lens_price']
            st.markdown(f"**{spec_data['brand']} {spec_data['model']}**")
            st.markdown(f"**Price: ₹{total_price:,}**")
            st.markdown(f"Material: {spec_data['material']} | Shape: {spec_data['shape']}")
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🛒 Add to Cart"):
                    st.success("Added to cart!")
            
            with col_btn2:
                if st.button("📄 View Details"):
                    st.session_state['selected_product'] = st.session_state['selected_tryon_spectacle']
                    st.rerun()
            
            with col_btn3:
                if st.button("📱 Share Photo"):
                    st.info("Photo sharing feature coming soon!")
        
        else:
            st.info("👆 Select a spectacle from the gallery below to try it on!")
    
    # Spectacle Gallery for Selection
    st.markdown("---")
    st.markdown("### 🖼️ Select Spectacles to Try On")
    
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        category_filter = st.selectbox("Category", 
            ["All", "Luxury", "Mid-Range", "Indian", "Budget"], key="tryon_category")
    
    with col_filter2:
        shape_filter = st.selectbox("Shape", 
            ["All", "Rectangle", "Round", "Aviator", "Cat-Eye", "Square"], key="tryon_shape")
    
    with col_filter3:
        price_filter = st.selectbox("Price Range", 
            ["All", "Under ₹5,000", "₹5,000-15,000", "Above ₹15,000"], key="tryon_price")
    
    # Apply filters and display gallery
    display_tryon_gallery(category_filter, shape_filter, price_filter)
    
    # Quick try-on with recommended spectacles
    if 'comprehensive_recommendations' in st.session_state:
        st.markdown("---")
        st.markdown("### 🎯 Try Your Recommended Spectacles")
        
        recommendations = st.session_state['comprehensive_recommendations'][:6]
        
        cols = st.columns(3)
        
        for i, spec_name in enumerate(recommendations):
            with cols[i % 3]:
                from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
                from modules.real_spectacle_images import load_spectacle_image
                
                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                    spec_image = load_spectacle_image(spec_name)
                    
                    st.image(spec_image, width=150)
                    st.markdown(f"**{spec_data['brand']}**")
                    st.markdown(f"{spec_data['model']}")
                    
                    if st.button(f"👓 Try On", key=f"rec_tryon_{i}"):
                        st.session_state['selected_tryon_spectacle'] = spec_name
                        st.rerun()

def display_tryon_gallery(category_filter, shape_filter, price_filter):
    """Display spectacle gallery for try-on selection"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    from modules.real_spectacle_images import load_spectacle_image
    
    # Apply filters
    filtered_specs = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
    
    if category_filter != "All":
        filtered_specs = {k: v for k, v in filtered_specs.items() if v['category'] == category_filter}
    
    if shape_filter != "All":
        filtered_specs = {k: v for k, v in filtered_specs.items() if v['shape'] == shape_filter}
    
    if price_filter != "All":
        if "Under" in price_filter:
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] <= 5000}
        elif "5,000-15,000" in price_filter:
            filtered_specs = {k: v for k, v in filtered_specs.items() if 5000 < v['price'] <= 15000}
        elif "Above" in price_filter:
            filtered_specs = {k: v for k, v in filtered_specs.items() if v['price'] > 15000}
    
    # Display gallery
    st.markdown(f"**{len(filtered_specs)} spectacles found**")
    
    cols = st.columns(4)
    
    for i, (spec_name, spec_data) in enumerate(list(filtered_specs.items())[:12]):
        with cols[i % 4]:
            spec_image = load_spectacle_image(spec_name)
            st.image(spec_image, width=150)
            
            st.markdown(f"**{spec_data['brand']}**")
            st.markdown(f"{spec_data['model']}")
            
            total_price = spec_data['price'] + spec_data['lens_price']
            st.markdown(f"**₹{total_price:,}**")
            
            if st.button(f"👓 Try On", key=f"tryon_{i}"):
                st.session_state['selected_tryon_spectacle'] = spec_name
                st.rerun()

def apply_spectacle_overlay(patient_photo, spec_name):
    """Apply spectacle overlay on patient photo"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    
    if spec_name not in COMPREHENSIVE_SPECTACLE_DATABASE:
        return patient_photo
    
    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
    
    # Convert to PIL Image
    if isinstance(patient_photo, np.ndarray):
        patient_img = Image.fromarray(patient_photo)
    else:
        patient_img = patient_photo.copy()
    
    # Detect face for positioning
    patient_array = np.array(patient_img)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(patient_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Draw spectacles based on shape
        draw = ImageDraw.Draw(patient_img)
        
        # Calculate spectacle dimensions
        spec_width = int(w * 0.8)
        spec_height = int(h * 0.25)
        spec_x = x + (w - spec_width) // 2
        spec_y = y + int(h * 0.25)
        
        # Draw spectacle frame
        if spec_data['shape'] == 'Rectangle':
            draw_rectangle_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        elif spec_data['shape'] == 'Round':
            draw_round_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        elif spec_data['shape'] == 'Aviator':
            draw_aviator_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        elif spec_data['shape'] == 'Cat-Eye':
            draw_cateye_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        elif spec_data['shape'] == 'Square':
            draw_square_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        else:
            draw_rectangle_frame(draw, spec_x, spec_y, spec_width, spec_height, spec_data)
        
        # Add brand watermark
        add_brand_watermark(draw, patient_img, spec_data)
    
    return patient_img

def draw_rectangle_frame(draw, x, y, width, height, spec_data):
    """Draw rectangular spectacle frame"""
    frame_color = get_frame_color(spec_data['material'])
    frame_thickness = get_frame_thickness(spec_data['material'])
    
    lens_width = width // 2 - 15
    lens_height = height
    
    # Left lens
    draw.rectangle([x, y, x + lens_width, y + lens_height], 
                  outline=frame_color, width=frame_thickness)
    
    # Right lens
    right_x = x + width - lens_width
    draw.rectangle([right_x, y, right_x + lens_width, y + lens_height], 
                  outline=frame_color, width=frame_thickness)
    
    # Bridge
    bridge_y = y + lens_height // 3
    draw.line([x + lens_width, bridge_y, right_x, bridge_y], 
             fill=frame_color, width=frame_thickness)
    
    # Temples
    temple_y = y + lens_height // 3
    draw.line([x, temple_y, x - 25, temple_y], 
             fill=frame_color, width=frame_thickness)
    draw.line([x + width, temple_y, x + width + 25, temple_y], 
             fill=frame_color, width=frame_thickness)

def draw_round_frame(draw, x, y, width, height, spec_data):
    """Draw round spectacle frame"""
    frame_color = get_frame_color(spec_data['material'])
    frame_thickness = get_frame_thickness(spec_data['material'])
    
    radius = min(width // 4, height // 2)
    
    # Left lens
    left_center_x = x + radius + 10
    center_y = y + height // 2
    draw.ellipse([left_center_x - radius, center_y - radius,
                 left_center_x + radius, center_y + radius], 
                outline=frame_color, width=frame_thickness)
    
    # Right lens
    right_center_x = x + width - radius - 10
    draw.ellipse([right_center_x - radius, center_y - radius,
                 right_center_x + radius, center_y + radius], 
                outline=frame_color, width=frame_thickness)
    
    # Bridge
    draw.line([left_center_x + radius, center_y, 
              right_center_x - radius, center_y], 
             fill=frame_color, width=frame_thickness)
    
    # Temples
    draw.line([left_center_x - radius, center_y, 
              left_center_x - radius - 25, center_y], 
             fill=frame_color, width=frame_thickness)
    draw.line([right_center_x + radius, center_y, 
              right_center_x + radius + 25, center_y], 
             fill=frame_color, width=frame_thickness)

def draw_aviator_frame(draw, x, y, width, height, spec_data):
    """Draw aviator spectacle frame"""
    frame_color = get_frame_color(spec_data['material'])
    frame_thickness = get_frame_thickness(spec_data['material'])
    
    # Simplified aviator shape
    lens_width = width // 2 - 10
    
    # Left lens (teardrop shape approximation)
    left_points = [
        (x, y + height // 2),
        (x + lens_width // 2, y),
        (x + lens_width, y + height // 3),
        (x + lens_width - 5, y + height),
        (x + 5, y + height)
    ]
    
    # Right lens
    right_x = x + width - lens_width
    right_points = [
        (right_x + 5, y + height),
        (right_x + lens_width - 5, y + height),
        (right_x + lens_width, y + height // 3),
        (right_x + lens_width // 2, y),
        (right_x + lens_width, y + height // 2)
    ]
    
    # Draw frames
    for i in range(len(left_points)):
        start = left_points[i]
        end = left_points[(i + 1) % len(left_points)]
        draw.line([start, end], fill=frame_color, width=frame_thickness)
    
    for i in range(len(right_points)):
        start = right_points[i]
        end = right_points[(i + 1) % len(right_points)]
        draw.line([start, end], fill=frame_color, width=frame_thickness)

def draw_cateye_frame(draw, x, y, width, height, spec_data):
    """Draw cat-eye spectacle frame"""
    frame_color = get_frame_color(spec_data['material'])
    frame_thickness = get_frame_thickness(spec_data['material'])
    
    lens_width = width // 2 - 10
    
    # Left lens (cat-eye shape)
    left_points = [
        (x, y + height // 2),
        (x + lens_width // 3, y),
        (x + lens_width, y + height // 4),
        (x + lens_width - 5, y + height),
        (x + 5, y + height)
    ]
    
    # Right lens (cat-eye shape)
    right_x = x + width - lens_width
    right_points = [
        (right_x + 5, y + height),
        (right_x + lens_width - 5, y + height),
        (right_x + lens_width, y + height // 4),
        (right_x + 2 * lens_width // 3, y),
        (right_x + lens_width, y + height // 2)
    ]
    
    # Draw frames
    for i in range(len(left_points)):
        start = left_points[i]
        end = left_points[(i + 1) % len(left_points)]
        draw.line([start, end], fill=frame_color, width=frame_thickness)
    
    for i in range(len(right_points)):
        start = right_points[i]
        end = right_points[(i + 1) % len(right_points)]
        draw.line([start, end], fill=frame_color, width=frame_thickness)

def draw_square_frame(draw, x, y, width, height, spec_data):
    """Draw square spectacle frame"""
    frame_color = get_frame_color(spec_data['material'])
    frame_thickness = get_frame_thickness(spec_data['material'])
    
    lens_size = min(width // 2 - 15, height)
    
    # Left lens
    draw.rectangle([x, y, x + lens_size, y + lens_size], 
                  outline=frame_color, width=frame_thickness)
    
    # Right lens
    right_x = x + width - lens_size
    draw.rectangle([right_x, y, right_x + lens_size, y + lens_size], 
                  outline=frame_color, width=frame_thickness)
    
    # Bridge
    bridge_y = y + lens_size // 3
    draw.line([x + lens_size, bridge_y, right_x, bridge_y], 
             fill=frame_color, width=frame_thickness)
    
    # Temples
    temple_y = y + lens_size // 3
    draw.line([x, temple_y, x - 25, temple_y], 
             fill=frame_color, width=frame_thickness)
    draw.line([x + width, temple_y, x + width + 25, temple_y], 
             fill=frame_color, width=frame_thickness)

def get_frame_color(material):
    """Get frame color based on material"""
    color_map = {
        'Metal': 'gold',
        'Acetate': 'black',
        'Plastic': 'navy',
        'TR90': 'darkblue',
        'O-Matter': 'darkgreen'
    }
    return color_map.get(material, 'black')

def get_frame_thickness(material):
    """Get frame thickness based on material"""
    thickness_map = {
        'Metal': 3,
        'Acetate': 5,
        'Plastic': 4,
        'TR90': 3,
        'O-Matter': 4
    }
    return thickness_map.get(material, 4)

def add_brand_watermark(draw, image, spec_data):
    """Add brand watermark to the image"""
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Add brand name in corner
    brand_text = f"{spec_data['brand']} {spec_data['model']}"
    draw.text((10, image.height - 30), brand_text, fill='white', font=font)
    draw.text((9, image.height - 31), brand_text, fill='black', font=font)  # Shadow effect

def create_comparison_tryon(patient_photo, spec_names):
    """Create side-by-side comparison of multiple spectacles on patient"""
    
    if len(spec_names) < 2:
        return None
    
    comparison_images = []
    
    for spec_name in spec_names[:4]:  # Max 4 comparisons
        tryon_image = apply_spectacle_overlay(patient_photo, spec_name)
        comparison_images.append(tryon_image)
    
    # Create comparison grid
    if len(comparison_images) == 2:
        # Side by side
        total_width = comparison_images[0].width * 2
        total_height = comparison_images[0].height
        comparison_grid = Image.new('RGB', (total_width, total_height), 'white')
        
        comparison_grid.paste(comparison_images[0], (0, 0))
        comparison_grid.paste(comparison_images[1], (comparison_images[0].width, 0))
    
    elif len(comparison_images) >= 3:
        # 2x2 grid
        total_width = comparison_images[0].width * 2
        total_height = comparison_images[0].height * 2
        comparison_grid = Image.new('RGB', (total_width, total_height), 'white')
        
        comparison_grid.paste(comparison_images[0], (0, 0))
        comparison_grid.paste(comparison_images[1], (comparison_images[0].width, 0))
        comparison_grid.paste(comparison_images[2], (0, comparison_images[0].height))
        if len(comparison_images) > 3:
            comparison_grid.paste(comparison_images[3], (comparison_images[0].width, comparison_images[0].height))
    
    return comparison_grid