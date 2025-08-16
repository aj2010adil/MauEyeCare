# Perplexity API Configuration
# SECURITY: API keys moved to Streamlit secrets for public repository safety

import streamlit as st
import os

def get_perplexity_api_key():
    """Get Perplexity API key from secure sources"""
    try:
        # Primary: Streamlit secrets
        if hasattr(st, 'secrets') and 'PERPLEXITY_API_KEY' in st.secrets:
            return st.secrets['PERPLEXITY_API_KEY']
        
        # Fallback: Environment variable
        return os.getenv('PERPLEXITY_API_KEY')
    except:
        return None

def get_grok_api_key():
    """Get Grok API key from secure sources"""
    try:
        # Primary: Streamlit secrets
        if hasattr(st, 'secrets') and 'GROK_API_KEY' in st.secrets:
            return st.secrets['GROK_API_KEY']
        
        # Fallback: Environment variable
        return os.getenv('GROK_API_KEY')
    except:
        return None

def get_ngrok_auth_token():
    """Get Ngrok auth token from secure sources"""
    try:
        # Primary: Streamlit secrets
        if hasattr(st, 'secrets') and 'NGROK_AUTH_TOKEN' in st.secrets:
            return st.secrets['NGROK_AUTH_TOKEN']
        
        # Fallback: Environment variable
        return os.getenv('NGROK_AUTH_TOKEN')
    except:
        return None

# Legacy support (deprecated - use functions above)
grok_key = get_grok_api_key()
YOUR_AUTHTOKEN = get_ngrok_auth_token()