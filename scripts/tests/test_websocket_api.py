import asyncio

from unittest.mock import AsyncMock, MagicMock, patch

from datetime import time

from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.resolved_day_context import (
    ResolvedDayContext,
)
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.scheduled_moment import (
    ScheduledMoment,
)
from custom_components.day_planner.planner.errors import PlannerError
from custom_components.day_planner.websocket_api import (
    _get_runtime,
    async_setup_websocket_api,
    websocket_get_calendar,
    websocket_get_configuration,
    websocket_update_scheduled_moment,
    websocket_update_day_type,
    websocket_add_day_type,
    websocket_remove_day_type,
)


def create_hass_with_runtime(runtime):
    hass = MagicMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [
        entry
    ]

    return hass


def test_get_runtime():
    runtime = MagicMock()

    hass = create_hass_with_runtime(
        runtime
    )

    result = _get_runtime(
        hass
    )

    assert result is runtime


def test_get_runtime_not_configured():
    hass = MagicMock()

    hass.config_entries.async_entries.return_value = []

    result = _get_runtime(
        hass
    )

    assert result is None


def test_setup_websocket_api():
    hass = MagicMock()

    with patch(
        "custom_components.day_planner.websocket_api."
        "websocket_api.async_register_command"
    ) as register:
        async_setup_websocket_api(
            hass
        )

    assert register.call_count == 6

    register.assert_any_call(
        hass,
        websocket_get_configuration,
    )

    register.assert_any_call(
        hass,
        websocket_get_calendar,
    )


def test_websocket_get_configuration():
    runtime = MagicMock()

    configuration = {
        "moments": [],
        "day_types": [],
        "week_schedules": [],
        "cycles": [],
        "calendar_exceptions": [],
    }

    runtime.engine.configuration.to_dict.return_value = (
        configuration
    )

    hass = create_hass_with_runtime(
        runtime
    )

    connection = MagicMock()

    websocket_get_configuration(
        hass,
        connection,
        {
            "id": 1,
            "type": "day_planner/get_configuration",
        },
    )

    connection.send_result.assert_called_once_with(
        1,
        configuration,
    )

    connection.send_error.assert_not_called()


def test_websocket_get_configuration_not_configured():
    hass = MagicMock()

    hass.config_entries.async_entries.return_value = []

    connection = MagicMock()

    websocket_get_configuration(
        hass,
        connection,
        {
            "id": 2,
            "type": "day_planner/get_configuration",
        },
    )

    connection.send_error.assert_called_once()

    connection.send_result.assert_not_called()


def test_websocket_get_calendar():
    runtime = MagicMock()

    moment = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
    )

    day_type = DayType(
        id="work",
        name="Travail",
        scheduled_moments=(
            ScheduledMoment(
                moment_id="wake_up",
                time_definition=TimeDefinition(
                    fixed_time=time(7, 0),
                ),
            ),
        ),
    )

    runtime.resolver.resolve_moment.return_value = moment

    runtime.resolver.resolve_day_context.side_effect = (
        lambda target_date: ResolvedDayContext(
            date=target_date,
            day_type=day_type,
            cycle_id="cycle_1",
            week_schedule_id="week_1",
            calendar_exception_id=None,
        )
    )

    hass = create_hass_with_runtime(
        runtime
    )

    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 3,
            "type": "day_planner/get_calendar",
            "start_date": "2026-09-01",
            "end_date": "2026-09-02",
        },
    )

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once()

    result = (
        connection.send_result
        .call_args.args[1]
    )

    assert result["start_date"] == "2026-09-01"
    assert result["end_date"] == "2026-09-02"

    assert len(result["days"]) == 2

    assert result["days"][0] == {
        "date": "2026-09-01",
        "day_type": day_type.to_dict(),
        "cycle_id": "cycle_1",
        "week_schedule_id": "week_1",
        "calendar_exception_id": None,
        "scheduled_moments": [
            {
                "moment": {
                    "id": "wake_up",
                    "name": "Réveil",
                    "icon": "mdi:alarm",
                },
                "time_definition": {
                    "fixed_time": "07:00:00",
                },
            }
        ],
    }

    assert result["days"][1]["date"] == "2026-09-02"
    runtime.resolver.resolve_moment.assert_called_with(
        "wake_up"
    )

    assert (
        runtime.resolver.resolve_day_context.call_count
        == 2
    )
    runtime.resolver.resolve_moment.return_value = moment


def test_websocket_get_calendar_without_day_type():
    
    runtime = MagicMock()

    runtime.resolver.resolve_day_context.return_value = (
        ResolvedDayContext(
            date=None,
            day_type=None,
            cycle_id=None,
            week_schedule_id=None,
            calendar_exception_id=None,
        )
    )

    hass = create_hass_with_runtime(
        runtime
    )

    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 4,
            "type": "day_planner/get_calendar",
            "start_date": "2026-09-01",
            "end_date": "2026-09-01",
        },
    )

    result = (
        connection.send_result
        .call_args.args[1]
    )

    assert result["days"] == [
        {
            "date": "2026-09-01",
            "day_type": None,
            "cycle_id": None,
            "week_schedule_id": None,
            "calendar_exception_id": None,
            "scheduled_moments": [],
        }
    ]


def test_websocket_get_calendar_invalid_date():
    runtime = MagicMock()

    hass = create_hass_with_runtime(
        runtime
    )

    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 5,
            "type": "day_planner/get_calendar",
            "start_date": "invalid",
            "end_date": "2026-09-30",
        },
    )

    connection.send_error.assert_called_once()

    connection.send_result.assert_not_called()

    runtime.resolver.resolve_day_context.assert_not_called()


def test_websocket_get_calendar_end_before_start():
    runtime = MagicMock()

    hass = create_hass_with_runtime(
        runtime
    )

    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 6,
            "type": "day_planner/get_calendar",
            "start_date": "2026-09-30",
            "end_date": "2026-09-01",
        },
    )

    connection.send_error.assert_called_once()

    connection.send_result.assert_not_called()

    runtime.resolver.resolve_day_context.assert_not_called()


def test_websocket_get_calendar_not_configured():
    hass = MagicMock()

    hass.config_entries.async_entries.return_value = []

    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 7,
            "type": "day_planner/get_calendar",
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
        },
    )

    connection.send_error.assert_called_once()

    connection.send_result.assert_not_called()


async def run_websocket_handler(
    hass,
    handler,
    connection,
    msg,
):
    tasks = []

    def create_background_task(
        coro,
        name,
        *,
        eager_start=False,
    ):
        task = asyncio.create_task(coro)
        tasks.append(task)
        return task

    hass.async_create_background_task = MagicMock(
        side_effect=create_background_task
    )

    handler(
        hass,
        connection,
        msg,
    )

    await asyncio.gather(*tasks)

def test_websocket_update_scheduled_moment():
    runtime = MagicMock()

    configuration = MagicMock()
    runtime.engine.configuration = configuration

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler( 
            hass,
            websocket_update_scheduled_moment,
            connection,
            {
                "id": 10,
                "type": "day_planner/update_scheduled_moment",
                "day_type_id": "work",
                "moment_id": "wake_up",
                "time": "07:30",
            },
        )
    )
    scheduled = (
        runtime.engine.update_scheduled_moment
        .call_args.args[1]
    )

    assert scheduled.moment_id == "wake_up"
    assert scheduled.time_definition.fixed_time == time(7, 30)

    runtime.engine.update_scheduled_moment.assert_called_once_with(
        "work",
        scheduled,
    )

    runtime.storage.async_save.assert_awaited_once_with(
        configuration
    )

    runtime.resolver.update_configuration.assert_called_once_with(
        configuration
    )

    runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

    connection.send_result.assert_called_once_with(
        10,
        {
            "day_type_id": "work",
            "moment_id": "wake_up",
            "time": "07:30:00",
        },
    )


def test_websocket_update_scheduled_moment_invalid_time():
    runtime = MagicMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_scheduled_moment,
            connection,
            {
                "id": 11,
                "type": "day_planner/update_scheduled_moment",
                "day_type_id": "work",
                "moment_id": "wake_up",
                "time": "invalid",
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.engine.update_scheduled_moment.assert_not_called()


def test_websocket_update_scheduled_moment_planner_error():
    runtime = MagicMock()

    runtime.engine.update_scheduled_moment.side_effect = (
        PlannerError("Scheduled moment not found")
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_scheduled_moment,
            connection,
            {
                "id": 12,
                "type": "day_planner/update_scheduled_moment",
                "day_type_id": "work",
                "moment_id": "wake_up",
                "time": "07:30",
            },
        )
    )

    connection.send_error.assert_called_once()

    runtime.storage.async_save.assert_not_awaited()

def test_websocket_update_day_type():
    runtime = MagicMock()

    current = DayType(
        id="work",
        name="Journée travail",
        scheduled_moments=(),
    )

    runtime.engine.get_day_type.return_value = (
        current
    )

    configuration = MagicMock()
    runtime.engine.configuration = configuration

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = (
        AsyncMock()
    )

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_day_type,
            connection,
            {
                "id": 20,
                "type":
                    "day_planner/update_day_type",
                "day_type_id": "work",
                "name": "Journée bureau",
            },
        )
    )

    updated = (
        runtime.engine.update_day_type
        .call_args.args[0]
    )

    assert updated.id == "work"
    assert updated.name == "Journée bureau"

    # Très important :
    # les moments existants sont conservés.
    assert (
        updated.scheduled_moments
        == current.scheduled_moments
    )

    runtime.storage.async_save.assert_awaited_once_with(
        configuration
    )

    runtime.resolver.update_configuration.assert_called_once_with(
        configuration
    )

    runtime.ha_scheduler.async_schedule_next.assert_awaited_once()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        20,
        {
            "day_type_id": "work",
            "name": "Journée bureau",
        },
    )

def test_websocket_update_day_type_not_found():
    runtime = MagicMock()

    runtime.engine.get_day_type.side_effect = (
        PlannerError(
            "Day type not found: unknown"
        )
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = (
        AsyncMock()
    )

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_day_type,
            connection,
            {
                "id": 21,
                "type":
                    "day_planner/update_day_type",
                "day_type_id": "unknown",
                "name": "Nouveau nom",
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.engine.update_day_type.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()

    runtime.resolver.update_configuration.assert_not_called()

    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()


def test_websocket_add_day_type():
    runtime = MagicMock()

    configuration = MagicMock()
    runtime.engine.configuration = configuration

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_day_type,
            connection,
            {
                "id": 30,
                "type": "day_planner/add_day_type",
                "day_type_id": "home",
                "name": "Journée Maison",
            },
        )
    )

    created = (
        runtime.engine.add_day_type
        .call_args.args[0]
    )

    assert created.id == "home"
    assert created.name == "Journée Maison"
    assert created.scheduled_moments == ()

    runtime.storage.async_save.assert_awaited_once_with(
        configuration
    )

    runtime.resolver.update_configuration.assert_called_once_with(
        configuration
    )

    runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        30,
        {
            "id": "home",
            "name": "Journée Maison",
            "scheduled_moments": [],
        },
    )


def test_websocket_add_day_type_planner_error():
    runtime = MagicMock()

    runtime.engine.add_day_type.side_effect = (
        PlannerError(
            "Day type already exists: home"
        )
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_day_type,
            connection,
            {
                "id": 31,
                "type": "day_planner/add_day_type",
                "day_type_id": "home",
                "name": "Journée Maison",
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

def test_websocket_remove_day_type():
    runtime = MagicMock()

    configuration = MagicMock()
    runtime.engine.configuration = configuration

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_day_type,
            connection,
            {
                "id": 32,
                "type": "day_planner/remove_day_type",
                "day_type_id": "home",
            },
        )
    )

    runtime.engine.remove_day_type.assert_called_once_with(
        "home"
    )

    runtime.storage.async_save.assert_awaited_once_with(
        configuration
    )

    runtime.resolver.update_configuration.assert_called_once_with(
        configuration
    )

    runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        32,
        {
            "day_type_id": "home",
        },
    )


def test_websocket_remove_day_type_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_day_type.side_effect = (
        PlannerError(
            "Cannot remove a day type used by a week schedule"
        )
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_day_type,
            connection,
            {
                "id": 33,
                "type": "day_planner/remove_day_type",
                "day_type_id": "home",
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()


