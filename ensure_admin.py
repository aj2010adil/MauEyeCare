import asyncio
from sqlalchemy import select
from database import get_session_maker
from user import User
from security import hash_password
from config import settings

async def main() -> int:
    SessionLocal = get_session_maker()
    async with SessionLocal() as db:
        stmt = select(User).where(User.email == settings.bootstrap_admin_email)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if user:
            print(f"Default admin user '{settings.bootstrap_admin_email}' already exists. Skipping.")
            return 0
        user = User(
            email=settings.bootstrap_admin_email,
            full_name="Default Doctor",
            role="doctor",
            password_hash=hash_password(settings.bootstrap_admin_password),
        )
        db.add(user)
        await db.commit()
        print(f"Default admin user '{settings.bootstrap_admin_email}' created.")
        return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
