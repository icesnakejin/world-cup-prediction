from decimal import Decimal

from sqlalchemy import select

from app.data.world_cup_2026 import GROUP_STAGE_MATCHES
from app.db.session import SessionLocal
from app.models.tournament import Tournament
from app.models.tournament_market import TournamentMarket

TOURNAMENT_NAME = "2026 FIFA World Cup"
TOURNAMENT_YEAR = 2026
TOURNAMENT_WINNER_MARKET_TYPE = "tournament_winner"


def _full_tournament_teams() -> list[str]:
    teams: list[str] = []
    for _group, home_team, away_team, _kickoff_time in GROUP_STAGE_MATCHES:
        for team in (home_team, away_team):
            normalized_team = "USA" if team == "United States" else team
            if normalized_team not in teams:
                teams.append(normalized_team)
    return teams


def _tournament_winner_markets() -> dict[str, Decimal]:
    featured_odds = {
        "Brazil": Decimal("5.0"),
        "Argentina": Decimal("6.0"),
        "France": Decimal("6.5"),
        "Spain": Decimal("7.0"),
        "England": Decimal("8.0"),
        "Germany": Decimal("10.0"),
        "Portugal": Decimal("12.0"),
        "Netherlands": Decimal("14.0"),
        "USA": Decimal("30.0"),
        "Mexico": Decimal("40.0"),
    }

    longshot_start = Decimal("45.0")
    longshot_step = Decimal("2.5")
    markets: dict[str, Decimal] = {}
    longshot_index = 0

    for team in _full_tournament_teams():
        odds = featured_odds.get(team)
        if odds is None:
            odds = longshot_start + (longshot_step * longshot_index)
            longshot_index += 1
        markets[team] = odds

    return markets


def main() -> None:
    with SessionLocal() as db:
        created_tournaments = 0
        created_markets = 0

        tournament = db.scalar(
            select(Tournament).where(
                Tournament.name == TOURNAMENT_NAME,
                Tournament.year == TOURNAMENT_YEAR,
            )
        )
        if tournament is None:
            tournament = Tournament(name=TOURNAMENT_NAME, year=TOURNAMENT_YEAR, status="OPEN")
            db.add(tournament)
            db.flush()
            created_tournaments += 1

        for selection, odds in _tournament_winner_markets().items():
            existing_market = db.scalar(
                select(TournamentMarket).where(
                    TournamentMarket.tournament_id == tournament.id,
                    TournamentMarket.market_type == TOURNAMENT_WINNER_MARKET_TYPE,
                    TournamentMarket.selection == selection,
                )
            )
            if existing_market is not None:
                continue

            db.add(
                TournamentMarket(
                    tournament_id=tournament.id,
                    market_type=TOURNAMENT_WINNER_MARKET_TYPE,
                    selection=selection,
                    odds=odds,
                    status="OPEN",
                )
            )
            created_markets += 1

        db.commit()

    print(f"Seed complete: created {created_tournaments} tournaments and {created_markets} tournament markets.")


if __name__ == "__main__":
    main()
