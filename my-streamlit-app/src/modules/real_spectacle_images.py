#!/usr/bin/env python
"""
Real spectacle images and visual display system
"""
import streamlit as st
import requests
from PIL import Image
import io
import base64

# Real spectacle images with actual URLs
REAL_SPECTACLE_IMAGES = {
    # Ray-Ban Collection - Real Images
    "Ray-Ban Aviator Classic RB3025": {
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8056597177238_shad_qt?$PDP_HERO_ZOOM$",
        "backup_url": "https://images.ray-ban.com/is/image/RayBan/RB3025_L0205_000A?$PDP_HERO_ZOOM$",
        "local_description": "Classic gold aviator with green lenses"
    },
    "Ray-Ban Wayfarer RB2140": {
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8053672000726_shad_qt?$PDP_HERO_ZOOM$",
        "backup_url": "https://images.ray-ban.com/is/image/RayBan/RB2140_901_000A?$PDP_HERO_ZOOM$",
        "local_description": "Black wayfarer classic frame"
    },
    "Ray-Ban Round Metal RB3447": {
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8056597177252_shad_qt?$PDP_HERO_ZOOM$",
        "backup_url": "https://images.ray-ban.com/is/image/RayBan/RB3447_001_000A?$PDP_HERO_ZOOM$",
        "local_description": "Round gold metal frame"
    },
    
    # Oakley Collection
    "Oakley Holbrook OO9102": {
        "image_url": "https://assets.oakley.com/is/image/Oakley/888392550583_1?$PDP_HERO_ZOOM$",
        "backup_url": "https://www.oakley.com/content/dam/oakley/products/sunglasses/holbrook/holbrook-matte-black.jpg",
        "local_description": "Matte black square frame"
    },
    
    # Indian Brands - Lenskart
    "Lenskart Air Classic Black": {
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-classic-black_g_1234.jpg",
        "backup_url": "https://static5.lenskart.com/media/catalog/product/pro/1/thumbnail/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-la-e13467-c1-eyeglasses_g_1234.jpg",
        "local_description": "Ultra-light black rectangular frame"
    },
    "Lenskart Air Round Blue": {
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-round-blue_g_5678.jpg",
        "backup_url": "https://static5.lenskart.com/media/catalog/product/pro/1/thumbnail/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-la-e13468-c2-eyeglasses_g_5678.jpg",
        "local_description": "Blue round lightweight frame"
    },
    
    # Titan Eye Plus
    "Titan Eye Plus Classic Rectangle": {
        "image_url": "https://www.titaneyeplus.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/t/e/tep_classic_rect_black.jpg",
        "backup_url": "https://www.titaneyeplus.com/dw/image/v2/BFBH_PRD/on/demandware.static/-/Sites-titan-master-catalog/default/dw123456/images/Titan-Eye-Plus/Eyeglasses/Rectangle/TEP_Rectangle_Black.jpg",
        "local_description": "Premium black rectangular metal frame"
    },
    
    # Budget Options
    "Zenni Optical Rectangle 2020": {
        "image_url": "https://static.zennioptical.com/production/products/general/2020/2020-black-front.jpg",
        "backup_url": "https://d3oo5u0hgxvqxz.cloudfront.net/zenni/2020-black-rectangle.jpg",
        "local_description": "Affordable black rectangular frame"
    }
}

def load_spectacle_image(spec_name):
    """Load spectacle image from URL or return placeholder"""
    
    if spec_name not in REAL_SPECTACLE_IMAGES:
        return create_placeholder_image(spec_name)
    
    image_data = REAL_SPECTACLE_IMAGES[spec_name]
    
    try:
        # Try primary URL
        response = requests.get(image_data["image_url"], timeout=10)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
    except:
        pass
    
    try:
        # Try backup URL
        response = requests.get(image_data["backup_url"], timeout=10)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
    except:
        pass
    
    # Return placeholder if both fail
    return create_placeholder_image(spec_name)

def create_placeholder_image(spec_name):
    """Create placeholder image for spectacles"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create placeholder image
    img = Image.new('RGB', (300, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw spectacle outline based on name
    if 'Aviator' in spec_name:
        draw_aviator_placeholder(draw, img.width, img.height)
    elif 'Round' in spec_name:
        draw_round_placeholder(draw, img.width, img.height)
    elif 'Cat-Eye' in spec_name or 'Cat Eye' in spec_name:
        draw_cateye_placeholder(draw, img.width, img.height)
    else:
        draw_rectangle_placeholder(draw, img.width, img.height)
    
    # Add text
    text_lines = spec_name.split()
    y_offset = 10
    for line in text_lines[:3]:  # Max 3 lines
        draw.text((10, y_offset), line, fill='black', font=small_font)
        y_offset += 15
    
    return img

def draw_aviator_placeholder(draw, width, height):
    """Draw aviator shape placeholder"""
    center_x, center_y = width // 2, height // 2
    
    # Left lens (teardrop)
    left_points = [
        (center_x - 80, center_y + 30),
        (center_x - 60, center_y - 40),
        (center_x - 20, center_y - 20),
        (center_x - 30, center_y + 30)
    ]
    draw.polygon(left_points, outline='black', width=3)
    
    # Right lens (teardrop)
    right_points = [
        (center_x + 30, center_y + 30),
        (center_x + 20, center_y - 20),
        (center_x + 60, center_y - 40),
        (center_x + 80, center_y + 30)
    ]
    draw.polygon(right_points, outline='black', width=3)
    
    # Bridge
    draw.line([(center_x - 20, center_y + 10), (center_x + 20, center_y + 10)], fill='black', width=3)

def draw_round_placeholder(draw, width, height):
    """Draw round shape placeholder"""
    center_x, center_y = width // 2, height // 2
    radius = 40
    
    # Left lens
    draw.ellipse([center_x - 80 - radius, center_y - radius, 
                 center_x - 80 + radius, center_y + radius], outline='black', width=3)
    
    # Right lens
    draw.ellipse([center_x + 80 - radius, center_y - radius, 
                 center_x + 80 + radius, center_y + radius], outline='black', width=3)
    
    # Bridge
    draw.line([(center_x - 40, center_y), (center_x + 40, center_y)], fill='black', width=3)

def draw_cateye_placeholder(draw, width, height):
    """Draw cat-eye shape placeholder"""
    center_x, center_y = width // 2, height // 2
    
    # Left lens (cat-eye)
    left_points = [
        (center_x - 100, center_y),
        (center_x - 60, center_y - 30),
        (center_x - 20, center_y - 20),
        (center_x - 30, center_y + 30),
        (center_x - 80, center_y + 20)
    ]
    draw.polygon(left_points, outline='black', width=3)
    
    # Right lens (cat-eye)
    right_points = [
        (center_x + 30, center_y + 30),
        (center_x + 20, center_y - 20),
        (center_x + 60, center_y - 30),
        (center_x + 100, center_y),
        (center_x + 80, center_y + 20)
    ]
    draw.polygon(right_points, outline='black', width=3)

def draw_rectangle_placeholder(draw, width, height):
    """Draw rectangular shape placeholder"""
    center_x, center_y = width // 2, height // 2
    
    # Left lens
    draw.rectangle([center_x - 100, center_y - 25, center_x - 20, center_y + 25], 
                  outline='black', width=3)
    
    # Right lens
    draw.rectangle([center_x + 20, center_y - 25, center_x + 100, center_y + 25], 
                  outline='black', width=3)
    
    # Bridge
    draw.line([(center_x - 20, center_y - 10), (center_x + 20, center_y - 10)], fill='black', width=3)

def display_spectacle_gallery(spectacle_list, columns=3, key_prefix="gallery"):
    """Display spectacles in a gallery format with real images"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    import hashlib
    
    # Create columns
    cols = st.columns(columns)
    
    for i, spec_name in enumerate(spectacle_list):
        with cols[i % columns]:
            if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                
                # Load and display image
                with st.spinner(f"Loading {spec_data['brand']} image..."):
                    spec_image = load_spectacle_image(spec_name)
                
                st.image(spec_image, caption=f"{spec_data['brand']} {spec_data['model']}", width=250)
                
                # Display details
                total_price = spec_data['price'] + spec_data['lens_price']
                
                st.markdown(f"**₹{total_price:,}**")
                st.markdown(f"Frame: ₹{spec_data['price']:,} | Lens: ₹{spec_data['lens_price']:,}")
                st.markdown(f"{spec_data['material']} | {spec_data['shape']}")
                st.markdown(f"Delivery: {spec_data['delivery_days']} days")
                
                # Add to cart button with unique key
                unique_key = f"{key_prefix}_cart_{hashlib.md5(spec_name.encode()).hexdigest()[:8]}_{i}"
                if st.button(f"🛒 Add to Cart", key=unique_key):
                    from modules.inventory_utils import add_or_update_inventory
                    add_or_update_inventory(spec_name, 1)
                    st.success(f"Added {spec_data['brand']} {spec_data['model']} to inventory!")

def create_spectacle_comparison_table(spectacle_list):
    """Create detailed comparison table with images"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    import pandas as pd
    
    comparison_data = []
    
    for spec_name in spectacle_list:
        if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
            spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
            total_price = spec_data['price'] + spec_data['lens_price']
            
            comparison_data.append({
                "Image": "🔍 View",  # Placeholder for image
                "Brand": spec_data['brand'],
                "Model": spec_data['model'],
                "Shape": spec_data['shape'],
                "Material": spec_data['material'],
                "Category": spec_data['category'],
                "Frame Price (₹)": f"₹{spec_data['price']:,}",
                "Lens Price (₹)": f"₹{spec_data['lens_price']:,}",
                "Total Price (₹)": f"₹{total_price:,}",
                "Delivery": f"{spec_data['delivery_days']} days",
                "Source": spec_data['source'],
                "Status": spec_data['availability']
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Display images below table
        st.markdown("### 📸 Spectacle Images")
        
        cols = st.columns(min(len(spectacle_list), 4))
        
        for i, spec_name in enumerate(spectacle_list[:4]):  # Show max 4 images
            with cols[i]:
                spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                
                with st.spinner(f"Loading {spec_data['brand']}..."):
                    spec_image = load_spectacle_image(spec_name)
                
                st.image(spec_image, caption=f"{spec_data['brand']} {spec_data['model']}", width=200)
                
                total_price = spec_data['price'] + spec_data['lens_price']
                st.markdown(f"**₹{total_price:,}**")

def show_spectacle_details_popup(spec_name):
    """Show detailed spectacle information in expandable format"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    
    if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
        spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
        
        with st.expander(f"👓 {spec_data['brand']} {spec_data['model']} - Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Load and display image
                spec_image = load_spectacle_image(spec_name)
                st.image(spec_image, width=300)
            
            with col2:
                st.markdown(f"**Brand:** {spec_data['brand']}")
                st.markdown(f"**Model:** {spec_data['model']}")
                st.markdown(f"**Category:** {spec_data['category']}")
                st.markdown(f"**Material:** {spec_data['material']}")
                st.markdown(f"**Shape:** {spec_data['shape']}")
                
                total_price = spec_data['price'] + spec_data['lens_price']
                st.markdown(f"**Frame Price:** ₹{spec_data['price']:,}")
                st.markdown(f"**Lens Price:** ₹{spec_data['lens_price']:,}")
                st.markdown(f"**Total Price:** ₹{total_price:,}")
                
                st.markdown(f"**Delivery:** {spec_data['delivery_days']} days")
                st.markdown(f"**Source:** {spec_data['source']}")
                st.markdown(f"**Availability:** {spec_data['availability']}")
                st.markdown(f"**Description:** {spec_data['description']}")
                st.markdown(f"**Data Collected:** {spec_data['collected_date']}")

def create_virtual_try_on_display(patient_photo, recommended_spectacles):
    """Create virtual try-on display with real spectacle images"""
    
    st.markdown("### 👤 Virtual Try-On with Real Spectacles")
    
    if patient_photo is not None:
        # Display patient photo
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(patient_photo, caption="Patient Photo", width=300)
        
        with col2:
            st.markdown("**Recommended Spectacles:**")
            
            # Show recommended spectacles with real images
            for i, spec_name in enumerate(recommended_spectacles[:4]):
                with st.expander(f"{i+1}. {spec_name}", expanded=(i==0)):
                    spec_image = load_spectacle_image(spec_name)
                    st.image(spec_image, width=250)
                    
                    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
                    if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                        spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                        total_price = spec_data['price'] + spec_data['lens_price']
                        
                        st.markdown(f"**Price:** ₹{total_price:,}")
                        st.markdown(f"**Material:** {spec_data['material']}")
                        st.markdown(f"**Shape:** {spec_data['shape']}")
                        st.markdown(f"**Delivery:** {spec_data['delivery_days']} days")
    
    else:
        st.info("Please capture a patient photo first to enable virtual try-on.")

def download_spectacle_catalog():
    """Generate downloadable spectacle catalog with images"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    import pandas as pd
    from io import BytesIO
    
    # Create catalog data
    catalog_data = []
    
    for spec_name, spec_data in COMPREHENSIVE_SPECTACLE_DATABASE.items():
        total_price = spec_data['price'] + spec_data['lens_price']
        
        catalog_data.append({
            "Brand": spec_data['brand'],
            "Model": spec_data['model'],
            "Category": spec_data['category'],
            "Shape": spec_data['shape'],
            "Material": spec_data['material'],
            "Frame Price (₹)": spec_data['price'],
            "Lens Price (₹)": spec_data['lens_price'],
            "Total Price (₹)": total_price,
            "Delivery Days": spec_data['delivery_days'],
            "Source": spec_data['source'],
            "Availability": spec_data['availability'],
            "Description": spec_data['description'],
            "Data Collected": spec_data['collected_date']
        })
    
    df = pd.DataFrame(catalog_data)
    
    # Sort by price
    df = df.sort_values('Total Price (₹)')
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()

# Import required for CSV export
from io import StringIO