"""WebSocket API for Day Planner."""

import logging
from datetime import date, time, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .domain.day_type import DayType
from .domain.scheduled_moment import ScheduledMoment
from .domain.time_definition import TimeDefinition
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
    _LOGGER.warning(
        "WS update start: day_type=%s moment=%s time=%s",
        msg["day_type_id"],
        msg["moment_id"],
        msg["time"],
    )

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
        _LOGGER.warning("WS update: engine")
        runtime.engine.update_scheduled_moment(
            msg["day_type_id"],
            scheduled_moment,
        )

        configuration = runtime.engine.configuration

        _LOGGER.warning("WS update: storage")

        await runtime.storage.async_save(configuration)

        _LOGGER.warning("WS update: resolver")

        runtime.resolver.update_configuration(configuration)

        _LOGGER.warning("WS update: scheduler")

        await runtime.ha_scheduler.async_schedule_next()

    except PlannerError as err:
        _LOGGER.warning(
            "WS update planner error: %s",
            err,
        )

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
    _LOGGER.warning("WS update: done")


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

        configuration = runtime.engine.configuration

        await runtime.storage.async_save(configuration)

        runtime.resolver.update_configuration(configuration)

        await runtime.ha_scheduler.async_schedule_next()

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

        configuration = runtime.engine.configuration

        await runtime.storage.async_save(configuration)

        runtime.resolver.update_configuration(configuration)

        await runtime.ha_scheduler.async_schedule_next()

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

        configuration = runtime.engine.configuration

        await runtime.storage.async_save(configuration)

        runtime.resolver.update_configuration(configuration)

        await runtime.ha_scheduler.async_schedule_next()

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
