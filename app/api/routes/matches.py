from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import MarketRead, MatchMarketRead, MatchRead
from app.services.matches import get_match_by_id, list_matches, list_open_markets_for_match, list_open_markets_for_matches

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchRead])
def read_matches(db: Session = Depends(get_db)) -> list[MatchRead]:
    return list_matches(db)


@router.get("/all-markets", response_model=list[MatchMarketRead])
def read_all_match_markets(db: Session = Depends(get_db)) -> list[MatchMarketRead]:
    markets = list_open_markets_for_matches(db)
    return [
        MatchMarketRead(
            id=market.id,
            match_id=market.match_id,
            market_type=market.market_type,
            selection=market.selection,
            line=market.line,
            odds=market.odds,
            status=market.status,
        )
        for market in markets
    ]


@router.get("/{match_id}", response_model=MatchRead)
def read_match(match_id: int, db: Session = Depends(get_db)) -> MatchRead:
    match = get_match_by_id(db, match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.get("/{match_id}/markets", response_model=list[MarketRead])
def read_match_markets(match_id: int, db: Session = Depends(get_db)) -> list[MarketRead]:
    match = get_match_by_id(db, match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return list_open_markets_for_match(db, match_id)
