#!/usr/bin/env python3
"""
Sync Manager for MauEyeCare
Handles synchronization between local data and Google Sheets
"""

import streamlit as st
from datetime import datetime, timezone, timedelta
import json
from .google_sheets_api import google_sheets_api
from .local_data_manager import local_data_manager

class SyncManager:
    def __init__(self):
        self.api = google_sheets_api
        self.local_manager = local_data_manager
    
    def test_google_sheets_connection(self):
        """Test connection to Google Sheets"""
        try:
            result = self.api.test_connection()
            return result
        except Exception as e:
            return {'success': False, 'message': f'Connection test failed: {str(e)}'}
    
    def sync_local_to_google_sheets(self):
        """Sync pending local data automatically to Google Sheets using Service Account"""
        try:
            st.info("📤 Syncing local data to Google Sheets...")
            sync_results = self.api.sync_pending_data()
            
            if sync_results.get('errors'):
                for err in sync_results['errors']:
                    st.error(f"❌ Error: {err}")
                    
            patients_synced = sync_results.get('patients', 0)
            prescriptions_synced = sync_results.get('prescriptions', 0)
            
            if patients_synced > 0 or prescriptions_synced > 0:
                st.success(f"✅ Synced {patients_synced} patients and {prescriptions_synced} prescriptions to Google Sheets!")
            else:
                st.info("📊 No pending data to sync")
                
            sync_results['success'] = len(sync_results.get('errors', [])) == 0
            
            # Update sync timestamp
            sync_info = {
                'last_sync_attempt': datetime.now().isoformat(),
                'patients_synced': patients_synced,
                'prescriptions_synced': prescriptions_synced,
                'status': 'success' if sync_results['success'] else 'partial',
                'message': 'Automated sync via Service Account completed'
            }
            self.local_manager.save_json_data('last_sync.json', sync_info)
            
            return sync_results
            
        except Exception as e:
            error_result = {
                'patients': 0,
                'prescriptions': 0,
                'errors': [str(e)],
                'success': False
            }
            st.error(f"❌ Sync to Google Sheets failed: {str(e)}")
            return error_result
    
    def sync_google_sheets_to_local(self):
        """Sync data from Google Sheets to local storage"""
        try:
            st.info("📥 Syncing data from Google Sheets to local storage...")
            
            # Use the existing sync method from local data manager
            sync_result = self.local_manager.sync_from_google_sheets(google_sheets_api)
            
            if sync_result.get('status') == 'success':
                st.success(f"✅ Synced from Google Sheets: {sync_result.get('medicines_count', 0)} medicines, {sync_result.get('spectacles_count', 0)} spectacles, {sync_result.get('patients_count', 0)} patients")
                return True
            else:
                st.error(f"❌ Sync from Google Sheets failed: {sync_result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error syncing from Google Sheets: {str(e)}")
            return False
    
    def get_sync_status(self):
        """Get current sync status"""
        try:
            sync_info = self.local_manager.load_json_data('last_sync.json', {})
            pending_patients = len(st.session_state.get('pending_patients', []))
            pending_prescriptions = len(st.session_state.get('pending_prescriptions', []))
            
            return {
                'last_sync': sync_info.get('last_sync', 'Never'),
                'pending_patients': pending_patients,
                'pending_prescriptions': pending_prescriptions,
                'last_sync_status': sync_info.get('status', 'unknown'),
                'last_sync_errors': sync_info.get('errors', [])
            }
        except Exception as e:
            return {
                'last_sync': 'Error',
                'pending_patients': 0,
                'pending_prescriptions': 0,
                'last_sync_status': 'error',
                'last_sync_errors': [str(e)]
            }
    
    def force_full_sync(self):
        """Force a complete sync (read from Sheets + prepare local data)"""
        try:
            st.info("🔄 Starting full sync...")
            
            # First, sync from Google Sheets to get latest data
            sheets_to_local = self.sync_google_sheets_to_local()
            
            # Then, sync local changes back to Google Sheets automatically
            local_to_sheets = self.sync_local_to_google_sheets()
            
            if sheets_to_local and local_to_sheets['success']:
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"❌ Full sync failed: {str(e)}")
            return False
    
    def show_sync_dashboard(self):
        """Display sync status dashboard"""
        st.subheader("🔄 Data Synchronization Dashboard")
        
        # Get sync status
        status = self.get_sync_status()
        
        # Status metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Last Sync", 
                     status['last_sync'][:10] if status['last_sync'] != 'Never' else 'Never')
        
        with col2:
            st.metric("Pending Patients", status['pending_patients'])
        
        with col3:
            st.metric("Pending Prescriptions", status['pending_prescriptions'])
        
        with col4:
            sync_status = status['last_sync_status']
            if sync_status == 'success':
                st.success("✅ Last Sync: Success")
            elif sync_status == 'partial':
                st.warning("⚠️ Last Sync: Partial")
            elif sync_status == 'error':
                st.error("❌ Last Sync: Failed")
            else:
                st.info("ℹ️ No sync history")
        
        # Sync actions
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Test Connection", use_container_width=True):
                with st.spinner("Testing Google Sheets connection..."):
                    result = self.test_google_sheets_connection()
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
        
        with col2:
            if st.button("📤 Sync to Sheets", use_container_width=True):
                with st.spinner("Syncing data to Google Sheets..."):
                    result = self.sync_local_to_google_sheets()
                    if result['success']:
                        if result.get('patients', 0) > 0 or result.get('prescriptions', 0) > 0:
                            st.success("✅ Data automatically synced to Google Sheets!")
                        else:
                            st.info("📊 No data to sync")
                    else:
                        st.error("❌ Sync to Sheets failed!")
        
        with col3:
            if st.button("📥 Sync from Sheets", use_container_width=True):
                with st.spinner("Syncing from Google Sheets to local..."):
                    success = self.sync_google_sheets_to_local()
                    if success:
                        st.success("✅ Sync from Google Sheets completed!")
                    else:
                        st.error("❌ Sync from Google Sheets failed!")
        
        with col4:
            if st.button("🔄 Full Sync", use_container_width=True):
                with st.spinner("Performing full sync (read from Sheets + prepare local data)..."):
                    success = self.force_full_sync()
                    if success:
                        st.success("✅ Full sync completed!")
                        st.info("📋 Local data updated from Google Sheets")
                        st.info("📤 Pending data automatically uploaded to Google Sheets")
        
        # Show errors if any
        if status['last_sync_errors']:
            st.markdown("---")
            st.subheader("⚠️ Last Sync Errors")
            for error in status['last_sync_errors']:
                st.error(f"• {error}")
        
        # Pending data details
        if status['pending_patients'] > 0 or status['pending_prescriptions'] > 0:
            st.markdown("---")
            st.subheader("📋 Pending Data Details")
            
            if status['pending_patients'] > 0:
                with st.expander(f"👥 {status['pending_patients']} Pending Patients"):
                    pending_patients = st.session_state.get('pending_patients', [])
                    for i, patient in enumerate(pending_patients[:5]):  # Show first 5
                        st.write(f"{i+1}. {patient.get('name', 'Unknown')} - {patient.get('mobile', 'No mobile')}")
                    if len(pending_patients) > 5:
                        st.write(f"... and {len(pending_patients) - 5} more")
            
            if status['pending_prescriptions'] > 0:
                with st.expander(f"📄 {status['pending_prescriptions']} Pending Prescriptions"):
                    pending_prescriptions = st.session_state.get('pending_prescriptions', [])
                    for i, prescription in enumerate(pending_prescriptions[:5]):  # Show first 5
                        st.write(f"{i+1}. {prescription.get('patient_name', 'Unknown')} - {prescription.get('date_created', 'No date')}")
                    if len(pending_prescriptions) > 5:
                        st.write(f"... and {len(pending_prescriptions) - 5} more")

# Global instance
sync_manager = SyncManager()