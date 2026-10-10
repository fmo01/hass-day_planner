"""WebSocket API for Day Planner."""

import logging
from datetime import date, time, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .domain.action import Action
from .domain.calendar_exception import CalendarException
from .domain.cycle import Cycle
from .domain.day_type import DayType
from .domain.moment import Moment
from .domain.scheduled_moment import ScheduledMoment
from .domain.time_definition import TimeDefinition
from .domain.week_schedule import WeekSchedule
from .planner.errors import PlannerError

_LOGGER = logging.getLogger(__name__)


def _get_runtime(hass: HomeAssistant):
    """Return Day Planner runtime data."""

    entry = next(
        iter(hass.config_entries.async_entries(DOMAIN)),
        None,
    )

    if entry is None:
        return None

    return entry.runtime_data


@callback
def async_setup_websocket_api(
    hass: HomeAssistant,
) -> None:
    """Register Day Planner WebSocket commands."""

    websocket_api.async_register_command(
        hass,
        websocket_get_configuration,
    )

    websocket_api.async_register_command(
        hass,
        websocket_get_calendar,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_scheduled_moment,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_day_type,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_day_type,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_day_type,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_scheduled_moment,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_scheduled_moment,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_week_schedule,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_week_schedule,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_week_schedule,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_cycle,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_cycle,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_cycle,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_calendar_exception,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_calendar_exception,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_calendar_exception,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_moment_action,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_moment_action,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_moment_action,
    )

    websocket_api.async_register_command(
        hass,
        websocket_add_moment,
    )

    websocket_api.async_register_command(
        hass,
        websocket_update_moment,
    )

    websocket_api.async_register_command(
        hass,
        websocket_remove_moment,
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/get_configuration",
    }
)
def websocket_get_configuration(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return complete Day Planner configuration."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    configuration = runtime.engine.configuration

    connection.send_result(
        msg["id"],
        configuration.to_dict(),
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/update_scheduled_moment",
        vol.Required("day_type_id"): str,
        vol.Required("moment_id"): str,
        vol.Required("time"): str,
    }
)
@websocket_api.async_response
async def websocket_update_scheduled_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a scheduled moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        fixed_time = time.fromisoformat(msg["time"])
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid time format",
        )
        return

    scheduled_moment = ScheduledMoment(
        moment_id=msg["moment_id"],
        time_definition=TimeDefinition(
            fixed_time=fixed_time,
        ),
    )

    try:
        runtime.engine.update_scheduled_moment(
            msg["day_type_id"],
            scheduled_moment,
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:

        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "day_type_id": msg["day_type_id"],
            "moment_id": msg["moment_id"],
            "time": fixed_time.isoformat(),
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/get_calendar",
        vol.Required("start_date"): str,
        vol.Required("end_date"): str,
    }
)
def websocket_get_calendar(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return resolved Day Planner calendar."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        start_date = date.fromisoformat(msg["start_date"])

        end_date = date.fromisoformat(msg["end_date"])
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid date format",
        )
        return

    if end_date < start_date:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "end_date must be greater than or equal to start_date",
        )
        return

    days = []

    target_date = start_date

    while target_date <= end_date:
        context = runtime.resolver.resolve_day_context(target_date)
        base_context = runtime.resolver.resolve_base_day_context(
            target_date
        )

        day_type = context.day_type

        scheduled_moments = []

        if day_type is not None:
            for scheduled in day_type.scheduled_moments:
                moment = runtime.resolver.resolve_moment(scheduled.moment_id)

                scheduled_moments.append(
                    {
                        "moment": {
                            "id": moment.id,
                            "name": moment.name,
                            "icon": moment.icon,
                        },
                        "time_definition": (scheduled.time_definition.to_dict()),
                    }
                )

        days.append(
            {
                "date": target_date.isoformat(),
                "day_type": (day_type.to_dict() if day_type is not None else None),
                "base_day_type": (
                    base_context.day_type.to_dict()
                    if base_context.day_type is not None
                    else None
                ),
                "cycle_id": context.cycle_id,
                "week_schedule_id": (context.week_schedule_id),
                "calendar_exception_id": (context.calendar_exception_id),
                "scheduled_moments": scheduled_moments,
            }
        )

        target_date += timedelta(days=1)

    connection.send_result(
        msg["id"],
        {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/update_day_type",
        vol.Required("day_type_id"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def websocket_update_day_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a day type."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        current = runtime.engine.get_day_type(msg["day_type_id"])

        updated = DayType(
            id=current.id,
            name=msg["name"],
            scheduled_moments=(current.scheduled_moments),
        )

        runtime.engine.update_day_type(updated)

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "day_type_id": updated.id,
            "name": updated.name,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/add_day_type",
        vol.Required("day_type_id"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def websocket_add_day_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a day type."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    day_type = DayType(
        id=msg["day_type_id"],
        name=msg["name"],
        scheduled_moments=(),
    )

    try:
        runtime.engine.add_day_type(day_type)

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        day_type.to_dict(),
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/remove_day_type",
        vol.Required("day_type_id"): str,
    }
)
@websocket_api.async_response
async def websocket_remove_day_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a day type."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_day_type(msg["day_type_id"])

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "day_type_id": msg["day_type_id"],
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/add_scheduled_moment",
        vol.Required(
            "day_type_id"
        ): str,
        vol.Required(
            "moment_id"
        ): str,
        vol.Required(
            "time"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_add_scheduled_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a scheduled moment to a day type."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        fixed_time = time.fromisoformat(
            msg["time"]
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid time format",
        )
        return

    scheduled_moment = ScheduledMoment(
        moment_id=msg["moment_id"],
        time_definition=TimeDefinition(
            fixed_time=fixed_time,
        ),
    )

    try:
        runtime.engine.add_scheduled_moment(
            msg["day_type_id"],
            scheduled_moment,
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "day_type_id": msg["day_type_id"],
            "moment_id": msg["moment_id"],
            "time": fixed_time.isoformat(),
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/remove_scheduled_moment",
        vol.Required(
            "day_type_id"
        ): str,
        vol.Required(
            "moment_id"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_remove_scheduled_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a scheduled moment from a day type."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_scheduled_moment(
            msg["day_type_id"],
            msg["moment_id"],
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "day_type_id": msg["day_type_id"],
            "moment_id": msg["moment_id"],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/add_week_schedule",
        vol.Required("week_schedule_id"): str,
        vol.Required("name"): str,
        vol.Required("monday"): str,
        vol.Required("tuesday"): str,
        vol.Required("wednesday"): str,
        vol.Required("thursday"): str,
        vol.Required("friday"): str,
        vol.Required("saturday"): str,
        vol.Required("sunday"): str,
    }
)
@websocket_api.async_response
async def websocket_add_week_schedule(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a week schedule."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    week_schedule = WeekSchedule(
        id=msg["week_schedule_id"],
        name=msg["name"],
        monday=msg["monday"],
        tuesday=msg["tuesday"],
        wednesday=msg["wednesday"],
        thursday=msg["thursday"],
        friday=msg["friday"],
        saturday=msg["saturday"],
        sunday=msg["sunday"],
    )

    try:
        runtime.engine.add_week_schedule(
            week_schedule
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "id": week_schedule.id,
            "name": week_schedule.name,
            "monday": week_schedule.monday,
            "tuesday": week_schedule.tuesday,
            "wednesday": week_schedule.wednesday,
            "thursday": week_schedule.thursday,
            "friday": week_schedule.friday,
            "saturday": week_schedule.saturday,
            "sunday": week_schedule.sunday,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/update_week_schedule",
        vol.Required("week_schedule_id"): str,
        vol.Required("name"): str,
        vol.Required("monday"): str,
        vol.Required("tuesday"): str,
        vol.Required("wednesday"): str,
        vol.Required("thursday"): str,
        vol.Required("friday"): str,
        vol.Required("saturday"): str,
        vol.Required("sunday"): str,
    }
)
@websocket_api.async_response
async def websocket_update_week_schedule(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a week schedule."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    week_schedule = WeekSchedule(
        id=msg["week_schedule_id"],
        name=msg["name"],
        monday=msg["monday"],
        tuesday=msg["tuesday"],
        wednesday=msg["wednesday"],
        thursday=msg["thursday"],
        friday=msg["friday"],
        saturday=msg["saturday"],
        sunday=msg["sunday"],
    )

    try:
        runtime.engine.update_week_schedule(
            week_schedule
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "id": week_schedule.id,
            "name": week_schedule.name,
            "monday": week_schedule.monday,
            "tuesday": week_schedule.tuesday,
            "wednesday": week_schedule.wednesday,
            "thursday": week_schedule.thursday,
            "friday": week_schedule.friday,
            "saturday": week_schedule.saturday,
            "sunday": week_schedule.sunday,
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/remove_week_schedule",
        vol.Required("week_schedule_id"): str,
    }
)
@websocket_api.async_response
async def websocket_remove_week_schedule(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a week schedule."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_week_schedule(
            msg["week_schedule_id"]
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "week_schedule_id":
                msg["week_schedule_id"],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/add_cycle",
        vol.Required(
            "cycle_id"
        ): str,
        vol.Required(
            "name"
        ): str,
        vol.Required(
            "start_date"
        ): str,
        vol.Required(
            "week_schedule_ids"
        ): [str],
    }
)
@websocket_api.async_response
async def websocket_add_cycle(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a cycle."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        start_date = date.fromisoformat(
            msg["start_date"]
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid start date format",
        )
        return

    week_schedule_ids = tuple(
        msg["week_schedule_ids"]
    )

    if not 1 <= len(week_schedule_ids) <= 4:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "A cycle must contain between 1 and 4 week schedules",
        )
        return

    cycle = Cycle(
        id=msg["cycle_id"],
        name=msg["name"],
        start_date=start_date,
        week_schedule_ids=week_schedule_ids,
    )

    try:
        runtime.engine.add_cycle(
            cycle
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        cycle.to_dict(),
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/update_cycle",
        vol.Required(
            "cycle_id"
        ): str,
        vol.Required(
            "name"
        ): str,
        vol.Required(
            "start_date"
        ): str,
        vol.Required(
            "week_schedule_ids"
        ): [str],
    }
)
@websocket_api.async_response
async def websocket_update_cycle(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a cycle."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        start_date = date.fromisoformat(
            msg["start_date"]
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid start date format",
        )
        return

    week_schedule_ids = tuple(
        msg["week_schedule_ids"]
    )

    if not 1 <= len(week_schedule_ids) <= 4:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "A cycle must contain between 1 and 4 week schedules",
        )
        return

    cycle = Cycle(
        id=msg["cycle_id"],
        name=msg["name"],
        start_date=start_date,
        week_schedule_ids=week_schedule_ids,
    )

    try:
        runtime.engine.update_cycle(
            cycle
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        cycle.to_dict(),
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/remove_cycle",
        vol.Required(
            "cycle_id"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_remove_cycle(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a cycle."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_cycle(
            msg["cycle_id"]
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "cycle_id": msg["cycle_id"],
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/add_calendar_exception",
        vol.Required(
            "calendar_exception_id"
        ): str,
        vol.Required(
            "date"
        ): str,
        vol.Required(
            "day_type_id"
        ): str,
        vol.Optional(
            "description"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_add_calendar_exception(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a calendar exception."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        exception_date = date.fromisoformat(
            msg["date"]
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid date format",
        )
        return

    calendar_exception = CalendarException(
        id=msg["calendar_exception_id"],
        date=exception_date,
        day_type_id=msg["day_type_id"],
        description=msg.get(
            "description"
        ),
    )

    try:
        runtime.engine.add_calendar_exception(
            calendar_exception
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        calendar_exception.to_dict(),
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/update_calendar_exception",
        vol.Required(
            "calendar_exception_id"
        ): str,
        vol.Required(
            "date"
        ): str,
        vol.Required(
            "day_type_id"
        ): str,
        vol.Optional(
            "description"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_update_calendar_exception(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a calendar exception."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        exception_date = date.fromisoformat(
            msg["date"]
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "Invalid date format",
        )
        return

    calendar_exception = CalendarException(
        id=msg["calendar_exception_id"],
        date=exception_date,
        day_type_id=msg["day_type_id"],
        description=msg.get(
            "description"
        ),
    )

    try:
        runtime.engine.update_calendar_exception(
            calendar_exception
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        calendar_exception.to_dict(),
    )

@websocket_api.websocket_command(
    {
        vol.Required(
            "type"
        ): "day_planner/remove_calendar_exception",
        vol.Required(
            "calendar_exception_id"
        ): str,
    }
)
@websocket_api.async_response
async def websocket_remove_calendar_exception(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a calendar exception."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_calendar_exception(
            msg["calendar_exception_id"]
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "calendar_exception_id":
                msg["calendar_exception_id"],
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/add_moment_action",
        vol.Required("moment_id"): str,
        vol.Required("action_id"): str,
        vol.Optional("label"): str,
        vol.Required("sequence"): list,
    }
)
@websocket_api.async_response
async def websocket_add_moment_action(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add an action to a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        moment = runtime.engine.get_moment(
            msg["moment_id"]
        )

        if any(
            action.id == msg["action_id"]
            for action in moment.actions
        ):
            connection.send_error(
                msg["id"],
                websocket_api.ERR_INVALID_FORMAT,
                f"Action already exists: {msg['action_id']}",
            )
            return

        action = Action(
            id=msg["action_id"],
            label=msg.get( "label", msg["action_id"],),
            sequence=list(msg["sequence"]),
        )

        updated_moment = Moment(
            id=moment.id,
            name=moment.name,
            icon=moment.icon,
            actions=(
                *moment.actions,
                action,
            ),
        )

        runtime.engine.update_moment(
            updated_moment
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "moment_id": msg["moment_id"],
            "action_id": msg["action_id"],
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/update_moment_action",
        vol.Required("moment_id"): str,
        vol.Required("action_id"): str,
        vol.Optional("label"): str,
        vol.Required("sequence"): list,
    }
)
@websocket_api.async_response
async def websocket_update_moment_action(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update an action of a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        moment = runtime.engine.get_moment(
            msg["moment_id"]
        )

        if not any(
            action.id == msg["action_id"]
            for action in moment.actions
        ):
            connection.send_error(
                msg["id"],
                websocket_api.ERR_NOT_FOUND,
                f"Action not found: {msg['action_id']}",
            )
            return

        current_action = next(
            action
            for action in moment.actions
            if action.id == msg["action_id"]
        )

        updated_action = Action(
            id=msg["action_id"],
            label=msg.get( "label", msg["action_id"],),
            sequence=list(msg["sequence"]),
        )

        actions = tuple(
            updated_action
            if action.id == msg["action_id"]
            else action
            for action in moment.actions
        )

        updated_moment = Moment(
            id=moment.id,
            name=moment.name,
            icon=moment.icon,
            actions=actions,
        )

        runtime.engine.update_moment(
            updated_moment
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "moment_id": msg["moment_id"],
            "action_id": msg["action_id"],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/remove_moment_action",
        vol.Required("moment_id"): str,
        vol.Required("action_id"): str,
    }
)
@websocket_api.async_response
async def websocket_remove_moment_action(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove an action from a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        moment = runtime.engine.get_moment(
            msg["moment_id"]
        )

        if not any(
            action.id == msg["action_id"]
            for action in moment.actions
        ):
            connection.send_error(
                msg["id"],
                websocket_api.ERR_NOT_FOUND,
                f"Action not found: {msg['action_id']}",
            )
            return

        actions = tuple(
            action
            for action in moment.actions
            if action.id != msg["action_id"]
        )

        updated_moment = Moment(
            id=moment.id,
            name=moment.name,
            icon=moment.icon,
            actions=actions,
        )

        runtime.engine.update_moment(
            updated_moment
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "moment_id": msg["moment_id"],
            "action_id": msg["action_id"],
        },
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/add_moment",
        vol.Required("moment_id"): str,
        vol.Required("name"): str,
        vol.Optional("icon", default=None): vol.Any(str, None),
    }
)
@websocket_api.async_response
async def websocket_add_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        moment = Moment(
            id=msg["moment_id"],
            name=msg["name"],
            icon=msg["icon"],
            actions=(),
        )

        runtime.engine.add_moment(
            moment
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        moment.to_dict(),
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/update_moment",
        vol.Required("moment_id"): str,
        vol.Required("name"): str,
        vol.Optional("icon", default=None): vol.Any(str, None),
    }
)
@websocket_api.async_response
async def websocket_update_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        current = runtime.engine.get_moment(
            msg["moment_id"]
        )

        updated_moment = Moment(
            id=current.id,
            name=msg["name"],
            icon=msg["icon"],
            actions=current.actions,
        )

        runtime.engine.update_moment(
            updated_moment
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "id": updated_moment.id,
            "name": updated_moment.name,
            "icon": updated_moment.icon,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "day_planner/remove_moment",
        vol.Required("moment_id"): str,
    }
)
@websocket_api.async_response
async def websocket_remove_moment(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a moment."""

    runtime = _get_runtime(hass)

    if runtime is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Day Planner is not configured",
        )
        return

    try:
        runtime.engine.remove_moment(
            msg["moment_id"]
        )

        await runtime.async_configuration_updated()

    except PlannerError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            str(err),
        )
        return

    connection.send_result(
        msg["id"],
        {
            "moment_id": msg["moment_id"],
        },
    )


