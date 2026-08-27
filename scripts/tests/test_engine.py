from datetime import date, time

import pytest

from custom_components.day_planner.domain.calendar_exception import (
     CalendarException,
)
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.planner_configuration import (
    PlannerConfiguration,
)
from custom_components.day_planner.domain.scheduled_moment import (
    ScheduledMoment,
)
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.week_schedule import WeekSchedule
from custom_components.day_planner.planner.engine import PlannerEngine
from custom_components.day_planner.planner.errors import (NotFoundError,
                                                          ValidationError)
from custom_components.day_planner.domain.action import Action

def test_engine_get_moment(moment):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(moment,),
            day_types=(),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    assert engine.get_moment("m1") == moment


def test_engine_get_moment_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Moment not found: unknown",
    ):
        engine.get_moment("unknown")


def test_engine_add_moment(moment):
    engine = PlannerEngine(PlannerConfiguration.empty())

    engine.add_moment(moment)

    assert engine.configuration.moments == (moment,)


def test_engine_update_moment(
    moment,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(moment,),
            day_types=(),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    updated_moment = Moment(
        id=moment.id,
        name="Moment modifié",
        icon="mdi:home",
    )
    engine.update_moment(updated_moment)

    assert engine.configuration.moments == (updated_moment,)


def test_engine_add_moment_with_action():
    action = Action(
        service="light.turn_on",
        data={
            "entity_id": "light.salon",
        },
    )

    moment = Moment(
        id="m1",
        name="Réveil",
        icon="mdi:alarm",
        actions=(action,),
    )

    engine = PlannerEngine(
        PlannerConfiguration.empty()
    )

    engine.add_moment(moment)

    assert engine.get_moment("m1") == moment
    assert engine.get_moment("m1").actions == (
        action,
    )


def test_engine_rejects_moment_with_invalid_action():
    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            Action(
                service="",
                data={},
            ),
        ),
    )

    engine = PlannerEngine(
        PlannerConfiguration.empty()
    )

    with pytest.raises(
        ValidationError,
        match="Action service cannot be empty",
    ):
        engine.add_moment(moment)

    assert engine.configuration.moments == ()


def test_engine_remove_moment(moment):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(moment,),
            day_types=(),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.remove_moment(moment.id)

    assert engine.configuration.moments == ()


def test_engine_remove_moment_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Moment not found: unknown",
    ):
        engine.remove_moment("unknown")


def test_engine_remove_moment_used_by_day_type(moment):
    scheduled = ScheduledMoment(
        moment_id=moment.id,
        time_definition=TimeDefinition(
            fixed_time=time(8, 0),
        ),
    )

    day_type = DayType(
        id="dt1",
        name="Télétravail",
        scheduled_moments=(scheduled,),
    )

    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(moment,),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    with pytest.raises(
        ValidationError,
        match="Cannot remove a moment used by a day type",
    ):
        engine.remove_moment(moment.id)


def test_engine_get_day_type(day_type):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    assert engine.get_day_type("dt1") == day_type


def test_engine_get_day_type_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Day type not found: unknown",
    ):
        engine.get_day_type("unknown")


def test_engine_add_day_type(day_type):
    engine = PlannerEngine(PlannerConfiguration.empty())

    engine.add_day_type(day_type)

    assert engine.configuration.day_types == (day_type,)


def test_engine_update_day_type(day_type):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    updated_day_type = DayType(
        id=day_type.id,
        name="DayType modifié",
        scheduled_moments=day_type.scheduled_moments,
    )

    engine.update_day_type(updated_day_type)

    assert engine.configuration.day_types == (updated_day_type,)


def test_engine_remove_day_type(day_type):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.remove_day_type(day_type.id)

    assert engine.configuration.day_types == ()


def test_engine_remove_day_type_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Day type not found: unknown",
    ):
        engine.remove_day_type("unknown")


def test_engine_remove_day_type_used_by_week_schedule(
    day_type,
):
    week_schedule = WeekSchedule(
        id="ws1",
        name="Semaine 1",
        monday=day_type.id,
        tuesday=day_type.id,
        wednesday=day_type.id,
        thursday=day_type.id,
        friday=day_type.id,
        saturday=day_type.id,
        sunday=day_type.id,
    )

    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    with pytest.raises(
        ValidationError,
        match="Cannot remove a day type used by a week schedule",
    ):
        engine.remove_day_type(day_type.id)

    assert engine.configuration.day_types == (day_type,)


def test_engine_remove_day_type_used_by_calendar_exception(
    day_type,
):
    calendar_exception = CalendarException(
        id="ce1",
        date=date(2027, 1, 1),
        day_type_id=day_type.id,
        description="Congé",
    )

    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(calendar_exception,),
        )
    )

    with pytest.raises(
        ValidationError,
        match="Cannot remove a day type used by a calendar exception",
    ):
        engine.remove_day_type(day_type.id)

    assert engine.configuration.day_types == (day_type,)


def test_engine_get_week_schedule1(week_schedule):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    assert engine.get_week_schedule(week_schedule.id) == week_schedule


def test_engine_get_week_schedule2(
    day_type,
    week_schedule,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    assert engine.get_week_schedule(week_schedule.id) == week_schedule


def test_engine_get_week_schedule_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Week schedule not found: unknown",
    ):
        engine.get_week_schedule("unknown")


def test_engine_add_week_schedule(
    day_type,
    week_schedule,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.add_week_schedule(week_schedule)

    assert engine.configuration.week_schedules == (week_schedule,)


def test_engine_update_week_schedule(
    day_type,
    week_schedule,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    updated = WeekSchedule(
        id=week_schedule.id,
        name="Semaine modifiée",
        monday=week_schedule.monday,
        tuesday=week_schedule.tuesday,
        wednesday=week_schedule.wednesday,
        thursday=week_schedule.thursday,
        friday=week_schedule.friday,
        saturday=week_schedule.saturday,
        sunday=week_schedule.sunday,
    )

    engine.update_week_schedule(updated)

    assert engine.configuration.week_schedules == (updated,)


def test_engine_remove_week_schedule(
    day_type,
    week_schedule,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.remove_week_schedule(week_schedule.id)

    assert engine.configuration.week_schedules == ()


def test_engine_remove_week_schedule_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Week schedule not found: unknown",
    ):
        engine.remove_week_schedule("unknown")


def test_engine_get_cycle(cycle, week_schedule):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(cycle,),
            calendar_exceptions=(),
        )
    )

    assert engine.get_cycle(cycle.id) == cycle


def test_engine_get_cycle_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Cycle not found: unknown",
    ):
        engine.get_cycle("unknown")


def test_engine_add_cycle(cycle, week_schedule):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.add_cycle(cycle)

    assert engine.get_cycle(cycle.id) == cycle


def test_engine_update_cycle(cycle, week_schedule):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(cycle,),
            calendar_exceptions=(),
        )
    )

    updated = Cycle(
        id=cycle.id,
        name="Cycle modifié",
        start_date=date(2026, 8, 31),
        week_schedule_ids=cycle.week_schedule_ids,
    )

    engine.update_cycle(updated)

    assert engine.get_cycle(cycle.id) == updated


def test_engine_remove_cycle(cycle, week_schedule):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(cycle,),
            calendar_exceptions=(),
        )
    )

    engine.remove_cycle(cycle.id)

    with pytest.raises(
        NotFoundError,
        match="Cycle not found: " + cycle.id,
    ):
        engine.get_cycle(cycle.id)


def test_engine_remove_cycle_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Cycle not found: unknown",
    ):
        engine.remove_cycle("unknown")


def test_engine_add_cycle_with_week_schedule(
    cycle,
    week_schedule,
):
    cycle = Cycle(
        id="c2",
        name="Cycle 2",
        start_date=date(2026, 8, 31),
        week_schedule_ids=(week_schedule.id,),
    )

    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.add_cycle(cycle)

    assert engine.get_cycle(cycle.id) == cycle


def test_engine_add_cycle_unknown_week_schedule():
    cycle = Cycle(
        id="c2",
        name="Cycle 2",
        start_date=date(2026, 8, 31),
        week_schedule_ids=("unknown",),
    )

    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        ValidationError,
        match="Unknown week schedule: unknown",
    ):
        engine.add_cycle(cycle)


def test_engine_get_calendar_exception(
    day_type,
    calendar_exception,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(calendar_exception,),
        )
    )

    assert engine.get_calendar_exception(calendar_exception.id) == calendar_exception


def test_engine_get_calendar_exception_not_found(
    day_type,
):
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Calendar exception not found: unknown",
    ):
        engine.get_calendar_exception("unknown")


def test_engine_add_calendar_exception(
    calendar_exception,
    day_type,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.add_calendar_exception(calendar_exception)

    assert engine.get_calendar_exception(calendar_exception.id) == calendar_exception


def test_engine_update_calendar_exception(
    calendar_exception,
    day_type,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(calendar_exception,),
        )
    )

    updated = CalendarException(
        id=calendar_exception.id,
        date=calendar_exception.date,
        day_type_id=calendar_exception.day_type_id,
        description="Congé modifié",
    )

    engine.update_calendar_exception(updated)

    assert engine.get_calendar_exception(calendar_exception.id) == updated


def test_engine_remove_calendar_exception(
    calendar_exception,
    day_type,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(calendar_exception,),
        )
    )

    engine.remove_calendar_exception(calendar_exception.id)

    with pytest.raises(
        NotFoundError,
        match=f"Calendar exception not found: " f"{calendar_exception.id}",
    ):
        engine.get_calendar_exception(calendar_exception.id)


def test_engine_remove_calendar_exception_not_found():
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Calendar exception not found: unknown",
    ):
        engine.remove_calendar_exception("unknown")


def test_engine_add_calendar_exception_unknown_day_type():
    exception = CalendarException(
        id="ce2",
        date=date(2027, 1, 2),
        day_type_id="unknown",
        description="Test",
    )

    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        ValidationError,
        match="Unknown day type: unknown",
    ):
        engine.add_calendar_exception(exception)


def test_engine_update_calendar_exception_unknown_day_type(
    calendar_exception,
    day_type,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(calendar_exception,),
        )
    )

    updated = CalendarException(
        id=calendar_exception.id,
        date=calendar_exception.date,
        day_type_id="unknown",
        description="Test",
    )

    with pytest.raises(
        ValidationError,
        match="Unknown day type: unknown",
    ):
        engine.update_calendar_exception(updated)


def test_engine_remove_week_schedule_used_by_cycle(
    week_schedule,
    cycle,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(),
            day_types=(),
            week_schedules=(week_schedule,),
            cycles=(cycle,),
            calendar_exceptions=(),
        )
    )

    with pytest.raises(
        ValidationError,
        match="Cannot remove a week schedule used by a cycle",
    ):
        engine.remove_week_schedule(week_schedule.id)


def test_engine_add_scheduled_moment(
    moment,
    day_type,
    scheduled_moment,
):
    engine = PlannerEngine(
        PlannerConfiguration(
            moments=(moment,),
            day_types=(day_type,),
            week_schedules=(),
            cycles=(),
            calendar_exceptions=(),
        )
    )

    engine.add_scheduled_moment(
        day_type.id,
        scheduled_moment,
    )

    updated_day_type = engine.get_day_type(day_type.id)

    assert scheduled_moment in (updated_day_type.scheduled_moments)


def test_engine_add_scheduled_moment_day_type_not_found(
    scheduled_moment,
):
    engine = PlannerEngine(PlannerConfiguration.empty())

    with pytest.raises(
        NotFoundError,
        match="Day type not found: unknown",
    ):
        engine.add_scheduled_moment(
            "unknown",
            scheduled_moment,
        )
