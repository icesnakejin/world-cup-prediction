from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.wallet_transaction import WalletTransaction


class WalletService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_balance(self, user_id: int) -> Decimal:
        amount = self.db.scalar(
            select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                WalletTransaction.user_id == user_id
            )
        )
        return Decimal(amount or 0)
