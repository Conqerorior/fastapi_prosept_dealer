from sqlalchemy import Column, Integer, String

from app.db.database import Base

from .security import pwd_context


class User(Base):
    """Таблица пользователей."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)
