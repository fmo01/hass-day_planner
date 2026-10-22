"""Verify Day Planner origin attribution and anomaly events in HA Logbook."""

from unittest.mock import MagicMock

from homeassistant.components.logbook import (LOGBOOK_ENTRY_MESSAGE,
                                              LOGBOOK_ENTRY_NAME,
                                              LOGBOOK_ENTRY_SOURCE)

from custom_components.day_planner.const import (
    DOMAIN, EVENT_DAY_PLANNER_ACTION, EVENT_DAY_PLANNER_ACTION_RESULT)
from custom_components.day_planner.logbook import async_describe_events


def test_logbook_origin_identifies_day_planner_action():
    register = MagicMock()
    async_describe_events(MagicMock(), register)

    assert register.call_count == 2
    origin = register.call_args_list[0].args
    result = register.call_args_list[1].args
    assert origin[:2] == (DOMAIN, EVENT_DAY_PLANNER_ACTION)
    assert result[:2] == (DOMAIN, EVENT_DAY_PLANNER_ACTION_RESULT)

    event = MagicMock()
    event.data = {
        "action_id": "XX1",
        "action_label": "XX1 test",
        "moment_name": "Retour Travail",
        "status": "started",
        "requested_service": "input_boolean.turn_off → input_boolean.day_planner_test",
    }
    described = origin[2](event)
    assert "Day Planner" in described[LOGBOOK_ENTRY_NAME]
    assert "XX1" in described[LOGBOOK_ENTRY_NAME]
    assert "XX1 test" in described[LOGBOOK_ENTRY_MESSAGE]
    assert "Retour Travail" in described[LOGBOOK_ENTRY_MESSAGE]
    assert "input_boolean.turn_off" in described[LOGBOOK_ENTRY_MESSAGE]
    assert "input_boolean.day_planner_test" in described[LOGBOOK_ENTRY_MESSAGE]
    assert "XX1" in described[LOGBOOK_ENTRY_SOURCE]

    event.data = {
        "action_id": "a2",
        "status": "missing_targets",
        "missing_entities": ["switch.cuisine"],
    }
    assert "switch.cuisine" in result[2](event)[LOGBOOK_ENTRY_MESSAGE]
    event.data = {"action_id": "a3", "status": "failed"}
    assert "échec" in result[2](event)[LOGBOOK_ENTRY_MESSAGE]


def test_logbook_origin_without_service_target_or_parent():
    """Origin/source describes Day Planner; it does not create a parent cause."""
    register = MagicMock()
    async_describe_events(MagicMock(), register)
    describe = register.call_args_list[0].args[2]

    event = MagicMock()
    event.data = {"action_id": "XX1", "action_label": "XX1"}
    entry = describe(event)
    assert entry[LOGBOOK_ENTRY_NAME] == "Day Planner — action XX1"
    assert entry[LOGBOOK_ENTRY_SOURCE] == "Day Planner — action XX1"
    assert entry[LOGBOOK_ENTRY_MESSAGE] == "a déclenché l'action 'XX1'"
    assert "context" not in entry  # HA Context is supplied when firing the event.


def test_logbook_result_is_not_an_origin_source():
    """A warning/failure log entry does not displace the initial origin."""
    register = MagicMock()
    async_describe_events(MagicMock(), register)
    describe_result = register.call_args_list[1].args[2]

    event = MagicMock()
    event.data = {"action_id": "XX1", "status": "missing_targets"}
    entry = describe_result(event)
    assert "cible(s) signalée(s) par Home Assistant" in entry[LOGBOOK_ENTRY_MESSAGE]
    assert LOGBOOK_ENTRY_SOURCE not in entry
