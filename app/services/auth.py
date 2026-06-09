from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction
from app.schemas.auth import UserRegister

INITIAL_BONUS_AMOUNT = 10_000
INITIAL_BONUS_TYPE = "INITIAL_BONUS"


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, user_in: UserRegister) -> User:
    user = User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.flush()

    db.add(
        WalletTransaction(
            user_id=user.id,
            amount=INITIAL_BONUS_AMOUNT,
            transaction_type=INITIAL_BONUS_TYPE,
            reference_id=None,
        )
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
