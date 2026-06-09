from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.wallet_transaction import WalletTransaction
from app.services.auth import INITIAL_BONUS_TYPE
from tests.conftest import TestingSessionLocal


def test_register_login_and_me() -> None:
    client = TestClient(app)

    register_response = client.post(
        "/auth/register",
        json={"username": "predictor", "email": "predictor@example.com", "password": "password123"},
    )

    assert register_response.status_code == 201
    registered_user = register_response.json()
    assert registered_user["email"] == "predictor@example.com"
    assert "balance" not in registered_user
    assert "hashed_password" not in registered_user

    with TestingSessionLocal() as db:
        wallet_transaction = db.scalar(select(WalletTransaction))
        assert wallet_transaction is not None
        assert wallet_transaction.transaction_type == INITIAL_BONUS_TYPE
        assert wallet_transaction.amount == 10000

    login_response = client.post(
        "/auth/login",
        json={"email": "predictor@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "predictor"
    assert "balance" not in me_response.json()
