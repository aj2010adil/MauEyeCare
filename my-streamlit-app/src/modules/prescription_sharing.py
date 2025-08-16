"""
Prescription Sharing Module - Cloud Compatible
Multiple ways to share prescriptions with patients
"""
import streamlit as st
from io import BytesIO
import base64
from urllib.parse import quote
import json
import time

def generate_qr_code_fallback(data):
    """Generate QR code using Google Charts API (cloud compatible)"""
    encoded_data = quote(data)
    qr_url = f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={encoded_data}"
    return qr_url

def create_shareable_link(prescription_data, patient_name):
    """Create shareable link for prescription"""
    # Encode prescription data
    prescription_text = f"Patient: {patient_name}\n"
    
    if prescription_data.get('prescription'):
        prescription_text += "Medicines:\n"
        for med, qty in prescription_data['prescription'].items():
            prescription_text += f"• {med} - Qty: {qty}\n"
    
    if prescription_data.get('rx_table'):
        prescription_text += "\nPrescription Details:\n"
        for eye in ['OD', 'OS']:
            eye_data = prescription_data['rx_table'].get(eye, {})
            if eye_data.get('Sphere'):
                prescription_text += f"{eye}: SPH {eye_data.get('Sphere', '')} "
                prescription_text += f"CYL {eye_data.get('Cylinder', '')} "
                prescription_text += f"AXIS {eye_data.get('Axis', '')}\n"
    
    # Create WhatsApp link
    whatsapp_text = quote(prescription_text)
    whatsapp_link = f"https://wa.me/?text={whatsapp_text}"
    
    # Create email link
    email_subject = quote(f"Prescription for {patient_name}")
    email_body = quote(prescription_text)
    email_link = f"mailto:?subject={email_subject}&body={email_body}"
    
    # Create SMS link
    sms_text = quote(prescription_text[:160])  # SMS limit
    sms_link = f"sms:?body={sms_text}"
    
    return {
        "whatsapp": whatsapp_link,
        "email": email_link,
        "sms": sms_link,
        "text": prescription_text
    }

def normalize_indian_mobile(mobile):
    """Normalize Indian mobile number with +91 prefix"""
    if not mobile:
        return mobile
    
    # Remove all spaces and special characters except +
    mobile = mobile.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # If already has +91, return as is
    if mobile.startswith('+91'):
        return mobile
    
    # If starts with 91, add +
    if mobile.startswith('91') and len(mobile) == 12:
        return '+' + mobile
    
    # If 10 digit number, add +91
    if len(mobile) == 10 and mobile.isdigit():
        return '+91' + mobile
    
    return mobile

def render_sharing_options(prescription_data, patient_name, patient_mobile=""):
    """Render prescription sharing UI"""
    
    # Extract mobile from prescription data if not provided
    if not patient_mobile and prescription_data.get('patient_mobile'):
        patient_mobile = prescription_data['patient_mobile']
    
    # Normalize mobile number with +91 prefix
    if patient_mobile:
        patient_mobile = normalize_indian_mobile(patient_mobile)
    
    # Create unique key suffix
    unique_id = str(int(time.time() * 1000))[-6:]
    key_suffix = f"{patient_name.replace(' ', '_')}_{unique_id}"
    
    st.subheader("📤 Share Prescription with Patient")
    
    if patient_mobile:
        st.success(f"📱 Patient Mobile: {patient_mobile}")
    else:
        st.warning("📱 No mobile number available - sharing options limited")
    
    # Create sharing links
    sharing_links = create_shareable_link(prescription_data, patient_name)
    
    # Sharing options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📱 WhatsApp**")
        if patient_mobile:
            # Clean mobile number for WhatsApp URL
            clean_mobile = patient_mobile.replace('+', '').replace(' ', '').replace('-', '')
            whatsapp_direct = f"https://wa.me/{clean_mobile}?text={quote(sharing_links['text'])}"
            st.markdown(f"[Send to {patient_mobile}]({whatsapp_direct})")
        st.markdown(f"[Share via WhatsApp]({sharing_links['whatsapp']})")
    
    with col2:
        st.markdown("**📧 Email**")
        st.markdown(f"[Send Email]({sharing_links['email']})")
    
    with col3:
        st.markdown("**💬 SMS**")
        if patient_mobile:
            sms_direct = f"sms:{patient_mobile}?body={quote(sharing_links['text'][:160])}"
            st.markdown(f"[Send SMS to {patient_mobile}]({sms_direct})")
        else:
            st.markdown(f"[Send SMS]({sharing_links['sms']})")
    
    # QR Code
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**📱 QR Code**")
        qr_data = sharing_links['text']
        qr_url = generate_qr_code_fallback(qr_data)
        st.markdown(f'<img src="{qr_url}" alt="Prescription QR Code" style="max-width: 200px;">', unsafe_allow_html=True)
        st.caption("Patient can scan with phone camera to view prescription instantly")
    
    with col2:
        st.markdown("**📋 Copy Text (Alternative)**")
        st.text_area("Prescription Text (Copy & Share)", sharing_links['text'], height=200, key=f"prescription_text_{key_suffix}")
        st.caption("Copy this text and paste in any messaging app")
    
    # Quick actions
    st.markdown("---")
    st.markdown("**⚡ Quick Actions**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📱 Open WhatsApp Web", key=f"whatsapp_btn_{key_suffix}"):
            st.markdown(f"[Open WhatsApp]({sharing_links['whatsapp']})")
    
    with col2:
        if st.button("📧 Open Email Client", key=f"email_btn_{key_suffix}"):
            st.markdown(f"[Open Email]({sharing_links['email']})")
    
    with col3:
        if st.button("📋 Copy to Clipboard", key=f"copy_btn_{key_suffix}"):
            st.code(sharing_links['text'])
            st.success("Text ready to copy!")
    
    with col4:
        if st.button("🖨️ Print Instructions", key=f"print_btn_{key_suffix}"):
            st.info("Use browser's print function (Ctrl+P) to print the prescription")
    
    # Mobile-friendly HTML prescription download with WhatsApp sharing (Priority)
    st.markdown("---")
    st.markdown("**📱 Recommended: HTML Prescription for Mobile Sharing**")
    if patient_mobile:
        st.success(f"✅ HTML format works best on mobile devices. Patient mobile {patient_mobile} will auto-populate in sharing apps.")
    else:
        st.info("✅ HTML format works best on mobile devices and can be easily shared via WhatsApp")
    
    # Generate HTML prescription
    html_prescription = create_patient_portal_link(prescription_data, patient_name)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download HTML Prescription (Recommended)",
            data=html_prescription,
            file_name=f"prescription_{patient_name.replace(' ', '_')}.html",
            mime="text/html",
            key=f"download_html_{key_suffix}",
            type="primary"
        )
        if patient_mobile:
            st.caption(f"✅ Best for mobile sharing - patient mobile {patient_mobile} included")
        else:
            st.caption("✅ Best for mobile sharing - works on all devices")
    
    with col2:
        # Enhanced sharing with patient mobile auto-populated
        if patient_mobile:
            # Clean mobile number for WhatsApp URL
            clean_mobile = patient_mobile.replace('+', '').replace(' ', '').replace('-', '')
            
            # WhatsApp sharing
            whatsapp_html_text = f"Hi {patient_name}! Your prescription from MauEyeCare is ready. I'm sending you the prescription file. Please open it on your phone to view all details. - Dr. Danish"
            whatsapp_direct_link = f"https://wa.me/{clean_mobile}?text={quote(whatsapp_html_text)}"
            
            col_wa, col_sms = st.columns(2)
            with col_wa:
                st.markdown(f"[📱 WhatsApp to {patient_mobile}]({whatsapp_direct_link})")
                st.caption("✅ Opens WhatsApp with patient number")
            
            with col_sms:
                # SMS sharing with patient mobile
                sms_text = f"Hi {patient_name}! Your prescription from MauEyeCare is ready. Please check the attached file. - Dr. Danish"
                sms_link = f"sms:{patient_mobile}?body={quote(sms_text)}"
                st.markdown(f"[💬 SMS to {patient_mobile}]({sms_link})")
                st.caption("✅ Opens SMS with patient number")
            
            st.success("✅ Patient mobile auto-populated in sharing links")
        else:
            whatsapp_html_text = f"Hi! Here's your prescription from MauEyeCare. Patient: {patient_name}. Please find the prescription file attached."
            whatsapp_html_link = f"https://wa.me/?text={quote(whatsapp_html_text)}"
            st.markdown(f"[📱 Share via WhatsApp]({whatsapp_html_link})")
            st.warning("⚠️ No patient mobile - you'll need to select contact manually")

def create_patient_portal_link(prescription_data, patient_name):
    """Create a mobile-friendly patient portal view"""
    
    # Create a mobile-optimized HTML page
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Prescription - {patient_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; background: #f5f5f5; font-size: 16px; }}
        .container {{ max-width: 100%; margin: 0 auto; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #2c5aa0; padding-bottom: 15px; margin-bottom: 20px; }}
        .clinic-name {{ font-size: 20px; font-weight: bold; color: #2c5aa0; }}
        .section {{ margin: 15px 0; }}
        .section-title {{ font-weight: bold; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; font-size: 18px; }}
        .medicine {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #2c5aa0; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        .whatsapp-share {{ background: #25d366; color: white; padding: 10px; text-align: center; border-radius: 5px; margin: 10px 0; }}
        .whatsapp-share a {{ color: white; text-decoration: none; font-weight: bold; }}
        @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} .whatsapp-share {{ display: none; }} }}
        @media (max-width: 600px) {{ .container {{ margin: 5px; padding: 10px; }} .clinic-name {{ font-size: 18px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="clinic-name">👁️ MauEyeCare Optical Center</div>
            <div>Dr. Danish - Eye Care Specialist</div>
            <div>Phone: +91 92356-47410</div>
        </div>
        
        <div class="section">
            <div class="section-title">Patient Information</div>
            <strong>Name:</strong> {patient_name}<br>
            <strong>Date:</strong> {prescription_data.get('date', 'Today')}
        </div>
        
        <div class="section">
            <div class="section-title">Prescribed Medications</div>
"""
    
    if prescription_data.get('prescription'):
        for med, qty in prescription_data['prescription'].items():
            html_content += f'<div class="medicine"><strong>{med}</strong><br>Quantity: {qty}</div>'
    
    html_content += f"""
        </div>
        
        <div class="section">
            <div class="section-title">Instructions</div>
            • Take medications as prescribed<br>
            • Follow up if symptoms persist<br>
            • Contact clinic for emergencies: +91 92356-47410
        </div>
        
        <div class="whatsapp-share">
            <a href="https://wa.me/?text=I have received my prescription from MauEyeCare. Thank you Dr. Danish!" target="_blank">
                📱 Share on WhatsApp - Thank the Doctor
            </a>
        </div>
        
        <div class="footer">
            MauEyeCare Optical Center - Your vision is our priority<br>
            📞 +91 92356-47410 | 📧 Contact us for any queries
        </div>
    </div>
    
    <script>
        // Auto-print option
        if(window.location.hash === '#print') {{
            window.print();
        }}
        
        // Mobile-friendly sharing
        function shareViaWhatsApp() {{
            const text = "I received my prescription from MauEyeCare. Patient: {patient_name}";
            const url = `https://wa.me/?text=${{encodeURIComponent(text)}}`;
            window.open(url, '_blank');
        }}
    </script>
</body>
</html>
"""
    
    return html_content.encode('utf-8')