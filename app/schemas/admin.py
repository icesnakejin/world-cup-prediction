from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class MatchResultUpdate(BaseModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class AdminMatchBetRead(BaseModel):
    id: int
    user_id: int
    username: str
    match_id: int
    home_team: str
    away_team: str
    kickoff_time: datetime
    market_id: int
    market_type: str
    selection: str
    odds: Decimal
    stake: int
    payout: int | None
    status: str
    created_at: datetime


class AdminTournamentBetRead(BaseModel):
    id: int
    user_id: int
    username: str
    tournament_id: int
    tournament_name: str
    tournament_market_id: int
    market_type: str
    selection: str
    odds: Decimal
    stake: int
    payout: int | None
    status: str
    created_at: datetime
