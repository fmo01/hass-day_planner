from datetime import date, datetime, time
from unittest.mock import MagicMock

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_moment import (
    ScheduledMoment,
)
from custom_components.day_planner.domain.time_definition import (
    TimeDefinition,
)
from custom_components.day_planner.planner.scheduler import (
    PlannerScheduler,
)


def test_scheduler_events_for_date():
    moment1 = Moment(
        id="m1",
        name="Réveil",
    )

    moment2 = Moment(
        id="m2",
        name="Départ",
    )

    scheduled1 = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(8, 15),
        ),
    )

    scheduled2 = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(7, 30),
        ),
    )

    resolver = MagicMock()

    resolver.resolve_schedule.return_value = (
        (scheduled1, moment1),
        (scheduled2, moment2),
    )

    scheduler = PlannerScheduler(
        resolver
    )

    events = scheduler.events_for_date(
        date(2026, 8, 31)
    )

    assert len(events) == 2

    assert events[0].scheduled_at == datetime(
        2026,
        8,
        31,
        7,
        30,
    )
    assert events[0].moment == moment2

    assert events[1].scheduled_at == datetime(
        2026,
        8,
        31,
        8,
        15,
    )
    assert events[1].moment == moment1

    resolver.resolve_schedule.assert_called_once_with(
        date(2026, 8, 31)
    )

def test_scheduler_next_event_today():
    moment1 = Moment(
        id="m1",
        name="Réveil",
    )

    moment2 = Moment(
        id="m2",
        name="Départ",
    )

    scheduled1 = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(7, 30),
        ),
    )

    scheduled2 = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(18, 0),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (scheduled1, moment1),
        (scheduled2, moment2),
    )

    scheduler = PlannerScheduler(resolver)

    event = scheduler.next_event(
        datetime(2026, 8, 31, 12, 0)
    )

    assert event is not None
    assert event.scheduled_at == datetime(
        2026, 8, 31, 18, 0
    )
    assert event.moment == moment2

def test_scheduler_next_event_tomorrow():
    moment = Moment(
        id="m1",
        name="Réveil",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(7, 30),
        ),
    )

    resolver = MagicMock()

    def resolve_schedule(target_date):
        if target_date == date(2026, 9, 1):
            return ((scheduled, moment),)

        return ()

    resolver.resolve_schedule.side_effect = resolve_schedule

    scheduler = PlannerScheduler(resolver)

    event = scheduler.next_event(
        datetime(2026, 8, 31, 23, 0)
    )

    assert event is not None
    assert event.scheduled_at == datetime(
        2026, 9, 1, 7, 30
    )
    assert event.moment == moment

def test_scheduler_next_event_none():
    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ()

    scheduler = PlannerScheduler(resolver)

    event = scheduler.next_event(
        datetime(2026, 8, 31, 12, 0),
        max_days=7,
    )

    assert event is None

def test_scheduler_next_event_at_now_is_skipped():
    moment_now = Moment(
        id="m1",
        name="Réveil",
    )

    moment_later = Moment(
        id="m2",
        name="Départ",
    )

    scheduled_now = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(12, 0),
        ),
    )

    scheduled_later = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(18, 0),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (scheduled_now, moment_now),
        (scheduled_later, moment_later),
    )

    scheduler = PlannerScheduler(resolver)

    event = scheduler.next_event(
        datetime(2026, 8, 31, 12, 0)
    )

    assert event is not None
    assert event.scheduled_at == datetime(
        2026,
        8,
        31,
        18,
        0,
    )
    assert event.moment == moment_later


