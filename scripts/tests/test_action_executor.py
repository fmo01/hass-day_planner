import asyncio
from unittest.mock import AsyncMock, MagicMock, call, patch

from homeassistant.core import HomeAssistant

from custom_components.day_planner.action_executor import ActionExecutor
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.moment import Moment


def test_execute_action():
    hass = MagicMock(spec=HomeAssistant)

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

    with patch(
        "custom_components.day_planner.action_executor.Script"
    ) as script_class:
        script = script_class.return_value
        script.async_run = AsyncMock()

        asyncio.run(
            executor.async_execute_action(
                action
            )
        )

    script_class.assert_called_once_with(
        hass,
        action.sequence,
        "Day Planner action: salon_on",
        "day_planner",
    )

    script.async_run.assert_awaited_once_with()


def test_execute_moment_actions():
    hass = MagicMock(spec=HomeAssistant)

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

    asyncio.run(
        executor.async_execute_moment(
            moment
        )
    )

    executor.async_execute_action.assert_has_awaits(
        [
            call(action_1),
            call(action_2),
        ]
    )

    assert (
        executor.async_execute_action.await_count
        == 2
    )


def test_execute_moment_without_actions():
    hass = MagicMock(spec=HomeAssistant)

    executor = ActionExecutor(hass)

    executor.async_execute_action = AsyncMock()

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(),
    )

    asyncio.run(
        executor.async_execute_moment(
            moment
        )
    )

    executor.async_execute_action.assert_not_awaited()


def test_execute_moment_continues_after_action_error():
    hass = MagicMock(spec=HomeAssistant)

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

    asyncio.run(
        executor.async_execute_moment(
            moment
        )
    )

    assert executor.async_execute_action.await_count == 2

    executor.async_execute_action.assert_has_awaits(
        [
            call(action_1),
            call(action_2),
        ]
    )
