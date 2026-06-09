from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TournamentMarket(Base):
    __tablename__ = "tournament_markets"
    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "market_type",
            "selection",
            name="uq_tournament_markets_tournament_type_selection",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False, index=True)
    market_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="tournament_winner",
        server_default="tournament_winner",
    )
    selection: Mapped[str] = mapped_column(String(100), nullable=False)
    odds: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN", server_default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tournament = relationship("Tournament", back_populates="markets")
    bets = relationship("TournamentBet", back_populates="tournament_market")
