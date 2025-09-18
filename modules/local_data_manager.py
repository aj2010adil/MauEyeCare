#!/usr/bin/env python3
"""
Local Data Manager for MauEyeCare
Handles local storage, Google Sheets sync, and comprehensive data management
"""

import json
import os
import pandas as pd
from datetime import datetime, timezone, timedelta
import streamlit as st
from io import BytesIO

class LocalDataManager:
    def __init__(self):
        self.data_dir = "local_data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_file_path(self, filename):
        """Get full path for data file"""
        return os.path.join(self.data_dir, filename)
    
    def load_json_data(self, filename, default=None):
        """Load JSON data from file"""
        if default is None:
            default = {}
        try:
            filepath = self.get_file_path(filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")
        return default
    
    def save_json_data(self, filename, data):
        """Save JSON data to file"""
        try:
            filepath = self.get_file_path(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving {filename}: {str(e)}")
            return False
    
    def sync_from_google_sheets(self, sheets_manager):
        """Sync all data from Google Sheets to local storage"""
        try:
            # Load Google Sheets data
            medicines = sheets_manager.get_medicines()
            spectacles = sheets_manager.get_spectacles()
            patients = sheets_manager.get_patients()
            prescriptions = sheets_manager.get_prescriptions()
            analytics = sheets_manager.get_analytics_data()
            
            # Convert to local format and save
            local_medicines = {}
            for med in medicines:
                if isinstance(med, dict) and 'name' in med:
                    local_medicines[med['name']] = {
                        'category': med.get('category', 'General'),
                        'type': med.get('type', 'Medicine'),
                        'price': med.get('price', 100),
                        'quantity': med.get('quantity', 0),
                        'prescription_required': med.get('prescription_required', True),
                        'indication': med.get('indication', 'As prescribed'),
                        'dosage': med.get('dosage', 'As prescribed'),
                        'source': 'google_sheets',
                        'last_updated': datetime.now().isoformat()
                    }
            
            local_spectacles = {}
            for spec in spectacles:
                if isinstance(spec, dict) and 'name' in spec:
                    local_spectacles[spec['name']] = {
                        'brand': spec.get('brand', 'Generic'),
                        'model': spec.get('model', 'Standard'),
                        'category': spec.get('category', 'Mid-Range'),
                        'price': spec.get('price', 5000),
                        'lens_price': spec.get('lens_price', 2000),
                        'material': spec.get('material', 'Plastic'),
                        'shape': spec.get('shape', 'Square'),
                        'quantity': spec.get('quantity', 0),
                        'image_path': spec.get('image_path', ''),
                        'source': 'google_sheets',
                        'last_updated': datetime.now().isoformat()
                    }
            
            # Save to local storage
            self.save_json_data('medicines.json', local_medicines)
            self.save_json_data('spectacles.json', local_spectacles)
            self.save_json_data('patients.json', patients)
            self.save_json_data('prescriptions.json', prescriptions)
            self.save_json_data('analytics.json', analytics)
            
            # Update sync timestamp
            sync_info = {
                'last_sync': datetime.now().isoformat(),
                'medicines_count': len(local_medicines),
                'spectacles_count': len(local_spectacles),
                'patients_count': len(patients),
                'status': 'success'
            }
            self.save_json_data('sync_info.json', sync_info)
            
            return sync_info
            
        except Exception as e:
            error_info = {
                'last_sync': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
            self.save_json_data('sync_info.json', error_info)
            return error_info
    
    def get_medicines(self):
        """Get all medicines (Google Sheets + local)"""
        return self.load_json_data('medicines.json', {})
    
    def get_spectacles(self):
        """Get all spectacles (Google Sheets + local)"""
        return self.load_json_data('spectacles.json', {})
    
    def get_patients(self):
        """Get all patients"""
        google_patients = self.load_json_data('patients.json', [])
        local_patients = st.session_state.get('pending_patients', [])
        
        # Merge and deduplicate
        all_patients = []
        seen = set()
        
        # Add Google Sheets patients
        for patient in google_patients:
            if isinstance(patient, dict):
                key = f"{patient.get('name', '').lower()}_{patient.get('mobile', '')}"
                if key not in seen:
                    all_patients.append(patient)
                    seen.add(key)
        
        # Add local patients
        for patient in local_patients:
            key = f"{patient.get('name', '').lower()}_{patient.get('mobile', '')}"
            if key not in seen:
                all_patients.append(patient)
                seen.add(key)
        
        return all_patients
    
    def update_medicine_quantity(self, medicine_name, quantity_used):
        """Update medicine quantity after usage"""
        medicines = self.get_medicines()
        if medicine_name in medicines:
            current_qty = medicines[medicine_name].get('quantity', 0)
            new_qty = max(0, current_qty - quantity_used)
            medicines[medicine_name]['quantity'] = new_qty
            medicines[medicine_name]['last_updated'] = datetime.now().isoformat()
            self.save_json_data('medicines.json', medicines)
            return new_qty
        return 0
    
    def update_spectacle_quantity(self, spectacle_name, quantity_used):
        """Update spectacle quantity after usage"""
        spectacles = self.get_spectacles()
        if spectacle_name in spectacles:
            current_qty = spectacles[spectacle_name].get('quantity', 0)
            new_qty = max(0, current_qty - quantity_used)
            spectacles[spectacle_name]['quantity'] = new_qty
            spectacles[spectacle_name]['last_updated'] = datetime.now().isoformat()
            self.save_json_data('spectacles.json', spectacles)
            return new_qty
        return 0
    
    def add_prescription(self, prescription_data):
        """Add new prescription"""
        prescriptions = self.load_json_data('prescriptions.json', [])
        prescription_data['id'] = len(prescriptions) + 1
        prescription_data['date_created'] = datetime.now().isoformat()
        prescriptions.append(prescription_data)
        self.save_json_data('prescriptions.json', prescriptions)
        return prescription_data['id']
    
    def get_low_stock_items(self, threshold=5):
        """Get items with low stock"""
        low_stock = []
        
        # Check medicines
        medicines = self.get_medicines()
        for name, data in medicines.items():
            qty = data.get('quantity', 0)
            if qty <= threshold:
                low_stock.append({
                    'name': name,
                    'type': 'Medicine',
                    'quantity': qty,
                    'category': data.get('category', 'General')
                })
        
        # Check spectacles
        spectacles = self.get_spectacles()
        for name, data in spectacles.items():
            qty = data.get('quantity', 0)
            if qty <= threshold:
                low_stock.append({
                    'name': name,
                    'type': 'Spectacle',
                    'quantity': qty,
                    'brand': data.get('brand', 'Generic')
                })
        
        return low_stock
    
    def export_complete_excel(self):
        """Export complete hospital data to Excel"""
        try:
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Medicines sheet
                medicines = self.get_medicines()
                if medicines:
                    med_data = []
                    for name, data in medicines.items():
                        med_data.append({
                            'Name': name,
                            'Category': data.get('category', 'General'),
                            'Type': data.get('type', 'Medicine'),
                            'Price': data.get('price', 100),
                            'Quantity': data.get('quantity', 0),
                            'Prescription Required': data.get('prescription_required', True),
                            'Indication': data.get('indication', 'As prescribed'),
                            'Dosage': data.get('dosage', 'As prescribed'),
                            'Source': data.get('source', 'local'),
                            'Last Updated': data.get('last_updated', ''),
                            'Status': 'OUT' if data.get('quantity', 0) == 0 else 'LOW' if data.get('quantity', 0) < 5 else 'OK'
                        })
                    pd.DataFrame(med_data).to_excel(writer, sheet_name='Medicines', index=False)
                
                # Spectacles sheet
                spectacles = self.get_spectacles()
                if spectacles:
                    spec_data = []
                    for name, data in spectacles.items():
                        spec_data.append({
                            'Name': name,
                            'Brand': data.get('brand', 'Generic'),
                            'Model': data.get('model', 'Standard'),
                            'Category': data.get('category', 'Mid-Range'),
                            'Frame Price': data.get('price', 5000),
                            'Lens Price': data.get('lens_price', 2000),
                            'Total Price': data.get('price', 5000) + data.get('lens_price', 2000),
                            'Material': data.get('material', 'Plastic'),
                            'Shape': data.get('shape', 'Square'),
                            'Quantity': data.get('quantity', 0),
                            'Image Path': data.get('image_path', ''),
                            'Source': data.get('source', 'local'),
                            'Last Updated': data.get('last_updated', ''),
                            'Status': 'OUT' if data.get('quantity', 0) == 0 else 'LOW' if data.get('quantity', 0) < 5 else 'OK'
                        })
                    pd.DataFrame(spec_data).to_excel(writer, sheet_name='Spectacles', index=False)
                
                # Patients sheet
                patients = self.get_patients()
                if patients:
                    patient_data = []
                    for patient in patients:
                        if isinstance(patient, dict):
                            patient_data.append({
                                'ID': patient.get('id', ''),
                                'Name': patient.get('name', ''),
                                'Age': patient.get('age', ''),
                                'Gender': patient.get('gender', ''),
                                'Mobile': patient.get('mobile', ''),
                                'Email': patient.get('email', ''),
                                'Address': patient.get('address', ''),
                                'City': patient.get('city', ''),
                                'State': patient.get('state', ''),
                                'Pincode': patient.get('pincode', ''),
                                'Registration Date': patient.get('registration_date', ''),
                                'Issue': patient.get('issue', ''),
                                'Advice': patient.get('advice', ''),
                                'Occupation': patient.get('occupation', ''),
                                'Screen Time': patient.get('screen_time', ''),
                                'Family History': patient.get('family_history', ''),
                                'Diabetes': patient.get('diabetes', ''),
                                'Hypertension': patient.get('hypertension', ''),
                                'Last Eye Exam': patient.get('last_eye_exam', ''),
                                'Current Glasses': patient.get('current_glasses', ''),
                                'Eye Strain': patient.get('eye_strain', ''),
                                'Referral Source': patient.get('referral_source', '')
                            })
                    pd.DataFrame(patient_data).to_excel(writer, sheet_name='Patients', index=False)
                
                # Prescriptions sheet
                prescriptions = self.load_json_data('prescriptions.json', [])
                if prescriptions:
                    pd.DataFrame(prescriptions).to_excel(writer, sheet_name='Prescriptions', index=False)
                
                # Analytics sheet
                analytics = st.session_state.get('visit_analytics', [])
                if analytics:
                    pd.DataFrame(analytics).to_excel(writer, sheet_name='Analytics', index=False)
                
                # Low Stock Alert sheet
                low_stock = self.get_low_stock_items()
                if low_stock:
                    pd.DataFrame(low_stock).to_excel(writer, sheet_name='Low Stock Alerts', index=False)
                
                # Summary sheet
                summary_data = [{
                    'Total Medicines': len(medicines) if medicines else 0,
                    'Total Spectacles': len(spectacles) if spectacles else 0,
                    'Total Patients': len(patients) if patients else 0,
                    'Total Prescriptions': len(prescriptions) if prescriptions else 0,
                    'Low Stock Items': len(low_stock) if low_stock else 0,
                    'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Last Google Sheets Sync': self.load_json_data('sync_info.json', {}).get('last_sync', 'Never')
                }]
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            st.error(f"Excel export failed: {str(e)}")
            return None

# Global instance
local_data_manager = LocalDataManager()