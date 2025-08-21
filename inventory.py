from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
import os
import json
import csv
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import uuid

from database import get_db_session
from dependencies import get_current_user_id
from spectacle import Spectacle
from medicine import Medicine
from prescription import Prescription
from patient import Patient
from visit import Visit

router = APIRouter()

# Spectacles endpoints
@router.get("/spectacles")
async def get_spectacles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    brand: Optional[str] = None,
    frame_shape: Optional[str] = None,
    lens_type: Optional[str] = None,
    gender: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Get spectacles with filtering and pagination"""
    query = select(Spectacle)
    
    # Apply filters
    if search:
        query = query.where(
            Spectacle.name.ilike(f"%{search}%") |
            Spectacle.brand.ilike(f"%{search}%") |
            Spectacle.description.ilike(f"%{search}%")
        )
    
    if brand:
        query = query.where(Spectacle.brand == brand)
    
    if frame_shape:
        query = query.where(Spectacle.frame_shape == frame_shape)
    
    if lens_type:
        query = query.where(Spectacle.lens_type == lens_type)
    
    if gender:
        query = query.where(Spectacle.gender == gender)
    
    if min_price is not None:
        query = query.where(Spectacle.price >= min_price)
    
    if max_price is not None:
        query = query.where(Spectacle.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            query = query.where(Spectacle.quantity > 0)
        else:
            query = query.where(Spectacle.quantity == 0)
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar_one()
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    spectacles = (await db.execute(query)).scalars().all()
    
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "brand": s.brand,
                "price": s.price,
                "image_url": s.image_url,
                "frame_material": s.frame_material,
                "frame_shape": s.frame_shape,
                "lens_type": s.lens_type,
                "gender": s.gender,
                "age_group": s.age_group,
                "description": s.description,
                "specifications": s.specifications,
                "in_stock": s.quantity > 0,
                "quantity": s.quantity
            }
            for s in spectacles
        ],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/spectacles/{spectacle_id}")
async def get_spectacle(
    spectacle_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific spectacle by ID"""
    spectacle = await db.get(Spectacle, spectacle_id)
    if not spectacle:
        raise HTTPException(status_code=404, detail="Spectacle not found")
    
    return {
        "id": spectacle.id,
        "name": spectacle.name,
        "brand": spectacle.brand,
        "price": spectacle.price,
        "image_url": spectacle.image_url,
        "frame_material": spectacle.frame_material,
        "frame_shape": spectacle.frame_shape,
        "lens_type": spectacle.lens_type,
        "gender": spectacle.gender,
        "age_group": spectacle.age_group,
        "description": spectacle.description,
        "specifications": spectacle.specifications,
        "in_stock": spectacle.quantity > 0,
        "quantity": spectacle.quantity
    }

# Image upload endpoint
@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    product_type: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Upload product image and return URL"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    # Return the image URL
    image_url = f"/uploads/{filename}"
    
    return {
        "image_url": image_url,
        "filename": filename,
        "size": len(content),
        "content_type": file.content_type
    }

# Image analysis endpoint
@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    product_type: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Analyze product image and return auto-detected tags and suggestions"""
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # For demo purposes, return mock analysis results
    # In production, this would integrate with AI/ML services like Google Vision API, Azure Computer Vision, etc.
    
    if product_type == "spectacle":
        tags = [
            {"id": "1", "name": "Eyeglasses", "confidence": 0.95, "category": "Product Type"},
            {"id": "2", "name": "Ray-Ban", "confidence": 0.87, "category": "Brand"},
            {"id": "3", "name": "Aviator", "confidence": 0.82, "category": "Style"},
            {"id": "4", "name": "Metal Frame", "confidence": 0.78, "category": "Material"},
            {"id": "5", "name": "Sunglasses", "confidence": 0.75, "category": "Type"}
        ]
        
        suggestions = {
            "name": "Ray-Ban Aviator Classic",
            "brand": "Ray-Ban",
            "category": "Sunglasses",
            "description": "Classic aviator sunglasses with metal frame",
            "price": 8500.0
        }
    else:  # medicine
        tags = [
            {"id": "1", "name": "Eye Drops", "confidence": 0.92, "category": "Product Type"},
            {"id": "2", "name": "Pharmaceutical", "confidence": 0.88, "category": "Category"},
            {"id": "3", "name": "Artificial Tears", "confidence": 0.85, "category": "Product"},
            {"id": "4", "name": "Lubricating", "confidence": 0.79, "category": "Function"},
            {"id": "5", "name": "Prescription", "confidence": 0.72, "category": "Type"}
        ]
        
        suggestions = {
            "name": "Artificial Tears Eye Drops",
            "brand": "Generic",
            "category": "Eye Care",
            "description": "Lubricating eye drops for dry eyes",
            "price": 150.0
        }
    
    return {
        "tags": tags,
        "suggestions": suggestions,
        "analysis_confidence": 0.85
    }

# Bulk file upload endpoint for inventory
@router.post("/upload")
async def upload_inventory_files(
    files: list[UploadFile] = File(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    if category not in ("spectacles", "medicines"):
        raise HTTPException(status_code=400, detail="Invalid category")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    items = []
    errors = []

    for f in files:
        try:
            if not f.content_type or not f.content_type.startswith("image/"):
                errors.append(f"{f.filename}: unsupported file type {f.content_type}")
                continue

            ext = (f.filename or "bin").split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(upload_dir, filename)

            content = await f.read()
            with open(path, "wb") as out:
                out.write(content)

            image_url = f"/uploads/{filename}"
            base_name = (f.filename or "Untitled").rsplit(".", 1)[0]

            if category == "spectacles":
                obj = Spectacle(
                    name=base_name,
                    brand="Unknown",
                    price=0.0,
                    image_url=image_url,
                    quantity=1,
                    in_stock=True
                )
            else:
                obj = Medicine(
                    name=base_name,
                    brand=None,
                    price=0.0,
                    image_url=image_url,
                    quantity=1,
                    in_stock=True
                )

            db.add(obj)
            await db.flush()
            items.append({
                "id": obj.id,
                "name": obj.name,
                "brand": getattr(obj, "brand", None),
                "price": float(getattr(obj, "price", 0) or 0),
                "quantity": getattr(obj, "quantity", 0)
            })
        except Exception as e:
            errors.append(f"{f.filename}: {str(e)}")

    await db.commit()
    return {"items": items, "errors": errors}


# CSV upload endpoint for inventory
@router.post("/upload-csv")
async def upload_inventory_csv(
    file: UploadFile = File(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    if category not in ("spectacles", "medicines"):
        raise HTTPException(status_code=400, detail="Invalid category")

    try:
        raw = await file.read()
        text = raw.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {str(e)}")

    reader = csv.DictReader(text.splitlines())
    items = []
    errors = []
    count = 0

    for i, row in enumerate(reader, start=1):
        try:
            # Normalize common fields
            name = row.get("name") or row.get("model_name") or row.get("model") or f"Item {i}"
            brand = row.get("brand")
            price = row.get("price") or "0"
            quantity = row.get("quantity") or "0"

            try:
                price_val = float(price)
            except Exception:
                price_val = 0.0
            try:
                qty_val = int(float(quantity))
            except Exception:
                qty_val = 0

            if category == "spectacles":
                obj = Spectacle(
                    name=name,
                    brand=brand or "Unknown",
                    price=price_val,
                    frame_material=row.get("frame_material"),
                    frame_shape=row.get("frame_shape"),
                    lens_type=row.get("lens_type"),
                    gender=row.get("gender"),
                    age_group=row.get("age_group"),
                    description=row.get("description"),
                    quantity=qty_val,
                    in_stock=qty_val > 0,
                )
            else:
                # Map common medicine fields
                dosage = row.get("dosage") or row.get("dosage_form")
                specs = {}
                for k, v in row.items():
                    if k.lower() not in {"name", "brand", "category", "price", "quantity", "dosage", "dosage_form"} and v:
                        specs[k] = v

                obj = Medicine(
                    name=name,
                    brand=brand,
                    category=row.get("category"),
                    dosage=dosage,
                    price=price_val,
                    description=row.get("description"),
                    specifications=specs if specs else None,
                    quantity=qty_val,
                    in_stock=qty_val > 0,
                )

            db.add(obj)
            await db.flush()
            items.append({
                "id": obj.id,
                "name": obj.name,
                "brand": getattr(obj, "brand", None),
                "price": float(getattr(obj, "price", 0) or 0),
                "quantity": getattr(obj, "quantity", 0)
            })
            count += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    await db.commit()
    return {"items": items, "errors": errors}

# Prescription export endpoints
@router.post("/prescriptions/{prescription_id}/export")
async def export_prescription(
    prescription_id: int,
    format: str = Form("html"),  # html, pdf, docx
    include_qr: bool = Form(True),
    branding: Optional[Dict] = Form(None),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Export prescription in various formats"""
    prescription = await db.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Get patient and visit details
    patient = await db.get(Patient, prescription.patient_id)
    visit = None
    if prescription.visit_id:
        visit = await db.get(Visit, prescription.visit_id)
    
    # Default branding
    if not branding:
        branding = {
            "clinic_name": "MAU Eye Care",
            "address": "Mubarakpur Azamgarh, Pura Sofi Bhonu Kuraishi Dasai Kuwa, Azamgarh, Uttar Pradesh",
            "phone": "092356 47410",
            "website": "www.facebook.com"
        }
    
    if format == "html":
        html_content = generate_prescription_html(prescription, patient, visit, branding, include_qr)
        return HTMLResponse(content=html_content)
    
    elif format == "pdf":
        # Generate PDF bytes and stream as a file download
        from pdf_generator import render_prescription_pdf
        pdf_bytes = await render_prescription_pdf(
            patient_id=prescription.patient_id,
            visit_id=prescription.visit_id,
            rx_values=prescription.rx_values,
            spectacles=prescription.spectacles,
            medicines=prescription.medicines,
            totals=prescription.totals,
        )
        from fastapi.responses import StreamingResponse
        headers = {"Content-Disposition": f'attachment; filename="prescription_{prescription_id}.pdf"'}
        return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers=headers)
    
    elif format == "docx":
        # Generate DOCX (would need python-docx library)
        docx_path = generate_prescription_docx(prescription, patient, visit, branding, include_qr)
        return FileResponse(docx_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"prescription_{prescription_id}.docx")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@router.get("/prescriptions/{prescription_id}/qr")
async def get_prescription_qr(
    prescription_id: int,
    size: int = Query(200, ge=50, le=500),
    foreground_color: str = Query("#000000"),
    background_color: str = Query("#FFFFFF"),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Generate QR code for prescription"""
    prescription = await db.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Generate QR code URL
    prescription_url = f"http://localhost:5173/prescription?id={prescription_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(prescription_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color=foreground_color, back_color=background_color)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "qr_code": f"data:image/png;base64,{img_str}",
        "url": prescription_url,
        "prescription_id": prescription_id
    }

@router.get("/prescriptions/{prescription_id}/qr.png")
async def get_prescription_qr_image(
    prescription_id: int,
    size: int = Query(200, ge=50, le=500),
    foreground_color: str = Query("#000000"),
    background_color: str = Query("#FFFFFF"),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    """Return QR code PNG image for embedding in documents"""
    prescription = await db.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Generate QR code URL
    prescription_url = f"http://localhost:5173/prescription?id={prescription_id}"

    # Create QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(prescription_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=foreground_color, back_color=background_color)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="image/png")

# Helper functions
def generate_prescription_html(prescription, patient, visit, branding, include_qr):
    """Generate HTML content for prescription"""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prescription - {patient.first_name} {patient.last_name}</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .prescription-container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .clinic-name {{
                font-size: 28px;
                font-weight: bold;
                color: #1e40af;
                margin-bottom: 5px;
            }}
            .clinic-address {{
                font-size: 14px;
                color: #6b7280;
                line-height: 1.4;
            }}
            .clinic-contact {{
                font-size: 14px;
                color: #6b7280;
                margin-top: 5px;
            }}
            .patient-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f8fafc;
                border-radius: 8px;
            }}
            .info-group {{
                display: flex;
                flex-direction: column;
            }}
            .info-label {{
                font-weight: bold;
                color: #374151;
                margin-bottom: 5px;
            }}
            .info-value {{
                color: #1f2937;
            }}
            .rx-section {{
                margin-bottom: 30px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #1e40af;
                margin-bottom: 15px;
                border-bottom: 2px solid #dbeafe;
                padding-bottom: 5px;
            }}
            .rx-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .rx-table th,
            .rx-table td {{
                border: 1px solid #d1d5db;
                padding: 12px;
                text-align: center;
            }}
            .rx-table th {{
                background-color: #f3f4f6;
                font-weight: bold;
                color: #374151;
            }}
            .rx-table td {{
                background-color: white;
            }}
            .items-section {{
                margin-bottom: 30px;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .items-table th,
            .items-table td {{
                border: 1px solid #d1d5db;
                padding: 10px;
                text-align: left;
            }}
            .items-table th {{
                background-color: #f3f4f6;
                font-weight: bold;
                color: #374151;
            }}
            .total-section {{
                display: flex;
                justify-content: flex-end;
                margin-bottom: 30px;
            }}
            .total-table {{
                border-collapse: collapse;
            }}
            .total-table td {{
                padding: 8px 15px;
                border: none;
            }}
            .total-table .total-row {{
                font-weight: bold;
                border-top: 2px solid #d1d5db;
            }}
            .footer {{
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
            }}
            .signature-section {{
                text-align: center;
            }}
            .signature-line {{
                width: 200px;
                border-bottom: 1px solid #000;
                margin-bottom: 5px;
            }}
            .qr-section {{
                text-align: center;
            }}
            .qr-code {{
                width: 80px;
                height: 80px;
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 5px;
            }}
            @media print {{
                body {{
                    background-color: white;
                    padding: 0;
                }}
                .prescription-container {{
                    box-shadow: none;
                    border-radius: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="prescription-container">
            <div class="header">
                <div class="clinic-name">{branding['clinic_name']}</div>
                <div class="clinic-address">
                    {branding['address']}
                </div>
                <div class="clinic-contact">
                    📞 {branding['phone']} | 🌐 {branding['website']}
                </div>
            </div>

            <div class="patient-info">
                <div class="info-group">
                    <span class="info-label">Patient Name:</span>
                    <span class="info-value">{patient.first_name} {patient.last_name or ''}</span>
                </div>
                <div class="info-group">
                    <span class="info-label">Visit Date:</span>
                    <span class="info-value">{visit.visit_date.strftime('%B %d, %Y') if visit else 'N/A'}</span>
                </div>
                <div class="info-group">
                    <span class="info-label">Phone:</span>
                    <span class="info-value">{patient.phone or 'N/A'}</span>
                </div>
                <div class="info-group">
                    <span class="info-label">Prescription ID:</span>
                    <span class="info-value">#{prescription.id}</span>
                </div>
            </div>
    """
    
    # Add RX values if available
    if prescription.rx_values:
        html += """
            <div class="rx-section">
                <div class="section-title">Prescription Details</div>
                <table class="rx-table">
                    <thead>
                        <tr>
                            <th>Eye</th>
                            <th>Sphere</th>
                            <th>Cylinder</th>
                            <th>Axis</th>
                            <th>Add</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        rx = prescription.rx_values
        html += f"""
                        <tr>
                            <td><strong>OD (Right)</strong></td>
                            <td>{rx.get('od_sphere', '0.00')}</td>
                            <td>{rx.get('od_cylinder', '0.00')}</td>
                            <td>{rx.get('od_axis', '0')}</td>
                            <td>{rx.get('od_add', '0.00')}</td>
                        </tr>
                        <tr>
                            <td><strong>OS (Left)</strong></td>
                            <td>{rx.get('os_sphere', '0.00')}</td>
                            <td>{rx.get('os_cylinder', '0.00')}</td>
                            <td>{rx.get('os_axis', '0')}</td>
                            <td>{rx.get('os_add', '0.00')}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """
    
    # Add spectacles if available
    if prescription.spectacles:
        html += """
            <div class="items-section">
                <div class="section-title">Spectacles</div>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for spectacle in prescription.spectacles:
            total = spectacle.get('price', 0) * spectacle.get('quantity', 1)
            html += f"""
                        <tr>
                            <td>{spectacle.get('name', 'N/A')}</td>
                            <td>{spectacle.get('quantity', 1)}</td>
                            <td>₹{spectacle.get('price', 0):,.2f}</td>
                            <td>₹{total:,.2f}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        """
    
    # Add medicines if available
    if prescription.medicines:
        html += """
            <div class="items-section">
                <div class="section-title">Medicines</div>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Medicine</th>
                            <th>Dosage</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for key, medicine in prescription.medicines.items():
            total = medicine.get('price', 0) * medicine.get('quantity', 1)
            html += f"""
                        <tr>
                            <td>{medicine.get('name', 'N/A')}</td>
                            <td>{medicine.get('dosage', 'N/A')}</td>
                            <td>{medicine.get('quantity', 1)}</td>
                            <td>₹{medicine.get('price', 0):,.2f}</td>
                            <td>₹{total:,.2f}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        """
    
    # Add totals
    if prescription.totals:
        html += """
            <div class="total-section">
                <table class="total-table">
        """
        
        totals = prescription.totals
        if totals.get('spectacles_total', 0) > 0:
            html += f"""
                    <tr>
                        <td>Spectacles Total:</td>
                        <td>₹{totals['spectacles_total']:,.2f}</td>
                    </tr>
            """
        
        if totals.get('medicines_total', 0) > 0:
            html += f"""
                    <tr>
                        <td>Medicines Total:</td>
                        <td>₹{totals['medicines_total']:,.2f}</td>
                    </tr>
            """
        
        html += f"""
                    <tr class="total-row">
                        <td>Grand Total:</td>
                        <td>₹{totals.get('grand_total', 0):,.2f}</td>
                    </tr>
                </table>
            </div>
        """
    
    # Footer with signature and QR code
    html += """
            <div class="footer">
                <div class="signature-section">
                    <div class="signature-line"></div>
                    <div>Doctor's Signature</div>
                </div>
    """
    
    if include_qr:
        html += f"""
                <div class="qr-section">
                    <div class="qr-code">
                        <img src="/api/inventory/prescriptions/{prescription.id}/qr.png" alt="QR Code" width="60" height="60">
                    </div>
                    <div style="font-size: 10px; color: #6b7280;">
                        Scan to view online
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_prescription_docx(prescription, patient, visit, branding, include_qr):
    """Generate DOCX file for prescription"""
    # This would require python-docx library
    # For now, return a placeholder
    raise HTTPException(status_code=501, detail="DOCX export not yet implemented")
