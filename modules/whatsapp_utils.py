#!/usr/bin/env python
"""
WhatsApp integration utilities for MauEyeCare
"""
import streamlit as st
import requests
import urllib.parse

def test_whatsapp_connection():
    """Test WhatsApp API connection"""
    try:
        # Check if WhatsApp credentials are configured
        access_token = st.secrets.get("WHATSAPP_ACCESS_TOKEN", "")
        phone_number_id = st.secrets.get("WHATSAPP_PHONE_NUMBER_ID", "")
        
        if access_token and phone_number_id:
            return {"success": True, "demo": False}
        else:
            return {"success": True, "demo": True}
    except:
        return {"success": True, "demo": True}

def send_text_message(phone_number, message):
    """Send text message via WhatsApp API"""
    try:
        # Check if WhatsApp credentials are configured
        access_token = st.secrets.get("WHATSAPP_ACCESS_TOKEN", "")
        phone_number_id = st.secrets.get("WHATSAPP_PHONE_NUMBER_ID", "")
        
        if not access_token or not phone_number_id:
            return {
                "success": True,
                "demo": True,
                "message": f"Demo mode: Would send message to {phone_number}"
            }
        
        # WhatsApp API endpoint
        url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_via_whatsapp_web(phone_number, message):
    """Generate WhatsApp Web URL for sending message"""
    # Clean phone number
    clean_number = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    
    # Encode message for URL
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp Web URL
    whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_message}"
    
    return whatsapp_url

def format_prescription_message(patient_name, prescription_link, doctor_name="Dr. Danish"):
    """Format professional prescription message"""
    message = f"""🏥 *MauEyeCare Prescription Ready*

Dear {patient_name},

Your eye care prescription has been prepared by {doctor_name}.

📄 *View Prescription:* {prescription_link}

📋 *Prescription Details:*
• Patient: {patient_name}
• Doctor: {doctor_name} (Reg: UPS 2908)
• Clinic: MauEyeCare Optical Center

📞 *For queries:* +91 92356-47410
📧 *Email:* maueyecare@gmail.com

*Thank you for choosing MauEyeCare!*

---
🏥 MauEyeCare Optical Center
👁️ Complete AI-Powered Eye Care"""
    
    return message