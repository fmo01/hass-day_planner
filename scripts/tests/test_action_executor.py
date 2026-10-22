import asyncio
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from homeassistant.core import Context, HomeAssistant

from custom_components.day_planner.action_executor import ActionExecutor
from custom_components.day_planner.const import (
    EVENT_DAY_PLANNER_ACTION, EVENT_DAY_PLANNER_ACTION_RESULT)
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.moment import Moment


def test_execute_action():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()

    executor = ActionExecutor(hass)

    action = Action(
        id="salon_on",
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

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script = script_class.return_value
        script.async_run = AsyncMock()

        asyncio.run(executor.async_execute_action(action))

    script_class.assert_called_once_with(
        hass,
        action.sequence,
        "Day Planner action: salon_on",
        "day_planner",
    )

    script.async_run.assert_awaited_once()
    assert isinstance(script.async_run.await_args.kwargs["context"], Context)


def test_execute_moment_actions():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()

    executor = ActionExecutor(hass)

    action_1 = Action(
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

    action_2 = Action(
        id="chauffage_off",
        sequence=[
            {
                "action": "switch.turn_off",
                "target": {
                    "entity_id": "switch.chauffage",
                },
            }
        ],
    )

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            action_1,
            action_2,
        ),
    )

    executor.async_execute_action = AsyncMock()

    asyncio.run(executor.async_execute_moment(moment))

    executor.async_execute_action.assert_has_awaits(
        [
            call(action_1, moment=moment),
            call(action_2, moment=moment),
        ]
    )

    assert executor.async_execute_action.await_count == 2


def test_execute_moment_without_actions():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()

    executor = ActionExecutor(hass)

    executor.async_execute_action = AsyncMock()

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(),
    )

    asyncio.run(executor.async_execute_moment(moment))

    executor.async_execute_action.assert_not_awaited()


def test_execute_moment_continues_after_action_error():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()

    executor = ActionExecutor(hass)

    action_1 = Action(
        id="action_1",
        sequence=[
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ],
    )

    action_2 = Action(
        id="action_2",
        sequence=[
            {
                "action": "switch.turn_on",
                "target": {
                    "entity_id": "switch.test",
                },
            }
        ],
    )

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            action_1,
            action_2,
        ),
    )

    executor.async_execute_action = AsyncMock(
        side_effect=[
            RuntimeError("Action failed"),
            None,
        ]
    )

    asyncio.run(executor.async_execute_moment(moment))

    assert executor.async_execute_action.await_count == 2

    executor.async_execute_action.assert_has_awaits(
        [
            call(action_1, moment=moment),
            call(action_2, moment=moment),
        ]
    )


def test_missing_entities_are_logged_as_day_planner_errors(caplog):
    """HA warns and does not necessarily raise for an unavailable target."""
    import logging

    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    hass.states.get.side_effect = [None, MagicMock(state="unavailable")]
    executor = ActionExecutor(hass)
    action = Action(
        id="volets",
        sequence=[
            {
                "action": "switch.turn_on",
                "target": {
                    "entity_id": [
                        "switch.cmd_5_volet_cuisine_cuisine",
                        "switch.cmd_1_volet_sejour_salle_a_manger",
                    ]
                },
            }
        ],
    )
    moment = Moment(id="m1", name="Réveil", actions=(action,))

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock()
        with caplog.at_level(
            logging.ERROR, logger="custom_components.day_planner.action_executor"
        ):
            asyncio.run(executor.async_execute_moment(moment))

    assert "switch.cmd_5_volet_cuisine_cuisine" in caplog.text
    assert "switch.cmd_1_volet_sejour_salle_a_manger" in caplog.text
    assert "moment='Réveil'" in caplog.text
    assert script_class.return_value.async_run.await_count == 1
    assert hass.bus.async_fire.call_args.args[0] == EVENT_DAY_PLANNER_ACTION_RESULT
    assert hass.bus.async_fire.call_args.args[1]["status"] == "missing_targets"
    assert len(hass.bus.async_fire.call_args.args[1]["missing_entities"]) == 2


def test_templates_and_nested_choose_do_not_report_false_missing_targets(caplog):
    import logging

    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    executor = ActionExecutor(hass)
    action = Action(
        id="conditionnelle",
        sequence=[
            {
                "choose": [
                    {
                        "conditions": [],
                        "sequence": [
                            {
                                "action": "switch.turn_on",
                                "target": {"entity_id": "switch.not_executed"},
                            }
                        ],
                    }
                ]
            },
            {
                "action": "switch.turn_on",
                "target": {"entity_id": "{{ states('input_text.target') }}"},
            },
        ],
    )
    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock()
        with caplog.at_level(
            logging.ERROR, logger="custom_components.day_planner.action_executor"
        ):
            asyncio.run(executor.async_execute_action(action))

    assert not caplog.records
    hass.states.get.assert_not_called()
    assert hass.bus.async_fire.call_args.args[0] == EVENT_DAY_PLANNER_ACTION
    assert hass.bus.async_fire.call_args.args[1]["status"] == "started"


def test_action_error_emits_failure_event_and_next_action_runs():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    executor = ActionExecutor(hass)
    a = Action(id="bad", sequence=[])
    b = Action(id="good", sequence=[])
    moment = Moment(id="m", name="Matin", actions=(a, b))

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock(
            side_effect=[ValueError("broken"), None]
        )
        asyncio.run(executor.async_execute_moment(moment))

    assert script_class.return_value.async_run.await_count == 2
    statuses = [call_.args[1]["status"] for call_ in hass.bus.async_fire.call_args_list]
    assert statuses == ["started", "failed", "started"]
    assert [call_.args[0] for call_ in hass.bus.async_fire.call_args_list] == [
        EVENT_DAY_PLANNER_ACTION,
        EVENT_DAY_PLANNER_ACTION_RESULT,
        EVENT_DAY_PLANNER_ACTION,
    ]
    assert all(
        "context" in call_.kwargs for call_ in hass.bus.async_fire.call_args_list
    )


def test_home_assistant_target_warning_is_mirrored_as_day_planner_error(caplog):
    """Catch an HA warning that does not raise, even with a dynamic target."""
    import logging

    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    executor = ActionExecutor(hass)
    action = Action(
        id="volet_templated",
        sequence=[
            {
                "action": "switch.turn_on",
                "target": {"entity_id": "{{ variables.target }}"},
            }
        ],
    )

    async def fake_script_run(**kwargs):
        logging.getLogger("homeassistant.helpers.service").warning(
            "Referenced entities switch.cmd_5_volet_cuisine_cuisine "
            "are missing or not currently available"
        )

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock(side_effect=fake_script_run)
        with caplog.at_level(
            logging.ERROR, logger="custom_components.day_planner.action_executor"
        ):
            asyncio.run(executor.async_execute_action(action))

    assert "Referenced entities switch.cmd_5_volet_cuisine_cuisine" in caplog.text
    assert hass.bus.async_fire.call_args.args[0] == EVENT_DAY_PLANNER_ACTION_RESULT
    assert hass.bus.async_fire.call_args.args[1]["status"] == "missing_targets"
    assert len(hass.bus.async_fire.call_args.args[1]["ha_warnings"]) == 1


def test_logbook_origin_precedes_turn_off_and_uses_same_context():
    """Service-origin metadata must precede the state transition in Logbook."""
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    history = []

    def record_bus(event_type, payload, *, context):
        history.append(("bus", event_type, payload, context))

    hass.bus.async_fire.side_effect = record_bus
    action = Action(
        id="XX1",
        label="XX1 test",
        sequence=[
            {
                "action": "input_boolean.turn_off",
                "target": {"entity_id": "input_boolean.day_planner_test"},
            }
        ],
    )
    moment = Moment(id="return_work", name="Retour Travail", actions=(action,))

    async def fake_run(**kwargs):
        # Real HA Script passes this context to hass.services.async_call.
        history.append(("service", "input_boolean.turn_off", kwargs["context"]))

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock(side_effect=fake_run)
        asyncio.run(ActionExecutor(hass).async_execute_moment(moment))

    assert len(history) == 2  # No redundant success event
    assert history[0][0:2] == ("bus", EVENT_DAY_PLANNER_ACTION)
    assert history[0][2]["action_id"] == "XX1"
    assert history[0][2]["status"] == "started"
    assert history[0][2]["moment_name"] == "Retour Travail"
    assert history[0][2]["requested_service"] == (
        "input_boolean.turn_off → input_boolean.day_planner_test"
    )
    assert history[1][0:2] == ("service", "input_boolean.turn_off")
    assert history[0][3] is history[1][2]


def test_origin_remains_first_when_action_fails():
    """A later failure event must not displace the origin context."""
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    history = []
    hass.bus.async_fire.side_effect = lambda event, data, *, context: history.append(
        (event, context)
    )
    action = Action(id="XX1", sequence=[])

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock(
            side_effect=RuntimeError("erreur")
        )
        import pytest

        with pytest.raises(RuntimeError):
            asyncio.run(ActionExecutor(hass).async_execute_action(action))

    assert [e for e, _ in history] == [
        EVENT_DAY_PLANNER_ACTION,
        EVENT_DAY_PLANNER_ACTION_RESULT,
    ]
    assert history[0][1] is history[1][1]


def test_warning_handler_filters_context_logger_and_message():
    """Only a matching HA target warning in this action's context is mirrored."""
    import logging

    from custom_components.day_planner.action_executor import (
        _ACTIVE_ACTION, _HAServiceWarningHandler)

    marker = object()
    handler = _HAServiceWarningHandler(marker, Action(id="XX1", sequence=[]), None)
    missing_warning = (
        "Referenced entities switch.cuisine " "are missing or not currently available"
    )

    def make_record(logger_name, message):
        return logging.LogRecord(
            name=logger_name,
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg=message,
            args=(),
            exc_info=None,
        )

    valid_record = make_record("homeassistant.helpers.service", missing_warning)
    token = _ACTIVE_ACTION.set(object())
    try:
        # An action running in another asynchronous context is not ours.
        handler.emit(valid_record)
        assert handler.messages == []
    finally:
        _ACTIVE_ACTION.reset(token)

    token = _ACTIVE_ACTION.set(marker)
    try:
        handler.emit(make_record("homeassistant.helpers.other", missing_warning))
        handler.emit(make_record("homeassistant.helpers.service", "Service called"))
        handler.emit(
            make_record(
                "homeassistant.helpers.service", "Referenced entities switch.cuisine"
            )
        )
        assert handler.messages == []

        with patch(
            "custom_components.day_planner.action_executor._LOGGER.error"
        ) as error:
            handler.emit(valid_record)
        assert handler.messages == [missing_warning]
        error.assert_called_once()
        assert error.call_args.args[1] == "XX1"
        assert error.call_args.args[2] == "exécution directe"
    finally:
        _ACTIVE_ACTION.reset(token)


@pytest.mark.parametrize(
    "sequence",
    [
        [None],  # Non-mapping step: no interpretable requested service.
        [{"action": "turn_off", "target": {"entity_id": "light.salon"}}],
        [
            {
                "action": "light.turn_off",
                "target": {"entity_id": "light.salon", "area_id": "salon"},
            }
        ],
        [{"action": "light.turn_off", "target": {"entity_id": "incorrect"}}],
    ],
    ids=["non_mapping", "invalid_service", "extra_target", "invalid_entity_id"],
)
def test_requested_service_does_not_invent_ambiguous_details(sequence):
    """A logbook description must not claim unsupported service targets."""
    from custom_components.day_planner.action_executor import \
        _simple_requested_service

    assert _simple_requested_service(Action(id="XX1", sequence=sequence)) is None


def test_static_check_skips_unstructured_steps_and_reports_duplicate_once(caplog):
    """Repeated missing targets are reported once, with stable event contents."""
    import logging

    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.bus = MagicMock()
    hass.states.get.return_value = None
    action = Action(
        id="XX1",
        sequence=[
            None,  # Defensive path (invalid input should not break the pre-check).
            {
                "action": "switch.turn_on",
                "target": {"entity_id": ["switch.cuisine", "switch.cuisine"]},
            },
            {"action": "switch.turn_on", "data": {"entity_id": "switch.cuisine"}},
        ],
    )

    with patch("custom_components.day_planner.action_executor.Script") as script_class:
        script_class.return_value.async_run = AsyncMock()
        with caplog.at_level(
            logging.ERROR, logger="custom_components.day_planner.action_executor"
        ):
            asyncio.run(ActionExecutor(hass).async_execute_action(action))

    assert hass.states.get.call_count == 2
    assert (
        len(
            [
                record
                for record in caplog.records
                if record.name == "custom_components.day_planner.action_executor"
            ]
        )
        == 1
    )
    assert hass.bus.async_fire.call_args.args[0] == EVENT_DAY_PLANNER_ACTION_RESULT
    assert hass.bus.async_fire.call_args.args[1]["missing_entities"] == [
        "switch.cuisine"
    ]
