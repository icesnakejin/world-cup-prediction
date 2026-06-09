from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.bet import Bet
from app.models.tournament_bet import TournamentBet
from app.models.tournament_market import TournamentMarket
from app.models.user import User
from app.schemas.admin import AdminMatchBetRead, AdminTournamentBetRead, MatchResultUpdate
from app.schemas.match import MatchRead
from app.schemas.tournament import TournamentRead, TournamentWinnerUpdate
from app.services.settlement import BetNotFoundError, MatchNotCompletedError, MatchNotFoundError, SettlementService
from app.services.tournaments import TournamentBetNotFoundError, TournamentNotCompletedError, TournamentNotFoundError, TournamentSettlementService

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.email.lower() not in settings.admin_email_set:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def serialize_admin_match_bet(bet: Bet) -> AdminMatchBetRead:
    return AdminMatchBetRead(
        id=bet.id,
        user_id=bet.user_id,
        username=bet.user.username,
        match_id=bet.match_id,
        home_team=bet.match.home_team,
        away_team=bet.match.away_team,
        kickoff_time=bet.match.kickoff_time,
        market_id=bet.market_id,
        market_type=bet.market.market_type,
        selection=bet.selection,
        odds=bet.odds,
        stake=bet.stake,
        payout=bet.payout,
        status=bet.status,
        created_at=bet.created_at,
    )


def serialize_admin_tournament_bet(bet: TournamentBet) -> AdminTournamentBetRead:
    tournament = bet.tournament_market.tournament
    return AdminTournamentBetRead(
        id=bet.id,
        user_id=bet.user_id,
        username=bet.user.username,
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        tournament_market_id=bet.tournament_market_id,
        market_type=bet.tournament_market.market_type,
        selection=bet.selection,
        odds=bet.odds,
        stake=bet.stake,
        payout=bet.payout,
        status=bet.status,
        created_at=bet.created_at,
    )


@router.get("/bets/matches", response_model=list[AdminMatchBetRead])
def read_admin_match_bets(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminMatchBetRead]:
    _ = current_user
    bets = list(
        db.scalars(
            select(Bet)
            .options(
                selectinload(Bet.user),
                selectinload(Bet.match),
                selectinload(Bet.market),
            )
            .order_by(Bet.created_at.desc(), Bet.id.desc())
        )
    )
    return [serialize_admin_match_bet(bet) for bet in bets]


@router.post("/bets/matches/{bet_id}/void", response_model=AdminMatchBetRead)
def void_admin_match_bet(
    bet_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> AdminMatchBetRead:
    _ = current_user
    try:
        bet = SettlementService(db).void_bet(bet_id)
    except BetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bet not found") from None
    return serialize_admin_match_bet(bet)


@router.get("/bets/tournaments", response_model=list[AdminTournamentBetRead])
def read_admin_tournament_bets(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminTournamentBetRead]:
    _ = current_user
    bets = list(
        db.scalars(
            select(TournamentBet)
            .options(
                selectinload(TournamentBet.user),
                selectinload(TournamentBet.tournament_market).selectinload(TournamentMarket.tournament),
            )
            .order_by(TournamentBet.created_at.desc(), TournamentBet.id.desc())
        )
    )
    return [serialize_admin_tournament_bet(bet) for bet in bets]


@router.post("/bets/tournaments/{bet_id}/void", response_model=AdminTournamentBetRead)
def void_admin_tournament_bet(
    bet_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> AdminTournamentBetRead:
    _ = current_user
    try:
        bet = TournamentSettlementService(db).void_tournament_bet(bet_id)
    except TournamentBetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament bet not found") from None
    return serialize_admin_tournament_bet(bet)


@router.patch("/matches/{match_id}/result", response_model=MatchRead)
def update_match_result(
    match_id: int,
    result: MatchResultUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> MatchRead:
    _ = current_user
    try:
        return SettlementService(db).update_result_and_settle(
            match_id=match_id,
            home_score=result.home_score,
            away_score=result.away_score,
        )
    except MatchNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found") from None


@router.post("/matches/{match_id}/unsettle", response_model=MatchRead)
def unsettle_match(
    match_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> MatchRead:
    _ = current_user
    try:
        return SettlementService(db).unsettle_match(match_id)
    except MatchNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found") from None
    except MatchNotCompletedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match is not completed") from None


@router.post("/matches/{match_id}/void-bets", response_model=MatchRead)
def void_match_bets(
    match_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> MatchRead:
    _ = current_user
    try:
        return SettlementService(db).void_match_bets(match_id)
    except MatchNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found") from None


@router.patch("/tournaments/{tournament_id}/winner", response_model=TournamentRead)
def update_tournament_winner(
    tournament_id: int,
    result: TournamentWinnerUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> TournamentRead:
    _ = current_user
    try:
        return TournamentSettlementService(db).settle_tournament(tournament_id, result.winner_team)
    except TournamentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found") from None


@router.patch("/tournaments/{tournament_id}/unsettle", response_model=TournamentRead)
def unsettle_tournament(
    tournament_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> TournamentRead:
    _ = current_user
    try:
        return TournamentSettlementService(db).unsettle_tournament(tournament_id)
    except TournamentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found") from None
    except TournamentNotCompletedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament is not completed") from None


@router.patch("/tournaments/{tournament_id}/void-bets", response_model=TournamentRead)
def void_tournament_bets(
    tournament_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> TournamentRead:
    _ = current_user
    try:
        return TournamentSettlementService(db).void_tournament_bets(tournament_id)
    except TournamentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found") from None
