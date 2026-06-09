from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallet import WalletRead
from app.services.wallet import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletRead)
def read_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> WalletRead:
    return WalletRead(balance=WalletService(db).get_balance(current_user.id))
