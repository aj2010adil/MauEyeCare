"""
pdf_utils.py
PDF generation utilities for MauEyeCare.
"""
from fpdf import FPDF
from io import BytesIO
import os
import sys

def generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name, age, gender, advice, rx_table, recommendations):
    pdf = FPDF()
    pdf.add_page()
    
    # Try to load Unicode font for checkboxes
    unicode_font = None
    try:
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        dejavu_path = os.path.join(font_dir, 'DejaVuSans.ttf')
        arialuni_path = os.path.join(font_dir, 'arialuni.ttf')
        
        if os.path.exists(dejavu_path):
            pdf.add_font('DejaVuSans', '', dejavu_path, uni=True)
            unicode_font = 'DejaVuSans'
        elif os.path.exists(arialuni_path):
            pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            unicode_font = 'ArialUnicode'
    except Exception as e:
        print(f"[WARNING] Could not load Unicode font: {e}", file=sys.stderr)
    
    # Colors
    blue = (41, 171, 226)
    
    # Always set a font before any cell/text
    pdf.set_font('Arial', 'B', 18)
    
    # Draw blue sidebar
    pdf.set_fill_color(*blue)
    pdf.rect(10, 10, 20, 270, 'F')
    
    # --- HEADER ---
    pdf.set_xy(32, 12)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(120, 10, 'Mau Eye Care Optical Center', ln=0)
    pdf.set_text_color(0,0,0)
    
    # Contact info
    pdf.set_xy(140, 12)
    pdf.set_fill_color(*blue)
    pdf.set_text_color(255,255,255)
    pdf.set_font('Arial', '', 11)
    pdf.cell(55, 10, 'Ph: 92356-47410', 0, 0, 'C', fill=True)
    pdf.set_text_color(0,0,0)
    
    # Tagline and address
    pdf.set_xy(32, 20)
    pdf.set_font('Arial', 'I', 11)
    pdf.cell(120, 6, 'Premium Eye Care & Optical Solutions', ln=2)
    pdf.set_x(32)
    pdf.set_font('Arial', '', 9)
    pdf.cell(120, 5, 'MubarakPur, Azamgarh | www.maueyeycare.com | info@maueyeycare.com', ln=2)
    
    # Doctor info
    pdf.set_x(32)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(120, 5, f'{doctor_name}, B.Sc. Optometry', ln=2)
    pdf.set_x(32)
    pdf.set_font('Arial', '', 9)
    pdf.cell(120, 5, 'Optometrist & Eye Specialist | Reg. No.: UP-123456', ln=2)
    
    # Header line
    pdf.set_draw_color(41, 171, 226)
    pdf.set_line_width(0.8)
    pdf.line(32, 38, 200, 38)
    pdf.set_line_width(0.2)

    # --- PATIENT INFO ---
    pdf.set_xy(15, 45)
    pdf.set_font('Arial', '', 10)
    pdf.cell(20, 7, 'Name:', ln=0)
    pdf.set_x(30)
    pdf.cell(60, 7, str(patient_name), ln=1)
    pdf.set_xy(15, 52)
    pdf.cell(20, 7, 'Age:', ln=0)
    pdf.set_x(30)
    pdf.cell(60, 7, str(age), ln=1)
    pdf.set_xy(15, 59)
    pdf.cell(20, 7, 'Sex:', ln=0)
    pdf.set_x(30)
    pdf.cell(60, 7, str(gender), ln=1)
    pdf.set_xy(15, 66)
    pdf.cell(20, 7, 'Advice:', ln=0)
    pdf.set_x(30)
    pdf.cell(60, 7, str(advice), ln=1)

    # Recommendations with checkboxes
    if recommendations:
        pdf.set_xy(15, 75)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 7, 'Recommendations:', ln=1)
        
        y_pos = 82
        for rec in recommendations:
            pdf.set_xy(20, y_pos)
            
            # Try Unicode checkbox first, fallback to ASCII
            if unicode_font:
                try:
                    pdf.set_font(unicode_font, '', 10)
                    pdf.cell(5, 6, '☑', ln=0)  # Unicode checked box
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f' {rec}', ln=1)
                except:
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f'[x] {rec}', ln=1)
            else:
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f'[x] {rec}', ln=1)
            y_pos += 6

    # Rx Table
    pdf.set_xy(90, 45)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(20, 8, 'Rx:', ln=0)
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(90, 53)
    for eye in ['OD', 'OS']:
        row = rx_table.get(eye, {'Sphere':'', 'Cylinder':'', 'Axis':'', 'Prism':'', 'NearVision':'', 'GlassType':'', 'GlassTint':''})
        rx_str = f"{eye}: Sph {row.get('Sphere','')} Cyl {row.get('Cylinder','')} Axis {row.get('Axis','')} Near {row.get('NearVision','')}"
        pdf.cell(0, 6, rx_str, ln=1)
        glass_str = f"Type: {row.get('GlassType','')} Tint: {row.get('GlassTint','')}"
        pdf.set_x(90)
        pdf.cell(0, 6, glass_str, ln=1)

    # Medicines
    if prescription:
        pdf.set_xy(90, 65)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, 'Medicines:', ln=1)
        pdf.set_font('Arial', '', 10)
        meds_line = '; '.join([f"{med} ({qty})" for med, qty in prescription.items()])
        pdf.set_x(90)
        pdf.multi_cell(0, 6, meds_line)

    # Dosage and Eye Test
    pdf.set_x(90)
    pdf.cell(0, 6, f"Dosage: {dosage}", ln=1)
    pdf.set_x(90)
    pdf.cell(0, 6, f"Eye Test: {eye_test}", ln=1)

    # Signature
    pdf.set_y(250)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, 'Doctor Signature: ___________________________', ln=1, align='R')

    # Footer
    pdf.set_y(265)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 6, 'Mau Eye Care Optical Center | MubarakPur, Azamgarh | www.maueyeycare.com | info@maueyeycare.com', ln=1, align='C')
    pdf.set_text_color(0,0,0)

    # --- BACK PAGE: Hospital Info ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Hospital name in English
    pdf.set_xy(20, 30)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 12, 'Mau Eye Care Optical Center', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    
    # Hospital details in English
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 8, 'Premium Eye Care & Optical Solutions\nMubarakPur, Azamgarh\nPhone: 92356-47410\nWebsite: www.maueyeycare.com\nEmail: info@maueyeycare.com', align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Services Offered:', ln=1, align='C')
    pdf.set_font('Arial', '', 10)
    services = ['Eye Examinations', 'Prescription Glasses', 'Contact Lens Fitting', 'Eye Disease Treatment', 'Vision Therapy']
    for service in services:
        pdf.cell(0, 6, f'- {service}', ln=1, align='C')

    # Return PDF as bytes - ensure bytes type for Streamlit
    try:
        # Try fpdf2 method first
        result = pdf.output()
        return bytes(result) if isinstance(result, bytearray) else result
    except:
        try:
            # Try classic fpdf method
            result = pdf.output(dest='S').encode('latin-1')
            return bytes(result) if isinstance(result, bytearray) else result
        except:
            # Fallback with BytesIO
            buffer = BytesIO()
            pdf_str = pdf.output(dest='S')
            if isinstance(pdf_str, str):
                buffer.write(pdf_str.encode('latin-1'))
            else:
                buffer.write(pdf_str)
            buffer.seek(0)
            result = buffer.getvalue()
            return bytes(result) if isinstance(result, bytearray) else result