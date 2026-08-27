import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner import (async_remove_entry,
                                           async_setup_entry,
                                           async_unload_entry)
from custom_components.day_planner.domain.planner_configuration import \
    PlannerConfiguration


def test_async_setup_entry_empty_configuration():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

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

    asyncio.run(run())

def test_async_setup_entry_existing_configuration():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

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

    asyncio.run(run())
def test_async_unload_entry():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        ha_scheduler = MagicMock()
        entry.runtime_data.ha_scheduler = ha_scheduler

        result = await async_unload_entry(
            hass,
            entry,
        )

        assert result is True

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
