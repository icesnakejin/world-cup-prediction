from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import MarketRead, MatchRead
from app.services.matches import get_match_by_id, list_matches, list_open_markets_for_match

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchRead])
def read_matches(db: Session = Depends(get_db)) -> list[MatchRead]:
    return list_matches(db)


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
