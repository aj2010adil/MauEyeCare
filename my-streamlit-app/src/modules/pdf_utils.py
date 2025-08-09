"""
pdf_utils.py
PDF generation utilities for MauEyeCare.
"""
from fpdf import FPDF  # (fpdf2 will override the classic fpdf)
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
    pdf.cell(0, 6, 'MauEye Care Hospital | MubarakPur, Azamgarh | www.maueyeycare.com | info@maueycare.com', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    # --- BACK PAGE: Info in Urdu and Hindi ---
    pdf.add_page()
    import os
    import sys
    font_added = False
    # Look for fonts in a 'fonts' subdirectory next to this script
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    noto_path = os.path.join(font_dir, 'NotoSans-Regular.ttf')
    arialuni_path = os.path.join(font_dir, 'arialuni.ttf')
    print(f"[DEBUG] Looking for Unicode fonts at: {noto_path} and {arialuni_path}", file=sys.stderr)
    try:
        if os.path.exists(noto_path):
            print(f"[DEBUG] Found NotoSans-Regular.ttf at {noto_path}", file=sys.stderr)
            pdf.add_font('NotoSans', '', noto_path, uni=True)
            pdf.set_font('NotoSans', '', 14)
            font_added = True
        elif os.path.exists(arialuni_path):
            print(f"[DEBUG] Found arialuni.ttf at {arialuni_path}", file=sys.stderr)
            pdf.add_font('ArialUnicode', '', arialuni_path, uni=True)
            pdf.set_font('ArialUnicode', '', 14)
            font_added = True
        else:
            print(f"[ERROR] Unicode font not found. Checked: {noto_path} and {arialuni_path}", file=sys.stderr)
            font_added = False
    except Exception as e:
        print(f"[ERROR] Exception loading Unicode font: {e}", file=sys.stderr)
        font_added = False
    pdf.set_xy(20, 30)
    pdf.set_text_color(41, 71, 226)
    pdf.cell(0, 12, 'MauEye Care Hospital', ln=1, align='C')
    pdf.set_text_color(0,0,0)
    if font_added:
        pdf.set_font_size(12)
        # Hindi
        pdf.ln(5)
        pdf.multi_cell(0, 10, 'मऊ आई केयर हॉस्पिटल\nआधुनिक नेत्र एवं दृष्टि देखभाल केंद्र\nमुबाकरपुर, आज़मगढ़ | www.maueyeycare.com | info@maueyeycare.com\nफोन: 92356-47410', align='C')
        # Urdu
        pdf.ln(5)
        pdf.set_font_size(13)
        urdu_text = 'مئو آئی کیئر ہسپتال\nجدید آنکھوں اور بصارت کی دیکھ بھال کا مرکز\nمبارک پور، اعظم گڑھ | www.maueycare.com | info@maueycare.com\nفون: 92356-47410'
        pdf.multi_cell(0, 10, urdu_text, align='C')
    else:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255,0,0)
        pdf.ln(10)
        pdf.cell(0, 10, 'Unicode font not found. Hindi/Urdu text not shown.', ln=1, align='C')
        pdf.set_text_color(0,0,0)
    # FPDF output(dest='S') returns bytes or bytearray; wrap as bytes for BytesIO
    pdf_bytes = pdf.output(dest='S')
    if not isinstance(pdf_bytes, (bytes, bytearray)):
        raise TypeError("FPDF output(dest='S') did not return bytes or bytearray")
    return BytesIO(bytes(pdf_bytes))

ALTER TABLE prescriptions ADD COLUMN issue TEXT;
