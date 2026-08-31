import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.planner_configuration import \
    PlannerConfiguration
from custom_components.day_planner.storage import DayPlannerStorage


def test_storage_load_empty():
    hass = MagicMock()

    async def run():
        with patch("custom_components.day_planner.storage.Store") as store_class:
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
        with patch("custom_components.day_planner.storage.Store") as store_class:
            store = store_class.return_value
            store.async_save = AsyncMock()

            storage = DayPlannerStorage(hass)

            await storage.async_save(configuration)

        configuration.to_dict.assert_called_once_with()
        store.async_save.assert_awaited_once_with({"test": "value"})

    asyncio.run(run())


def test_storage_delete():
    hass = MagicMock()

    async def run():
        with patch("custom_components.day_planner.storage.Store") as store_class:
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
        with patch("custom_components.day_planner.storage.Store") as store_class, patch(
            "custom_components.day_planner.storage.PlannerConfiguration.from_dict"
        ) as from_dict:
            store = store_class.return_value
            store.async_load = AsyncMock(return_value={"test": "data"})

            from_dict.return_value = configuration

            storage = DayPlannerStorage(hass)

            result = await storage.async_load()

            assert result == configuration
            from_dict.assert_called_once_with({"test": "data"})

    asyncio.run(run())


def test_storage_roundtrip_moment_with_actions():
    hass = MagicMock()

    configuration = PlannerConfiguration(
        moments=(
            Moment(
                id="m1",
                name="Réveil",
                icon="mdi:alarm",
                actions=(
                    Action(
                        id="salon_on",
                        sequence=[
                            {
                                "action": "light.turn_on",
                                "target": {
                                    "entity_id": "light.salon",
                                },
                                "data": {
                                    "brightness_pct": 50,
                                },
                            }
                        ],
                    ),
                ),
            ),
        ),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    async def run():
        saved_data = None

        with patch("custom_components.day_planner.storage.Store") as store_class:
            store = store_class.return_value

            async def fake_save(data):
                nonlocal saved_data
                saved_data = data

            store.async_save = AsyncMock(side_effect=fake_save)
            store.async_load = AsyncMock(side_effect=lambda: saved_data)

            storage = DayPlannerStorage(hass)

            await storage.async_save(configuration)

            restored = await storage.async_load()

        assert restored == configuration

        assert restored.moments[0].actions[0].id == "salon_on"

        assert restored.moments[0].actions[0].sequence == [
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
                "data": {
                    "brightness_pct": 50,
                },
            }
        ]
    asyncio.run(run())
