from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MatchRead(BaseModel):
    id: int
    match_number: int | None
    stage: str | None
    group: str | None
    home_team: str | None
    away_team: str | None
    home_placeholder: str | None
    away_placeholder: str | None
    kickoff_time: datetime
    venue: str | None
    status: str
    home_score: int | None
    away_score: int | None

    model_config = ConfigDict(from_attributes=True)


class MarketRead(BaseModel):
    id: int
    market_type: str
    selection: str
    line: Decimal | None
    odds: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)
