from decimal import Decimal

from pydantic import BaseModel, field_serializer


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    balance: Decimal

    @field_serializer("balance")
    def serialize_balance(self, balance: Decimal) -> int:
        return int(balance)
