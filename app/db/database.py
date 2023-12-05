from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base # функция declarative_base была перемещена в sqlalchemy.orm начиная с версии 2.0 SQLAlchemy

from sqlalchemy.orm import sessionmaker

from app.config import (DB_HOST, DB_NAME, DB_PORT, POSTGRES_PASSWORD,
                        POSTGRES_USER)

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session
        await session.commit()
