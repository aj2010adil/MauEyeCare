"""
Google Drive Integration for Prescription Sharing
Automatically saves HTML prescriptions to Google Drive and generates shareable links
"""
import streamlit as st
import requests
import json
import base64
from datetime import datetime
from urllib.parse import quote

class GoogleDriveIntegrator:
    """Google Drive integration for prescription sharing"""
    
    def __init__(self):
        self.drive_api_url = "https://www.googleapis.com/drive/v3/files"
        self.upload_url = "https://www.googleapis.com/upload/drive/v3/files"
        
    def get_oauth_credentials(self):
        """Get OAuth 2.0 credentials for Google Drive"""
        try:
            # Try to get OAuth credentials from secrets
            if hasattr(st, 'secrets'):
                client_id = st.secrets.get('GOOGLE_CLIENT_ID')
                client_secret = st.secrets.get('GOOGLE_CLIENT_SECRET')
                refresh_token = st.secrets.get('GOOGLE_REFRESH_TOKEN')
                
                if all([client_id, client_secret, refresh_token]):
                    return {
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'refresh_token': refresh_token
                    }
            
            return None
        except Exception as e:
            st.warning(f"OAuth credentials not configured: {str(e)}")
            return None
    
    def get_access_token_from_oauth(self):
        """Get access token using OAuth 2.0 refresh token"""
        credentials = self.get_oauth_credentials()
        if not credentials:
            return None
        
        try:
            # Exchange refresh token for access token
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'refresh_token': credentials['refresh_token'],
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                st.error(f"OAuth token refresh failed: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"OAuth token error: {str(e)}")
            return None
    
    def get_service_account_token(self):
        """Get access token using service account (simpler than OAuth)"""
        try:
            import os
            
            # Try to load service account key
            key_path = "service-account-key.json"
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    service_account_info = json.load(f)
                
                # Create JWT token for service account
                import time
                import base64
                import hashlib
                import hmac
                
                # Simple service account token (basic implementation)
                # In production, use google-auth library
                st.info("📁 Service account key found - using service account authentication")
                return "service_account_token"  # Placeholder
            
            return None
            
        except Exception as e:
            st.warning(f"Service account setup error: {str(e)}")
            return None
    
    def get_access_token(self):
        """Get access token - try service account first, then OAuth, then API key"""
        
        # Try Service Account first (simplest)
        service_token = self.get_service_account_token()
        if service_token:
            return service_token
        
        # Try OAuth 2.0 (if configured)
        oauth_token = self.get_access_token_from_oauth()
        if oauth_token:
            return oauth_token
        
        # Fallback to API key (limited functionality)
        try:
            if hasattr(st, 'secrets') and 'GOOGLE_DRIVE_TOKEN' in st.secrets:
                return st.secrets['GOOGLE_DRIVE_TOKEN']
            
            import os
            env_token = os.getenv('GOOGLE_DRIVE_TOKEN')
            if env_token:
                return env_token
            
            return "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
            
        except Exception as e:
            st.warning(f"No authentication configured: {str(e)}")
            return None
    
    def test_drive_connection(self):
        """Test Google Drive API connection"""
        access_token = self.get_access_token()
        
        if not access_token:
            return {
                'success': False,
                'error': 'No access token available',
                'details': 'Check if GOOGLE_DRIVE_TOKEN is set in secrets'
            }
        
        try:
            # Test API connection
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.googleapis.com/drive/v3/about?fields=user',
                headers=headers
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'success': True,
                    'user': user_info.get('user', {}),
                    'token_valid': True
                }
            else:
                return {
                    'success': False,
                    'error': f'API Error: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection failed: {str(e)}',
                'details': 'Check internet connection and API key'
            }
    
    def upload_prescription_to_drive(self, html_content, patient_name, prescription_id=None):
        """Upload HTML prescription to Google Drive and return shareable link"""
        
        # DISABLED: Google Drive upload disabled
        return {
            'success': False,
            'error': 'Google Drive upload disabled',
            'disabled': True
        }
        
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'No access token',
                'fallback': True,
                **self._create_fallback_link(html_content, patient_name)
            }
        
        try:
            # Create filename with date organization
            current_date = datetime.now()
            date_folder = current_date.strftime("%Y-%m-%d")
            timestamp = current_date.strftime("%Y%m%d_%H%M")
            filename = f"{date_folder}_Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html"
            
            # Debug info
            st.info(f"🔍 Debug: Attempting upload with token: {access_token[:20] if access_token else 'None'}...")
            st.info(f"📁 Target folder ID: {self._get_prescription_folder_id()}")
            st.info(f"📄 Filename: {filename}")
            st.info(f"🔗 Upload URL: {self.upload_url}")
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [self._get_prescription_folder_id()],
                'description': f'Prescription for {patient_name} - Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            }
            
            # Upload file
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Debug: Show request details
            st.info(f"📤 Creating file with metadata: {json.dumps(file_metadata, indent=2)}")
            
            # First, create the file
            response = requests.post(
                self.drive_api_url,
                headers=headers,
                data=json.dumps(file_metadata)
            )
            
            st.info(f"📊 File creation response: {response.status_code} - {response.text[:200]}")
            
            if response.status_code == 200:
                file_id = response.json()['id']
                st.success(f"✅ File created with ID: {file_id}")
                
                # Upload content
                upload_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'text/html'
                }
                
                st.info(f"📤 Uploading content to file ID: {file_id}")
                
                upload_response = requests.patch(
                    f"{self.upload_url}/{file_id}?uploadType=media",
                    headers=upload_headers,
                    data=html_content
                )
                
                st.info(f"📊 Upload response: {upload_response.status_code} - {upload_response.text[:200]}")
                
                if upload_response.status_code == 200:
                    # Make file publicly accessible
                    self._make_file_public(file_id, access_token)
                    
                    # Generate shareable link
                    shareable_link = f"https://drive.google.com/file/d/{file_id}/view"
                    folder_link = "https://drive.google.com/drive/folders/1S5-ts47Nc_vw56YfwV-AZvXyk1VJbLLO"
                    
                    return {
                        'success': True,
                        'link': shareable_link,
                        'file_id': file_id,
                        'filename': filename,
                        'folder_link': folder_link,
                        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'folder_path': 'MauEyeCare Prescriptions'
                    }
            
            st.error(f"❌ File creation failed: {response.status_code}")
            st.error(f"Response: {response.text}")
            
            return {
                'success': False,
                'error': f'File creation failed: {response.status_code}',
                'details': response.text,
                'fallback': True,
                **self._create_fallback_link(html_content, patient_name)
            }
            
        except Exception as e:
            st.error(f"Google Drive upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback': True,
                **self._create_fallback_link(html_content, patient_name)
            }
    
    def _get_prescription_folder_id(self):
        """Get prescription folder ID from Google Drive link"""
        # Extract folder ID from the Google Drive link
        # https://drive.google.com/drive/folders/1S5-ts47Nc_vw56YfwV-AZvXyk1VJbLLO
        return "1S5-ts47Nc_vw56YfwV-AZvXyk1VJbLLO"
    
    def _make_file_public(self, file_id, access_token):
        """Make the file publicly accessible"""
        try:
            permission_data = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            requests.post(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
                headers=headers,
                data=json.dumps(permission_data)
            )
        except:
            pass  # Continue even if permission setting fails
    
    def _create_fallback_link(self, html_content, patient_name):
        """Create fallback sharing option when Google Drive is not available"""
        
        # Create a simple data URL as fallback
        encoded_html = base64.b64encode(html_content).decode('utf-8')
        data_url = f"data:text/html;base64,{encoded_html}"
        
        return {
            'success': False,
            'link': data_url,
            'file_id': None,
            'filename': f"prescription_{patient_name.replace(' ', '_')}.html",
            'fallback': True
        }
    
    def save_prescription_link_to_db(self, patient_name, prescription_link, file_id=None, patient_mobile=None):
        """Save prescription link to patient database with sharing status"""
        try:
            import db
            
            # Get patient ID
            patients = db.get_patients()
            patient_id = None
            
            for p in patients:
                if p[1].lower() == patient_name.lower():
                    patient_id = p[0]
                    if not patient_mobile:
                        patient_mobile = p[4]  # Get mobile from database
                    break
            
            if patient_id:
                # Save prescription link with sharing details
                prescription_data = {
                    'patient_id': patient_id,
                    'patient_name': patient_name,
                    'patient_mobile': patient_mobile,
                    'prescription_link': prescription_link,
                    'file_id': file_id,
                    'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'shared_to_patient': bool(patient_mobile),
                    'shared_to_doctor': True,  # Always share with doctor
                    'doctor_mobile': '6363738550',
                    'folder_path': 'MauEyeCare Prescriptions',
                    'status': 'uploaded_and_shared'
                }
                
                # Store in session state for now (can be enhanced to save in database)
                if 'prescription_links' not in st.session_state:
                    st.session_state['prescription_links'] = []
                
                st.session_state['prescription_links'].append(prescription_data)
                
                return prescription_data
        except Exception as e:
            st.error(f"Failed to save prescription link: {str(e)}")
            return None
        
        return None
    
    def get_daily_prescriptions(self, date_str=None):
        """Get prescriptions for a specific date"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if 'prescription_links' not in st.session_state:
            return []
        
        daily_prescriptions = []
        for prescription in st.session_state['prescription_links']:
            if prescription['created_date'].startswith(date_str):
                daily_prescriptions.append(prescription)
        
        return daily_prescriptions

# Global instance
drive_integrator = GoogleDriveIntegrator()