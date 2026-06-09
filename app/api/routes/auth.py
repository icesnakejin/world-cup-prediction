from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRead, UserRegister
from app.services.auth import authenticate_user, create_user, get_user_by_email, get_user_by_username

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> User:
    if get_user_by_email(db, str(user_in.email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if get_user_by_username(db, user_in.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    return create_user(db, user_in)


@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, str(credentials.email), credentials.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return Token(access_token=create_access_token(subject=str(user.id)))


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
