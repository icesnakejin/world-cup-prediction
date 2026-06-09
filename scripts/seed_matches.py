from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.market import Market
from app.models.match import Match

MATCH_WINNER_MARKET_TYPE = "match_winner"
OVER_UNDER_MARKET_TYPE = "over_under"
EXACT_SCORE_MARKET_TYPE = "exact_score"
OVER_UNDER_LINE = Decimal("2.5")
OVER_UNDER_MARKETS = {
    "OVER": Decimal("1.95"),
    "UNDER": Decimal("1.85"),
}
EXACT_SCORE_MARKETS = {
    "0-0": Decimal("8.00"),
    "1-0": Decimal("7.50"),
    "1-1": Decimal("6.50"),
    "2-1": Decimal("9.00"),
    "2-0": Decimal("10.00"),
    "2-2": Decimal("12.00"),
    "3-0": Decimal("14.00"),
    "3-1": Decimal("13.00"),
    "3-2": Decimal("17.00"),
    "3-3": Decimal("26.00"),
    "4-0": Decimal("30.00"),
    "4-1": Decimal("28.00"),
    "4-2": Decimal("34.00"),
    "4-3": Decimal("51.00"),
    "4-4": Decimal("81.00"),
    "0-1": Decimal("8.50"),
    "0-2": Decimal("11.00"),
    "1-2": Decimal("9.50"),
}

SAMPLE_MATCHES = [
    {
        "home_team": "United States",
        "away_team": "Mexico",
        "kickoff_time": datetime(2026, 6, 11, 19, 0, tzinfo=UTC),
        "markets": {
            "HOME_WIN": Decimal("2.10"),
            "DRAW": Decimal("3.25"),
            "AWAY_WIN": Decimal("3.40"),
        },
    },
    {
        "home_team": "Canada",
        "away_team": "France",
        "kickoff_time": datetime(2026, 6, 12, 20, 0, tzinfo=UTC),
        "markets": {
            "HOME_WIN": Decimal("4.75"),
            "DRAW": Decimal("3.60"),
            "AWAY_WIN": Decimal("1.80"),
        },
    },
    {
        "home_team": "Brazil",
        "away_team": "England",
        "kickoff_time": datetime(2026, 6, 13, 18, 0, tzinfo=UTC),
        "markets": {
            "HOME_WIN": Decimal("2.35"),
            "DRAW": Decimal("3.10"),
            "AWAY_WIN": Decimal("2.95"),
        },
    },
    {
        "home_team": "Argentina",
        "away_team": "Spain",
        "kickoff_time": datetime(2026, 6, 14, 21, 0, tzinfo=UTC),
        "markets": {
            "HOME_WIN": Decimal("2.55"),
            "DRAW": Decimal("3.20"),
            "AWAY_WIN": Decimal("2.70"),
        },
    },
]


def main() -> None:
    with SessionLocal() as db:
        created_matches = 0
        created_markets = 0

        for sample in SAMPLE_MATCHES:
            match = db.scalar(
                select(Match).where(
                    Match.home_team == sample["home_team"],
                    Match.away_team == sample["away_team"],
                    Match.kickoff_time == sample["kickoff_time"],
                )
            )

            if match is None:
                match = Match(
                    home_team=sample["home_team"],
                    away_team=sample["away_team"],
                    kickoff_time=sample["kickoff_time"],
                    status="scheduled",
                )
                db.add(match)
                db.flush()
                created_matches += 1

            for selection, odds in sample["markets"].items():
                existing_market = db.scalar(
                    select(Market).where(
                        Market.match_id == match.id,
                        Market.market_type == MATCH_WINNER_MARKET_TYPE,
                        Market.selection == selection,
                    )
                )
                if existing_market is not None:
                    continue

                db.add(
                    Market(
                        match_id=match.id,
                        market_type=MATCH_WINNER_MARKET_TYPE,
                        selection=selection,
                        line=None,
                        odds=odds,
                        status="OPEN",
                    )
                )
                created_markets += 1

            for selection, odds in OVER_UNDER_MARKETS.items():
                existing_market = db.scalar(
                    select(Market).where(
                        Market.match_id == match.id,
                        Market.market_type == OVER_UNDER_MARKET_TYPE,
                        Market.selection == selection,
                    )
                )
                if existing_market is not None:
                    continue

                db.add(
                    Market(
                        match_id=match.id,
                        market_type=OVER_UNDER_MARKET_TYPE,
                        selection=selection,
                        line=OVER_UNDER_LINE,
                        odds=odds,
                        status="OPEN",
                    )
                )
                created_markets += 1

            for selection, odds in EXACT_SCORE_MARKETS.items():
                existing_market = db.scalar(
                    select(Market).where(
                        Market.match_id == match.id,
                        Market.market_type == EXACT_SCORE_MARKET_TYPE,
                        Market.selection == selection,
                    )
                )
                if existing_market is not None:
                    continue

                db.add(
                    Market(
                        match_id=match.id,
                        market_type=EXACT_SCORE_MARKET_TYPE,
                        selection=selection,
                        line=None,
                        odds=odds,
                        status="OPEN",
                    )
                )
                created_markets += 1

        db.commit()

    print(f"Seed complete: created {created_matches} matches and {created_markets} markets.")


if __name__ == "__main__":
    main()
