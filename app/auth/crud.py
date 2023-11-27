from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User

from .security import get_password_hash


async def create_user(db: AsyncSession, username: str, password: str):
    """Создание нового пользователя в БД."""

    user = User(username=username,
                hashed_password=get_password_hash(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, username: str):
    """Получение пользователя по имени из БД."""

    result = await db.execute(select(User).filter(
        User.username == username))
    user = result.scalars().first()
    return user
