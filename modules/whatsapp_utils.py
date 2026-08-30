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
    """Format professional prescription message with link"""
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


def format_clinical_whatsapp_message(patient_name, date_str, rx_table=None, ipd=None, spectacles=None, medicines=None, advice=None, next_review=None, doctor_name="Dr. Danish"):
    """Format complete clinical prescription summary for direct WhatsApp sending"""
    lines = [
        "🏥 *MAU EYE CARE - CLINICAL PRESCRIPTION*",
        f"👤 *Patient:* {patient_name}",
        f"📅 *Date:* {date_str}",
        f"👨‍⚕️ *Doctor:* {doctor_name} (B.Sc. Optometry, Reg: UPS 2908)",
        "------------------------------------"
    ]
    
    # Eye Prescription / Refraction
    if rx_table:
        od = rx_table.get('OD', {})
        os = rx_table.get('OS', {})
        lines.append("👁️ *SPECTACLE REFRACTION (POWER):*")
        od_text = f"• *OD (Right Eye):* SPH: {od.get('Sphere','')} | CYL: {od.get('Cylinder','')} | AXIS: {od.get('Axis','')} | ADD: {od.get('ADD','')}"
        os_text = f"• *OS (Left Eye):* SPH: {os.get('Sphere','')} | CYL: {os.get('Cylinder','')} | AXIS: {os.get('Axis','')} | ADD: {os.get('ADD','')}"
        lines.append(od_text)
        lines.append(os_text)
        if ipd:
            lines.append(f"• *IPD (Pupillary Distance):* {ipd}")
        lines.append("")
    
    # Recommended Spectacles
    if spectacles:
        lines.append("👓 *RECOMMENDED SPECTACLES:*")
        for spec in spectacles:
            lines.append(f"• {spec}")
        lines.append("")
        
    # Prescribed Medicines
    if medicines:
        lines.append("💊 *PRESCRIBED MEDICINES:*")
        for med_name, details in medicines.items():
            qty = details.get('quantity', 1)
            dosage = details.get('dosage', 'As directed')
            timing = details.get('timing', '')
            med_line = f"• *{med_name}* (Qty: {qty})\n   ↳ Dosage: {dosage}"
            if timing:
                med_line += f" | Timing: {timing}"
            lines.append(med_line)
        lines.append("")

    # Advice & Next Review
    if advice and advice != 'N/A':
        lines.append(f"💡 *Doctor's Advice:* {advice}")
        
    if next_review and next_review != 'N/A':
        lines.append(f"🗓️ *Next Review / Follow-up:* {next_review}")
        
    lines.extend([
        "",
        "------------------------------------",
        "⭐ *Rate Us on Google:* https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur",
        "📞 *Helpline / Appointments:* 9235647410 / 8299461251",
        "📍 Pura Khizir, Mubarakpur, Azamgarh (U.P.)"
    ])
    
    return "\n".join(lines)


def format_followup_reminder_message(patient_name, target_date_str, reason="", doctor_name="Dr. Danish"):
    """Format a respectful, friendly clinical follow-up reminder for WhatsApp"""
    return f"""🏥 *MAU EYE CARE - PATIENT REVIEW REMINDER* 👁️

Namaste *{patient_name}* ji,

This is a gentle reminder from *{doctor_name}* (B.Sc. Optometry, Reg: UPS 2908) at *Mau Eye Care*.

📋 *Follow-up Details:*
• Patient: {patient_name}
• Scheduled Review Date: {target_date_str}
• Purpose: {reason or 'Routine Eye Checkup / Spectacle Vision Review'}

⏰ *Clinic Timings:* Mon - Sat: 10:00 AM – 5:00 PM (Sunday Closed)
📍 *Address:* Pura Khizir (Near Mubarakpur Marriage Hall, Nai Pani ki tanki), Mubarakpur, Azamgarh (U.P.)
📞 *Helpline / Appointments:* 9235647410 / 8299461251

*Timely eye checkups protect your vision and ensure comfortable sight.*

⭐ *Rate Us on Google:* https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur"""
