import asyncio
from datetime import date, datetime, time, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_event import ScheduledEvent
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.ha_scheduler import HomeAssistantScheduler
from custom_components.day_planner.planner.scheduler import PlannerScheduler


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

    scheduler = PlannerScheduler(resolver)

    events = scheduler.events_for_date(date(2026, 8, 31))

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

    resolver.resolve_schedule.assert_called_once_with(date(2026, 8, 31))


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

    event = scheduler.next_event(datetime(2026, 8, 31, 12, 0))

    assert event is not None
    assert event.scheduled_at == datetime(2026, 8, 31, 18, 0)
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

    event = scheduler.next_event(datetime(2026, 8, 31, 23, 0))

    assert event is not None
    assert event.scheduled_at == datetime(2026, 9, 1, 7, 30)
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

    event = scheduler.next_event(datetime(2026, 8, 31, 12, 0))

    assert event is not None
    assert event.scheduled_at == datetime(
        2026,
        8,
        31,
        18,
        0,
    )
    assert event.moment == moment_later


def test_scheduler_next_event_with_timezone():
    moment = Moment(
        id="m1",
        name="Test",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(23, 30),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ((scheduled, moment),)

    scheduler = PlannerScheduler(resolver)

    local_tz = timezone(timedelta(hours=2))

    now = datetime(
        2026,
        8,
        28,
        23,
        0,
        tzinfo=local_tz,
    )

    event = scheduler.next_event(now)

    assert event is not None

    assert event.scheduled_at == datetime(
        2026,
        8,
        28,
        23,
        30,
        tzinfo=local_tz,
    )

    assert event.scheduled_at.tzinfo == local_tz


def test_scheduler_current_event():
    moment = Moment(
        id="m1",
        name="Test",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(23, 30),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ((scheduled, moment),)

    scheduler = PlannerScheduler(resolver)

    local_tz = timezone(timedelta(hours=2))

    now = datetime(
        2026,
        8,
        28,
        23,
        30,
        30,
        tzinfo=local_tz,
    )

    event = scheduler.current_event(now)

    assert event is not None
    assert event.moment == moment
    assert event.scheduled_at == datetime(
        2026,
        8,
        28,
        23,
        30,
        tzinfo=local_tz,
    )


def test_scheduler_current_event_timezone_aware():
    moment = Moment(
        id="m1",
        name="Test",
    )

    local_tz = timezone(timedelta(hours=2))

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(23, 30),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ((scheduled, moment),)

    scheduler = PlannerScheduler(resolver)

    now = datetime(
        2026,
        8,
        28,
        23,
        30,
        30,
        tzinfo=local_tz,
    )

    event = scheduler.events_for_date(date(2026, 8, 28))[0]

    aware_event = ScheduledEvent(
        scheduled_at=event.scheduled_at.replace(tzinfo=local_tz),
        moment=event.moment,
    )

    scheduler.events_for_date = MagicMock(return_value=(aware_event,))

    result = scheduler.current_event(now)

    assert result is aware_event


def test_scheduler_current_event_none():
    moment = Moment(
        id="m1",
        name="Test",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(23, 30),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ((scheduled, moment),)

    scheduler = PlannerScheduler(resolver)

    now = datetime(
        2026,
        8,
        28,
        22,
        0,
    )

    result = scheduler.current_event(now)

    assert result is None


def test_scheduler_current_moment():
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
            fixed_time=time(8, 0),
        ),
    )

    scheduled2 = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(9, 0),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (scheduled1, moment1),
        (scheduled2, moment2),
    )

    scheduler = PlannerScheduler(resolver)

    event = scheduler.current_moment(
        datetime(
            2026,
            8,
            29,
            8,
            30,
        )
    )

    assert event is not None
    assert event.moment == moment1
    assert event.scheduled_at == datetime(
        2026,
        8,
        29,
        8,
        0,
    )


def test_scheduler_current_moment_latest():
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
            fixed_time=time(8, 0),
        ),
    )

    scheduled2 = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(9, 0),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (scheduled1, moment1),
        (scheduled2, moment2),
    )

    scheduler = PlannerScheduler(resolver)

    event = scheduler.current_moment(
        datetime(
            2026,
            8,
            29,
            14,
            0,
        )
    )

    assert event is not None
    assert event.moment == moment2


def test_scheduler_current_moment_none():
    moment = Moment(
        id="m1",
        name="Réveil",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(8, 0),
        ),
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = ((scheduled, moment),)

    scheduler = PlannerScheduler(resolver)

    event = scheduler.current_moment(
        datetime(
            2026,
            8,
            29,
            7,
            0,
        )
    )

    assert event is None


def test_scheduler_normalizes_naive_datetime_timezone():
    naive = datetime(
        2026,
        8,
        31,
        7,
        30,
    )

    aware_now = datetime(
        2026,
        8,
        31,
        6,
        0,
        tzinfo=timezone.utc,
    )

    normalized = PlannerScheduler._normalize_scheduled_at(
        naive,
        aware_now,
    )

    assert normalized == datetime(
        2026,
        8,
        31,
        7,
        30,
        tzinfo=timezone.utc,
    )


def test_scheduler_keeps_aware_datetime():
    scheduled_at = datetime(
        2026,
        8,
        31,
        7,
        30,
        tzinfo=timezone.utc,
    )

    reference = datetime(
        2026,
        8,
        31,
        6,
        0,
        tzinfo=timezone.utc,
    )

    normalized = PlannerScheduler._normalize_scheduled_at(
        scheduled_at,
        reference,
    )

    assert normalized is scheduled_at


def test_scheduler_does_not_catch_up_missed_event():
    resolver = MagicMock()

    missed_moment = Moment(
        id="wake_up",
        name="Réveil",
    )

    next_moment = Moment(
        id="departure",
        name="Départ",
    )

    resolver.resolve_schedule.return_value = (
        (
            ScheduledMoment(
                moment_id="wake_up",
                time_definition=TimeDefinition(
                    fixed_time=time(7, 30),
                ),
            ),
            missed_moment,
        ),
        (
            ScheduledMoment(
                moment_id="departure",
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
            next_moment,
        ),
    )

    scheduler = PlannerScheduler(resolver)

    now = datetime(
        2026,
        8,
        31,
        7,
        35,
    )

    event = scheduler.next_event(now)

    assert event is not None
    assert event.moment == next_moment
    assert event.scheduled_at == datetime(
        2026,
        8,
        31,
        8,
        0,
    )


def test_ha_scheduler_replans_after_configuration_change():
    hass = MagicMock()

    moment = Moment(
        id="departure",
        name="Départ",
    )

    old_event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            31,
            8,
            0,
        ),
        moment=moment,
    )

    new_event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            31,
            8,
            30,
        ),
        moment=moment,
    )

    scheduler = MagicMock()

    scheduler.next_event.side_effect = [
        old_event,
        new_event,
    ]

    scheduler.events_at.side_effect = [
        (old_event,),
        (new_event,),
    ]

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    old_cancel = MagicMock()
    new_cancel = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    async def run():
        with (
            patch(
                "custom_components.day_planner.ha_scheduler.dt_util.now",
                return_value=datetime(
                    2026,
                    8,
                    31,
                    7,
                    30,
                ),
            ),
            patch(
                "custom_components.day_planner.ha_scheduler."
                "async_track_point_in_time",
                side_effect=[
                    old_cancel,
                    new_cancel,
                ],
            ) as track,
        ):
            # Première programmation : 08:00
            await ha_scheduler.async_schedule_next()

            assert ha_scheduler._cancel is old_cancel
            assert track.call_args_list[0].args[2] == datetime(
                2026,
                8,
                31,
                8,
                0,
            )

            # Simulation d'une modification de configuration :
            # le scheduler retourne maintenant 08:30.
            await ha_scheduler.async_schedule_next()

            # L'ancienne programmation doit être annulée.
            old_cancel.assert_called_once_with()

            # La nouvelle doit être installée.
            assert ha_scheduler._cancel is new_cancel

            assert track.call_args_list[1].args[2] == datetime(
                2026,
                8,
                31,
                8,
                30,
            )

    asyncio.run(run())

    assert scheduler.next_event.call_count == 2


def test_scheduler_current_moment_normalizes_timezone():
    resolver = MagicMock()

    moment = Moment(
        id="m1",
        name="Réveil",
    )

    resolver.resolve_schedule.return_value = (
        (
            ScheduledMoment(
                moment_id="m1",
                time_definition=TimeDefinition(
                    fixed_time=time(7, 30),
                ),
            ),
            moment,
        ),
    )

    scheduler = PlannerScheduler(resolver)

    local_tz = timezone(timedelta(hours=2))

    now = datetime(
        2026,
        8,
        31,
        8,
        0,
        tzinfo=local_tz,
    )

    event = scheduler.current_moment(now)

    assert event is not None

    assert event.scheduled_at == datetime(
        2026,
        8,
        31,
        7,
        30,
        tzinfo=local_tz,
    )

    assert event.moment == moment


def test_scheduler_events_at_returns_simultaneous_moments():
    moment1 = Moment(
        id="m1",
        name="Réveil",
    )

    moment2 = Moment(
        id="m2",
        name="Chauffage",
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (
            ScheduledMoment(
                moment_id="m1",
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
            moment1,
        ),
        (
            ScheduledMoment(
                moment_id="m2",
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
            moment2,
        ),
    )

    scheduler = PlannerScheduler(resolver)

    scheduled_at = datetime(
        2026,
        10,
        13,
        8,
        0,
        tzinfo=timezone.utc,
    )

    events = scheduler.events_at(scheduled_at)

    assert len(events) == 2
    assert [event.moment for event in events] == [
        moment1,
        moment2,
    ]
    assert all(event.scheduled_at == scheduled_at for event in events)


def test_scheduler_handles_midnight_transition():
    evening = Moment(
        id="evening",
        name="Soir",
    )

    morning = Moment(
        id="morning",
        name="Réveil",
    )

    resolver = MagicMock()
    resolver.resolve_schedule.return_value = (
        (
            ScheduledMoment(
                moment_id="evening",
                time_definition=TimeDefinition(
                    fixed_time=time(23, 55),
                ),
            ),
            evening,
        ),
        (
            ScheduledMoment(
                moment_id="morning",
                time_definition=TimeDefinition(
                    fixed_time=time(0, 5),
                ),
            ),
            morning,
        ),
    )

    scheduler = PlannerScheduler(resolver)

    # Avant minuit, le dernier moment atteint est celui du soir.
    before_midnight = datetime(2026, 10, 13, 23, 59)

    current = scheduler.current_moment(before_midnight)

    assert current is not None
    assert current.moment == evening

    # Le prochain événement doit être celui du lendemain à 00:05.
    next_event = scheduler.next_event(before_midnight)

    assert next_event is not None
    assert next_event.moment == morning
    assert next_event.scheduled_at == datetime(2026, 10, 14, 0, 5)

    # Après minuit, le moment de la veille n'est pas reporté.
    assert scheduler.current_moment(datetime(2026, 10, 14, 0, 0)) is None

    # À 00:05, le premier moment du nouveau jour est atteint.
    current = scheduler.current_moment(datetime(2026, 10, 14, 0, 5))

    assert current is not None
    assert current.moment == morning
    assert current.scheduled_at == datetime(2026, 10, 14, 0, 5)


def _make_dst_scheduler(*hours):
    resolver = MagicMock()

    resolver.resolve_schedule.return_value = tuple(
        (
            ScheduledMoment(
                moment_id=f"m{index}",
                time_definition=TimeDefinition(
                    fixed_time=time(hour, minute),
                ),
            ),
            Moment(
                id=f"m{index}",
                name=f"Moment {index}",
            ),
        )
        for index, (hour, minute) in enumerate(hours)
    )

    return PlannerScheduler(resolver)


def test_scheduler_dst_spring_runs_missing_time_at_three():
    paris = ZoneInfo("Europe/Paris")

    scheduler = _make_dst_scheduler((2, 30))

    now = datetime(
        2026,
        3,
        29,
        1,
        59,
        tzinfo=paris,
    )

    event = scheduler.next_event(now)

    assert event is not None
    assert event.scheduled_at.isoformat() == ("2026-03-29T03:00:00+02:00")


def test_scheduler_dst_autumn_runs_only_first_occurrence():
    paris = ZoneInfo("Europe/Paris")

    scheduler = _make_dst_scheduler((2, 30))

    # Premier passage à 02:15 : 02:30 reste à venir.
    first_pass = datetime(
        2026,
        10,
        25,
        2,
        15,
        tzinfo=paris,
        fold=0,
    )

    event = scheduler.next_event(first_pass)

    assert event is not None
    assert event.scheduled_at.isoformat() == ("2026-10-25T02:30:00+02:00")

    # Second passage à 02:15 : le premier 02:30 est déjà passé.
    second_pass = datetime(
        2026,
        10,
        25,
        2,
        15,
        tzinfo=paris,
        fold=1,
    )

    event = scheduler.next_event(second_pass)

    assert event is not None
    assert event.scheduled_at.isoformat() == ("2026-10-26T02:30:00+01:00")


def test_scheduler_dst_spring_groups_missing_and_regular_moments():
    paris = ZoneInfo("Europe/Paris")

    scheduler = _make_dst_scheduler(
        (2, 10),
        (2, 30),
        (3, 0),
    )

    scheduled_at = datetime(
        2026,
        3,
        29,
        3,
        0,
        tzinfo=paris,
    )

    events = scheduler.events_at(scheduled_at)

    assert [event.moment.id for event in events] == [
        "m0",
        "m1",
        "m2",
    ]

    assert all(
        event.scheduled_at.isoformat() == "2026-03-29T03:00:00+02:00"
        for event in events
    )
