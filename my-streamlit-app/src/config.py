#!/usr/bin/env python
"""
Secure configuration loader for MauEyeCare
"""
import os
from pathlib import Path

def load_config():
    """Load configuration from environment variables or .env file"""
    config = {}
    
    # Try to load from .env file
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    
    # Override with environment variables if they exist
    config['GROK_API_KEY'] = os.getenv('GROK_API_KEY', config.get('GROK_API_KEY'))
    config['WHATSAPP_ACCESS_TOKEN'] = os.getenv('WHATSAPP_ACCESS_TOKEN', config.get('WHATSAPP_ACCESS_TOKEN'))
    config['WHATSAPP_PHONE_NUMBER_ID'] = os.getenv('WHATSAPP_PHONE_NUMBER_ID', config.get('WHATSAPP_PHONE_NUMBER_ID'))
    config['DOCTOR_PHONE'] = os.getenv('DOCTOR_PHONE', config.get('DOCTOR_PHONE', '92356-47410'))
    
    return config

# Load configuration
CONFIG = load_config()