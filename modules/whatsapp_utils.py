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
    """Generate WhatsApp Web URL for sending message safely with validation and auto-country code"""
    import re
    # Extract only digits
    digits_only = re.sub(r'\D', '', str(phone_number or ''))
    encoded_message = urllib.parse.quote(message)
    
    # If no valid digits or less than 10 digits (e.g. name or empty), open generic WhatsApp share link
    if len(digits_only) < 10:
        return f"https://wa.me/?text={encoded_message}"
        
    # If standard 10-digit Indian mobile number, prefix 91
    if len(digits_only) == 10:
        digits_only = "91" + digits_only
    elif len(digits_only) == 11 and digits_only.startswith("0"):
        digits_only = "91" + digits_only[1:]
        
    return f"https://wa.me/{digits_only}?text={encoded_message}"

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


# ─────────────────────────────────────────────
# LANGUAGE OPTIONS for doctor to choose from
# ─────────────────────────────────────────────
REMINDER_LANGUAGE_OPTIONS = [
    "🌐 Urdu-Hindi Mixed (Default)",
    "اردو  Urdu Only",
    "हिंदी  Hindi Only",
]

def format_followup_reminder_message(patient_name, target_date_str, reason="", doctor_name="Dr. Danish", language="🌐 Urdu-Hindi Mixed (Default)"):
    """
    Format a culturally appropriate WhatsApp follow-up reminder.
    language choices:
      - '🌐 Urdu-Hindi Mixed (Default)' : Hindustani mix, Islamic tone (recommended for Mubarakpur)
      - 'اردو  Urdu Only'               : Pure Urdu script with full Islamic etiquette
      - 'हिंदी  Hindi Only'              : Pure Hindi for Hindu / general patients
    """

    # Clean up reason — strip the raw "Interval:" text if no real diagnosis was captured
    clean_reason = ""
    if reason and "Interval:" not in reason and reason.strip():
        clean_reason = reason.strip()

    # ──────────────────────────────────────────
    # 1. URDU-HINDI MIXED (Default / Islamic)
    # ──────────────────────────────────────────
    if "Urdu-Hindi" in language or "Mixed" in language or "Default" in language:
        purpose_line = f"• *Wajah:* {clean_reason}" if clean_reason else ""
        return f"""🕌 *السلام علیکم ورحمۃ اللہ وبرکاتہ*
_Assalamu Alaikum wa Rahmatullahi wa Barakatuh_

*{patient_name}* ji, Aadab! 🙏

Yeh aek mohabbat bhari yaad-daasht hai *{doctor_name}* (B.Sc. Optometry, Reg: UPS 2908) ki taraf se — *Mau Eye Care, Mubarakpur*.

━━━━━━━━━━━━━━━━━━━━━
👁️ *Aankh Ki Jaanch Ka Waqt Aa Gaya Hai*
━━━━━━━━━━━━━━━━━━━━━

📋 *Tafseelat:*
• *Mareez:* {patient_name}
• *Mulaqaat Ki Taareekh:* {target_date_str}
{purpose_line}

_"Sehat Allah ki naaimat hai — aankhein uski amaanat hain."_
Waqt par jaanch karwaana iss amaanat ki hifazat hai. 🤲

━━━━━━━━━━━━━━━━━━━━━
🏥 *Mau Eye Care — Mubarakpur*
━━━━━━━━━━━━━━━━━━━━━
⏰ *Waqt:* Peer ta Shanichar, Subah 10 baje – Shaam 5 baje
   _(Itwar / Sunday band)_
📍 *Pata:* Pura Khizir (Shaadi Hall ke paas, Nai Pani Ki Tanki), Mubarakpur, Azamgarh
📞 *Appointment:* 9235647410 / 8299461251

⭐ *Google par Rate Karein:*
https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur

_InshAllah, aapki aankhein hamesha roshni se bhari rahein._ 🤲
*Allah Hafiz!*"""

    # ──────────────────────────────────────────
    # 2. PURE URDU (Full Islamic / Urdu script)
    # ──────────────────────────────────────────
    elif "Urdu" in language or "اردو" in language:
        purpose_line = f"• *وجہ:* {clean_reason}" if clean_reason else ""
        return f"""🕌 *السلام علیکم ورحمۃ اللہ وبرکاتہ*

*{patient_name}* جی، آداب! 🙏

یہ ایک محبت بھری یاد دہانی ہے *{doctor_name}* (B.Sc. آپٹومیٹری، Reg: UPS 2908) کی طرف سے — *Mau Eye Care، مبارکپور*۔

━━━━━━━━━━━━━━━━━━━━━
👁️ *آنکھ کی جانچ کا وقت آ گیا ہے*
━━━━━━━━━━━━━━━━━━━━━

📋 *تفصیلات:*
• *مریض:* {patient_name}
• *ملاقات کی تاریخ:* {target_date_str}
{purpose_line}

_"صحت اللہ کی نعمت ہے — آنکھیں اس کی امانت ہیں۔"_
وقت پر جانچ کروانا اس امانت کی حفاظت ہے۔ 🤲

━━━━━━━━━━━━━━━━━━━━━
🏥 *Mau Eye Care — مبارکپور*
━━━━━━━━━━━━━━━━━━━━━
⏰ *وقت:* پیر تا ہفتہ — صبح ۱۰ بجے تا شام ۵ بجے
   _(اتوار کو کلینک بند رہے گی)_
📍 *پتہ:* پورہ خضیر (شادی ہال کے پاس، نئی پانی کی ٹنکی)، مبارکپور، اعظم گڑھ (یو پی)
📞 *ملاقات:* 9235647410 / 8299461251

⭐ *گوگل پر ریٹ کریں:*
https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur

_ان شاء اللہ، آپ کی آنکھیں ہمیشہ روشنی سے بھری رہیں۔_ 🤲
*اللہ حافظ!*"""

    # ──────────────────────────────────────────
    # 3. PURE HINDI (हिंदी - for Hindu patients)
    # ──────────────────────────────────────────
    else:
        purpose_line = f"• *कारण:* {clean_reason}" if clean_reason else ""
        return f"""🏥 *मऊ आई केयर — मुबारकपुर*
👁️ *नेत्र जांच की याद दिलाना*

नमस्ते *{patient_name}* जी! 🙏

यह एक विनम्र सूचना है *{doctor_name}* (B.Sc. ऑप्टोमेट्री, Reg: UPS 2908) की ओर से — *Mau Eye Care, मुबारकपुर*।

━━━━━━━━━━━━━━━━━━━━━
📋 *विवरण (Details):*
• *मरीज़:* {patient_name}
• *जांच की तारीख:* {target_date_str}
{purpose_line}

_"आँखें ईश्वर का अनमोल उपहार हैं — समय पर जांच करवाएं।"_ 🌟

━━━━━━━━━━━━━━━━━━━━━
🏥 *Mau Eye Care — मुबारकपुर*
━━━━━━━━━━━━━━━━━━━━━
⏰ *समय:* सोमवार से शनिवार — सुबह 10 बजे से शाम 5 बजे तक
   _(रविवार को क्लिनिक बंद रहेगी)_
📍 *पता:* पुरा ख़िज़ीर (शादी हॉल के पास, नई पानी की टंकी), मुबारकपुर, आज़मगढ़ (उ.प्र.)
📞 *अपॉइंटमेंट:* 9235647410 / 8299461251

⭐ *Google पर हमें Rate करें:*
https://maps.google.com/?q=Mau+Eye+Care+Mubarakpur

_भगवान करे, आपकी आँखें सदा स्वस्थ और रोशन रहें।_ 🙏
*धन्यवाद!*"""
