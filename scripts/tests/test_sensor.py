import asyncio
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from custom_components.day_planner.const import (
    SIGNAL_PLANNER_UPDATED,
)

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.resolved_day_context import (
    ResolvedDayContext,
)
from custom_components.day_planner.domain.scheduled_event import (
    ScheduledEvent,
)
from custom_components.day_planner.sensor import (
    DayPlannerNextEventSensor,
    DayPlannerCurrentDayTypeSensor,
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

    assert len(entities) == 2
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

    sensor = DayPlannerNextEventSensor(
        runtime
    )

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
        "moment_id": "wake_up",
        "scheduled_at": "2026-08-31T07:30:00",
    }

    assert runtime.scheduler.next_event.call_count == 2

def test_sensor_without_next_event():
    runtime = MagicMock()

    runtime.scheduler.next_event.return_value = None

    sensor = DayPlannerNextEventSensor(
        runtime
    )

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
        assert sensor.extra_state_attributes == {}

def test_sensor_dispatcher_update():
    runtime = MagicMock()

    sensor = DayPlannerNextEventSensor(
        runtime
    )

    hass = MagicMock()
    sensor.hass = hass

    remove_listener = MagicMock()

    with patch(
        "custom_components.day_planner.sensor.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        sensor.async_on_remove = MagicMock()

        asyncio.run(
            sensor.async_added_to_hass()
        )

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        sensor._handle_planner_updated,
    )

    sensor.async_on_remove.assert_called_once_with(
        remove_listener
    )

def test_sensor_handle_planner_updated():
    runtime = MagicMock()

    sensor = DayPlannerNextEventSensor(
        runtime
    )

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

    runtime.resolver.resolve_day_context.return_value = (
        context
    )

    sensor = DayPlannerCurrentDayTypeSensor(
        runtime
    )

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

    runtime.resolver.resolve_day_context.return_value = (
        context
    )

    sensor = DayPlannerCurrentDayTypeSensor(
        runtime
    )

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
        "date": "2026-08-29",
        "cycle_id": None,
        "week_schedule_id": None,
        "calendar_exception_id": None,
    }



def test_sensor_current_day_type_dispatcher_update():
    runtime = MagicMock()

    sensor = DayPlannerCurrentDayTypeSensor(
        runtime
    )

    hass = MagicMock()
    sensor.hass = hass

    remove_listener = MagicMock()

    sensor.async_on_remove = MagicMock()
    sensor.async_write_ha_state = MagicMock()

    with patch(
        "custom_components.day_planner.sensor.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        asyncio.run(
            sensor.async_added_to_hass()
        )

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        sensor._handle_planner_updated,
    )

    sensor.async_on_remove.assert_called_once_with(
        remove_listener
    )

    sensor._handle_planner_updated()

    sensor.async_write_ha_state.assert_called_once_with()


