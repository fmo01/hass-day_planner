"""Home Assistant services for Day Planner."""

import logging
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, time
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    SERVICE_ADD_CALENDAR_EXCEPTION,
    SERVICE_ADD_CYCLE,
    SERVICE_ADD_DAY_TYPE,
    SERVICE_ADD_MOMENT,
    SERVICE_ADD_SCHEDULED_MOMENT,
    SERVICE_ADD_WEEK_SCHEDULE,
    SERVICE_REMOVE_CALENDAR_EXCEPTION,
    SERVICE_REMOVE_CYCLE,
    SERVICE_REMOVE_DAY_TYPE,
    SERVICE_REMOVE_MOMENT,
    SERVICE_REMOVE_SCHEDULED_MOMENT,
    SERVICE_REMOVE_WEEK_SCHEDULE,
    SERVICE_UPDATE_CALENDAR_EXCEPTION,
    SERVICE_UPDATE_CYCLE,
    SERVICE_UPDATE_DAY_TYPE,
    SERVICE_UPDATE_MOMENT,
    SERVICE_UPDATE_SCHEDULED_MOMENT,
    SERVICE_UPDATE_WEEK_SCHEDULE,
)
from .domain.action import Action
from .domain.calendar_exception import CalendarException
from .domain.cycle import Cycle
from .domain.day_type import DayType
from .domain.moment import Moment
from .domain.scheduled_moment import ScheduledMoment
from .domain.time_definition import TimeDefinition
from .domain.week_schedule import WeekSchedule
from .planner.errors import PlannerError
from .runtime import DayPlannerRuntimeData
from .schemas import (
    ADD_CALENDAR_EXCEPTION_SCHEMA,
    ADD_CYCLE_SCHEMA,
    ADD_DAY_TYPE_SCHEMA,
    ADD_MOMENT_SCHEMA,
    ADD_SCHEDULED_MOMENT_SCHEMA,
    ADD_WEEK_SCHEDULE_SCHEMA,
    REMOVE_CALENDAR_EXCEPTION_SCHEMA,
    REMOVE_CYCLE_SCHEMA,
    REMOVE_DAY_TYPE_SCHEMA,
    REMOVE_MOMENT_SCHEMA,
    REMOVE_SCHEDULED_MOMENT_SCHEMA,
    REMOVE_WEEK_SCHEDULE_SCHEMA,
    UPDATE_CALENDAR_EXCEPTION_SCHEMA,
    UPDATE_CYCLE_SCHEMA,
    UPDATE_DAY_TYPE_SCHEMA,
    UPDATE_MOMENT_SCHEMA,
    UPDATE_SCHEDULED_MOMENT_SCHEMA,
    UPDATE_WEEK_SCHEDULE_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


def _get_runtime(
    hass: HomeAssistant,
) -> DayPlannerRuntimeData:
    """Return the Day Planner runtime."""

    entry = next(
        iter(hass.config_entries.async_entries(DOMAIN)),
        None,
    )

    if entry is None:
        raise HomeAssistantError("Day Planner is not configured.")

    return entry.runtime_data


async def _async_get_actor_name(
    call: ServiceCall,
) -> str:
    """Return the Home Assistant user display name."""

    user_id = call.context.user_id

    if user_id is None:
        return "system"

    user = await call.hass.auth.async_get_user(user_id)

    if user is not None and user.name:
        return user.name

    return user_id


async def _execute(
    operation: Callable[[], Any],
    runtime: DayPlannerRuntimeData,
    description: str,
) -> None:
    """Execute an engine operation and persist the configuration."""

    try:
        operation()

        await runtime.async_configuration_updated()

    except PlannerError as err:
        _LOGGER.warning(
            "%s: %s",
            description,
            err,
        )
        raise HomeAssistantError(
            str(err),
        ) from err

    except Exception:
        _LOGGER.exception(description)
        raise


async def async_setup_services(
    hass: HomeAssistant,
) -> None:
    """Register Day Planner services."""

    async def add_moment(
        call: ServiceCall,
    ) -> None:
        """Add a moment."""

        runtime = _get_runtime(call.hass)

        modified_by = await _async_get_actor_name(call)

        moment = Moment(
            id=call.data["id"],
            name=call.data["name"],
            icon=call.data["icon"],
            actions=tuple(
                Action(
                    id=action["id"],
                    label=action.get(
                        "label",
                        action["id"],
                    ),
                    sequence=list(action["sequence"]),
                )
                for action in call.data.get("actions", [])
            ),
        )

        await _execute(
            lambda: runtime.engine.add_moment(
                moment,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to add moment '{moment.id}'",
        )

    async def update_moment(
        call: ServiceCall,
    ) -> None:
        """Update a moment."""

        runtime = _get_runtime(hass)

        modified_by = await _async_get_actor_name(call)

        current_moment = runtime.engine.get_moment(call.data["id"])

        if "actions" in call.data:
            actions = tuple(
                Action(
                    id=action["id"],
                    label=action.get(
                        "label",
                        action["id"],
                    ),
                    sequence=list(action["sequence"]),
                )
                for action in call.data["actions"]
            )
        else:
            actions = current_moment.actions

        moment = Moment(
            id=call.data["id"],
            name=call.data["name"],
            icon=call.data.get("icon"),
            actions=actions,
        )

        await _execute(
            lambda: runtime.engine.update_moment(
                moment,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to update moment '{moment.id}'",
        )

    async def remove_moment(
        call: ServiceCall,
    ) -> None:
        """Remove a moment."""

        runtime = _get_runtime(hass)

        await _execute(
            lambda: runtime.engine.remove_moment(call.data["id"]),
            runtime=runtime,
            description=(f"Unable to remove moment " f"'{call.data['id']}'"),
        )

    #
    # day type²
    #

    async def add_day_type(
        call: ServiceCall,
    ) -> None:
        """Add a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        day_type = DayType(
            id=call.data["id"],
            name=call.data["name"],
            scheduled_moments=(),
        )

        await _execute(
            operation=lambda: runtime.engine.add_day_type(
                day_type,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to add day type '{day_type.id}'",
        )

    async def update_day_type(
        call: ServiceCall,
    ) -> None:
        """Update a day type without losing scheduled moments."""

        runtime = _get_runtime(
            call.hass,
        )

        day_type_id = call.data["id"]
        modified_by = await _async_get_actor_name(call)

        def operation() -> None:
            current = runtime.engine.get_day_type(
                day_type_id,
            )

            updated_day_type = replace(
                current,
                name=call.data["name"],
            )

            runtime.engine.update_day_type(
                updated_day_type,
                modified_by=modified_by,
            )

        await _execute(
            operation=operation,
            runtime=runtime,
            description=f"Unable to update day type '{day_type_id}'",
        )

    async def remove_day_type(
        call: ServiceCall,
    ) -> None:
        """Remove a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        day_type_id = call.data["id"]

        await _execute(
            operation=lambda: runtime.engine.remove_day_type(
                day_type_id,
            ),
            runtime=runtime,
            description=f"Unable to remove day type '{day_type_id}'",
        )

    #
    # scheduled moment
    #

    async def add_scheduled_moment(
        call: ServiceCall,
    ) -> None:
        """Add a scheduled moment to a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        scheduled_moment = ScheduledMoment(
            moment_id=call.data["moment_id"],
            time_definition=TimeDefinition(
                fixed_time=time.fromisoformat(call.data["time"]),
            ),
        )

        await _execute(
            operation=lambda: runtime.engine.add_scheduled_moment(
                call.data["day_type_id"],
                scheduled_moment,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=(
                "Unable to add scheduled moment "
                f"'{call.data['moment_id']}' "
                f"to day type '{call.data['day_type_id']}'"
            ),
        )

    async def update_scheduled_moment(
        call: ServiceCall,
    ) -> None:
        """Update a scheduled moment in a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        scheduled_moment = ScheduledMoment(
            moment_id=call.data["moment_id"],
            time_definition=TimeDefinition(
                fixed_time=time.fromisoformat(call.data["time"]),
            ),
        )

        await _execute(
            operation=lambda: runtime.engine.update_scheduled_moment(
                call.data["day_type_id"],
                scheduled_moment,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=(
                "Unable to update scheduled moment "
                f"'{call.data['moment_id']}' "
                f"in day type '{call.data['day_type_id']}'"
            ),
        )

    async def remove_scheduled_moment(
        call: ServiceCall,
    ) -> None:
        """Remove a scheduled moment from a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        await _execute(
            operation=lambda: runtime.engine.remove_scheduled_moment(
                call.data["day_type_id"],
                call.data["moment_id"],
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=(
                "Unable to remove scheduled moment "
                f"'{call.data['moment_id']}' "
                f"from day type '{call.data['day_type_id']}'"
            ),
        )

    #
    # week_schedule
    #

    async def add_week_schedule(
        call: ServiceCall,
    ) -> None:
        """Add a week schedule."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        week_schedule = WeekSchedule(
            id=call.data["id"],
            name=call.data["name"],
            monday=call.data["monday"],
            tuesday=call.data["tuesday"],
            wednesday=call.data["wednesday"],
            thursday=call.data["thursday"],
            friday=call.data["friday"],
            saturday=call.data["saturday"],
            sunday=call.data["sunday"],
        )

        await _execute(
            operation=lambda: runtime.engine.add_week_schedule(
                week_schedule,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to add week schedule '{week_schedule.id}'",
        )

    async def update_week_schedule(
        call: ServiceCall,
    ) -> None:
        """Update a week schedule."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        week_schedule = WeekSchedule(
            id=call.data["id"],
            name=call.data["name"],
            monday=call.data["monday"],
            tuesday=call.data["tuesday"],
            wednesday=call.data["wednesday"],
            thursday=call.data["thursday"],
            friday=call.data["friday"],
            saturday=call.data["saturday"],
            sunday=call.data["sunday"],
        )

        await _execute(
            operation=lambda: runtime.engine.update_week_schedule(
                week_schedule,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to update week schedule '{week_schedule.id}'",
        )

    async def remove_week_schedule(
        call: ServiceCall,
    ) -> None:
        """Remove a week schedule."""

        runtime = _get_runtime(
            call.hass,
        )

        await _execute(
            operation=lambda: runtime.engine.remove_week_schedule(
                call.data["id"],
            ),
            runtime=runtime,
            description=(f"Unable to remove week schedule " f"'{call.data['id']}'"),
        )

    #
    # cycle
    #

    async def add_cycle(
        call: ServiceCall,
    ) -> None:
        """Add a cycle."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        cycle = Cycle(
            id=call.data["id"],
            name=call.data["name"],
            start_date=date.fromisoformat(call.data["start_date"]),
            week_schedule_ids=tuple(call.data["week_schedule_ids"]),
        )

        await _execute(
            operation=lambda: runtime.engine.add_cycle(
                cycle,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to add cycle '{cycle.id}'",
        )

    async def update_cycle(
        call: ServiceCall,
    ) -> None:
        """Update a cycle."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        cycle = Cycle(
            id=call.data["id"],
            name=call.data["name"],
            start_date=date.fromisoformat(call.data["start_date"]),
            week_schedule_ids=tuple(call.data["week_schedule_ids"]),
        )

        await _execute(
            operation=lambda: runtime.engine.update_cycle(
                cycle,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to update cycle '{cycle.id}'",
        )

    async def remove_cycle(
        call: ServiceCall,
    ) -> None:
        """Remove a cycle."""

        runtime = _get_runtime(
            call.hass,
        )

        cycle_id = call.data["id"]

        await _execute(
            operation=lambda: runtime.engine.remove_cycle(
                cycle_id,
            ),
            runtime=runtime,
            description=f"Unable to remove cycle '{cycle_id}'",
        )

    #
    # calendar exception
    #

    async def add_calendar_exception(
        call: ServiceCall,
    ) -> None:
        """Add a calendar_exception."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        calendar_exception = CalendarException(
            id=call.data["id"],
            date=date.fromisoformat(
                datetime.strptime(
                    call.data["date"],
                    "%d/%m/%Y",
                )
                .date()
                .isoformat()
            ),
            day_type_id=call.data["day_type_id"],
            description=call.data.get("description"),
        )

        await _execute(
            operation=lambda: runtime.engine.add_calendar_exception(
                calendar_exception,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to add calendar exception '{calendar_exception.id}'",
        )

    async def update_calendar_exception(
        call: ServiceCall,
    ) -> None:
        """Update a calendar_exception."""

        runtime = _get_runtime(
            call.hass,
        )

        modified_by = await _async_get_actor_name(call)

        calendar_exception = CalendarException(
            id=call.data["id"],
            date=date.fromisoformat(
                datetime.strptime(
                    call.data["date"],
                    "%d/%m/%Y",
                )
                .date()
                .isoformat()
            ),
            day_type_id=call.data["day_type_id"],
            description=call.data.get("description"),
        )

        await _execute(
            operation=lambda: runtime.engine.update_calendar_exception(
                calendar_exception,
                modified_by=modified_by,
            ),
            runtime=runtime,
            description=f"Unable to update calendar exception '{calendar_exception.id}'",
        )

    async def remove_calendar_exception(
        call: ServiceCall,
    ) -> None:
        """Remove a calendar_exception."""

        runtime = _get_runtime(
            call.hass,
        )

        calendar_exception_id = call.data["id"]

        await _execute(
            operation=lambda: runtime.engine.remove_calendar_exception(
                calendar_exception_id,
            ),
            runtime=runtime,
            description=f"Unable to remove calendar exception '{calendar_exception_id}'",
        )

    #
    # Enregistrement des services
    #

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_MOMENT,
        add_moment,
        schema=ADD_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_MOMENT,
        update_moment,
        schema=UPDATE_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_MOMENT,
        remove_moment,
        schema=REMOVE_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_DAY_TYPE,
        add_day_type,
        schema=ADD_DAY_TYPE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_DAY_TYPE,
        update_day_type,
        schema=UPDATE_DAY_TYPE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_DAY_TYPE,
        remove_day_type,
        schema=REMOVE_DAY_TYPE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SCHEDULED_MOMENT,
        add_scheduled_moment,
        schema=ADD_SCHEDULED_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_SCHEDULED_MOMENT,
        update_scheduled_moment,
        schema=UPDATE_SCHEDULED_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_SCHEDULED_MOMENT,
        remove_scheduled_moment,
        schema=REMOVE_SCHEDULED_MOMENT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_WEEK_SCHEDULE,
        add_week_schedule,
        schema=ADD_WEEK_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_WEEK_SCHEDULE,
        update_week_schedule,
        schema=UPDATE_WEEK_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_WEEK_SCHEDULE,
        remove_week_schedule,
        schema=REMOVE_WEEK_SCHEDULE_SCHEMA,
    )
    #
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_CYCLE,
        add_cycle,
        schema=ADD_CYCLE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_CYCLE,
        update_cycle,
        schema=UPDATE_CYCLE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_CYCLE,
        remove_cycle,
        schema=REMOVE_CYCLE_SCHEMA,
    )
    #
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_CALENDAR_EXCEPTION,
        add_calendar_exception,
        schema=ADD_CALENDAR_EXCEPTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_CALENDAR_EXCEPTION,
        update_calendar_exception,
        schema=UPDATE_CALENDAR_EXCEPTION_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_CALENDAR_EXCEPTION,
        remove_calendar_exception,
        schema=REMOVE_CALENDAR_EXCEPTION_SCHEMA,
    )
