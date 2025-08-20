from __future__ import annotations

import asyncio

from sqlalchemy import select

from config import settings
from database import get_session_maker
from security import hash_password
from user import User


async def main():
    """
    Ensures the default admin user exists and has the correct password from settings.
    This is safe to run multiple times and will fix any password mismatches.
    """
    print("Connecting to the database...")
    SessionLocal = get_session_maker()
    async with SessionLocal() as db:  # type: ignore[call-arg]
        admin_email = settings.bootstrap_admin_email
        admin_password = settings.bootstrap_admin_password

        print(f"Checking for admin user: {admin_email}...")
        stmt = select(User).where(User.email == admin_email)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user:
            print("Admin user found. Resetting password to match current settings...")
            user.password_hash = hash_password(admin_password)
            user.is_active = True  # Also ensure the user is active
        else:
            print("Admin user not found. Creating a new admin user...")
            user = User(email=admin_email, full_name="Default Doctor", role="doctor", password_hash=hash_password(admin_password))
            db.add(user)

        await db.commit()
        print("\n[ OK ] Admin account is ready.")
        print(f"You can now log in with:\n  - Email: {admin_email}\n  - Password: {admin_password}")


if __name__ == "__main__":
    asyncio.run(main())