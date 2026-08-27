"""Runtime data for Day Planner."""

from dataclasses import dataclass

from .action_executor import ActionExecutor
from .ha_scheduler import HomeAssistantScheduler
from .planner.engine import PlannerEngine
from .planner.resolver import PlannerResolver
from .planner.scheduler import PlannerScheduler
from .storage import DayPlannerStorage


@dataclass
class DayPlannerRuntimeData:
    """Runtime data for a Day Planner instance."""

    storage: DayPlannerStorage
    engine: PlannerEngine
    resolver: PlannerResolver
    scheduler: PlannerScheduler
    action_executor: ActionExecutor
    ha_scheduler: HomeAssistantScheduler
