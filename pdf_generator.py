from __future__ import annotations

from typing import Optional
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


async def render_prescription_pdf(
    *,
    patient_id: int,
    visit_id: int | None,
    rx_values: Optional[dict],
    spectacles: Optional[list],
    medicines: Optional[dict],
    totals: Optional[dict],
) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    def text(x, y, s, size=10, bold=False):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x, y, s)

    y = height - 20 * mm
    text(20 * mm, y, "MauEyeCare Prescription", 16, True)
    y -= 8 * mm
    text(20 * mm, y, f"Patient #{patient_id} • Visit #{visit_id or 0}")
    y -= 10 * mm
    c.setStrokeColor(colors.HexColor("#0ea5e9"))
    c.line(20 * mm, y, width - 20 * mm, y)

    def section(title: str, obj):
        nonlocal y
        y -= 8 * mm
        text(20 * mm, y, title, 12, True)
        y -= 6 * mm
        for line in (str(obj) or "{}").splitlines():
            if y < 30 * mm:
                c.showPage(); y = height - 20 * mm
            text(22 * mm, y, line[:110])
            y -= 5 * mm

    section("RX Values", rx_values or {})
    section("Spectacles", spectacles or [])
    section("Medicines", medicines or {})
    section("Totals", totals or {})

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


