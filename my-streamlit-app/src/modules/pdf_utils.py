"""
pdf_utils.py
PDF generation utilities for MauEyeCare.
"""
from fpdf import FPDF
from io import BytesIO

def generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name, age, gender, advice, rx_table, recommendations):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, doctor_name, ln=1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 7, 'Optometrist & Eye Specialist', ln=1)
    pdf.cell(0, 7, 'Department of Ophthalmology', ln=1)
    pdf.cell(0, 7, 'Mob: 9235647410', ln=1)
    pdf.cell(0, 7, 'MubarakPur, Azamgarh', ln=1)
    pdf.ln(2)
    # Patient info
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f'Name: {patient_name}', ln=1)
    pdf.cell(0, 7, f'Age: {age}', ln=1)
    pdf.cell(0, 7, f'Sex: {gender}', ln=1)
    pdf.cell(0, 7, f'Adv: {advice}', ln=1)
    pdf.ln(2)
    # RX Table
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Rx:', ln=1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(20, 7, '', 0)
    pdf.cell(25, 7, 'Sphere', 1)
    pdf.cell(25, 7, 'Cylinder', 1)
    pdf.cell(25, 7, 'Axis', 1)
    pdf.cell(25, 7, 'Prism', 1, ln=1)
    for eye in ['OD', 'OS']:
        row = rx_table.get(eye, {'Sphere':'', 'Cylinder':'', 'Axis':'', 'Prism':''})
        pdf.cell(20, 7, eye, 1)
        pdf.cell(25, 7, row.get('Sphere',''), 1)
        pdf.cell(25, 7, row.get('Cylinder',''), 1)
        pdf.cell(25, 7, row.get('Axis',''), 1)
        pdf.cell(25, 7, row.get('Prism',''), 1, ln=1)
    pdf.ln(2)
    # Recommendations
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Recommendations:', ln=1)
    pdf.set_font('Arial', '', 10)
    for rec in recommendations:
        pdf.cell(0, 7, f'- {rec}', ln=1)
    pdf.ln(2)
    # Medicines
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Medicines:', ln=1)
    pdf.set_font('Arial', '', 10)
    for med, qty in prescription.items():
        pdf.cell(0, 7, f'- {med}: {qty}', ln=1)
    pdf.ln(2)
    # Dosage and Eye Test
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 7, f'Dosage Details: {dosage}', ln=1)
    pdf.cell(0, 7, f'Eye Test Details: {eye_test}', ln=1)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)
