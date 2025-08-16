"""
Cloud-compatible prescription generator
Works without external dependencies like python-docx
"""
import datetime
from io import BytesIO

def generate_prescription_text(prescription, doctor_name, patient_name, age, gender, advice, rx_table, recommendations, dosages=None):
    """Generate prescription as downloadable text file"""
    
    timestamp = datetime.datetime.now()
    
    content = f"""
═══════════════════════════════════════════════════════════════
                    👁️ MauEyeCare Optical Center
                     Dr. Danish - Eye Care Specialist
                  Phone: +91 92356-47410 | Reg. No: UPS 2908
                      Email: info@maueyecare.com
═══════════════════════════════════════════════════════════════

Date: {timestamp.strftime("%d/%m/%Y %H:%M")}
Prescription No: RX-{timestamp.strftime("%Y%m%d%H%M")}

PATIENT INFORMATION:
───────────────────────────────────────────────────────────────
Patient Name: {patient_name}
Age: {age} years
Gender: {gender}

"""
    
    # RX Details
    if rx_table and any(rx_table.get(eye, {}).get('Sphere') for eye in ['OD', 'OS']):
        content += """PRESCRIPTION DETAILS:
───────────────────────────────────────────────────────────────
"""
        for eye in ['OD', 'OS']:
            eye_data = rx_table.get(eye, {})
            if eye_data.get('Sphere'):
                rx_line = f"{eye} (Right Eye): " if eye == 'OD' else f"{eye} (Left Eye):  "
                if eye_data.get('Sphere'):
                    rx_line += f"SPH {eye_data['Sphere']} "
                if eye_data.get('Cylinder'):
                    rx_line += f"CYL {eye_data['Cylinder']} "
                if eye_data.get('Axis'):
                    rx_line += f"AXIS {eye_data['Axis']}"
                content += rx_line + "\n"
        content += "\n"
    
    # Medicines
    if prescription:
        content += """PRESCRIBED MEDICATIONS:
───────────────────────────────────────────────────────────────
"""
        for item, qty in prescription.items():
            content += f"• {item}\n"
            content += f"  Quantity: {qty}\n"
            
            if dosages and item in dosages:
                dosage_info = dosages[item]
                content += f"  Dosage: {dosage_info.get('dosage', 'As directed')}\n"
                content += f"  Timing: {dosage_info.get('timing', 'As directed')}\n"
            else:
                content += f"  Dosage: {'1 drop' if 'drop' in item.lower() else '1 tablet'}\n"
                content += f"  Timing: Twice daily\n"
            content += "\n"
    
    # Advice
    if advice and advice != "Other":
        content += f"""DOCTOR'S ADVICE:
───────────────────────────────────────────────────────────────
{advice}

"""
    
    # Instructions
    content += """GENERAL INSTRUCTIONS:
───────────────────────────────────────────────────────────────
• Take medications exactly as prescribed
• Do not skip doses or stop medication abruptly
• Follow up after 2 weeks if symptoms persist
• Avoid rubbing or touching your eyes
• Use prescribed eye drops regularly as directed
• Maintain proper eye hygiene
• Contact clinic immediately for any emergency
• Store medications as per instructions on the package

FOLLOW-UP:
───────────────────────────────────────────────────────────────
Next visit: As advised or if symptoms worsen
Emergency contact: +91 92356-47410

"""
    
    # Footer
    content += f"""═══════════════════════════════════════════════════════════════
                        Thank you for choosing
                      MauEyeCare Optical Center
                    Your vision is our priority
═══════════════════════════════════════════════════════════════


                                              Dr. Danish
                                         Eye Care Specialist
                                           MCI Reg: UPS 2908
                                      Date: {timestamp.strftime("%d/%m/%Y")}

"""
    
    return content.encode('utf-8')

def generate_prescription_html(prescription, doctor_name, patient_name, age, gender, advice, rx_table, recommendations, dosages=None):
    """Generate prescription as HTML for better formatting"""
    
    timestamp = datetime.datetime.now()
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Prescription - {patient_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }}
        .clinic-name {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
        .doctor-info {{ font-size: 16px; margin: 10px 0; }}
        .prescription-info {{ text-align: right; margin: 20px 0; }}
        .section {{ margin: 20px 0; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        .patient-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .rx-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .rx-table th, .rx-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .rx-table th {{ background-color: #f2f2f2; }}
        .medicine-item {{ margin: 10px 0; padding: 10px; border-left: 3px solid #2c5aa0; background: #f9f9f9; }}
        .instructions {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }}
        .footer {{ text-align: right; margin-top: 40px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="clinic-name">👁️ MauEyeCare Optical Center</div>
        <div class="doctor-info">Dr. Danish - Eye Care Specialist</div>
        <div class="doctor-info">Phone: +91 92356-47410 | Reg. No: UPS 2908</div>
        <div class="doctor-info">Email: info@maueyecare.com</div>
    </div>
    
    <div class="prescription-info">
        <strong>Date:</strong> {timestamp.strftime("%d/%m/%Y %H:%M")}<br>
        <strong>Prescription No:</strong> RX-{timestamp.strftime("%Y%m%d%H%M")}
    </div>
    
    <div class="section">
        <div class="section-title">Patient Information</div>
        <div class="patient-info">
            <strong>Patient Name:</strong> {patient_name}<br>
            <strong>Age:</strong> {age} years<br>
            <strong>Gender:</strong> {gender}
        </div>
    </div>
"""
    
    # RX Details
    if rx_table and any(rx_table.get(eye, {}).get('Sphere') for eye in ['OD', 'OS']):
        html_content += """
    <div class="section">
        <div class="section-title">Prescription Details</div>
        <table class="rx-table">
            <tr>
                <th>Eye</th>
                <th>Sphere (SPH)</th>
                <th>Cylinder (CYL)</th>
                <th>Axis</th>
            </tr>
"""
        for eye in ['OD', 'OS']:
            eye_data = rx_table.get(eye, {})
            if eye_data.get('Sphere'):
                eye_name = "Right Eye (OD)" if eye == 'OD' else "Left Eye (OS)"
                html_content += f"""
            <tr>
                <td>{eye_name}</td>
                <td>{eye_data.get('Sphere', '')}</td>
                <td>{eye_data.get('Cylinder', '')}</td>
                <td>{eye_data.get('Axis', '')}</td>
            </tr>
"""
        html_content += """
        </table>
    </div>
"""
    
    # Medicines
    if prescription:
        html_content += """
    <div class="section">
        <div class="section-title">Prescribed Medications</div>
"""
        for item, qty in prescription.items():
            html_content += f"""
        <div class="medicine-item">
            <strong>{item}</strong><br>
            <strong>Quantity:</strong> {qty}<br>
"""
            if dosages and item in dosages:
                dosage_info = dosages[item]
                html_content += f"""
            <strong>Dosage:</strong> {dosage_info.get('dosage', 'As directed')}<br>
            <strong>Timing:</strong> {dosage_info.get('timing', 'As directed')}
"""
            else:
                dosage = '1 drop' if 'drop' in item.lower() else '1 tablet'
                html_content += f"""
            <strong>Dosage:</strong> {dosage}<br>
            <strong>Timing:</strong> Twice daily
"""
            html_content += """
        </div>
"""
        html_content += """
    </div>
"""
    
    # Advice
    if advice and advice != "Other":
        html_content += f"""
    <div class="section">
        <div class="section-title">Doctor's Advice</div>
        <p>{advice}</p>
    </div>
"""
    
    # Instructions
    html_content += """
    <div class="section">
        <div class="section-title">General Instructions</div>
        <div class="instructions">
            <ul>
                <li>Take medications exactly as prescribed</li>
                <li>Do not skip doses or stop medication abruptly</li>
                <li>Follow up after 2 weeks if symptoms persist</li>
                <li>Avoid rubbing or touching your eyes</li>
                <li>Use prescribed eye drops regularly as directed</li>
                <li>Maintain proper eye hygiene</li>
                <li>Contact clinic immediately for any emergency</li>
                <li>Store medications as per instructions on the package</li>
            </ul>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Follow-up</div>
        <p><strong>Next visit:</strong> As advised or if symptoms worsen<br>
        <strong>Emergency contact:</strong> +91 92356-47410</p>
    </div>
    
    <div class="footer">
        <p><strong>Dr. Danish</strong><br>
        Eye Care Specialist<br>
        MCI Reg: UPS 2908<br>
        Date: """ + timestamp.strftime("%d/%m/%Y") + """</p>
    </div>
    
    <div style="text-align: center; margin-top: 30px; color: #666;">
        <p>Thank you for choosing MauEyeCare Optical Center<br>
        Your vision is our priority</p>
    </div>
</body>
</html>
"""
    
    return html_content.encode('utf-8')