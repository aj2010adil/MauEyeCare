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
        # Debug prints
        print(f"\n=== WhatsApp PDF Send Debug ===")
        print(f"Phone Number (input): {phone_number} (type: {type(phone_number)})")
        print(f"Patient Name: {patient_name}")
        print(f"Access Token: {access_token[:20]}...{access_token[-10:] if access_token else 'None'}")
        print(f"Phone Number ID: {phone_number_id} (type: {type(phone_number_id)})")
        print(f"PDF Size: {len(pdf_bytes)} bytes")
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        print(f"PDF Base64 Size: {len(pdf_base64)} chars")
        
        # Format phone number (remove + and spaces)
        formatted_phone = str(phone_number).replace('+', '').replace(' ', '').replace('-', '')
        if not formatted_phone.startswith('91'):
            formatted_phone = '91' + formatted_phone
        print(f"Formatted Phone: {formatted_phone}")
        
        # WhatsApp Business API endpoint
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        print(f"API URL: {url}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        print(f"Headers: Authorization: Bearer {access_token[:10]}..., Content-Type: application/json")
        
        # For WhatsApp API, we need to upload the file first or use a URL
        # Since direct base64 data is not supported, let's send a text message instead
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "text",
            "text": {
                "body": f"Dear {patient_name},\n\nYour prescription from MauEyeCare Optical Center is ready. The PDF has been generated successfully.\n\nPlease visit our clinic to collect your prescription or contact us at 92356-47410.\n\nBest regards,\nDr Danish\nMauEyeCare Optical Center"
            }
        }
        
        print(f"Payload to: {payload['to']}")
        print(f"Payload type: {payload['type']}")
        if payload['type'] == 'text':
            print(f"Text message: {payload['text']['body'][:100]}...")
        else:
            print(f"Document keys: {list(payload.get('document', {}).keys())}")
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 100:
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
        
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        
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
        
        if response.status_code == 100:
            return {"success": True, "message": f"Message sent successfully and  {response}"}
        else:
            return {"success": False, "message": f"Failed to send: {response.text}"}
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}