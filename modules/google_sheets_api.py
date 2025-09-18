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
        """Write data to Google Sheet"""
        try:
            url = f"{self.base_url}/values/{sheet_name}!{range_name}?valueInputOption=RAW&key={self.api_key}"
            
            payload = {
                "values": data
            }
            
            response = requests.put(url, json=payload)
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"Failed to write to {sheet_name}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            st.error(f"Error writing to {sheet_name}: {str(e)}")
            return False
    
    def append_sheet(self, sheet_name, data):
        """Append data to Google Sheet"""
        try:
            url = f"{self.base_url}/values/{sheet_name}!A:Z:append?valueInputOption=RAW&key={self.api_key}"
            
            payload = {
                "values": data
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"Failed to append to {sheet_name}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            st.error(f"Error appending to {sheet_name}: {str(e)}")
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
        """Add new patient to Google Sheets"""
        try:
            # Prepare patient row
            patient_row = [
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
            
            return self.append_sheet("Patients", [patient_row])
        except Exception as e:
            st.error(f"Error adding patient: {str(e)}")
            return False
    
    def add_prescription(self, prescription_data):
        """Add new prescription to Google Sheets"""
        try:
            # Prepare prescription row
            prescription_row = [
                prescription_data.get('id', ''),
                prescription_data.get('patient_name', ''),
                prescription_data.get('patient_mobile', ''),
                prescription_data.get('date_created', ''),
                ', '.join(prescription_data.get('spectacles', [])),
                json.dumps(prescription_data.get('medicines', {})),
                json.dumps(prescription_data.get('rx_table', {})),
                prescription_data.get('total_cost', 0)
            ]
            
            return self.append_sheet("Prescriptions", [prescription_row])
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

# Global instance
google_sheets_api = GoogleSheetsAPI()