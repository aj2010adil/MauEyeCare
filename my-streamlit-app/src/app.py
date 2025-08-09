
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

import requests
import importlib.util


grok_key = None
try:
    import sys, os
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

    st.header("Doctor & Patient Details")
    doctor_name = st.text_input("Doctor Name", "Dr. Smith")
    patient_name = st.text_input("Patient Name", "John Doe")

    st.header("1. Select Medicines")
    med_options = list(inventory.keys())
    selected_meds = st.multiselect("Choose medicines", med_options)
    prescription = {}
    out_of_stock = []
    for med in selected_meds:
        max_qty = inventory[med]
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
            st.success("Prescription approved. Please use the download button above to print.")

if __name__ == "__main__":
    main()