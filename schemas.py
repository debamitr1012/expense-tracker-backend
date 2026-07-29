from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterDto(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6)


class LoginDto(BaseModel):
    username: str
    password: str


class AuthResponseDto(BaseModel):
    token: str
    name: str
    username: str


class ExpenseDto(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=Decimal("0"), le=Decimal("1000000"))
    category: str = Field(min_length=1, max_length=50)
    date: date

    @field_validator("description")
    @classmethod
    def _strip_description(cls, v: str) -> str:
        return v.strip()


class ExpenseResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str
    amount: float
    category: str
    date: date
