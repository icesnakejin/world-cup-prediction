from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.models.market import Market
from app.models.match import Match
from tests.conftest import TestingSessionLocal


def register_and_login(client: TestClient) -> str:
    register_response = client.post(
        "/auth/register",
        json={"username": "bettor", "email": "bettor@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "bettor@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def seed_open_market() -> int:
    with TestingSessionLocal() as db:
        match = Match(
            home_team="Brazil",
            away_team="England",
            kickoff_time=datetime.now(UTC) + timedelta(days=7),
            status="scheduled",
        )
        db.add(match)
        db.flush()

        market = Market(
            match_id=match.id,
            market_type="match_winner",
            selection="HOME_WIN",
            odds=Decimal("2.35"),
            status="OPEN",
        )
        db.add(market)
        db.commit()
        return market.id


def test_wallet_balance_and_place_bet_flow() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    market_id = seed_open_market()

    wallet_response = client.get("/wallet", headers=headers)

    assert wallet_response.status_code == 200
    assert wallet_response.json() == {"balance": 10000}

    bet_response = client.post("/bets", headers=headers, json={"market_id": market_id, "stake": 100})

    assert bet_response.status_code == 201
    bet = bet_response.json()
    assert bet["market_id"] == market_id
    assert bet["selection"] == "HOME_WIN"
    assert bet["stake"] == 100
    assert bet["status"] == "PENDING"

    updated_wallet_response = client.get("/wallet", headers=headers)

    assert updated_wallet_response.status_code == 200
    assert updated_wallet_response.json() == {"balance": 9900}

    my_bets_response = client.get("/bets/me", headers=headers)

    assert my_bets_response.status_code == 200
    assert len(my_bets_response.json()) == 1
    assert my_bets_response.json()[0]["bet_id"] == bet["bet_id"]
    assert my_bets_response.json()[0]["match"]["home_team"] == "Brazil"
    assert my_bets_response.json()[0]["match"]["away_team"] == "England"
    assert "kickoff_time" in my_bets_response.json()[0]["match"]


def test_cannot_place_bet_without_sufficient_balance() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    market_id = seed_open_market()

    response = client.post("/bets", headers=headers, json={"market_id": market_id, "stake": 10001})

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}
