"""
Simple Google Drive API Test Script
Run this locally to test the Google Drive integration
"""
import requests
import json

# Your API key
API_KEY = "AIzaSyDIF_ARHGjP22vWXIMzdH6m2bKowbzFODg"
FOLDER_ID = "1S5-ts47Nc_vw56YfwV-AZvXyk1VJbLLO"

def test_api_key():
    """Test if API key is valid"""
    print("🔍 Testing API Key...")
    
    try:
        # Test basic API access
        url = f"https://www.googleapis.com/drive/v3/files?key={API_KEY}"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ API Key is valid")
            return True
        else:
            print("❌ API Key issue")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_folder_access():
    """Test if we can access the specific folder"""
    print("\n📁 Testing Folder Access...")
    
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{FOLDER_ID}?key={API_KEY}"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            folder_info = response.json()
            print(f"✅ Folder accessible: {folder_info.get('name', 'Unknown')}")
            return True
        else:
            print("❌ Cannot access folder")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload_permission():
    """Test if we can upload to the folder"""
    print("\n📤 Testing Upload Permission...")
    
    try:
        # Try to create a simple text file
        file_metadata = {
            'name': 'test_file.txt',
            'parents': [FOLDER_ID]
        }
        
        url = f"https://www.googleapis.com/drive/v3/files?key={API_KEY}"
        response = requests.post(url, json=file_metadata)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload permission granted")
            return True
        else:
            print("❌ Upload permission denied")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Google Drive API Test\n")
    
    # Test 1: API Key
    api_valid = test_api_key()
    
    # Test 2: Folder Access
    folder_accessible = test_folder_access()
    
    # Test 3: Upload Permission
    upload_allowed = test_upload_permission()
    
    print("\n📊 Test Results:")
    print(f"API Key Valid: {'✅' if api_valid else '❌'}")
    print(f"Folder Accessible: {'✅' if folder_accessible else '❌'}")
    print(f"Upload Allowed: {'✅' if upload_allowed else '❌'}")
    
    if all([api_valid, folder_accessible, upload_allowed]):
        print("\n🎉 All tests passed! Google Drive should work.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
        print("\n💡 Common solutions:")
        print("1. Enable Google Drive API in Google Cloud Console")
        print("2. Make sure the folder is publicly accessible")
        print("3. Check if API key has proper permissions")
        print("4. Try using OAuth2 instead of API key")

if __name__ == "__main__":
    main()