"""Runtime data for Day Planner."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .action_executor import ActionExecutor
from .const import SIGNAL_PLANNER_UPDATED
from .ha_scheduler import HomeAssistantScheduler
from .planner.engine import PlannerEngine
from .planner.resolver import PlannerResolver
from .planner.scheduler import PlannerScheduler
from .storage import DayPlannerStorage


@dataclass
class DayPlannerRuntimeData:
    """Runtime data for a Day Planner instance."""

    hass: HomeAssistant
    storage: DayPlannerStorage
    engine: PlannerEngine
    resolver: PlannerResolver
    scheduler: PlannerScheduler
    action_executor: ActionExecutor
    ha_scheduler: HomeAssistantScheduler

    async def async_configuration_updated(self) -> None:
        """Synchronize runtime after a configuration change."""

        configuration = self.engine.configuration

        await self.storage.async_save(configuration)

        self.resolver.update_configuration(configuration)

        await self.ha_scheduler.async_schedule_next()

        async_dispatcher_send(
            self.hass,
            SIGNAL_PLANNER_UPDATED,
        )
