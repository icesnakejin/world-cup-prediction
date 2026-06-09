from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models.tournament import Tournament
from app.models.tournament_bet import TournamentBet
from app.models.tournament_market import TournamentMarket
from app.models.wallet_transaction import WalletTransaction
from scripts.seed_tournaments import _tournament_winner_markets
from app.services.tournaments import (
    TOURNAMENT_BET_PLACED_TRANSACTION_TYPE,
    TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE,
    TOURNAMENT_BET_WON_TRANSACTION_TYPE,
    TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE,
)
from tests.conftest import TestingSessionLocal


def register_and_login(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={"username": "futurebettor", "email": "ian@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    response = client.post(
        "/auth/login",
        json={"email": "ian@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def seed_tournament() -> tuple[int, dict[str, int]]:
    with TestingSessionLocal() as db:
        tournament = Tournament(name="2026 FIFA World Cup", year=2026, status="OPEN")
        db.add(tournament)
        db.flush()

        markets = [
            TournamentMarket(
                tournament_id=tournament.id,
                market_type="tournament_winner",
                selection="Brazil",
                odds=Decimal("5.00"),
                status="OPEN",
            ),
            TournamentMarket(
                tournament_id=tournament.id,
                market_type="tournament_winner",
                selection="Argentina",
                odds=Decimal("6.00"),
                status="OPEN",
            ),
        ]
        db.add_all(markets)
        db.commit()
        return tournament.id, {market.selection: market.id for market in markets}


def test_tournament_and_market_apis() -> None:
    tournament_id, market_ids = seed_tournament()
    client = TestClient(app)

    tournaments_response = client.get("/tournaments")
    assert tournaments_response.status_code == 200
    assert tournaments_response.json()[0]["name"] == "2026 FIFA World Cup"

    tournament_response = client.get(f"/tournaments/{tournament_id}")
    assert tournament_response.status_code == 200
    assert tournament_response.json()["status"] == "OPEN"

    markets_response = client.get(f"/tournaments/{tournament_id}/markets")
    assert markets_response.status_code == 200
    assert {market["id"] for market in markets_response.json()} == set(market_ids.values())


def test_tournament_seed_covers_full_world_cup_field() -> None:
    markets = _tournament_winner_markets()
    assert len(markets) == 48
    assert "USA" in markets
    assert "United States" not in markets


def test_tournament_bet_placement_deducts_wallet() -> None:
    tournament_id, market_ids = seed_tournament()
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    bet_response = client.post(
        "/tournament-bets",
        headers=headers,
        json={"tournament_market_id": market_ids["Brazil"], "stake": 100},
    )

    assert bet_response.status_code == 201
    bet = bet_response.json()
    assert bet["tournament_id"] == tournament_id
    assert bet["selection"] == "Brazil"
    assert bet["odds"] == "5.00"
    assert bet["status"] == "PENDING"
    assert client.get("/wallet", headers=headers).json() == {"balance": 9900}

    my_bets_response = client.get("/tournament-bets/me", headers=headers)
    assert my_bets_response.status_code == 200
    assert my_bets_response.json()[0]["selection"] == "Brazil"

    with TestingSessionLocal() as db:
        transaction = db.scalar(
            select(WalletTransaction).where(WalletTransaction.transaction_type == TOURNAMENT_BET_PLACED_TRANSACTION_TYPE)
        )
        assert transaction is not None
        assert transaction.amount == -100


def test_tournament_settlement_unsettlement_and_idempotency() -> None:
    tournament_id, market_ids = seed_tournament()
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    brazil_bet = client.post(
        "/tournament-bets",
        headers=headers,
        json={"tournament_market_id": market_ids["Brazil"], "stake": 100},
    )
    argentina_bet = client.post(
        "/tournament-bets",
        headers=headers,
        json={"tournament_market_id": market_ids["Argentina"], "stake": 100},
    )
    assert brazil_bet.status_code == 201
    assert argentina_bet.status_code == 201
    assert client.get("/wallet", headers=headers).json() == {"balance": 9800}

    settle_response = client.patch(
        f"/admin/tournaments/{tournament_id}/winner",
        headers=headers,
        json={"winner_team": "Brazil"},
    )
    assert settle_response.status_code == 200
    assert settle_response.json()["status"] == "COMPLETED"
    assert settle_response.json()["winner_team"] == "Brazil"
    assert client.get("/wallet", headers=headers).json() == {"balance": 10300}

    repeated_settle_response = client.patch(
        f"/admin/tournaments/{tournament_id}/winner",
        headers=headers,
        json={"winner_team": "Brazil"},
    )
    assert repeated_settle_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10300}

    my_bets = client.get("/tournament-bets/me", headers=headers).json()
    bets_by_selection = {bet["selection"]: bet for bet in my_bets}
    assert bets_by_selection["Brazil"]["status"] == "WON"
    assert bets_by_selection["Brazil"]["payout"] == 500
    assert bets_by_selection["Argentina"]["status"] == "LOST"
    assert bets_by_selection["Argentina"]["payout"] == 0

    with TestingSessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(TournamentBet)) == 2
        won_transaction_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == TOURNAMENT_BET_WON_TRANSACTION_TYPE)
        )
        assert won_transaction_count == 1
        settled_market_count = db.scalar(
            select(func.count()).where(TournamentMarket.status == "SETTLED")
        )
        assert settled_market_count == 2

    unsettle_response = client.patch(f"/admin/tournaments/{tournament_id}/unsettle", headers=headers)
    assert unsettle_response.status_code == 200
    assert unsettle_response.json()["status"] == "OPEN"
    assert unsettle_response.json()["winner_team"] is None
    assert client.get("/wallet", headers=headers).json() == {"balance": 9800}

    repeated_unsettle_response = client.patch(f"/admin/tournaments/{tournament_id}/unsettle", headers=headers)
    assert repeated_unsettle_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 9800}

    with TestingSessionLocal() as db:
        reversal_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE)
        )
        assert reversal_count == 1
        assert db.scalar(select(func.count()).where(TournamentMarket.status == "OPEN")) == 2
        reset_bet_count = db.scalar(select(func.count()).where(TournamentBet.status == "PENDING", TournamentBet.payout.is_(None)))
        assert reset_bet_count == 2


def test_void_tournament_bets_refunds_pending_bets_and_is_idempotent() -> None:
    tournament_id, market_ids = seed_tournament()
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    bet_response = client.post(
        "/tournament-bets",
        headers=headers,
        json={"tournament_market_id": market_ids["Brazil"], "stake": 100},
    )
    assert bet_response.status_code == 201
    assert client.get("/wallet", headers=headers).json() == {"balance": 9900}

    void_response = client.patch(f"/admin/tournaments/{tournament_id}/void-bets", headers=headers)
    assert void_response.status_code == 200
    assert void_response.json()["status"] == "OPEN"
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    my_bets = client.get("/tournament-bets/me", headers=headers).json()
    assert my_bets[0]["status"] == "VOID"
    assert my_bets[0]["payout"] is None

    repeated_void_response = client.patch(f"/admin/tournaments/{tournament_id}/void-bets", headers=headers)
    assert repeated_void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    with TestingSessionLocal() as db:
        refund_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE)
        )
        assert refund_count == 1


def test_void_tournament_bets_reverses_settlement_and_refunds_stake() -> None:
    tournament_id, market_ids = seed_tournament()
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    bet_response = client.post(
        "/tournament-bets",
        headers=headers,
        json={"tournament_market_id": market_ids["Brazil"], "stake": 100},
    )
    assert bet_response.status_code == 201

    settle_response = client.patch(
        f"/admin/tournaments/{tournament_id}/winner",
        headers=headers,
        json={"winner_team": "Brazil"},
    )
    assert settle_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10400}

    void_response = client.patch(f"/admin/tournaments/{tournament_id}/void-bets", headers=headers)
    assert void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    my_bets = client.get("/tournament-bets/me", headers=headers).json()
    assert my_bets[0]["status"] == "VOID"
    assert my_bets[0]["payout"] is None

    repeated_void_response = client.patch(f"/admin/tournaments/{tournament_id}/void-bets", headers=headers)
    assert repeated_void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    with TestingSessionLocal() as db:
        reversal_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE)
        )
        refund_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE)
        )
        assert reversal_count == 1
        assert refund_count == 1
