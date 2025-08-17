"""
WhatsApp Integration for MauEyeCare
Sends prescription links to patients via WhatsApp
"""

import requests
import json
import streamlit as st

# WhatsApp Business API Configuration
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"

def get_whatsapp_config():
    """Get WhatsApp configuration from environment or secrets"""
    try:
        # Try to get from Streamlit secrets
        if hasattr(st, 'secrets'):
            access_token = st.secrets.get('WHATSAPP_ACCESS_TOKEN')
            phone_number_id = st.secrets.get('WHATSAPP_PHONE_NUMBER_ID')
        else:
            access_token = None
            phone_number_id = None
        
        # Fallback to environment variables
        if not access_token:
            import os
            access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        
        # Default test configuration (for demo purposes)
        if not access_token:
            access_token = "demo_token_replace_with_real"
            phone_number_id = "demo_phone_id_replace_with_real"
        
        return {
            'access_token': access_token,
            'phone_number_id': phone_number_id
        }
    
    except Exception as e:
        return {
            'access_token': None,
            'phone_number_id': None,
            'error': str(e)
        }

def send_text_message(to_number, message_text):
    """
    Send a text message via WhatsApp Business API
    
    Args:
        to_number (str): Recipient phone number (with country code)
        message_text (str): Message content
    
    Returns:
        dict: Result with success status and message
    """
    
    config = get_whatsapp_config()
    
    if not config.get('access_token') or not config.get('phone_number_id'):
        return {
            'success': False,
            'error': 'WhatsApp configuration missing',
            'details': 'Please configure WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID'
        }
    
    # Check if using demo configuration
    if config['access_token'] == "demo_token_replace_with_real":
        return {
            'success': True,
            'message_id': 'demo_message_id',
            'demo': True,
            'details': f'Demo mode: Would send to {to_number}: {message_text[:50]}...'
        }
    
    try:
        # Prepare WhatsApp API request
        url = f"{WHATSAPP_API_URL}/{config['phone_number_id']}/messages"
        
        headers = {
            'Authorization': f"Bearer {config['access_token']}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        # Send request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'message_id': result.get('messages', [{}])[0].get('id'),
                'response': result
            }
        else:
            return {
                'success': False,
                'error': f'WhatsApp API error: {response.status_code}',
                'details': response.text
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'WhatsApp sending failed: {str(e)}',
            'details': 'Check internet connection and API configuration'
        }

def send_prescription_link(patient_name, patient_mobile, prescription_link):
    """
    Send prescription link to patient via WhatsApp
    
    Args:
        patient_name (str): Patient name
        patient_mobile (str): Patient mobile number
        prescription_link (str): Google Drive prescription link
    
    Returns:
        dict: Result with success status
    """
    
    # Format message
    message = f"""Hi {patient_name},

Your prescription from MauEyeCare is ready! 👁️

📄 View your prescription: {prescription_link}

📞 For any queries, call: +91 92356-47410

Thank you for choosing MauEyeCare!
- Dr. Danish"""
    
    # Format mobile number
    mobile = patient_mobile.replace("+91", "").replace(" ", "").replace("-", "")
    if not mobile.startswith("91"):
        mobile = "91" + mobile
    
    # Send message
    return send_text_message(mobile, message)

def test_whatsapp_connection():
    """Test WhatsApp API connection"""
    
    config = get_whatsapp_config()
    
    if not config.get('access_token'):
        return {
            'success': False,
            'error': 'No WhatsApp access token configured'
        }
    
    # Check if demo mode
    if config['access_token'] == "demo_token_replace_with_real":
        return {
            'success': True,
            'demo': True,
            'message': 'WhatsApp is in demo mode - configure real tokens for production'
        }
    
    try:
        # Test API connection
        url = f"{WHATSAPP_API_URL}/{config['phone_number_id']}"
        
        headers = {
            'Authorization': f"Bearer {config['access_token']}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'WhatsApp API connection successful'
            }
        else:
            return {
                'success': False,
                'error': f'WhatsApp API test failed: {response.status_code}',
                'details': response.text
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'WhatsApp connection test failed: {str(e)}'
        }

# Alternative methods for sending messages

def send_via_whatsapp_web(phone_number, message):
    """
    Generate WhatsApp Web link for manual sending
    
    Args:
        phone_number (str): Phone number
        message (str): Message text
    
    Returns:
        str: WhatsApp Web URL
    """
    
    # Format phone number
    phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    
    # Encode message for URL
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp Web URL
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    return whatsapp_url

def send_via_system_whatsapp(phone_number, message):
    """
    Try to open WhatsApp desktop app (if installed)
    
    Args:
        phone_number (str): Phone number
        message (str): Message text
    
    Returns:
        dict: Result status
    """
    
    try:
        import webbrowser
        
        # Generate WhatsApp Web URL
        whatsapp_url = send_via_whatsapp_web(phone_number, message)
        
        # Try to open in browser/WhatsApp app
        webbrowser.open(whatsapp_url)
        
        return {
            'success': True,
            'method': 'WhatsApp Web/Desktop',
            'url': whatsapp_url
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to open WhatsApp: {str(e)}'
        }