import asyncio
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components import websocket_api

from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.resolved_day_context import \
    ResolvedDayContext
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.planner.errors import PlannerError
from custom_components.day_planner.websocket_api import (
    _get_runtime, async_setup_websocket_api, websocket_add_calendar_exception,
    websocket_add_cycle, websocket_add_day_type, websocket_add_moment,
    websocket_add_moment_action, websocket_add_scheduled_moment,
    websocket_add_week_schedule, websocket_get_calendar,
    websocket_get_configuration, websocket_remove_calendar_exception,
    websocket_remove_cycle, websocket_remove_day_type, websocket_remove_moment,
    websocket_remove_moment_action, websocket_remove_scheduled_moment,
    websocket_remove_week_schedule, websocket_update_calendar_exception,
    websocket_update_cycle, websocket_update_day_type, websocket_update_moment,
    websocket_update_moment_action, websocket_update_scheduled_moment,
    websocket_update_week_schedule)


def create_hass_with_runtime(runtime):
    hass = MagicMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    return hass


def test_get_runtime():
    runtime = MagicMock()

    hass = create_hass_with_runtime(runtime)

    result = _get_runtime(hass)

    assert result is runtime


def test_get_runtime_not_configured():
    hass = MagicMock()

    hass.config_entries.async_entries.return_value = []

    result = _get_runtime(hass)

    assert result is None


def test_setup_websocket_api():
    hass = MagicMock()

    with patch(
        "custom_components.day_planner.websocket_api."
        "websocket_api.async_register_command"
    ) as register:
        async_setup_websocket_api(hass)

    registered_commands = {call.args[1] for call in register.call_args_list}

    assert registered_commands == {
        websocket_get_configuration,
        websocket_get_calendar,
        websocket_update_scheduled_moment,
        websocket_update_day_type,
        websocket_add_day_type,
        websocket_remove_day_type,
        websocket_add_scheduled_moment,
        websocket_remove_scheduled_moment,
        websocket_add_week_schedule,
        websocket_update_week_schedule,
        websocket_remove_week_schedule,
        websocket_add_cycle,
        websocket_update_cycle,
        websocket_remove_cycle,
        websocket_add_calendar_exception,
        websocket_update_calendar_exception,
        websocket_remove_calendar_exception,
        websocket_add_moment,
        websocket_update_moment,
        websocket_remove_moment,
        websocket_add_moment_action,
        websocket_update_moment_action,
        websocket_remove_moment_action,
    }


def test_websocket_get_configuration():
    runtime = MagicMock()

    configuration = {
        "moments": [],
        "day_types": [],
        "week_schedules": [],
        "cycles": [],
        "calendar_exceptions": [],
    }

    runtime.engine.configuration.to_dict.return_value = configuration

    hass = create_hass_with_runtime(runtime)

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

    runtime.resolver.resolve_base_day_context.side_effect = (
        lambda target_date: ResolvedDayContext(
            date=target_date,
            day_type=day_type,
            cycle_id="cycle_1",
            week_schedule_id="week_1",
            calendar_exception_id=None,
        )
    )

    hass = create_hass_with_runtime(runtime)

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

    result = connection.send_result.call_args.args[1]

    assert result["start_date"] == "2026-09-01"
    assert result["end_date"] == "2026-09-02"

    assert len(result["days"]) == 2

    assert result["days"][0] == {
        "date": "2026-09-01",
        "day_type": day_type.to_dict(),
        "base_day_type": day_type.to_dict(),
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
    runtime.resolver.resolve_moment.assert_called_with("wake_up")

    assert runtime.resolver.resolve_day_context.call_count == 2

    assert runtime.resolver.resolve_base_day_context.call_count == 2

    runtime.resolver.resolve_moment.return_value = moment


def test_websocket_get_calendar_without_day_type():
    runtime = MagicMock()

    runtime.resolver.resolve_day_context.return_value = ResolvedDayContext(
        date=None,
        day_type=None,
        cycle_id=None,
        week_schedule_id=None,
        calendar_exception_id=None,
    )

    runtime.resolver.resolve_base_day_context.return_value = ResolvedDayContext(
        date=None,
        day_type=None,
        cycle_id=None,
        week_schedule_id=None,
        calendar_exception_id=None,
    )

    hass = create_hass_with_runtime(runtime)

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

    result = connection.send_result.call_args.args[1]

    assert result["days"] == [
        {
            "date": "2026-09-01",
            "day_type": None,
            "base_day_type": None,
            "cycle_id": None,
            "week_schedule_id": None,
            "calendar_exception_id": None,
            "scheduled_moments": [],
        }
    ]


def test_websocket_get_calendar_invalid_date():
    runtime = MagicMock()

    hass = create_hass_with_runtime(runtime)

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

    hass = create_hass_with_runtime(runtime)

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

    hass.async_create_background_task = MagicMock(side_effect=create_background_task)

    handler(
        hass,
        connection,
        msg,
    )

    await asyncio.gather(*tasks)


def test_websocket_update_scheduled_moment():
    runtime = MagicMock()

    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user = SimpleNamespace(
        id="test_user_123",
        name="Utilisateur Test",
    )

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
    scheduled = runtime.engine.update_scheduled_moment.call_args.args[1]

    assert scheduled.moment_id == "wake_up"
    assert scheduled.time_definition.fixed_time == time(7, 30)

    runtime.engine.update_scheduled_moment.assert_called_once_with(
        "work",
        scheduled,
        modified_by="Utilisateur Test",
    )

    runtime.async_configuration_updated.assert_awaited_once_with()

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

    runtime.engine.update_scheduled_moment.side_effect = PlannerError(
        "Scheduled moment not found"
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

    runtime.engine.get_day_type.return_value = current

    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "test_user_123"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_day_type,
            connection,
            {
                "id": 20,
                "type": "day_planner/update_day_type",
                "day_type_id": "work",
                "name": "Journée bureau",
            },
        )
    )

    updated = runtime.engine.update_day_type.call_args.args[0]

    assert updated.id == "work"
    assert updated.name == "Journée bureau"

    # Très important :
    # les moments existants sont conservés.
    assert updated.scheduled_moments == current.scheduled_moments

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        20,
        {
            "day_type_id": "work",
            "name": "Journée bureau",
        },
    )

    assert runtime.engine.update_day_type.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }


def test_websocket_update_day_type_not_found():
    runtime = MagicMock()

    runtime.engine.get_day_type.side_effect = PlannerError(
        "Day type not found: unknown"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_day_type,
            connection,
            {
                "id": 21,
                "type": "day_planner/update_day_type",
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

    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "test_user_123"
    connection.user.name = "Utilisateur Test"

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

    created = runtime.engine.add_day_type.call_args.args[0]
    assert runtime.engine.add_day_type.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }
    assert created.id == "home"
    assert created.name == "Journée Maison"
    assert created.scheduled_moments == ()

    runtime.async_configuration_updated.assert_awaited_once_with()

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

    runtime.engine.add_day_type.side_effect = PlannerError(
        "Day type already exists: home"
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

    runtime.async_configuration_updated = AsyncMock()

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

    runtime.engine.remove_day_type.assert_called_once_with("home")

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        32,
        {
            "day_type_id": "home",
        },
    )


def test_websocket_remove_day_type_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_day_type.side_effect = PlannerError(
        "Cannot remove a day type used by a week schedule"
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


def test_websocket_add_scheduled_moment():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "test_user_123"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_scheduled_moment,
            connection,
            {
                "id": 40,
                "type": "day_planner/add_scheduled_moment",
                "day_type_id": "travail",
                "moment_id": "reveil",
                "time": "07:30:00",
            },
        )
    )

    runtime.engine.add_scheduled_moment.assert_called_once()

    day_type_id, scheduled_moment = runtime.engine.add_scheduled_moment.call_args.args

    assert day_type_id == "travail"
    assert scheduled_moment.moment_id == "reveil"
    assert scheduled_moment.time_definition.fixed_time == time(7, 30)
    assert runtime.engine.add_scheduled_moment.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        40,
        {
            "day_type_id": "travail",
            "moment_id": "reveil",
            "time": "07:30:00",
        },
    )


def test_websocket_add_scheduled_moment_invalid_time():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_scheduled_moment,
            connection,
            {
                "id": 41,
                "type": "day_planner/add_scheduled_moment",
                "day_type_id": "travail",
                "moment_id": "reveil",
                "time": "25:99",
            },
        )
    )

    runtime.engine.add_scheduled_moment.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        41,
        websocket_api.ERR_INVALID_FORMAT,
        "Invalid time format",
    )


def test_websocket_add_scheduled_moment_planner_error():
    runtime = MagicMock()

    runtime.engine.add_scheduled_moment.side_effect = PlannerError(
        "Scheduled moment already exists"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_scheduled_moment,
            connection,
            {
                "id": 42,
                "type": "day_planner/add_scheduled_moment",
                "day_type_id": "travail",
                "moment_id": "reveil",
                "time": "07:30:00",
            },
        )
    )

    runtime.engine.add_scheduled_moment.assert_called_once()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        42,
        websocket_api.ERR_INVALID_FORMAT,
        "Scheduled moment already exists",
    )


def test_websocket_remove_scheduled_moment():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "test_user_123"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_scheduled_moment,
            connection,
            {
                "id": 43,
                "type": "day_planner/remove_scheduled_moment",
                "day_type_id": "travail",
                "moment_id": "reveil",
            },
        )
    )

    runtime.engine.remove_scheduled_moment.assert_called_once_with(
        "travail",
        "reveil",
        modified_by="Utilisateur Test",
    )

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        43,
        {
            "day_type_id": "travail",
            "moment_id": "reveil",
        },
    )


def test_websocket_remove_scheduled_moment_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_scheduled_moment.side_effect = PlannerError(
        "Scheduled moment not found"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    connection.user.id = "test_user_123"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_scheduled_moment,
            connection,
            {
                "id": 44,
                "type": "day_planner/remove_scheduled_moment",
                "day_type_id": "travail",
                "moment_id": "reveil",
            },
        )
    )

    runtime.engine.remove_scheduled_moment.assert_called_once_with(
        "travail",
        "reveil",
        modified_by="Utilisateur Test",
    )

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        44,
        websocket_api.ERR_INVALID_FORMAT,
        "Scheduled moment not found",
    )


def test_websocket_add_week_schedule():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_001"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_week_schedule,
            connection,
            {
                "id": 50,
                "type": "day_planner/add_week_schedule",
                "week_schedule_id": "normal",
                "name": "Semaine normale",
                "monday": "travail",
                "tuesday": "travail",
                "wednesday": "travail",
                "thursday": "travail",
                "friday": "travail",
                "saturday": "maison",
                "sunday": "maison",
            },
        )
    )

    runtime.engine.add_week_schedule.assert_called_once()
    assert runtime.engine.add_week_schedule.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }

    week_schedule = runtime.engine.add_week_schedule.call_args.args[0]

    assert week_schedule.id == "normal"
    assert week_schedule.name == "Semaine normale"
    assert week_schedule.monday == "travail"
    assert week_schedule.tuesday == "travail"
    assert week_schedule.wednesday == "travail"
    assert week_schedule.thursday == "travail"
    assert week_schedule.friday == "travail"
    assert week_schedule.saturday == "maison"
    assert week_schedule.sunday == "maison"

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        50,
        {
            "id": "normal",
            "name": "Semaine normale",
            "monday": "travail",
            "tuesday": "travail",
            "wednesday": "travail",
            "thursday": "travail",
            "friday": "travail",
            "saturday": "maison",
            "sunday": "maison",
        },
    )


def test_websocket_add_week_schedule_planner_error():
    runtime = MagicMock()

    runtime.engine.add_week_schedule.side_effect = PlannerError(
        "Day type not found: travail"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_week_schedule,
            connection,
            {
                "id": 51,
                "type": "day_planner/add_week_schedule",
                "week_schedule_id": "normal",
                "name": "Semaine normale",
                "monday": "travail",
                "tuesday": "travail",
                "wednesday": "travail",
                "thursday": "travail",
                "friday": "travail",
                "saturday": "maison",
                "sunday": "maison",
            },
        )
    )

    runtime.engine.add_week_schedule.assert_called_once()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        51,
        websocket_api.ERR_INVALID_FORMAT,
        "Day type not found: travail",
    )


def test_websocket_update_week_schedule():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_002"
    connection.user.name = None

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_week_schedule,
            connection,
            {
                "id": 52,
                "type": "day_planner/update_week_schedule",
                "week_schedule_id": "normal",
                "name": "Semaine modifiée",
                "monday": "travail",
                "tuesday": "travail",
                "wednesday": "maison",
                "thursday": "travail",
                "friday": "travail",
                "saturday": "maison",
                "sunday": "maison",
            },
        )
    )

    runtime.engine.update_week_schedule.assert_called_once()
    assert runtime.engine.update_week_schedule.call_args.kwargs == {
        "modified_by": "user_002",
    }

    week_schedule = runtime.engine.update_week_schedule.call_args.args[0]

    assert week_schedule.id == "normal"
    assert week_schedule.name == "Semaine modifiée"
    assert week_schedule.wednesday == "maison"
    assert week_schedule.sunday == "maison"

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        52,
        {
            "id": "normal",
            "name": "Semaine modifiée",
            "monday": "travail",
            "tuesday": "travail",
            "wednesday": "maison",
            "thursday": "travail",
            "friday": "travail",
            "saturday": "maison",
            "sunday": "maison",
        },
    )


def test_websocket_update_week_schedule_planner_error():
    runtime = MagicMock()

    runtime.engine.update_week_schedule.side_effect = PlannerError(
        "Week schedule not found: normal"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_week_schedule,
            connection,
            {
                "id": 53,
                "type": "day_planner/update_week_schedule",
                "week_schedule_id": "normal",
                "name": "Semaine modifiée",
                "monday": "travail",
                "tuesday": "travail",
                "wednesday": "travail",
                "thursday": "travail",
                "friday": "travail",
                "saturday": "maison",
                "sunday": "maison",
            },
        )
    )

    runtime.engine.update_week_schedule.assert_called_once()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        53,
        websocket_api.ERR_INVALID_FORMAT,
        "Week schedule not found: normal",
    )


def test_websocket_remove_week_schedule():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_week_schedule,
            connection,
            {
                "id": 54,
                "type": "day_planner/remove_week_schedule",
                "week_schedule_id": "normal",
            },
        )
    )

    runtime.engine.remove_week_schedule.assert_called_once_with("normal")

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        54,
        {
            "week_schedule_id": "normal",
        },
    )


def test_websocket_remove_week_schedule_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_week_schedule.side_effect = PlannerError(
        "Cannot remove a week schedule used by a cycle"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_week_schedule,
            connection,
            {
                "id": 55,
                "type": "day_planner/remove_week_schedule",
                "week_schedule_id": "normal",
            },
        )
    )

    runtime.engine.remove_week_schedule.assert_called_once_with("normal")

    runtime.storage.async_save.assert_not_awaited()

    runtime.resolver.update_configuration.assert_not_called()

    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        55,
        websocket_api.ERR_INVALID_FORMAT,
        "Cannot remove a week schedule used by a cycle",
    )


def test_websocket_add_cycle():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_001"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_cycle,
            connection,
            {
                "id": 60,
                "type": "day_planner/add_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle principal",
                "start_date": "2026-09-01",
                "week_schedule_ids": [
                    "semaine1",
                    "semaine2",
                ],
            },
        )
    )

    runtime.engine.add_cycle.assert_called_once()
    assert runtime.engine.add_cycle.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }

    cycle = runtime.engine.add_cycle.call_args.args[0]

    assert cycle.id == "cycle1"
    assert cycle.name == "Cycle principal"
    assert cycle.start_date == date(2026, 9, 1)

    assert cycle.week_schedule_ids == (
        "semaine1",
        "semaine2",
    )

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        60,
        {
            "id": "cycle1",
            "name": "Cycle principal",
            "start_date": "2026-09-01",
            "week_schedule_ids": [
                "semaine1",
                "semaine2",
            ],
        },
    )


def test_websocket_add_cycle_invalid_date():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_cycle,
            connection,
            {
                "id": 61,
                "type": "day_planner/add_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle principal",
                "start_date": "2026-99-99",
                "week_schedule_ids": [
                    "semaine1",
                ],
            },
        )
    )

    runtime.engine.add_cycle.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        61,
        websocket_api.ERR_INVALID_FORMAT,
        "Invalid start date format",
    )


def test_websocket_add_cycle_invalid_week_count():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_cycle,
            connection,
            {
                "id": 62,
                "type": "day_planner/add_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle principal",
                "start_date": "2026-09-01",
                "week_schedule_ids": [],
            },
        )
    )

    runtime.engine.add_cycle.assert_not_called()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        62,
        websocket_api.ERR_INVALID_FORMAT,
        "A cycle must contain between 1 and 4 week schedules",
    )


def test_websocket_update_cycle():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_002"
    connection.user.name = None

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_cycle,
            connection,
            {
                "id": 63,
                "type": "day_planner/update_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle été",
                "start_date": "2026-09-15",
                "week_schedule_ids": [
                    "semaine2",
                    "semaine1",
                ],
            },
        )
    )

    runtime.engine.update_cycle.assert_called_once()
    assert runtime.engine.update_cycle.call_args.kwargs == {
        "modified_by": "user_002",
    }

    cycle = runtime.engine.update_cycle.call_args.args[0]

    assert cycle.id == "cycle1"
    assert cycle.name == "Cycle été"
    assert cycle.start_date == date(2026, 9, 15)

    assert cycle.week_schedule_ids == (
        "semaine2",
        "semaine1",
    )

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        63,
        {
            "id": "cycle1",
            "name": "Cycle été",
            "start_date": "2026-09-15",
            "week_schedule_ids": [
                "semaine2",
                "semaine1",
            ],
        },
    )


def test_websocket_update_cycle_invalid_date():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_cycle,
            connection,
            {
                "id": 64,
                "type": "day_planner/update_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle été",
                "start_date": "2026-13-40",
                "week_schedule_ids": [
                    "semaine1",
                ],
            },
        )
    )

    runtime.engine.update_cycle.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        64,
        websocket_api.ERR_INVALID_FORMAT,
        "Invalid start date format",
    )


def test_websocket_update_cycle_invalid_week_count():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_cycle,
            connection,
            {
                "id": 65,
                "type": "day_planner/update_cycle",
                "cycle_id": "cycle1",
                "name": "Cycle été",
                "start_date": "2026-09-15",
                "week_schedule_ids": [
                    "s1",
                    "s2",
                    "s3",
                    "s4",
                    "s5",
                ],
            },
        )
    )

    runtime.engine.update_cycle.assert_not_called()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        65,
        websocket_api.ERR_INVALID_FORMAT,
        "A cycle must contain between 1 and 4 week schedules",
    )


def test_websocket_remove_cycle():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_cycle,
            connection,
            {
                "id": 66,
                "type": "day_planner/remove_cycle",
                "cycle_id": "cycle1",
            },
        )
    )

    runtime.engine.remove_cycle.assert_called_once_with("cycle1")

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        66,
        {
            "cycle_id": "cycle1",
        },
    )


def test_websocket_remove_cycle_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_cycle.side_effect = PlannerError("Cycle not found: cycle1")

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_cycle,
            connection,
            {
                "id": 67,
                "type": "day_planner/remove_cycle",
                "cycle_id": "cycle1",
            },
        )
    )

    runtime.engine.remove_cycle.assert_called_once_with("cycle1")

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        67,
        websocket_api.ERR_INVALID_FORMAT,
        "Cycle not found: cycle1",
    )


def test_websocket_add_cycle_duplicate_start_date():
    runtime = MagicMock()

    runtime.engine.add_cycle.side_effect = PlannerError(
        "Duplicate cycle start date: 2026-09-07"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_cycle,
            connection,
            {
                "id": 68,
                "type": "day_planner/add_cycle",
                "cycle_id": "cycle2",
                "name": "Cycle 2",
                "start_date": "2026-09-07",
                "week_schedule_ids": [
                    "semaine1",
                ],
            },
        )
    )

    runtime.engine.add_cycle.assert_called_once()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        68,
        websocket_api.ERR_INVALID_FORMAT,
        "Duplicate cycle start date: 2026-09-07",
    )


def test_websocket_add_calendar_exception():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_001"
    connection.user.name = "Utilisateur Test"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_calendar_exception,
            connection,
            {
                "id": 70,
                "type": "day_planner/add_calendar_exception",
                "calendar_exception_id": "exception1",
                "date": "2026-09-14",
                "day_type_id": "repos",
                "description": "Jour exceptionnel",
            },
        )
    )

    runtime.engine.add_calendar_exception.assert_called_once()

    assert runtime.engine.add_calendar_exception.call_args.kwargs == {
        "modified_by": "Utilisateur Test",
    }

    calendar_exception = runtime.engine.add_calendar_exception.call_args.args[0]

    assert calendar_exception.id == "exception1"
    assert calendar_exception.date == date(2026, 9, 14)
    assert calendar_exception.day_type_id == "repos"
    assert calendar_exception.description == "Jour exceptionnel"

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        70,
        {
            "id": "exception1",
            "date": "2026-09-14",
            "day_type_id": "repos",
            "description": "Jour exceptionnel",
        },
    )


def test_websocket_add_calendar_exception_invalid_date():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_calendar_exception,
            connection,
            {
                "id": 71,
                "type": "day_planner/add_calendar_exception",
                "calendar_exception_id": "exception1",
                "date": "2026-99-99",
                "day_type_id": "repos",
            },
        )
    )

    runtime.engine.add_calendar_exception.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        71,
        websocket_api.ERR_INVALID_FORMAT,
        "Invalid date format",
    )


def test_websocket_update_calendar_exception():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_002"
    connection.user.name = None

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_calendar_exception,
            connection,
            {
                "id": 72,
                "type": "day_planner/update_calendar_exception",
                "calendar_exception_id": "exception1",
                "date": "2026-09-15",
                "day_type_id": "travail",
                "description": "Exception modifiée",
            },
        )
    )

    runtime.engine.update_calendar_exception.assert_called_once()
    assert runtime.engine.update_calendar_exception.call_args.kwargs == {
        "modified_by": "user_002",
    }

    calendar_exception = runtime.engine.update_calendar_exception.call_args.args[0]

    assert calendar_exception.id == "exception1"
    assert calendar_exception.date == date(2026, 9, 15)
    assert calendar_exception.day_type_id == "travail"
    assert calendar_exception.description == "Exception modifiée"

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()


def test_websocket_update_calendar_exception_invalid_date():
    runtime = MagicMock()

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_calendar_exception,
            connection,
            {
                "id": 73,
                "type": "day_planner/update_calendar_exception",
                "calendar_exception_id": "exception1",
                "date": "2026-99-99",
                "day_type_id": "travail",
            },
        )
    )

    runtime.engine.update_calendar_exception.assert_not_called()

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        73,
        websocket_api.ERR_INVALID_FORMAT,
        "Invalid date format",
    )


def test_websocket_remove_calendar_exception():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_calendar_exception,
            connection,
            {
                "id": 74,
                "type": "day_planner/remove_calendar_exception",
                "calendar_exception_id": "exception1",
            },
        )
    )

    runtime.engine.remove_calendar_exception.assert_called_once_with("exception1")

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        74,
        {
            "calendar_exception_id": "exception1",
        },
    )


def test_websocket_remove_calendar_exception_planner_error():
    runtime = MagicMock()

    runtime.engine.remove_calendar_exception.side_effect = PlannerError(
        "Calendar exception not found: exception1"
    )

    runtime.storage.async_save = AsyncMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_calendar_exception,
            connection,
            {
                "id": 75,
                "type": "day_planner/remove_calendar_exception",
                "calendar_exception_id": "exception1",
            },
        )
    )

    runtime.engine.remove_calendar_exception.assert_called_once_with("exception1")

    runtime.storage.async_save.assert_not_awaited()
    runtime.resolver.update_configuration.assert_not_called()
    runtime.ha_scheduler.async_schedule_next.assert_not_awaited()

    connection.send_result.assert_not_called()

    connection.send_error.assert_called_once_with(
        75,
        websocket_api.ERR_INVALID_FORMAT,
        "Calendar exception not found: exception1",
    )


def test_websocket_get_calendar_with_exception_base_day_type():
    runtime = MagicMock()

    base_day_type = DayType(
        id="work",
        name="Travail",
        scheduled_moments=(),
    )

    exception_day_type = DayType(
        id="rest",
        name="Repos",
        scheduled_moments=(),
    )

    runtime.resolver.resolve_day_context.return_value = ResolvedDayContext(
        date=date(2026, 9, 14),
        day_type=exception_day_type,
        cycle_id="cycle_1",
        week_schedule_id="week_1",
        calendar_exception_id="exception-2026-09-14",
    )

    runtime.resolver.resolve_base_day_context.return_value = ResolvedDayContext(
        date=date(2026, 9, 14),
        day_type=base_day_type,
        cycle_id="cycle_1",
        week_schedule_id="week_1",
        calendar_exception_id=None,
    )

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    websocket_get_calendar(
        hass,
        connection,
        {
            "id": 8,
            "type": "day_planner/get_calendar",
            "start_date": "2026-09-14",
            "end_date": "2026-09-14",
        },
    )

    connection.send_error.assert_not_called()

    result = connection.send_result.call_args.args[1]

    assert result["days"][0] == {
        "date": "2026-09-14",
        "day_type": exception_day_type.to_dict(),
        "base_day_type": base_day_type.to_dict(),
        "cycle_id": "cycle_1",
        "week_schedule_id": "week_1",
        "calendar_exception_id": ("exception-2026-09-14"),
        "scheduled_moments": [],
    }


def test_websocket_add_moment_action():
    runtime = MagicMock()

    existing_action = Action(
        id="existing",
        sequence=[
            {
                "action": "light.turn_off",
                "label": "Allumer le salon",
                "target": {
                    "entity_id": "light.cuisine",
                },
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(existing_action,),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.name = "Utilisateur C"
    connection.user.id = "user_003"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_moment_action,
            connection,
            {
                "id": 100,
                "type": "day_planner/add_moment_action",
                "moment_id": "wake_up",
                "action_id": "salon_on",
                "label": "Allumer le salon",
                "sequence": [
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            },
        )
    )

    runtime.engine.get_moment.assert_called_once_with("wake_up")

    updated = runtime.engine.update_moment.call_args.args[0]

    assert (
        runtime.engine.update_moment.call_args.kwargs["modified_by"] == "Utilisateur C"
    )

    assert updated.id == "wake_up"
    assert updated.name == "Réveil"
    assert updated.icon == "mdi:alarm"

    assert len(updated.actions) == 2

    assert updated.actions[0] is existing_action

    assert updated.actions[1].id == "salon_on"
    assert updated.actions[1].label == "Allumer le salon"
    assert updated.actions[1].sequence == [
        {
            "action": "light.turn_on",
            "target": {
                "entity_id": "light.salon",
            },
        }
    ]

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        100,
        {
            "moment_id": "wake_up",
            "action_id": "salon_on",
        },
    )


def test_websocket_update_moment_action():
    runtime = MagicMock()

    action_1 = Action(
        id="salon_on",
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ],
    )

    action_2 = Action(
        id="other",
        sequence=[
            {
                "action": "light.turn_off",
                "target": {
                    "entity_id": "light.cuisine",
                },
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(
            action_1,
            action_2,
        ),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.name = None
    connection.user.id = "user_123"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_moment_action,
            connection,
            {
                "id": 101,
                "type": "day_planner/update_moment_action",
                "moment_id": "wake_up",
                "action_id": "salon_on",
                "label": "Éteindre le salon",
                "sequence": [
                    {
                        "action": "light.turn_off",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            },
        )
    )

    runtime.engine.get_moment.assert_called_once_with("wake_up")

    updated = runtime.engine.update_moment.call_args.args[0]

    assert runtime.engine.update_moment.call_args.kwargs["modified_by"] == "user_123"

    assert updated.id == current.id
    assert updated.name == current.name
    assert updated.icon == current.icon

    assert len(updated.actions) == 2

    assert updated.actions[0].id == "salon_on"
    assert updated.actions[0].label == "Éteindre le salon"
    assert updated.actions[0].sequence == [
        {
            "action": "light.turn_off",
            "target": {
                "entity_id": "light.salon",
            },
        }
    ]

    # L'autre action doit être conservée.
    assert updated.actions[1] is action_2

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        101,
        {
            "moment_id": "wake_up",
            "action_id": "salon_on",
        },
    )


def test_websocket_remove_moment_action():
    runtime = MagicMock()

    action_to_remove = Action(
        id="salon_on",
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ],
    )

    action_to_keep = Action(
        id="other",
        sequence=[
            {
                "action": "light.turn_off",
                "target": {
                    "entity_id": "light.cuisine",
                },
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(
            action_to_remove,
            action_to_keep,
        ),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.name = "Utilisateur D"
    connection.user.id = "user_005"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_moment_action,
            connection,
            {
                "id": 102,
                "type": "day_planner/remove_moment_action",
                "moment_id": "wake_up",
                "action_id": "salon_on",
            },
        )
    )

    runtime.engine.get_moment.assert_called_once_with("wake_up")

    updated = runtime.engine.update_moment.call_args.args[0]

    assert (
        runtime.engine.update_moment.call_args.kwargs["modified_by"] == "Utilisateur D"
    )

    assert updated.id == current.id
    assert updated.name == current.name
    assert updated.icon == current.icon

    assert updated.actions == (action_to_keep,)

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        102,
        {
            "moment_id": "wake_up",
            "action_id": "salon_on",
        },
    )


def test_websocket_update_moment_action_not_found():
    runtime = MagicMock()

    existing_action = Action(
        id="existing",
        sequence=[
            {
                "action": "light.turn_on",
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(existing_action,),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_moment_action,
            connection,
            {
                "id": 103,
                "type": "day_planner/update_moment_action",
                "moment_id": "wake_up",
                "action_id": "unknown",
                "sequence": [
                    {
                        "action": "light.turn_off",
                    }
                ],
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.engine.update_moment.assert_not_called()
    runtime.async_configuration_updated.assert_not_awaited()


def test_websocket_remove_moment_action_not_found():
    runtime = MagicMock()

    existing_action = Action(
        id="existing",
        sequence=[
            {
                "action": "light.turn_on",
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(existing_action,),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_moment_action,
            connection,
            {
                "id": 104,
                "type": "day_planner/remove_moment_action",
                "moment_id": "wake_up",
                "action_id": "unknown",
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.engine.update_moment.assert_not_called()
    runtime.async_configuration_updated.assert_not_awaited()


def test_websocket_add_moment_action_duplicate_id():
    runtime = MagicMock()

    existing_action = Action(
        id="salon_on",
        label="Allumer le salon",
        sequence=[
            {
                "action": "light.turn_on",
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(existing_action,),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_moment_action,
            connection,
            {
                "id": 105,
                "type": "day_planner/add_moment_action",
                "moment_id": "wake_up",
                "action_id": "salon_on",
                "label": "Éteindre le salon",
                "sequence": [
                    {
                        "action": "light.turn_off",
                    }
                ],
            },
        )
    )

    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

    runtime.engine.update_moment.assert_not_called()
    runtime.async_configuration_updated.assert_not_awaited()


def test_websocket_add_moment():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.name = "Utilisateur A"
    connection.user.id = "user_001"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_add_moment,
            connection,
            {
                "id": 200,
                "type": "day_planner/add_moment",
                "moment_id": "wake_up",
                "name": "Réveil",
                "icon": "mdi:alarm",
            },
        )
    )

    created = runtime.engine.add_moment.call_args.args[0]

    assert runtime.engine.add_moment.call_args.kwargs["modified_by"] == "Utilisateur A"
    assert created.id == "wake_up"
    assert created.name == "Réveil"
    assert created.icon == "mdi:alarm"
    assert created.actions == ()

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        200,
        {
            "id": "wake_up",
            "name": "Réveil",
            "icon": "mdi:alarm",
            "actions": [],
        },
    )


def test_websocket_update_moment():
    runtime = MagicMock()

    existing_action = Action(
        id="ouvrir_volets",
        label="Ouvrir les volets",
        sequence=[
            {
                "action": "cover.open_cover",
            }
        ],
    )

    current = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(existing_action,),
    )

    runtime.engine.get_moment.return_value = current
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()
    connection.user.id = "user_002"
    connection.user.name = "Utilisateur B"

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_update_moment,
            connection,
            {
                "id": 201,
                "type": "day_planner/update_moment",
                "moment_id": "wake_up",
                "name": "Réveil semaine",
                "icon": "mdi:alarm-note",
            },
        )
    )

    runtime.engine.get_moment.assert_called_once_with("wake_up")

    assert (
        runtime.engine.update_moment.call_args.kwargs["modified_by"] == "Utilisateur B"
    )

    updated = runtime.engine.update_moment.call_args.args[0]

    assert updated.id == "wake_up"
    assert updated.name == "Réveil semaine"
    assert updated.icon == "mdi:alarm-note"

    # Les actions doivent être conservées.
    assert updated.actions == current.actions

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        201,
        {
            "id": "wake_up",
            "name": "Réveil semaine",
            "icon": "mdi:alarm-note",
        },
    )


def test_websocket_remove_moment():
    runtime = MagicMock()
    runtime.async_configuration_updated = AsyncMock()

    hass = create_hass_with_runtime(runtime)
    connection = MagicMock()

    asyncio.run(
        run_websocket_handler(
            hass,
            websocket_remove_moment,
            connection,
            {
                "id": 202,
                "type": "day_planner/remove_moment",
                "moment_id": "wake_up",
            },
        )
    )

    runtime.engine.remove_moment.assert_called_once_with("wake_up")

    runtime.async_configuration_updated.assert_awaited_once_with()

    connection.send_error.assert_not_called()

    connection.send_result.assert_called_once_with(
        202,
        {
            "moment_id": "wake_up",
        },
    )


MUTATIONS_WITHOUT_RUNTIME = [
    "update_scheduled_moment",
    "update_day_type",
    "add_day_type",
    "remove_day_type",
    "add_scheduled_moment",
    "remove_scheduled_moment",
    "add_week_schedule",
    "update_week_schedule",
    "remove_week_schedule",
    "add_cycle",
    "update_cycle",
    "remove_cycle",
    "add_calendar_exception",
    "update_calendar_exception",
    "remove_calendar_exception",
    "add_moment_action",
    "update_moment_action",
    "remove_moment_action",
    "add_moment",
    "update_moment",
    "remove_moment",
]


@pytest.mark.parametrize("command", MUTATIONS_WITHOUT_RUNTIME)
def test_websocket_mutation_not_configured(command):
    async def run():
        hass = MagicMock()
        hass.config_entries.async_entries.return_value = []
        connection = MagicMock()
        await run_websocket_handler(
            hass,
            globals()[f"websocket_{command}"],
            connection,
            {"id": 1, "type": f"day_planner/{command}"},
        )
        connection.send_error.assert_called_once_with(
            1,
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        connection.send_result.assert_not_called()

    asyncio.run(run())


@pytest.mark.parametrize(
    "command",
    [
        "update_cycle",
        "add_calendar_exception",
        "update_calendar_exception",
        "add_moment_action",
        "update_moment_action",
        "remove_moment_action",
        "add_moment",
        "update_moment",
        "remove_moment",
    ],
)
def test_websocket_mutation_configuration_update_error(command):
    async def run():
        runtime = MagicMock()
        runtime.async_configuration_updated = AsyncMock(
            side_effect=PlannerError("Save failed")
        )
        actions = (
            ()
            if command == "add_moment_action"
            else (
                Action(id="a1", label="Action", sequence=[{"action": "light.turn_on"}]),
            )
        )
        runtime.engine.get_moment.return_value = Moment(
            id="m1",
            name="Moment",
            icon=None,
            actions=actions,
        )
        hass = MagicMock()
        entry = MagicMock()
        entry.runtime_data = runtime
        hass.config_entries.async_entries.return_value = [entry]
        connection = MagicMock()
        msg = {
            "id": 2,
            "type": f"day_planner/{command}",
            "moment_id": "m1",
            "action_id": "a1",
            "cycle_id": "c1",
            "calendar_exception_id": "ce1",
            "day_type_id": "dt1",
            "name": "Name",
            "icon": None,
            "start_date": "2026-10-12",
            "week_schedule_ids": ["ws1"],
            "date": "2026-10-12",
            "description": "Exception",
            "sequence": [{"action": "light.turn_on"}],
            "label": "Action",
        }
        await run_websocket_handler(
            hass, globals()[f"websocket_{command}"], connection, msg
        )
        runtime.async_configuration_updated.assert_awaited_once_with()
        connection.send_error.assert_called_once_with(
            2,
            websocket_api.ERR_INVALID_FORMAT,
            "Save failed",
        )
        connection.send_result.assert_not_called()

    asyncio.run(run())
