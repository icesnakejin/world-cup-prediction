from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_number: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True, index=True)
    stage: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    group: Mapped[str | None] = mapped_column(String(5), nullable=True, index=True)
    home_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    away_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_placeholder: Mapped[str | None] = mapped_column(String(100), nullable=True)
    away_placeholder: Mapped[str | None] = mapped_column(String(100), nullable=True)
    kickoff_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    venue: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled", server_default="scheduled")
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    markets = relationship("Market", back_populates="match")
    bets = relationship("Bet", back_populates="match")
