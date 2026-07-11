"""
Integration Configuration for MauEyeCare
Configure WhatsApp and Google Drive integrations
"""

import streamlit as st
import os

def show_integration_setup():
    """Show integration setup page"""
    
    st.header("🔧 Integration Setup")
    st.markdown("Configure WhatsApp and Google Drive integrations for prescription sharing")
    
    # WhatsApp Configuration
    st.subheader("📱 WhatsApp Business API Setup")
    
    with st.expander("📋 WhatsApp Configuration Instructions"):
        st.markdown("""
        **To enable WhatsApp integration:**
        
        1. **Get WhatsApp Business API Access:**
           - Go to [Facebook Developers](https://developers.facebook.com/)
           - Create a new app and add WhatsApp Business API
           - Get your Access Token and Phone Number ID
        
        2. **Configure in Streamlit:**
           - Add to `.streamlit/secrets.toml`:
           ```toml
           WHATSAPP_ACCESS_TOKEN = "your_access_token_here"
           WHATSAPP_PHONE_NUMBER_ID = "your_phone_number_id_here"
           ```
        
        3. **Alternative Methods:**
           - WhatsApp Web integration (no API required)
           - Manual copy-paste of messages
        """)
    
    # Current WhatsApp Status
    from modules.whatsapp_utils import test_whatsapp_connection
    whatsapp_status = test_whatsapp_connection()
    
    if whatsapp_status['success']:
        if whatsapp_status.get('demo'):
            st.warning("📱 WhatsApp is in demo mode - configure real tokens for production")
        else:
            st.success("📱 WhatsApp API is configured and working!")
    else:
        st.error("📱 WhatsApp API not configured")
        st.info("💡 Don't worry! You can still use WhatsApp Web integration")
    
    # Google Drive Configuration
    st.subheader("☁️ Google Drive API Setup")
    
    with st.expander("📋 Google Drive Configuration Instructions"):
        st.markdown("""
        **To enable Google Drive integration:**
        
        1. **Get Google Drive API Access:**
           - Go to [Google Cloud Console](https://console.cloud.google.com/)
           - Enable Google Drive API
           - Create credentials (Service Account or OAuth 2.0)
        
        2. **Configure in Streamlit:**
           - Add to `.streamlit/secrets.toml`:
           ```toml
           GOOGLE_DRIVE_TOKEN = "your_access_token_here"
           ```
        
        3. **Create Prescription Folder:**
           - Create a folder in Google Drive for prescriptions
           - Share it publicly or with specific users
        """)
    
    # Current Google Drive Status
    from modules.google_drive_integration import GoogleDriveIntegrator
    drive_integrator = GoogleDriveIntegrator()
    drive_status = drive_integrator.test_drive_connection()
    
    if drive_status['success']:
        st.success("☁️ Google Drive API is configured and working!")
        if 'user' in drive_status:
            user_info = drive_status['user']
            st.info(f"📧 Connected as: {user_info.get('emailAddress', 'Unknown')}")
    else:
        st.error("☁️ Google Drive API not configured")
        st.info("💡 Prescriptions will be generated but not uploaded to cloud")
    
    # Test Integration
    st.subheader("🧪 Test Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Test WhatsApp"):
            test_number = st.text_input("Test Phone Number (with country code):", 
                                      placeholder="919876543210")
            if test_number:
                from modules.whatsapp_utils import send_text_message
                result = send_text_message(test_number, "Test message from MauEyeCare! 👁️")
                
                if result['success']:
                    st.success("✅ WhatsApp test successful!")
                else:
                    st.error(f"❌ WhatsApp test failed: {result.get('error')}")
    
    with col2:
        if st.button("☁️ Test Google Drive"):
            result = drive_integrator.test_drive_connection()
            
            if result['success']:
                st.success("✅ Google Drive test successful!")
            else:
                st.error(f"❌ Google Drive test failed: {result.get('error')}")
    
    # Manual Configuration
    st.subheader("⚙️ Manual Configuration")
    
    st.markdown("""
    **If you don't want to use API integrations:**
    
    1. **WhatsApp:** Use WhatsApp Web integration (opens in browser)
    2. **Google Drive:** Manually upload prescription files
    3. **SMS:** Copy prescription links and send via SMS
    4. **Email:** Copy prescription content and email to patients
    
    The system works perfectly without API configurations!
    """)

if __name__ == "__main__":
    show_integration_setup()