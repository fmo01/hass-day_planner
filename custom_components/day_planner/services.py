"""Home Assistant services for Day Planner."""

from typing import Any
from datetime import (
      date,
      datetime,
)

from collections.abc import Callable

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import logging

from .const import (
    DOMAIN,
    SERVICE_ADD_MOMENT,
    SERVICE_UPDATE_MOMENT,
    SERVICE_REMOVE_MOMENT,
    SERVICE_ADD_DAY_TYPE,
    SERVICE_UPDATE_DAY_TYPE,
    SERVICE_REMOVE_DAY_TYPE,
    SERVICE_ADD_WEEK_SCHEDULE,
    SERVICE_UPDATE_WEEK_SCHEDULE,
    SERVICE_REMOVE_WEEK_SCHEDULE,
    SERVICE_ADD_CYCLE,
    SERVICE_UPDATE_CYCLE,
    SERVICE_REMOVE_CYCLE,
    SERVICE_ADD_CALENDAR_EXCEPTION,
    SERVICE_UPDATE_CALENDAR_EXCEPTION,
    SERVICE_REMOVE_CALENDAR_EXCEPTION,
)
from .domain.moment import Moment
from .domain.day_type import DayType
from .domain.week_schedule import WeekSchedule
from .domain.cycle import Cycle
from .domain.calendar_exception import CalendarException
from .planner.errors import PlannerError
from .runtime import DayPlannerRuntimeData
from .schemas import (
    ADD_MOMENT_SCHEMA,
    UPDATE_MOMENT_SCHEMA,
    REMOVE_MOMENT_SCHEMA,
    ADD_DAY_TYPE_SCHEMA,
    UPDATE_DAY_TYPE_SCHEMA,
    REMOVE_DAY_TYPE_SCHEMA,
    ADD_WEEK_SCHEDULE_SCHEMA,
    UPDATE_WEEK_SCHEDULE_SCHEMA,
    REMOVE_WEEK_SCHEDULE_SCHEMA,
    ADD_CYCLE_SCHEMA,
    UPDATE_CYCLE_SCHEMA,
    REMOVE_CYCLE_SCHEMA,
    ADD_CALENDAR_EXCEPTION_SCHEMA,
    UPDATE_CALENDAR_EXCEPTION_SCHEMA,
    REMOVE_CALENDAR_EXCEPTION_SCHEMA,
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
        raise HomeAssistantError(
            "Day Planner is not configured."
        )

    return entry.runtime_data


async def _execute(
    operation: Callable[[], Any],
    runtime: DayPlannerRuntimeData,
    description: str,
) -> None:
    """Execute an engine operation and persist the configuration."""

    try:
        operation()

        await runtime.storage.async_save(
            runtime.engine.configuration,
        )

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

        moment = Moment(
            id=call.data["id"],
            name=call.data["name"],
            icon=call.data["icon"],
        )

        await _execute(
            lambda: runtime.engine.add_moment(moment),
            runtime=runtime,
            description=f"Unable to add moment '{moment.id}'",
        )

    async def update_moment(
        call: ServiceCall,
    ) -> None:
        """Update a moment."""

        runtime = _get_runtime(hass)

        moment = Moment(
            id=call.data["id"],
            name=call.data["name"],
            icon=call.data.get("icon"),
        )

        await _execute(
            lambda: runtime.engine.update_moment(
                moment
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
            lambda: runtime.engine.remove_moment(
                call.data["id"]
            ),
            runtime=runtime,
            description=(
                f"Unable to remove moment "
                f"'{call.data['id']}'"
            ),
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

        day_type = DayType(
            id=call.data["id"],
            name=call.data["name"],
            scheduled_moments=(),
        )

        await _execute(
            operation=lambda: runtime.engine.add_day_type(
                day_type,
            ),
            runtime=runtime,
            description=f"Unable to add day type '{day_type.id}'",
        )

    async def update_day_type(
        call: ServiceCall,
    ) -> None:
        """Update a day type."""

        runtime = _get_runtime(
            call.hass,
        )

        day_type = DayType(
            id=call.data["id"],
            name=call.data["name"],
            scheduled_moments=(),
        )

        await _execute(
            operation=lambda: runtime.engine.update_day_type(
                day_type,
            ),
            runtime=runtime,
            description=f"Unable to update day type '{day_type.id}'",
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
    # week_schedule
    #

    async def add_week_schedule(
        call: ServiceCall,
    ) -> None:
        """Add a week schedule."""

        runtime = _get_runtime(
            call.hass,
        )

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
            description=(
                f"Unable to remove week schedule "
                f"'{call.data['id']}'"
            ),
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

        cycle = Cycle(
            id=call.data["id"],
            name=call.data["name"],
            week_schedule_ids=tuple(
                call.data["week_schedule_ids"]
            )
        )

        await _execute(
            operation=lambda: runtime.engine.add_cycle(
                cycle,
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

        cycle = Cycle(
            id=call.data["id"],
            name=call.data["name"],
            week_schedule_ids=tuple(
                call.data["week_schedule_ids"]
            )
        )

        await _execute(
            operation=lambda: runtime.engine.update_cycle(
                cycle,
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

        calendar_exception = CalendarException(
            id=call.data["id"],
            date=date.fromisoformat(
                datetime.strptime(
                    call.data["date"],
                    "%d/%m/%Y",
                ).date().isoformat()
            ),
            day_type_id=call.data["day_type_id"],
            description=call.data.get(
                "description"
            ),
        )

        await _execute(
            operation=lambda: runtime.engine.add_calendar_exception(
                calendar_exception,
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

        calendar_exception = CalendarException(
            id=call.data["id"],
            date=date.fromisoformat(
                datetime.strptime(
                    call.data["date"],
                    "%d/%m/%Y",
                ).date().isoformat()
            ),
            day_type_id=call.data["day_type_id"],
            description=call.data.get(
                "description"
            ),
        )

        await _execute(
            operation=lambda: runtime.engine.update_calendar_exception(
                calendar_exception,
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
