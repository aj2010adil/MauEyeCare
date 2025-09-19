#!/usr/bin/env python3
"""
Patient Manager for MauEyeCare
Handles patient registration, duplicate prevention, and visit tracking
"""

import streamlit as st
from datetime import datetime
from .oauth_sheets_api import oauth_sheets_api

class PatientManager:
    def __init__(self):
        self.oauth_api = oauth_sheets_api
    
    def register_patient(self, patient_data):
        """Register patient with duplicate check and visit tracking"""
        try:
            if self.oauth_api.is_authenticated():
                # Use OAuth API for real-time sync
                result = self.oauth_api.add_patient(patient_data)
                
                if result['success']:
                    # Store in session for immediate use
                    st.session_state.update({
                        'patient_id': result['patient_id'],
                        'patient_name': patient_data['name'],
                        'patient_mobile': patient_data.get('mobile', ''),
                        'patient_visits': result['visits'],
                        'is_new_patient': result['new_patient']
                    })
                    
                    # Clear form and prepare for next patient
                    self.clear_patient_form()
                    
                    return {
                        'success': True,
                        'message': f"{'New patient registered' if result['new_patient'] else 'Return visit recorded'} - Visit #{result['visits']}",
                        'patient_id': result['patient_id'],
                        'visits': result['visits'],
                        'new_patient': result['new_patient']
                    }
                else:
                    return {'success': False, 'error': result['error']}
            else:
                # Fallback to local storage
                return self.register_patient_locally(patient_data)
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def register_patient_locally(self, patient_data):
        """Register patient locally when OAuth not available"""
        # Check for duplicates in local storage
        pending_patients = st.session_state.get('pending_patients', [])
        
        for patient in pending_patients:
            if (patient.get('name', '').lower() == patient_data.get('name', '').lower() and 
                patient.get('mobile', '') == patient_data.get('mobile', '')):
                # Update visit count
                patient['visits'] = patient.get('visits', 1) + 1
                patient['last_visit'] = datetime.now().isoformat()
                
                st.session_state.update({
                    'patient_id': patient.get('id', len(pending_patients)),
                    'patient_name': patient_data['name'],
                    'patient_mobile': patient_data.get('mobile', ''),
                    'patient_visits': patient['visits'],
                    'is_new_patient': False
                })
                
                return {
                    'success': True,
                    'message': f"Return visit recorded - Visit #{patient['visits']}",
                    'patient_id': patient.get('id'),
                    'visits': patient['visits'],
                    'new_patient': False
                }
        
        # Add new patient
        patient_id = len(pending_patients) + 1
        patient_data.update({
            'id': patient_id,
            'visits': 1,
            'registration_date': datetime.now().isoformat(),
            'last_visit': datetime.now().isoformat()
        })
        
        pending_patients.append(patient_data)
        st.session_state['pending_patients'] = pending_patients
        
        st.session_state.update({
            'patient_id': patient_id,
            'patient_name': patient_data['name'],
            'patient_mobile': patient_data.get('mobile', ''),
            'patient_visits': 1,
            'is_new_patient': True
        })
        
        return {
            'success': True,
            'message': "New patient registered locally",
            'patient_id': patient_id,
            'visits': 1,
            'new_patient': True
        }
    
    def clear_patient_form(self):
        """Clear patient form for next patient"""
        form_keys = [
            'first_name', 'last_name', 'age', 'gender', 'contact', 'email',
            'address', 'city', 'state', 'pincode', 'patient_issue', 'advice',
            'occupation', 'screen_time', 'family_history', 'diabetes',
            'hypertension', 'last_eye_exam', 'current_glasses', 'eye_strain',
            'referral_source', 'selected_spectacles', 'selected_medicines',
            'medicine_details'
        ]
        
        for key in form_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_patient_summary(self):
        """Get current patient summary"""
        if 'patient_name' in st.session_state:
            return {
                'name': st.session_state.get('patient_name'),
                'id': st.session_state.get('patient_id'),
                'visits': st.session_state.get('patient_visits', 1),
                'is_new': st.session_state.get('is_new_patient', True),
                'mobile': st.session_state.get('patient_mobile', '')
            }
        return None
    
    def complete_patient_process(self):
        """Complete current patient process and prepare for next"""
        # Save any pending prescription data
        if 'selected_spectacles' in st.session_state or 'medicine_details' in st.session_state:
            prescription_data = {
                'patient_id': st.session_state.get('patient_id'),
                'patient_name': st.session_state.get('patient_name'),
                'patient_mobile': st.session_state.get('patient_mobile'),
                'spectacles': st.session_state.get('selected_spectacles', []),
                'medicines': st.session_state.get('medicine_details', {}),
                'rx_table': st.session_state.get('rx_table', {}),
                'total_cost': sum([details.get('total_cost', 0) for details in st.session_state.get('medicine_details', {}).values()])
            }
            
            if self.oauth_api.is_authenticated():
                self.oauth_api.add_prescription(prescription_data)
        
        # Clear all patient-related session data
        patient_keys = [
            'patient_id', 'patient_name', 'patient_mobile', 'patient_visits',
            'is_new_patient', 'age', 'gender', 'advice', 'patient_issue',
            'rx_table', 'selected_spectacles', 'selected_medicines', 'medicine_details'
        ]
        
        for key in patient_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        return True

# Global instance
patient_manager = PatientManager()