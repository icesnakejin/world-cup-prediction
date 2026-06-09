from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tournament import TournamentBetCreate, TournamentBetRead, TournamentMarketRead, TournamentRead
from app.services.tournaments import (
    TournamentClosedError,
    TournamentInsufficientBalanceError,
    TournamentMarketClosedError,
    TournamentMarketNotFoundError,
    get_tournament_by_id,
    list_open_tournament_markets,
    list_tournament_bets_for_user,
    list_tournaments,
    place_tournament_bet,
    serialize_tournament_bet,
)

router = APIRouter(tags=["tournaments"])


@router.get("/tournaments", response_model=list[TournamentRead])
def read_tournaments(db: Session = Depends(get_db)) -> list[TournamentRead]:
    return list_tournaments(db)


@router.get("/tournaments/{tournament_id}", response_model=TournamentRead)
def read_tournament(tournament_id: int, db: Session = Depends(get_db)) -> TournamentRead:
    tournament = get_tournament_by_id(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    return tournament


@router.get("/tournaments/{tournament_id}/markets", response_model=list[TournamentMarketRead])
def read_tournament_markets(tournament_id: int, db: Session = Depends(get_db)) -> list[TournamentMarketRead]:
    tournament = get_tournament_by_id(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    return list_open_tournament_markets(db, tournament_id)


@router.post("/tournament-bets", response_model=TournamentBetRead, status_code=status.HTTP_201_CREATED)
def create_tournament_bet(
    bet_in: TournamentBetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TournamentBetRead:
    try:
        bet = place_tournament_bet(
            db,
            user_id=current_user.id,
            tournament_market_id=bet_in.tournament_market_id,
            stake=bet_in.stake,
        )
    except TournamentMarketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament market not found") from None
    except TournamentMarketClosedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament market is not open") from None
    except TournamentClosedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament is not open") from None
    except TournamentInsufficientBalanceError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance") from None

    return serialize_tournament_bet(bet)


@router.get("/tournament-bets/me", response_model=list[TournamentBetRead])
def read_my_tournament_bets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TournamentBetRead]:
    return [serialize_tournament_bet(bet) for bet in list_tournament_bets_for_user(db, current_user.id)]
