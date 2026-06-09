from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.leaderboard import LeaderboardEntry
from app.services.leaderboard import DEFAULT_LEADERBOARD_LIMIT, get_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
def read_leaderboard(
    limit: int = Query(default=DEFAULT_LEADERBOARD_LIMIT, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LeaderboardEntry]:
    return get_leaderboard(db, limit=limit)
