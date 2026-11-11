import asyncio
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from custom_components.day_planner.const import SIGNAL_PLANNER_UPDATED
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.resolved_day_context import ResolvedDayContext
from custom_components.day_planner.domain.scheduled_event import ScheduledEvent
from custom_components.day_planner.integration_info import INTEGRATION_VERSION
from custom_components.day_planner.sensor import (
    DayPlannerCurrentDayTypeSensor,
    DayPlannerCurrentMomentSensor,
    DayPlannerNextEventSensor,
    async_setup_entry,
)


def test_sensor_setup_entry():
    hass = MagicMock()
    entry = MagicMock()
    runtime = MagicMock()

    entry.runtime_data = runtime

    async_add_entities = MagicMock()

    asyncio.run(
        async_setup_entry(
            hass,
            entry,
            async_add_entities,
        )
    )

    async_add_entities.assert_called_once()

    entities = async_add_entities.call_args.args[0]

    assert len(entities) == 3
    assert isinstance(
        entities[0],
        DayPlannerNextEventSensor,
    )
    assert isinstance(
        entities[1],
        DayPlannerCurrentDayTypeSensor,
    )


def test_sensor_next_event():
    runtime = MagicMock()

    moment = Moment(
        id="wake_up",
        name="Réveil",
    )

    event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            31,
            7,
            30,
        ),
        moment=moment,
    )

    runtime.scheduler.next_event.return_value = event

    sensor = DayPlannerNextEventSensor(runtime)

    current = datetime(
        2026,
        8,
        31,
        6,
        0,
    )

    with patch(
        "custom_components.day_planner.sensor.dt_util.now",
        return_value=current,
    ):
        assert sensor.native_value == "Réveil"

        attributes = sensor.extra_state_attributes

    assert attributes == {
        "integration": "Day Planner",
        "integration_version": INTEGRATION_VERSION,
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
        "moment_id": "wake_up",
        "scheduled_at": "2026-08-31T07:30:00",
    }

    assert runtime.scheduler.next_event.call_count == 2


def test_sensor_without_next_event():
    runtime = MagicMock()

    runtime.scheduler.next_event.return_value = None

    sensor = DayPlannerNextEventSensor(runtime)

    current = datetime(
        2026,
        8,
        31,
        12,
        0,
    )

    with patch(
        "custom_components.day_planner.sensor.dt_util.now",
        return_value=current,
    ):
        assert sensor.native_value is None
        assert sensor.extra_state_attributes == {
            "integration": "Day Planner",
            "integration_version": INTEGRATION_VERSION,
            "release_url": "https://github.com/fmo01/hass-day_planner/releases",
            "moment_id": None,
            "scheduled_at": None,
        }


def test_sensor_dispatcher_update():
    runtime = MagicMock()

    sensor = DayPlannerNextEventSensor(runtime)

    hass = MagicMock()
    sensor.hass = hass

    remove_listener = MagicMock()

    with patch(
        "custom_components.day_planner.sensor.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        sensor.async_on_remove = MagicMock()

        asyncio.run(sensor.async_added_to_hass())

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        sensor._handle_planner_updated,
    )

    sensor.async_on_remove.assert_called_once_with(remove_listener)


def test_sensor_handle_planner_updated():
    runtime = MagicMock()

    sensor = DayPlannerNextEventSensor(runtime)

    sensor.async_write_ha_state = MagicMock()

    sensor._handle_planner_updated()

    sensor.async_write_ha_state.assert_called_once_with()


def test_sensor_current_day_type():
    runtime = MagicMock()

    day_type = DayType(
        id="test_day",
        name="Test Day",
        scheduled_moments=(),
    )

    context = ResolvedDayContext(
        date=date(2026, 8, 29),
        day_type=day_type,
        cycle_id="test_cycle",
        week_schedule_id="test_week",
        calendar_exception_id=None,
    )

    runtime.resolver.resolve_day_context.return_value = context

    sensor = DayPlannerCurrentDayTypeSensor(runtime)

    current = datetime(
        2026,
        8,
        29,
        10,
        0,
    )

    with patch(
        "custom_components.day_planner.sensor.dt_util.now",
        return_value=current,
    ):
        assert sensor.native_value == "Test Day"

        attributes = sensor.extra_state_attributes

    assert attributes == {
        "integration": "Day Planner",
        "integration_version": INTEGRATION_VERSION,
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
        "date": "2026-08-29",
        "cycle_id": "test_cycle",
        "week_schedule_id": "test_week",
        "calendar_exception_id": None,
        "day_type_id": "test_day",
    }


def test_sensor_current_day_type_none():
    runtime = MagicMock()

    context = ResolvedDayContext(
        date=date(2026, 8, 29),
        day_type=None,
        cycle_id=None,
        week_schedule_id=None,
        calendar_exception_id=None,
    )

    runtime.resolver.resolve_day_context.return_value = context

    sensor = DayPlannerCurrentDayTypeSensor(runtime)

    current = datetime(
        2026,
        8,
        29,
        10,
        0,
    )

    with patch(
        "custom_components.day_planner.sensor.dt_util.now",
        return_value=current,
    ):
        assert sensor.native_value is None

        attributes = sensor.extra_state_attributes

    assert attributes == {
        "integration": "Day Planner",
        "integration_version": INTEGRATION_VERSION,
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
        "date": "2026-08-29",
        "cycle_id": None,
        "week_schedule_id": None,
        "calendar_exception_id": None,
        "day_type_id": None,
    }


def test_sensor_current_day_type_dispatcher_update():
    runtime = MagicMock()

    sensor = DayPlannerCurrentDayTypeSensor(runtime)

    hass = MagicMock()
    sensor.hass = hass

    remove_listener = MagicMock()

    sensor.async_on_remove = MagicMock()
    sensor.async_write_ha_state = MagicMock()

    with patch(
        "custom_components.day_planner.sensor.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        asyncio.run(sensor.async_added_to_hass())

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        sensor._handle_planner_updated,
    )

    sensor.async_on_remove.assert_called_once_with(remove_listener)

    sensor._handle_planner_updated()

    sensor.async_write_ha_state.assert_called_once_with()


def test_sensor_current_moment():
    runtime = MagicMock()

    moment = Moment(
        id="m1",
        name="Réveil",
    )

    event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            29,
            8,
            0,
        ),
        moment=moment,
    )

    runtime.scheduler.current_moment.return_value = event

    sensor = DayPlannerCurrentMomentSensor(runtime)

    assert sensor.native_value == "Réveil"

    assert sensor.extra_state_attributes == {
        "integration": "Day Planner",
        "integration_version": INTEGRATION_VERSION,
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
        "moment_id": "m1",
        "scheduled_at": "2026-08-29T08:00:00",
    }


def test_sensor_current_moment_none():
    runtime = MagicMock()

    runtime.scheduler.current_moment.return_value = None

    sensor = DayPlannerCurrentMomentSensor(runtime)

    assert sensor.native_value is None
    assert sensor.extra_state_attributes == {}


def test_sensor_current_moment_dispatcher_update():
    runtime = MagicMock()

    sensor = DayPlannerCurrentMomentSensor(runtime)

    hass = MagicMock()
    sensor.hass = hass

    remove_listener = MagicMock()

    sensor.async_on_remove = MagicMock()
    sensor.async_write_ha_state = MagicMock()

    with patch(
        "custom_components.day_planner.sensor.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        asyncio.run(sensor.async_added_to_hass())

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        sensor._handle_planner_updated,
    )

    sensor.async_on_remove.assert_called_once_with(remove_listener)

    sensor._handle_planner_updated()

    sensor.async_write_ha_state.assert_called_once_with()


def test_location_binary_sensor(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from homeassistant.helpers.entity import EntityCategory
    from homeassistant.util import dt as dt_util

    from custom_components.day_planner.binary_sensor import (
        DayPlannerLocationSensor,
    )
    from custom_components.day_planner.binary_sensor import (
        async_setup_entry as setup_binary,
    )
    from custom_components.day_planner.location import LocationResult, LocationStatus

    async def run():
        location = SimpleNamespace(result=None, async_evaluate=AsyncMock())
        entry = SimpleNamespace(runtime_data=SimpleNamespace(location=location))
        add = MagicMock()
        translations = await _location_translations(tmp_path, "fr")
        hass = MagicMock()
        hass.config.language = "fr"
        with patch(
            "custom_components.day_planner.binary_sensor.async_get_translations",
            AsyncMock(return_value=translations),
        ) as get_translations:
            await setup_binary(hass, entry, add)
            get_translations.assert_awaited_once_with(hass, "fr", "entity", {"day_planner"})
        entity = add.call_args.args[0][0]
        assert isinstance(entity, DayPlannerLocationSensor)
        assert entity.unique_id == "day_planner_location"
        assert entity.entity_id == "binary_sensor.day_planner_location"
        entity.platform_data = SimpleNamespace(
            domain="binary_sensor",
            platform_name="day_planner",
            platform_translations=translations,
            component_translations={},
        )
        assert entity.name == "Day Planner — Localisation"
        assert entity.translation_key == "location"
        assert entity.has_entity_name
        assert "_attr_name" not in DayPlannerLocationSensor.__dict__
        assert entity.entity_category == EntityCategory.DIAGNOSTIC
        assert not entity.should_poll
        assert not entity.available
        assert entity.is_on is None
        assert entity.extra_state_attributes["integration"] == "Day Planner"
        now = dt_util.utcnow()
        location.result = LocationResult(
            LocationStatus.RESOLVED,
            country_code="CH",
            country_name="Switzerland",
            subdivision_code="CH-GE",
            subdivision_name="Genève",
            locality="Genève",
            last_evaluated=now,
            resolved_at=now,
            from_cache=True,
        )
        assert entity.available and entity.is_on
        attrs = entity.extra_state_attributes
        assert attrs["country_code"] == "CH"
        assert attrs["last_evaluated"] == now.isoformat()
        assert attrs["resolved_at"] == now.isoformat()
        assert attrs["from_cache"] is True
        assert attrs["status"] == "resolved"
        location.result = LocationResult(LocationStatus.UNRESOLVED, reason="request_failed")
        assert entity.available and not entity.is_on
        assert entity.extra_state_attributes["reason"] == "request_failed"
        assert "inaccessible" in entity.extra_state_attributes["reason_detail"]
        assert entity.extra_state_attributes["last_evaluated"] is None
        assert entity.extra_state_attributes["resolved_at"] is None
        entity.hass = MagicMock()
        with patch("custom_components.day_planner.binary_sensor.async_dispatcher_connect") as connect:
            with patch.object(entity, "async_on_remove") as remove:
                await entity.async_added_to_hass()
                remove.assert_called_once_with(connect.return_value)
        with patch.object(entity, "async_write_ha_state") as write:
            entity._location_updated()
            write.assert_called_once_with()
        await entity.async_update()
        location.async_evaluate.assert_awaited_once_with()

    asyncio.run(run())


async def _location_translations(tmp_path, language):
    """Load the delivered JSON files through HA's actual translation loader."""
    import json
    from pathlib import Path
    from unittest.mock import AsyncMock

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.translation import async_get_translations
    from homeassistant.loader import Integration
    from homeassistant.loader import async_setup as setup_loader

    hass = HomeAssistant(str(tmp_path))
    setup_loader(hass)
    root = Path(__file__).resolve().parents[2] / "custom_components/day_planner"
    integration = Integration(
        hass,
        "custom_components.day_planner",
        root,
        json.loads((root / "manifest.json").read_text()),
        {"translations"},
    )
    try:
        with patch(
            "homeassistant.helpers.translation.async_get_integrations",
            AsyncMock(return_value={"day_planner": integration}),
        ):
            return await async_get_translations(hass, language, "entity", {"day_planner"})
    finally:
        await hass.async_stop()


def test_location_native_translations_and_fallback(tmp_path):
    """Verify names and readable reasons use HA's native JSON translations."""
    from types import SimpleNamespace

    from custom_components.day_planner.binary_sensor import DayPlannerLocationSensor
    from custom_components.day_planner.location import LocationResult, LocationStatus

    async def run():
        for language, name, fragment in [
            ("fr", "Day Planner — Localisation", "inaccessible"),
            ("en", "Day Planner — Location", "unreachable"),
            ("zz", "Day Planner — Location", "unreachable"),
        ]:
            translations = await _location_translations(tmp_path, language)
            location = SimpleNamespace(result=LocationResult(LocationStatus.UNRESOLVED, reason="request_failed"))
            entity = DayPlannerLocationSensor(location, translations)
            entity.platform_data = SimpleNamespace(
                domain="binary_sensor",
                platform_name="day_planner",
                platform_translations=translations,
                component_translations={},
            )
            assert entity.name == name
            assert fragment in entity.extra_state_attributes["reason_detail"]
            assert entity.extra_state_attributes["reason"] == "request_failed"
            location.result = LocationResult(LocationStatus.UNRESOLVED, reason="future_reason")
            assert entity.extra_state_attributes["reason_detail"] == "future_reason"
            location.result = LocationResult(LocationStatus.RESOLVED)
            assert entity.extra_state_attributes["reason_detail"] is None
            key = "component.day_planner.entity.binary_sensor.location.state_attributes."
            assert translations[key + "country_name.name"]
            assert translations[key + "status.state.resolved"]

    asyncio.run(run())


def test_location_translation_schema_and_reason_coverage():
    """Every emitted reason must be translated in both delivered languages."""
    import ast
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "custom_components/day_planner"
    tree = ast.parse((root / "location.py").read_text())
    reasons = {
        node.value
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        for keyword in call.keywords
        if keyword.arg == "reason"
        for node in ast.walk(keyword.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    catalogs = [
        json.loads((root / name).read_text())["entity"]["binary_sensor"]["location"]
        for name in ["strings.json", "translations/en.json", "translations/fr.json"]
    ]
    assert catalogs[0] == catalogs[1]
    for catalog in catalogs:
        attributes = catalog["state_attributes"]
        assert attributes["reason"]["state"].keys() == reasons
        assert attributes["status"]["state"].keys() == {
            "resolved",
            "unresolved",
            "unsupported",
        }
        assert all(isinstance(v, str) and v for v in attributes["reason"]["state"].values())
        assert all(v["name"] for v in attributes.values())
