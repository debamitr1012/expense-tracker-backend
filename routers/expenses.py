import calendar
from datetime import date, datetime
from typing import Any

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from models import Expense
from schemas import ExpenseDto, ExpenseResponseDto
from security import get_current_user_id

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _extract_date(val: Any) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return date.fromisoformat(val[:10])
        except ValueError:
            return None
    return None


def _to_dto(expense: Expense) -> ExpenseResponseDto:
    extracted = _extract_date(expense.date) or date.today()
    return ExpenseResponseDto(
        id=str(expense.id),
        description=expense.description or "",
        amount=float(expense.amount or 0.0),
        category=expense.category or "General",
        date=extracted,
    )


def _to_datetime(value: date | datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str):
        try:
            d = date.fromisoformat(value[:10])
            return datetime(d.year, d.month, d.day)
        except ValueError:
            pass
    now = datetime.now()
    return datetime(now.year, now.month, now.day)


@router.get("", response_model=list[ExpenseResponseDto])
async def get_all(
    user_id: PydanticObjectId = Depends(get_current_user_id),
) -> list[ExpenseResponseDto]:
    expenses = (
        await Expense.find(Expense.user_id == user_id)
        .sort("-date", "-_id")
        .to_list()
    )
    return [_to_dto(e) for e in expenses]


@router.post("", response_model=ExpenseResponseDto, status_code=status.HTTP_201_CREATED)
async def create(
    dto: ExpenseDto,
    user_id: PydanticObjectId = Depends(get_current_user_id),
) -> ExpenseResponseDto:
    expense = Expense(
        description=dto.description.strip(),
        amount=dto.amount,
        category=dto.category,
        date=_to_datetime(dto.date),
        user_id=user_id,
    )
    await expense.insert()
    return _to_dto(expense)


@router.put("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(
    expense_id: PydanticObjectId,
    dto: ExpenseDto,
    user_id: PydanticObjectId = Depends(get_current_user_id),
) -> Response:
    expense = await Expense.find_one(
        Expense.id == expense_id, Expense.user_id == user_id
    )
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    expense.description = dto.description.strip()
    expense.amount = dto.amount
    expense.category = dto.category
    expense.date = _to_datetime(dto.date)
    await expense.save()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    expense_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
) -> Response:
    expense = await Expense.find_one(
        Expense.id == expense_id, Expense.user_id == user_id
    )
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await expense.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/summary")
async def summary(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    user_id: PydanticObjectId = Depends(get_current_user_id),
) -> dict:
    expenses = await Expense.find(Expense.user_id == user_id).to_list()

    today = date.today()
    target_year, target_month = today.year, today.month

    if month:
        try:
            parts = month.split("-")
            if len(parts) == 2:
                y, m = int(parts[0]), int(parts[1])
                if 1 <= m <= 12 and 1 <= y <= 9999:
                    target_year, target_month = y, m
        except (ValueError, TypeError):
            pass

    if target_month == 1:
        prev_year, prev_month = target_year - 1, 12
    else:
        prev_year, prev_month = target_year, target_month - 1

    target_month_expenses: list[Expense] = []
    prev_month_expenses: list[Expense] = []

    for e in expenses:
        d = _extract_date(e.date)
        if d is not None:
            if d.year == target_year and d.month == target_month:
                target_month_expenses.append(e)
            elif d.year == prev_year and d.month == prev_month:
                prev_month_expenses.append(e)

    month_total = sum((float(e.amount or 0) for e in target_month_expenses), start=0.0)
    prev_month_total = sum((float(e.amount or 0) for e in prev_month_expenses), start=0.0)
    total_all_time = sum((float(e.amount or 0) for e in expenses), start=0.0)

    by_category_map: dict[str, float] = {}
    for e in target_month_expenses:
        cat = e.category or "General"
        by_category_map[cat] = by_category_map.get(cat, 0.0) + float(e.amount or 0)

    by_category = [
        {"category": cat, "total": round(tot, 2)}
        for cat, tot in sorted(by_category_map.items(), key=lambda kv: kv[1], reverse=True)
    ]

    _, num_days = calendar.monthrange(target_year, target_month)
    if target_year == today.year and target_month == today.month:
        days_passed = max(today.day, 1)
    else:
        days_passed = num_days

    avg_per_day = month_total / days_passed if days_passed > 0 else 0.0

    daily_totals: dict[date, float] = {}
    for e in target_month_expenses:
        d = _extract_date(e.date)
        if d is not None:
            daily_totals[d] = daily_totals.get(d, 0.0) + float(e.amount or 0)

    daily_trend = []
    for day_num in range(1, num_days + 1):
        d = date(target_year, target_month, day_num)
        day_total = daily_totals.get(d, 0.0)
        daily_trend.append({"date": d.isoformat(), "total": round(day_total, 2)})

    return {
        "selectedMonth": f"{target_year:04d}-{target_month:02d}",
        "total": round(total_all_time, 2),
        "monthTotal": round(month_total, 2),
        "prevMonthTotal": round(prev_month_total, 2),
        "count": len(target_month_expenses),
        "totalCount": len(expenses),
        "avgPerDay": round(avg_per_day, 2),
        "byCategory": by_category,
        "dailyTrend": daily_trend,
    }

