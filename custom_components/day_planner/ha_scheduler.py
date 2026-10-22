"""Home Assistant scheduler for Day Planner."""

import logging
from collections.abc import Callable
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .action_executor import ActionExecutor
from .planner.scheduler import PlannerScheduler

_LOGGER = logging.getLogger(__name__)


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
        _LOGGER.debug("Recherche du prochain événement Day Planner à partir de %s", now)

        event = self._scheduler.next_event(now)

        if event is None:
            _LOGGER.info("Aucun prochain événement Day Planner à programmer")
            return
        scheduled_at = event.scheduled_at

        if scheduled_at.tzinfo is None and now.tzinfo is not None:
            scheduled_at = scheduled_at.replace(tzinfo=now.tzinfo)

        events = self._scheduler.events_at(scheduled_at)
        _LOGGER.info(
            "Programmation Day Planner : %s, %d moment(s)",
            scheduled_at.isoformat(),
            len(events),
        )

        executed = False

        async def handle_event(
            now: datetime,
        ) -> None:
            """Handle scheduled event."""

            nonlocal executed

            if executed:
                _LOGGER.debug("Événement Day Planner déjà exécuté à %s", scheduled_at)
                return

            executed = True
            self._cancel = None

            try:
                for scheduled_event in events:
                    _LOGGER.debug(
                        "Déclenchement planifié : moment='%s', date=%s",
                        scheduled_event.moment.id,
                        scheduled_at.isoformat(),
                    )
                    await self._action_executor.async_execute_moment(
                        scheduled_event.moment
                    )
            except Exception:
                _LOGGER.exception(
                    "Échec inattendu du déclenchement Day Planner à %s",
                    scheduled_at.isoformat(),
                )
                raise
            finally:
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

        _LOGGER.debug("Annulation de la programmation précédente Day Planner")
        self._cancel()
        self._cancel = None
