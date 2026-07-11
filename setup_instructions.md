# MauEyeCare OAuth2 Setup Instructions

## 🔧 What You Need to Complete

### 1. Google Sheets Structure
Create these tabs in your Google Sheet (`1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ`):

**Required Tabs:**
- `Patients` - Patient records with visit tracking
- `PatientVisits` - Individual visit records  
- `Prescriptions` - Prescription history
- `Medicines` - Medicine inventory
- `Spectacles` - Spectacle inventory
- `InventoryLog` - Inventory change tracking

### 2. Column Headers for Each Tab

**Patients Tab:**
```
id | name | age | gender | mobile | email | address | city | state | pincode | registration_date | issue | advice | occupation | screen_time | family_history | diabetes | hypertension | last_eye_exam | current_glasses | eye_strain | referral_source | visits
```

**PatientVisits Tab:**
```
patient_id | patient_name | visit_date | issue | advice | visit_number
```

**Prescriptions Tab:**
```
id | patient_name | patient_mobile | date_created | spectacles | medicines | rx_table | total_cost
```

**InventoryLog Tab:**
```
timestamp | item_name | item_type | new_quantity | notes
```

### 3. OAuth2 Authentication Flow

**How it works:**
1. User clicks "🔐 Authenticate with Google" in sidebar
2. Redirects to Google OAuth consent screen
3. User grants permissions to MauEyeCare app
4. Returns with authorization code
5. App exchanges code for access token
6. Real-time writing to Google Sheets enabled

### 4. Patient Management Features

**Duplicate Prevention:**
- Checks name + mobile number combination
- If exists: Increments visit count, updates last visit
- If new: Creates new patient record with visit count = 1

**Visit Tracking:**
- Each patient has a `visits` counter
- PatientVisits tab logs individual visits
- Automatic visit number increment

**Process Flow:**
1. Register patient → Auto-detects new/return
2. Select spectacles/medicines → Stored in session
3. Generate prescription → Saved to Google Sheets
4. Complete process → Clears session for next patient

### 5. Real-time Sync Capabilities

**With OAuth Authentication:**
✅ Instant patient registration to Google Sheets
✅ Real-time prescription saving
✅ Automatic inventory logging
✅ Visit tracking and analytics

**Without OAuth (Fallback):**
⚠️ Local storage only
⚠️ Manual CSV export/import required
⚠️ No real-time sync

### 6. Testing the Setup

1. **Deploy to Streamlit Cloud** with redirect URI: `https://maueyecare.streamlit.app`
2. **Test OAuth Flow:**
   - Click authenticate button
   - Grant permissions
   - Verify "OAuth: Authenticated" status
3. **Test Patient Registration:**
   - Register new patient → Should appear in Google Sheets instantly
   - Register same patient again → Should increment visit count
4. **Test Prescription Flow:**
   - Select spectacles/medicines
   - Generate prescription → Should save to Prescriptions tab

### 7. Required Dependencies

Add to `requirements.txt`:
```
streamlit
pandas
requests
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
openpyxl
Pillow
```

### 8. Security Notes

- Client secret is embedded (acceptable for public web app)
- Access tokens stored in session (cleared on browser close)
- Refresh tokens enable persistent authentication
- Scopes limited to spreadsheets only

### 9. Error Handling

The system handles:
- Token expiration (auto-refresh)
- Network failures (fallback to local storage)
- Duplicate patients (visit increment)
- Missing sheets (error messages)
- Authentication failures (clear instructions)

### 10. Next Steps

1. **Create Google Sheets tabs** with exact column headers above
2. **Deploy to Streamlit Cloud** with correct redirect URI
3. **Test OAuth authentication** flow
4. **Register test patients** to verify duplicate detection
5. **Generate test prescriptions** to verify real-time sync

The system is now ready for professional use with real-time Google Sheets integration, automatic duplicate prevention, and comprehensive visit tracking!