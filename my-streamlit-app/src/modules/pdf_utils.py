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
    # --- HEADER ---
    # Hospital Name
    pdf.set_xy(32, 12)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(120, 10, 'MauEye Care Hospital', ln=0)
    pdf.set_text_color(0,0,0)
    # Contact info (right, blue bubble)
    pdf.set_xy(140, 12)
    pdf.set_fill_color(*blue)
    pdf.set_text_color(255,255,255)
    pdf.set_font('Arial', '', 11)
    pdf.cell(55, 10, 'Ph: 92356-47410', 0, 0, 'C', fill=True)
    pdf.set_text_color(0,0,0)
    # Tagline
    pdf.set_xy(32, 20)
    pdf.set_font('Arial', 'I', 11)
    pdf.cell(120, 6, 'Advanced Eye & Vision Care Center', ln=2)
    # Address, website, email
    pdf.set_x(32)
    pdf.set_font('Arial', '', 9)
    pdf.cell(120, 5, 'MubarakPur, Azamgarh | www.maueyeycare.com | info@maueyeycare.com', ln=2)
    # Doctor info and Reg No
    pdf.set_x(32)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(120, 5, f'{doctor_name}, B.Sc. Optometry', ln=2)
    pdf.set_x(32)
    pdf.set_font('Arial', '', 9)
    pdf.cell(120, 5, 'Optometrist & Eye Specialist | Reg. No.: UP-123456', ln=2)
    # Line below header
    pdf.set_draw_color(41, 171, 226)
    pdf.set_line_width(0.8)
    pdf.line(32, 38, 200, 38)
    pdf.set_line_width(0.2)
    # Patient info box (left)
    pdf.set_xy(15, 45)
    pdf.set_font('Arial', '', 10)
    pdf.cell(20, 7, 'Name:', ln=2)
    pdf.cell(20, 7, 'Age:', ln=2)
    pdf.cell(20, 7, 'Sex:', ln=2)
    pdf.cell(20, 7, 'Adv:', ln=2)
    # Fill patient info lines
    pdf.set_xy(30, 45)
    pdf.cell(60, 7, str(patient_name), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(age), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(gender), ln=2)
    pdf.set_x(30)
    pdf.cell(60, 7, str(advice), ln=2)
    # Recommendations (left)
    pdf.set_xy(15, 90)
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
    pdf.set_xy(90, 45)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(20, 12, 'Rx', ln=0)
    # Date
    pdf.set_xy(160, 45)
    pdf.set_font('Arial', '', 10)
    from datetime import datetime
    pdf.cell(30, 7, f'Date: {datetime.now().strftime("%d-%m-%Y")}', ln=0)
    # Rx Table
    pdf.set_xy(90, 60)
    pdf.set_font('Arial', '', 10)
    pdf.cell(15, 8, '', 0, 0)
    pdf.cell(25, 8, 'Sphere', 1, 0, 'C')
    pdf.cell(25, 8, 'Cylinder', 1, 0, 'C')
    pdf.cell(25, 8, 'Axis', 1, 0, 'C')
    pdf.cell(25, 8, 'Prism', 1, 1, 'C')
    for eye in ['OD', 'OS']:
        row = rx_table.get(eye, {'Sphere':'', 'Cylinder':'', 'Axis':'', 'Prism':''})
        pdf.set_x(90)
        pdf.cell(15, 8, eye, 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Sphere','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Cylinder','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Axis','')), 1, 0, 'C')
        pdf.cell(25, 8, str(row.get('Prism','')), 1, 1, 'C')
    # Medicines (below Rx table)
    pdf.set_xy(90, 90)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'Medicines:', ln=1)
    pdf.set_font('Arial', '', 10)
    for med, qty in prescription.items():
        pdf.set_x(95)
        pdf.cell(0, 6, f'- {med}: {qty}', ln=1)
    # Dosage and Eye Test
    pdf.set_x(90)
    pdf.cell(0, 6, f'Dosage: {dosage}', ln=1)
    pdf.set_x(90)
    pdf.cell(0, 6, f'Eye Test: {eye_test}', ln=1)
    # Signature line
    pdf.set_y(250)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, 'Doctor Signature: ___________________________', ln=1, align='R')
    # Footer
    pdf.set_y(265)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 6, 'MauEye Care Hospital | MubarakPur, Azamgarh | www.maueyeycare.com | info@maueyeycare.com', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)
