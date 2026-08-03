from dataclasses import dataclass

from .storage import DayPlannerStorage


@dataclass(slots=True)
class DayPlannerRuntimeData:
    """Runtime data."""

    storage: DayPlannerStorage

