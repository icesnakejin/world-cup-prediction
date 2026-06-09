from __future__ import annotations

import os

from sqlalchemy import exists, select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction
from app.services.auth import INITIAL_BONUS_AMOUNT, INITIAL_BONUS_TYPE
from scripts.seed_matches import main as seed_matches
from scripts.seed_tournaments import main as seed_tournaments

DEFAULT_SEED_USERS = [
    ("ian", "ian@test.com", "password123"),
    ("demo", "demo@test.com", "password123"),
]


def configured_seed_users() -> list[tuple[str, str, str]]:
    raw_users = os.getenv("SEED_USERS")
    if not raw_users:
        return DEFAULT_SEED_USERS

    users: list[tuple[str, str, str]] = []
    for raw_user in raw_users.split(","):
        parts = [part.strip() for part in raw_user.split(":")]
        if len(parts) != 3 or not all(parts):
            raise ValueError("SEED_USERS entries must use username:email:password format.")
        users.append((parts[0], parts[1], parts[2]))
    return users


def seed_users() -> None:
    with SessionLocal() as db:
        created_users = 0
        created_wallet_transactions = 0

        for username, email, password in configured_seed_users():
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(username=username, email=email, hashed_password=hash_password(password))
                db.add(user)
                db.flush()
                created_users += 1

            has_initial_bonus = db.scalar(
                select(
                    exists().where(
                        WalletTransaction.user_id == user.id,
                        WalletTransaction.transaction_type == INITIAL_BONUS_TYPE,
                    )
                )
            )
            if not has_initial_bonus:
                db.add(
                    WalletTransaction(
                        user_id=user.id,
                        amount=INITIAL_BONUS_AMOUNT,
                        transaction_type=INITIAL_BONUS_TYPE,
                        reference_id=None,
                    )
                )
                created_wallet_transactions += 1

        db.commit()

    print(
        "Seed users complete: "
        f"created {created_users} users and {created_wallet_transactions} wallet transactions."
    )


def main() -> None:
    seed_users()
    seed_matches()
    seed_tournaments()


if __name__ == "__main__":
    main()
