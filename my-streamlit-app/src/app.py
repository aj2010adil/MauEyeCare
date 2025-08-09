
# MauEyeCare Main App
# Entry point for Streamlit UI. Uses modules for PDF, AI, and inventory logic.

import streamlit as st
import pandas as pd
from io import BytesIO
import sys, os
sys.path.append(os.path.dirname(__file__))
import db
from fpdf import FPDF
from modules.pdf_utils import generate_pdf
from modules.ai_utils import get_grok_suggestion
from modules.inventory_utils import get_inventory_dict, add_or_update_inventory, reduce_inventory

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

    st.title("MauEyeCare - Prescription & Inventory Management")

    tab1, tab2, tab3 = st.tabs(["Prescription & Patient", "Inventory Management", "Patient History"])

    # --- Prescription & Patient Tab ---
    with tab1:
        st.header("Patient Information")
        # --- Patient Form ---
        with st.form("patient_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            patient_name = f"{first_name} {last_name}".strip()
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Mobile Number")
            advice = st.text_area("Advice/Notes")
            patient_issue = st.text_area("Patient Issue/Complaint (Describe symptoms, e.g. blurry vision, redness, etc.)")
            # RX Table
            st.markdown("**Rx Table** (Fill for OD and OS)")
            rx_table = {}
            for eye in ['OD', 'OS']:
                st.markdown(f"**{eye}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    sphere = st.text_input(f"Sphere {eye}", key=f"sphere_{eye}")
                with col2:
                    cylinder = st.text_input(f"Cylinder {eye}", key=f"cylinder_{eye}")
                with col3:
                    axis = st.text_input(f"Axis {eye}", key=f"axis_{eye}")
                with col4:
                    prism = st.text_input(f"Prism {eye}", key=f"prism_{eye}")
                rx_table[eye] = {"Sphere": sphere, "Cylinder": cylinder, "Axis": axis, "Prism": prism}
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
                st.session_state['show_prescription_pdf'] = True

        # --- Show download buttons after form submission ---
        if st.session_state.get('show_prescription_pdf', False):
            patient_id = st.session_state['patient_id']
            patient_name = st.session_state['patient_name']
            age = st.session_state['age']
            gender = st.session_state['gender']
            advice = st.session_state['advice']
            rx_table = st.session_state['rx_table']
            recommendations = st.session_state['recommendations']
            st.success(f"Patient saved/selected: {patient_name}")
            st.markdown("---")
            st.subheader("Review & Print Basic Prescription for Selected Patient")
            pdf_file = generate_pdf(
                {}, # No medicines yet
                '', # No dosage
                '', # No eye test
                "Dr Danish",
                patient_name,
                age,
                gender,
                advice,
                rx_table,
                recommendations
            )
            st.download_button(
                label="Download/Print Basic Prescription PDF",
                data=pdf_file,
                file_name=f"prescription_{patient_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"pdf_btn_basic_{patient_id}"
            )
            # --- Add medicine selection and prescription PDF generation ---
            st.markdown("---")
            st.subheader("Add Medicines and Print Prescription")
            inventory_db = get_inventory_dict()
            med_options = list(inventory_db.keys())
            selected_meds = st.multiselect("Choose medicines/spectacles for this patient", med_options, key=f"meds_{patient_id}")
            prescription = {}
            out_of_stock = []
            for med in selected_meds:
                max_qty = inventory_db[med]
                qty = st.number_input(f"Quantity for {med} (In stock: {max_qty})", min_value=1, max_value=10, value=1, key=f"qty_{patient_id}_{med}")
                if max_qty >= qty:
                    prescription[med] = qty
                else:
                    out_of_stock.append(med)
            if out_of_stock:
                st.warning(f"Out of stock or insufficient: {', '.join(out_of_stock)}. Please add to inventory later.")
            if st.button("Generate Prescription PDF for Patient", key=f"genpdf_{patient_id}"):
                pdf_file2 = generate_pdf(
                    prescription,
                    '',
                    '',
                    "Dr Danish",
                    patient_name,
                    age,
                    gender,
                    advice,
                    rx_table,
                    recommendations
                )
                st.session_state[f'pdf_file2_{patient_id}'] = pdf_file2
                st.session_state[f'pdf_file2_ready_{patient_id}'] = True
            if st.session_state.get(f'pdf_file2_ready_{patient_id}', False):
                pdf_file2 = st.session_state.get(f'pdf_file2_{patient_id}')
                st.success("Prescription PDF generated. Please review below.")
                st.download_button(
                    label="Download/Print Prescription PDF",
                    data=pdf_file2,
                    file_name=f"prescription_{patient_name.replace(' ', '_')}_with_meds.pdf",
                    mime="application/pdf",
                    key=f"pdf_btn_full_{patient_id}"
                )
    # --- Patient History Tab ---
    with tab3:
        st.header("Patient History & Search")
        patients = db.get_patients()
        search_mobile = st.text_input("Search by Mobile Number", key="history_search_mobile")
        search_name = st.text_input("Search by Name", key="history_search_name")
        filtered = [p for p in patients if (search_mobile in p[4]) and (search_name.lower() in p[1].lower())]
        st.write(f"Found {len(filtered)} patient(s)")
        for p in filtered:
            st.markdown(f"**Name:** {p[1]} | **Age:** {p[2]} | **Gender:** {p[3]} | **Mobile:** {p[4]}")
            history = db.get_prescriptions(p[0])
    with tab3:
        st.header("Patient History & Search")
        patients = db.get_patients()
        search_mobile = st.text_input("Search by Mobile Number")
        search_name = st.text_input("Search by Name")
        # Merge patients by name and mobile
        merged = {}
        for p in patients:
            key = (p[1].strip().lower(), p[4].strip())
            if key not in merged:
                merged[key] = list(p)
            else:
                # If duplicate, keep the earliest age/gender
                merged[key][2] = min(merged[key][2], p[2])
        merged_patients = list(merged.values())
        st.write(f"Found {len(merged_patients)} patient(s)")
        if merged_patients:
            patient_df = pd.DataFrame(merged_patients, columns=["ID", "Name", "Age", "Gender", "Mobile"])
            st.dataframe(patient_df)
            st.download_button(
                label="Download Patient Data (Excel)",
                data=to_excel(patient_df),
                file_name="patients.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # Upload patient data Excel
            uploaded_patients = st.file_uploader("Upload Patient Data (Excel)", type=["xlsx"], key="upload_patients")
            if uploaded_patients:
                df_pat = pd.read_excel(uploaded_patients)
                for _, row in df_pat.iterrows():
                    db.add_patient(row["Name"], int(row["Age"]), row["Gender"], str(row["Mobile"]))
                st.success("Uploaded and merged patient data.")

            # Show prescription history for selected patient
            selected_patient = st.selectbox("Select patient to view prescription history", patient_df["ID"])
            history = db.get_prescriptions(selected_patient)
            if history:
                hist_df = pd.DataFrame(history, columns=["ID", "PatientID", "Doctor", "Medicines", "Dosage", "EyeTest", "Issue", "MoneyGiven", "MoneyPending", "Date"])
                hist_df = hist_df.sort_values(by="Date", ascending=False)
                # Show all columns including Date, Doctor, Issue, Medicines, Dosage, EyeTest, MoneyGiven, MoneyPending
                show_cols = ["Date", "Doctor", "Issue", "Medicines", "Dosage", "EyeTest", "MoneyGiven", "MoneyPending"]
                # Add a prominent action button for each row
                def render_action_buttons(row):
                    import streamlit as st
                    try:
                        meds = eval(row['Medicines']) if isinstance(row['Medicines'], str) and row['Medicines'].startswith('{') else row['Medicines']
                    except Exception:
                        meds = {}
                    pdf_file = generate_pdf(
                        meds if isinstance(meds, dict) else {},
                        row['Dosage'],
                        row['EyeTest'],
                        row['Doctor'],
                        patient_df[patient_df['ID'] == row['PatientID']]['Name'].values[0] if 'Name' in patient_df.columns else '',
                        0,
                        '',
                        '',
                        {},
                        []
                    )
                    st.download_button(
                        label=f"Download/Print PDF",
                        data=pdf_file,
                        file_name=f"prescription_{row['Date']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_btn_{row['ID']}"
                    )

                # Show table with action buttons
                for idx, row in hist_df.iterrows():
                    st.write(":heavy_minus_sign:"*30)
                    st.markdown(f"**Date:** {row['Date']} | **Doctor:** {row['Doctor']} | **Issue:** {row['Issue']} | **Medicines:** {row['Medicines']} | **Dosage:** {row['Dosage']} | **Money Given:** {row['MoneyGiven']} | **Money Pending:** {row['MoneyPending']}")
                    render_action_buttons(row)
                st.download_button(
                    label="Download Prescription History (Excel)",
                    data=to_excel(hist_df[show_cols]),
                    file_name="prescription_history.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                # Upload prescription history Excel
                uploaded_presc = st.file_uploader("Upload Prescription History (Excel)", type=["xlsx"], key="upload_presc")
                if uploaded_presc:
                    df_presc = pd.read_excel(uploaded_presc)
                    for _, row in df_presc.iterrows():
                        db.add_prescription(
                            row["PatientID"],
                            row["Doctor"],
                            {'medicines': row["Medicines"], 'dosage': row["Dosage"], 'eye_test': row["EyeTest"], 'issue': row["Issue"], 'money_given': row["MoneyGiven"], 'money_pending': row["MoneyPending"]},
                            row["Dosage"],
                            row["EyeTest"]
                        )
                    st.success("Uploaded and merged prescription history.")
            else:
                st.write("No prescription history.")
        else:
            st.write("No patients found.")
            if history:
                for pres in history:
                    st.markdown(f"- **Date:** {pres[6]} | **Doctor:** {pres[2]} | **Meds:** {pres[3]} | **Dosage:** {pres[4]} | **Eye Test:** {pres[5]}")
            else:
                st.write("No history found.")

            st.header("1. Select Medicines/Spectacles")
            inventory_db = get_inventory_dict()
            med_options = list(inventory_db.keys())
            # Agent suggestion for medicines based on patient issue
            if patient_issue:
                if st.button("Get Agent Medicine Suggestions for Issue"):
                    with st.spinner("Agent is suggesting medicines for the issue..."):
                        import perplexity_config
                        grok_key = getattr(perplexity_config, "grok_key", None)
                        suggestion = get_grok_suggestion(grok_key, "Dr Danish", patient_name, [], "", patient_issue)
                    st.info(f"Agent Suggestion: {suggestion}")
            selected_meds = st.multiselect("Choose medicines/spectacles", med_options)
            prescription = {}
            out_of_stock = []
            for med in selected_meds:
                max_qty = inventory_db[med]
                qty = st.number_input(f"Quantity for {med} (In stock: {max_qty})", min_value=1, max_value=10, value=1, key=med)
                if max_qty >= qty:
                    prescription[med] = qty
                else:
                    out_of_stock.append(med)

            if out_of_stock:
                st.warning(f"Out of stock or insufficient: {', '.join(out_of_stock)}. Please add to inventory later.")

            st.header("2. Dosage Details")
            dosage = st.text_area("Enter dosage instructions")

            st.header("3. Eye Testing Details")
            eye_test = st.text_area("Enter eye testing details")

            st.header("4. Visit Details")
            issue = st.text_area("Patient Issue/Complaint for this visit")
            money_given = st.number_input("Money Given by Patient", min_value=0.0, value=0.0, step=0.01)
            money_pending = st.number_input("Money Pending (Due)", min_value=0.0, value=0.0, step=0.01)

            st.header("AI Suggestions")
            if st.button("Get Grok AI Suggestions"):
                with st.spinner("Contacting Grok AI for suggestions..."):
                    import perplexity_config
                    grok_key = getattr(perplexity_config, "grok_key", None)
                    suggestion = get_grok_suggestion(grok_key, "Dr Danish", patient_name, selected_meds, dosage, eye_test)
                st.info(suggestion)

            st.header("5. Review & Generate Prescription PDF")
            if st.button("Generate PDF for Review"):
                if not prescription:
                    st.error("Please select at least one medicine with available stock.")
                else:
                    pdf_file = generate_pdf(
                        prescription, dosage, eye_test, "Dr Danish", patient_name, age, gender, advice, rx_table, recommendations
                    )
                    st.success("PDF generated. Please review below.")
                    st.download_button(
                        label="Download Prescription PDF",
                        data=pdf_file,
                        file_name="prescription.pdf",
                        mime="application/pdf"
                    )
                    st.session_state['pdf_ready'] = True
            else:
                st.session_state['pdf_ready'] = False

            if st.session_state.get('pdf_ready', False):
                st.header("6. Approve & Print Prescription")
                if st.button("Approve and Print (Download)"):
                    # Store all visit info in prescription
                    pres_data = {
                        'medicines': str(prescription),
                        'dosage': dosage,
                        'eye_test': eye_test,
                        'issue': issue,
                        'money_given': money_given,
                        'money_pending': money_pending
                    }
                    db.add_prescription(patient_id, "Dr Danish", pres_data, dosage, eye_test)
                    for med, qty in prescription.items():
                        reduce_inventory(med, qty)
                    st.success("Prescription approved, saved, and inventory updated. Please use the download button above to print.")

    with tab2:
        st.header("Inventory Management (Medicines & Spectacles)")
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

if __name__ == "__main__":
    main()