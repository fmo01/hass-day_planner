from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_DELETE_DATA_ON_REMOVE, DEFAULT_DELETE_DATA_ON_REMOVE
from .planner.engine import PlannerEngine
from .runtime import DayPlannerRuntimeData
from .services import async_setup_services
from .storage import DayPlannerStorage


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Day Planner."""

    storage = DayPlannerStorage(hass)

    configuration = await storage.async_load()

    if not configuration.has_data():
        await storage.async_save(configuration)

    engine = PlannerEngine(configuration)

    entry.runtime_data = DayPlannerRuntimeData(
        storage=storage,
        engine=engine,
    )

    await async_setup_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Day Planner."""

    return True


async def async_remove_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Handle removal of the config entry."""

    if entry.options.get(
        CONF_DELETE_DATA_ON_REMOVE,
        DEFAULT_DELETE_DATA_ON_REMOVE,
    ):
        storage = DayPlannerStorage(hass)
        await storage.async_delete()
