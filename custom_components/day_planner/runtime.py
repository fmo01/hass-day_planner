"""Runtime data for Day Planner."""

from dataclasses import dataclass

from .planner.engine import PlannerEngine
from .storage import DayPlannerStorage


@dataclass
class DayPlannerRuntimeData:
    """Runtime data for a Day Planner instance."""

    storage: DayPlannerStorage
    engine: PlannerEngine
