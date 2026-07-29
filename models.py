from datetime import datetime, timezone
from decimal import Decimal

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Document):
    name: str
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=_utcnow)

    class Settings:
        name = "users"
        indexes = [
            pymongo.IndexModel("username", unique=True),
        ]


class Expense(Document):
    description: str
    amount: Decimal
    category: str
    # Stored as datetime (MongoDB has no plain date type); converted to/from
    # date at the API boundary.
    date: datetime
    created_at: datetime = Field(default_factory=_utcnow)
    user_id: PydanticObjectId

    class Settings:
        name = "expenses"
        indexes = ["user_id"]
