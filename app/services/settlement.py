from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.models.market import Market
from app.models.match import Match
from app.models.wallet_transaction import WalletTransaction

BET_STATUS_LOST = "LOST"
BET_STATUS_PENDING = "PENDING"
BET_STATUS_VOID = "VOID"
BET_STATUS_WON = "WON"
BET_PLACED_TRANSACTION_TYPE = "BET_PLACED"
BET_WON_TRANSACTION_TYPE = "BET_WON"
BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE = "BET_SETTLEMENT_REVERSED"
BET_VOID_REFUND_TRANSACTION_TYPE = "BET_VOID_REFUND"
MARKET_STATUS_SETTLED = "SETTLED"
MARKET_STATUS_OPEN = "OPEN"
MATCH_STATUS_COMPLETED = "COMPLETED"
MATCH_STATUS_SCHEDULED = "scheduled"
MATCH_WINNER_MARKET_TYPE = "match_winner"
OVER_UNDER_MARKET_TYPE = "over_under"
EXACT_SCORE_MARKET_TYPE = "exact_score"


class MatchNotFoundError(Exception):
    pass


class MatchNotCompletedError(Exception):
    pass


class BetNotFoundError(Exception):
    pass


class SettlementService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def update_result_and_settle(self, match_id: int, home_score: int, away_score: int) -> Match:
        try:
            match = self.db.get(Match, match_id)
            if match is None:
                raise MatchNotFoundError

            if match.status == MATCH_STATUS_COMPLETED or self._markets_are_settled(match_id):
                return match

            match.home_score = home_score
            match.away_score = away_score
            match.status = MATCH_STATUS_COMPLETED

            self.settle_match(match_id)
            self.db.commit()
            self.db.refresh(match)
            return match
        except Exception:
            self.db.rollback()
            raise

    def unsettle_match(self, match_id: int) -> Match:
        try:
            match = self.db.get(Match, match_id)
            if match is None:
                raise MatchNotFoundError
            if match.status != MATCH_STATUS_COMPLETED:
                raise MatchNotCompletedError

            settled_bets = list(
                self.db.scalars(
                    select(Bet).where(
                        Bet.match_id == match_id,
                        Bet.status.in_([BET_STATUS_WON, BET_STATUS_LOST]),
                    )
                )
            )

            for bet in settled_bets:
                if bet.status == BET_STATUS_WON:
                    self._create_reversal_transaction(bet)
                bet.status = BET_STATUS_PENDING
                bet.payout = None

            markets = list(self.db.scalars(select(Market).where(Market.match_id == match_id)))
            for market in markets:
                market.status = MARKET_STATUS_OPEN

            match.home_score = None
            match.away_score = None
            match.status = MATCH_STATUS_SCHEDULED

            self.db.commit()
            self.db.refresh(match)
            return match
        except Exception:
            self.db.rollback()
            raise

    def void_match_bets(self, match_id: int) -> Match:
        try:
            match = self.db.get(Match, match_id)
            if match is None:
                raise MatchNotFoundError

            bets = list(self.db.scalars(select(Bet).where(Bet.match_id == match_id)))
            for bet in bets:
                if bet.status == BET_STATUS_WON:
                    self._create_reversal_transaction(bet)
                self._create_void_refund_transaction(bet)
                bet.status = BET_STATUS_VOID
                bet.payout = None

            markets = list(self.db.scalars(select(Market).where(Market.match_id == match_id)))
            for market in markets:
                market.status = MARKET_STATUS_OPEN

            match.home_score = None
            match.away_score = None
            match.status = MATCH_STATUS_SCHEDULED

            self.db.commit()
            self.db.refresh(match)
            return match
        except Exception:
            self.db.rollback()
            raise

    def void_bet(self, bet_id: int) -> Bet:
        try:
            bet = self.db.get(Bet, bet_id)
            if bet is None:
                raise BetNotFoundError

            if bet.status == BET_STATUS_WON:
                self._create_reversal_transaction(bet)
            self._create_void_refund_transaction(bet)
            bet.status = BET_STATUS_VOID
            bet.payout = None

            self.db.commit()
            self.db.refresh(bet)
            return bet
        except Exception:
            self.db.rollback()
            raise

    def settle_match(self, match_id: int) -> None:
        match = self.db.get(Match, match_id)
        if match is None:
            raise MatchNotFoundError
        if match.home_score is None or match.away_score is None:
            raise ValueError("Match score is required before settlement")
        if self._markets_are_settled(match_id):
            return

        pending_bets = list(
            self.db.scalars(
                select(Bet).where(
                    Bet.match_id == match_id,
                    Bet.status == BET_STATUS_PENDING,
                )
            )
        )

        for bet in pending_bets:
            if self._bet_won(bet, match):
                payout = int(Decimal(bet.stake) * bet.odds)
                bet.status = BET_STATUS_WON
                bet.payout = payout

                if not self._has_bet_won_transaction(bet.id):
                    self.db.add(
                        WalletTransaction(
                            user_id=bet.user_id,
                            amount=payout,
                            transaction_type=BET_WON_TRANSACTION_TYPE,
                            reference_id=str(bet.id),
                        )
                    )
            else:
                bet.status = BET_STATUS_LOST
                bet.payout = 0

        markets = list(self.db.scalars(select(Market).where(Market.match_id == match_id)))
        for market in markets:
            market.status = MARKET_STATUS_SETTLED

    def _markets_are_settled(self, match_id: int) -> bool:
        has_market = self.db.scalar(select(exists().where(Market.match_id == match_id)))
        has_unsettled_market = self.db.scalar(
            select(exists().where(Market.match_id == match_id, Market.status != MARKET_STATUS_SETTLED))
        )
        return bool(has_market and not has_unsettled_market)

    def _has_bet_won_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == BET_WON_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )

    def _create_reversal_transaction(self, bet: Bet) -> None:
        if self._has_reversal_transaction(bet.id):
            return

        original_transaction = self.db.scalar(
            select(WalletTransaction).where(
                WalletTransaction.transaction_type == BET_WON_TRANSACTION_TYPE,
                WalletTransaction.reference_id == str(bet.id),
            )
        )
        if original_transaction is None:
            return

        self.db.add(
            WalletTransaction(
                user_id=bet.user_id,
                amount=-original_transaction.amount,
                transaction_type=BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )

    def _create_void_refund_transaction(self, bet: Bet) -> None:
        if self._has_void_refund_transaction(bet.id):
            return

        original_transaction = self.db.scalar(
            select(WalletTransaction).where(
                WalletTransaction.transaction_type == BET_PLACED_TRANSACTION_TYPE,
                WalletTransaction.reference_id == str(bet.id),
            )
        )
        if original_transaction is None:
            return

        self.db.add(
            WalletTransaction(
                user_id=bet.user_id,
                amount=-original_transaction.amount,
                transaction_type=BET_VOID_REFUND_TRANSACTION_TYPE,
                reference_id=str(bet.id),
            )
        )

    def _has_void_refund_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == BET_VOID_REFUND_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )

    def _has_reversal_transaction(self, bet_id: int) -> bool:
        return self.db.scalar(
            select(
                exists().where(
                    WalletTransaction.transaction_type == BET_SETTLEMENT_REVERSED_TRANSACTION_TYPE,
                    WalletTransaction.reference_id == str(bet_id),
                )
            )
        )

    def _winning_selections(self, home_score: int, away_score: int) -> set[str]:
        if home_score > away_score:
            return {"HOME", "HOME_WIN"}
        if home_score < away_score:
            return {"AWAY", "AWAY_WIN"}
        return {"DRAW"}

    def _bet_won(self, bet: Bet, match: Match) -> bool:
        if bet.market.market_type == MATCH_WINNER_MARKET_TYPE:
            return bet.selection in self._winning_selections(match.home_score, match.away_score)

        if bet.market.market_type == OVER_UNDER_MARKET_TYPE:
            if bet.market.line is None:
                return False
            total_goals = Decimal(match.home_score + match.away_score)
            if bet.selection == "OVER":
                return total_goals > bet.market.line
            if bet.selection == "UNDER":
                return total_goals < bet.market.line
            return False

        if bet.market.market_type == EXACT_SCORE_MARKET_TYPE:
            actual_score = f"{match.home_score}-{match.away_score}"
            return bet.selection == actual_score

        return False
