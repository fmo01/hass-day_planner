"""Resolve Day Planner configuration for a date."""

from datetime import date

from ..domain.day_type import DayType
from ..domain.planner_configuration import PlannerConfiguration
from ..domain.moment import Moment
from ..domain.scheduled_moment import ScheduledMoment


class PlannerResolver:
    """Resolve the applicable Day Planner configuration."""

    def __init__(
        self,
        configuration: PlannerConfiguration,
    ) -> None:
        """Initialize resolver."""

        self._configuration = configuration

    def resolve_day_type(
        self,
        target_date: date,
    ) -> DayType | None:
        """Resolve the day type applicable to a date."""

        calendar_exception = next(
            (
                item
                for item in self._configuration.calendar_exceptions
                if item.date == target_date
            ),
            None,
        )

        if calendar_exception is not None:
            return self._find_day_type(
                calendar_exception.day_type_id
            )

        if not self._configuration.cycles:
            return None

        cycle = self._configuration.cycles[0]

        if target_date < cycle.start_date:
            return None

        days_since_start = (
            target_date - cycle.start_date
        ).days

        week_index = (
            days_since_start // 7
        ) % len(cycle.week_schedule_ids)

        week_schedule_id = cycle.week_schedule_ids[
            week_index
        ]

        week_schedule = next(
            item
            for item in self._configuration.week_schedules
            if item.id == week_schedule_id
        )

        day_type_id = getattr(
            week_schedule,
            target_date.strftime("%A").lower(),
        )

        return self._find_day_type(day_type_id)

    def _find_day_type(
        self,
        day_type_id: str,
    ) -> DayType:
        """Find a day type."""

        return next(
            item
            for item in self._configuration.day_types
            if item.id == day_type_id
        )

    def resolve_scheduled_moments(
        self,
        target_date: date,
    ) -> tuple[ScheduledMoment, ...]:
        """Resolve scheduled moments for a date."""

        day_type = self.resolve_day_type(
            target_date
        )

        if day_type is None:
            return ()

        return day_type.scheduled_moments


    def resolve_moment(
        self,
        moment_id: str,
    ) -> Moment:
        """Resolve a moment by id."""

        return next(
            item
            for item in self._configuration.moments
            if item.id == moment_id
        )


    def resolve_schedule(
        self,
        target_date: date,
    ) -> tuple[tuple[ScheduledMoment, Moment], ...]:
        """Resolve scheduled moments with their moment definitions."""

        return tuple(
            (
                scheduled,
                self.resolve_moment(
                    scheduled.moment_id
                ),
            )
            for scheduled in self.resolve_scheduled_moments(
                target_date
            )
        )

    def update_configuration(
        self,
        configuration: PlannerConfiguration,
    ) -> None:
        """Update resolver configuration."""

        self._configuration = configuration

