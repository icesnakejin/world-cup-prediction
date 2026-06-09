from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TournamentRead(BaseModel):
    id: int
    name: str
    year: int
    status: str
    winner_team: str | None

    model_config = ConfigDict(from_attributes=True)


class TournamentMarketRead(BaseModel):
    id: int
    tournament_id: int
    market_type: str
    selection: str
    odds: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class TournamentBetCreate(BaseModel):
    tournament_market_id: int
    stake: int = Field(gt=0)


class TournamentBetRead(BaseModel):
    id: int
    tournament_market_id: int
    tournament_id: int
    tournament_name: str
    selection: str
    odds: Decimal
    stake: int
    payout: int | None
    status: str
    created_at: datetime


class TournamentWinnerUpdate(BaseModel):
    winner_team: str = Field(min_length=1, max_length=100)
