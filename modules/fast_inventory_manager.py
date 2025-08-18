#!/usr/bin/env python3
"""
Fast Inventory Manager for MauEyeCare
Optimized for speed and simplicity
"""

import streamlit as st
import pandas as pd
from .inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
from .comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
from .comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE

def show_inventory_management_page():
    """Fast inventory management interface"""
    
    st.header("📦 Inventory Management")
    
    # Quick stats
    inventory = get_inventory_dict()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(inventory))
    with col2:
        total_stock = sum(inventory.values())
        st.metric("Total Stock", total_stock)
    with col3:
        low_stock = len([k for k, v in inventory.items() if v < 5])
        st.metric("Low Stock", low_stock, delta=f"-{low_stock}" if low_stock > 0 else "0")
    with col4:
        out_of_stock = len([k for k, v in inventory.items() if v == 0])
        st.metric("Out of Stock", out_of_stock, delta=f"-{out_of_stock}" if out_of_stock > 0 else "0")
    
    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Current Stock", "➕ Add Stock", "🔍 Search & Update", "⚠️ Alerts"])
    
    with tab1:
        st.subheader("Current Inventory")
        
        if inventory:
            # Convert to DataFrame for better display
            df = pd.DataFrame([
                {"Item": item, "Stock": stock, "Type": "Spectacle" if item in COMPREHENSIVE_SPECTACLE_DATABASE else "Medicine"}
                for item, stock in inventory.items()
            ])
            
            # Sort by stock (low first)
            df = df.sort_values("Stock")
            
            # Color coding
            def color_stock(val):
                if val == 0:
                    return 'background-color: #ffebee'  # Red
                elif val < 5:
                    return 'background-color: #fff3e0'  # Orange
                else:
                    return 'background-color: #e8f5e8'  # Green
            
            styled_df = df.style.applymap(color_stock, subset=['Stock'])
            st.dataframe(styled_df, use_container_width=True, height=400)
        else:
            st.info("No inventory items found. Click 'Load Complete Database' in sidebar to populate.")
    
    with tab2:
        st.subheader("Add New Stock")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Add Spectacle Stock**")
            spec_names = list(COMPREHENSIVE_SPECTACLE_DATABASE.keys())[:50]  # Limit for speed
            selected_spec = st.selectbox("Select Spectacle", [""] + spec_names, key="add_spec")
            spec_quantity = st.number_input("Quantity", min_value=1, value=10, key="spec_qty")
            
            if st.button("Add Spectacle Stock", key="add_spec_btn"):
                if selected_spec:
                    add_or_update_inventory(selected_spec, spec_quantity)
                    st.success(f"Added {spec_quantity} units of {selected_spec}")
                    st.rerun()
        
        with col2:
            st.markdown("**Add Medicine Stock**")
            med_names = list(COMPREHENSIVE_MEDICINE_DATABASE.keys())[:50]  # Limit for speed
            selected_med = st.selectbox("Select Medicine", [""] + med_names, key="add_med")
            med_quantity = st.number_input("Quantity", min_value=1, value=20, key="med_qty")
            
            if st.button("Add Medicine Stock", key="add_med_btn"):
                if selected_med:
                    add_or_update_inventory(selected_med, med_quantity)
                    st.success(f"Added {med_quantity} units of {selected_med}")
                    st.rerun()
    
    with tab3:
        st.subheader("Search & Update Stock")
        
        search_term = st.text_input("🔍 Search items", placeholder="Type to search...")
        
        if search_term:
            # Search in current inventory
            matching_items = [item for item in inventory.keys() if search_term.lower() in item.lower()]
            
            if matching_items:
                for item in matching_items[:10]:  # Limit results
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{item}**")
                        st.write(f"Current stock: {inventory[item]}")
                    
                    with col2:
                        new_stock = st.number_input("New Stock", min_value=0, value=inventory[item], key=f"update_{item}")
                    
                    with col3:
                        if st.button("Update", key=f"btn_{item}"):
                            add_or_update_inventory(item, new_stock - inventory[item])
                            st.success("Updated!")
                            st.rerun()
            else:
                st.info("No matching items found")
    
    with tab4:
        st.subheader("Stock Alerts")
        
        # Low stock items
        low_stock_items = [(item, stock) for item, stock in inventory.items() if stock < 5]
        out_of_stock_items = [(item, stock) for item, stock in inventory.items() if stock == 0]
        
        if out_of_stock_items:
            st.error("🚨 Out of Stock Items:")
            for item, stock in out_of_stock_items:
                st.write(f"❌ {item}")
        
        if low_stock_items:
            st.warning("⚠️ Low Stock Items (< 5 units):")
            for item, stock in low_stock_items:
                if stock > 0:  # Don't show out of stock here
                    st.write(f"🔸 {item}: {stock} units")
        
        if not low_stock_items and not out_of_stock_items:
            st.success("✅ All items are well stocked!")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Inventory"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export to CSV"):
            if inventory:
                df = pd.DataFrame([
                    {"Item": item, "Stock": stock}
                    for item, stock in inventory.items()
                ])
                csv = df.to_csv(index=False)
                st.download_button(
                    "💾 Download CSV",
                    csv,
                    "inventory.csv",
                    "text/csv"
                )
    
    with col3:
        if st.button("⚡ Load Sample Data"):
            # Add sample data quickly
            sample_items = {
                "Ray-Ban Aviator": 15,
                "Oakley Holbrook": 12,
                "Refresh Tears": 25,
                "Systane Ultra": 18
            }
            for item, stock in sample_items.items():
                add_or_update_inventory(item, stock)
            st.success("Sample data loaded!")
            st.rerun()

# Create instance for easy import
inventory_manager = type('InventoryManager', (), {
    'show_inventory_management_page': show_inventory_management_page
})()