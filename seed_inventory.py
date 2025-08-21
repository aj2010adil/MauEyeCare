import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from spectacle import Spectacle
from medicine import Medicine


async def seed_inventory():
    """Seed the database with sample inventory data"""
    async for db in get_db_session():
        # Sample spectacles
        spectacles = [
            {
                "name": "Ray-Ban Aviator Classic",
                "brand": "Ray-Ban",
                "price": 8500.0,
                "frame_material": "Metal",
                "frame_shape": "Aviator",
                "lens_type": "Sunglasses",
                "gender": "Unisex",
                "age_group": "Adult",
                "description": "Classic aviator sunglasses with gold-tone metal frame",
                "specifications": {
                    "lens_width": "58mm",
                    "bridge_width": "14mm",
                    "temple_length": "135mm",
                    "lens_material": "Glass",
                    "polarized": True
                },
                "quantity": 15,
                "in_stock": True
            },
            {
                "name": "Oakley Holbrook",
                "brand": "Oakley",
                "price": 12000.0,
                "frame_material": "Plastic",
                "frame_shape": "Rectangle",
                "lens_type": "Sunglasses",
                "gender": "Unisex",
                "age_group": "Adult",
                "description": "Modern rectangular sunglasses with O Matter frame",
                "specifications": {
                    "lens_width": "59mm",
                    "bridge_width": "18mm",
                    "temple_length": "135mm",
                    "lens_material": "Plutonite",
                    "polarized": True
                },
                "quantity": 8,
                "in_stock": True
            },
            {
                "name": "Titan Eyeplus Rimless",
                "brand": "Titan",
                "price": 3500.0,
                "frame_material": "Titanium",
                "frame_shape": "Rimless",
                "lens_type": "Prescription",
                "gender": "Unisex",
                "age_group": "Adult",
                "description": "Lightweight rimless titanium frames",
                "specifications": {
                    "lens_width": "52mm",
                    "bridge_width": "18mm",
                    "temple_length": "140mm",
                    "lens_material": "High Index",
                    "anti_reflective": True
                },
                "quantity": 12,
                "in_stock": True
            },
            {
                "name": "Vincent Chase Round",
                "brand": "Vincent Chase",
                "price": 1800.0,
                "frame_material": "Acetate",
                "frame_shape": "Round",
                "lens_type": "Prescription",
                "gender": "Unisex",
                "age_group": "Adult",
                "description": "Classic round frames with acetate material",
                "specifications": {
                    "lens_width": "50mm",
                    "bridge_width": "18mm",
                    "temple_length": "135mm",
                    "lens_material": "CR-39",
                    "anti_reflective": True
                },
                "quantity": 20,
                "in_stock": True
            },
            {
                "name": "Fastrack Sports",
                "brand": "Fastrack",
                "price": 2500.0,
                "frame_material": "Plastic",
                "frame_shape": "Sports",
                "lens_type": "Sunglasses",
                "gender": "Unisex",
                "age_group": "Youth",
                "description": "Sporty sunglasses for active lifestyle",
                "specifications": {
                    "lens_width": "60mm",
                    "bridge_width": "16mm",
                    "temple_length": "130mm",
                    "lens_material": "Polycarbonate",
                    "polarized": False
                },
                "quantity": 25,
                "in_stock": True
            }
        ]

        # Sample medicines
        medicines = [
            {
                "name": "Artificial Tears",
                "brand": "Generic",
                "category": "Eye Care",
                "dosage": "1-2 drops as needed",
                "price": 150.0,
                "description": "Lubricating eye drops for dry eyes",
                "specifications": {
                    "volume": "10ml",
                    "preservative_free": True,
                    "suitable_for_contacts": True
                },
                "quantity": 50,
                "in_stock": True,
                "prescription_required": False
            },
            {
                "name": "Tropicamide 1%",
                "brand": "Generic",
                "category": "Dilation",
                "dosage": "1-2 drops before examination",
                "price": 200.0,
                "description": "Eye drops for pupil dilation during examination",
                "specifications": {
                    "volume": "5ml",
                    "prescription_required": True,
                    "duration": "4-6 hours"
                },
                "quantity": 30,
                "in_stock": True,
                "prescription_required": True
            },
            {
                "name": "Antibiotic Eye Drops",
                "brand": "Generic",
                "category": "Antibiotic",
                "dosage": "1 drop 4 times daily",
                "price": 300.0,
                "description": "Antibiotic eye drops for bacterial infections",
                "specifications": {
                    "volume": "5ml",
                    "prescription_required": True,
                    "course_duration": "7 days"
                },
                "quantity": 20,
                "in_stock": True,
                "prescription_required": True
            },
            {
                "name": "Vitamin A Supplements",
                "brand": "Generic",
                "category": "Vitamin",
                "dosage": "1 tablet daily",
                "price": 250.0,
                "description": "Vitamin A supplements for eye health",
                "specifications": {
                    "tablets_per_bottle": 30,
                    "strength": "5000 IU",
                    "prescription_required": False
                },
                "quantity": 40,
                "in_stock": True,
                "prescription_required": False
            },
            {
                "name": "Omega-3 Supplements",
                "brand": "Generic",
                "category": "Supplement",
                "dosage": "1 capsule daily",
                "price": 400.0,
                "description": "Omega-3 fatty acids for dry eye relief",
                "specifications": {
                    "capsules_per_bottle": 60,
                    "strength": "1000mg",
                    "prescription_required": False
                },
                "quantity": 35,
                "in_stock": True,
                "prescription_required": False
            }
        ]

        # Add spectacles
        for spectacle_data in spectacles:
            spectacle = Spectacle(**spectacle_data)
            db.add(spectacle)

        # Add medicines
        for medicine_data in medicines:
            medicine = Medicine(**medicine_data)
            db.add(medicine)

        await db.commit()
        print("Inventory seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_inventory())
