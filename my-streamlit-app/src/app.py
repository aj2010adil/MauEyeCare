import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

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