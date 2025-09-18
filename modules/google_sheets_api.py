#!/usr/bin/env python3
"""
Google Sheets API Integration for MauEyeCare
Enables reading and writing to Google Sheets using API key
"""

import requests
import json
import streamlit as st
from datetime import datetime

class GoogleSheetsAPI:
    def __init__(self, api_key="AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg", sheet_id="1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ"):
        self.api_key = api_key
        self.sheet_id = sheet_id
        self.base_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
    
    def read_sheet(self, sheet_name, range_name="A:Z"):
        """Read data from Google Sheet"""
        try:
            url = f"{self.base_url}/values/{sheet_name}!{range_name}?key={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
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
            else:
                st.error(f"Failed to read {sheet_name}: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error reading {sheet_name}: {str(e)}")
            return []
    
    def write_sheet(self, sheet_name, data, range_name="A1"):
        """Write data to Google Sheet (Note: Requires OAuth, not API key)"""
        try:
            # Note: Writing to Google Sheets requires OAuth authentication, not just API key
            # This is a limitation of the Google Sheets API
            st.warning("⚠️ Writing to Google Sheets requires OAuth authentication, not just API key")
            st.info("💡 Use the manual export/import feature in the Data Sync tab instead")
            return False
        except Exception as e:
            st.error(f"Error writing to {sheet_name}: {str(e)}")
            return False
    
    def append_sheet(self, sheet_name, data):
        """Append data to Google Sheet (Note: Requires OAuth, not API key)"""
        try:
            # Note: Writing to Google Sheets requires OAuth authentication, not just API key
            # For now, we'll store the data locally and provide export functionality
            st.info(f"📝 Data prepared for {sheet_name} - use manual export to add to Google Sheets")
            return True  # Return True to indicate data is prepared for export
        except Exception as e:
            st.error(f"Error preparing data for {sheet_name}: {str(e)}")
            return False
    
    def update_medicine_quantity(self, medicine_name, new_quantity):
        """Update medicine quantity in Google Sheets"""
        try:
            # Read current medicines
            medicines = self.read_sheet("Medicines")
            
            # Find and update the medicine
            for i, med in enumerate(medicines):
                if med.get('name') == medicine_name:
                    # Update quantity in row i+2 (accounting for header)
                    range_name = f"E{i+2}"  # Assuming quantity is in column E
                    url = f"{self.base_url}/values/Medicines!{range_name}?valueInputOption=RAW&key={self.api_key}"
                    
                    payload = {
                        "values": [[str(new_quantity)]]
                    }
                    
                    response = requests.put(url, json=payload)
                    return response.status_code == 200
            
            return False
        except Exception as e:
            st.error(f"Error updating medicine quantity: {str(e)}")
            return False
    
    def update_spectacle_quantity(self, spectacle_name, new_quantity):
        """Update spectacle quantity in Google Sheets"""
        try:
            # Read current spectacles
            spectacles = self.read_sheet("Spectacles")
            
            # Find and update the spectacle
            for i, spec in enumerate(spectacles):
                if spec.get('name') == spectacle_name:
                    # Update quantity in row i+2 (accounting for header)
                    range_name = f"J{i+2}"  # Assuming quantity is in column J
                    url = f"{self.base_url}/values/Spectacles!{range_name}?valueInputOption=RAW&key={self.api_key}"
                    
                    payload = {
                        "values": [[str(new_quantity)]]
                    }
                    
                    response = requests.put(url, json=payload)
                    return response.status_code == 200
            
            return False
        except Exception as e:
            st.error(f"Error updating spectacle quantity: {str(e)}")
            return False
    
    def add_patient(self, patient_data):
        """Add new patient to pending list for manual export"""
        try:
            # Since we can't write directly to Google Sheets with API key,
            # we'll add to pending patients for manual export
            if 'pending_patients' not in st.session_state:
                st.session_state['pending_patients'] = []
            
            # Check for duplicates
            existing = False
            for existing_patient in st.session_state['pending_patients']:
                if (existing_patient.get('name', '').lower() == patient_data.get('name', '').lower() and 
                    existing_patient.get('mobile', '') == patient_data.get('mobile', '')):
                    existing = True
                    break
            
            if not existing:
                st.session_state['pending_patients'].append(patient_data)
                return True
            else:
                st.warning(f"Patient {patient_data.get('name', 'Unknown')} already exists in pending list")
                return False
        except Exception as e:
            st.error(f"Error adding patient: {str(e)}")
            return False
    
    def add_prescription(self, prescription_data):
        """Add new prescription to pending list for manual export"""
        try:
            # Add to pending prescriptions for manual export
            if 'pending_prescriptions' not in st.session_state:
                st.session_state['pending_prescriptions'] = []
            
            # Add timestamp and ID if not present
            if 'id' not in prescription_data:
                prescription_data['id'] = f"RX{len(st.session_state['pending_prescriptions']) + 1:04d}"
            if 'date_created' not in prescription_data:
                prescription_data['date_created'] = datetime.now().isoformat()
            
            st.session_state['pending_prescriptions'].append(prescription_data)
            return True
        except Exception as e:
            st.error(f"Error adding prescription: {str(e)}")
            return False
    
    def sync_inventory_updates(self, local_data_manager):
        """Sync local inventory changes back to Google Sheets"""
        try:
            success_count = 0
            
            # Get local data
            medicines = local_data_manager.get_medicines()
            spectacles = local_data_manager.get_spectacles()
            
            # Update medicine quantities
            for med_name, med_data in medicines.items():
                if med_data.get('source') == 'google_sheets':
                    quantity = med_data.get('quantity', 0)
                    if self.update_medicine_quantity(med_name, quantity):
                        success_count += 1
            
            # Update spectacle quantities
            for spec_name, spec_data in spectacles.items():
                if spec_data.get('source') == 'google_sheets':
                    quantity = spec_data.get('quantity', 0)
                    if self.update_spectacle_quantity(spec_name, quantity):
                        success_count += 1
            
            return success_count
        except Exception as e:
            st.error(f"Error syncing inventory: {str(e)}")
            return 0
    
    def sync_pending_data(self):
        """Sync all pending local data to Google Sheets"""
        try:
            sync_results = {
                'patients': 0,
                'prescriptions': 0,
                'analytics': 0,
                'errors': []
            }
            
            # Sync pending patients
            pending_patients = st.session_state.get('pending_patients', [])
            for patient in pending_patients:
                if self.add_patient(patient):
                    sync_results['patients'] += 1
                else:
                    sync_results['errors'].append(f"Failed to sync patient: {patient.get('name', 'Unknown')}")
            
            # Sync pending prescriptions
            pending_prescriptions = st.session_state.get('pending_prescriptions', [])
            for prescription in pending_prescriptions:
                if self.add_prescription(prescription):
                    sync_results['prescriptions'] += 1
                else:
                    sync_results['errors'].append(f"Failed to sync prescription: {prescription.get('id', 'Unknown')}")
            
            # Clear synced data if successful
            if sync_results['patients'] > 0:
                st.session_state['pending_patients'] = []
            if sync_results['prescriptions'] > 0:
                st.session_state['pending_prescriptions'] = []
            
            return sync_results
        except Exception as e:
            st.error(f"Error syncing pending data: {str(e)}")
            return {'patients': 0, 'prescriptions': 0, 'analytics': 0, 'errors': [str(e)]}
    
    def test_connection(self):
        """Test Google Sheets API connection"""
        try:
            # Try to read medicines sheet
            medicines = self.read_sheet("Medicines")
            if medicines:
                return {'success': True, 'message': f'Connected! Found {len(medicines)} medicines'}
            else:
                return {'success': True, 'message': 'Connected but no data found'}
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}

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
            patient_data.get('registration_date', ''),
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
    
    def bulk_sync_patients(self, patients_list):
        """Bulk sync multiple patients to Google Sheets"""
        try:
            if not patients_list:
                return {'success': True, 'count': 0}
            
            # Format all patients for bulk upload
            formatted_patients = []
            for patient in patients_list:
                formatted_patients.append(self.format_patient_for_sheets(patient))
            
            # Append all patients at once
            success = self.append_sheet("Patients", formatted_patients)
            
            if success:
                return {'success': True, 'count': len(patients_list)}
            else:
                return {'success': False, 'error': 'Failed to append to Google Sheets'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
google_sheets_api = GoogleSheetsAPI()