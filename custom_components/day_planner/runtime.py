from dataclasses import dataclass

from .storage import DayPlannerStorage


@dataclass
class DayPlannerRuntimeData:
    """Runtime data for a Day Planner instance."""

    storage: DayPlannerStorage
    data: dict
