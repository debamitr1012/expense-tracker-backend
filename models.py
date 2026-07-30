from datetime import datetime, timezone
from decimal import Decimal

import pymongo
from beanie import Document, PydanticObjectId
from bson.decimal128 import Decimal128
from pydantic import Field, field_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Document):
    name: str
    username: str
    password_hash: str | None = None
    google_id: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)

    class Settings:
        name = "users"
        indexes = [
            pymongo.IndexModel("username", unique=True),
            pymongo.IndexModel("google_id", unique=True, sparse=True),
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

    @field_validator("amount", mode="before")
    @classmethod
    def convert_bson_decimal128(cls, value: object) -> object:
        """Convert MongoDB's BSON Decimal128 value into a Python Decimal.

        Motor returns existing Decimal128 fields as ``Decimal128`` objects,
        which Pydantic does not coerce automatically.  New API values are
        already normal Python numeric values and pass through unchanged.
        """
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value

    class Settings:
        name = "expenses"
        indexes = ["user_id"]
