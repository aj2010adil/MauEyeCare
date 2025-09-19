#!/usr/bin/env python3
"""
WhatsApp Integration for MauEyeCare
Handles prescription sharing via WhatsApp API and Web
"""

import streamlit as st
import requests
from urllib.parse import quote

def send_text_message(mobile, message):
    """Send WhatsApp message via API (demo mode)"""
    try:
        # Demo mode - simulate API call
        return {
            'success': True,
            'demo': True,
            'message': f'Message prepared for {mobile}',
            'mobile': mobile,
            'content': message[:100] + '...' if len(message) > 100 else message
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def send_via_whatsapp_web(mobile, message):
    """Generate WhatsApp Web URL for manual sending"""
    # Clean mobile number
    clean_mobile = mobile.replace('+', '').replace(' ', '').replace('-', '')
    if not clean_mobile.startswith('91'):
        clean_mobile = '91' + clean_mobile
    
    # Encode message for URL
    encoded_message = quote(message)
    
    # Generate WhatsApp Web URL
    whatsapp_url = f"https://wa.me/{clean_mobile}?text={encoded_message}"
    
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

📞 *For queries:* +91 92356-47410
📧 *Email:* maueyecare@gmail.com

*Thank you for choosing MauEyeCare!*

---
🏥 MauEyeCare Optical Center
👁️ Complete AI-Powered Eye Care"""
    
    return message

def send_prescription_link(patient_name, mobile, prescription_link):
    """Send prescription link to patient"""
    message = format_prescription_message(patient_name, prescription_link)
    
    # Try API first (demo mode)
    api_result = send_text_message(mobile, message)
    
    # Also generate web URL as backup
    web_url = send_via_whatsapp_web(mobile, message)
    
    return {
        'api_result': api_result,
        'web_url': web_url,
        'message': message
    }