from datetime import date, time

from custom_components.day_planner.domain.calendar_exception import (
    CalendarException,
)
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.planner_configuration import (
    PlannerConfiguration,
)
from custom_components.day_planner.domain.week_schedule import (
    WeekSchedule,
)
from custom_components.day_planner.planner.resolver import (
    PlannerResolver,
)
from datetime import time

from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_moment import (
    ScheduledMoment,
)
from custom_components.day_planner.domain.time_definition import (
    TimeDefinition,
)


def test_resolver_without_cycle():
    configuration = PlannerConfiguration.empty()

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_day_type(
        date(2026, 8, 31)
    ) is None


def test_resolver_before_cycle_start_date():
    day_type = DayType(
        id="dt1",
        name="Travail",
        scheduled_moments=(),
    )

    week_schedule = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday="dt1",
        tuesday="dt1",
        wednesday="dt1",
        thursday="dt1",
        friday="dt1",
        saturday="dt1",
        sunday="dt1",
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("ws1",),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_day_type(
        date(2026, 8, 30)
    ) is None


def test_resolver_calendar_exception_has_priority():
    normal = DayType(
        id="normal",
        name="Normal",
        scheduled_moments=(),
    )

    holiday = DayType(
        id="holiday",
        name="Férié",
        scheduled_moments=(),
    )

    week_schedule = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday="normal",
        tuesday="normal",
        wednesday="normal",
        thursday="normal",
        friday="normal",
        saturday="normal",
        sunday="normal",
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("ws1",),
    )

    calendar_exception = CalendarException(
        id="ce1",
        date=date(2026, 9, 1),
        day_type_id="holiday",
        description="Exception",
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(normal, holiday),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(calendar_exception,),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_day_type(
        date(2026, 9, 1)
    ) == holiday


def test_resolver_two_week_cycle():
    week1_day = DayType(
        id="week1",
        name="Semaine 1",
        scheduled_moments=(),
    )

    week2_day = DayType(
        id="week2",
        name="Semaine 2",
        scheduled_moments=(),
    )

    week_schedule1 = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday="week1",
        tuesday="week1",
        wednesday="week1",
        thursday="week1",
        friday="week1",
        saturday="week1",
        sunday="week1",
    )

    week_schedule2 = WeekSchedule(
        id="ws2",
        name="Semaine 2",
        monday="week2",
        tuesday="week2",
        wednesday="week2",
        thursday="week2",
        friday="week2",
        saturday="week2",
        sunday="week2",
    )

    cycle = Cycle(
        id="c1",
        name="Cycle alterné",
        start_date=date(2026, 8, 31),
        week_schedule_ids=(
            "ws1",
            "ws2",
        ),
    )

    configuration = PlannerConfiguration(
        moments=(),
        day_types=(week1_day, week2_day),
        week_schedules=(
            week_schedule1,
            week_schedule2,
        ),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_day_type(
        date(2026, 8, 31)
    ) == week1_day

    assert resolver.resolve_day_type(
        date(2026, 9, 6)
    ) == week1_day

    assert resolver.resolve_day_type(
        date(2026, 9, 7)
    ) == week2_day

    assert resolver.resolve_day_type(
        date(2026, 9, 13)
    ) == week2_day

    assert resolver.resolve_day_type(
        date(2026, 9, 14)
    ) == week1_day

def test_resolver_scheduled_moments():
    moment = Moment(
        id="m1",
        name="Réveil",
    )

    scheduled = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(8, 0),
        ),
    )

    day_type = DayType(
        id="dt1",
        name="Travail",
        scheduled_moments=(scheduled,),
    )

    week_schedule = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday="dt1",
        tuesday="dt1",
        wednesday="dt1",
        thursday="dt1",
        friday="dt1",
        saturday="dt1",
        sunday="dt1",
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("ws1",),
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_scheduled_moments(
        date(2026, 8, 31)
    ) == (
        scheduled,
    )

def test_resolver_resolve_moment():
    moment = Moment(
        id="m1",
        name="Réveil",
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_moment(
        "m1"
    ) == moment


def test_resolver_resolve_schedule():
    moment1 = Moment(
        id="m1",
        name="Réveil",
    )

    moment2 = Moment(
        id="m2",
        name="Départ",
    )

    scheduled1 = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(7, 30),
        ),
    )

    scheduled2 = ScheduledMoment(
        moment_id="m2",
        time_definition=TimeDefinition(
            fixed_time=time(8, 15),
        ),
    )

    day_type = DayType(
        id="dt1",
        name="Travail",
        scheduled_moments=(
            scheduled1,
            scheduled2,
        ),
    )

    week_schedule = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday="dt1",
        tuesday="dt1",
        wednesday="dt1",
        thursday="dt1",
        friday="dt1",
        saturday="dt1",
        sunday="dt1",
    )

    cycle = Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("ws1",),
    )

    configuration = PlannerConfiguration(
        moments=(
            moment1,
            moment2,
        ),
        day_types=(day_type,),
        week_schedules=(week_schedule,),
        cycles=(cycle,),
        calendar_exceptions=(),
    )

    resolver = PlannerResolver(configuration)

    assert resolver.resolve_schedule(
        date(2026, 8, 31)
    ) == (
        (
            scheduled1,
            moment1,
        ),
        (
            scheduled2,
            moment2,
        ),
    )


def test_resolver_resolve_scheduled_moments_without_day_type():
    configuration = PlannerConfiguration.empty()

    resolver = PlannerResolver(
        configuration
    )

    result = resolver.resolve_scheduled_moments(
        date(2026, 8, 31)
    )

    assert result == ()

def test_resolver_update_configuration():
    resolver = PlannerResolver(
        PlannerConfiguration.empty()
    )

    moment = Moment(
        id="m1",
        name="Réveil",
    )

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    resolver.update_configuration(
        configuration
    )

    assert resolver.resolve_moment("m1") == moment
