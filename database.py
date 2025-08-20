from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

from config import settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global engine
    if engine is None:
        # The database_url from settings is already configured for asyncpg
        engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    return engine


def get_session_maker() -> sessionmaker[AsyncSession]:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = get_session_maker()
    async with SessionLocal() as session:  # type: ignore[call-arg]
        try:
            yield session
        finally:
            await session.close()


def create_start_app_handler(app):
    async def start_app() -> None:
        # Warm up connection
        async with get_engine().begin() as conn:
            await conn.execute(text("SELECT 1"))
    return start_app


def create_stop_app_handler(app):
    async def stop_app() -> None:
        global engine
        if engine is not None:
            await engine.dispose()
            engine = None
    return stop_app
