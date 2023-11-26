from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from .crud import create_user, get_user
from .schemas import LoginRequest, Token, User, UserCreate
from .security import create_access_token

user_router = APIRouter()


@user_router.post("/token", response_model=Token)
async def login_for_access_token(login_request: LoginRequest,
                                 db: Session = Depends(get_db)):
    user = await get_user(db, login_request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/users/", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")
    return await create_user(db=db, username=user.username,
                             password=user.password)
