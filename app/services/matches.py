from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market import Market
from app.models.match import Match

OPEN_MARKET_STATUS = "OPEN"


def list_matches(db: Session) -> list[Match]:
    return list(db.scalars(select(Match).order_by(Match.match_number.nullslast(), Match.kickoff_time, Match.id)))


def get_match_by_id(db: Session, match_id: int) -> Match | None:
    return db.get(Match, match_id)


def list_open_markets_for_match(db: Session, match_id: int) -> list[Market]:
    return list(
        db.scalars(
            select(Market)
            .where(Market.match_id == match_id, Market.status == OPEN_MARKET_STATUS)
            .order_by(Market.id)
        )
    )
