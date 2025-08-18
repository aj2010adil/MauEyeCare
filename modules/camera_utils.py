#!/usr/bin/env python
"""
Camera utilities for face analysis and spectacle recommendations
"""
import cv2
import streamlit as st
import numpy as np
from PIL import Image
import base64
from io import BytesIO

def capture_photo():
    """Capture photo using webcam"""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Camera not available"
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb, "Photo captured successfully"
        else:
            return None, "Failed to capture photo"
    except Exception as e:
        return None, f"Camera error: {str(e)}"

def analyze_face_shape(image):
    """Analyze face shape and recommend spectacles"""
    try:
        # Convert PIL to OpenCV format
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Simple face detection using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return "No face detected", []
        
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Calculate face ratios
        face_ratio = w / h
        
        # Determine face shape based on ratio
        if face_ratio > 1.2:
            face_shape = "Wide/Round"
            recommendations = [
                "Rectangular frames to add length",
                "Angular frames to create definition",
                "Avoid round or wide frames"
            ]
        elif face_ratio < 0.8:
            face_shape = "Long/Oval"
            recommendations = [
                "Wide frames to balance proportions",
                "Round or square frames work well",
                "Avoid narrow frames"
            ]
        else:
            face_shape = "Balanced/Oval"
            recommendations = [
                "Most frame styles suit you",
                "Cat-eye frames for elegance",
                "Aviator style for classic look"
            ]
        
        return face_shape, recommendations
        
    except Exception as e:
        return f"Analysis error: {str(e)}", []

def get_spectacle_recommendations(face_shape, age, gender):
    """Get detailed spectacle recommendations"""
    
    base_recommendations = {
        "Wide/Round": {
            "frames": ["Rectangular", "Angular", "Cat-eye"],
            "avoid": ["Round", "Oversized round"],
            "colors": ["Dark colors", "Bold patterns"]
        },
        "Long/Oval": {
            "frames": ["Wide rectangular", "Round", "Square"],
            "avoid": ["Narrow frames", "Small frames"],
            "colors": ["Bright colors", "Decorative temples"]
        },
        "Balanced/Oval": {
            "frames": ["Any style works", "Aviator", "Cat-eye", "Round"],
            "avoid": ["Extremely oversized"],
            "colors": ["Any color", "Experiment with styles"]
        }
    }
    
    # Age-based adjustments
    if age > 50:
        style_notes = "Consider progressive lenses, larger frames for easier reading"
    elif age > 30:
        style_notes = "Professional styles, anti-glare coating recommended"
    else:
        style_notes = "Trendy styles, blue light protection for screen use"
    
    # Gender-based suggestions
    if gender.lower() == "female":
        additional = "Cat-eye, decorative temples, colorful options"
    else:
        additional = "Classic rectangular, aviator, minimalist designs"
    
    recommendations = base_recommendations.get(face_shape, base_recommendations["Balanced/Oval"])
    
    return {
        "face_shape": face_shape,
        "recommended_frames": recommendations["frames"],
        "avoid_frames": recommendations["avoid"],
        "color_suggestions": recommendations["colors"],
        "age_considerations": style_notes,
        "style_preferences": additional
    }