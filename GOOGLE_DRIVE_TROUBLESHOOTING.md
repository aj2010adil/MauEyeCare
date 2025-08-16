# 🔧 Google Drive Integration Troubleshooting

## 🚨 Most Likely Issues:

### 1. **API Key vs OAuth2 Issue**
- **Problem**: The provided key looks like an API key, but Google Drive file uploads typically require OAuth2
- **Solution**: Need to use OAuth2 authentication instead of simple API key

### 2. **API Key Permissions**
- **Problem**: API key might not have Google Drive API enabled
- **Solution**: Enable Google Drive API in Google Cloud Console

### 3. **Folder Permissions**
- **Problem**: The target folder might not be publicly accessible
- **Solution**: Make folder publicly accessible or use service account

## 🧪 Testing Steps:

### **Step 1: Run Local Test**
```bash
cd d:\MauEyeCare\MauEyeCare\MauEyeCare
python test_google_drive.py
```

### **Step 2: Check Results**
- ✅ All tests pass = Integration should work
- ❌ Tests fail = Follow solutions below

## 🔑 Authentication Solutions:

### **Option 1: Service Account (Recommended)**
1. Go to Google Cloud Console
2. Create Service Account
3. Download JSON key file
4. Share folder with service account email
5. Use service account authentication

### **Option 2: OAuth2 Flow**
1. Set up OAuth2 credentials
2. Implement OAuth2 flow in app
3. Get access tokens dynamically

### **Option 3: Make Folder Public**
1. Right-click folder in Google Drive
2. Share > Anyone with link can edit
3. Use simple API key for uploads

## 🛠️ Quick Fix for Testing:

### **Temporary Solution:**
```python
# Use this in google_drive_integration.py for testing
def upload_prescription_to_drive(self, html_content, patient_name):
    # For now, create a simple file download
    import tempfile
    import os
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    temp_file.write(html_content)
    temp_file.close()
    
    return {
        'success': True,
        'link': f'file://{temp_file.name}',
        'filename': f'prescription_{patient_name}.html',
        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'note': 'Temporary local file - Google Drive integration needs OAuth2'
    }
```

## 📞 Next Steps:
1. Run `test_google_drive.py` locally
2. Share the test results
3. Based on results, implement proper authentication
4. Test with actual prescription upload

## 🔍 Common Error Messages:
- **403 Forbidden**: API key lacks permissions
- **401 Unauthorized**: Authentication issue
- **404 Not Found**: Folder not accessible
- **400 Bad Request**: Invalid request format