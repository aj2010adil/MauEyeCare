#!/usr/bin/env python
"""
Helper script to get WhatsApp Business API token
"""
import requests
import json

def get_meta_token_info():
    """Get information about Meta token setup"""
    print("WhatsApp Business API Token Setup")
    print("=" * 50)
    
    print("\n📋 Steps to get your token:")
    print("1. Go to: https://developers.facebook.com")
    print("2. Create/Login to Meta Business account")
    print("3. Create new app → Business → WhatsApp")
    print("4. Go to WhatsApp → Getting Started")
    print("5. Copy the Access Token and Phone Number ID")
    
    print("\n🔑 What you need:")
    print("- Access Token (starts with EAA...)")
    print("- Phone Number ID (long number)")
    print("- Verified business phone number")
    
    print("\n⚠️  Important Notes:")
    print("- Temporary tokens expire in 24 hours")
    print("- For production, create permanent token")
    print("- Phone number must be verified")
    print("- Business verification may be required")
    
    print("\n🧪 For Testing:")
    print("- Use Meta's test phone numbers")
    print("- Send to your own verified number")
    print("- Check webhook configuration")

def validate_token(access_token, phone_number_id):
    """Validate WhatsApp token"""
    if not access_token or not phone_number_id:
        return {"valid": False, "error": "Missing credentials"}
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "valid": True, 
                "phone": data.get("display_phone_number", "Unknown"),
                "status": data.get("status", "Unknown")
            }
        else:
            return {
                "valid": False, 
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {"valid": False, "error": str(e)}

if __name__ == "__main__":
    get_meta_token_info()
    
    print("\n" + "=" * 50)
    print("💡 Quick Test:")
    
    # Test current config
    try:
        import perplexity_config
        token = getattr(perplexity_config, 'WHATSAPP_ACCESS_TOKEN', '')
        phone_id = getattr(perplexity_config, 'WHATSAPP_PHONE_NUMBER_ID', '')
        
        if token and phone_id:
            print(f"Testing token: {token[:10]}...")
            result = validate_token(token, phone_id)
            
            if result["valid"]:
                print(f"✅ Token is valid!")
                print(f"📞 Phone: {result['phone']}")
                print(f"📊 Status: {result['status']}")
            else:
                print(f"❌ Token invalid: {result['error']}")
        else:
            print("❌ No credentials found in config")
            
    except ImportError:
        print("❌ Config file not found")
    
    print("\n🔗 Useful Links:")
    print("- Meta Business: https://business.facebook.com")
    print("- Developers: https://developers.facebook.com")
    print("- WhatsApp API Docs: https://developers.facebook.com/docs/whatsapp")