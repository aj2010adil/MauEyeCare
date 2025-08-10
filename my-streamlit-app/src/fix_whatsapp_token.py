#!/usr/bin/env python
"""
Quick fix for WhatsApp token issue
"""

def get_new_token_instructions():
    print("WhatsApp Token Fix Instructions")
    print("=" * 40)
    print("Your current token has expired. Here's how to get a new one:")
    print()
    print("STEP 1: Go to Meta Business")
    print("- Visit: https://developers.facebook.com")
    print("- Login to your Meta account")
    print()
    print("STEP 2: Find Your App")
    print("- Go to 'My Apps'")
    print("- Select your WhatsApp Business app")
    print()
    print("STEP 3: Get New Token")
    print("- Click 'WhatsApp' in left menu")
    print("- Go to 'Getting Started'")
    print("- Copy the new 'Temporary access token'")
    print()
    print("STEP 4: Update Config")
    print("- Open: src/perplexity_config.py")
    print("- Replace WHATSAPP_ACCESS_TOKEN with new token")
    print("- Token should start with 'EAA'")
    print()
    print("STEP 5: Test")
    print("- Restart the app")
    print("- Try sending PDF via WhatsApp")
    print()
    print("Current config location:")
    print("MauEyeCare/my-streamlit-app/src/perplexity_config.py")

if __name__ == "__main__":
    get_new_token_instructions()