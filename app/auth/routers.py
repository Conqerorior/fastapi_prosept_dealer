from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from .crud import create_user, get_user
from .schemas import LoginRequest, Token, User, UserCreate
from .security import create_access_token, pwd_context

user_router = APIRouter()


@user_router.post("/token", response_model=Token,
                  summary='Получение JWT токена',
                  tags=['Аутентификация'])
async def login_for_access_token(login_request: LoginRequest,
                                 db: AsyncSession = Depends(get_db)):
    """Аутентификация пользователя, получение JWT-токена."""

    user = await get_user(db, login_request.username)
    if not user or not pwd_context.verify(login_request.password,
                                          user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/users/", response_model=User,
                  summary='Регистрация пользователей',
                  tags=['Аутентификация'])
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя."""

    db_user = await get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")
    return await create_user(db=db, username=user.username,
                             password=user.password)
