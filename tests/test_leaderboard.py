from fastapi.testclient import TestClient

from app.main import app
from app.models.wallet_transaction import WalletTransaction
from tests.conftest import TestingSessionLocal


def register_user(client: TestClient, username: str, email: str) -> int:
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def add_wallet_transaction(user_id: int, amount: int, transaction_type: str) -> None:
    with TestingSessionLocal() as db:
        db.add(
            WalletTransaction(
                user_id=user_id,
                amount=amount,
                transaction_type=transaction_type,
                reference_id=None,
            )
        )
        db.commit()


def test_leaderboard_orders_users_by_wallet_balance() -> None:
    client = TestClient(app)
    user_1 = register_user(client, "ian", "ian@example.com")
    user_2 = register_user(client, "alex", "alex@example.com")
    user_3 = register_user(client, "sam", "sam@example.com")

    add_wallet_transaction(user_1, 110, "TEST_ADJUSTMENT")
    add_wallet_transaction(user_2, -200, "TEST_ADJUSTMENT")
    add_wallet_transaction(user_3, 500, "TEST_ADJUSTMENT")

    response = client.get("/leaderboard")

    assert response.status_code == 200
    leaderboard = response.json()
    assert leaderboard == [
        {"rank": 1, "user_id": user_3, "username": "sam", "balance": 10500},
        {"rank": 2, "user_id": user_1, "username": "ian", "balance": 10110},
        {"rank": 3, "user_id": user_2, "username": "alex", "balance": 9800},
    ]


def test_leaderboard_limit() -> None:
    client = TestClient(app)
    register_user(client, "ian", "ian@example.com")
    register_user(client, "alex", "alex@example.com")

    response = client.get("/leaderboard?limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["rank"] == 1
