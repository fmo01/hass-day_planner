from dataclasses import replace
from datetime import date, time

import pytest

from custom_components.day_planner.const import DEFAULT_MAX_CYCLES
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.calendar_exception import \
    CalendarException
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.planner_configuration import \
    PlannerConfiguration
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.week_schedule import WeekSchedule
from custom_components.day_planner.planner.validator import (PlannerValidator,
                                                             ValidationError)


def test_validator_accepts_valid_configuration(
    moment,
    day_type,
    week_schedule,
    cycle,
    calendar_exception,
):
    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(calendar_exception,),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_duplicate_ids(
    moment,
):
    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(
            DayType(
                id="m1",
                name="Duplicate",
                scheduled_moments=(),
            ),
        ),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate identifier detected",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_accepts_day_type_with_moments(
    moment,
):
    day_type = DayType(
        id="dt1",
        name="Télétravail",
        scheduled_moments=(
            ScheduledMoment(
                moment_id=moment.id,
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_unknown_moment():
    day_type = DayType(
        id="dt1",
        name="Télétravail",
        scheduled_moments=(
            ScheduledMoment(
                moment_id="unknown",
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Unknown moment: unknown",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_duplicate_moment_in_day_type(
    moment,
):
    day_type = DayType(
        id="dt1",
        name="Télétravail",
        scheduled_moments=(
            ScheduledMoment(
                moment_id=moment.id,
                time_definition=TimeDefinition(
                    fixed_time=time(8, 0),
                ),
            ),
            ScheduledMoment(
                moment_id=moment.id,
                time_definition=TimeDefinition(
                    fixed_time=time(18, 0),
                ),
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate moment in day type: Télétravail",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_accepts_cycle_with_one_week_schedule(week_schedule, day_type):
    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=(week_schedule.id,),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_accepts_cycle_with_four_week_schedules(day_type):
    week_schedules = tuple(
        WeekSchedule(
            id=f"ws{i}",
            name=f"Semaine {i}",
            monday="dt1",
            tuesday="dt1",
            wednesday="dt1",
            thursday="dt1",
            friday="dt1",
            saturday="dt1",
            sunday="dt1",
        )
        for i in range(1, 5)
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=tuple(item.id for item in week_schedules),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=week_schedules,
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_cycle_without_week_schedule(day_type):
    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=(),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Cycle must contain between 1 and 4 weeks",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_cycle_with_five_week_schedules(day_type):
    week_schedules = tuple(
        WeekSchedule(
            id=f"ws{i}",
            name=f"Semaine {i}",
            monday="dt1",
            tuesday="dt1",
            wednesday="dt1",
            thursday="dt1",
            friday="dt1",
            saturday="dt1",
            sunday="dt1",
        )
        for i in range(1, 6)
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=tuple(item.id for item in week_schedules),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=week_schedules,
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Cycle must contain between 1 and 4 weeks",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_unknown_week_schedule(day_type):
    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("unknown",),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Unknown week schedule: unknown",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_accepts_calendar_exception(
    day_type,
):
    calendar_exception = CalendarException(
        id="ce1",
        date=date(2027, 1, 1),
        day_type_id=day_type.id,
        description="Congé",
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(calendar_exception,),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_unknown_day_type_in_calendar_exception():
    calendar_exception = CalendarException(
        id="ce1",
        date=date(2027, 1, 1),
        day_type_id="unknown",
        description="Congé",
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(calendar_exception,),
    )

    with pytest.raises(
        ValidationError,
        match="Unknown day type: unknown",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_accepts_moment_with_action():
    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            Action(
                id="salon",
                sequence=[
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_action_without_sequence():
    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            Action(
                id="action_1",
                sequence=[],
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Action sequence cannot be empty",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_action_without_id():
    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            Action(
                id="",
                sequence=[
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Action id cannot be empty",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_cycle_start_date_not_monday(
    week_schedule,
    day_type,
):
    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 9, 1),
        week_schedule_ids=(week_schedule.id,),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Cycle start date must be a Monday",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_multiple_cycles(
    week_schedule,
    day_type,
):
    cycles = tuple(
        Cycle(
            id=f"c{index}",
            name=f"Cycle {index}",
            start_date=start_date,
            week_schedule_ids=(week_schedule.id,),
        )
        for index, start_date in enumerate(
            (
                date(2026, 8, 31),
                date(2026, 9, 7),
                date(2026, 9, 14),
                date(2026, 9, 21),
            ),
            start=1,
        )
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=cycles,
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match=rf"Maximum number of cycles exceeded: {DEFAULT_MAX_CYCLES}",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_cycle_not_starting_monday(
    week_schedule,
    day_type,
):
    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 9, 1),  # mardi
        week_schedule_ids=(week_schedule.id,),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Cycle start date must be a Monday",
    ):
        PlannerValidator.validate_configuration(configuration)


def test_validator_rejects_duplicate_action_id():
    moment = Moment(
        id="wake_up",
        name="Réveil",
        icon="mdi:alarm",
        actions=(
            Action(
                id="salon",
                sequence=[
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
            Action(
                id="salon",
                sequence=[
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
        ),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match=("Duplicate action id in moment " "'wake_up': salon"),
    ):
        PlannerValidator.validate_configuration(configuration)


def test_cycles_cannot_have_same_start_date(
    day_type,
    week_schedule,
):
    cycle1 = Cycle(
        id="cycle1",
        name="Cycle 1",
        start_date=date(2026, 9, 7),
        week_schedule_ids=(week_schedule.id,),
    )

    cycle2 = Cycle(
        id="cycle2",
        name="Cycle 2",
        start_date=date(2026, 9, 7),
        week_schedule_ids=(week_schedule.id,),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(
            cycle1,
            cycle2,
        ),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match=("Duplicate cycle start date: " "2026-09-07"),
    ):
        PlannerValidator.validate_configuration(configuration)


def test_calendar_exceptions_cannot_have_same_date(
    day_type,
):
    exception1 = CalendarException(
        id="exception1",
        date=date(2026, 9, 15),
        day_type_id=day_type.id,
        description="Exception 1",
    )

    exception2 = CalendarException(
        id="exception2",
        date=date(2026, 9, 15),
        day_type_id=day_type.id,
        description="Exception 2",
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(
            exception1,
            exception2,
        ),
    )

    with pytest.raises(
        ValidationError,
        match=("Duplicate calendar exception date: " "2026-09-15"),
    ):
        PlannerValidator.validate_configuration(configuration)


@pytest.mark.parametrize(
    "weekday",
    (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ),
)
def test_validator_rejects_unknown_day_type_in_week_schedule(
    weekday,
    day_type,
    week_schedule,
):
    invalid_week = replace(
        week_schedule,
        **{weekday: "unknown"},
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(invalid_week,),
        cycles=(),
        calendar_exceptions=(),
    )

    with pytest.raises(
        ValidationError,
        match="Unknown day type: unknown",
    ):
        PlannerValidator.validate_configuration(configuration)
