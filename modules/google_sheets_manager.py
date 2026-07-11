#!/usr/bin/env python3
"""
Google Sheets Manager for MauEyeCare Hospital System
Manages inventory, patient data, and analytics via Google Sheets
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
import json

class GoogleSheetsManager:
    def __init__(self, sheet_id="1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ"):
        self.sheet_id = sheet_id
        self.base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
    
    def read_sheet(self, sheet_name):
        """Read data from Google Sheet"""
        try:
            url = f"{self.base_url}{sheet_name}"
            df = pd.read_csv(url)
            return df
        except Exception as e:
            st.error(f"Error reading {sheet_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_medicines(self):
        """Get medicine inventory from Google Sheets"""
        df = self.read_sheet("Medicines")
        if not df.empty:
            return df.to_dict('records')
        return []
    
    def get_spectacles(self):
        """Get spectacle inventory from Google Sheets"""
        df = self.read_sheet("Spectacles")
        if not df.empty:
            return df.to_dict('records')
        return []
    
    def get_patients(self):
        """Get patient data from Google Sheets"""
        df = self.read_sheet("Patients")
        if not df.empty:
            return df.to_dict('records')
        return []
    
    def get_prescriptions(self):
        """Get prescription data from Google Sheets"""
        df = self.read_sheet("Prescriptions")
        if not df.empty:
            return df.to_dict('records')
        return []
    
    def get_analytics_data(self):
        """Get analytics data from Google Sheets"""
        df = self.read_sheet("Analytics")
        if not df.empty:
            return df.to_dict('records')
        return []
    
    def add_patient_record(self, patient_data):
        """Add patient record to session state for batch upload"""
        if 'pending_patients' not in st.session_state:
            st.session_state['pending_patients'] = []
        
        # Add timestamp
        patient_data['registration_date'] = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M:%S')
        patient_data['patient_id'] = f"P{len(st.session_state['pending_patients']) + 1:04d}"
        
        st.session_state['pending_patients'].append(patient_data)
    
    def add_prescription_record(self, prescription_data):
        """Add prescription record to session state"""
        if 'pending_prescriptions' not in st.session_state:
            st.session_state['pending_prescriptions'] = []
        
        prescription_data['prescription_id'] = f"RX{len(st.session_state['pending_prescriptions']) + 1:04d}"
        prescription_data['date_created'] = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M:%S')
        
        st.session_state['pending_prescriptions'].append(prescription_data)
    
    def add_analytics_record(self, analytics_data):
        """Add analytics record to session state"""
        if 'pending_analytics' not in st.session_state:
            st.session_state['pending_analytics'] = []
        
        analytics_data['record_date'] = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M:%S')
        
        st.session_state['pending_analytics'].append(analytics_data)
    
    def show_sheet_instructions(self):
        """Show instructions for Google Sheets setup"""
        st.markdown("""
        ### 📊 Google Sheets Integration Setup
        
        **Sheet ID:** `1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ`
        
        **Required Sheets:**
        1. **Medicines** - Medicine inventory management
        2. **Spectacles** - Spectacle inventory management  
        3. **Patients** - Patient registration data
        4. **Prescriptions** - Prescription records
        5. **Analytics** - Hospital analytics data
        
        **Setup Instructions:**
        1. Copy the Google Sheet template
        2. Make it publicly viewable (Anyone with link can view)
        3. Create the required sheets with proper headers
        4. Use the sheet for real-time inventory and patient management
        
        **Benefits:**
        - Real-time inventory updates
        - Professional patient database
        - Marketing analytics
        - Multi-user access
        - Cloud backup
        """)

# Initialize global sheets manager
sheets_manager = GoogleSheetsManager()