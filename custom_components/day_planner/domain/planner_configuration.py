from dataclasses import dataclass

from .calendar_exception import CalendarException
from .cycle import Cycle
from .day_type import DayType
from .moment import Moment
from .week_schedule import WeekSchedule


@dataclass(frozen=True, slots=True)
class PlannerConfiguration:
    """Root configuration of Day Planner."""

    moments: tuple[Moment, ...]
    day_types: tuple[DayType, ...]
    week_schedules: tuple[WeekSchedule, ...]
    cycles: tuple[Cycle, ...]
    calendar_exceptions: tuple[CalendarException, ...]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "moments": [item.to_dict() for item in self.moments],
            "day_types": [item.to_dict() for item in self.day_types],
            "week_schedules": [item.to_dict() for item in self.week_schedules],
            "cycles": [item.to_dict() for item in self.cycles],
            "calendar_exceptions": [
                item.to_dict() for item in self.calendar_exceptions
            ],
        }

    @classmethod
    def empty(cls) -> "PlannerConfiguration":
        """Create an empty configuration."""

        return cls(
            moments=(),
            day_types=(),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "PlannerConfiguration":
        """Deserialize object."""

        return cls(
            moments=tuple(
                Moment.from_dict(item)
                for item in data.get(
                    "moments",
                    [],
                )
            ),
            day_types=tuple(
                DayType.from_dict(item)
                for item in data.get(
                    "day_types",
                    [],
                )
            ),
            week_schedules=tuple(
                WeekSchedule.from_dict(item)
                for item in data.get(
                    "week_schedules",
                    [],
                )
            ),
            cycles=tuple(
                Cycle.from_dict(item)
                for item in data.get(
                    "cycles",
                    [],
                )
            ),
            calendar_exceptions=tuple(
                CalendarException.from_dict(item)
                for item in data.get(
                    "calendar_exceptions",
                    [],
                )
            ),
        )

    def has_data(self) -> bool:
        """Return True if configuration contains data."""

        return any(
            (
                self.moments,
                self.day_types,
                self.week_schedules,
                self.cycles,
                self.calendar_exceptions,
            )
        )
