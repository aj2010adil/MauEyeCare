
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import requests
import importlib.util
import sys, os
sys.path.append(os.path.dirname(__file__))
import db

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

def generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Prescription', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Doctor: {doctor_name}', ln=True)
    pdf.cell(0, 10, f'Patient: {patient_name}', ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, 'Medicines:', ln=True)
    for med, qty in prescription.items():
        pdf.cell(0, 10, f'- {med}: {qty}', ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f'Dosage Details: {dosage}', ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f'Eye Test Details: {eye_test}', ln=True)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

def main():

    st.title("MauEyeCare - Prescription & Inventory Management")

    st.header("Patient Information")
    with st.form("patient_form"):
        patient_name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact Info")
        doctor_name = st.text_input("Doctor Name", "Dr. Smith")
        submitted = st.form_submit_button("Save/Select Patient")
        if submitted:
            patient_id = db.add_patient(patient_name, age, gender, contact)
            st.session_state['patient_id'] = patient_id
            st.success(f"Patient saved/selected: {patient_name}")

    patient_id = st.session_state.get('patient_id', None)
    if patient_id:
        st.info(f"Current patient ID: {patient_id}")
        # Show patient history
        st.subheader("Patient Prescription History")
        history = db.get_prescriptions(patient_id)
        if history:
            for pres in history:
                st.markdown(f"- **Date:** {pres[6]} | **Doctor:** {pres[2]} | **Meds:** {pres[3]} | **Dosage:** {pres[4]} | **Eye Test:** {pres[5]}")
        else:
            st.write("No history found.")

        st.header("1. Select Medicines")
        inventory_db = {row[0]: row[1] for row in db.get_inventory()}
        med_options = list(inventory_db.keys())
        selected_meds = st.multiselect("Choose medicines", med_options)
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

        st.header("AI Suggestions")
        if st.button("Get Grok AI Suggestions"):
            with st.spinner("Contacting Grok AI for suggestions..."):
                suggestion = get_grok_suggestion(doctor_name, patient_name, selected_meds, dosage, eye_test)
            st.info(suggestion)

        st.header("4. Review & Generate Prescription PDF")
        if st.button("Generate PDF for Review"):
            if not prescription:
                st.error("Please select at least one medicine with available stock.")
            else:
                pdf_file = generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name)
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
            st.header("5. Approve & Print Prescription")
            if st.button("Approve and Print (Download)"):
                # Save prescription to DB
                db.add_prescription(patient_id, doctor_name, str(prescription), dosage, eye_test)
                # Reduce inventory in DB
                for med, qty in prescription.items():
                    db.reduce_inventory(med, qty)
                st.success("Prescription approved, saved, and inventory updated. Please use the download button above to print.")

if __name__ == "__main__":
    main()