from unittest.mock import MagicMock

import asyncio

from homeassistant.config_entries import ConfigEntry

from custom_components.day_planner.options_flow import (
    DayPlannerOptionsFlow,
)
from custom_components.day_planner.const import (
    DOMAIN,
    CONF_DELETE_DATA_ON_REMOVE,
    DEFAULT_DELETE_DATA_ON_REMOVE,
)


def create_flow(options=None):
    config_entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Day Planner",
        data={},
        source="user",
        options=options or {},
        entry_id="test_entry",
        discovery_keys={},
        subentries_data={},
        unique_id=None,
    )

    hass = MagicMock()

    hass.config_entries.async_get_known_entry.return_value = (
        config_entry
    )

    flow = DayPlannerOptionsFlow()

    flow.hass = hass
    flow.handler = config_entry.entry_id

    return flow


def test_options_flow_show_form():
    async def run():
        flow = create_flow()

        flow.async_show_form = MagicMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_init()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "init"

        schema = call.kwargs["data_schema"]

        result_schema = schema({})

        assert (
            result_schema[CONF_DELETE_DATA_ON_REMOVE]
            == DEFAULT_DELETE_DATA_ON_REMOVE
        )

        assert result == {
            "type": "form"
        }

    asyncio.run(run())


def test_options_flow_create_entry():
    async def run():
        flow = create_flow()

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
                "data": {
                    CONF_DELETE_DATA_ON_REMOVE: True,
                },
            }
        )

        user_input = {
            CONF_DELETE_DATA_ON_REMOVE: True,
        }

        result = await flow.async_step_init(
            user_input
        )

        flow.async_create_entry.assert_called_once_with(
            title="",
            data=user_input,
        )

        assert result == {
            "type": "create_entry",
            "data": user_input,
        }

    asyncio.run(run())
