from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.models.market import Market
from app.models.match import Match
from tests.conftest import TestingSessionLocal


def seed_match_with_markets() -> int:
    with TestingSessionLocal() as db:
        match = Match(
            home_team="United States",
            away_team="Mexico",
            kickoff_time=datetime(2026, 6, 11, 19, 0, tzinfo=UTC),
            status="scheduled",
        )
        db.add(match)
        db.flush()
        db.add_all(
            [
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
                Market(
                    match_id=match.id,
                    market_type="match_winner",
                    selection="HOME_WIN_CLOSED",
                    odds=Decimal("2.00"),
                    status="CLOSED",
                ),
            ]
        )
        db.commit()
        return match.id


def test_list_and_read_matches() -> None:
    match_id = seed_match_with_markets()
    client = TestClient(app)

    list_response = client.get("/matches")

    assert list_response.status_code == 200
    matches = list_response.json()
    assert len(matches) == 1
    assert matches[0]["id"] == match_id
    assert matches[0]["home_team"] == "United States"
    assert set(matches[0]) == {
        "id",
        "match_number",
        "stage",
        "group",
        "home_team",
        "away_team",
        "home_placeholder",
        "away_placeholder",
        "kickoff_time",
        "venue",
        "status",
        "home_score",
        "away_score",
    }

    detail_response = client.get(f"/matches/{match_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["away_team"] == "Mexico"


def test_read_match_not_found() -> None:
    client = TestClient(app)

    response = client.get("/matches/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found"


def test_list_open_markets_for_match() -> None:
    match_id = seed_match_with_markets()
    client = TestClient(app)

    response = client.get(f"/matches/{match_id}/markets")

    assert response.status_code == 200
    markets = response.json()
    assert len(markets) == 3
    assert {market["selection"] for market in markets} == {"HOME_WIN", "DRAW", "AWAY_WIN"}
    assert all(market["status"] == "OPEN" for market in markets)
    assert set(markets[0]) == {"id", "market_type", "selection", "line", "odds", "status"}
    assert markets[0]["line"] is None


def test_list_all_open_markets() -> None:
    match_id = seed_match_with_markets()
    client = TestClient(app)

    response = client.get("/matches/all-markets")

    assert response.status_code == 200
    markets = response.json()
    assert len(markets) == 3
    assert all(market["match_id"] == match_id for market in markets)
