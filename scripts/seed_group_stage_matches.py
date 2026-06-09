from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, select

from app.data.world_cup_2026 import get_world_cup_2026_matches
from app.db.session import SessionLocal
from app.models.bet import Bet
from app.models.market import Market
from app.models.match import Match
from app.models.tournament_bet import TournamentBet
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction
from app.services.auth import INITIAL_BONUS_AMOUNT, INITIAL_BONUS_TYPE
from scripts.seed_matches import (
    EXACT_SCORE_MARKETS,
    EXACT_SCORE_MARKET_TYPE,
    MATCH_WINNER_MARKET_TYPE,
    OVER_UNDER_LINE,
    OVER_UNDER_MARKETS,
    OVER_UNDER_MARKET_TYPE,
)

MATCH_WINNER_MARKETS = {
    "HOME": Decimal("2.10"),
    "DRAW": Decimal("3.25"),
    "AWAY": Decimal("3.40"),
}


def _parse_kickoff(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _ensure_market(
    db,
    match_id: int,
    market_type: str,
    selection: str,
    odds: Decimal,
    line: Decimal | None = None,
) -> bool:
    existing_market = db.scalar(
        select(Market).where(
            Market.match_id == match_id,
            Market.market_type == market_type,
            Market.selection == selection,
        )
    )
    if existing_market is not None:
        return False

    db.add(
        Market(
            match_id=match_id,
            market_type=market_type,
            selection=selection,
            line=line,
            odds=odds,
            status="OPEN",
        )
    )
    return True


def main(replace_existing: bool = False) -> dict[str, int]:
    with SessionLocal() as db:
        deleted_bets = 0
        deleted_tournament_bets = 0
        deleted_markets = 0
        deleted_matches = 0
        deleted_wallet_transactions = 0
        reset_wallets = 0
        created_matches = 0
        created_markets = 0

        if replace_existing:
            deleted_bets = db.execute(delete(Bet)).rowcount or 0
            deleted_tournament_bets = db.execute(delete(TournamentBet)).rowcount or 0
            deleted_markets = db.execute(delete(Market)).rowcount or 0
            deleted_matches = db.execute(delete(Match)).rowcount or 0
            deleted_wallet_transactions = db.execute(delete(WalletTransaction)).rowcount or 0
            users = list(db.scalars(select(User)))
            for user in users:
                db.add(
                    WalletTransaction(
                        user_id=user.id,
                        amount=INITIAL_BONUS_AMOUNT,
                        transaction_type=INITIAL_BONUS_TYPE,
                        reference_id=None,
                    )
                )
                reset_wallets += 1

        for match_data in get_world_cup_2026_matches():
            kickoff = _parse_kickoff(str(match_data["kickoff_time"]))
            match = db.scalar(
                select(Match).where(Match.match_number == int(match_data["match_number"]))
            )
            if match is None:
                match = Match(
                    match_number=int(match_data["match_number"]),
                    kickoff_time=kickoff,
                    status="scheduled",
                )
                db.add(match)
                db.flush()
                created_matches += 1
            match.match_number = int(match_data["match_number"])
            match.stage = str(match_data["stage"])
            match.group = match_data["group"]
            match.home_team = match_data["home_team"]
            match.away_team = match_data["away_team"]
            match.home_placeholder = match_data["home_placeholder"]
            match.away_placeholder = match_data["away_placeholder"]
            match.kickoff_time = kickoff
            match.venue = match_data["venue"]
            match.status = str(match_data["status"])
            match.home_score = None
            match.away_score = None

            for selection, odds in MATCH_WINNER_MARKETS.items():
                created_markets += int(_ensure_market(db, match.id, MATCH_WINNER_MARKET_TYPE, selection, odds))

            for selection, odds in OVER_UNDER_MARKETS.items():
                created_markets += int(
                    _ensure_market(db, match.id, OVER_UNDER_MARKET_TYPE, selection, odds, OVER_UNDER_LINE)
                )

            for selection, odds in EXACT_SCORE_MARKETS.items():
                created_markets += int(_ensure_market(db, match.id, EXACT_SCORE_MARKET_TYPE, selection, odds))

        db.commit()

    result = {
        "deleted_bets": deleted_bets,
        "deleted_tournament_bets": deleted_tournament_bets,
        "deleted_markets": deleted_markets,
        "deleted_matches": deleted_matches,
        "deleted_wallet_transactions": deleted_wallet_transactions,
        "reset_wallets": reset_wallets,
        "created_matches": created_matches,
        "created_markets": created_markets,
        "total_matches": len(get_world_cup_2026_matches()),
    }
    print(
        "World Cup 2026 seed complete: "
        f"deleted {deleted_bets} match bets, {deleted_tournament_bets} tournament bets, "
        f"{deleted_markets} markets, {deleted_matches} matches, "
        f"and {deleted_wallet_transactions} wallet transactions; reset {reset_wallets} wallets; "
        f"created {created_matches} matches and {created_markets} markets."
    )
    return result


if __name__ == "__main__":
    main()
