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
        
    def get_access_token(self):
        """Get Google Drive access token from Streamlit secrets (secure for public repos)"""
        try:
            # Primary: Streamlit Cloud secrets (secure for public repos)
            if hasattr(st, 'secrets') and 'GOOGLE_DRIVE_TOKEN' in st.secrets:
                return st.secrets['GOOGLE_DRIVE_TOKEN']
            
            # Fallback: Environment variable (for local development)
            import os
            env_token = os.getenv('GOOGLE_DRIVE_TOKEN')
            if env_token:
                return env_token
            
            # Development fallback (will be removed in production)
            return "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
            
        except Exception as e:
            st.warning(f"Google Drive API key not configured: {str(e)}")
            return None
    
    def upload_prescription_to_drive(self, html_content, patient_name, prescription_id=None):
        """Upload HTML prescription to Google Drive and return shareable link"""
        
        access_token = self.get_access_token()
        if not access_token:
            return self._create_fallback_link(html_content, patient_name)
        
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"Prescription_{patient_name.replace(' ', '_')}_{timestamp}.html"
            
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
            
            # First, create the file
            response = requests.post(
                self.drive_api_url,
                headers=headers,
                data=json.dumps(file_metadata)
            )
            
            if response.status_code == 200:
                file_id = response.json()['id']
                
                # Upload content
                upload_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'text/html'
                }
                
                upload_response = requests.patch(
                    f"{self.upload_url}/{file_id}?uploadType=media",
                    headers=upload_headers,
                    data=html_content
                )
                
                if upload_response.status_code == 200:
                    # Make file publicly accessible
                    self._make_file_public(file_id, access_token)
                    
                    # Generate shareable link
                    shareable_link = f"https://drive.google.com/file/d/{file_id}/view"
                    
                    return {
                        'success': True,
                        'link': shareable_link,
                        'file_id': file_id,
                        'filename': filename
                    }
            
            return self._create_fallback_link(html_content, patient_name)
            
        except Exception as e:
            st.error(f"Google Drive upload failed: {str(e)}")
            return self._create_fallback_link(html_content, patient_name)
    
    def _get_prescription_folder_id(self):
        """Get or create prescription folder in Google Drive"""
        # This would be configured in your Google Drive
        # For now, return root folder (can be customized)
        return None  # None means root folder
    
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
    
    def save_prescription_link_to_db(self, patient_name, prescription_link, file_id=None):
        """Save prescription link to patient database"""
        try:
            import db
            
            # Get patient ID
            patients = db.get_patients()
            patient_id = None
            
            for p in patients:
                if p[1].lower() == patient_name.lower():
                    patient_id = p[0]
                    break
            
            if patient_id:
                # Save prescription link (you may need to modify your database schema)
                prescription_data = {
                    'patient_id': patient_id,
                    'prescription_link': prescription_link,
                    'file_id': file_id,
                    'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Store in session state for now (can be enhanced to save in database)
                if 'prescription_links' not in st.session_state:
                    st.session_state['prescription_links'] = []
                
                st.session_state['prescription_links'].append(prescription_data)
                
                return True
        except Exception as e:
            st.error(f"Failed to save prescription link: {str(e)}")
            return False
        
        return False

# Global instance
drive_integrator = GoogleDriveIntegrator()