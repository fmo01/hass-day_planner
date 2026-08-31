import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_event import ScheduledEvent
from custom_components.day_planner.ha_scheduler import HomeAssistantScheduler


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
