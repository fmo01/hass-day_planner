"""Home Assistant scheduler for Day Planner."""

from collections.abc import Callable
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .action_executor import ActionExecutor
from .planner.scheduler import PlannerScheduler


class HomeAssistantScheduler:
    """Schedule Day Planner events in Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        scheduler: PlannerScheduler,
        action_executor: ActionExecutor,
    ) -> None:
        """Initialize scheduler."""

        self._hass = hass
        self._scheduler = scheduler
        self._action_executor = action_executor
        self._cancel: Callable[[], None] | None = None

    async def async_schedule_next(
        self,
    ) -> None:
        """Schedule the next Day Planner event."""

        self.cancel()

        now = dt_util.now()

        event = self._scheduler.next_event(now)

        if event is None:
            return
        scheduled_at = event.scheduled_at

        if scheduled_at.tzinfo is None and now.tzinfo is not None:
            scheduled_at = scheduled_at.replace(tzinfo=now.tzinfo)

        async def handle_event(
            now: datetime,
        ) -> None:
            """Handle scheduled event."""

            self._cancel = None

            await self._action_executor.async_execute_moment(event.moment)

            await self.async_schedule_next()

        self._cancel = async_track_point_in_time(
            self._hass,
            handle_event,
            scheduled_at,
        )

    def cancel(self) -> None:
        """Cancel currently scheduled event."""

        if self._cancel is None:
            return

        self._cancel()
        self._cancel = None
