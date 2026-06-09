from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bet import Bet
from app.models.user import User
from app.schemas.bet import BetCreate, BetMatchRead, BetRead
from app.services.bets import (
    InsufficientBalanceError,
    MarketClosedError,
    MarketNotFoundError,
    MatchAlreadyStartedError,
    list_bets_for_user,
    place_bet,
)

router = APIRouter(prefix="/bets", tags=["bets"])


def serialize_bet(bet: Bet) -> BetRead:
    return BetRead(
        bet_id=bet.id,
        market_id=bet.market_id,
        match_id=bet.match_id,
        match=BetMatchRead(
            home_team=bet.match.home_team,
            away_team=bet.match.away_team,
            kickoff_time=bet.match.kickoff_time,
        ),
        selection=bet.selection,
        odds=bet.odds,
        stake=bet.stake,
        payout=bet.payout,
        status=bet.status,
        created_at=bet.created_at,
    )


@router.post("", response_model=BetRead, status_code=status.HTTP_201_CREATED)
def create_bet(
    bet_in: BetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BetRead:
    try:
        bet = place_bet(db, user_id=current_user.id, market_id=bet_in.market_id, stake=bet_in.stake)
    except MarketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found") from None
    except MarketClosedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Market is not open") from None
    except MatchAlreadyStartedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match has already started") from None
    except InsufficientBalanceError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance") from None

    return serialize_bet(bet)


@router.get("/me", response_model=list[BetRead])
def read_my_bets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[BetRead]:
    return [serialize_bet(bet) for bet in list_bets_for_user(db, current_user.id)]
