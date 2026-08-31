"""Execute Day Planner actions in Home Assistant."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.script import Script

from .domain.action import Action
from .domain.moment import Moment

_LOGGER = logging.getLogger(__name__)


class ActionExecutor:
    """Execute actions attached to moments."""

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the action executor."""

        self._hass = hass

    async def async_execute_action(
        self,
        action: Action,
    ) -> None:
        """Execute one action."""

        script = Script(
            self._hass,
            action.sequence,
            f"Day Planner action: {action.id}",
            "day_planner",
        )

        await script.async_run()

    async def async_execute_moment(
        self,
        moment: Moment,
    ) -> None:
        """Execute all actions attached to a moment."""

        for action in moment.actions:
            try:
                await self.async_execute_action(action)
            except Exception:
                _LOGGER.exception(
                    "Unable to execute Day Planner action '%s' " "for moment '%s'",
                    action.id,
                    moment.id,
                )
