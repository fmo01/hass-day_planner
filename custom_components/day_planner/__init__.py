from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .action_executor import ActionExecutor
from .const import (CONF_DELETE_DATA_ON_REMOVE, CONF_MAX_CYCLES,
                    DEFAULT_DELETE_DATA_ON_REMOVE, DEFAULT_MAX_CYCLES,
                    PLATFORMS)
from .frontend import async_setup_frontend
from .ha_scheduler import HomeAssistantScheduler
from .planner.engine import PlannerEngine
from .planner.resolver import PlannerResolver
from .planner.scheduler import PlannerScheduler
from .runtime import DayPlannerRuntimeData
from .services import async_setup_services
from .storage import DayPlannerStorage
from .websocket_api import async_setup_websocket_api


async def _async_migrate_entity_ids(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Migrate legacy Day Planner entity IDs."""

    entity_registry = er.async_get(hass)

    migrations = {
        "day_planner_next_event": ("sensor.day_planner_next_event"),
        "day_planner_current_day_type": ("sensor.day_planner_current_day_type"),
        "day_planner_current_moment": ("sensor.day_planner_current_moment"),
        "day_planner_calendar": ("calendar.day_planner_planning"),
    }

    entries = er.async_entries_for_config_entry(
        entity_registry,
        entry.entry_id,
    )

    for entity in entries:
        new_entity_id = migrations.get(entity.unique_id)

        if new_entity_id is None or entity.entity_id == new_entity_id:
            continue

        entity_registry.async_update_entity(
            entity.entity_id,
            new_entity_id=new_entity_id,
        )


async def _async_options_updated(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload Day Planner when options change."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up Day Planner integration."""

    async_setup_websocket_api(hass)

    await async_setup_frontend(hass)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Day Planner."""

    storage = DayPlannerStorage(hass)

    configuration = await storage.async_load()

    if not configuration.has_data():
        await storage.async_save(configuration)

    engine = PlannerEngine(
        configuration,
        max_cycles=entry.options.get(
            CONF_MAX_CYCLES,
            DEFAULT_MAX_CYCLES,
        ),
    )
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

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    await async_setup_services(hass)
    await _async_migrate_entity_ids(
        hass,
        entry,
    )
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
