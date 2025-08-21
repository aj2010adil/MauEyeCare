import asyncio
import httpx
import json


async def test_inventory_api():
    """Test the inventory API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Inventory API Endpoints...")
        
        # Test 1: Get spectacles
        print("\n1. Testing GET /api/inventory/spectacles")
        try:
            response = await client.get(f"{base_url}/api/inventory/spectacles")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Found {data.get('total', 0)} spectacles")
                if data.get('items'):
                    print(f"First spectacle: {data['items'][0]['name']}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: Get specific spectacle
        print("\n2. Testing GET /api/inventory/spectacles/1")
        try:
            response = await client.get(f"{base_url}/api/inventory/spectacles/1")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Spectacle: {data.get('name', 'N/A')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: Image analysis (mock)
        print("\n3. Testing POST /api/inventory/analyze-image")
        try:
            # Create a mock image file
            files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
            data = {"product_type": "spectacle"}
            response = await client.post(f"{base_url}/api/inventory/analyze-image", files=files, data=data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Analysis confidence: {data.get('analysis_confidence', 0)}")
                print(f"Found {len(data.get('tags', []))} tags")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: QR code generation
        print("\n4. Testing GET /api/inventory/prescriptions/1/qr")
        try:
            response = await client.get(f"{base_url}/api/inventory/prescriptions/1/qr")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"QR code generated for prescription {data.get('prescription_id')}")
                print(f"URL: {data.get('url')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nInventory API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_inventory_api())
