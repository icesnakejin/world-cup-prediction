from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MatchRead(BaseModel):
    id: int
    home_team: str
    away_team: str
    kickoff_time: datetime
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
