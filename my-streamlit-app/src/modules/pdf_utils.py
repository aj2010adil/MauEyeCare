"""
pdf_utils.py
PDF generation utilities for MauEyeCare.
"""
from fpdf import FPDF
from io import BytesIO

def generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name, age, gender, advice, rx_table, recommendations):
    pdf = FPDF()
    pdf.add_page()
    # Colors
    blue = (41, 171, 226)
    gray = (230, 230, 230)
    # Draw blue sidebar
    pdf.set_fill_color(*blue)
    pdf.rect(10, 10, 20, 270, 'F')
    # Header - Doctor info (left)
    pdf.set_xy(32, 12)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(80, 10, doctor_name, ln=0)
    # Contact info (right, blue bubble)
    pdf.set_xy(130, 12)
    pdf.set_fill_color(*blue)
    pdf.set_text_color(255,255,255)
    pdf.set_font('Arial', '', 12)
    pdf.cell(65, 10, '123-456-7890   444-666-8899', 0, 0, 'C', fill=True)
    pdf.set_text_color(0,0,0)
    # Subtitle
    pdf.set_xy(32, 20)
    pdf.set_font('Arial', '', 10)
    pdf.cell(80, 6, 'Optometrist & Eye Specialist', ln=2)
    pdf.set_x(32)
    pdf.cell(80, 6, 'Department of Ophthalmology', ln=2)
    # Patient info box (left)
    pdf.set_xy(15, 40)
    pdf.set_font('Arial', '', 10)
    pdf.cell(20, 7, 'Name:', ln=2)
    pdf.cell(20, 7, 'Age:', ln=2)
    pdf.cell(20, 7, 'Sex:', ln=2)
    pdf.cell(20, 7, 'Adv:', ln=2)
    # Fill patient info lines
    pdf.set_xy(30, 40)
    pdf.cell(60, 7, str(patient_name), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(age), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(gender), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(advice), ln=2)
    # Recommendations (left)
    pdf.set_xy(15, 80)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 7, 'Recommendations', ln=2)
    pdf.set_font('Arial', '', 9)
    rec_opts = [
        "Single Vision", "Bifocal", "Trifocal", "Progressive", "Photochromatic", "Tint", "Polarized", "AR Coat", "HiIndex"
    ]
    y = pdf.get_y()
    for rec in rec_opts:
        mark = '[x]' if rec in recommendations else '[ ]'
        pdf.set_x(17)
        pdf.cell(10, 5, mark, 0, 0)
        pdf.cell(30, 5, rec, ln=1)
    # Rx and table (right)
    pdf.set_xy(80, 40)
    pdf.set_font('Arial', 'B', 28)
    pdf.cell(20, 12, 'Rx', ln=0)
    # Date
    pdf.set_xy(160, 40)
    pdf.set_font('Arial', '', 10)
    from datetime import datetime
    pdf.cell(30, 7, f'Date: {datetime.now().strftime("%d-%m-%Y")}', ln=0)
    # Rx Table
    pdf.set_xy(80, 55)
    pdf.set_font('Arial', '', 10)
    pdf.cell(15, 8, '', 0, 0)
    pdf.cell(25, 8, 'Sphere', 1, 0, 'C')
    pdf.cell(25, 8, 'Cylinder', 1, 0, 'C')
    pdf.cell(25, 8, 'Axis', 1, 0, 'C')
    pdf.cell(25, 8, 'Prism', 1, 1, 'C')
    for eye in ['OD', 'OS']:
        row = rx_table.get(eye, {'Sphere':'', 'Cylinder':'', 'Axis':'', 'Prism':''})
        pdf.set_x(80)
        pdf.cell(15, 8, eye, 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Sphere','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Cylinder','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Axis','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Prism','')), 1, 1, 'C')
    # Medicines (below Rx table)
    pdf.set_xy(80, 85)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'Medicines:', ln=1)
    pdf.set_font('Arial', '', 10)
    for med, qty in prescription.items():
        pdf.set_x(85)
        pdf.cell(0, 6, f'- {med}: {qty}', ln=1)
    # Dosage and Eye Test
    pdf.set_x(80)
    pdf.cell(0, 6, f'Dosage: {dosage}', ln=1)
    pdf.set_x(80)
    pdf.cell(0, 6, f'Eye Test: {eye_test}', ln=1)
    # Footer
    pdf.set_y(265)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(0,0,0)
    pdf.cell(0, 6, '123-456-7890, 444-666-8899', ln=1, align='C')
    pdf.cell(0, 6, 'Street address here, City Suite, Zip Code', ln=1, align='C')
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)
