from __future__ import annotations

import os
import time
from typing import Any

import httpx
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction

API_BASE_URL = os.getenv("SMOKE_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("SMOKE_ADMIN_EMAIL", "ian@test.com")
ADMIN_PASSWORD = os.getenv("SMOKE_ADMIN_PASSWORD", "password123")
SMOKE_PASSWORD = os.getenv("SMOKE_USER_PASSWORD", "password123")


def assert_status(response: httpx.Response, expected_status: int) -> None:
    if response.status_code != expected_status:
        raise RuntimeError(f"{response.request.method} {response.request.url} returned {response.status_code}: {response.text}")


def register_and_login(client: httpx.Client) -> tuple[str, str]:
    suffix = int(time.time())
    email = f"smoke-{suffix}@test.com"
    username = f"smoke{suffix}"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": SMOKE_PASSWORD},
    )
    assert_status(response, 201)

    login_response = client.post("/auth/login", json={"email": email, "password": SMOKE_PASSWORD})
    assert_status(login_response, 200)
    return email, login_response.json()["access_token"]


def login_admin(client: httpx.Client) -> str:
    response = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert_status(response, 200)
    return response.json()["access_token"]


def find_smoke_match(client: httpx.Client) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    response = client.get("/matches")
    assert_status(response, 200)

    for match in response.json():
        if match["status"] != "scheduled":
            continue
        markets_response = client.get(f"/matches/{match['id']}/markets")
        assert_status(markets_response, 200)
        markets = markets_response.json()
        by_key = {(market["market_type"], market["selection"]): market for market in markets}
        required = {
            "home_win": by_key.get(("match_winner", "HOME_WIN")),
            "over": by_key.get(("over_under", "OVER")),
            "exact": by_key.get(("exact_score", "2-1")),
        }
        if all(required.values()):
            return match, required

    raise RuntimeError("No scheduled match with HOME_WIN, OVER 2.5, and exact score 2-1 markets was found.")


def place_bet(client: httpx.Client, token: str, market_id: int, stake: int) -> dict[str, Any]:
    response = client.post(
        "/bets",
        headers={"Authorization": f"Bearer {token}"},
        json={"market_id": market_id, "stake": stake},
    )
    assert_status(response, 201)
    return response.json()


def ledger_balance_for_email(email: str) -> int:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            raise RuntimeError(f"Smoke user {email} was not found in the database.")
        balance = db.scalar(select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(WalletTransaction.user_id == user.id))
        return int(balance)


def main() -> None:
    with httpx.Client(base_url=API_BASE_URL, timeout=10) as client:
        health_response = client.get("/health")
        assert_status(health_response, 200)

        smoke_email, user_token = register_and_login(client)
        admin_token = login_admin(client)

        wallet_response = client.get("/wallet", headers={"Authorization": f"Bearer {user_token}"})
        assert_status(wallet_response, 200)
        assert wallet_response.json()["balance"] == 10000

        match, markets = find_smoke_match(client)
        place_bet(client, user_token, markets["home_win"]["id"], 100)
        place_bet(client, user_token, markets["exact"]["id"], 100)
        place_bet(client, user_token, markets["over"]["id"], 100)

        wallet_after_bets = client.get("/wallet", headers={"Authorization": f"Bearer {user_token}"})
        assert_status(wallet_after_bets, 200)
        assert wallet_after_bets.json()["balance"] == 9700

        settle_response = client.patch(
            f"/admin/matches/{match['id']}/result",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"home_score": 2, "away_score": 1},
        )
        assert_status(settle_response, 200)

        bets_response = client.get("/bets/me", headers={"Authorization": f"Bearer {user_token}"})
        assert_status(bets_response, 200)
        statuses = {bet["status"] for bet in bets_response.json()}
        assert statuses == {"WON"}

        wallet_after_settlement = client.get("/wallet", headers={"Authorization": f"Bearer {user_token}"})
        assert_status(wallet_after_settlement, 200)
        api_balance = wallet_after_settlement.json()["balance"]
        ledger_balance = ledger_balance_for_email(smoke_email)
        assert api_balance == ledger_balance

    print("Smoke test passed.")
    print(f"Smoke user: {smoke_email}")
    print(f"Final wallet balance: {api_balance}")


if __name__ == "__main__":
    main()
