from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import asyncio

from custom_components.day_planner.storage import DayPlannerStorage
from custom_components.day_planner.domain.planner_configuration import (
    PlannerConfiguration,
)

def test_storage_load_empty():
    hass = MagicMock()

    async def run():
        with patch(
            "custom_components.day_planner.storage.Store"
        ) as store_class:
            store = store_class.return_value
            store.async_load = AsyncMock(return_value=None)

            storage = DayPlannerStorage(hass)

            result = await storage.async_load()

        assert result == PlannerConfiguration.empty()
        store.async_load.assert_awaited_once_with()

    asyncio.run(run())

def test_storage_save():
    hass = MagicMock()
    configuration = MagicMock()
    configuration.to_dict.return_value = {"test": "value"}

    async def run():
        with patch(
            "custom_components.day_planner.storage.Store"
        ) as store_class:
            store = store_class.return_value
            store.async_save = AsyncMock()

            storage = DayPlannerStorage(hass)

            await storage.async_save(configuration)

        configuration.to_dict.assert_called_once_with()
        store.async_save.assert_awaited_once_with(
            {"test": "value"}
        )

    asyncio.run(run())

def test_storage_delete():
    hass = MagicMock()

    async def run():
        with patch(
            "custom_components.day_planner.storage.Store"
        ) as store_class:
            store = store_class.return_value
            store.async_remove = AsyncMock()

            storage = DayPlannerStorage(hass)

            await storage.async_delete()

        store.async_remove.assert_awaited_once_with()

    asyncio.run(run())

def test_storage_load_configuration():
    hass = MagicMock()

    configuration = PlannerConfiguration.empty()

    async def run():
        with patch(
            "custom_components.day_planner.storage.Store"
        ) as store_class, patch(
            "custom_components.day_planner.storage.PlannerConfiguration.from_dict"
        ) as from_dict:

            store = store_class.return_value
            store.async_load = AsyncMock(
                return_value={"test": "data"}
            )

            from_dict.return_value = configuration

            storage = DayPlannerStorage(hass)

            result = await storage.async_load()

            assert result == configuration
            from_dict.assert_called_once_with(
                {"test": "data"}
            )

    asyncio.run(run())

