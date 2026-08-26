import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner import (
    async_remove_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.day_planner.domain.planner_configuration import (
    PlannerConfiguration,
)


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
                "custom_components.day_planner.async_setup_services",
                new=AsyncMock(),
            ),
        ):
            storage = storage_class.return_value
            storage.async_load = AsyncMock(
                return_value=configuration
            )
            storage.async_save = AsyncMock()

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

        assert entry.runtime_data is not None

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
            ),
            patch(
                "custom_components.day_planner.async_setup_services",
                new=AsyncMock(),
            ),
        ):
            storage = storage_class.return_value
            storage.async_load = AsyncMock(
                return_value=configuration
            )
            storage.async_save = AsyncMock()

            result = await async_setup_entry(
                hass,
                entry,
            )

        assert result is True

        storage.async_load.assert_awaited_once_with()
        storage.async_save.assert_not_awaited()

    asyncio.run(run())


def test_async_unload_entry():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        result = await async_unload_entry(
            hass,
            entry,
        )

        assert result is True

    asyncio.run(run())


def test_async_remove_entry_delete_enabled():
    async def run():
        hass = MagicMock()
        entry = MagicMock()

        entry.options = {
            "delete_data_on_remove": True,
        }

        with patch(
            "custom_components.day_planner.DayPlannerStorage"
        ) as storage_class:
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

        with patch(
            "custom_components.day_planner.DayPlannerStorage"
        ) as storage_class:
            storage = storage_class.return_value
            storage.async_delete = AsyncMock()

            await async_remove_entry(
                hass,
                entry,
            )

            storage.async_delete.assert_not_awaited()

    asyncio.run(run())


