from datetime import date, datetime, time

from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.calendar_exception import \
    CalendarException
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.metadata import Audit
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.planner_configuration import \
    PlannerConfiguration
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.week_schedule import WeekSchedule


def test_moment_roundtrip(moment):
    data = moment.to_dict()

    restored = Moment.from_dict(data)

    assert restored == moment


def test_action_roundtrip():
    action = Action(
        id="salon_on",
        service="light.turn_on",
        data={
            "entity_id": "light.salon",
        },
    )

    data = action.to_dict()

    assert data == {
        "id": "salon_on",
        "service": "light.turn_on",
        "data": {
            "entity_id": "light.salon",
        },
    }

    restored = Action.from_dict(data)

    assert restored == action


def test_moment_with_actions_roundtrip():
    action = Action(
        id="salon_on",
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

    data = moment.to_dict()

    assert data == {
        "id": "m1",
        "name": "Réveil",
        "icon": "mdi:alarm",
        "actions": [
            {
                "id": "salon_on",
                "service": "light.turn_on",
                "data": {
                    "entity_id": "light.salon",
                },
            },
        ],
    }

    restored = Moment.from_dict(data)

    assert restored == moment


def test_day_type_roundtrip(day_type):
    data = day_type.to_dict()

    restored = DayType.from_dict(data)

    assert restored == day_type


def test_week_schedule_roundtrip(week_schedule):
    data = week_schedule.to_dict()

    restored = WeekSchedule.from_dict(data)

    assert restored == week_schedule


def test_cycle_roundtrip(cycle):
    data = cycle.to_dict()
    assert data["start_date"] == "2026-08-31"

    restored = Cycle.from_dict(data)

    assert restored == cycle
    assert restored.start_date == date(
        2026,
        8,
        31,
    )


def test_calendar_exception_roundtrip(calendar_exception):
    data = calendar_exception.to_dict()

    assert data["date"] == "2027-01-01"

    restored = CalendarException.from_dict(data)

    assert restored == calendar_exception


def test_time_definition_roundtrip():
    time_definition = TimeDefinition(
        fixed_time=time(8, 30),
    )

    data = time_definition.to_dict()

    assert data == {
        "fixed_time": "08:30:00",
    }

    restored = TimeDefinition.from_dict(data)

    assert restored == time_definition


def test_scheduled_moment_roundtrip():
    scheduled_moment = ScheduledMoment(
        moment_id="m1",
        time_definition=TimeDefinition(
            fixed_time=time(8, 30),
        ),
    )

    data = scheduled_moment.to_dict()

    assert data == {
        "moment_id": "m1",
        "time_definition": {
            "fixed_time": "08:30:00",
        },
    }

    restored = ScheduledMoment.from_dict(data)

    assert restored == scheduled_moment


def test_planner_configuration_empty():
    configuration = PlannerConfiguration.empty()

    assert configuration.moments == ()
    assert configuration.day_types == ()
    assert configuration.week_schedules == ()
    assert configuration.cycles == ()
    assert configuration.calendar_exceptions == ()


def test_planner_configuration_roundtrip(
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

    data = configuration.to_dict()

    restored = PlannerConfiguration.from_dict(data)

    assert restored == configuration


def test_planner_configuration_has_data(
    moment,
):
    empty = PlannerConfiguration.empty()

    assert empty.has_data() is False

    configuration = PlannerConfiguration(
        moments=(moment,),
        day_types=(),
        week_schedules=(),
        cycles=(),
        calendar_exceptions=(),
    )

    assert configuration.has_data() is True


def test_action():
    action = Action(
        id="salon_on",
        service="light.turn_on",
        data={"entity_id": "light.salon"},
    )

    assert action.service == "light.turn_on"
    assert action.data == {
        "entity_id": "light.salon",
    }


def test_audit():
    now = datetime.now()

    audit = Audit(
        created_by="user",
        created_at=now,
        modified_by="user",
        modified_at=now,
    )

    assert audit.created_by == "user"
    assert audit.created_at == now
    assert audit.modified_by == "user"
    assert audit.modified_at == now
