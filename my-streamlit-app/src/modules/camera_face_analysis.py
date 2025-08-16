#!/usr/bin/env python
"""
Camera capture and AI-powered face analysis for spectacle recommendations
"""
import cv2
import streamlit as st
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import requests
from config import CONFIG

def capture_webcam_photo():
    """Capture photo using webcam with Streamlit"""
    try:
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None, "Camera not accessible. Please check camera permissions."
        
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Capture frame
        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb, "Photo captured successfully"
        else:
            return None, "Failed to capture photo"
            
    except Exception as e:
        return None, f"Camera error: {str(e)}"

def analyze_face_with_ai(image_array, patient_name, age, gender):
    """Use AI to analyze face and recommend spectacles"""
    
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "AI analysis unavailable - API key not configured"
    
    try:
        # Convert image to base64 for description
        pil_image = Image.fromarray(image_array)
        
        # Analyze face shape using basic measurements
        height, width = image_array.shape[:2]
        
        # Simple face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            face_description = "No clear face detected in image"
        else:
            # Get the largest face
            face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = face
            
            # Calculate face ratios
            face_ratio = w / h
            
            if face_ratio > 1.2:
                face_shape = "Wide/Round face"
            elif face_ratio < 0.8:
                face_shape = "Long/Oval face"
            else:
                face_shape = "Balanced/Square face"
            
            face_description = f"{face_shape} detected with width-to-height ratio of {face_ratio:.2f}"
        
        # Create AI prompt for spectacle recommendation
        prompt = f"""
        As an expert optician and fashion consultant, analyze this patient for spectacle recommendations:
        
        Patient Details:
        - Name: {patient_name}
        - Age: {age}
        - Gender: {gender}
        - Face Analysis: {face_description}
        
        Based on the face shape analysis, provide detailed recommendations for:
        
        1. FRAME SHAPES (most suitable):
           - Best frame shapes for this face type
           - Shapes to avoid
        
        2. FRAME MATERIALS:
           - Metal vs Plastic recommendations
           - Titanium, acetate, or other materials
        
        3. FRAME SIZES:
           - Width recommendations
           - Bridge size considerations
        
        4. STYLE RECOMMENDATIONS:
           - Professional/casual styles
           - Color recommendations
           - Modern trends suitable for age/gender
        
        5. LENS RECOMMENDATIONS:
           - Anti-glare coatings
           - Blue light protection
           - Photochromic options
        
        6. SPECIFIC PRODUCT SUGGESTIONS:
           - 3-5 specific frame style names
           - Brand recommendations if applicable
        
        Provide practical, actionable advice that a patient can use when selecting spectacles.
        """
        
        # Call AI API
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are an expert optician and fashion consultant specializing in spectacle recommendations based on face analysis."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_recommendation = result["choices"][0]["message"]["content"]
            return ai_recommendation
        else:
            return f"AI analysis error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Face analysis failed: {str(e)}"

def get_face_shape_basic(image_array):
    """Basic face shape detection without AI"""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return "No face detected", []
        
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Calculate face ratios
        face_ratio = w / h
        
        # Determine face shape and recommendations
        if face_ratio > 1.2:
            face_shape = "Wide/Round Face"
            recommendations = [
                "✓ Rectangular frames to add length",
                "✓ Angular frames for definition", 
                "✓ Cat-eye frames for elegance",
                "✗ Avoid round or wide frames",
                "✓ Dark colors and bold patterns work well"
            ]
        elif face_ratio < 0.8:
            face_shape = "Long/Oval Face"
            recommendations = [
                "✓ Wide rectangular frames for balance",
                "✓ Round or square frames work well",
                "✓ Decorative temples add width",
                "✗ Avoid narrow or small frames",
                "✓ Bright colors and patterns recommended"
            ]
        else:
            face_shape = "Balanced/Square Face"
            recommendations = [
                "✓ Most frame styles suit you well",
                "✓ Round frames to soften angles",
                "✓ Oval frames for classic look",
                "✓ Cat-eye for feminine touch",
                "✓ Any color works - experiment freely"
            ]
        
        return face_shape, recommendations
        
    except Exception as e:
        return f"Analysis error: {str(e)}", []

def create_spectacle_shopping_list(ai_recommendations):
    """Extract specific items from AI recommendations for inventory"""
    
    # Common spectacle items that might be recommended
    spectacle_items = []
    
    # Parse AI recommendations for specific items
    rec_lower = ai_recommendations.lower()
    
    if "rectangular" in rec_lower or "rectangle" in rec_lower:
        spectacle_items.append("Rectangular Frames")
    
    if "round" in rec_lower:
        spectacle_items.append("Round Frames")
    
    if "cat-eye" in rec_lower or "cat eye" in rec_lower:
        spectacle_items.append("Cat-Eye Frames")
    
    if "aviator" in rec_lower:
        spectacle_items.append("Aviator Frames")
    
    if "progressive" in rec_lower:
        spectacle_items.append("Progressive Lenses")
    
    if "anti-glare" in rec_lower or "anti glare" in rec_lower:
        spectacle_items.append("Anti-Glare Coating")
    
    if "blue light" in rec_lower:
        spectacle_items.append("Blue Light Filter")
    
    if "photochromic" in rec_lower or "transition" in rec_lower:
        spectacle_items.append("Photochromic Lenses")
    
    if "titanium" in rec_lower:
        spectacle_items.append("Titanium Frames")
    
    if "plastic" in rec_lower or "acetate" in rec_lower:
        spectacle_items.append("Plastic Frames")
    
    # Add some default items if none found
    if not spectacle_items:
        spectacle_items = [
            "Standard Frames",
            "Anti-Glare Coating",
            "Blue Light Filter"
        ]
    
    return spectacle_items