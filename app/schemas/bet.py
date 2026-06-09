from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BetCreate(BaseModel):
    market_id: int
    stake: int = Field(gt=0)


class BetMatchRead(BaseModel):
    home_team: str
    away_team: str
    kickoff_time: datetime


class BetRead(BaseModel):
    bet_id: int
    market_id: int
    match_id: int
    match: BetMatchRead
    selection: str
    odds: Decimal
    stake: int
    payout: int | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
