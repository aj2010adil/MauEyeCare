#!/usr/bin/env python
"""
Create patient photos with spectacle overlays and comprehensive analysis
"""
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Some features may be limited.")

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import requests
from io import BytesIO
import datetime

def create_patient_with_spectacles_overlay(patient_photo, spectacle_recommendations, face_coordinates):
    """Create images showing patient wearing recommended spectacles"""
    
    if isinstance(patient_photo, np.ndarray):
        patient_img = Image.fromarray(patient_photo)
    else:
        patient_img = patient_photo
    
    # Get face coordinates
    if face_coordinates and len(face_coordinates) == 4:
        x, y, w, h = face_coordinates
    else:
        # Default face area (center of image)
        x, y = patient_img.width // 4, patient_img.height // 4
        w, h = patient_img.width // 2, patient_img.height // 2
    
    overlaid_images = []
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    
    for spec_name in spectacle_recommendations[:6]:  # Top 6 recommendations
        if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
            spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
            
            # Create a copy of patient image
            patient_copy = patient_img.copy()
            draw = ImageDraw.Draw(patient_copy)
            
            # Calculate spectacle overlay position
            spec_width = int(w * 0.8)  # 80% of face width
            spec_height = int(h * 0.3)  # 30% of face height
            spec_x = x + (w - spec_width) // 2
            spec_y = y + int(h * 0.2)  # Position on upper face
            
            # Draw spectacle frame based on shape
            if spec_data['shape'] == 'Rectangle':
                draw_rectangle_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            elif spec_data['shape'] == 'Round':
                draw_round_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            elif spec_data['shape'] == 'Aviator':
                draw_aviator_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            elif spec_data['shape'] == 'Cat-Eye':
                draw_cateye_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            elif spec_data['shape'] == 'Square':
                draw_square_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            else:
                draw_rectangle_spectacles(draw, spec_x, spec_y, spec_width, spec_height, spec_data['material'])
            
            # Add spectacle info overlay
            add_spectacle_info_overlay(patient_copy, spec_data)
            
            overlaid_images.append({
                'image': patient_copy,
                'spec_name': spec_name,
                'spec_data': spec_data
            })
    
    return overlaid_images

def draw_rectangle_spectacles(draw, x, y, width, height, material):
    """Draw rectangular spectacle frame"""
    frame_thickness = 3 if material == 'Metal' else 5
    
    # Left lens
    left_lens_width = width // 2 - 10
    draw.rectangle([x, y, x + left_lens_width, y + height], 
                  outline='black', width=frame_thickness)
    
    # Right lens
    right_lens_x = x + width // 2 + 10
    draw.rectangle([right_lens_x, y, right_lens_x + left_lens_width, y + height], 
                  outline='black', width=frame_thickness)
    
    # Bridge
    bridge_y = y + height // 4
    draw.line([(x + left_lens_width, bridge_y), (right_lens_x, bridge_y)], 
             fill='black', width=frame_thickness)
    
    # Temples
    draw.line([(x, y + height // 3), (x - 20, y + height // 3)], 
             fill='black', width=frame_thickness)
    draw.line([(x + width, y + height // 3), (x + width + 20, y + height // 3)], 
             fill='black', width=frame_thickness)

def draw_round_spectacles(draw, x, y, width, height, material):
    """Draw round spectacle frame"""
    frame_thickness = 3 if material == 'Metal' else 5
    radius = min(width // 4, height // 2)
    
    # Left lens
    left_center_x = x + radius
    left_center_y = y + height // 2
    draw.ellipse([left_center_x - radius, left_center_y - radius,
                 left_center_x + radius, left_center_y + radius], 
                outline='black', width=frame_thickness)
    
    # Right lens
    right_center_x = x + width - radius
    right_center_y = y + height // 2
    draw.ellipse([right_center_x - radius, right_center_y - radius,
                 right_center_x + radius, right_center_y + radius], 
                outline='black', width=frame_thickness)
    
    # Bridge
    draw.line([(left_center_x + radius, left_center_y), 
               (right_center_x - radius, right_center_y)], 
             fill='black', width=frame_thickness)
    
    # Temples
    draw.line([(left_center_x - radius, left_center_y), 
               (left_center_x - radius - 20, left_center_y)], 
             fill='black', width=frame_thickness)
    draw.line([(right_center_x + radius, right_center_y), 
               (right_center_x + radius + 20, right_center_y)], 
             fill='black', width=frame_thickness)

def draw_aviator_spectacles(draw, x, y, width, height, material):
    """Draw aviator spectacle frame"""
    frame_thickness = 3
    
    # Aviator teardrop shape - simplified as triangular top with curved bottom
    left_points = [
        (x + 10, y + height),  # Bottom left
        (x + width//4, y),     # Top
        (x + width//2 - 5, y + height//2),  # Right curve
        (x + width//2 - 15, y + height)     # Bottom right
    ]
    
    right_points = [
        (x + width//2 + 15, y + height),    # Bottom left
        (x + width//2 + 5, y + height//2),  # Left curve
        (x + 3*width//4, y),                # Top
        (x + width - 10, y + height)        # Bottom right
    ]
    
    # Draw left lens
    for i in range(len(left_points)):
        start = left_points[i]
        end = left_points[(i + 1) % len(left_points)]
        draw.line([start, end], fill='black', width=frame_thickness)
    
    # Draw right lens
    for i in range(len(right_points)):
        start = right_points[i]
        end = right_points[(i + 1) % len(right_points)]
        draw.line([start, end], fill='black', width=frame_thickness)
    
    # Bridge
    draw.line([(x + width//2 - 15, y + height), 
               (x + width//2 + 15, y + height)], 
             fill='black', width=frame_thickness)

def draw_cateye_spectacles(draw, x, y, width, height, material):
    """Draw cat-eye spectacle frame"""
    frame_thickness = 4
    
    # Left lens - cat eye shape
    left_points = [
        (x, y + height//2),           # Left middle
        (x + width//4, y),            # Top left
        (x + width//2 - 10, y + height//4),  # Top right (upswept)
        (x + width//2 - 15, y + height),     # Bottom right
        (x + 5, y + height)           # Bottom left
    ]
    
    # Right lens - cat eye shape
    right_points = [
        (x + width//2 + 15, y + height),     # Bottom left
        (x + width//2 + 10, y + height//4),  # Top left (upswept)
        (x + 3*width//4, y),                 # Top right
        (x + width, y + height//2),          # Right middle
        (x + width - 5, y + height)          # Bottom right
    ]
    
    # Draw left lens
    for i in range(len(left_points)):
        start = left_points[i]
        end = left_points[(i + 1) % len(left_points)]
        draw.line([start, end], fill='black', width=frame_thickness)
    
    # Draw right lens
    for i in range(len(right_points)):
        start = right_points[i]
        end = right_points[(i + 1) % len(right_points)]
        draw.line([start, end], fill='black', width=frame_thickness)

def draw_square_spectacles(draw, x, y, width, height, material):
    """Draw square spectacle frame"""
    frame_thickness = 4 if material == 'Acetate' else 3
    
    # Left lens - square
    left_size = width // 2 - 10
    draw.rectangle([x, y, x + left_size, y + left_size], 
                  outline='black', width=frame_thickness)
    
    # Right lens - square
    right_x = x + width // 2 + 10
    draw.rectangle([right_x, y, right_x + left_size, y + left_size], 
                  outline='black', width=frame_thickness)
    
    # Bridge
    bridge_y = y + left_size // 3
    draw.line([(x + left_size, bridge_y), (right_x, bridge_y)], 
             fill='black', width=frame_thickness)
    
    # Temples
    draw.line([(x, y + left_size // 3), (x - 20, y + left_size // 3)], 
             fill='black', width=frame_thickness)
    draw.line([(x + width, y + left_size // 3), (x + width + 20, y + left_size // 3)], 
             fill='black', width=frame_thickness)

def add_spectacle_info_overlay(image, spec_data):
    """Add spectacle information overlay on the image"""
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add semi-transparent background for text
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Background rectangle
    text_bg_height = 80
    overlay_draw.rectangle([0, image.height - text_bg_height, image.width, image.height], 
                          fill=(0, 0, 0, 180))
    
    # Composite overlay
    image_with_overlay = Image.alpha_composite(image.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(image_with_overlay)
    
    # Add text information
    y_pos = image.height - text_bg_height + 5
    
    # Brand and model
    draw.text((10, y_pos), f"{spec_data['brand']} {spec_data['model']}", 
             fill='white', font=font)
    
    # Price information
    total_price = spec_data['price'] + spec_data['lens_price']
    draw.text((10, y_pos + 20), f"₹{total_price:,} (Frame: ₹{spec_data['price']:,} + Lens: ₹{spec_data['lens_price']:,})", 
             fill='yellow', font=small_font)
    
    # Material and shape
    draw.text((10, y_pos + 35), f"{spec_data['material']} | {spec_data['shape']} | {spec_data['category']}", 
             fill='lightblue', font=small_font)
    
    # Delivery info
    draw.text((10, y_pos + 50), f"Delivery: {spec_data['delivery_days']} days | Source: {spec_data['source']}", 
             fill='lightgreen', font=small_font)
    
    # Convert back to RGB
    return image_with_overlay.convert('RGB')

def create_comprehensive_analysis_page(patient_photo, analysis_result, spectacle_recommendations):
    """Create a comprehensive analysis page with patient wearing spectacles"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    
    # Create overlaid images
    overlaid_images = create_patient_with_spectacles_overlay(
        patient_photo, 
        spectacle_recommendations, 
        analysis_result.get('face_coordinates')
    )
    
    # Create comprehensive report image
    report_width = 1400
    report_height = 2000
    
    report_img = Image.new('RGB', (report_width, report_height), 'white')
    draw = ImageDraw.Draw(report_img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        subtitle_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header
    draw.text((50, 30), "MauEyeCare - Comprehensive Spectacle Analysis", fill="blue", font=title_font)
    draw.text((50, 80), f"Patient: {analysis_result.get('patient_name', 'N/A')} | Age: {analysis_result.get('age', 'N/A')} | Gender: {analysis_result.get('gender', 'N/A')}", 
             fill="gray", font=text_font)
    draw.text((50, 110), f"Analysis Date: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 
             fill="gray", font=text_font)
    
    # Face analysis summary
    y_pos = 150
    draw.text((50, y_pos), "Face Analysis Summary:", fill="black", font=subtitle_font)
    y_pos += 35
    
    if analysis_result.get('status') == 'success':
        draw.text((70, y_pos), f"• Face Shape: {analysis_result['face_shape']}", fill="green", font=text_font)
        y_pos += 25
        draw.text((70, y_pos), f"• Confidence: {analysis_result['confidence']:.1f}%", fill="green", font=text_font)
        y_pos += 25
        draw.text((70, y_pos), f"• Best Shapes: {', '.join(analysis_result['best_shapes'])}", fill="blue", font=text_font)
        y_pos += 25
        draw.text((70, y_pos), f"• Avoid Shapes: {', '.join(analysis_result['avoid_shapes'])}", fill="red", font=text_font)
        y_pos += 25
        draw.text((70, y_pos), f"• Reasoning: {analysis_result['reasoning']}", fill="purple", font=small_font)
    
    # Patient with spectacles section
    y_pos += 60
    draw.text((50, y_pos), "Patient Wearing Recommended Spectacles:", fill="black", font=subtitle_font)
    y_pos += 40
    
    # Display overlaid images in grid
    images_per_row = 3
    image_width = 180
    image_height = 150
    margin = 20
    
    for i, overlay_data in enumerate(overlaid_images[:6]):
        row = i // images_per_row
        col = i % images_per_row
        
        x_pos = 50 + col * (image_width + margin)
        y_img_pos = y_pos + row * (image_height + 80)
        
        # Resize and paste image
        resized_img = overlay_data['image'].resize((image_width, image_height))
        report_img.paste(resized_img, (x_pos, y_img_pos))
        
        # Add spectacle name below image
        spec_data = overlay_data['spec_data']
        draw.text((x_pos, y_img_pos + image_height + 5), 
                 f"{spec_data['brand']} {spec_data['model']}", 
                 fill="black", font=small_font)
        
        total_price = spec_data['price'] + spec_data['lens_price']
        draw.text((x_pos, y_img_pos + image_height + 20), 
                 f"₹{total_price:,}", 
                 fill="red", font=small_font)
    
    return report_img

def generate_pricing_table_inr(spectacle_recommendations, prescription_type="Single Vision"):
    """Generate pricing table in INR with comprehensive details"""
    
    from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    
    table_data = []
    
    for spec_name in spectacle_recommendations:
        if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
            spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
            
            # Calculate lens pricing based on prescription type
            base_lens_price = spec_data['lens_price']
            
            if prescription_type == "Progressive":
                lens_price = base_lens_price + 12000  # Add progressive cost
            elif prescription_type == "Bifocal":
                lens_price = base_lens_price + 6000   # Add bifocal cost
            elif prescription_type == "Single Vision":
                lens_price = base_lens_price + 4000   # Add single vision cost
            else:
                lens_price = base_lens_price
            
            frame_price = spec_data['price']
            total_price = frame_price + lens_price
            
            # Calculate delivery date
            delivery_date = datetime.datetime.now() + datetime.timedelta(days=spec_data['delivery_days'])
            
            table_data.append({
                "Brand": spec_data['brand'],
                "Model": spec_data['model'],
                "Frame Price (₹)": f"₹{frame_price:,}",
                "Lens Price (₹)": f"₹{lens_price:,}",
                "Total Price (₹)": f"₹{total_price:,}",
                "Material": spec_data['material'],
                "Shape": spec_data['shape'],
                "Category": spec_data['category'],
                "Source": spec_data['source'],
                "Delivery Date": delivery_date.strftime("%d/%m/%Y"),
                "Delivery Days": spec_data['delivery_days'],
                "Availability": spec_data['availability'],
                "Description": spec_data['description'],
                "Collected Date": spec_data['collected_date']
            })
    
    return table_data