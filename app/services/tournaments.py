from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.models.tournament import Tournament
from app.models.tournament_bet import TournamentBet
from app.models.tournament_market import TournamentMarket
from app.models.wallet_transaction import WalletTransaction
from app.schemas.tournament import TournamentBetRead
from app.services.wallet import WalletService

TOURNAMENT_STATUS_OPEN = "OPEN"
TOURNAMENT_STATUS_COMPLETED = "COMPLETED"
TOURNAMENT_MARKET_STATUS_OPEN = "OPEN"
TOURNAMENT_MARKET_STATUS_SETTLED = "SETTLED"
TOURNAMENT_BET_STATUS_PENDING = "PENDING"
TOURNAMENT_BET_STATUS_WON = "WON"
TOURNAMENT_BET_STATUS_LOST = "LOST"
TOURNAMENT_BET_STATUS_VOID = "VOID"
TOURNAMENT_BET_PLACED_TRANSACTION_TYPE = "TOURNAMENT_BET_PLACED"
TOURNAMENT_BET_WON_TRANSACTION_TYPE = "TOURNAMENT_BET_WON"
TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE = "TOURNAMENT_SETTLEMENT_REVERSED"
TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE = "TOURNAMENT_BET_VOID_REFUND"


class TournamentNotFoundError(Exception):
    pass


class TournamentMarketNotFoundError(Exception):
    pass


class TournamentMarketClosedError(Exception):
    pass


class TournamentClosedError(Exception):
    pass


class TournamentInsufficientBalanceError(Exception):
    pass


class TournamentNotCompletedError(Exception):
    pass


class TournamentBetNotFoundError(Exception):
    pass


def list_tournaments(db: Session) -> list[Tournament]:
    return list(db.scalars(select(Tournament).order_by(Tournament.year.desc(), Tournament.id)))


def get_tournament_by_id(db: Session, tournament_id: int) -> Tournament | None:
    return db.get(Tournament, tournament_id)


def list_open_tournament_markets(db: Session, tournament_id: int) -> list[TournamentMarket]:
    return list(
        db.scalars(
            select(TournamentMarket)
            .where(TournamentMarket.tournament_id == tournament_id, TournamentMarket.status == TOURNAMENT_MARKET_STATUS_OPEN)
            .order_by(TournamentMarket.odds, TournamentMarket.id)
        )
    )


def list_tournament_bets_for_user(db: Session, user_id: int) -> list[TournamentBet]:
    return list(
        db.scalars(
            select(TournamentBet)
            .options(selectinload(TournamentBet.tournament_market).selectinload(TournamentMarket.tournament))
            .where(TournamentBet.user_id == user_id)
            .order_by(TournamentBet.created_at.desc(), TournamentBet.id.desc())
        )
    )


def serialize_tournament_bet(bet: TournamentBet) -> TournamentBetRead:
    tournament = bet.tournament_market.tournament
    return TournamentBetRead(
        id=bet.id,
        tournament_market_id=bet.tournament_market_id,
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        selection=bet.selection,
        odds=bet.odds,
        stake=bet.stake,
        payout=bet.payout,
        status=bet.status,
        created_at=bet.created_at,
    )


def place_tournament_bet(db: Session, user_id: int, tournament_market_id: int, stake: int) -> TournamentBet:
    try:
        market = db.get(TournamentMarket, tournament_market_id)
        if market is None:
            raise TournamentMarketNotFoundError
        if market.status != TOURNAMENT_MARKET_STATUS_OPEN:
            raise TournamentMarketClosedError
        if market.tournament.status != TOURNAMENT_STATUS_OPEN:
            raise TournamentClosedError

        balance = WalletService(db).get_balance(user_id)
        if balance < stake:
            raise TournamentInsufficientBalanceError

        bet = TournamentBet(
            user_id=user_id,
            tournament_market_id=market.id,
            selection=market.selection,
            odds=market.odds,
            stake=stake,
            payout=None,
            status=TOURNAMENT_BET_STATUS_PENDING,
        )
        db.add(bet)
        db.flush()

        db.add(
            WalletTransaction(
                user_id=user_id,
                amount=-stake,
                transaction_type=TOURNAMENT_BET_PLACED_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )
        db.commit()
        db.refresh(bet)
        return bet
    except Exception:
        db.rollback()
        raise


class TournamentSettlementService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def settle_tournament(self, tournament_id: int, winner_team: str) -> Tournament:
        try:
            tournament = self.db.get(Tournament, tournament_id)
            if tournament is None:
                raise TournamentNotFoundError
            if tournament.status == TOURNAMENT_STATUS_COMPLETED or self._markets_are_settled(tournament_id):
                return tournament

            tournament.status = TOURNAMENT_STATUS_COMPLETED
            tournament.winner_team = winner_team

            pending_bets = list(
                self.db.scalars(
                    select(TournamentBet)
                    .join(TournamentMarket)
                    .where(
                        TournamentMarket.tournament_id == tournament_id,
                        TournamentBet.status == TOURNAMENT_BET_STATUS_PENDING,
                    )
                )
            )

            for bet in pending_bets:
                if bet.selection == winner_team:
                    payout = int(Decimal(bet.stake) * bet.odds)
                    bet.status = TOURNAMENT_BET_STATUS_WON
                    bet.payout = payout
                    if not self._has_won_transaction(bet.id):
                        self.db.add(
                            WalletTransaction(
                                user_id=bet.user_id,
                                amount=payout,
                                transaction_type=TOURNAMENT_BET_WON_TRANSACTION_TYPE,
                                reference_id=str(bet.id),
                            )
                        )
                else:
                    bet.status = TOURNAMENT_BET_STATUS_LOST
                    bet.payout = 0

            markets = list(self.db.scalars(select(TournamentMarket).where(TournamentMarket.tournament_id == tournament_id)))
            for market in markets:
                market.status = TOURNAMENT_MARKET_STATUS_SETTLED

            self.db.commit()
            self.db.refresh(tournament)
            return tournament
        except Exception:
            self.db.rollback()
            raise

    def unsettle_tournament(self, tournament_id: int) -> Tournament:
        try:
            tournament = self.db.get(Tournament, tournament_id)
            if tournament is None:
                raise TournamentNotFoundError
            if tournament.status != TOURNAMENT_STATUS_COMPLETED:
                return tournament

            settled_bets = list(
                self.db.scalars(
                    select(TournamentBet)
                    .join(TournamentMarket)
                    .where(
                        TournamentMarket.tournament_id == tournament_id,
                        TournamentBet.status.in_([TOURNAMENT_BET_STATUS_WON, TOURNAMENT_BET_STATUS_LOST]),
                    )
                )
            )

            for bet in settled_bets:
                if bet.status == TOURNAMENT_BET_STATUS_WON:
                    self._create_reversal_transaction(bet)
                bet.status = TOURNAMENT_BET_STATUS_PENDING
                bet.payout = None

            markets = list(self.db.scalars(select(TournamentMarket).where(TournamentMarket.tournament_id == tournament_id)))
            for market in markets:
                market.status = TOURNAMENT_MARKET_STATUS_OPEN

            tournament.status = TOURNAMENT_STATUS_OPEN
            tournament.winner_team = None
            self.db.commit()
            self.db.refresh(tournament)
            return tournament
        except Exception:
            self.db.rollback()
            raise

    def void_tournament_bets(self, tournament_id: int) -> Tournament:
        try:
            tournament = self.db.get(Tournament, tournament_id)
            if tournament is None:
                raise TournamentNotFoundError

            bets = list(
                self.db.scalars(
                    select(TournamentBet)
                    .join(TournamentMarket)
                    .where(TournamentMarket.tournament_id == tournament_id)
                )
            )

            for bet in bets:
                if bet.status == TOURNAMENT_BET_STATUS_WON:
                    self._create_reversal_transaction(bet)
                self._create_void_refund_transaction(bet)
                bet.status = TOURNAMENT_BET_STATUS_VOID
                bet.payout = None

            markets = list(self.db.scalars(select(TournamentMarket).where(TournamentMarket.tournament_id == tournament_id)))
            for market in markets:
                market.status = TOURNAMENT_MARKET_STATUS_OPEN

            tournament.status = TOURNAMENT_STATUS_OPEN
            tournament.winner_team = None
            self.db.commit()
            self.db.refresh(tournament)
            return tournament
        except Exception:
            self.db.rollback()
            raise

    def void_tournament_bet(self, tournament_bet_id: int) -> TournamentBet:
        try:
            bet = self.db.get(TournamentBet, tournament_bet_id)
            if bet is None:
                raise TournamentBetNotFoundError

            if bet.status == TOURNAMENT_BET_STATUS_WON:
                self._create_reversal_transaction(bet)
            self._create_void_refund_transaction(bet)
            bet.status = TOURNAMENT_BET_STATUS_VOID
            bet.payout = None

            self.db.commit()
            self.db.refresh(bet)
            return bet
        except Exception:
            self.db.rollback()
            raise

    def _markets_are_settled(self, tournament_id: int) -> bool:
        has_market = self.db.scalar(select(exists().where(TournamentMarket.tournament_id == tournament_id)))
        has_unsettled_market = self.db.scalar(
            select(
                exists().where(
                    TournamentMarket.tournament_id == tournament_id,
                    TournamentMarket.status != TOURNAMENT_MARKET_STATUS_SETTLED,
                )
            )
        )
        return bool(has_market and not has_unsettled_market)

    def _has_won_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == TOURNAMENT_BET_WON_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )

    def _has_reversal_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )

    def _create_reversal_transaction(self, bet: TournamentBet) -> None:
        if self._has_reversal_transaction(bet.id):
            return
        original_transaction = self.db.scalar(
            select(WalletTransaction).where(
                WalletTransaction.transaction_type == TOURNAMENT_BET_WON_TRANSACTION_TYPE,
                WalletTransaction.reference_id == str(bet.id),
            )
        )
        if original_transaction is None:
            return
        self.db.add(
            WalletTransaction(
                user_id=bet.user_id,
                amount=-original_transaction.amount,
                transaction_type=TOURNAMENT_SETTLEMENT_REVERSED_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )

    def _create_void_refund_transaction(self, bet: TournamentBet) -> None:
        if self._has_void_refund_transaction(bet.id):
            return
        original_transaction = self.db.scalar(
            select(WalletTransaction).where(
                WalletTransaction.transaction_type == TOURNAMENT_BET_PLACED_TRANSACTION_TYPE,
                WalletTransaction.reference_id == str(bet.id),
            )
        )
        if original_transaction is None:
            return
        self.db.add(
            WalletTransaction(
                user_id=bet.user_id,
                amount=-original_transaction.amount,
                transaction_type=TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )

    def _has_void_refund_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == TOURNAMENT_BET_VOID_REFUND_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )
