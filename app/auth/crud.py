from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import User

from .security import get_password_hash


async def create_user(db: Session, username: str, password: str):
    db_user = User(username=username,
                   hashed_password=get_password_hash(password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: Session, username: str):
    result = await db.execute(select(User).filter(
        User.username == username))
    user = result.scalars().first()
    return user
