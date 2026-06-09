from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False, index=True)
    selection: Mapped[str] = mapped_column(String(30), nullable=False)
    stake: Mapped[int] = mapped_column(Integer, nullable=False)
    odds: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payout: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", server_default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="bets")
    match = relationship("Match", back_populates="bets")
    market = relationship("Market", back_populates="bets")
