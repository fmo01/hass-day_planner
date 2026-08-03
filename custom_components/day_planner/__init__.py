from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .runtime import DayPlannerRuntimeData
from .storage import DayPlannerStorage


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    storage = DayPlannerStorage(hass)

    data = await storage.async_load()

    entry.runtime_data = DayPlannerRuntimeData(
        storage=storage,
        data=data,
    )

    return True
