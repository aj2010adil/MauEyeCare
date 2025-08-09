"""
pdf_utils.py
PDF generation utilities for MauEyeCare.
"""
from fpdf import FPDF  # (fpdf2 will override the classic fpdf)
from io import BytesIO

def generate_pdf(prescription, dosage, eye_test, doctor_name, patient_name, age, gender, advice, rx_table, recommendations):
    pdf = FPDF()
    pdf.add_page()
    # Always set a font before any cell/text on a new page
    pdf.set_font('Arial', 'B', 18)
    # Colors
    blue = (41, 171, 226)
    gray = (230, 230, 230)
    # Draw blue sidebar
    pdf.set_fill_color(*blue)
    pdf.rect(10, 10, 20, 270, 'F')
    # --- HEADER ---
    # Hospital Name (English, front page)
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

    # --- PATIENT & PRESCRIPTION DETAILS (Front Page) ---
    # Patient Info
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

    # Recommendations (one-liner)
    if recommendations:
        pdf.set_xy(15, 75)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 7, 'Recommendations:', ln=0)
        pdf.set_font('Arial', '', 10)
        rec_line = ', '.join(recommendations)
        pdf.set_x(55)
        pdf.cell(0, 7, rec_line, ln=1)

    # Rx Table (one-liner per eye)
    pdf.set_xy(90, 45)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(20, 8, 'Rx:', ln=0)
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(90, 53)
    for eye in ['OD', 'OS']:
        row = rx_table.get(eye, {'Sphere':'', 'Cylinder':'', 'Axis':'', 'Prism':''})
        rx_str = f"{eye}: Sph {row.get('Sphere','')} Cyl {row.get('Cylinder','')} Axis {row.get('Axis','')} Prism {row.get('Prism','')}"
        pdf.cell(0, 6, rx_str, ln=1)

    # Medicines (one-liner)
    if prescription:
        pdf.set_xy(90, 65)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, 'Medicines:', ln=1)
        pdf.set_font('Arial', '', 10)
        meds_line = '; '.join([f"{med} ({qty})" for med, qty in prescription.items()])
        pdf.set_x(90)
        pdf.multi_cell(0, 6, meds_line)

    # Dosage and Eye Test (one-liners)
    pdf.set_x(90)
    pdf.cell(0, 6, f"Dosage: {dosage}", ln=1)
    pdf.set_x(90)
    pdf.cell(0, 6, f"Eye Test: {eye_test}", ln=1)

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
    pdf = FPDF()
    pdf.add_page()
    # Always set a font before any cell/text on a new page
    pdf.set_font('Arial', 'B', 18)
    # Colors
    blue = (41, 171, 226)
    gray = (230, 230, 230)
    # Draw blue sidebar
    pdf.set_fill_color(*blue)
    pdf.rect(10, 10, 20, 270, 'F')
    # --- HEADER ---
    # Hospital Name (English, front page)
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
    # --- BACK PAGE: Info in Urdu and Hindi ---
    pdf.add_page()
    # Always set a default font before any cell/text on a new page
    pdf.set_font('Arial', 'B', 14)
    import os
    import sys
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    dev_path = os.path.join(font_dir, 'NotoSansDevanagari-Regular.ttf')
    arabic_path = os.path.join(font_dir, 'NotoNaskhArabic-Regular.ttf')
    arialuni_path = os.path.join(font_dir, 'arialuni.ttf')
    print(f"[DEBUG] Looking for Hindi font at: {dev_path}", file=sys.stderr)
    print(f"[DEBUG] Looking for Urdu font at: {arabic_path}", file=sys.stderr)
    print(f"[DEBUG] Looking for fallback font at: {arialuni_path}", file=sys.stderr)
    font_hindi = None
    font_urdu = None
    try:
        if os.path.exists(dev_path):
            pdf.add_font('NotoSansDevanagari', '', dev_path, uni=True)
            font_hindi = 'NotoSansDevanagari'
            print(f"[DEBUG] Found NotoSansDevanagari-Regular.ttf at {dev_path}", file=sys.stderr)
        elif os.path.exists(arialuni_path):
            pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            font_hindi = 'ArialUnicode'
            print(f"[DEBUG] Using ArialUnicode for Hindi at {arialuni_path}", file=sys.stderr)
        else:
            print(f"[ERROR] Hindi font not found. Checked: {dev_path} and {arialuni_path}", file=sys.stderr)
        if os.path.exists(arabic_path):
            pdf.add_font('NotoNaskhArabic', '', arabic_path, uni=True)
            font_urdu = 'NotoNaskhArabic'
            print(f"[DEBUG] Found NotoNaskhArabic-Regular.ttf at {arabic_path}", file=sys.stderr)
        elif os.path.exists(arialuni_path):
            if not font_hindi:  # Only add if not already added
                pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            font_urdu = 'ArialUnicode'
            print(f"[DEBUG] Using ArialUnicode for Urdu at {arialuni_path}", file=sys.stderr)
        else:
            print(f"[ERROR] Urdu font not found. Checked: {arabic_path} and {arialuni_path}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Exception loading Unicode font: {e}", file=sys.stderr)
    pdf.set_xy(20, 30)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 12, 'MauEye Care Hospital', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    if font_hindi:
        pdf.set_font(font_hindi, '', 12)
        pdf.ln(5)
        pdf.multi_cell(0, 10, 'मऊ आई केयर हॉस्पिटल\nआधुनिक नेत्र एवं दृष्टि देखभाल केंद्र\nमुबाकरपुर, आज़मगढ़ | www.maueyeycare.com | info@maueyeycare.com\nफोन: 92356-47410', align='C')
    else:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255,0,0)
        pdf.ln(10)
        pdf.cell(0, 10, 'Hindi Unicode font not found. Hindi text not shown.', ln=1, align='C')
        pdf.set_text_color(0,0,0)
    if font_urdu:
        pdf.set_font(font_urdu, '', 13)
        pdf.ln(5)
        urdu_text = 'مئو آئی کیئر ہسپتال\nجدید آنکھوں اور بصارت کی دیکھ بھال کا مرکز\nمبارک پور، اعظم گڑھ | www.maueycare.com | info@maueyeycare.com\nفون: 92356-47410'
        pdf.multi_cell(0, 10, urdu_text, align='C')
    else:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255,0,0)
        pdf.ln(10)
        pdf.cell(0, 10, 'Urdu Unicode font not found. Urdu text not shown.', ln=1, align='C')
        pdf.set_text_color(0,0,0)
    # (Back page should not repeat patient info, Rx, or recommendations)
    # --- BACK PAGE: Info in Urdu and Hindi ---
    pdf.add_page()
    # Always set a default font before any cell/text on a new page
    pdf.set_font('Arial', 'B', 14)
    import os
    import sys
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    dev_path = os.path.join(font_dir, 'NotoSansDevanagari-Regular.ttf')
    arabic_path = os.path.join(font_dir, 'NotoNaskhArabic-Regular.ttf')
    arialuni_path = os.path.join(font_dir, 'arialuni.ttf')
    print(f"[DEBUG] Looking for Hindi font at: {dev_path}", file=sys.stderr)
    print(f"[DEBUG] Looking for Urdu font at: {arabic_path}", file=sys.stderr)
    print(f"[DEBUG] Looking for fallback font at: {arialuni_path}", file=sys.stderr)
    font_hindi = None
    font_urdu = None
    try:
        if os.path.exists(dev_path):
            pdf.add_font('NotoSansDevanagari', '', dev_path, uni=True)
            font_hindi = 'NotoSansDevanagari'
            print(f"[DEBUG] Found NotoSansDevanagari-Regular.ttf at {dev_path}", file=sys.stderr)
        elif os.path.exists(arialuni_path):
            pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            font_hindi = 'ArialUnicode'
            print(f"[DEBUG] Using ArialUnicode for Hindi at {arialuni_path}", file=sys.stderr)
        else:
            print(f"[ERROR] Hindi font not found. Checked: {dev_path} and {arialuni_path}", file=sys.stderr)
        if os.path.exists(arabic_path):
            pdf.add_font('NotoNaskhArabic', '', arabic_path, uni=True)
            font_urdu = 'NotoNaskhArabic'
            print(f"[DEBUG] Found NotoNaskhArabic-Regular.ttf at {arabic_path}", file=sys.stderr)
        elif os.path.exists(arialuni_path):
            if not font_hindi:  # Only add if not already added
                pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            font_urdu = 'ArialUnicode'
            print(f"[DEBUG] Using ArialUnicode for Urdu at {arialuni_path}", file=sys.stderr)
        else:
            print(f"[ERROR] Urdu font not found. Checked: {arabic_path} and {arialuni_path}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Exception loading Unicode font: {e}", file=sys.stderr)
    pdf.set_xy(20, 30)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 12, 'MauEye Care Hospital', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    if font_hindi:
        pdf.set_font(font_hindi, '', 12)
        pdf.ln(5)
        pdf.multi_cell(0, 10, 'मऊ आई केयर हॉस्पिटल\nआधुनिक नेत्र एवं दृष्टि देखभाल केंद्र\nमुबाकरपुर, आज़मगढ़ | www.maueyeycare.com | info@maueyeycare.com\nफोन: 92356-47410', align='C')
    else:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255,0,0)
        pdf.ln(10)
        pdf.cell(0, 10, 'Hindi Unicode font not found. Hindi text not shown.', ln=1, align='C')
        pdf.set_text_color(0,0,0)
    if font_urdu:
        pdf.set_font(font_urdu, '', 13)
        pdf.ln(5)
        urdu_text = 'مئو آئی کیئر ہسپتال\nجدید آنکھوں اور بصارت کی دیکھ بھال کا مرکز\nمبارک پور، اعظم گڑھ | www.maueycare.com | info@maueyeycare.com\nفون: 92356-47410'
        pdf.multi_cell(0, 10, urdu_text, align='C')
    else:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255,0,0)
        pdf.ln(10)
        pdf.cell(0, 10, 'Urdu Unicode font not found. Urdu text not shown.', ln=1, align='C')
        pdf.set_text_color(0,0,0)
    # FPDF output(dest='S') returns bytes or bytearray; wrap as bytes for BytesIO
    pdf_bytes = pdf.output(dest='S')
    if not isinstance(pdf_bytes, (bytes, bytearray)):
        raise TypeError("FPDF output(dest='S') did not return bytes or bytearray")
    return BytesIO(bytes(pdf_bytes))


