"""Execute Day Planner actions in Home Assistant."""

from homeassistant.core import HomeAssistant

from .domain.action import Action
from .domain.moment import Moment


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

        domain, service = action.service.split(
            ".",
            1,
        )

        await self._hass.services.async_call(
            domain,
            service,
            action.data,
            blocking=True,
        )

    async def async_execute_moment(
        self,
        moment: Moment,
    ) -> None:
        """Execute all actions attached to a moment."""

        for action in moment.actions:
            await self.async_execute_action(action)
