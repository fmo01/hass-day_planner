"""Core engine for Day Planner."""

from dataclasses import replace
from typing import TypeVar

from ..domain.calendar_exception import CalendarException
from ..domain.cycle import Cycle
from ..domain.day_type import DayType
from ..domain.moment import Moment
from ..domain.planner_configuration import PlannerConfiguration
from ..domain.scheduled_moment import ScheduledMoment
from ..domain.week_schedule import WeekSchedule
from .errors import NotFoundError, ValidationError
from .protocols import HasId
from .validator import PlannerValidator

T = TypeVar("T", bound=HasId)


class PlannerEngine:
    """Manipulate Day Planner configuration."""

    T = TypeVar("T")

    def __init__(
        self,
        configuration: PlannerConfiguration,
    ) -> None:
        """Initialize engine."""

        self._configuration = configuration

        PlannerValidator.validate_configuration(configuration)

    @property
    def configuration(
        self,
    ) -> PlannerConfiguration:
        """Return current configuration."""

        return self._configuration

    #
    # Generic helpers
    #

    def _find_by_id(
        self,
        items: tuple[T, ...],
        object_id: str,
        object_name: str,
    ) -> T:
        """Find an object by identifier."""

        for item in items:
            if item.id == object_id:
                return item

        raise NotFoundError(f"{object_name} not found: {object_id}")

    def _append(
        self,
        items: tuple[T, ...],
        item: T,
    ) -> tuple[T, ...]:
        """Return a tuple with an appended item."""

        return (
            *items,
            item,
        )

    def _replace_by_id(
        self,
        items: tuple[T, ...],
        item: T,
    ) -> tuple[T, ...]:
        """Replace an item having the same identifier."""

        return tuple(item if current.id == item.id else current for current in items)

    def _remove_by_id(
        self,
        items: tuple[T, ...],
        object_id: str,
    ) -> tuple[T, ...]:
        """Remove an item by identifier."""

        return tuple(item for item in items if item.id != object_id)

    def _replace_configuration(
        self,
        **changes,
    ) -> None:
        """Replace the current planner configuration."""

        configuration = replace(
            self._configuration,
            **changes,
        )

        PlannerValidator.validate_configuration(
            configuration,
        )

        self._configuration = configuration

    #
    # Moments
    #

    def get_moment(
        self,
        moment_id: str,
    ) -> Moment:
        """Return a moment by id."""

        return self._find_by_id(
            self._configuration.moments,
            moment_id,
            "Moment",
        )

    def add_moment(
        self,
        moment: Moment,
    ) -> None:
        """Add a moment."""

        self._replace_configuration(
            moments=self._append(
                self._configuration.moments,
                moment,
            ),
        )

    def update_moment(
        self,
        moment: Moment,
    ) -> None:
        """Replace an existing moment."""

        self.get_moment(
            moment.id,
        )

        self._replace_configuration(
            moments=self._replace_by_id(
                self._configuration.moments,
                moment,
            ),
        )

    def remove_moment(
        self,
        moment_id: str,
    ) -> None:
        """Remove a moment."""

        self.get_moment(
            moment_id,
        )
        for day_type in self._configuration.day_types:
            if any(
                scheduled.moment_id == moment_id
                for scheduled in day_type.scheduled_moments
            ):
                raise ValidationError("Cannot remove a moment used by a day type")

        self._replace_configuration(
            moments=self._remove_by_id(
                self._configuration.moments,
                moment_id,
            ),
        )

    #
    # Day types
    #

    def get_day_type(
        self,
        day_type_id: str,
    ) -> DayType:
        """Return a day type by id."""

        return self._find_by_id(
            self._configuration.day_types,
            day_type_id,
            "Day type",
        )

    def add_day_type(
        self,
        day_type: DayType,
    ) -> None:
        """Add a day type."""

        self._replace_configuration(
            day_types=self._append(
                self._configuration.day_types,
                day_type,
            ),
        )

    def update_day_type(
        self,
        day_type: DayType,
    ) -> None:
        """Replace an existing day type."""

        self.get_day_type(
            day_type.id,
        )

        self._replace_configuration(
            day_types=self._replace_by_id(
                self._configuration.day_types,
                day_type,
            ),
        )

    def remove_day_type(
        self,
        day_type_id: str,
    ) -> None:
        """Remove a day type."""

        self.get_day_type(
            day_type_id,
        )

        for week_schedule in self._configuration.week_schedules:
            if day_type_id in (
                week_schedule.monday,
                week_schedule.tuesday,
                week_schedule.wednesday,
                week_schedule.thursday,
                week_schedule.friday,
                week_schedule.saturday,
                week_schedule.sunday,
            ):
                raise ValidationError(
                    "Cannot remove a day type " "used by a week schedule"
                )

        for calendar_exception in self._configuration.calendar_exceptions:
            if calendar_exception.day_type_id == day_type_id:
                raise ValidationError(
                    "Cannot remove a day type used by a calendar exception"
                )

        self._replace_configuration(
            day_types=self._remove_by_id(
                self._configuration.day_types,
                day_type_id,
            ),
        )

    #
    # week_schedule
    #

    def get_week_schedule(
        self,
        week_schedule_id: str,
    ) -> WeekSchedule:
        """Return a week schedule."""

        return self._find_by_id(
            self._configuration.week_schedules,
            week_schedule_id,
            "Week schedule",
        )

    def add_week_schedule(
        self,
        week_schedule: WeekSchedule,
    ) -> None:
        """Add a week schedule."""

        self._replace_configuration(
            week_schedules=self._append(
                self._configuration.week_schedules,
                week_schedule,
            ),
        )

    def update_week_schedule(
        self,
        week_schedule: WeekSchedule,
    ) -> None:
        """Update a week schedule."""

        self.get_week_schedule(
            week_schedule.id,
        )

        self._replace_configuration(
            week_schedules=self._replace_by_id(
                self._configuration.week_schedules,
                week_schedule,
            ),
        )

    def remove_week_schedule(
        self,
        week_schedule_id: str,
    ) -> None:
        """Remove a week schedule."""

        self.get_week_schedule(
            week_schedule_id,
        )

        for cycle in self._configuration.cycles:
            if week_schedule_id in cycle.week_schedule_ids:
                raise ValidationError("Cannot remove a week schedule used by a cycle")

        self._replace_configuration(
            week_schedules=self._remove_by_id(
                self._configuration.week_schedules,
                week_schedule_id,
            ),
        )

    #
    # cycle
    #

    def get_cycle(
        self,
        cycle_id: str,
    ) -> Cycle:
        """Return a cycle."""

        return self._find_by_id(
            self._configuration.cycles,
            cycle_id,
            "Cycle",
        )

    def add_cycle(
        self,
        cycle: Cycle,
    ) -> None:
        """Add a cycle."""

        self._replace_configuration(
            cycles=self._append(
                self._configuration.cycles,
                cycle,
            ),
        )

    def update_cycle(
        self,
        cycle: Cycle,
    ) -> None:
        """Update a cycle."""

        self.get_cycle(
            cycle.id,
        )

        self._replace_configuration(
            cycles=self._replace_by_id(
                self._configuration.cycles,
                cycle,
            ),
        )

    def remove_cycle(
        self,
        cycle_id: str,
    ) -> None:
        """Remove a cycle."""

        self.get_cycle(
            cycle_id,
        )

        self._replace_configuration(
            cycles=self._remove_by_id(
                self._configuration.cycles,
                cycle_id,
            ),
        )

    #
    # calendar exception
    #

    def get_calendar_exception(
        self,
        calendar_exception_id: str,
    ) -> CalendarException:
        """Return a calendar_exception."""

        return self._find_by_id(
            self._configuration.calendar_exceptions,
            calendar_exception_id,
            "Calendar exception",
        )

    def add_calendar_exception(
        self,
        calendar_exception: CalendarException,
    ) -> None:
        """Add a calendar_exception."""

        self._replace_configuration(
            calendar_exceptions=self._append(
                self._configuration.calendar_exceptions,
                calendar_exception,
            ),
        )

    def update_calendar_exception(
        self,
        calendar_exception: CalendarException,
    ) -> None:
        """Update a calendar_exception."""

        self.get_calendar_exception(
            calendar_exception.id,
        )

        self._replace_configuration(
            calendar_exceptions=self._replace_by_id(
                self._configuration.calendar_exceptions,
                calendar_exception,
            ),
        )

    def remove_calendar_exception(
        self,
        calendar_exception_id: str,
    ) -> None:
        """Remove a calendar_exception."""

        self.get_calendar_exception(
            calendar_exception_id,
        )

        self._replace_configuration(
            calendar_exceptions=self._remove_by_id(
                self._configuration.calendar_exceptions,
                calendar_exception_id,
            ),
        )

    #

    def add_scheduled_moment(
        self,
        day_type_id: str,
        scheduled_moment: ScheduledMoment,
    ) -> None:
        """Add scheduled moment to day type."""

        day_types = list(self._configuration.day_types)

        for index, day_type in enumerate(day_types):
            if day_type.id == day_type_id:
                day_types[index] = replace(
                    day_type,
                    scheduled_moments=(
                        *day_type.scheduled_moments,
                        scheduled_moment,
                    ),
                )

                configuration = replace(
                    self._configuration,
                    day_types=tuple(day_types),
                )

                PlannerValidator.validate_configuration(configuration)

                self._configuration = configuration

                return

        raise NotFoundError(f"Day type not found: {day_type_id}")

    def update_scheduled_moment(
        self,
        day_type_id: str,
        scheduled_moment: ScheduledMoment,
    ) -> None:
        """Update a scheduled moment in a day type."""

        day_type = self.get_day_type(day_type_id)

        found = False
        scheduled_moments = []

        for item in day_type.scheduled_moments:
            if item.moment_id == scheduled_moment.moment_id:
                scheduled_moments.append(scheduled_moment)
                found = True
            else:
                scheduled_moments.append(item)

        if not found:
            raise NotFoundError(
                "Scheduled moment not found: " f"{scheduled_moment.moment_id}"
            )

        updated_day_type = DayType(
            id=day_type.id,
            name=day_type.name,
            scheduled_moments=tuple(scheduled_moments),
        )

        self.update_day_type(updated_day_type)

    def remove_scheduled_moment(
        self,
        day_type_id: str,
        moment_id: str,
    ) -> None:
        """Remove a scheduled moment from a day type."""

        day_type = self.get_day_type(day_type_id)

        scheduled_moments = tuple(
            item for item in day_type.scheduled_moments if item.moment_id != moment_id
        )

        if len(scheduled_moments) == len(day_type.scheduled_moments):
            raise NotFoundError("Scheduled moment not found: " f"{moment_id}")

        updated_day_type = DayType(
            id=day_type.id,
            name=day_type.name,
            scheduled_moments=scheduled_moments,
        )

        self.update_day_type(updated_day_type)
