# 📱 WhatsApp Business API Setup Guide

## Step 1: Get WhatsApp Business API Access

### Option A: Meta Business (Recommended)
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a Meta Business account
3. Create a new app → Business → WhatsApp
4. Add WhatsApp product to your app

### Option B: WhatsApp Business API Providers
- **Twilio**: Easy setup, pay-per-message
- **360Dialog**: WhatsApp official partner
- **MessageBird**: Global messaging platform

## Step 2: Get Your Credentials

### From Meta Business:
1. Go to WhatsApp → Getting Started
2. Copy **Access Token** (temporary - 24 hours)
3. Copy **Phone Number ID**
4. For permanent token: Go to System Users → Create permanent token

### Required Information:
```
Access Token: EAAxxxxxxxxxx (starts with EAA)
Phone Number ID: 1234567890123456
Phone Number: +91xxxxxxxxxx
```

## Step 3: Update Configuration

Edit `src/perplexity_config.py`:
```python
# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN = "YOUR_PERMANENT_ACCESS_TOKEN"
WHATSAPP_PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"
DOCTOR_PHONE = "92356-47410"
```

## Step 4: Verify Phone Number

1. In Meta Business Manager
2. Go to WhatsApp → Phone Numbers
3. Verify your business phone number
4. Complete business verification

## Step 5: Test Integration

1. Use the test phone number provided by Meta
2. Send a test message
3. Verify delivery

## 🔧 Troubleshooting

### Common Issues:
- **Token Expired**: Get new token from Meta Business
- **Phone Not Verified**: Complete phone verification
- **Business Not Approved**: Submit business verification
- **Rate Limits**: Start with test numbers

### Error Messages:
- `Invalid OAuth access token`: Token expired/invalid
- `Phone number not registered`: Verify phone in Meta Business
- `Business not verified`: Complete business verification process

## 💡 Quick Fix for Testing

For immediate testing, you can:
1. Use Meta's test phone numbers
2. Get a 24-hour temporary token
3. Test with your own verified number

## 📞 Alternative: SMS Integration

If WhatsApp setup is complex, we can add SMS integration:
- Twilio SMS API
- AWS SNS
- Local SMS gateway

Would you like me to implement SMS as backup?