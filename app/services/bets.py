from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.bet import Bet
from app.models.market import Market
from app.models.wallet_transaction import WalletTransaction
from app.services.wallet import WalletService

BET_STATUS_PENDING = "PENDING"
BET_TRANSACTION_TYPE = "BET_PLACED"
MARKET_STATUS_OPEN = "OPEN"


class BetPlacementError(Exception):
    pass


class MarketNotFoundError(BetPlacementError):
    pass


class MarketClosedError(BetPlacementError):
    pass


class MatchAlreadyStartedError(BetPlacementError):
    pass


class InsufficientBalanceError(BetPlacementError):
    pass


def list_bets_for_user(db: Session, user_id: int) -> list[Bet]:
    return list(
        db.scalars(
            select(Bet)
            .options(selectinload(Bet.match))
            .where(Bet.user_id == user_id)
            .order_by(Bet.created_at.desc(), Bet.id.desc())
        )
    )


def place_bet(db: Session, user_id: int, market_id: int, stake: int) -> Bet:
    try:
        market = db.get(Market, market_id)
        if market is None:
            raise MarketNotFoundError

        if market.status != MARKET_STATUS_OPEN:
            raise MarketClosedError

        kickoff_time = market.match.kickoff_time
        if kickoff_time.tzinfo is None:
            kickoff_time = kickoff_time.replace(tzinfo=UTC)
        if kickoff_time <= datetime.now(UTC):
            raise MatchAlreadyStartedError

        balance = WalletService(db).get_balance(user_id)
        if balance < stake:
            raise InsufficientBalanceError

        bet = Bet(
            user_id=user_id,
            match_id=market.match_id,
            market_id=market.id,
            selection=market.selection,
            stake=stake,
            odds=market.odds,
            payout=None,
            status=BET_STATUS_PENDING,
        )
        db.add(bet)
        db.flush()

        db.add(
            WalletTransaction(
                user_id=user_id,
                amount=-stake,
                transaction_type=BET_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )

        db.commit()
        db.refresh(bet)
        return bet
    except Exception:
        db.rollback()
        raise
