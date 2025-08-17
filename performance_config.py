#!/usr/bin/env python3
"""
Performance Configuration for MauEyeCare
Optimizes loading and caching
"""

import streamlit as st

# Configure Streamlit for better performance
def configure_performance():
    """Configure Streamlit for optimal performance"""
    
    # Set page config for better performance
    if not hasattr(st, '_is_running_with_streamlit'):
        return
    
    # Enable caching
    st.set_page_config(
        page_title="MauEyeCare",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Cache configuration
CACHE_CONFIG = {
    'ttl': 3600,  # 1 hour cache
    'max_entries': 100,
    'show_spinner': False
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'lazy_loading': True,
    'limit_gallery_items': 20,  # Show only 20 items per gallery for speed
    'limit_database_load': 50,  # Load only 50 items initially
    'enable_image_caching': True,
    'compress_images': True
}