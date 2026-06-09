from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models.market import Market
from app.models.match import Match
from app.models.wallet_transaction import WalletTransaction
from app.services.settlement import BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE, BET_VOID_REFUND_TRANSACTION_TYPE, BET_WON_TRANSACTION_TYPE
from tests.conftest import TestingSessionLocal


def register_and_login(client: TestClient) -> str:
    register_response = client.post(
        "/auth/register",
        json={"username": "settler", "email": "ian@test.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "ian@test.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def seed_match_winner_markets() -> tuple[int, dict[str, int]]:
    with TestingSessionLocal() as db:
        match = Match(
            home_team="Brazil",
            away_team="England",
            kickoff_time=datetime.now(UTC) + timedelta(days=7),
            status="scheduled",
        )
        db.add(match)
        db.flush()

        markets = [
            Market(
                match_id=match.id,
                market_type="match_winner",
                selection="HOME_WIN",
                odds=Decimal("2.10"),
                status="OPEN",
            ),
            Market(
                match_id=match.id,
                market_type="match_winner",
                selection="DRAW",
                odds=Decimal("3.25"),
                status="OPEN",
            ),
            Market(
                match_id=match.id,
                market_type="match_winner",
                selection="AWAY_WIN",
                odds=Decimal("3.40"),
                status="OPEN",
            ),
        ]
        db.add_all(markets)
        db.commit()
        return match.id, {market.selection: market.id for market in markets}


def seed_over_under_markets() -> tuple[int, dict[str, int]]:
    with TestingSessionLocal() as db:
        match = Match(
            home_team="United States",
            away_team="Mexico",
            kickoff_time=datetime.now(UTC) + timedelta(days=7),
            status="scheduled",
        )
        db.add(match)
        db.flush()

        markets = [
            Market(
                match_id=match.id,
                market_type="over_under",
                selection="OVER",
                line=Decimal("2.5"),
                odds=Decimal("1.95"),
                status="OPEN",
            ),
            Market(
                match_id=match.id,
                market_type="over_under",
                selection="UNDER",
                line=Decimal("2.5"),
                odds=Decimal("1.85"),
                status="OPEN",
            ),
        ]
        db.add_all(markets)
        db.commit()
        return match.id, {market.selection: market.id for market in markets}


def seed_exact_score_markets() -> tuple[int, dict[str, int]]:
    with TestingSessionLocal() as db:
        match = Match(
            home_team="Argentina",
            away_team="Spain",
            kickoff_time=datetime.now(UTC) + timedelta(days=7),
            status="scheduled",
        )
        db.add(match)
        db.flush()

        markets = [
            Market(
                match_id=match.id,
                market_type="exact_score",
                selection="2-1",
                line=None,
                odds=Decimal("9.00"),
                status="OPEN",
            ),
            Market(
                match_id=match.id,
                market_type="exact_score",
                selection="1-1",
                line=None,
                odds=Decimal("6.50"),
                status="OPEN",
            ),
        ]
        db.add_all(markets)
        db.commit()
        return match.id, {market.selection: market.id for market in markets}


def test_update_result_settles_bets_and_is_idempotent() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_match_winner_markets()

    winning_bet_response = client.post(
        "/bets",
        headers=headers,
        json={"market_id": market_ids["HOME_WIN"], "stake": 100},
    )
    losing_bet_response = client.post(
        "/bets",
        headers=headers,
        json={"market_id": market_ids["AWAY_WIN"], "stake": 50},
    )

    assert winning_bet_response.status_code == 201
    assert losing_bet_response.status_code == 201
    assert client.get("/wallet", headers=headers).json() == {"balance": 9850}

    result_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )

    assert result_response.status_code == 200
    assert result_response.json()["status"] == "COMPLETED"
    assert result_response.json()["home_score"] == 2
    assert result_response.json()["away_score"] == 1

    my_bets = client.get("/bets/me", headers=headers).json()
    bets_by_selection = {bet["selection"]: bet for bet in my_bets}
    assert bets_by_selection["HOME_WIN"]["status"] == "WON"
    assert bets_by_selection["HOME_WIN"]["payout"] == 210
    assert bets_by_selection["AWAY_WIN"]["status"] == "LOST"
    assert bets_by_selection["AWAY_WIN"]["payout"] == 0
    assert client.get("/wallet", headers=headers).json() == {"balance": 10060}

    markets = client.get(f"/matches/{match_id}/markets").json()
    assert markets == []

    repeated_result_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )

    assert repeated_result_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10060}

    with TestingSessionLocal() as db:
        bet_won_transaction_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == BET_WON_TRANSACTION_TYPE)
        )
        assert bet_won_transaction_count == 1


def test_over_under_settlement_over_wins_on_three_goals() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_over_under_markets()

    over_response = client.post("/bets", headers=headers, json={"market_id": market_ids["OVER"], "stake": 100})
    under_response = client.post("/bets", headers=headers, json={"market_id": market_ids["UNDER"], "stake": 100})
    assert over_response.status_code == 201
    assert under_response.status_code == 201

    result_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )

    assert result_response.status_code == 200
    bets_by_selection = {bet["selection"]: bet for bet in client.get("/bets/me", headers=headers).json()}
    assert bets_by_selection["OVER"]["status"] == "WON"
    assert bets_by_selection["OVER"]["payout"] == 195
    assert bets_by_selection["UNDER"]["status"] == "LOST"
    assert bets_by_selection["UNDER"]["payout"] == 0


def test_over_under_settlement_under_wins_on_two_goals() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_over_under_markets()

    over_response = client.post("/bets", headers=headers, json={"market_id": market_ids["OVER"], "stake": 100})
    under_response = client.post("/bets", headers=headers, json={"market_id": market_ids["UNDER"], "stake": 100})
    assert over_response.status_code == 201
    assert under_response.status_code == 201

    result_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 1, "away_score": 1},
    )

    assert result_response.status_code == 200
    bets_by_selection = {bet["selection"]: bet for bet in client.get("/bets/me", headers=headers).json()}
    assert bets_by_selection["OVER"]["status"] == "LOST"
    assert bets_by_selection["OVER"]["payout"] == 0
    assert bets_by_selection["UNDER"]["status"] == "WON"
    assert bets_by_selection["UNDER"]["payout"] == 185


def test_exact_score_settlement() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_exact_score_markets()

    winning_response = client.post("/bets", headers=headers, json={"market_id": market_ids["2-1"], "stake": 100})
    losing_response = client.post("/bets", headers=headers, json={"market_id": market_ids["1-1"], "stake": 100})
    assert winning_response.status_code == 201
    assert losing_response.status_code == 201

    result_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )

    assert result_response.status_code == 200
    bets_by_selection = {bet["selection"]: bet for bet in client.get("/bets/me", headers=headers).json()}
    assert bets_by_selection["2-1"]["status"] == "WON"
    assert bets_by_selection["2-1"]["payout"] == 900
    assert bets_by_selection["1-1"]["status"] == "LOST"
    assert bets_by_selection["1-1"]["payout"] == 0


def test_unsettle_match_reverts_settlement_effects() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_match_winner_markets()

    bet_response = client.post(
        "/bets",
        headers=headers,
        json={"market_id": market_ids["HOME_WIN"], "stake": 100},
    )
    assert bet_response.status_code == 201

    settle_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )
    assert settle_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10110}

    unsettle_response = client.post(f"/admin/matches/{match_id}/unsettle", headers=headers)

    assert unsettle_response.status_code == 200
    unsettled_match = unsettle_response.json()
    assert unsettled_match["status"] == "scheduled"
    assert unsettled_match["home_score"] is None
    assert unsettled_match["away_score"] is None

    my_bets = client.get("/bets/me", headers=headers).json()
    assert my_bets[0]["status"] == "PENDING"
    assert my_bets[0]["payout"] is None
    assert client.get("/wallet", headers=headers).json() == {"balance": 9900}

    markets = client.get(f"/matches/{match_id}/markets").json()
    assert len(markets) == 3
    assert all(market["status"] == "OPEN" for market in markets)

    with TestingSessionLocal() as db:
        bet_won_transaction_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == BET_WON_TRANSACTION_TYPE)
        )
        reversal_transaction_count = db.scalar(
            select(func.count()).where(
                WalletTransaction.transaction_type == BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE
            )
        )
        assert bet_won_transaction_count == 1
        assert reversal_transaction_count == 1

    repeated_unsettle_response = client.post(f"/admin/matches/{match_id}/unsettle", headers=headers)

    assert repeated_unsettle_response.status_code == 400
    assert repeated_unsettle_response.json()["detail"] == "Match is not completed"

    with TestingSessionLocal() as db:
        reversal_transaction_count = db.scalar(
            select(func.count()).where(
                WalletTransaction.transaction_type == BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE
            )
        )
        assert reversal_transaction_count == 1


def test_unsettle_requires_completed_match() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, _ = seed_match_winner_markets()

    response = client.post(f"/admin/matches/{match_id}/unsettle", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Match is not completed"


def test_void_match_bets_refunds_pending_bets_and_is_idempotent() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_match_winner_markets()

    bet_response = client.post(
        "/bets",
        headers=headers,
        json={"market_id": market_ids["HOME_WIN"], "stake": 100},
    )
    assert bet_response.status_code == 201
    assert client.get("/wallet", headers=headers).json() == {"balance": 9900}

    void_response = client.post(f"/admin/matches/{match_id}/void-bets", headers=headers)
    assert void_response.status_code == 200
    assert void_response.json()["status"] == "scheduled"
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    my_bets = client.get("/bets/me", headers=headers).json()
    assert my_bets[0]["status"] == "VOID"
    assert my_bets[0]["payout"] is None

    repeated_void_response = client.post(f"/admin/matches/{match_id}/void-bets", headers=headers)
    assert repeated_void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    with TestingSessionLocal() as db:
        refund_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == BET_VOID_REFUND_TRANSACTION_TYPE)
        )
        assert refund_count == 1


def test_void_match_bets_reverses_settlement_and_refunds_stake() -> None:
    client = TestClient(app)
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    match_id, market_ids = seed_match_winner_markets()

    bet_response = client.post(
        "/bets",
        headers=headers,
        json={"market_id": market_ids["HOME_WIN"], "stake": 100},
    )
    assert bet_response.status_code == 201
    settle_response = client.patch(
        f"/admin/matches/{match_id}/result",
        headers=headers,
        json={"home_score": 2, "away_score": 1},
    )
    assert settle_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10110}

    void_response = client.post(f"/admin/matches/{match_id}/void-bets", headers=headers)
    assert void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    my_bets = client.get("/bets/me", headers=headers).json()
    assert my_bets[0]["status"] == "VOID"
    assert my_bets[0]["payout"] is None

    repeated_void_response = client.post(f"/admin/matches/{match_id}/void-bets", headers=headers)
    assert repeated_void_response.status_code == 200
    assert client.get("/wallet", headers=headers).json() == {"balance": 10000}

    with TestingSessionLocal() as db:
        payout_reversal_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE)
        )
        refund_count = db.scalar(
            select(func.count()).where(WalletTransaction.transaction_type == BET_VOID_REFUND_TRANSACTION_TYPE)
        )
        assert payout_reversal_count == 1
        assert refund_count == 1


def test_update_result_requires_authentication() -> None:
    match_id, _ = seed_match_winner_markets()
    client = TestClient(app)

    response = client.patch(
        f"/admin/matches/{match_id}/result",
        json={"home_score": 2, "away_score": 1},
    )

    assert response.status_code == 401
