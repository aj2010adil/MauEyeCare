import asyncio
import csv
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session_maker
from config import settings
from user import User
from product import Product
from security import hash_password

async def seed_products_from_csv(db: AsyncSession, file_path: Path, category: str):
    """Idempotent seeding of products for a specific category from a CSV."""
    print(f"Checking for '{category}' products from {file_path.name}...")
    
    # Check if products of this category already exist
    stmt = select(Product).where(Product.category == category).limit(1)
    if (await db.execute(stmt)).scalars().first():
        print(f"  '{category}' products already exist. Skipping.")
        return

    print(f"  Seeding '{category}' products...")
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        objects_to_add = []
        for row in reader:
            # Convert numeric types, providing defaults if missing
            for key in ['price', 'mrp', 'gst_rate']:
                if key in row and row[key]:
                    row[key] = float(row[key])
                else:
                    row.pop(key, None) # Remove if empty to use model default
            objects_to_add.append(Product(**row))
    
    if objects_to_add:
        db.add_all(objects_to_add)
        print(f"  Added {len(objects_to_add)} '{category}' products.")

async def main():
    SessionLocal = get_session_maker()
    async with SessionLocal() as db:
        # Ensure default user
        admin_email = settings.bootstrap_admin_email
        stmt = select(User).where(User.email == admin_email)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            print(f"Default admin user '{admin_email}' not found. Creating it...")
            db.add(User(
                email=admin_email,
                full_name="Doctor",
                role="doctor",
                password_hash=hash_password(settings.bootstrap_admin_password)
            ))
        else:
            print(f"Default admin user '{admin_email}' already exists. Skipping.")

        # Seed product data for prescription writer
        data_dir = Path(__file__).parent / "data"
        await seed_products_from_csv(db, data_dir / "medicines.csv", "medicine")
        await seed_products_from_csv(db, data_dir / "spectacles.csv", "frame")

        await db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
