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
from modules.google_drive_integration import drive_integrator

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
    
    # Mobile-friendly HTML prescription download with WhatsApp sharing
    st.markdown("---")
    st.markdown("**📱 HTML Prescription Sharing Options**")
    if patient_mobile:
        st.info(f"💡 Choose your preferred sharing method. Patient mobile {patient_mobile} will auto-populate in sharing apps.")
    else:
        st.info("💡 Choose your preferred sharing method. Add patient mobile for auto-populated sharing.")
    
    # Generate HTML prescription
    html_prescription = create_patient_portal_link(prescription_data, patient_name)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download HTML Prescription",
            data=html_prescription,
            file_name=f"prescription_{patient_name.replace(' ', '_')}.html",
            mime="text/html",
            key=f"download_html_{key_suffix}"
        )
        if patient_mobile:
            st.caption(f"✅ Manual sharing - patient mobile {patient_mobile} included")
        else:
            st.caption("✅ Manual sharing - works on all devices")
    
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
            
            # Enhanced workflow instructions
            st.markdown("**🚀 Sharing Options:**")
            st.markdown("""
            **Option 1 - Google Drive Auto-Upload (Recommended):**
            1. 🌐 **Upload to Google Drive** (button below)
            2. 📁 **Stored in**: MauEyeCare Prescriptions folder
            3. 📱 **Auto-notify**: Doctor (6363738550) & Patient
            4. 🔗 **Share links** generated automatically
            
            **Option 2 - Manual File Sharing:**
            1. 📥 **Download HTML** (above button)
            2. 📱 **Click WhatsApp/SMS** (opens with patient number)
            3. 📎 **Attach downloaded file** (from Downloads folder)
            4. ➡️ **Send** - Done!
            """)
            
            # Alternative: Share prescription content directly
            st.markdown("---")
            st.markdown("**⚡ Alternative: Send Prescription Text Directly**")
            
            # Create comprehensive prescription text
            prescription_summary = f"""Hi {patient_name}!

Your prescription from MauEyeCare is ready:

"""
            
            if prescription_data.get('prescription'):
                prescription_summary += "MEDICINES:\n"
                for med, qty in prescription_data['prescription'].items():
                    prescription_summary += f"• {med} - Qty: {qty}\n"
                prescription_summary += "\n"
            
            if prescription_data.get('rx_table'):
                prescription_summary += "EYE PRESCRIPTION:\n"
                for eye in ['OD', 'OS']:
                    eye_data = prescription_data['rx_table'].get(eye, {})
                    if eye_data.get('Sphere'):
                        prescription_summary += f"{eye}: SPH {eye_data.get('Sphere', '')} CYL {eye_data.get('Cylinder', '')} AXIS {eye_data.get('Axis', '')}\n"
                prescription_summary += "\n"
            
            prescription_summary += f"""INSTRUCTIONS:
• Take medications as prescribed
• Follow up if symptoms persist
• Contact us: +91 92356-47410

Best regards,
Dr. Danish
MauEyeCare Optical Center"""
            
            # Direct sharing with full prescription text
            col_direct_wa, col_direct_sms = st.columns(2)
            
            with col_direct_wa:
                direct_wa_link = f"https://wa.me/{clean_mobile}?text={quote(prescription_summary)}"
                st.markdown(f"[🚀 Send Complete Prescription via WhatsApp]({direct_wa_link})")
                st.caption("✅ No file attachment needed")
            
            with col_direct_sms:
                # SMS has character limit, so send shorter version
                sms_summary = f"Hi {patient_name}! Your prescription is ready. Please visit MauEyeCare or call +91 92356-47410 for details. - Dr. Danish"
                direct_sms_link = f"sms:{patient_mobile}?body={quote(sms_summary)}"
                st.markdown(f"[🚀 Send SMS Notification]({direct_sms_link})")
                st.caption("✅ Quick notification to patient")
            
            # Google Drive Integration
            st.markdown("---")
            st.markdown("**🌐 Google Drive Auto-Upload & Share**")
            
            # Test connection button
            if st.button("🔍 Test Google Drive Connection", key=f"test_drive_{key_suffix}"):
                with st.spinner("Testing Google Drive connection..."):
                    test_result = drive_integrator.test_drive_connection()
                
                if test_result['success']:
                    st.success("✅ Google Drive connection successful!")
                    if 'user' in test_result:
                        st.info(f"👤 Connected as: {test_result['user'].get('displayName', 'Unknown')}")
                else:
                    st.error(f"❌ Connection failed: {test_result['error']}")
                    st.error(f"Details: {test_result.get('details', 'No details')}")
            
            col_drive, col_status = st.columns([2, 1])
            
            with col_drive:
                if st.button("🚀 Upload to Google Drive & Share Link", key=f"drive_upload_{key_suffix}", type="primary"):
                    with st.spinner("Uploading prescription to Google Drive..."):
                        # Generate HTML prescription
                        html_prescription = create_patient_portal_link(prescription_data, patient_name)
                        
                        # Upload to Google Drive
                        upload_result = drive_integrator.upload_prescription_to_drive(
                            html_prescription, patient_name
                        )
                        
                        if upload_result['success']:
                            # Save link to database with sharing details
                            sharing_data = drive_integrator.save_prescription_link_to_db(
                                patient_name, upload_result['link'], upload_result['file_id'], patient_mobile
                            )
                            
                            # Detailed success notification
                            st.success("✅ Prescription Successfully Uploaded to Google Drive!")
                            
                            # Upload details
                            col_details, col_sharing = st.columns(2)
                            
                            with col_details:
                                st.info(f"""
                                **📁 Upload Details:**
                                • **File**: {upload_result['filename']}
                                • **Folder**: MauEyeCare Prescriptions
                                • **Time**: {upload_result['upload_time']}
                                • **Status**: ✅ Successfully Uploaded
                                """)
                            
                            with col_sharing:
                                st.info(f"""
                                **📤 Sharing Status:**
                                • **Patient**: {patient_name} {'(✅ Will be shared)' if patient_mobile else '(⚠️ No mobile)'}
                                • **Doctor**: Dr. Danish (✅ Notified)
                                • **Doctor Mobile**: 6363738550
                                """)
                            
                            # Sharing links
                            st.markdown("**🔗 Sharing Links:**")
                            
                            col_patient, col_doctor = st.columns(2)
                            
                            with col_patient:
                                if patient_mobile:
                                    drive_message = f"Hi {patient_name}! Your prescription from MauEyeCare is ready. View it here: {upload_result['link']} - Dr. Danish"
                                    drive_wa_link = f"https://wa.me/{clean_mobile}?text={quote(drive_message)}"
                                    st.markdown(f"[📱 Share with Patient]({drive_wa_link})")
                                else:
                                    st.warning("⚠️ Patient mobile not available")
                            
                            with col_doctor:
                                doctor_message = f"Prescription uploaded for {patient_name}. Link: {upload_result['link']} Folder: {upload_result['folder_link']}"
                                doctor_wa_link = f"https://wa.me/916363738550?text={quote(doctor_message)}"
                                st.markdown(f"[📱 Notify Doctor (6363738550)]({doctor_wa_link})")
                            
                            # Direct links for copying
                            st.markdown("**📋 Copy Links:**")
                            st.code(f"Patient Link: {upload_result['link']}", language="text")
                            st.code(f"Folder Link: {upload_result['folder_link']}", language="text")
                            
                            # Store in session for later use
                            st.session_state[f'drive_link_{patient_name}'] = upload_result['link']
                            st.session_state[f'drive_data_{patient_name}'] = upload_result
                            
                        else:
                            if upload_result.get('fallback'):
                                st.warning("⚠️ Google Drive upload failed. Using fallback method.")
                                st.error(f"Error: {upload_result.get('error', 'Unknown error')}")
                                if upload_result.get('details'):
                                    st.error(f"Details: {upload_result['details']}")
                                st.info("💡 Use 'Test Google Drive Connection' button to diagnose issues")
                            else:
                                st.error("❌ Failed to upload to Google Drive")
                                st.error(f"Error: {upload_result.get('error', 'Unknown error')}")
            
            with col_status:
                # Show existing Google Drive link if available
                existing_link = st.session_state.get(f'drive_link_{patient_name}')
                existing_data = st.session_state.get(f'drive_data_{patient_name}')
                
                if existing_link:
                    st.success("✅ Already uploaded")
                    st.markdown(f"[🔗 View Link]({existing_link})")
                    if existing_data:
                        st.caption(f"Uploaded: {existing_data.get('upload_time', 'Unknown')}")
                else:
                    st.info("📁 Not uploaded yet")
            
            # Daily prescriptions summary
            st.markdown("---")
            st.markdown("**📅 Today's Prescriptions Summary**")
            
            daily_prescriptions = drive_integrator.get_daily_prescriptions()
            if daily_prescriptions:
                st.success(f"✅ {len(daily_prescriptions)} prescriptions uploaded today")
                
                for i, prescription in enumerate(daily_prescriptions, 1):
                    with st.expander(f"{i}. {prescription['patient_name']} - {prescription['created_date']}"):
                        col_info, col_links = st.columns(2)
                        
                        with col_info:
                            st.write(f"**Patient**: {prescription['patient_name']}")
                            st.write(f"**Mobile**: {prescription.get('patient_mobile', 'N/A')}")
                            st.write(f"**Status**: {prescription['status']}")
                        
                        with col_links:
                            st.markdown(f"[🔗 View Prescription]({prescription['prescription_link']})")
                            if prescription.get('patient_mobile'):
                                patient_msg = f"Hi {prescription['patient_name']}! Your prescription: {prescription['prescription_link']}"
                                patient_link = f"https://wa.me/{prescription['patient_mobile'].replace('+', '').replace(' ', '')}?text={quote(patient_msg)}"
                                st.markdown(f"[📱 Share with Patient]({patient_link})")
            else:
                st.info("📅 No prescriptions uploaded today yet")
        else:
            whatsapp_html_text = f"Hi! Here's your prescription from MauEyeCare. Patient: {patient_name}. Please find the prescription file attached."
            whatsapp_html_link = f"https://wa.me/?text={quote(whatsapp_html_text)}"
            st.markdown(f"[📱 Share via WhatsApp]({whatsapp_html_link})")
            st.warning("⚠️ No patient mobile - you'll need to select contact manually")
            st.info("💡 **Tip**: Add patient mobile number in the Patient form to enable auto-populated sharing")
            
            # Google Drive option even without mobile
            st.markdown("---")
            st.markdown("**🌐 Google Drive Upload (No Mobile Required)**")
            
            if st.button("🚀 Upload to Google Drive", key=f"drive_upload_no_mobile_{key_suffix}"):
                with st.spinner("Uploading prescription to Google Drive..."):
                    html_prescription = create_patient_portal_link(prescription_data, patient_name)
                    upload_result = drive_integrator.upload_prescription_to_drive(html_prescription, patient_name)
                    
                    if upload_result['success']:
                        sharing_data = drive_integrator.save_prescription_link_to_db(patient_name, upload_result['link'], upload_result['file_id'])
                        
                        st.success("✅ Prescription uploaded to Google Drive!")
                        st.info(f"""
                        **📁 Upload Details:**
                        • **File**: {upload_result['filename']}
                        • **Folder**: MauEyeCare Prescriptions
                        • **Time**: {upload_result['upload_time']}
                        """)
                        
                        st.code(f"Share Link: {upload_result['link']}", language="text")
                        st.code(f"Folder Link: {upload_result['folder_link']}", language="text")
                        
                        # Doctor notification
                        doctor_message = f"Prescription uploaded for {patient_name}. Link: {upload_result['link']}"
                        doctor_wa_link = f"https://wa.me/916363738550?text={quote(doctor_message)}"
                        st.markdown(f"[📱 Notify Doctor (6363738550)]({doctor_wa_link})")
                        
                        st.session_state[f'drive_link_{patient_name}'] = upload_result['link']
                    else:
                        st.error("❌ Google Drive upload failed")
                        st.error(f"Error: {upload_result.get('error', 'Unknown error')}")
                        if upload_result.get('details'):
                            st.error(f"Details: {upload_result['details']}")
                        st.info("💡 Use 'Test Google Drive Connection' button to diagnose issues")

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