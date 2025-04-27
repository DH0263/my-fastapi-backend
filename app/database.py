from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/academy_db")
SQLALCHEMY_DATABASE_URL = "sqlite:///./academy_schedule.db"

engine_async = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)

engine_sync = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def create_tables():
    Base.metadata.create_all(bind=engine_sync)
