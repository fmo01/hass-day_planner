from collections.abc import Mapping

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class DayPlannerStorage:
    """Persistent storage handler."""

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:

        self._store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )

    async def async_load(self) -> dict:
        """Load data."""

        data = await self._store.async_load()

        if data is None:
            return {
                "moments": [],
                "day_types": [],
                "weeks": [],
                "cycles": [],
                "exceptions": [],
            }

        return data

    async def async_save(
        self,
        data: Mapping,
    ) -> None:
        """Save data."""

        await self._store.async_save(
            dict(data)
        )
