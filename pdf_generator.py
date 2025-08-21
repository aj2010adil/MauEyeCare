from __future__ import annotations

from typing import Optional
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import qrcode


async def render_prescription_pdf(
    *,
    patient_id: int,
    visit_id: int | None,
    rx_values: Optional[dict],
    spectacles: Optional[list],
    medicines: Optional[dict],
    totals: Optional[dict],
) -> bytes:
    """
    Generate a professionally branded MauEyeCare prescription PDF including a QR code.
    Signature kept the same to avoid breaking existing callers.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    def text(x, y, s, size=10, bold=False, color=colors.black):
        c.setFillColor(color)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x, y, s)

    y = height - 18 * mm

    # Header branding
    text(20 * mm, y, "MAU Eye Care", 18, True, colors.HexColor("#1e40af"))
    y -= 6 * mm
    text(20 * mm, y, "Mubarakpur Azamgarh, Pura Sofi Bhonu Kuraishi Dasai Kuwa, Azamgarh, Uttar Pradesh", 9, False, colors.HexColor("#334155"))
    y -= 5 * mm
    text(20 * mm, y, "📞 092356 47410  |  🌐 www.facebook.com", 9, False, colors.HexColor("#334155"))
    y -= 6 * mm

    c.setStrokeColor(colors.HexColor("#2563eb"))
    c.line(20 * mm, y, width - 20 * mm, y)

    # Patient/visit info
    y -= 8 * mm
    text(20 * mm, y, f"Patient ID: {patient_id}", 11, True)
    text(90 * mm, y, f"Visit ID: {visit_id or 'N/A'}", 11)
    y -= 8 * mm

    # QR code (right side)
    try:
        qr_url = f"http://localhost:5173/prescription?id={patient_id}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#000000", back_color="#FFFFFF")
        img_buf = BytesIO()
        qr_img.save(img_buf, format="PNG")
        img_buf.seek(0)
        qr_reader = ImageReader(img_buf)
        c.drawImage(qr_reader, width - 50 * mm, y + 2 * mm, 30 * mm, 30 * mm, preserveAspectRatio=True, mask='auto')
    except Exception:
        pass

    # Sections helper
    def section(title: str):
        nonlocal y
        y -= 10 * mm
        if y < 40 * mm:
            c.showPage(); y = height - 18 * mm
        text(20 * mm, y, title, 13, True, colors.HexColor("#1e40af"))
        y -= 2 * mm
        c.setStrokeColor(colors.HexColor("#dbeafe"))
        c.line(20 * mm, y, width - 20 * mm, y)

    def kv(label: str, value: str):
        nonlocal y
        y -= 6 * mm
        if y < 30 * mm:
            c.showPage(); y = height - 18 * mm
        text(22 * mm, y, f"{label}: ", 10, True)
        text(45 * mm, y, value or "-")

    # RX values
    if rx_values:
        section("Prescription Details")
        kv("OD Sphere", str(rx_values.get("od_sphere", "0.00")))
        kv("OD Cylinder", str(rx_values.get("od_cylinder", "0.00")))
        kv("OD Axis", str(rx_values.get("od_axis", "0")))
        kv("OD Add", str(rx_values.get("od_add", "0.00")))
        kv("OS Sphere", str(rx_values.get("os_sphere", "0.00")))
        kv("OS Cylinder", str(rx_values.get("os_cylinder", "0.00")))
        kv("OS Axis", str(rx_values.get("os_axis", "0")))
        kv("OS Add", str(rx_values.get("os_add", "0.00")))

    # Spectacles
    if spectacles:
        section("Spectacles")
        for spec in spectacles:
            name = str(spec.get("name", ""))
            qty = int(spec.get("quantity", 1) or 1)
            price = float(spec.get("price", 0) or 0)
            total = price * qty
            kv(name, f"Qty {qty}  •  ₹{price:,.2f}  •  Total ₹{total:,.2f}")

    # Medicines
    if medicines:
        section("Medicines")
        for key, med in medicines.items():
            name = str(med.get("name", key))
            dosage = str(med.get("dosage", ""))
            qty = int(med.get("quantity", 1) or 1)
            price = float(med.get("price", 0) or 0)
            total = price * qty
            kv(name, f"{dosage}  •  Qty {qty}  •  ₹{price:,.2f}  •  Total ₹{total:,.2f}")

    # Totals
    if totals:
        section("Totals")
        st = float(totals.get("spectacles_total", 0) or 0)
        mt = float(totals.get("medicines_total", 0) or 0)
        gt = float(totals.get("grand_total", 0) or 0)
        kv("Spectacles Total", f"₹{st:,.2f}")
        kv("Medicines Total", f"₹{mt:,.2f}")
        kv("Grand Total", f"₹{gt:,.2f}")

    # Signature/footer
    y = max(y, 35 * mm)
    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.line(20 * mm, 30 * mm, 90 * mm, 30 * mm)
    text(20 * mm, 27 * mm, "Doctor's Signature", 10)
    text(width - 70 * mm, 27 * mm, "Scan QR to view online", 9, False, colors.HexColor("#334155"))

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


