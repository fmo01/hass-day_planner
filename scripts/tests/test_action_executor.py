import asyncio
from unittest.mock import AsyncMock, MagicMock, call

from homeassistant.core import HomeAssistant

from custom_components.day_planner.action_executor import ActionExecutor
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.moment import Moment


def test_execute_action():
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()

    executor = ActionExecutor(hass)

    action = Action(
        id="salon_on",
        service="light.turn_on",
        data={
            "entity_id": "light.salon",
            "brightness_pct": 50,
        },
    )

    asyncio.run(executor.async_execute_action(action))

    hass.services.async_call.assert_awaited_once_with(
        "light",
        "turn_on",
        {
            "entity_id": "light.salon",
            "brightness_pct": 50,
        },
        blocking=True,
    )


def test_execute_moment_actions():
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()

    executor = ActionExecutor(hass)

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(
            Action(
                id="salon_on",
                service="light.turn_on",
                data={
                    "entity_id": "light.salon",
                },
            ),
            Action(
                id="salon_off",
                service="switch.turn_off",
                data={
                    "entity_id": "switch.chauffage",
                },
            ),
        ),
    )

    asyncio.run(executor.async_execute_moment(moment))

    assert hass.services.async_call.await_count == 2

    hass.services.async_call.assert_has_awaits(
        [
            call(
                "light",
                "turn_on",
                {
                    "entity_id": "light.salon",
                },
                blocking=True,
            ),
            call(
                "switch",
                "turn_off",
                {
                    "entity_id": "switch.chauffage",
                },
                blocking=True,
            ),
        ]
    )


def test_execute_moment_without_actions():
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()

    executor = ActionExecutor(hass)

    moment = Moment(
        id="m1",
        name="Réveil",
        actions=(),
    )

    asyncio.run(executor.async_execute_moment(moment))

    hass.services.async_call.assert_not_awaited()
