"""Domain validation rules for Day Planner."""

from ..const import DEFAULT_MAX_CYCLES
from ..domain.calendar_exception import CalendarException
from ..domain.cycle import Cycle
from ..domain.day_type import DayType
from ..domain.planner_configuration import PlannerConfiguration
from .errors import ValidationError


class PlannerValidator:
    """Validate Day Planner domain objects."""

    @staticmethod
    def validate_configuration(
        configuration: PlannerConfiguration,
        max_cycles: int = DEFAULT_MAX_CYCLES,
    ) -> None:
        """Validate complete configuration."""

        PlannerValidator._validate_unique_ids(configuration)

        PlannerValidator._validate_moments(configuration)

        PlannerValidator._validate_day_types(configuration)

        PlannerValidator._validate_cycles(configuration)

        PlannerValidator._validate_cycle_count(
            configuration,
            max_cycles,
        )

        PlannerValidator._validate_calendar_exceptions(configuration)

        PlannerValidator._validate_action_ids(
            configuration
        )

        PlannerValidator._validate_action_ids(
            configuration
        )

    @staticmethod
    def _validate_unique_ids(
        configuration: PlannerConfiguration,
    ) -> None:
        """Ensure all IDs are unique."""

        ids: list[str] = []

        ids.extend(item.id for item in configuration.moments)

        ids.extend(item.id for item in configuration.day_types)

        ids.extend(item.id for item in configuration.week_schedules)

        ids.extend(item.id for item in configuration.cycles)

        ids.extend(item.id for item in configuration.calendar_exceptions)

        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate identifier detected")

    @staticmethod
    def _validate_moments(
        configuration: PlannerConfiguration,
    ) -> None:
        """Validate moments."""

        for moment in configuration.moments:
            for action in moment.actions:
                PlannerValidator._validate_action(
                    action,
                )

    @staticmethod
    def _validate_action_ids(
        configuration: PlannerConfiguration,
    ) -> None:
        """Validate action identifiers."""

        for moment in configuration.moments:
            action_ids: set[str] = set()

            for action in moment.actions:
                if not action.id:
                    raise ValidationError(
                        "Action id cannot be empty"
                    )

                if action.id in action_ids:
                    raise ValidationError(
                        f"Duplicate action id in moment "
                        f"'{moment.id}': {action.id}"
                    )

                action_ids.add(action.id)


    @staticmethod
    def _validate_action(
        action,
    ) -> None:
        """Validate one action."""

        if not action.service.strip():
            raise ValidationError("Action service cannot be empty")

    @staticmethod
    def _validate_day_types(
        configuration: PlannerConfiguration,
    ) -> None:
        """Validate day types."""

        moment_ids = {item.id for item in configuration.moments}

        for day_type in configuration.day_types:
            PlannerValidator._validate_day_type(
                day_type,
                moment_ids,
            )

    @staticmethod
    def _validate_day_type(
        day_type: DayType,
        moment_ids: set[str],
    ) -> None:
        """Validate one day type."""

        used_moments: set[str] = set()

        for scheduled in day_type.scheduled_moments:
            if scheduled.moment_id not in moment_ids:
                raise ValidationError(f"Unknown moment: " f"{scheduled.moment_id}")

            if scheduled.moment_id in used_moments:
                raise ValidationError(
                    f"Duplicate moment in " f"day type: {day_type.name}"
                )

            used_moments.add(scheduled.moment_id)

    @staticmethod
    def _validate_cycles(
        configuration: PlannerConfiguration,
    ) -> None:
        """Validate cycles."""

        week_schedule_ids = {item.id for item in configuration.week_schedules}

        for cycle in configuration.cycles:
            PlannerValidator._validate_cycle(
                cycle,
                week_schedule_ids,
            )

    @staticmethod
    def _validate_cycle(
        cycle: Cycle,
        week_schedule_ids: set[str],
    ) -> None:
        """Validate one cycle."""

        if cycle.start_date.weekday() != 0:
            raise ValidationError("Cycle start date must be a Monday")

        size = len(cycle.week_schedule_ids)

        if size < 1 or size > 4:
            raise ValidationError("Cycle must contain between 1 and 4 weeks")

        for week_schedule_id in cycle.week_schedule_ids:
            if week_schedule_id not in week_schedule_ids:
                raise ValidationError(f"Unknown week schedule: {week_schedule_id}")

    @staticmethod
    def _validate_cycle_count(
        configuration: PlannerConfiguration,
        max_cycles: int,
    ) -> None:
        """Ensure the maximum cycle count is not exceeded."""

        if len(configuration.cycles) > max_cycles:
            raise ValidationError(
                f"Maximum number of cycles exceeded: {max_cycles}"
            )

    @staticmethod
    def _validate_calendar_exceptions(
        configuration: PlannerConfiguration,
    ) -> None:
        """Validate calendar exceptions."""

        day_type_ids = {item.id for item in configuration.day_types}

        for calendar_exception in configuration.calendar_exceptions:
            PlannerValidator._validate_calendar_exception(
                calendar_exception,
                day_type_ids,
            )

    @staticmethod
    def _validate_calendar_exception(
        calendar_exception: CalendarException,
        day_type_ids: set[str],
    ) -> None:
        """Validate one calendar exception."""

        if calendar_exception.day_type_id not in day_type_ids:
            raise ValidationError(
                f"Unknown day type: " f"{calendar_exception.day_type_id}"
            )
