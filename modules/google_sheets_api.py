#!/usr/bin/env python3
"""
Google Sheets API Integration for MauEyeCare
Enables reading and writing to Google Sheets using a Service Account
"""

import os
import json
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsAPI:
    def __init__(self, sheet_id="1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ"):
        self.sheet_id = sheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        self.service = self._authenticate()
        
    def _authenticate(self):
        """Authenticate using Service Account"""
        try:
            # First try Streamlit secrets
            try:
                if "gcp_service_account" in st.secrets:
                    creds_info = dict(st.secrets["gcp_service_account"])
                    creds = Credentials.from_service_account_info(
                        creds_info, 
                        scopes=self.scopes
                    )
                    return build('sheets', 'v4', credentials=creds, cache_discovery=False)
            except Exception:
                pass
            
            # Fallback to local credentials.json
            if os.path.exists(self.credentials_path):
                creds = Credentials.from_service_account_file(self.credentials_path, scopes=self.scopes)
                return build('sheets', 'v4', credentials=creds, cache_discovery=False)
            
            st.error("Service Account credentials not found in secrets or credentials.json!")
            return None
        except Exception as e:
            st.error(f"Failed to authenticate with Google Sheets: {str(e)}")
            return None

    def read_sheet(self, sheet_name, range_name="A:Z"):
        """Read data from Google Sheet"""
        if not self.service:
            return []
            
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.sheet_id, range=f"{sheet_name}!{range_name}").execute()
            values = result.get('values', [])
            
            if not values:
                return []
                
            # Convert to list of dictionaries
            headers = values[0]
            rows = []
            for row in values[1:]:
                # Pad row to match headers length
                while len(row) < len(headers):
                    row.append('')
                row_dict = dict(zip(headers, row))
                rows.append(row_dict)
            return rows
            
        except Exception as e:
            st.error(f"Error reading {sheet_name}: {str(e)}")
            return []
            
    def write_sheet(self, sheet_name, data, range_name="A1"):
        """Write exact data to Google Sheet starting at range"""
        if not self.service:
            return False
            
        try:
            sheet = self.service.spreadsheets()
            body = {'values': data}
            result = sheet.values().update(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!{range_name}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            return True
        except Exception as e:
            st.error(f"Error writing to {sheet_name}: {str(e)}")
            return False
            
    def append_sheet(self, sheet_name, data):
        """Append rows to Google Sheet"""
        if not self.service:
            return False
            
        try:
            sheet = self.service.spreadsheets()
            body = {'values': data}
            result = sheet.values().append(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A:A",
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return True
        except Exception as e:
            st.error(f"Error appending to {sheet_name}: {str(e)}")
            return False
            
    def update_medicine_quantity(self, medicine_name, new_quantity):
        """Update medicine quantity in Google Sheets"""
        try:
            medicines = self.read_sheet("Medicines")
            for i, med in enumerate(medicines):
                if med.get('name') == medicine_name:
                    range_name = f"E{i+2}" # Assuming quantity is in column E
                    return self.write_sheet("Medicines", [[str(new_quantity)]], range_name)
            return False
        except Exception as e:
            st.error(f"Error updating medicine quantity: {str(e)}")
            return False

    def update_spectacle_quantity(self, spectacle_name, new_quantity):
        """Update spectacle quantity in Google Sheets"""
        try:
            spectacles = self.read_sheet("Spectacles")
            for i, spec in enumerate(spectacles):
                if spec.get('name') == spectacle_name:
                    range_name = f"J{i+2}" # Assuming quantity is in column J
                    return self.write_sheet("Spectacles", [[str(new_quantity)]], range_name)
            return False
        except Exception as e:
            st.error(f"Error updating spectacle quantity: {str(e)}")
            return False
            
    def format_patient_for_sheets(self, patient_data):
        """Format patient data for Google Sheets"""
        return [
            patient_data.get('id', ''),
            patient_data.get('name', ''),
            patient_data.get('age', ''),
            patient_data.get('gender', ''),
            patient_data.get('mobile', ''),
            patient_data.get('email', ''),
            patient_data.get('address', ''),
            patient_data.get('city', ''),
            patient_data.get('state', ''),
            patient_data.get('pincode', ''),
            patient_data.get('registration_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
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
            patient_data.get('referral_source', '')
        ]

    def add_patient(self, patient_data):
        """Add new patient to Google Sheets automatically"""
        try:
            # Check for duplicates first
            existing_patients = self.read_sheet("Patients")
            for existing_patient in existing_patients:
                if (existing_patient.get('name', '').lower() == patient_data.get('name', '').lower() and 
                    existing_patient.get('mobile', '') == patient_data.get('mobile', '')):
                    st.warning(f"Patient {patient_data.get('name', 'Unknown')} already exists in Sheets")
                    return False
            
            # Format and Append
            formatted_data = self.format_patient_for_sheets(patient_data)
            success = self.append_sheet("Patients", [formatted_data])
            if success:
                st.success(f"Successfully added patient {patient_data.get('name')} to Google Sheets.")
                return True
            return False
        except Exception as e:
            st.error(f"Error adding patient to Sheets: {str(e)}")
            return False
            
    def add_prescription(self, prescription_data):
        """Add new prescription to Google Sheets automatically"""
        try:
            # Add timestamp and ID if not present
            if 'id' not in prescription_data:
                prescription_data['id'] = f"RX-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            rx_row = [
                prescription_data.get('id', ''),
                prescription_data.get('patient_name', ''),
                prescription_data.get('patient_mobile', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ', '.join(prescription_data.get('spectacles', [])),
                json.dumps(prescription_data.get('medicines', {})),
                json.dumps(prescription_data.get('rx_table', {})),
                prescription_data.get('total_cost', 0)
            ]
            
            success = self.append_sheet("Prescriptions", [rx_row])
            return success
        except Exception as e:
            st.error(f"Error adding prescription to Sheets: {str(e)}")
            return False
            
    def bulk_sync_patients(self, patients_list):
        """Bulk sync multiple patients to Google Sheets"""
        try:
            if not patients_list:
                return {'success': True, 'count': 0}
                
            formatted_patients = [self.format_patient_for_sheets(patient) for patient in patients_list]
            success = self.append_sheet("Patients", formatted_patients)
            
            if success:
                return {'success': True, 'count': len(patients_list)}
            else:
                return {'success': False, 'error': 'Failed to append to Google Sheets'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def sync_inventory_updates(self, local_data_manager):
        """Sync local inventory changes back to Google Sheets"""
        try:
            success_count = 0
            
            medicines = local_data_manager.get_medicines()
            spectacles = local_data_manager.get_spectacles()
            
            for med_name, med_data in medicines.items():
                if med_data.get('source') == 'google_sheets':
                    if self.update_medicine_quantity(med_name, med_data.get('quantity', 0)):
                        success_count += 1
                        
            for spec_name, spec_data in spectacles.items():
                if spec_data.get('source') == 'google_sheets':
                    if self.update_spectacle_quantity(spec_name, spec_data.get('quantity', 0)):
                        success_count += 1
                        
            return success_count
        except Exception as e:
            st.error(f"Error syncing inventory to Sheets: {str(e)}")
            return 0
            
    def sync_pending_data(self):
        """Sync all pending local data to Google Sheets (Now redundant but kept for backward compatibility)"""
        try:
            sync_results = {'patients': 0, 'prescriptions': 0, 'analytics': 0, 'errors': []}
            
            # Sync pending patients
            pending_patients = st.session_state.get('pending_patients', [])
            synced_patients = []
            for patient in pending_patients:
                if self.add_patient(patient):
                    sync_results['patients'] += 1
                    synced_patients.append(patient)
                else:
                    sync_results['errors'].append(f"Failed to sync patient: {patient.get('name', 'Unknown')}")
                    
            # Sync pending prescriptions
            pending_prescriptions = st.session_state.get('pending_prescriptions', [])
            synced_prescriptions = []
            for prescription in pending_prescriptions:
                if self.add_prescription(prescription):
                    sync_results['prescriptions'] += 1
                    synced_prescriptions.append(prescription)
                else:
                    sync_results['errors'].append(f"Failed to sync prescription: {prescription.get('id', 'Unknown')}")
                    
            # Clear if successful
            st.session_state['pending_patients'] = [p for p in pending_patients if p not in synced_patients]
            st.session_state['pending_prescriptions'] = [p for p in pending_prescriptions if p not in synced_prescriptions]
                
            return sync_results
        except Exception as e:
            return {'patients': 0, 'prescriptions': 0, 'analytics': 0, 'errors': [str(e)]}
            
    def test_connection(self):
        """Test Google Sheets API connection via Service Account"""
        try:
            if not self.service:
                return {'success': False, 'message': 'Service Account authentication failed. Check credentials.json.'}
                
            medicines = self.read_sheet("Medicines")
            if medicines:
                return {'success': True, 'message': f'Authenticated & Connected! Found {len(medicines)} medicines via Service Account.'}
            else:
                return {'success': True, 'message': 'Authenticated but no data found in Medicines tab.'}
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}

# Global instance
google_sheets_api = GoogleSheetsAPI()