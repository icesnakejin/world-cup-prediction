from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Market(Base):
    __tablename__ = "markets"
    __table_args__ = (
        UniqueConstraint("match_id", "market_type", "selection", name="uq_markets_match_type_selection"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    market_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="match_winner",
        server_default="match_winner",
    )
    selection: Mapped[str] = mapped_column(String(30), nullable=False)
    line: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    odds: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN", server_default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    match = relationship("Match", back_populates="markets")
    bets = relationship("Bet", back_populates="market")
