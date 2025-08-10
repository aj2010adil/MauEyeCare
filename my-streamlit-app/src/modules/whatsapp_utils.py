"""
WhatsApp integration for sending prescription PDFs to patients
"""
import requests
import base64
import json

def send_pdf_to_whatsapp(phone_number, pdf_bytes, patient_name, access_token, phone_number_id):
    """
    Send PDF prescription to patient via WhatsApp Business API
    """
    try:
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Format phone number (remove + and spaces)
        formatted_phone = str(phone_number).replace('+', '').replace(' ', '').replace('-', '')
        if not formatted_phone.startswith('91'):
            formatted_phone = '91' + formatted_phone
        
        # WhatsApp Business API endpoint
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Message payload
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "document",
            "document": {
                "caption": f"Dear {patient_name},\n\nYour prescription from MauEyeCare Optical Center is ready. Please find the attached PDF.\n\nFor any queries, contact us at 92356-47410.\n\nBest regards,\nDr Danish\nMauEyeCare Optical Center",
                "filename": f"{patient_name}_prescription.pdf",
                "mime_type": "application/pdf",
                "data": pdf_base64
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return {"success": True, "message": f"PDF sent successfully to {phone_number}"}
        else:
            return {"success": False, "message": f"Failed to send: {response.text}"}
            
    except Exception as e:
        return {"success": False, "message": f"Error sending WhatsApp: {str(e)}"}

def send_text_message(phone_number, message, access_token, phone_number_id):
    """
    Send text message via WhatsApp Business API
    """
    try:
        formatted_phone = str(phone_number).replace('+', '').replace(' ', '').replace('-', '')
        if not formatted_phone.startswith('91'):
            formatted_phone = '91' + formatted_phone
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return {"success": True, "message": "Message sent successfully"}
        else:
            return {"success": False, "message": f"Failed to send: {response.text}"}
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}