#!/usr/bin/env python
"""
Advanced camera system with face detection and quality checks
"""
import cv2
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

class FaceDetectionCamera:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
    def check_face_quality(self, frame):
        """Check if face is properly positioned and clear"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return False, "No face detected. Please position your face in the camera."
        
        if len(faces) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in frame."
        
        # Get the face
        x, y, w, h = faces[0]
        face_area = w * h
        frame_area = frame.shape[0] * frame.shape[1]
        
        # Check if face is too small
        if face_area < frame_area * 0.1:
            return False, "Face too small. Please move closer to the camera."
        
        # Check if face is too large
        if face_area > frame_area * 0.6:
            return False, "Face too large. Please move back from the camera."
        
        # Check if face is centered
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        frame_center_x = frame.shape[1] // 2
        frame_center_y = frame.shape[0] // 2
        
        if abs(face_center_x - frame_center_x) > frame.shape[1] * 0.2:
            return False, "Please center your face horizontally."
        
        if abs(face_center_y - frame_center_y) > frame.shape[0] * 0.2:
            return False, "Please center your face vertically."
        
        # Check for eyes (indicates face is frontal)
        face_roi = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
        
        if len(eyes) < 2:
            return False, "Please face the camera directly. Both eyes should be visible."
        
        return True, "Face positioned correctly!"
    
    def add_face_guide_overlay(self, frame):
        """Add visual guides to help position face correctly"""
        height, width = frame.shape[:2]
        
        # Convert to PIL for better drawing
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # Draw face guide oval
        center_x, center_y = width // 2, height // 2
        oval_width, oval_height = width // 3, height // 2
        
        # Face guide oval
        draw.ellipse([
            center_x - oval_width // 2,
            center_y - oval_height // 2,
            center_x + oval_width // 2,
            center_y + oval_height // 2
        ], outline="green", width=3)
        
        # Center crosshair
        draw.line([center_x - 20, center_y, center_x + 20, center_y], fill="green", width=2)
        draw.line([center_x, center_y - 20, center_x, center_y + 20], fill="green", width=2)
        
        # Instructions text
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "Position your face in the green oval", fill="green", font=font)
        draw.text((10, 30), "Look directly at the camera", fill="green", font=font)
        
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def capture_with_guidance(self):
        """Capture photo with real-time face detection guidance"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None, "Camera not accessible"
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Create Streamlit placeholders
        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        button_placeholder = st.empty()
        
        captured_frame = None
        capture_ready = False
        
        # Real-time preview loop
        for i in range(100):  # Limit to prevent infinite loop
            ret, frame = cap.read()
            if not ret:
                break
            
            # Add face guide overlay
            guided_frame = self.add_face_guide_overlay(frame)
            
            # Check face quality
            face_ok, message = self.check_face_quality(frame)
            
            # Display frame
            frame_rgb = cv2.cvtColor(guided_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, caption="Live Camera Feed", use_column_width=True)
            
            # Display status
            if face_ok:
                status_placeholder.success(f"✅ {message}")
                capture_ready = True
                
                # Show capture button
                if button_placeholder.button("📸 Capture Photo", key=f"capture_{i}"):
                    captured_frame = frame.copy()
                    break
            else:
                status_placeholder.warning(f"⚠️ {message}")
                capture_ready = False
            
            time.sleep(0.1)  # Small delay to prevent too rapid updates
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured_frame is not None:
            return cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB), "Photo captured successfully!"
        else:
            return None, "Photo capture cancelled or failed"

def create_combined_photo_display(original_photo, face_analysis_result, recommendations):
    """Create a combined display showing photo with analysis overlay"""
    
    # Convert to PIL for easier manipulation
    if isinstance(original_photo, np.ndarray):
        pil_image = Image.fromarray(original_photo)
    else:
        pil_image = original_photo
    
    # Create a larger canvas for combined display
    canvas_width = pil_image.width + 400
    canvas_height = max(pil_image.height, 600)
    
    combined_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Paste original photo
    combined_image.paste(pil_image, (0, 0))
    
    # Add analysis overlay
    draw = ImageDraw.Draw(combined_image)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        text_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Analysis results section
    text_x = pil_image.width + 20
    text_y = 20
    
    # Title
    draw.text((text_x, text_y), "Face Analysis Results", fill="black", font=title_font)
    text_y += 40
    
    # Face shape
    draw.text((text_x, text_y), f"Face Shape: {face_analysis_result.get('shape', 'Unknown')}", fill="blue", font=text_font)
    text_y += 30
    
    # Recommendations
    draw.text((text_x, text_y), "Recommended Frames:", fill="black", font=title_font)
    text_y += 30
    
    # List recommendations
    for i, rec in enumerate(recommendations[:5]):  # Show top 5
        draw.text((text_x, text_y), f"• {rec}", fill="green", font=text_font)
        text_y += 25
    
    # Add face detection overlay on original photo
    if 'face_coords' in face_analysis_result:
        x, y, w, h = face_analysis_result['face_coords']
        draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
        draw.text((x, y-25), "Detected Face", fill="red", font=text_font)
    
    return combined_image

def analyze_face_with_detection(image_array):
    """Analyze face and return detailed information including coordinates"""
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        return {"shape": "No face detected", "confidence": 0, "face_coords": None}
    
    # Get the largest face
    face = max(faces, key=lambda x: x[2] * x[3])
    x, y, w, h = face
    
    # Calculate face ratios
    face_ratio = w / h
    
    # Determine face shape with confidence
    if face_ratio > 1.2:
        face_shape = "Wide/Round"
        confidence = min(95, 70 + (face_ratio - 1.2) * 50)
    elif face_ratio < 0.8:
        face_shape = "Long/Oval"
        confidence = min(95, 70 + (0.8 - face_ratio) * 50)
    else:
        face_shape = "Balanced/Square"
        confidence = min(95, 70 + (1.0 - abs(face_ratio - 1.0)) * 50)
    
    return {
        "shape": face_shape,
        "confidence": confidence,
        "face_coords": (x, y, w, h),
        "face_ratio": face_ratio,
        "face_area": w * h
    }