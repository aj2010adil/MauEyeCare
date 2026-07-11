"""
Professional Inventory Management System for MauEyeCare
Allows doctors to upload and manage medicines and spectacles inventory
"""

import streamlit as st
import pandas as pd
import json
import datetime
from modules.inventory_utils import add_or_update_inventory, get_inventory_dict, reduce_inventory
from modules.comprehensive_medicine_database import COMPREHENSIVE_MEDICINE_DATABASE
from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE

class ProfessionalInventoryManager:
    """Professional inventory management with upload capabilities"""
    
    def __init__(self):
        self.inventory_file = "inventory_data.json"
        self.medicine_categories = [
            "Antibiotic", "Anti-inflammatory", "Lubricant", "Antihistamine", 
            "Antiviral", "Glaucoma", "Mydriatic", "Anesthetic"
        ]
        self.spectacle_categories = [
            "Luxury", "Mid-Range", "Budget", "Progressive", "Reading", 
            "Computer", "Safety", "Kids", "Sports"
        ]
    
    def show_inventory_management_page(self):
        """Main inventory management interface"""
        
        st.header("📦 Professional Inventory Management")
        st.markdown("*Manage medicines and spectacles inventory with professional tools*")
        
        # Inventory overview
        self._show_inventory_overview()
        
        # Management tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💊 Add Medicines", 
            "👓 Add Spectacles", 
            "📊 Current Stock", 
            "📈 Analytics", 
            "⚙️ Bulk Operations"
        ])
        
        with tab1:
            self._show_medicine_upload_form()
        
        with tab2:
            self._show_spectacle_upload_form()
        
        with tab3:
            self._show_current_stock()
        
        with tab4:
            self._show_inventory_analytics()
        
        with tab5:
            self._show_bulk_operations()
    
    def _show_inventory_overview(self):
        """Display inventory overview dashboard"""
        
        inventory = get_inventory_dict()
        
        # Calculate statistics
        total_items = len(inventory)
        total_medicines = len([k for k in inventory.keys() if k in COMPREHENSIVE_MEDICINE_DATABASE])
        total_spectacles = len([k for k in inventory.keys() if k in COMPREHENSIVE_SPECTACLE_DATABASE])
        low_stock_items = len([k for k, v in inventory.items() if v <= 5])
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total Items", total_items)
        
        with col2:
            st.metric("💊 Medicines", total_medicines)
        
        with col3:
            st.metric("👓 Spectacles", total_spectacles)
        
        with col4:
            st.metric("⚠️ Low Stock", low_stock_items, delta=-low_stock_items if low_stock_items > 0 else 0)
        
        # Alerts
        if low_stock_items > 0:
            st.warning(f"⚠️ **{low_stock_items} items** have low stock (≤5 units). Please restock soon!")
    
    def _show_medicine_upload_form(self):
        """Medicine upload and management form"""
        
        st.subheader("💊 Add New Medicine to Inventory")
        
        with st.form("medicine_upload_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                medicine_name = st.text_input("Medicine Name*", placeholder="Enter medicine name")
                category = st.selectbox("Category*", self.medicine_categories)
                manufacturer = st.text_input("Manufacturer", placeholder="e.g., Sun Pharma")
                composition = st.text_input("Composition", placeholder="e.g., Moxifloxacin 0.5%")
            
            with col2:
                price = st.number_input("Price per Unit (₹)*", min_value=0.0, step=0.01)
                stock_quantity = st.number_input("Initial Stock Quantity*", min_value=0, step=1)
                prescription_required = st.checkbox("Prescription Required")
                expiry_date = st.date_input("Expiry Date", min_value=datetime.date.today())
            
            # Additional details
            st.markdown("**Additional Information**")
            col3, col4 = st.columns(2)
            
            with col3:
                dosage_form = st.selectbox("Dosage Form", 
                    ["Drops", "Ointment", "Tablet", "Capsule", "Injection", "Gel"])
                strength = st.text_input("Strength", placeholder="e.g., 5ml, 10mg")
            
            with col4:
                conditions = st.multiselect("Treats Conditions", 
                    ["dry_eyes", "infection", "allergy", "inflammation", "glaucoma", "pain"])
                storage_temp = st.selectbox("Storage Temperature", 
                    ["Room Temperature", "Refrigerated", "Frozen"])
            
            # Batch information
            st.markdown("**Batch Information**")
            col5, col6 = st.columns(2)
            
            with col5:
                batch_number = st.text_input("Batch Number", placeholder="e.g., BT2024001")
                supplier = st.text_input("Supplier", placeholder="Supplier name")
            
            with col6:
                purchase_date = st.date_input("Purchase Date", value=datetime.date.today())
                cost_price = st.number_input("Cost Price (₹)", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("💊 Add Medicine to Inventory", type="primary")
            
            if submitted and medicine_name and category and price > 0 and stock_quantity > 0:
                # Create medicine data
                medicine_data = {
                    'name': medicine_name,
                    'category': category,
                    'manufacturer': manufacturer,
                    'composition': composition,
                    'price': price,
                    'prescription_required': prescription_required,
                    'expiry_date': expiry_date.isoformat(),
                    'dosage_form': dosage_form,
                    'strength': strength,
                    'conditions': conditions,
                    'storage_temp': storage_temp,
                    'batch_number': batch_number,
                    'supplier': supplier,
                    'purchase_date': purchase_date.isoformat(),
                    'cost_price': cost_price,
                    'added_date': datetime.datetime.now().isoformat(),
                    'added_by': 'Dr. Danish'
                }
                
                # Add to inventory
                add_or_update_inventory(medicine_name, stock_quantity)
                
                # Save medicine data to custom database
                self._save_custom_medicine_data(medicine_name, medicine_data)
                
                st.success(f"✅ **{medicine_name}** added to inventory with {stock_quantity} units!")
                st.balloons()
    
    def _show_spectacle_upload_form(self):
        """Spectacle upload and management form"""
        
        st.subheader("👓 Add New Spectacle to Inventory")
        
        with st.form("spectacle_upload_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                brand = st.text_input("Brand*", placeholder="e.g., Ray-Ban, Lenskart")
                model = st.text_input("Model*", placeholder="e.g., Aviator Classic")
                frame_price = st.number_input("Frame Price (₹)*", min_value=0.0, step=0.01)
                lens_price = st.number_input("Lens Price (₹)*", min_value=0.0, step=0.01)
            
            with col2:
                category = st.selectbox("Category*", self.spectacle_categories)
                stock_quantity = st.number_input("Initial Stock Quantity*", min_value=0, step=1)
                material = st.selectbox("Frame Material", 
                    ["Metal", "Plastic", "Titanium", "Acetate", "TR90", "Wood"])
                shape = st.selectbox("Frame Shape", 
                    ["Aviator", "Wayfarer", "Round", "Square", "Cat-eye", "Rectangular", "Oval"])
            
            # Additional specifications
            st.markdown("**Frame Specifications**")
            col3, col4 = st.columns(2)
            
            with col3:
                lens_width = st.number_input("Lens Width (mm)", min_value=0, max_value=100, step=1)
                bridge_width = st.number_input("Bridge Width (mm)", min_value=0, max_value=50, step=1)
                temple_length = st.number_input("Temple Length (mm)", min_value=0, max_value=200, step=1)
            
            with col4:
                color = st.text_input("Color", placeholder="e.g., Black, Gold, Silver")
                gender = st.selectbox("Gender", ["Unisex", "Male", "Female", "Kids"])
                face_shapes = st.multiselect("Suitable Face Shapes", 
                    ["Round", "Square", "Oval", "Heart", "Long/Oval", "Diamond"])
            
            # Lens options
            st.markdown("**Lens Options**")
            col5, col6 = st.columns(2)
            
            with col5:
                lens_types = st.multiselect("Available Lens Types", 
                    ["Single Vision", "Progressive", "Bifocal", "Reading", "Computer", "Photochromic"])
                coatings = st.multiselect("Available Coatings", 
                    ["Anti-Glare", "Blue Light", "UV Protection", "Scratch Resistant", "Water Repellent"])
            
            with col6:
                prescription_range = st.text_input("Prescription Range", 
                    placeholder="e.g., -8.00 to +6.00")
                warranty_period = st.selectbox("Warranty Period", 
                    ["6 months", "1 year", "2 years", "Lifetime"])
            
            # Supplier information
            st.markdown("**Supplier Information**")
            col7, col8 = st.columns(2)
            
            with col7:
                supplier = st.text_input("Supplier", placeholder="Supplier name")
                supplier_code = st.text_input("Supplier Code", placeholder="e.g., SUP001")
            
            with col8:
                purchase_date = st.date_input("Purchase Date", value=datetime.date.today())
                cost_price = st.number_input("Cost Price per Unit (₹)", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("👓 Add Spectacle to Inventory", type="primary")
            
            if submitted and brand and model and frame_price > 0 and stock_quantity > 0:
                # Create spectacle data
                spectacle_name = f"{brand} {model}"
                spectacle_data = {
                    'brand': brand,
                    'model': model,
                    'category': category,
                    'price': frame_price,
                    'lens_price': lens_price,
                    'material': material,
                    'shape': shape,
                    'lens_width': lens_width,
                    'bridge_width': bridge_width,
                    'temple_length': temple_length,
                    'color': color,
                    'gender': gender,
                    'face_shapes': face_shapes,
                    'lens_types': lens_types,
                    'coatings': coatings,
                    'prescription_range': prescription_range,
                    'warranty_period': warranty_period,
                    'supplier': supplier,
                    'supplier_code': supplier_code,
                    'purchase_date': purchase_date.isoformat(),
                    'cost_price': cost_price,
                    'added_date': datetime.datetime.now().isoformat(),
                    'added_by': 'Dr. Danish'
                }
                
                # Add to inventory
                add_or_update_inventory(spectacle_name, stock_quantity)
                
                # Save spectacle data to custom database
                self._save_custom_spectacle_data(spectacle_name, spectacle_data)
                
                st.success(f"✅ **{spectacle_name}** added to inventory with {stock_quantity} units!")
                st.balloons()
    
    def _show_current_stock(self):
        """Display current stock levels"""
        
        st.subheader("📊 Current Stock Levels")
        
        inventory = get_inventory_dict()
        
        if not inventory:
            st.info("📦 No items in inventory. Add medicines and spectacles using the forms above.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_type = st.selectbox("Filter by Type", ["All", "Medicines", "Spectacles"])
        
        with col2:
            stock_filter = st.selectbox("Stock Level", ["All", "Low Stock (≤5)", "Medium Stock (6-20)", "High Stock (>20)"])
        
        with col3:
            search_term = st.text_input("Search Items", placeholder="Search by name...")
        
        # Prepare data for display
        stock_data = []
        
        for item_name, quantity in inventory.items():
            # Determine item type
            if item_name in COMPREHENSIVE_MEDICINE_DATABASE:
                item_type_actual = "Medicine"
                item_data = COMPREHENSIVE_MEDICINE_DATABASE[item_name]
                price = item_data.get('price', 0)
                category = item_data.get('category', 'Unknown')
            elif item_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                item_type_actual = "Spectacle"
                item_data = COMPREHENSIVE_SPECTACLE_DATABASE[item_name]
                price = item_data.get('price', 0) + item_data.get('lens_price', 0)
                category = item_data.get('category', 'Unknown')
            else:
                item_type_actual = "Custom"
                price = 0
                category = "Custom Added"
            
            # Apply filters
            if item_type != "All" and item_type_actual != item_type.rstrip('s'):
                continue
            
            if stock_filter != "All":
                if stock_filter == "Low Stock (≤5)" and quantity > 5:
                    continue
                elif stock_filter == "Medium Stock (6-20)" and (quantity <= 5 or quantity > 20):
                    continue
                elif stock_filter == "High Stock (>20)" and quantity <= 20:
                    continue
            
            if search_term and search_term.lower() not in item_name.lower():
                continue
            
            # Stock status
            if quantity <= 5:
                status = "🔴 Low"
            elif quantity <= 20:
                status = "🟡 Medium"
            else:
                status = "🟢 High"
            
            stock_data.append({
                'Item Name': item_name,
                'Type': item_type_actual,
                'Category': category,
                'Current Stock': quantity,
                'Status': status,
                'Unit Price (₹)': price,
                'Total Value (₹)': price * quantity
            })
        
        if stock_data:
            df = pd.DataFrame(stock_data)
            
            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Items Shown", len(df))
            
            with col2:
                total_value = df['Total Value (₹)'].sum()
                st.metric("Total Inventory Value", f"₹{total_value:,.2f}")
            
            with col3:
                low_stock_count = len(df[df['Status'] == '🔴 Low'])
                st.metric("Low Stock Items", low_stock_count)
            
            with col4:
                avg_stock = df['Current Stock'].mean()
                st.metric("Average Stock Level", f"{avg_stock:.1f}")
            
            # Display table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Quick actions
            st.markdown("### 🔧 Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export to CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"inventory_{datetime.date.today()}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("⚠️ Show Low Stock Only"):
                    low_stock_df = df[df['Status'] == '🔴 Low']
                    if not low_stock_df.empty:
                        st.dataframe(low_stock_df, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ No low stock items!")
            
            with col3:
                if st.button("🔄 Refresh Data"):
                    st.rerun()
        
        else:
            st.info("📦 No items match the current filters.")
    
    def _show_inventory_analytics(self):
        """Show inventory analytics and insights"""
        
        st.subheader("📈 Inventory Analytics")
        
        inventory = get_inventory_dict()
        
        if not inventory:
            st.info("📊 No data available for analytics. Add items to inventory first.")
            return
        
        # Analytics calculations
        total_items = len(inventory)
        total_stock = sum(inventory.values())
        
        # Category breakdown
        medicine_items = [k for k in inventory.keys() if k in COMPREHENSIVE_MEDICINE_DATABASE]
        spectacle_items = [k for k in inventory.keys() if k in COMPREHENSIVE_SPECTACLE_DATABASE]
        
        # Display charts and metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Inventory Composition**")
            
            composition_data = {
                'Medicines': len(medicine_items),
                'Spectacles': len(spectacle_items),
                'Custom Items': total_items - len(medicine_items) - len(spectacle_items)
            }
            
            st.bar_chart(composition_data)
        
        with col2:
            st.markdown("**📈 Stock Distribution**")
            
            stock_levels = {
                'Low Stock (≤5)': len([k for k, v in inventory.items() if v <= 5]),
                'Medium Stock (6-20)': len([k for k, v in inventory.items() if 6 <= v <= 20]),
                'High Stock (>20)': len([k for k, v in inventory.items() if v > 20])
            }
            
            st.bar_chart(stock_levels)
        
        # Top items
        st.markdown("**🔝 Top 10 Items by Stock**")
        
        top_items = sorted(inventory.items(), key=lambda x: x[1], reverse=True)[:10]
        top_df = pd.DataFrame(top_items, columns=['Item', 'Stock'])
        
        st.dataframe(top_df, use_container_width=True, hide_index=True)
    
    def _show_bulk_operations(self):
        """Bulk inventory operations"""
        
        st.subheader("⚙️ Bulk Operations")
        
        operation = st.selectbox("Select Operation", [
            "Bulk Stock Update",
            "Import from CSV",
            "Export All Data",
            "Reset Low Stock Items",
            "Generate Reorder Report"
        ])
        
        if operation == "Bulk Stock Update":
            st.markdown("**📦 Bulk Stock Update**")
            
            uploaded_file = st.file_uploader("Upload CSV with Item Name and New Stock columns", type=['csv'])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    if 'Item Name' in df.columns and 'New Stock' in df.columns:
                        st.dataframe(df, use_container_width=True)
                        
                        if st.button("🔄 Update Stock Levels"):
                            updated_count = 0
                            
                            for _, row in df.iterrows():
                                item_name = row['Item Name']
                                new_stock = int(row['New Stock'])
                                
                                add_or_update_inventory(item_name, new_stock)
                                updated_count += 1
                            
                            st.success(f"✅ Updated {updated_count} items successfully!")
                    else:
                        st.error("❌ CSV must have 'Item Name' and 'New Stock' columns")
                
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
        
        elif operation == "Generate Reorder Report":
            st.markdown("**📋 Reorder Report**")
            
            inventory = get_inventory_dict()
            low_stock_items = [(k, v) for k, v in inventory.items() if v <= 5]
            
            if low_stock_items:
                reorder_df = pd.DataFrame(low_stock_items, columns=['Item Name', 'Current Stock'])
                reorder_df['Suggested Reorder Quantity'] = reorder_df['Current Stock'].apply(lambda x: max(20 - x, 10))
                
                st.dataframe(reorder_df, use_container_width=True, hide_index=True)
                
                csv = reorder_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Reorder Report",
                    data=csv,
                    file_name=f"reorder_report_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.success("✅ No items need reordering!")
    
    def _save_custom_medicine_data(self, medicine_name, medicine_data):
        """Save custom medicine data to file"""
        try:
            # Load existing custom data
            try:
                with open('custom_medicines.json', 'r') as f:
                    custom_medicines = json.load(f)
            except FileNotFoundError:
                custom_medicines = {}
            
            # Add new medicine
            custom_medicines[medicine_name] = medicine_data
            
            # Save back to file
            with open('custom_medicines.json', 'w') as f:
                json.dump(custom_medicines, f, indent=2)
        
        except Exception as e:
            st.error(f"Error saving medicine data: {str(e)}")
    
    def _save_custom_spectacle_data(self, spectacle_name, spectacle_data):
        """Save custom spectacle data to file"""
        try:
            # Load existing custom data
            try:
                with open('custom_spectacles.json', 'r') as f:
                    custom_spectacles = json.load(f)
            except FileNotFoundError:
                custom_spectacles = {}
            
            # Add new spectacle
            custom_spectacles[spectacle_name] = spectacle_data
            
            # Save back to file
            with open('custom_spectacles.json', 'w') as f:
                json.dump(custom_spectacles, f, indent=2)
        
        except Exception as e:
            st.error(f"Error saving spectacle data: {str(e)}")

# Global instance
inventory_manager = ProfessionalInventoryManager()