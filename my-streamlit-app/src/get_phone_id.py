#!/usr/bin/env python
"""
Get correct WhatsApp Phone Number ID from Meta
"""
import requests
import perplexity_config

def get_phone_number_id():
    """Get the correct phone number ID from Meta API"""
    token = perplexity_config.WHATSAPP_ACCESS_TOKEN
    
    # Get business account info
    url = "https://graph.facebook.com/v18.0/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"App ID: {data.get('id')}")
            
            # Get phone numbers associated with this app
            phone_url = f"https://graph.facebook.com/v18.0/{data['id']}/phone_numbers"
            phone_response = requests.get(phone_url, headers=headers)
            
            if phone_response.status_code == 200:
                phone_data = phone_response.json()
                print("Available phone numbers:")
                for phone in phone_data.get('data', []):
                    print(f"- ID: {phone['id']}")
                    print(f"  Number: {phone.get('display_phone_number', 'N/A')}")
                    print(f"  Status: {phone.get('status', 'N/A')}")
                    print()
                    
                if phone_data.get('data'):
                    correct_id = phone_data['data'][0]['id']
                    print(f"Use this Phone Number ID: {correct_id}")
                    return correct_id
            else:
                print(f"Phone numbers error: {phone_response.text}")
        else:
            print(f"API Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    phone_id = get_phone_number_id()
    if phone_id:
        print(f"\nUpdate your config with:")
        print(f'META_WA_PHONE_NUMBER_ID="{phone_id}"')
    else:
        print("Could not get phone number ID")