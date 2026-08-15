"""Storage management for Day Planner."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .domain.planner_configuration import (
    PlannerConfiguration,
)

from .const import (
    STORAGE_KEY,
    STORAGE_VERSION,
)


class DayPlannerStorage:
    """Handle persistent storage."""

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize storage."""

        self._store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )

    async def async_load(
        self,
    ) -> PlannerConfiguration:
        """Load configuration."""

        data = await self._store.async_load()

        if data is None:
            return PlannerConfiguration.empty()

        return PlannerConfiguration.from_dict(
            data
        )

    async def async_save(
        self,
        configuration: PlannerConfiguration,
    ) -> None:
        """Save configuration."""

        await self._store.async_save(
            configuration.to_dict()
        )

    async def async_delete(self) -> None:
        """Delete stored planner data."""

        await self._store.async_remove()
