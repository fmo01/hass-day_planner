from datetime import date, time

import pytest

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
from custom_components.day_planner.planner.engine import PlannerEngine


@pytest.fixture
def moment():
    return Moment(
        id="m1",
        name="Moment 1",
        icon="mdi:coffee",
    )


@pytest.fixture
def moment2():
    return Moment(
        id="m2",
        name="Moment 2",
        icon="mdi:home",
    )


@pytest.fixture
def day_type():
    return DayType(
        id="dt1",
        name="Télétravail",
        scheduled_moments=(),
    )


@pytest.fixture
def week_schedule():
    return WeekSchedule(
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


@pytest.fixture
def cycle():
    return Cycle(
        id="c1",
        name="Cycle 1",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("ws1",),
    )


@pytest.fixture
def calendar_exception():
    return CalendarException(
        id="ce1",
        date=date(2027, 1, 1),
        day_type_id="dt1",
        description="Congé",
    )


@pytest.fixture
def scheduled_moment(moment):
    return ScheduledMoment(
        moment_id=moment.id,
        time_definition=TimeDefinition(
            fixed_time=time(8, 0),
        ),
    )


@pytest.fixture
def empty_configuration():
    return PlannerConfiguration.empty()


@pytest.fixture
def engine():
    return PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )
