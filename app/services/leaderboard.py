from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wallet_transaction import WalletTransaction
from app.schemas.leaderboard import LeaderboardEntry

DEFAULT_LEADERBOARD_LIMIT = 50


def get_leaderboard(db: Session, limit: int = DEFAULT_LEADERBOARD_LIMIT) -> list[LeaderboardEntry]:
    balance = func.coalesce(func.sum(WalletTransaction.amount), 0).label("balance")
    rows = db.execute(
        select(
            User.id.label("user_id"),
            User.username,
            balance,
        )
        .join(WalletTransaction, WalletTransaction.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(desc(balance), User.id)
        .limit(limit)
    ).all()

    return [
        LeaderboardEntry(
            rank=index,
            user_id=row.user_id,
            username=row.username,
            balance=Decimal(row.balance or 0),
        )
        for index, row in enumerate(rows, start=1)
    ]
