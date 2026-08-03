from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .runtime import DayPlannerRuntimeData
from .storage import DayPlannerStorage


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Day Planner."""

    storage = DayPlannerStorage(hass)

    entry.runtime_data = DayPlannerRuntimeData(
        storage=storage,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Day Planner."""

    return True
