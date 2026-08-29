import asyncio
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)
from homeassistant.config_entries import ConfigEntry

from custom_components.day_planner.const import (
    CONF_DELETE_DATA_ON_REMOVE,
    DEFAULT_DELETE_DATA_ON_REMOVE,
    DOMAIN,
    SIGNAL_PLANNER_UPDATED,
)

from custom_components.day_planner.options_flow import DayPlannerOptionsFlow


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

    hass.config_entries.async_get_known_entry.return_value = config_entry

    flow = DayPlannerOptionsFlow()

    flow.hass = hass
    flow.handler = config_entry.entry_id

    return flow

def test_options_flow_init_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(
            return_value={
                "type": "menu",
            }
        )

        result = await flow.async_step_init()

        flow.async_show_menu.assert_called_once_with(
            step_id="init",
            menu_options=[
                "moments",
                "day_types",
                "week_schedules",
                "cycles",
                "calendar_exceptions",
                "settings",
            ],
        )

        assert result == {
            "type": "menu",
        }

    asyncio.run(run())


def test_options_flow_moments_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(
            return_value={
                "type": "menu",
            }
        )

        result = await flow.async_step_moments()

        flow.async_show_menu.assert_called_once_with(
            step_id="moments",
            menu_options=[
                "add_moment",
                "edit_moment",
                "remove_moment",
            ],
        )

        assert result == {
            "type": "menu",
        }

    asyncio.run(run())


def test_options_flow_settings_form():
    async def run():
        flow = create_flow()

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_settings()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "settings"

        schema = call.kwargs["data_schema"]

        result_schema = schema({})

        assert (
            result_schema[
                CONF_DELETE_DATA_ON_REMOVE
            ]
            == DEFAULT_DELETE_DATA_ON_REMOVE
        )

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_settings_existing_value():
    async def run():
        flow = create_flow(
            {
                CONF_DELETE_DATA_ON_REMOVE: True,
            }
        )

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        await flow.async_step_settings()

        call = flow.async_show_form.call_args

        schema = call.kwargs["data_schema"]

        result_schema = schema({})

        assert (
            result_schema[
                CONF_DELETE_DATA_ON_REMOVE
            ]
            is True
        )

    asyncio.run(run())


def test_options_flow_settings_create_entry():
    async def run():
        flow = create_flow()

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        user_input = {
            CONF_DELETE_DATA_ON_REMOVE: True,
        }

        result = await flow.async_step_settings(
            user_input
        )

        flow.async_create_entry.assert_called_once_with(
            title="",
            data=user_input,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())

def test_options_flow_add_moment_form():
    async def run():
        flow = create_flow()

        flow.async_show_form = MagicMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_add_moment()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_moment"

        schema = call.kwargs["data_schema"]

        result_schema = schema(
            {
                "id": "wake_up",
                "name": "Réveil",
                "icon": "mdi:alarm",
            }
        )

        assert result_schema == {
            "id": "wake_up",
            "name": "Réveil",
            "icon": "mdi:alarm",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_moment_create():
    async def run():
        flow = create_flow()

        runtime = MagicMock()

        flow.config_entry.runtime_data = runtime

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        flow.async_create_entry = MagicMock(
            return_value={"type": "create_entry"}
        )

        user_input = {
            "id": "wake_up",
            "name": "Réveil",
            "icon": "mdi:alarm",
        }

        with patch(
            "custom_components.day_planner.options_flow."
            "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_moment(
                user_input
            )

        moment = runtime.engine.add_moment.call_args.args[0]

        assert moment.id == "wake_up"
        assert moment.name == "Réveil"
        assert moment.icon == "mdi:alarm"
        assert moment.actions == ()

        runtime.engine.add_moment.assert_called_once()

        runtime.storage.async_save.assert_awaited_once_with(
            configuration
        )

        runtime.resolver.update_configuration.assert_called_once_with(
            configuration
        )

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        flow.async_create_entry.assert_called_once_with(
            title="",
            data=flow.config_entry.options,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_moment_not_implemented():
    async def run():
        flow = create_flow()

        flow.async_abort = MagicMock(
            return_value={
                "type": "abort",
            }
        )

        result = await flow.async_step_edit_moment()

        flow.async_abort.assert_called_once_with(
            reason="not_implemented"
        )

        assert result == {
            "type": "abort",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_not_implemented():
    async def run():
        flow = create_flow()

        flow.async_abort = MagicMock(
            return_value={
                "type": "abort",
            }
        )

        result = await flow.async_step_remove_moment()

        flow.async_abort.assert_called_once_with(
            reason="not_implemented"
        )

        assert result == {
            "type": "abort",
        }

    asyncio.run(run())


