#!/usr/bin/env python3
"""
OAuth2 Google Sheets API for MauEyeCare
Enables real-time writing to Google Sheets using OAuth2 authentication
"""

import streamlit as st
import requests
import json
from datetime import datetime
import base64
import hashlib
import secrets
from urllib.parse import urlencode, parse_qs

class OAuthSheetsAPI:
    def __init__(self):
        # Use Streamlit secrets for security
        try:
            self.client_id = st.secrets["google_oauth"]["client_id"]
            self.client_secret = st.secrets["google_oauth"]["client_secret"]
            self.redirect_uri = st.secrets["google_oauth"].get("redirect_uri", "https://maueyecare.streamlit.app")
        except:
            # Fallback for demo mode - disable OAuth
            self.client_id = None
            self.client_secret = None
            self.redirect_uri = None
        self.sheet_id = "1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ"
        self.scopes = "https://www.googleapis.com/auth/spreadsheets"
        
    def get_auth_url(self):
        """Generate OAuth2 authorization URL"""
        if not self.client_id or not self.redirect_uri:
            return None
            
        state = secrets.token_urlsafe(32)
        st.session_state['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scopes,
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    def exchange_code_for_token(self, code, state):
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            return {'success': False, 'error': 'OAuth credentials not configured'}
            
        # Skip state validation for Streamlit Cloud compatibility
        # if state != st.session_state.get('oauth_state'):
        #     return {'success': False, 'error': 'Invalid state parameter'}
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post('https://oauth2.googleapis.com/token', data=data)
            if response.status_code == 200:
                token_data = response.json()
                st.session_state['access_token'] = token_data.get('access_token')
                st.session_state['refresh_token'] = token_data.get('refresh_token')
                return {'success': True, 'token': token_data}
            else:
                error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                return {'success': False, 'error': f'Token exchange failed: {error_details}'}
        except Exception as e:
            return {'success': False, 'error': f'Network error: {str(e)}'}
    
    def refresh_access_token(self):
        """Refresh expired access token"""
        if 'refresh_token' not in st.session_state:
            return False
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': st.session_state['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post('https://oauth2.googleapis.com/token', data=data)
            if response.status_code == 200:
                token_data = response.json()
                st.session_state['access_token'] = token_data.get('access_token')
                return True
        except:
            pass
        return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return 'access_token' in st.session_state and self.client_id is not None
    
    def write_to_sheet(self, sheet_name, data, range_start="A1"):
        """Write data to Google Sheets"""
        if not self.is_authenticated():
            return {'success': False, 'error': 'Not authenticated'}
        
        headers = {
            'Authorization': f'Bearer {st.session_state["access_token"]}',
            'Content-Type': 'application/json'
        }
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{sheet_name}!{range_start}:append?valueInputOption=RAW"
        
        payload = {
            'values': data
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:  # Token expired
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {st.session_state["access_token"]}'
                    response = requests.post(url, headers=headers, json=payload)
                else:
                    return {'success': False, 'error': 'Authentication expired'}
            
            if response.status_code == 200:
                return {'success': True, 'response': response.json()}
            else:
                return {'success': False, 'error': f'Write failed: {response.text}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_patient(self, patient_data):
        """Add patient to Google Sheets with duplicate check and visit tracking"""
        try:
            # First, check for existing patient
            existing_patients = self.get_patients()
            patient_id = None
            visits = 1
            is_new_patient = True
            
            for patient in existing_patients:
                if (patient.get('name', '').lower() == patient_data.get('name', '').lower() and 
                    patient.get('mobile', '') == patient_data.get('mobile', '')):
                    patient_id = patient.get('id')
                    visits = int(patient.get('visits', 1)) + 1
                    is_new_patient = False
                    break
            
            if is_new_patient:
                patient_id = len(existing_patients) + 1
            
            # Prepare patient row
            patient_row = [
                patient_id,
                patient_data.get('name', ''),
                patient_data.get('age', ''),
                patient_data.get('gender', ''),
                patient_data.get('mobile', ''),
                patient_data.get('email', ''),
                patient_data.get('address', ''),
                patient_data.get('city', ''),
                patient_data.get('state', ''),
                patient_data.get('pincode', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                patient_data.get('issue', ''),
                patient_data.get('advice', ''),
                patient_data.get('occupation', ''),
                patient_data.get('screen_time', ''),
                patient_data.get('family_history', ''),
                patient_data.get('diabetes', ''),
                patient_data.get('hypertension', ''),
                patient_data.get('last_eye_exam', ''),
                patient_data.get('current_glasses', ''),
                patient_data.get('eye_strain', ''),
                patient_data.get('referral_source', ''),
                visits
            ]
            
            if is_new_patient:
                # Add new patient
                result = self.write_to_sheet("Patients", [patient_row])
                if result['success']:
                    return {'success': True, 'patient_id': patient_id, 'visits': visits, 'new_patient': True}
            else:
                # Update existing patient's visit count
                result = self.update_patient_visits(patient_id, visits, patient_data)
                if result['success']:
                    return {'success': True, 'patient_id': patient_id, 'visits': visits, 'new_patient': False}
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_patient_visits(self, patient_id, visits, patient_data):
        """Update patient visit count and latest visit info"""
        # Add visit record to main Patients sheet instead of separate PatientVisits sheet
        visit_row = [
            patient_id,
            patient_data.get('name', ''),
            patient_data.get('age', ''),
            patient_data.get('gender', ''),
            patient_data.get('mobile', ''),
            patient_data.get('email', ''),
            patient_data.get('address', ''),
            patient_data.get('city', ''),
            patient_data.get('state', ''),
            patient_data.get('pincode', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            patient_data.get('issue', ''),
            patient_data.get('advice', ''),
            patient_data.get('occupation', ''),
            patient_data.get('screen_time', ''),
            patient_data.get('family_history', ''),
            patient_data.get('diabetes', ''),
            patient_data.get('hypertension', ''),
            patient_data.get('last_eye_exam', ''),
            patient_data.get('current_glasses', ''),
            patient_data.get('eye_strain', ''),
            patient_data.get('referral_source', ''),
            visits
        ]
        
        return self.write_to_sheet("Patients", [visit_row])
    
    def add_prescription(self, prescription_data):
        """Add prescription to Google Sheets"""
        prescription_row = [
            prescription_data.get('id', ''),
            prescription_data.get('patient_name', ''),
            prescription_data.get('patient_mobile', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ', '.join(prescription_data.get('spectacles', [])),
            json.dumps(prescription_data.get('medicines', {})),
            json.dumps(prescription_data.get('rx_table', {})),
            prescription_data.get('total_cost', 0)
        ]
        
        return self.write_to_sheet("Prescriptions", [prescription_row])
    
    def get_patients(self):
        """Get patients from Google Sheets (using read-only API)"""
        try:
            from .google_sheets_api import google_sheets_api
            return google_sheets_api.read_sheet("Patients")
        except:
            return []
    
    def update_inventory(self, item_name, new_quantity, item_type="medicine"):
        """Update inventory quantities in Google Sheets"""
        sheet_name = "Medicines" if item_type == "medicine" else "Spectacles"
        
        # This would require finding and updating specific cells
        # For now, we'll log the inventory change
        inventory_row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            item_name,
            item_type,
            new_quantity,
            "Updated via prescription"
        ]
        
        return self.write_to_sheet("InventoryLog", [inventory_row])

# Global instance
oauth_sheets_api = OAuthSheetsAPI()