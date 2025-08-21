import pytest
import asyncio
import httpx
from typing import AsyncGenerator
import json

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

class TestMauEyeCareIntegration:
    """Integration tests for complete doctor workflow"""
    
    @pytest.fixture
    async def client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with httpx.AsyncClient() as client:
            yield client
    
    @pytest.fixture
    async def auth_token(self, client: httpx.AsyncClient) -> str:
        """Bootstrap default user if needed and obtain access token"""
        # Ensure default admin/doctor account exists (idempotent)
        try:
            await client.post(f"{BASE_URL}/api/auth/bootstrap")
        except Exception:
            pass
        login_data = {
            "username": "doctor@maueyecare.com",
            "password": "MauEyeCareAdmin@2024",
            "grant_type": "password",
        }
        response = await client.post(f"{BASE_URL}/api/auth/login", data=login_data)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data["access_token"]
    
    async def test_health_check(self, client: httpx.AsyncClient):
        """Test if the API is running"""
        response = await client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    async def test_patient_workflow(self, client: httpx.AsyncClient, auth_token: str):
        """Test complete patient workflow"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. Create a new patient
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
            "age": 35,
            "gender": "Male"
        }
        response = await client.post(
            f"{BASE_URL}/api/patients",
            json=patient_data,
            headers=headers
        )
        assert response.status_code == 200
        patient = response.json()
        patient_id = patient["id"]
        
        # 2. Create a visit
        visit_data = {
            "patient_id": patient_id,
            "issue": "Blurred vision",
            "advice": "Need prescription glasses"
        }
        response = await client.post(
            f"{BASE_URL}/api/visits",
            json=visit_data,
            headers=headers
        )
        assert response.status_code == 200
        visit = response.json()
        visit_id = visit["id"]
        
        # 3. Create a prescription
        prescription_data = {
            "patient_id": patient_id,
            "visit_id": visit_id,
            "rx_values": {
                "od_sphere": -2.5,
                "od_cylinder": -0.5,
                "od_axis": 90,
                "os_sphere": -2.25,
                "os_cylinder": -0.25,
                "os_axis": 85
            },
            "spectacles": [
                {
                    "name": "Ray-Ban Aviator Classic",
                    "price": 8500.0,
                    "quantity": 1
                }
            ],
            "medicines": {
                "artificial_tears": {
                    "name": "Artificial Tears",
                    "dosage": "1-2 drops as needed",
                    "quantity": 1,
                    "price": 150.0
                }
            },
            "totals": {
                "spectacles_total": 8500.0,
                "medicines_total": 150.0,
                "grand_total": 8650.0
            }
        }
        response = await client.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription_data,
            headers=headers
        )
        assert response.status_code == 200
        prescription = response.json()
        prescription_id = prescription["id"]
        
        # 4. Export prescription as HTML
        export_data = {
            "format": "html",
            "include_qr": True
        }
        response = await client.post(
            f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/export",
            data=export_data,
            headers=headers
        )
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # 5. Generate QR code
        response = await client.get(
            f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/qr",
            headers=headers
        )
        assert response.status_code == 200
        qr_data = response.json()
        assert "qr_code" in qr_data
        assert "url" in qr_data
    
    async def test_spectacle_showcase(self, client: httpx.AsyncClient, auth_token: str):
        """Test spectacle showcase functionality"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. Get spectacles with filters
        response = await client.get(
            f"{BASE_URL}/api/inventory/spectacles?brand=Ray-Ban&in_stock=true",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        # 2. Get specific spectacle
        if data["items"]:
            spectacle_id = data["items"][0]["id"]
            response = await client.get(
                f"{BASE_URL}/api/inventory/spectacles/{spectacle_id}",
                headers=headers
            )
            assert response.status_code == 200
            spectacle = response.json()
            assert spectacle["id"] == spectacle_id
    
    async def test_image_analysis(self, client: httpx.AsyncClient, auth_token: str):
        """Test image analysis functionality"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a mock image file
        files = {"image": ("test_spectacle.jpg", b"fake image data", "image/jpeg")}
        data = {"product_type": "spectacle"}
        
        response = await client.post(
            f"{BASE_URL}/api/inventory/analyze-image",
            files=files,
            data=data,
            headers=headers
        )
        assert response.status_code == 200
        analysis = response.json()
        assert "tags" in analysis
        assert "suggestions" in analysis
        assert "analysis_confidence" in analysis
    
    async def test_inventory_upload(self, client: httpx.AsyncClient, auth_token: str):
        """Test inventory upload functionality"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test image upload
        files = {"file": ("test_product.jpg", b"fake image data", "image/jpeg")}
        data = {"product_type": "spectacle"}
        
        response = await client.post(
            f"{BASE_URL}/api/inventory/upload-image",
            files=files,
            data=data,
            headers=headers
        )
        assert response.status_code == 200
        upload_data = response.json()
        assert "image_url" in upload_data
        assert "filename" in upload_data
    
    async def test_prescription_export_formats(self, client: httpx.AsyncClient, auth_token: str):
        """Test prescription export in different formats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create a prescription (simplified)
        patient_data = {"first_name": "Test", "last_name": "Patient"}
        response = await client.post(
            f"{BASE_URL}/api/patients",
            json=patient_data,
            headers=headers
        )
        patient_id = response.json()["id"]
        
        prescription_data = {
            "patient_id": patient_id,
            "rx_values": {"od_sphere": -1.0, "os_sphere": -1.0}
        }
        response = await client.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription_data,
            headers=headers
        )
        prescription_id = response.json()["id"]
        
        # Test HTML export
        response = await client.post(
            f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/export",
            data={"format": "html"},
            headers=headers
        )
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Test PDF export (if implemented)
        response = await client.post(
            f"{BASE_URL}/api/inventory/prescriptions/{prescription_id}/export",
            data={"format": "pdf"},
            headers=headers
        )
        # PDF might not be implemented yet, so we accept 501
        assert response.status_code in [200, 501]
    
    async def test_error_handling(self, client: httpx.AsyncClient, auth_token: str):
        """Test error handling"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test invalid prescription ID
        response = await client.get(
            f"{BASE_URL}/api/inventory/prescriptions/99999/qr",
            headers=headers
        )
        assert response.status_code == 404
        
        # Test invalid spectacle ID
        response = await client.get(
            f"{BASE_URL}/api/inventory/spectacles/99999",
            headers=headers
        )
        assert response.status_code == 404
        
        # Test invalid image upload
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        data = {"product_type": "spectacle"}
        response = await client.post(
            f"{BASE_URL}/api/inventory/upload-image",
            files=files,
            data=data,
            headers=headers
        )
        assert response.status_code == 400


class TestFrontendIntegration:
    """Frontend integration tests"""
    
    async def test_frontend_accessible(self, client: httpx.AsyncClient):
        """Test if frontend is accessible"""
        response = await client.get(FRONTEND_URL)
        assert response.status_code == 200
    
    async def test_frontend_routes(self, client: httpx.AsyncClient):
        """Test frontend routes"""
        routes = [
            "/",
            "/login",
            "/dashboard",
            "/patients",
            "/prescriptions"
        ]
        
        for route in routes:
            response = await client.get(f"{FRONTEND_URL}{route}")
            # Frontend should return 200 or redirect to login
            assert response.status_code in [200, 302]


# Performance tests
class TestPerformance:
    """Performance tests"""
    
    async def test_spectacle_list_performance(self, client: httpx.AsyncClient, auth_token: str):
        """Test spectacle list performance"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        import time
        start_time = time.time()
        
        response = await client.get(
            f"{BASE_URL}/api/inventory/spectacles?limit=100",
            headers=headers
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
    
    async def test_concurrent_requests(self, client: httpx.AsyncClient, auth_token: str):
        """Test concurrent request handling"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def make_request():
            return await client.get(
                f"{BASE_URL}/api/inventory/spectacles",
                headers=headers
            )
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
