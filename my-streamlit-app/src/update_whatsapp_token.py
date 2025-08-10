#!/usr/bin/env python
"""
Quick script to update WhatsApp token
"""

def update_token():
    print("WhatsApp Token Update Instructions")
    print("=" * 40)
    print()
    print("Your WhatsApp token has expired. Follow these steps:")
    print()
    print("1. Go to: https://developers.facebook.com")
    print("2. Login and select your WhatsApp Business app")
    print("3. Click 'WhatsApp' in the left menu")
    print("4. Go to 'Getting Started'")
    print("5. Copy the new 'Temporary access token'")
    print()
    print("6. Open: src/perplexity_config.py")
    print("7. Replace the value in this line:")
    print('   META_WA_ACCESS_TOKEN="YOUR_NEW_TOKEN_HERE"')
    print()
    print("8. Save the file and restart the app")
    print()
    print("Current config file location:")
    print("MauEyeCare/my-streamlit-app/src/perplexity_config.py")
    print()
    print("The new token should start with 'EAA' and be very long")

if __name__ == "__main__":
    update_token()