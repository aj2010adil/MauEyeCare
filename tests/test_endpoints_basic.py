import pytest
import httpx
from typing import AsyncGenerator

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as c:
        yield c

@pytest.fixture
async def auth_token(client: httpx.AsyncClient) -> str:
    # Ensure default user exists (idempotent)
    try:
        await client.post(f"{BASE_URL}/api/auth/bootstrap")
    except Exception:
        pass
    data = {
        "username": "doctor@maueyecare.com",
        "password": "MauEyeCareAdmin@2024",
        "grant_type": "password",
    }
    resp = await client.post(f"{BASE_URL}/api/auth/login", data=data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]

@pytest.mark.asyncio
async def test_me_unauthorized(client: httpx.AsyncClient):
    resp = await client.get(f"{BASE_URL}/api/auth/me")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_authorized(client: httpx.AsyncClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert resp.status_code == 200
    me = resp.json()
    assert set(["id","email","role"]).issubset(me.keys())

@pytest.mark.asyncio
async def test_prescription_export_and_qr(client: httpx.AsyncClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create a patient
    pres_patient = {"first_name": "PDF", "last_name": "Tester"}
    r = await client.post(f"{BASE_URL}/api/patients", json=pres_patient, headers=headers)
    assert r.status_code == 200
    patient_id = r.json()["id"]

    # Create a prescription (minimal)
    rx_payload = {
        "patient_id": patient_id,
        "rx_values": {"od_sphere": -1.0, "os_sphere": -1.0},
        "totals": {"grand_total": 0}
    }
    r = await client.post(f"{BASE_URL}/api/prescriptions", json=rx_payload, headers=headers)
    assert r.status_code == 200
    prescription_id = r.json()["id"]

    # HTML export
    r = await client.post(f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/export", data={"format": "html"}, headers=headers)
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type","")

    # PDF export
    r = await client.post(f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/export", data={"format": "pdf"}, headers=headers)
    assert r.status_code == 200
    assert "application/pdf" in r.headers.get("content-type","")

    # QR JSON
    r = await client.get(f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/qr", headers=headers)
    assert r.status_code == 200
    data = r.json(); assert "qr_code" in data and "url" in data

    # QR PNG
    r = await client.get(f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/qr.png", headers=headers)
    assert r.status_code == 200
    assert "image/png" in r.headers.get("content-type","")

    # Invalid id
    r = await client.get(f"{BASE_URL}/api/inventory/prescriptions/999999/qr.png", headers=headers)
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_inventory_spectacles_list(client: httpx.AsyncClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = await client.get(f"{BASE_URL}/api/inventory/spectacles?limit=5", headers=headers)
    assert r.status_code == 200
    payload = r.json()
    assert "items" in payload and "total" in payload
