#!/usr/bin/env python
"""
AI-powered doctor tools for enhanced diagnosis and recommendations
"""
import requests
import json
from config import CONFIG

def analyze_symptoms_ai(symptoms, age, gender, medical_history=""):
    """AI-powered symptom analysis"""
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "AI analysis unavailable - API key not configured"
    
    prompt = f"""
    As an experienced ophthalmologist, analyze these symptoms:
    
    Patient Details:
    - Age: {age}
    - Gender: {gender}
    - Symptoms: {symptoms}
    - Medical History: {medical_history}
    
    Provide:
    1. Possible diagnoses (most likely first)
    2. Recommended tests/examinations
    3. Treatment suggestions
    4. When to seek immediate care
    
    Keep response concise and professional.
    """
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are an expert ophthalmologist providing clinical analysis."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"AI analysis error: {response.status_code}"
    except Exception as e:
        return f"AI analysis failed: {str(e)}"

def suggest_medications_ai(diagnosis, age, allergies=""):
    """AI-powered medication suggestions"""
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "Medication suggestions unavailable"
    
    prompt = f"""
    As an ophthalmologist, suggest appropriate medications for:
    
    Diagnosis: {diagnosis}
    Patient Age: {age}
    Known Allergies: {allergies}
    
    Provide:
    1. First-line medications with dosages
    2. Alternative options
    3. Duration of treatment
    4. Important precautions
    
    Format as a clear medication list.
    """
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are an expert ophthalmologist prescribing medications."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return "Medication suggestion error"
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_prescription_interactions(medications):
    """Check for drug interactions"""
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "Interaction check unavailable"
    
    med_list = ", ".join(medications)
    prompt = f"""
    Check for potential drug interactions between these eye medications:
    {med_list}
    
    Provide:
    1. Any known interactions
    2. Timing recommendations
    3. Safety precautions
    4. Monitoring requirements
    
    Be specific about ophthalmic drug interactions.
    """
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are a clinical pharmacist specializing in ophthalmology."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return "Interaction check failed"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_patient_education_ai(condition, treatment):
    """Generate patient education content"""
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "Patient education unavailable"
    
    prompt = f"""
    Create patient education content for:
    
    Condition: {condition}
    Treatment: {treatment}
    
    Include:
    1. What is this condition? (simple explanation)
    2. How to use prescribed medications
    3. Do's and Don'ts
    4. When to contact the doctor
    5. Expected recovery timeline
    
    Use simple, patient-friendly language.
    """
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are a patient educator explaining eye conditions in simple terms."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return "Education content generation failed"
    except Exception as e:
        return f"Error: {str(e)}"

def smart_inventory_suggestions(current_inventory, patient_demographics):
    """AI-powered inventory management suggestions"""
    grok_key = CONFIG.get('GROK_API_KEY')
    if not grok_key:
        return "Inventory suggestions unavailable"
    
    inventory_list = ", ".join([f"{item}: {qty}" for item, qty in current_inventory.items()])
    
    prompt = f"""
    As a healthcare inventory manager for an eye clinic, analyze this inventory:
    
    Current Stock: {inventory_list}
    Patient Demographics: {patient_demographics}
    
    Suggest:
    1. Items to reorder (with quantities)
    2. New items to stock based on common eye conditions
    3. Seasonal considerations
    4. Cost-effective alternatives
    
    Focus on practical inventory management.
    """
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "You are a healthcare inventory specialist for eye clinics."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return "Inventory analysis failed"
    except Exception as e:
        return f"Error: {str(e)}"