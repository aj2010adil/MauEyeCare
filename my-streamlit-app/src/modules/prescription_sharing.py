"""
Prescription Sharing Module
Multiple ways to share prescriptions with patients
"""
import streamlit as st
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote

def generate_qr_code(prescription_url):
    """Generate QR code for prescription sharing"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(prescription_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

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

def render_sharing_options(prescription_data, patient_name, patient_mobile=""):
    """Render prescription sharing UI"""
    
    st.subheader("📤 Share Prescription with Patient")
    
    # Create sharing links
    sharing_links = create_shareable_link(prescription_data, patient_name)
    
    # Sharing options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📱 WhatsApp**")
        if patient_mobile:
            whatsapp_direct = f"https://wa.me/{patient_mobile.replace('+', '').replace(' ', '')}?text={quote(sharing_links['text'])}"
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
        try:
            qr_data = sharing_links['text']
            qr_image = generate_qr_code(qr_data)
            st.image(qr_image, caption="Scan to view prescription", width=200)
            
            # Download QR code
            st.download_button(
                label="📥 Download QR Code",
                data=qr_image,
                file_name=f"prescription_qr_{patient_name.replace(' ', '_')}.png",
                mime="image/png"
            )
        except Exception as e:
            st.error("QR code generation failed. Install qrcode package.")
    
    with col2:
        st.markdown("**📋 Copy Text**")
        st.text_area("Prescription Text (Copy & Share)", sharing_links['text'], height=200)
    
    # Quick actions
    st.markdown("---")
    st.markdown("**⚡ Quick Actions**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📱 Open WhatsApp Web"):
            st.markdown(f"[Open WhatsApp]({sharing_links['whatsapp']})")
    
    with col2:
        if st.button("📧 Open Email Client"):
            st.markdown(f"[Open Email]({sharing_links['email']})")
    
    with col3:
        if st.button("📋 Copy to Clipboard"):
            st.code(sharing_links['text'])
            st.success("Text ready to copy!")
    
    with col4:
        if st.button("🖨️ Print Instructions"):
            st.info("Use browser's print function (Ctrl+P) to print the prescription")

def create_patient_portal_link(prescription_data, patient_name):
    """Create a simple patient portal view"""
    
    # Encode prescription data as base64 for URL
    import json
    prescription_json = json.dumps({
        "patient": patient_name,
        "prescription": prescription_data.get('prescription', {}),
        "rx_table": prescription_data.get('rx_table', {}),
        "advice": prescription_data.get('advice', ''),
        "date": prescription_data.get('date', '')
    })
    
    encoded_data = base64.b64encode(prescription_json.encode()).decode()
    
    # Create a simple HTML page
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Prescription - {patient_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #2c5aa0; padding-bottom: 15px; margin-bottom: 20px; }}
        .clinic-name {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
        .section {{ margin: 15px 0; }}
        .section-title {{ font-weight: bold; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        .medicine {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #2c5aa0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} }}
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
        
        <div class="footer">
            MauEyeCare Optical Center - Your vision is our priority
        </div>
    </div>
    
    <script>
        // Auto-print option
        if(window.location.hash === '#print') {{
            window.print();
        }}
    </script>
</body>
</html>
"""
    
    return html_content.encode('utf-8')