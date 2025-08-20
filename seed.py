import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session_maker
from config import settings
from user import User
from security import hash_password
from patient import Patient


async def main():
    SessionLocal = get_session_maker()
    async with SessionLocal() as db:  # type: ignore[call-arg]
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
            print(f"Default admin user '{admin_email}' already exists. Skipping creation.")
        # Sample patients
        if not (await db.execute(select(Patient))).scalars().first():
            print("Seeding sample patients...")
            db.add_all([
                Patient(first_name="Amit", last_name="Sharma", gender="Male", age=34, phone="9990001111"),
                Patient(first_name="Priya", last_name="Verma", gender="Female", age=28, phone="8881112222"),
            ])
        else:
            print("Sample patients already exist. Skipping creation.")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
