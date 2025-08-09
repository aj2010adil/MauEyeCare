
# MauEyeCare Main App
# Entry point for Streamlit UI. Uses modules for PDF, AI, and inventory logic.

import streamlit as st
import pandas as pd
from io import BytesIO
import sys, os
import requests
sys.path.append(os.path.dirname(__file__))
import db
from fpdf import FPDF
from modules.pdf_utils import generate_pdf
from modules.ai_utils import get_grok_suggestion
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory
# LangGraph imports - will be loaded conditionally
try:
    from langgraph_agent import mau_agent
    from market_updater import market_updater
    LANGGRAPH_AVAILABLE = True
    print("LangGraph components loaded successfully")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    mau_agent = None
    market_updater = None
    print(f"LangGraph not available: {e}")

def to_excel(df):
    """Convert DataFrame to Excel for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

db.init_db()

grok_key = None
try:
    config_path = os.path.join(os.path.dirname(__file__), "perplexity_config.py")
    if config_path not in sys.path:
        sys.path.append(os.path.dirname(config_path))
    import perplexity_config
    grok_key = getattr(perplexity_config, "grok_key", None)
except Exception:
    grok_key = None


def get_grok_suggestion(doctor_name, patient_name, selected_meds, dosage, eye_test):
    if not grok_key:
        return "Grok API key not set. Please add it to src/perplexity_config.py."
    prompt = f"Doctor: {doctor_name}\nPatient: {patient_name}\nSelected medicines: {selected_meds}\nDosage: {dosage}\nEye test: {eye_test}\nSuggest best practices, additional medicines, or dosage improvements as per latest standards and what other doctors use."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
    data = {
        "model": "qwen/qwen3-32b",
        "messages": [
            {"role": "system", "content": "You are a helpful medical assistant for eye care prescription."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Grok API error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error contacting Grok: {e}"

# Sample inventory (in a real app, this would come from a database)
inventory = {
    'Eye Drop A': 10,
    'Tablet B': 5,
    'Ointment C': 0,
    'Capsule D': 2
}



def main():

    st.title("🔍 Mau Eye Care Optical Center")
    st.markdown("*Advanced Eye Care & Prescription Management System*")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Prescription & Patient", "📦 Inventory Management", "📊 Patient History", "🤖 AI Agent Tools"])

    # --- Prescription & Patient Tab ---
    with tab1:
        st.header("👥 Patient Information & Prescription")
        # --- Patient Form ---
        with st.form("patient_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            patient_name = f"{first_name} {last_name}".strip()
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Mobile Number")
            
            # Patient Issue/Complaint (moved before advice)
            issue_options = ["Blurry Vision", "Eye Pain", "Redness", "Dry Eyes", "Double Vision", "Headache", "Light Sensitivity", "Floaters", "Night Vision Problems", "Other"]
            patient_issue = st.selectbox("Patient Issue/Complaint", issue_options)
            if patient_issue == "Other":
                patient_issue = st.text_input("Specify Other Issue")
            
            # Advice/Notes with dropdown
            advice_options = ["Cataract Surgery Recommended", "Spectacle Prescription", "Contact Lens Fitting", "Regular Eye Checkup", "Glaucoma Treatment", "Diabetic Eye Care", "Dry Eye Treatment", "Other"]
            advice = st.selectbox("Advice/Notes", advice_options)
            if advice == "Other":
                advice = st.text_input("Specify Other Advice")
            # RX Table with dropdowns
            st.markdown("**Rx Table** (Fill for OD and OS)")
            rx_table = {}
            sphere_options = ["", "+0.25", "+0.50", "+0.75", "+1.00", "+1.25", "+1.50", "+2.00", "+2.50", "+3.00", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-2.00", "-2.50", "-3.00"]
            cylinder_options = ["", "-0.25", "-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-2.00"]
            axis_options = ["", "90", "180", "45", "135", "30", "60", "120", "150"]
            glass_type_options = ["Single Vision", "Bifocal", "Progressive", "Reading Only"]
            glass_tint_options = ["Clear", "Photochromic", "Sunglasses", "Blue Light Filter", "Anti-Glare"]
            
            for eye in ['OD', 'OS']:
                st.markdown(f"**{eye}**")
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                with col1:
                    sphere = st.selectbox(f"Sphere {eye}", sphere_options, key=f"sphere_{eye}")
                with col2:
                    cylinder = st.selectbox(f"Cylinder {eye}", cylinder_options, key=f"cylinder_{eye}")
                with col3:
                    axis = st.selectbox(f"Axis {eye}", axis_options, key=f"axis_{eye}")
                with col4:
                    prism = st.text_input(f"Prism {eye}", key=f"prism_{eye}")
                with col5:
                    near_vision = st.selectbox(f"Near Vision {eye}", ["", "N6", "N8", "N10", "N12", "N18", "N24"], key=f"near_{eye}")
                with col6:
                    glass_type = st.selectbox(f"Glass Type {eye}", glass_type_options, key=f"type_{eye}")
                with col7:
                    glass_tint = st.selectbox(f"Glass Tint {eye}", glass_tint_options, key=f"tint_{eye}")
                rx_table[eye] = {"Sphere": sphere, "Cylinder": cylinder, "Axis": axis, "Prism": prism, "NearVision": near_vision, "GlassType": glass_type, "GlassTint": glass_tint}
            # Medical Tests
            st.markdown("**Medical Tests**")
            col1, col2 = st.columns(2)
            with col1:
                bp_options = ["Normal (120/80)", "High (>140/90)", "Low (<90/60)", "Not Tested"]
                blood_pressure = st.selectbox("Blood Pressure", bp_options)
                sugar_options = ["Normal (70-100)", "High (>126)", "Low (<70)", "Not Tested"]
                blood_sugar = st.selectbox("Blood Sugar", sugar_options)
            with col2:
                cbt_options = ["Normal", "Abnormal", "Not Done"]
                complete_blood_test = st.selectbox("Complete Blood Test", cbt_options)
                viral_options = ["Negative", "Positive", "Not Done"]
                viral_marker = st.selectbox("Viral Marker", viral_options)
            
            # Special Investigations
            st.markdown("**Special Investigations**")
            col3, col4, col5 = st.columns(3)
            with col3:
                fundus_options = ["Normal", "Diabetic Retinopathy", "Hypertensive Retinopathy", "Macular Degeneration", "Not Done"]
                fundus_examination = st.selectbox("Fundus Examination", fundus_options)
                iop_options = ["Normal (10-21 mmHg)", "High (>21 mmHg)", "Low (<10 mmHg)", "Not Measured"]
                iop = st.selectbox("IOP (Intraocular Pressure)", iop_options)
            with col4:
                retino_dry_options = ["Normal", "Myopia", "Hyperopia", "Astigmatism", "Not Done"]
                retinoscopy_dry = st.selectbox("Retinoscopy (Dry)", retino_dry_options)
                retino_wet_options = ["Normal", "Myopia", "Hyperopia", "Astigmatism", "Not Done"]
                retinoscopy_wet = st.selectbox("Retinoscopy (Wet)", retino_wet_options)
            with col5:
                syringing_options = ["Patent", "Blocked", "Partially Blocked", "Not Done"]
                syringing = st.selectbox("Syringing", syringing_options)
            
            # Medicine Selection (moved before save)
            st.markdown("**Medicine Selection**")
            inventory_db = get_inventory_dict()
            med_options = list(inventory_db.keys())
            selected_meds = st.multiselect("Choose medicines/spectacles", med_options, key="form_meds")
            prescription = {}
            for med in selected_meds:
                max_qty = inventory_db[med]
                qty = st.number_input(f"Quantity for {med} (Stock: {max_qty})", min_value=1, max_value=max_qty, value=1, key=f"form_qty_{med}")
                prescription[med] = qty
            
            # Recommendations
            st.markdown("**Recommendations** (Select all that apply)")
            rec_options = [
                "Single Vision", "Bifocal", "Trifocal", "Progressive", "Photochromatic", "Tint", "Polarized", "AR Coat", "HiIndex"
            ]
            recommendations = st.multiselect("Recommendations", rec_options)
            submitted = st.form_submit_button("Save/Select Patient")
            if submitted:
                # Check for duplicate by mobile and name
                patients = db.get_patients()
                found = False
                for p in patients:
                    if p[1].lower() == patient_name.lower() and p[4] == contact:
                        patient_id = p[0]
                        found = True
                        break
                if not found:
                    patient_id = db.add_patient(patient_name, age, gender, contact)
                    # Only add a history record for a new patient, and only if there is a non-empty issue
                    if patient_issue.strip():
                        db.add_prescription(
                            patient_id,
                            "Dr Danish",
                            {'medicines': {}, 'dosage': '', 'eye_test': '', 'issue': patient_issue, 'money_given': 0, 'money_pending': 0},
                            '',
                            ''
                        )
                st.session_state['patient_id'] = patient_id
                st.session_state['patient_name'] = patient_name
                st.session_state['age'] = age
                st.session_state['gender'] = gender
                st.session_state['advice'] = advice
                st.session_state['rx_table'] = rx_table
                st.session_state['recommendations'] = recommendations
                st.session_state['patient_issue'] = patient_issue
                st.session_state['prescription'] = prescription
                st.session_state['medical_tests'] = {
                    'blood_pressure': blood_pressure,
                    'blood_sugar': blood_sugar,
                    'complete_blood_test': complete_blood_test,
                    'viral_marker': viral_marker,
                    'fundus_examination': fundus_examination,
                    'iop': iop,
                    'retinoscopy_dry': retinoscopy_dry,
                    'retinoscopy_wet': retinoscopy_wet,
                    'syringing': syringing
                }
                st.session_state['show_prescription_pdf'] = True

        # --- Show patient history and AI verification after form submission ---
        if st.session_state.get('show_prescription_pdf', False):
            patient_id = st.session_state['patient_id']
            patient_name = st.session_state['patient_name']
            age = st.session_state['age']
            gender = st.session_state['gender']
            advice = st.session_state['advice']
            rx_table = st.session_state['rx_table']
            recommendations = st.session_state['recommendations']
            prescription = st.session_state['prescription']
            patient_issue = st.session_state['patient_issue']
            medical_tests = st.session_state['medical_tests']
            
            st.success(f"Patient saved/selected: {patient_name}")
            
            # Show Patient History with Medical Tests
            st.markdown("---")
            st.subheader("Patient History")
            
            # Show medical test history
            try:
                med_history = db.get_medical_tests(patient_id)
                if med_history:
                    st.markdown("**Recent Medical Tests:**")
                    latest_test = med_history[0]  # Most recent
                    st.info(f"Last Test Date: {latest_test[11]} | BP: {latest_test[2]} | Sugar: {latest_test[3]} | IOP: {latest_test[7]}")
                    
                    # Check for changes if there are previous tests
                    if len(med_history) > 1:
                        prev_test = med_history[1]
                        changes = []
                        if latest_test[2] != prev_test[2]: changes.append(f"BP: {prev_test[2]} → {latest_test[2]}")
                        if latest_test[3] != prev_test[3]: changes.append(f"Sugar: {prev_test[3]} → {latest_test[3]}")
                        if latest_test[7] != prev_test[7]: changes.append(f"IOP: {prev_test[7]} → {latest_test[7]}")
                        if changes:
                            st.warning(f"Changes detected: {'; '.join(changes)}")
            except Exception:
                st.info("No medical test history available")
            
            # Show prescription history
            history = db.get_prescriptions(patient_id)
            if history:
                st.markdown("**Recent Prescriptions:**")
                for pres in history[-3:]:  # Show last 3 records
                    st.info(f"Date: {pres[9]} | Issue: {pres[6]} | Medicines: {pres[3]} | Money Pending: ${pres[8]}")
            else:
                st.info("No previous history found.")
            
            # AI Agent Verification
            st.markdown("---")
            st.subheader("🤖 AI Agent Verification")
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("✅ Verify Prescription", type="primary"):
                    with st.spinner("🔍 AI verifying..."):
                        med_list = ', '.join([f"{med}({qty})" for med, qty in prescription.items()])
                        prompt = f"Patient: {patient_name}, Age: {age}, Issue: {patient_issue}, Advice: {advice}, Medicines: {med_list}. Verify prescription appropriateness in one concise line."
                        try:
                            import perplexity_config
                            grok_key = getattr(perplexity_config, "grok_key", None)
                            if grok_key:
                                url = "https://api.groq.com/openai/v1/chat/completions"
                                headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
                                data = {
                                    "model": "qwen/qwen3-32b",
                                    "messages": [{"role": "user", "content": prompt}]
                                }
                                response = requests.post(url, headers=headers, json=data, timeout=30)
                                if response.status_code == 200:
                                    result = response.json()
                                    ai_result = result["choices"][0]["message"]["content"]
                                    st.session_state['ai_verification'] = ai_result
                                else:
                                    st.session_state['ai_verification'] = "AI verification unavailable"
                            else:
                                st.session_state['ai_verification'] = "AI key not configured"
                        except Exception as e:
                            st.session_state['ai_verification'] = f"AI verification failed: {e}"
            with col2:
                if 'ai_verification' in st.session_state:
                    if "appropriate" in st.session_state['ai_verification'].lower() or "suitable" in st.session_state['ai_verification'].lower():
                        st.success(f"✅ {st.session_state['ai_verification']}")
                    else:
                        st.warning(f"⚠️ {st.session_state['ai_verification']}")
            
            st.markdown("---")
            st.subheader("📝 Generate Prescription PDF")
            pdf_file = generate_pdf(
                prescription,
                '',  # No dosage for now
                '',  # No eye test for now
                "Dr Danish",
                patient_name,
                age,
                gender,
                advice,
                rx_table,
                recommendations
            )
            st.download_button(
                label="Download/Print Prescription PDF",
                data=pdf_file,
                file_name=f"prescription_{patient_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"pdf_btn_{patient_id}"
            )
            
            # Save prescription and medical tests to database
            if st.button("Save Prescription & Medical Tests to Database", key=f"save_{patient_id}"):
                # Save medical tests
                try:
                    db.add_medical_tests(
                        patient_id,
                        medical_tests['blood_pressure'],
                        medical_tests['blood_sugar'],
                        medical_tests['complete_blood_test'],
                        medical_tests['viral_marker'],
                        medical_tests['fundus_examination'],
                        medical_tests['iop'],
                        medical_tests['retinoscopy_dry'],
                        medical_tests['retinoscopy_wet'],
                        medical_tests['syringing']
                    )
                except Exception as e:
                    st.error(f"Error saving medical tests: {e}")
                
                # Save prescription
                pres_data = {
                    'medicines': str(prescription),
                    'dosage': '',
                    'eye_test': '',
                    'issue': patient_issue,
                    'money_given': 0,
                    'money_pending': 0
                }
                db.add_prescription(patient_id, "Dr Danish", pres_data, '', '')
                for med, qty in prescription.items():
                    reduce_inventory(med, qty)
                st.success("Prescription and medical tests saved! Inventory updated!")
    # --- Patient History Tab ---
    with tab3:
        st.header("🔍 Patient History & Search")
        patients = db.get_patients()
        search_mobile = st.text_input("Search by Mobile Number", key="history_search_mobile")
        search_name = st.text_input("Search by Name", key="history_search_name")
        filtered = [p for p in patients if (search_mobile in p[4]) and (search_name.lower() in p[1].lower())]
        st.write(f"Found {len(filtered)} patient(s)")
        if filtered:
            for p in filtered:
                st.markdown(f"**Name:** {p[1]} | **Age:** {p[2]} | **Gender:** {p[3]} | **Mobile:** {p[4]}")
                
                # Show medical test history
                try:
                    med_tests = db.get_medical_tests(p[0])
                    if med_tests:
                        latest = med_tests[0]
                        st.info(f"Latest Tests ({latest[11]}): BP: {latest[2]} | Sugar: {latest[3]} | IOP: {latest[7]} | Fundus: {latest[6]}")
                except Exception:
                    st.info("No medical test history available")
                
                # Show prescription history
                history = db.get_prescriptions(p[0])
                if history:
                    for pres in history[-2:]:  # Show last 2 records
                        st.info(f"Date: {pres[9]} | Issue: {pres[6]} | Medicines: {pres[3]} | Money Pending: ${pres[8]}")
                else:
                    st.write("No prescription history found.")
        else:
            st.write("No patients found.")



    with tab2:
        st.header("📦 Inventory Management (Medicines & Spectacles)")
        inventory_db = get_inventory_dict()
        st.table(pd.DataFrame(list(inventory_db.items()), columns=["Item", "Quantity"]))

        st.subheader("Add/Buy Medicine to Inventory")
        new_med = st.text_input("Medicine Name to Add/Buy", key="inv_med")
        new_qty = st.number_input("Quantity to Add/Buy", min_value=1, value=1, key="inv_qty")
        if st.button("Add/Buy Medicine", key="inv_add_med"):
            add_or_update_inventory(new_med, new_qty)
            st.success(f"Added {new_qty} of {new_med} to inventory.")

        st.subheader("Add/Buy Spectacle to Inventory")
        spectacle_name = st.text_input("Spectacle Name to Add/Buy", key="inv_spec")
        spectacle_qty = st.number_input("Spectacle Quantity to Add/Buy", min_value=1, value=1, key="inv_spec_qty")
        if st.button("Add/Buy Spectacle", key="inv_add_spec"):
            add_or_update_inventory(spectacle_name, spectacle_qty)
            st.success(f"Added {spectacle_qty} of {spectacle_name} to inventory.")

        st.info("For medicine suggestions, refer to reputable sites like drugs.com or medlineplus.gov. You can add any medicine or spectacle needed for eye specialists. The agent will keep the inventory updated.")
        
        # Market Data Integration
        st.markdown("---")
        st.subheader("📊 Market Data & Auto-Update")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Update from Market", type="primary"):
                if LANGGRAPH_AVAILABLE and market_updater:
                    with st.spinner("Fetching latest market data..."):
                        result = market_updater.update_inventory_from_market()
                        if result:
                            st.success("Inventory updated with latest market data!")
                            st.rerun()
                        else:
                            st.error("Failed to update inventory")
                else:
                    st.warning("LangGraph not available. Install with: pip install langgraph")
        
        with col2:
            if st.button("⚠️ Check Low Stock"):
                if LANGGRAPH_AVAILABLE and market_updater:
                    low_stock = market_updater.check_low_stock_alerts()
                    if low_stock:
                        st.warning(f"Low stock items: {len(low_stock)}")
                        for item, qty in low_stock:
                            st.write(f"- {item}: {qty} remaining")
                    else:
                        st.success("All items have sufficient stock")
                else:
                    st.warning("LangGraph not available")
        
        with col3:
            if st.button("📈 Market Trends"):
                if LANGGRAPH_AVAILABLE and market_updater:
                    trends = market_updater.get_market_trends()
                    st.json(trends)
                else:
                    st.warning("LangGraph not available")

    # --- AI Agent Tools Tab ---
    with tab4:
        st.header("🤖 AI Agent Tools")
        st.markdown("*LangGraph-powered intelligent tools for automated tasks*")
        
        if not LANGGRAPH_AVAILABLE:
            st.error("🚀 LangGraph not available. Install with: pip install langgraph langchain langchain-core")
            st.info("The AI Agent Tools require LangGraph to be installed. Please install the dependencies and restart the application.")
            return
        
        # Agent Task Executor
        st.subheader("🚀 Agent Task Executor")
        task_options = [
            "Generate PDF for patient",
            "Fetch latest market data",
            "Update inventory from market",
            "Check low stock items",
            "Get patient data summary",
            "Custom task"
        ]
        
        selected_task = st.selectbox("Select Agent Task", task_options)
        
        if selected_task == "Custom task":
            custom_task = st.text_input("Enter custom task description")
            task_to_execute = custom_task
        else:
            task_to_execute = selected_task
        
        # Task context inputs
        if "patient" in selected_task.lower():
            patient_id = st.number_input("Patient ID", min_value=1, value=1)
            context = {"patient_id": patient_id}
        else:
            context = {}
        
        # Execute task
        if st.button("▶️ Execute Agent Task", type="primary"):
            if task_to_execute and mau_agent:
                with st.spinner(f"Agent executing: {task_to_execute}..."):
                    try:
                        result = mau_agent.execute_task(task_to_execute, context)
                        st.success("Task completed successfully!")
                        st.json(result)
                    except Exception as e:
                        st.error(f"Agent task failed: {str(e)}")
            else:
                st.warning("Please enter a task description")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Auto-Generate PDF"):
                if mau_agent and 'patient_id' in st.session_state:
                    patient_data = {
                        'patient_name': st.session_state.get('patient_name', ''),
                        'age': st.session_state.get('age', 0),
                        'gender': st.session_state.get('gender', ''),
                        'prescription': st.session_state.get('prescription', {}),
                        'advice': st.session_state.get('advice', ''),
                        'rx_table': st.session_state.get('rx_table', {}),
                        'recommendations': st.session_state.get('recommendations', [])
                    }
                    result = mau_agent.generate_patient_pdf(patient_data)
                    st.success(result)
                elif not mau_agent:
                    st.warning("LangGraph agent not available")
                else:
                    st.warning("No patient selected. Please go to Prescription tab first.")
        
        with col2:
            if st.button("🔄 Smart Inventory Update"):
                if mau_agent:
                    result = mau_agent.update_inventory_from_market()
                    st.info(result)
                else:
                    st.warning("LangGraph agent not available")
        
        with col3:
            if st.button("📈 Stock Analysis"):
                if mau_agent:
                    result = mau_agent.check_low_stock()
                    st.info(result)
                else:
                    st.warning("LangGraph agent not available")
        
        # Agent Status
        st.markdown("---")
        st.subheader("📊 Agent Status")
        
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.metric("Tools Available", "4")
            st.write("- PDF Generator")
            st.write("- Market Data Fetcher")
            st.write("- Inventory Manager")
            st.write("- Patient Data Reader")
        
        with status_col2:
            st.metric("Agent Status", "Active ✅")
            st.write("- LangGraph: Enabled")
            st.write("- Auto-updates: Running")
            st.write("- Market sync: Every 6h")
            st.write("- Stock alerts: Every 2h")

if __name__ == "__main__":
    main()