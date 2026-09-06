import asyncio
from datetime import datetime, time, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_event import ScheduledEvent
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.ha_scheduler import HomeAssistantScheduler
from custom_components.day_planner.planner.scheduler import PlannerScheduler


def test_ha_scheduler_no_event():
    hass = MagicMock()

    scheduler = MagicMock()
    scheduler.next_event.return_value = None

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    with patch("custom_components.day_planner.ha_scheduler.dt_util.now") as now:
        now.return_value = MagicMock()

        asyncio.run(ha_scheduler.async_schedule_next())

    scheduler.next_event.assert_called_once_with(now.return_value)

    action_executor.async_execute_moment.assert_not_awaited()


def test_ha_scheduler_schedules_event():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    cancel = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    with (
        patch("custom_components.day_planner.ha_scheduler.dt_util.now") as now,
        patch(
            "custom_components.day_planner.ha_scheduler." "async_track_point_in_time",
            return_value=cancel,
        ) as track,
    ):
        current = datetime(
            2026,
            8,
            31,
            6,
            0,
        )
        now.return_value = current

        asyncio.run(ha_scheduler.async_schedule_next())

    scheduler.next_event.assert_called_once_with(current)

    track.assert_called_once()

    assert track.call_args.args[0] is hass
    assert callable(track.call_args.args[1])
    assert track.call_args.args[2] == event.scheduled_at

    assert ha_scheduler._cancel is cancel


def test_ha_scheduler_executes_event_and_reschedules():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    cancel = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    async def run():
        with (
            patch(
                "custom_components.day_planner.ha_scheduler." "dt_util.now",
                return_value=datetime(
                    2026,
                    8,
                    31,
                    6,
                    0,
                ),
            ),
            patch(
                "custom_components.day_planner.ha_scheduler."
                "async_track_point_in_time",
                return_value=cancel,
            ) as track,
        ):
            await ha_scheduler.async_schedule_next()

            callback = track.call_args.args[1]

            # On isole ici la reprogrammation :
            # son comportement propre sera testé séparément.
            ha_scheduler.async_schedule_next = AsyncMock()

            await callback(
                datetime(
                    2026,
                    8,
                    31,
                    7,
                    30,
                )
            )

    asyncio.run(run())

    action_executor.async_execute_moment.assert_awaited_once_with(moment)

    ha_scheduler.async_schedule_next.assert_awaited_once_with()

    assert ha_scheduler._cancel is None


def test_ha_scheduler_cancel():
    hass = MagicMock()
    scheduler = MagicMock()
    action_executor = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    cancel = MagicMock()
    ha_scheduler._cancel = cancel

    ha_scheduler.cancel()

    cancel.assert_called_once_with()

    assert ha_scheduler._cancel is None

    # Un deuxième cancel doit être sans effet.
    ha_scheduler.cancel()

    cancel.assert_called_once_with()


def test_ha_scheduler_reschedule_cancels_previous():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    old_cancel = MagicMock()
    new_cancel = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    ha_scheduler._cancel = old_cancel

    async def run():
        with (
            patch(
                "custom_components.day_planner.ha_scheduler." "dt_util.now",
                return_value=datetime(
                    2026,
                    8,
                    31,
                    6,
                    0,
                ),
            ),
            patch(
                "custom_components.day_planner.ha_scheduler."
                "async_track_point_in_time",
                return_value=new_cancel,
            ),
        ):
            await ha_scheduler.async_schedule_next()

    asyncio.run(run())

    old_cancel.assert_called_once_with()

    assert ha_scheduler._cancel is new_cancel


def test_ha_scheduler_converts_naive_event_to_timezone():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    cancel = MagicMock()

    ha_scheduler = HomeAssistantScheduler(
        hass=hass,
        scheduler=scheduler,
        action_executor=action_executor,
    )

    local_tz = timezone(timedelta(hours=2))

    now = datetime(
        2026,
        8,
        31,
        6,
        0,
        tzinfo=local_tz,
    )

    with (
        patch(
            "custom_components.day_planner.ha_scheduler.dt_util.now",
            return_value=now,
        ),
        patch(
            "custom_components.day_planner.ha_scheduler." "async_track_point_in_time",
            return_value=cancel,
        ) as track,
    ):
        asyncio.run(ha_scheduler.async_schedule_next())

    scheduled_at = track.call_args.args[2]

    assert scheduled_at == datetime(
        2026,
        8,
        31,
        7,
        30,
        tzinfo=local_tz,
    )


def test_ha_scheduler_reschedules_after_action_error():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock(
        side_effect=RuntimeError("Action failed")
    )

    cancel = MagicMock()

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
                    6,
                    0,
                ),
            ),
            patch(
                "custom_components.day_planner.ha_scheduler."
                "async_track_point_in_time",
                return_value=cancel,
            ) as track,
        ):
            await ha_scheduler.async_schedule_next()

            callback = track.call_args.args[1]

            ha_scheduler.async_schedule_next = AsyncMock()

            try:
                await callback(
                    datetime(
                        2026,
                        8,
                        31,
                        7,
                        30,
                    )
                )
            except RuntimeError as err:
                assert str(err) == "Action failed"
            else:
                raise AssertionError("RuntimeError was not propagated")

    asyncio.run(run())

    action_executor.async_execute_moment.assert_awaited_once_with(moment)

    ha_scheduler.async_schedule_next.assert_awaited_once_with()

    assert ha_scheduler._cancel is None


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


def test_ha_scheduler_cancels_when_no_next_event():
    hass = MagicMock()

    moment = Moment(
        id="departure",
        name="Départ",
    )

    event = ScheduledEvent(
        scheduled_at=datetime(
            2026,
            8,
            31,
            8,
            0,
        ),
        moment=moment,
    )

    scheduler = MagicMock()
    scheduler.next_event.side_effect = [
        event,
        None,
    ]

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    old_cancel = MagicMock()

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
                return_value=old_cancel,
            ) as track,
        ):
            # Premier calcul : un événement existe à 08:00.
            await ha_scheduler.async_schedule_next()

            assert ha_scheduler._cancel is old_cancel
            assert track.call_count == 1

            # Nouveau calcul après modification :
            # plus aucun événement à programmer.
            await ha_scheduler.async_schedule_next()

            old_cancel.assert_called_once_with()

            assert ha_scheduler._cancel is None

            # Aucun nouveau callback ne doit être créé.
            assert track.call_count == 1

    asyncio.run(run())

    assert scheduler.next_event.call_count == 2


def test_ha_scheduler_does_not_execute_same_callback_twice():
    hass = MagicMock()

    moment = Moment(
        id="m1",
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

    scheduler = MagicMock()
    scheduler.next_event.return_value = event

    action_executor = MagicMock()
    action_executor.async_execute_moment = AsyncMock()

    cancel = MagicMock()

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
                    6,
                    0,
                ),
            ),
            patch(
                "custom_components.day_planner.ha_scheduler."
                "async_track_point_in_time",
                return_value=cancel,
            ) as track,
        ):
            await ha_scheduler.async_schedule_next()

            callback = track.call_args.args[1]

            # On neutralise la reprogrammation pour isoler
            # uniquement le comportement du callback.
            ha_scheduler.async_schedule_next = AsyncMock()

            callback_time = datetime(
                2026,
                8,
                31,
                7,
                30,
            )

            await callback(callback_time)
            await callback(callback_time)

    asyncio.run(run())

    action_executor.async_execute_moment.assert_awaited_once_with(moment)
