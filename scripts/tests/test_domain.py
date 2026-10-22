from dataclasses import replace
from datetime import date, datetime, time, timezone

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
        label="salon_on",
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
                "data": {
                    "brightness_pct": 50,
                },
            }
        ],
    )

    data = action.to_dict()

    assert data == {
        "id": "salon_on",
        "label": "salon_on",
        "sequence": [
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
                "data": {
                    "brightness_pct": 50,
                },
            }
        ],
    }

    restored = Action.from_dict(data)

    assert restored == action


def test_moment_with_actions_roundtrip():
    action = Action(
        id="salon_on",
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ],
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
                "label": "salon_on",
                "sequence": [
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
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
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ],
    )

    assert action.id == "salon_on"
    assert action.sequence == [
        {
            "action": "light.turn_on",
            "target": {
                "entity_id": "light.salon",
            },
        }
    ]


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


def test_action_label_defaults_to_id():
    action = Action(
        id="salon_on",
        sequence=[
            {
                "action": "light.turn_on",
            }
        ],
    )

    assert action.label == "salon_on"

    assert action.to_dict() == {
        "id": "salon_on",
        "label": "salon_on",
        "sequence": [
            {
                "action": "light.turn_on",
            }
        ],
    }


def test_action_from_dict_without_label_is_backward_compatible():
    action = Action.from_dict(
        {
            "id": "ouvrir_volets",
            "sequence": [
                {
                    "action": "cover.open_cover",
                }
            ],
        }
    )

    assert action.id == "ouvrir_volets"
    assert action.label == "ouvrir_volets"
    assert action.sequence == [
        {
            "action": "cover.open_cover",
        }
    ]


def test_audit_roundtrip():
    """Audit metadata serialization roundtrip."""

    from datetime import timezone

    created_at = datetime(
        2026,
        10,
        19,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        19,
        12,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="user_creation",
        created_at=created_at,
        modified_by="user_modification",
        modified_at=modified_at,
    )

    data = audit.to_dict()

    assert data == {
        "created_by": "user_creation",
        "created_at": "2026-10-19T10:00:00+00:00",
        "modified_by": "user_modification",
        "modified_at": "2026-10-19T12:00:00+00:00",
    }

    restored = Audit.from_dict(data)

    assert restored == audit


def test_day_type_with_audit_roundtrip():
    """DayType preserves audit metadata."""

    from datetime import timezone

    now = datetime(
        2026,
        10,
        19,
        10,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="admin",
        created_at=now,
        modified_by="admin",
        modified_at=now,
    )

    day_type = DayType(
        id="jour_travail",
        name="Jour de travail",
        scheduled_moments=(),
        audit=audit,
    )

    data = day_type.to_dict()

    assert data["audit"] == audit.to_dict()

    restored = DayType.from_dict(data)

    assert restored == day_type
    assert restored.audit == audit


def test_day_type_without_audit_backward_compatible():
    """Old DayType data without audit remains supported."""

    old_data = {
        "id": "jour_repos",
        "name": "Jour de repos",
        "scheduled_moments": [],
    }

    day_type = DayType.from_dict(old_data)

    assert day_type.audit is None
    assert day_type.to_dict() == old_data


def test_day_type_with_null_audit():
    """Explicit null audit is accepted."""

    data = {
        "id": "jour_repos",
        "name": "Jour de repos",
        "scheduled_moments": [],
        "audit": None,
    }

    day_type = DayType.from_dict(data)

    assert day_type.audit is None
    assert "audit" not in day_type.to_dict()


def test_moment_with_audit_roundtrip():
    """Moment audit metadata survives serialization."""

    created_at = datetime(
        2026,
        10,
        20,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        21,
        8,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="Utilisateur Test",
        created_at=created_at,
        modified_by="Administrateur",
        modified_at=modified_at,
    )

    moment = Moment(
        id="m1",
        name="Réveil",
        icon="mdi:alarm",
        actions=(),
        audit=audit,
    )

    data = moment.to_dict()

    assert data["audit"] == {
        "created_by": "Utilisateur Test",
        "created_at": created_at.isoformat(),
        "modified_by": "Administrateur",
        "modified_at": modified_at.isoformat(),
    }

    restored = Moment.from_dict(data)

    assert restored == moment
    assert restored.audit == audit


def test_moment_without_audit_backward_compatible():
    """Existing moments without audit remain supported."""

    old_data = {
        "id": "m1",
        "name": "Réveil",
        "icon": "mdi:alarm",
        "actions": [],
    }

    moment = Moment.from_dict(old_data)

    assert moment.audit is None
    assert moment.to_dict() == old_data

    # An explicitly null audit must also be accepted.
    data_with_null = {
        **old_data,
        "audit": None,
    }

    restored = Moment.from_dict(data_with_null)

    assert restored.audit is None
    assert "audit" not in restored.to_dict()


def test_week_schedule_with_audit_roundtrip(week_schedule):
    """WeekSchedule audit survives serialization."""

    created_at = datetime(
        2026,
        10,
        20,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        21,
        8,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="Utilisateur Test",
        created_at=created_at,
        modified_by="Administrateur",
        modified_at=modified_at,
    )

    schedule = replace(
        week_schedule,
        audit=audit,
    )

    data = schedule.to_dict()

    assert data["audit"] == {
        "created_by": "Utilisateur Test",
        "created_at": created_at.isoformat(),
        "modified_by": "Administrateur",
        "modified_at": modified_at.isoformat(),
    }

    restored = WeekSchedule.from_dict(data)

    assert restored == schedule
    assert restored.audit == audit

    # All seven day-type references must be preserved.
    assert restored.monday == week_schedule.monday
    assert restored.tuesday == week_schedule.tuesday
    assert restored.wednesday == week_schedule.wednesday
    assert restored.thursday == week_schedule.thursday
    assert restored.friday == week_schedule.friday
    assert restored.saturday == week_schedule.saturday
    assert restored.sunday == week_schedule.sunday


def test_week_schedule_without_audit_backward_compatible(
    week_schedule,
):
    """Existing WeekSchedule data without audit is supported."""

    old_data = week_schedule.to_dict()

    assert "audit" not in old_data

    restored = WeekSchedule.from_dict(old_data)

    assert restored == week_schedule
    assert restored.audit is None
    assert restored.to_dict() == old_data

    # Explicitly null audit is also supported.
    data_with_null = {
        **old_data,
        "audit": None,
    }

    restored = WeekSchedule.from_dict(data_with_null)

    assert restored.audit is None
    assert restored.to_dict() == old_data


def test_cycle_with_audit_roundtrip(cycle):
    """Cycle preserves audit metadata."""

    created_at = datetime(
        2026,
        10,
        20,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        21,
        8,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="Utilisateur Test",
        created_at=created_at,
        modified_by="Administrateur",
        modified_at=modified_at,
    )

    updated_cycle = replace(
        cycle,
        audit=audit,
    )

    data = updated_cycle.to_dict()

    assert data["audit"] == {
        "created_by": "Utilisateur Test",
        "created_at": created_at.isoformat(),
        "modified_by": "Administrateur",
        "modified_at": modified_at.isoformat(),
    }

    restored = Cycle.from_dict(data)

    assert restored == updated_cycle
    assert restored.audit == audit
    assert restored.start_date == cycle.start_date
    assert restored.week_schedule_ids == cycle.week_schedule_ids


def test_cycle_without_audit_backward_compatible(cycle):
    """Existing cycles without audit remain supported."""

    old_data = cycle.to_dict()

    assert "audit" not in old_data

    restored = Cycle.from_dict(old_data)

    assert restored == cycle
    assert restored.audit is None
    assert restored.to_dict() == old_data

    # Explicitly null audit remains supported.
    data_with_null = {
        **old_data,
        "audit": None,
    }

    restored = Cycle.from_dict(data_with_null)

    assert restored.audit is None
    assert restored.to_dict() == old_data


def test_calendar_exception_with_audit_roundtrip(
    calendar_exception,
):
    """CalendarException preserves audit metadata."""

    created_at = datetime(
        2026,
        10,
        20,
        10,
        0,
        tzinfo=timezone.utc,
    )
    modified_at = datetime(
        2026,
        10,
        21,
        8,
        0,
        tzinfo=timezone.utc,
    )

    audit = Audit(
        created_by="Utilisateur Test",
        created_at=created_at,
        modified_by="Administrateur",
        modified_at=modified_at,
    )

    exception = replace(
        calendar_exception,
        audit=audit,
    )

    data = exception.to_dict()

    assert data["audit"] == {
        "created_by": "Utilisateur Test",
        "created_at": created_at.isoformat(),
        "modified_by": "Administrateur",
        "modified_at": modified_at.isoformat(),
    }

    restored = CalendarException.from_dict(data)

    assert restored == exception
    assert restored.audit == audit

    assert restored.date == calendar_exception.date
    assert restored.day_type_id == calendar_exception.day_type_id
    assert restored.description == calendar_exception.description


def test_calendar_exception_without_audit_backward_compatible(
    calendar_exception,
):
    """Existing exceptions without audit remain supported."""

    old_data = calendar_exception.to_dict()

    assert "audit" not in old_data

    restored = CalendarException.from_dict(old_data)

    assert restored == calendar_exception
    assert restored.audit is None
    assert restored.to_dict() == old_data

    # Explicit null audit remains supported.
    data_with_null = {
        **old_data,
        "audit": None,
    }

    restored = CalendarException.from_dict(data_with_null)

    assert restored.audit is None
    assert restored.to_dict() == old_data
