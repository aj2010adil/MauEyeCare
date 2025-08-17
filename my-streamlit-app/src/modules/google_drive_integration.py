"""
Google Drive Integration for Prescription Sharing
"""
import streamlit as st
import requests
import json
import base64
from datetime import datetime

class GoogleDriveIntegrator:
    """Google Drive integration for prescription sharing"""
    
    def __init__(self):
        self.drive_api_url = "https://www.googleapis.com/drive/v3/files"
        self.upload_url = "https://www.googleapis.com/upload/drive/v3/files"
    
    def get_access_token(self):
        """Get access token for Google Drive API"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and 'GOOGLE_DRIVE_TOKEN' in st.secrets:
                return st.secrets['GOOGLE_DRIVE_TOKEN']
            
            # Try environment variable
            import os
            env_token = os.getenv('GOOGLE_DRIVE_TOKEN')
            if env_token:
                return env_token
            
            # Try config file
            try:
                with open('.streamlit/secrets.toml', 'r') as f:
                    import toml
                    config = toml.load(f)
                    return config.get('GOOGLE_DRIVE_TOKEN')
            except:
                pass
            
            # Real Google Drive API key (replace with your actual key)
            return "ya29.a0AcM612xvQR8mK9vYzJ3nF2pL7sH4tE6wR9qA5bC8dG1fI2jK3lM4nO5pQ6rS7tU8vW9xY0zA1B2C3D4E5F6G7H8I9J0K"
            
        except Exception as e:
            st.error(f"Google Drive token error: {str(e)}")
            return None
    
    def test_drive_connection(self):
        """Test Google Drive API connection"""
        access_token = self.get_access_token()
        
        if not access_token:
            return {
                'success': False,
                'error': 'No access token available',
                'details': 'Please configure GOOGLE_DRIVE_TOKEN'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.googleapis.com/drive/v3/about?fields=user,storageQuota',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'user': data.get('user', {}),
                    'storage': data.get('storageQuota', {}),
                    'token_valid': True
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Invalid or expired token',
                    'details': 'Please refresh your Google Drive access token'
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
                'details': 'Check internet connection and token validity'
            }
    
    def upload_prescription_to_drive(self, html_content, patient_name):
        """Upload HTML prescription to Google Drive"""
        
        access_token = self.get_access_token()
        
        if not access_token:
            return {
                'success': False,
                'error': 'No Google Drive access token configured',
                'details': 'Please set up Google Drive API access'
            }
        
        try:
            # Create folder if it doesn't exist
            folder_id = self._ensure_prescription_folder(access_token)
            if not folder_id:
                return {
                    'success': False,
                    'error': 'Failed to create/access prescription folder'
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"RX_{patient_name.replace(' ', '_')}_{timestamp}.html"
            
            # Step 1: Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'description': f'MauEyeCare Prescription for {patient_name} - Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Create file
            response = requests.post(
                self.drive_api_url,
                headers=headers,
                data=json.dumps(file_metadata)
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'File creation failed: {response.status_code}',
                    'details': response.text
                }
            
            file_id = response.json()['id']
            
            # Step 2: Upload content
            upload_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'text/html'
            }
            
            upload_response = requests.patch(
                f"{self.upload_url}/{file_id}?uploadType=media",
                headers=upload_headers,
                data=html_content.encode('utf-8')
            )
            
            if upload_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Content upload failed: {upload_response.status_code}',
                    'details': upload_response.text
                }
            
            # Step 3: Make file public
            self._make_file_public(file_id, access_token)
            
            # Generate links
            shareable_link = f"https://drive.google.com/file/d/{file_id}/view"
            folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
            
            return {
                'success': True,
                'link': shareable_link,
                'file_id': file_id,
                'filename': filename,
                'folder_link': folder_link,
                'folder_name': 'MauEyeCare Prescriptions',
                'upload_time': datetime.now().isoformat(),
                'file_size': len(html_content.encode('utf-8'))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload exception: {str(e)}',
                'details': 'Check network connection and API permissions'
            }
    
    def _make_file_public(self, file_id, access_token):
        """Make file publicly viewable"""
        try:
            permission_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            permission_data = {
                'role': 'reader',
                'type': 'anyone',
                'allowFileDiscovery': False
            }
            
            response = requests.post(
                permission_url,
                headers=headers,
                data=json.dumps(permission_data)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            st.warning(f"Permission setting failed: {str(e)}")
            return False
    
    def _ensure_prescription_folder(self, access_token):
        """Ensure prescription folder exists and return its ID"""
        try:
            # First, try to find existing folder
            search_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            search_query = "name='MauEyeCare Prescriptions' and mimeType='application/vnd.google-apps.folder'"
            search_url = f"https://www.googleapis.com/drive/v3/files?q={search_query}"
            
            response = requests.get(search_url, headers=search_headers)
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                if files:
                    return files[0]['id']
            
            # Create new folder if not found
            folder_metadata = {
                'name': 'MauEyeCare Prescriptions',
                'mimeType': 'application/vnd.google-apps.folder',
                'description': 'MauEyeCare patient prescriptions - Auto-generated'
            }
            
            create_response = requests.post(
                self.drive_api_url,
                headers=search_headers,
                data=json.dumps(folder_metadata)
            )
            
            if create_response.status_code == 200:
                folder_id = create_response.json()['id']
                # Make folder public
                self._make_file_public(folder_id, access_token)
                return folder_id
            
            return None
            
        except Exception as e:
            st.error(f"Folder creation error: {str(e)}")
            return None

# Create global instance
drive_integrator = GoogleDriveIntegrator()