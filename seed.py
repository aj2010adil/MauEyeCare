import asyncio
import csv
from pathlib import Path
from sqlalchemy import select

from database import get_session_maker
from config import settings
import models
from security import hash_password

async def seed_table(db, model, file_path: Path):
    """Generic function to seed a table from a CSV file if it's empty."""
    # Check if table has data
    if (await db.execute(select(model))).scalars().first():
        print(f"Table '{model.__tablename__}' already has data. Skipping seed.")
        return

    print(f"Seeding data for '{model.__tablename__}' from {file_path}...")
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        objects_to_add = []
        for row in reader:
            # Handle type conversion for integer fields
            if 'stock' in row and row['stock']:
                row['stock'] = int(row['stock'])
            objects_to_add.append(model(**row))
        
        if objects_to_add:
            db.add_all(objects_to_add)
            print(f"  Added {len(objects_to_add)} records.")

async def main():
    SessionLocal = get_session_maker()
    async with SessionLocal() as db:
        # Ensure default user
        admin_email = settings.bootstrap_admin_email
        stmt = select(models.User).where(models.User.email == admin_email)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            print(f"Default admin user '{admin_email}' not found. Creating it...")
            db.add(models.User(
                email=admin_email,
                full_name="Doctor",
                role="doctor",
                password_hash=hash_password(settings.bootstrap_admin_password)
            ))
        else:
            print(f"Default admin user '{admin_email}' already exists. Skipping.")

        # Seed inventory data
        data_dir = Path(__file__).parent / "data"
        await seed_table(db, models.Medicine, data_dir / "medicines.csv")
        await seed_table(db, models.Spectacle, data_dir / "spectacles.csv")

        await db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
