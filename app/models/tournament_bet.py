from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TournamentBet(Base):
    __tablename__ = "tournament_bets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    tournament_market_id: Mapped[int] = mapped_column(ForeignKey("tournament_markets.id"), nullable=False, index=True)
    selection: Mapped[str] = mapped_column(String(100), nullable=False)
    odds: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stake: Mapped[int] = mapped_column(Integer, nullable=False)
    payout: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", server_default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="tournament_bets")
    tournament_market = relationship("TournamentMarket", back_populates="bets")
