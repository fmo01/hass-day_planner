import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.metadata import Audit
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


def test_storage_roundtrip_day_type_with_audit():
    """Audit metadata survives storage save and load."""

    hass = MagicMock()

    created_at = datetime(
        2026,
        10,
        19,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        19,
        12,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="user_1",
        created_at=created_at,
        modified_by="user_2",
        modified_at=modified_at,
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(
            DayType(
                id="work",
                name="Télétravail",
                scheduled_moments=(),
                audit=audit,
            ),
        ),
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

            assert saved_data["day_types"][0]["audit"] == {
                "created_by": "user_1",
                "created_at": created_at.isoformat(),
                "modified_by": "user_2",
                "modified_at": modified_at.isoformat(),
            }

            restored = await storage.async_load()

        assert restored == configuration

        restored_audit = restored.day_types[0].audit

        assert restored_audit is not None
        assert restored_audit.created_by == "user_1"
        assert restored_audit.created_at == created_at
        assert restored_audit.modified_by == "user_2"
        assert restored_audit.modified_at == modified_at

    asyncio.run(run())


def test_storage_load_legacy_day_type_without_audit():
    """Existing configurations without audit remain readable."""

    hass = MagicMock()

    legacy_data = {
        "moments": [],
        "day_types": [
            {
                "id": "legacy",
                "name": "Ancienne journée",
                "scheduled_moments": [],
            },
        ],
        "week_schedules": [],
        "cycles": [],
        "calendar_exceptions": [],
    }

    async def run():
        with patch("custom_components.day_planner.storage.Store") as store_class:
            store = store_class.return_value
            store.async_load = AsyncMock(return_value=legacy_data)

            storage = DayPlannerStorage(hass)

            restored = await storage.async_load()

        assert len(restored.day_types) == 1

        day_type = restored.day_types[0]

        assert day_type.id == "legacy"
        assert day_type.name == "Ancienne journée"
        assert day_type.audit is None

        assert "audit" not in day_type.to_dict()

    asyncio.run(run())
