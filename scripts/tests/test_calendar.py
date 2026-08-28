import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

from homeassistant.components.calendar import CalendarEvent
from homeassistant.util import dt as dt_util

from custom_components.day_planner.calendar import (
    DayPlannerCalendar,
    async_setup_entry,
)
from custom_components.day_planner.const import (
    SIGNAL_PLANNER_UPDATED,
)
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_event import (
    ScheduledEvent,
)


def test_calendar_setup_entry():
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

    assert len(entities) == 1
    assert isinstance(
        entities[0],
        DayPlannerCalendar,
    )


def test_calendar_event():
    runtime = MagicMock()

    moment = Moment(
        id="m1",
        name="Réveil",
    )

    scheduled_event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            31,
            7,
            30,
        ),
        moment=moment,
    )

    runtime.scheduler.next_event.return_value = (
        scheduled_event
    )

    calendar = DayPlannerCalendar(runtime)

    with patch(
        "custom_components.day_planner.calendar.dt_util.now",
        return_value=datetime(
            2026,
            8,
            31,
            6,
            0,
        ),
    ):
        event = calendar.event

    assert isinstance(
        event,
        CalendarEvent,
    )

    assert event.summary == "Réveil"
    assert event.start.hour == 7
    assert event.start.minute == 30
    assert event.end.hour == 7
    assert event.end.minute == 31


def test_calendar_event_none():
    runtime = MagicMock()

    runtime.scheduler.next_event.return_value = None

    calendar = DayPlannerCalendar(runtime)

    with patch(
        "custom_components.day_planner.calendar.dt_util.now",
        return_value=datetime(
            2026,
            8,
            31,
            12,
            0,
        ),
    ):
        assert calendar.event is None


def test_calendar_dispatcher_update():
    runtime = MagicMock()

    calendar = DayPlannerCalendar(runtime)

    hass = MagicMock()
    calendar.hass = hass

    remove_listener = MagicMock()

    calendar.async_on_remove = MagicMock()
    calendar.async_write_ha_state = MagicMock()
    calendar.async_update_event_listeners = MagicMock()

    with patch(
        "custom_components.day_planner.calendar.async_dispatcher_connect",
        return_value=remove_listener,
    ) as dispatcher_connect:
        asyncio.run(
            calendar.async_added_to_hass()
        )

    dispatcher_connect.assert_called_once_with(
        hass,
        SIGNAL_PLANNER_UPDATED,
        calendar._handle_planner_updated,
    )

    calendar.async_on_remove.assert_called_once_with(
        remove_listener
    )

    calendar._handle_planner_updated()

    calendar.async_write_ha_state.assert_called_once_with()
    calendar.async_update_event_listeners.assert_called_once_with()

def test_calendar_get_events():
    runtime = MagicMock()

    moment1 = Moment(
        id="m1",
        name="Réveil",
    )

    moment2 = Moment(
        id="m2",
        name="Départ",
    )

    runtime.scheduler.events_for_date.side_effect = [
        (
            ScheduledEvent(
                scheduled_at=datetime(
                    2026, 8, 31, 7, 30
                ),
                moment=moment1,
            ),
            ScheduledEvent(
                scheduled_at=datetime(
                    2026, 8, 31, 8, 15
                ),
                moment=moment2,
            ),
        ),
        (),
    ]

    calendar = DayPlannerCalendar(runtime)

    start = datetime(
        2026, 8, 31, 0, 0,
        tzinfo=dt_util.DEFAULT_TIME_ZONE,
    )

    end = datetime(
        2026, 9, 1, 0, 0,
        tzinfo=dt_util.DEFAULT_TIME_ZONE,
    )

    events = asyncio.run(
        calendar.async_get_events(
            MagicMock(),
            start,
            end,
        )
    )

    assert len(events) == 2

    assert events[0].summary == "Réveil"
    assert events[0].start.hour == 7
    assert events[0].start.minute == 30

    assert events[1].summary == "Départ"
    assert events[1].start.hour == 8
    assert events[1].start.minute == 15


def test_calendar_get_events_filters_range():
    runtime = MagicMock()

    moment = Moment(
        id="m1",
        name="Réveil",
    )

    runtime.scheduler.events_for_date.return_value = (
        ScheduledEvent(
            scheduled_at=datetime(
                2026, 8, 31, 7, 30
            ),
            moment=moment,
        ),
    )

    calendar = DayPlannerCalendar(runtime)

    start = datetime(
        2026, 8, 31, 8, 0,
        tzinfo=dt_util.DEFAULT_TIME_ZONE,
    )

    end = datetime(
        2026, 8, 31, 12, 0,
        tzinfo=dt_util.DEFAULT_TIME_ZONE,
    )

    events = asyncio.run(
        calendar.async_get_events(
            MagicMock(),
            start,
            end,
        )
    )

    assert events == []
