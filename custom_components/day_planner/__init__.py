from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .action_executor import ActionExecutor
from .const import (CONF_DELETE_DATA_ON_REMOVE, DEFAULT_DELETE_DATA_ON_REMOVE,
                    PLATFORMS)
from .ha_scheduler import HomeAssistantScheduler
from .planner.engine import PlannerEngine
from .planner.resolver import PlannerResolver
from .planner.scheduler import PlannerScheduler
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

    resolver = PlannerResolver(engine.configuration)

    scheduler = PlannerScheduler(resolver)

    action_executor = ActionExecutor(hass)

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    entry.runtime_data = DayPlannerRuntimeData(
        hass=hass,
        storage=storage,
        engine=engine,
        resolver=resolver,
        scheduler=scheduler,
        action_executor=action_executor,
        ha_scheduler=ha_scheduler,
    )

    await async_setup_services(hass)
    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    await ha_scheduler.async_schedule_next()

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Day Planner."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        entry.runtime_data.ha_scheduler.cancel()

    return unload_ok


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
