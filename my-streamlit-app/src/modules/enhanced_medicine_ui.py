"""
Enhanced Medicine UI Component
Provides comprehensive medicine selection and management interface
"""
import streamlit as st
import pandas as pd
from modules.enhanced_inventory_manager import enhanced_inventory
from modules.mcp_medicine_integration import mcp_integrator
import db

def render_medicine_selection_ui():
    """Render enhanced medicine selection interface"""
    
    st.subheader("💊 Enhanced Medicine Selection")
    
    # Medicine search and selection tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Search & Select", 
        "🏥 By Condition", 
        "🛒 Purchase External", 
        "📊 Inventory Status"
    ])
    
    with tab1:
        st.markdown("**Search and Select Medicines**")
        
        # Search functionality
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search medicines by name or condition", 
                                      placeholder="e.g., eye drops, dry eyes, antibiotic")
        with col2:
            search_button = st.button("Search", type="primary")
        
        # Get all medicines
        if search_term or search_button:
            if search_term:
                medicines = enhanced_inventory.search_medicines(search_term)
            else:
                medicines = enhanced_inventory.get_all_medicines()
        else:
            medicines = enhanced_inventory.get_all_medicines()
        
        if medicines:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                categories = list(set([med.get("category", "Unknown") for med in medicines.values()]))
                selected_category = st.selectbox("Filter by Category", ["All"] + categories)
            
            with col2:
                types = list(set([med.get("type", "Unknown") for med in medicines.values()]))
                selected_type = st.selectbox("Filter by Type", ["All"] + types)
            
            with col3:
                stock_filter = st.selectbox("Stock Status", ["All", "In Stock", "Out of Stock", "External Available"])
            
            # Apply filters
            filtered_medicines = {}
            for med_name, med_data in medicines.items():
                # Category filter
                if selected_category != "All" and med_data.get("category") != selected_category:
                    continue
                
                # Type filter
                if selected_type != "All" and med_data.get("type") != selected_type:
                    continue
                
                # Stock filter
                current_stock = med_data.get("current_stock", 0)
                external_stock = med_data.get("external_stock", 0)
                
                if stock_filter == "In Stock" and current_stock <= 0:
                    continue
                elif stock_filter == "Out of Stock" and current_stock > 0:
                    continue
                elif stock_filter == "External Available" and external_stock <= 0:
                    continue
                
                filtered_medicines[med_name] = med_data
            
            # Display medicines
            st.markdown(f"**Found {len(filtered_medicines)} medicines**")
            
            selected_medicines = {}
            dosages = {}
            
            for med_name, med_data in filtered_medicines.items():
                with st.expander(f"💊 {med_name}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Category:** {med_data.get('category', 'N/A')}")
                        st.write(f"**Type:** {med_data.get('type', 'N/A')}")
                        st.write(f"**Price:** ₹{med_data.get('price', 0)}")
                        if med_data.get("indication"):
                            st.write(f"**Indication:** {med_data['indication']}")
                        
                        # Stock information
                        current_stock = med_data.get("current_stock", 0)
                        external_stock = med_data.get("external_stock", 0)
                        
                        if current_stock > 0:
                            st.success(f"✅ In Stock: {current_stock} units")
                        elif external_stock > 0:
                            st.info(f"🛒 Available for purchase: {external_stock} units from {med_data.get('source', 'External')}")
                        else:
                            st.warning("⚠️ Out of stock")
                    
                    with col2:
                        # Selection checkbox
                        select_med = st.checkbox(f"Select", key=f"select_{med_name}")
                        
                        if select_med:
                            max_qty = max(current_stock, 1) if current_stock > 0 else 10
                            qty = st.number_input(f"Quantity", min_value=1, max_value=max_qty, 
                                                value=1, key=f"qty_{med_name}")
                            selected_medicines[med_name] = qty
                    
                    with col3:
                        if select_med:
                            # Dosage selection
                            dosage_options = ["1 drop", "2 drops", "1 tablet", "2 tablets", "As directed"]
                            dosage = st.selectbox("Dosage", dosage_options, key=f"dose_{med_name}")
                            
                            timing_options = ["Once daily", "Twice daily", "Thrice daily", "As needed"]
                            timing = st.selectbox("Timing", timing_options, key=f"timing_{med_name}")
                            
                            dosages[med_name] = {"dosage": dosage, "timing": timing}
            
            # Store selections in session state
            if selected_medicines:
                st.session_state["selected_medicines"] = selected_medicines
                st.session_state["medicine_dosages"] = dosages
                st.success(f"✅ Selected {len(selected_medicines)} medicines")
    
    with tab2:
        st.markdown("**Select Medicines by Eye Condition**")
        
        # Condition selection
        conditions = [
            "dry_eyes", "bacterial_infection", "allergic_conjunctivitis", 
            "glaucoma", "inflammation", "viral_infection", "eye_strain"
        ]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_condition = st.selectbox("Select Eye Condition", conditions)
        with col2:
            patient_age = st.number_input("Patient Age", min_value=1, max_value=120, value=30)
        
        if st.button("Get Recommendations", type="primary"):
            recommendations = enhanced_inventory.get_medicines_by_condition(selected_condition, patient_age)
            
            # Display local recommendations
            if recommendations["local_recommendations"]:
                st.markdown("**🏠 Local Inventory Recommendations:**")
                for med_name, med_data in recommendations["local_recommendations"].items():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{med_name}**")
                            st.write(f"Price: ₹{med_data.get('price', 0)} | {med_data.get('indication', 'N/A')}")
                        with col2:
                            if st.button(f"Add", key=f"add_local_{med_name}"):
                                if "selected_medicines" not in st.session_state:
                                    st.session_state["selected_medicines"] = {}
                                st.session_state["selected_medicines"][med_name] = 1
                                st.success(f"Added {med_name}")
            
            # Display MCP recommendations
            if recommendations["mcp_recommendations"]:
                st.markdown("**🌐 External Database Recommendations:**")
                for med_data in recommendations["mcp_recommendations"]:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{med_data['name']}**")
                            price_range = med_data['price_range']
                            st.write(f"Price: ₹{price_range['min']}-₹{price_range['max']} | Available from: {', '.join(med_data['sources'])}")
                        with col2:
                            st.write(f"Rx Required: {'Yes' if med_data['prescription_required'] else 'No'}")
    
    with tab3:
        st.markdown("**Purchase Medicines from External Sources**")
        
        # Get external inventory
        external_inventory = mcp_integrator.get_real_time_inventory()
        
        for category, medicines in external_inventory.items():
            st.markdown(f"**{category.replace('_', ' ').title()}**")
            
            for med_name, med_data in medicines.items():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{med_name}**")
                        st.write(f"Source: {med_data['source']}")
                    
                    with col2:
                        st.write(f"₹{med_data['price']}")
                        st.write(f"Stock: {med_data['stock']}")
                    
                    with col3:
                        purchase_qty = st.number_input(f"Qty", min_value=1, max_value=med_data['stock'], 
                                                     value=1, key=f"purchase_qty_{med_name}")
                    
                    with col4:
                        if st.button(f"Purchase", key=f"purchase_{med_name}"):
                            with st.spinner("Processing purchase..."):
                                result = enhanced_inventory.purchase_medicine_external(
                                    med_name, purchase_qty, med_data['source']
                                )
                            
                            if result["status"] == "success":
                                st.success(f"✅ Purchased {purchase_qty} units of {med_name}")
                                st.info(f"Tracking ID: {result['tracking_id']}")
                                st.info(f"Estimated Delivery: {result['estimated_delivery']}")
                                st.rerun()
                            else:
                                st.error("❌ Purchase failed")
    
    with tab4:
        st.markdown("**Inventory Status & Management**")
        
        # Generate inventory report
        if st.button("📊 Generate Inventory Report", type="primary"):
            report_df = enhanced_inventory.generate_inventory_report()
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_items = len(report_df)
                st.metric("Total Items", total_items)
            
            with col2:
                in_stock_items = len(report_df[report_df["Status"] == "In Stock"])
                st.metric("In Stock", in_stock_items)
            
            with col3:
                out_of_stock = len(report_df[report_df["Status"] == "Out of Stock"])
                st.metric("Out of Stock", out_of_stock)
            
            with col4:
                total_value = enhanced_inventory.get_inventory_value()
                st.metric("Total Value", f"₹{total_value:,.0f}")
            
            # Display detailed report
            st.markdown("**Detailed Inventory Report:**")
            st.dataframe(report_df, use_container_width=True)
            
            # Low stock alerts
            low_stock = enhanced_inventory.get_low_stock_items()
            if low_stock:
                st.warning("⚠️ **Low Stock Alert:**")
                for item, stock in low_stock:
                    st.write(f"• {item}: {stock} units remaining")
    
    return st.session_state.get("selected_medicines", {}), st.session_state.get("medicine_dosages", {})

def render_prescription_summary(selected_medicines, dosages):
    """Render prescription summary"""
    if selected_medicines:
        st.markdown("**📋 Prescription Summary:**")
        
        total_cost = 0
        for med_name, qty in selected_medicines.items():
            # Get medicine data
            all_medicines = enhanced_inventory.get_all_medicines()
            med_data = all_medicines.get(med_name, {})
            
            price = med_data.get("price", 0)
            cost = price * qty
            total_cost += cost
            
            dosage_info = dosages.get(med_name, {})
            dosage_text = f"{dosage_info.get('dosage', 'As directed')} {dosage_info.get('timing', '')}"
            
            st.write(f"• **{med_name}** - Qty: {qty} - ₹{cost} - {dosage_text}")
        
        st.write(f"**Total Cost: ₹{total_cost}**")
        
        return total_cost
    
    return 0