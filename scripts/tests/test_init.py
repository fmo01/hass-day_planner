import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner import (
    _async_migrate_entity_ids,
    async_remove_entry,
    async_setup_entry,
    async_unload_entry,
    )
from custom_components.day_planner.domain.planner_configuration import \
    PlannerConfiguration
from custom_components.day_planner.const import (
    CONF_DELETE_DATA_ON_REMOVE,
    PLATFORMS,
)


def test_async_setup_entry_empty_configuration():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        hass.config_entries.async_forward_entry_setups = AsyncMock()

        configuration = PlannerConfiguration.empty()

        with (
            patch(
                "custom_components.day_planner.DayPlannerStorage"
            ) as storage_class,
            patch(
                "custom_components.day_planner.PlannerEngine"
            ) as engine_class,
            patch(
                "custom_components.day_planner.PlannerResolver"
            ) as resolver_class,
            patch(
                "custom_components.day_planner.PlannerScheduler"
            ) as scheduler_class,
            patch(
                "custom_components.day_planner.ActionExecutor"
            ) as action_executor_class,
            patch(
                "custom_components.day_planner.HomeAssistantScheduler"
            ) as ha_scheduler_class,
            patch(
                "custom_components.day_planner.async_setup_services",
                new=AsyncMock(),
            ) as setup_services,
            patch(
                "custom_components.day_planner._async_migrate_entity_ids",
                new=AsyncMock(),
            ) as migrate_entity_ids,
        ):
            storage = storage_class.return_value
            storage.async_load = AsyncMock(
                return_value=configuration
            )
            storage.async_save = AsyncMock()

            engine = engine_class.return_value
            engine.configuration = configuration

            resolver = resolver_class.return_value
            scheduler = scheduler_class.return_value
            action_executor = action_executor_class.return_value

            ha_scheduler = ha_scheduler_class.return_value
            ha_scheduler.async_schedule_next = AsyncMock()

            result = await async_setup_entry(
                hass,
                entry,
            )

            assert result is True

            storage.async_load.assert_awaited_once_with()
            storage.async_save.assert_awaited_once_with(
                configuration
            )

            engine_class.assert_called_once_with(
                configuration
            )

            resolver_class.assert_called_once_with(
                configuration
            )

            scheduler_class.assert_called_once_with(
                resolver
            )

            action_executor_class.assert_called_once_with(
                hass
            )

            ha_scheduler_class.assert_called_once_with(
                hass=hass,
                scheduler=scheduler,
                action_executor=action_executor,
            )

            assert entry.runtime_data.storage is storage
            assert entry.runtime_data.engine is engine
            assert entry.runtime_data.resolver is resolver
            assert entry.runtime_data.scheduler is scheduler
            assert (
                entry.runtime_data.action_executor
                is action_executor
            )
            assert (
                entry.runtime_data.ha_scheduler
                is ha_scheduler
            )

            setup_services.assert_awaited_once_with(
                hass
            )

            ha_scheduler.async_schedule_next.assert_awaited_once_with()

            hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
                entry,
                PLATFORMS,
            )
            migrate_entity_ids.assert_awaited_once_with(
                hass,
                entry,
            )

    asyncio.run(run())

def test_async_setup_entry_existing_configuration():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        hass.config_entries.async_forward_entry_setups = AsyncMock()

        configuration = MagicMock()
        configuration.has_data.return_value = True

        with (
            patch(
                "custom_components.day_planner.DayPlannerStorage"
            ) as storage_class,
            patch(
                "custom_components.day_planner.PlannerEngine"
            ) as engine_class,
            patch(
                "custom_components.day_planner.PlannerResolver"
            ) as resolver_class,
            patch(
                "custom_components.day_planner.PlannerScheduler"
            ) as scheduler_class,
            patch(
                "custom_components.day_planner.ActionExecutor"
            ) as action_executor_class,
            patch(
                "custom_components.day_planner.HomeAssistantScheduler"
            ) as ha_scheduler_class,
            patch(
                "custom_components.day_planner.async_setup_services",
                new=AsyncMock(),
            ) as setup_services,
        ):
            storage = storage_class.return_value
            storage.async_load = AsyncMock(
                return_value=configuration
            )
            storage.async_save = AsyncMock()

            engine = engine_class.return_value
            engine.configuration = configuration

            resolver = resolver_class.return_value
            scheduler = scheduler_class.return_value
            action_executor = action_executor_class.return_value

            ha_scheduler = ha_scheduler_class.return_value
            ha_scheduler.async_schedule_next = AsyncMock()

            result = await async_setup_entry(
                hass,
                entry,
            )

            assert result is True

            storage.async_load.assert_awaited_once_with()

            storage.async_save.assert_not_awaited()

            engine_class.assert_called_once_with(
                configuration
            )

            resolver_class.assert_called_once_with(
                configuration
            )

            scheduler_class.assert_called_once_with(
                resolver
            )

            action_executor_class.assert_called_once_with(
                hass
            )

            ha_scheduler_class.assert_called_once_with(
                hass=hass,
                scheduler=scheduler,
                action_executor=action_executor,
            )

            setup_services.assert_awaited_once_with(
                hass
            )

            ha_scheduler.async_schedule_next.assert_awaited_once_with()

            hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
                entry,
                PLATFORMS,
            )

    asyncio.run(run())


def test_async_unload_entry():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        hass.config_entries.async_unload_platforms = AsyncMock(
            return_value=True
        )

        ha_scheduler = MagicMock()
        entry.runtime_data.ha_scheduler = ha_scheduler

        result = await async_unload_entry(
            hass,
            entry,
        )

        assert result is True

        hass.config_entries.async_unload_platforms.assert_awaited_once_with(
            entry,
            PLATFORMS,
        )

        ha_scheduler.cancel.assert_called_once_with()

    asyncio.run(run())

def test_async_remove_entry_delete_enabled():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        entry.options = {
            "delete_data_on_remove": True,
        }

        with patch("custom_components.day_planner.DayPlannerStorage") as storage_class:
            storage = storage_class.return_value
            storage.async_delete = AsyncMock()

            await async_remove_entry(
                hass,
                entry,
            )

            storage.async_delete.assert_awaited_once_with()

    asyncio.run(run())


def test_async_remove_entry_delete_disabled():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        entry.options = {
            "delete_data_on_remove": False,
        }

        with patch("custom_components.day_planner.DayPlannerStorage") as storage_class:
            storage = storage_class.return_value
            storage.async_delete = AsyncMock()

            await async_remove_entry(
                hass,
                entry,
            )

            storage.async_delete.assert_not_awaited()

    asyncio.run(run())

def test_async_unload_entry_failure():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        hass.config_entries.async_unload_platforms = AsyncMock(
            return_value=False
        )

        ha_scheduler = MagicMock()
        entry.runtime_data.ha_scheduler = ha_scheduler

        result = await async_unload_entry(
            hass,
            entry,
        )

        assert result is False

        hass.config_entries.async_unload_platforms.assert_awaited_once_with(
            entry,
            PLATFORMS,
        )

        ha_scheduler.cancel.assert_not_called()

    asyncio.run(run())

def test_migrate_entity_ids():
    async def run():
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "entry1"

        registry = MagicMock()

        next_event = MagicMock()
        next_event.unique_id = "day_planner_next_event"
        next_event.entity_id = "sensor.next_event"

        current_day_type = MagicMock()
        current_day_type.unique_id = (
            "day_planner_current_day_type"
        )
        current_day_type.entity_id = (
            "sensor.current_day_type"
        )

        current_moment = MagicMock()
        current_moment.unique_id = (
            "day_planner_current_moment"
        )
        current_moment.entity_id = (
            "sensor.current_moment"
        )

        calendar = MagicMock()
        calendar.unique_id = "day_planner_calendar"
        calendar.entity_id = "calendar.planning"

        entries = [
            next_event,
            current_day_type,
            current_moment,
            calendar,
        ]

        with (
            patch(
                "custom_components.day_planner.er.async_get",
                return_value=registry,
            ),
            patch(
                "custom_components.day_planner."
                "er.async_entries_for_config_entry",
                return_value=entries,
            ) as entries_for_config_entry,
        ):
            await _async_migrate_entity_ids(
                hass,
                entry,
            )

        entries_for_config_entry.assert_called_once_with(
            registry,
            "entry1",
        )

        assert (
            registry.async_update_entity.call_count
            == 4
        )

        registry.async_update_entity.assert_any_call(
            "sensor.next_event",
            new_entity_id="sensor.day_planner_next_event",
        )

        registry.async_update_entity.assert_any_call(
            "sensor.current_day_type",
            new_entity_id=(
                "sensor.day_planner_current_day_type"
            ),
        )

        registry.async_update_entity.assert_any_call(
            "sensor.current_moment",
            new_entity_id=(
                "sensor.day_planner_current_moment"
            ),
        )

        registry.async_update_entity.assert_any_call(
            "calendar.planning",
            new_entity_id=(
                "calendar.day_planner_planning"
            ),
        )

    asyncio.run(run())

def test_migrate_entity_ids_already_migrated():
    async def run():
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "entry1"

        registry = MagicMock()

        entity = MagicMock()
        entity.unique_id = "day_planner_next_event"
        entity.entity_id = (
            "sensor.day_planner_next_event"
        )

        with (
            patch(
                "custom_components.day_planner.er.async_get",
                return_value=registry,
            ),
            patch(
                "custom_components.day_planner."
                "er.async_entries_for_config_entry",
                return_value=[entity],
            ),
        ):
            await _async_migrate_entity_ids(
                hass,
                entry,
            )

        registry.async_update_entity.assert_not_called()

    asyncio.run(run())


def test_migrate_entity_ids_missing():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        registry = MagicMock()
        registry.async_get_entity_id.return_value = None

        with patch(
            "custom_components.day_planner.er.async_get",
            return_value=registry,
        ):
            await _async_migrate_entity_ids(
                hass,
                entry,
            )

        registry.async_update_entity.assert_not_called()

    asyncio.run(run())



