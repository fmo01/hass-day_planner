"""Resolved Day Planner context for a date."""

from dataclasses import dataclass
from datetime import date as Date

from .day_type import DayType


@dataclass(frozen=True, slots=True)
class ResolvedDayContext:
    """Resolved planning context for one date."""

    date: Date
    day_type: DayType | None
    cycle_id: str | None
    week_schedule_id: str | None
    calendar_exception_id: str | None
