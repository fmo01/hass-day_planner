import asyncio
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry

from custom_components.day_planner.const import (CONF_DELETE_DATA_ON_REMOVE,
                                                 CONF_MAX_CYCLES,
                                                 DEFAULT_DELETE_DATA_ON_REMOVE,
                                                 DEFAULT_MAX_CYCLES, DOMAIN,
                                                 SIGNAL_PLANNER_UPDATED)
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.calendar_exception import \
    CalendarException
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_moment import \
    ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.week_schedule import WeekSchedule
from custom_components.day_planner.options_flow import DayPlannerOptionsFlow
from custom_components.day_planner.planner.errors import ValidationError


def create_flow(
    options=None,
    runtime=None,
):
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

    if runtime is not None:
        config_entry.runtime_data = runtime

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
                "moment_actions",
            ],
        )

        assert result == {
            "type": "menu",
        }

    asyncio.run(run())


def test_options_flow_settings_max_cycles_too_small():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = (
            MagicMock(),
            MagicMock(),
        )

        flow = create_flow(
            {
                CONF_DELETE_DATA_ON_REMOVE: False,
                CONF_MAX_CYCLES: 2,
            },
            runtime=runtime,
        )

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        flow.async_create_entry = MagicMock()

        result = await flow.async_step_settings(
            {
                CONF_DELETE_DATA_ON_REMOVE: False,
                CONF_MAX_CYCLES: 1,
            }
        )

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "settings"

        assert call.kwargs["errors"] == {
            "base": "max_cycles_too_small",
        }

        assert call.kwargs["description_placeholders"] == {
            "value": "1",
            "minimum": "2",
        }

        flow.async_create_entry.assert_not_called()

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_settings_form():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = ()

        flow = create_flow(
            runtime=runtime,
        )

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
            result_schema[CONF_DELETE_DATA_ON_REMOVE] == DEFAULT_DELETE_DATA_ON_REMOVE
        )

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_settings_existing_value():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = ()

        flow = create_flow(
            {
                CONF_DELETE_DATA_ON_REMOVE: True,
                CONF_MAX_CYCLES: 3,
            },
            runtime=runtime,
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

        assert result_schema[CONF_DELETE_DATA_ON_REMOVE] is True

        assert result_schema[CONF_MAX_CYCLES] == 3

    asyncio.run(run())


def test_options_flow_settings_create_entry():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = ()

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        user_input = {
            CONF_DELETE_DATA_ON_REMOVE: True,
        }

        result = await flow.async_step_settings(user_input)

        flow.async_create_entry.assert_called_once_with(
            title="",
            data={
                CONF_DELETE_DATA_ON_REMOVE: True,
                CONF_MAX_CYCLES: DEFAULT_MAX_CYCLES,
            },
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())


def test_options_flow_add_moment_form():
    async def run():
        flow = create_flow()

        flow.async_show_form = MagicMock(return_value={"type": "form"})

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

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        user_input = {
            "id": "wake_up",
            "name": "Réveil",
            "icon": "mdi:alarm",
        }

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_moment(user_input)

        moment = runtime.engine.add_moment.call_args.args[0]

        assert moment.id == "wake_up"
        assert moment.name == "Réveil"
        assert moment.icon == "mdi:alarm"
        assert moment.actions == ()

        runtime.engine.add_moment.assert_called_once()

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

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


def test_options_flow_remove_moment_form():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.configuration.moments = (moment,)

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_remove_moment()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_moment"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "wake_up",
            }
        )

        assert validated["id"] == "wake_up"

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_edit_moment_form():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.configuration.moments = (moment,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_moment()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_moment"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "wake_up",
            }
        )

        assert validated["id"] == "wake_up"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_select():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_step_edit_moment_details = AsyncMock(return_value={"type": "form"})

        result = await flow.async_step_edit_moment(
            {
                "id": "wake_up",
            }
        )

        assert flow._selected_moment_id == "wake_up"

        flow.async_step_edit_moment_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_details_create():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        existing_action = Action(
            id="salon_on",
            service="light.turn_on",
            data={
                "entity_id": "light.salon",
            },
        )

        current_moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(existing_action,),
        )

        runtime.engine.get_moment.return_value = current_moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_moment_details(
                {
                    "name": "Réveil modifié",
                    "icon": "mdi:coffee",
                }
            )

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == "wake_up"
        assert updated.name == "Réveil modifié"
        assert updated.icon == "mdi:coffee"

        # Important : les actions existantes doivent être conservées.
        assert updated.actions == (existing_action,)

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())


def test_options_flow_edit_moment_details_form():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        flow._selected_moment_id = "wake_up"

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_edit_moment_details()

        runtime.engine.get_moment.assert_called_once_with("wake_up")

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_moment_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["name"] == "Réveil"
        assert validated["icon"] == "mdi:alarm"

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_confirm_form():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        flow._selected_remove_moment_id = "wake_up"

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_remove_moment_confirm()

        runtime.engine.get_moment.assert_called_once_with("wake_up")

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_moment_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Réveil",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_not_confirmed():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        flow._selected_remove_moment_id = "wake_up"

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_remove_moment_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_moment.assert_not_called()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_moment_confirm"

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_confirmed():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_remove_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_moment_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_moment.assert_called_once_with("wake_up")

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_select():
    async def run():
        runtime = MagicMock()

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_step_remove_moment_confirm = AsyncMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_remove_moment(
            {
                "id": "wake_up",
            }
        )

        assert flow._selected_remove_moment_id == "wake_up"

        flow.async_step_remove_moment_confirm.assert_awaited_once_with()

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_day_types_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_day_types()

        flow.async_show_menu.assert_called_once_with(
            step_id="day_types",
            menu_options=[
                "add_day_type",
                "edit_day_type",
                "remove_day_type",
                "scheduled_moments",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_day_type_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_day_type()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_day_type"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "work",
                "name": "Travail",
            }
        )

        assert validated == {
            "id": "work",
            "name": "Travail",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_day_type_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_day_type(
                {
                    "id": "work",
                    "name": "Travail",
                }
            )

        day_type = runtime.engine.add_day_type.call_args.args[0]

        assert day_type.id == "work"
        assert day_type.name == "Travail"
        assert day_type.scheduled_moments == ()

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_day_type_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.configuration.day_types = (day_type,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_day_type()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_day_type"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "work",
            }
        )

        assert validated["id"] == "work"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_day_type_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_edit_day_type_details = AsyncMock(return_value={"type": "form"})

        result = await flow.async_step_edit_day_type(
            {
                "id": "work",
            }
        )

        assert flow._selected_day_type_id == "work"

        flow.async_step_edit_day_type_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_day_type_details_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow._selected_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_day_type_details()

        runtime.engine.get_day_type.assert_called_once_with("work")

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_day_type_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["name"] == "Travail"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_day_type_details_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        scheduled_moments = (MagicMock(),)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=scheduled_moments,
        )

        runtime.engine.get_day_type.return_value = day_type

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_day_type_id = "work"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_day_type_details(
                {
                    "name": "Travail modifié",
                }
            )

        updated = runtime.engine.update_day_type.call_args.args[0]

        assert updated.id == "work"
        assert updated.name == "Travail modifié"
        assert updated.scheduled_moments == scheduled_moments

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_day_type_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.configuration.day_types = (day_type,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_day_type()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_day_type"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "work",
            }
        )

        assert validated["id"] == "work"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_day_type_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_remove_day_type_confirm = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_remove_day_type(
            {
                "id": "work",
            }
        )

        assert flow._selected_remove_day_type_id == "work"

        flow.async_step_remove_day_type_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_day_type_confirm_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow._selected_remove_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_day_type_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_day_type_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Travail",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_day_type_not_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow._selected_remove_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_day_type_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_day_type.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_day_type_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_remove_day_type_id = "work"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_day_type_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_day_type.assert_called_once_with("work")

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_scheduled_moments_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.configuration.day_types = (day_type,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_scheduled_moments()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "scheduled_moments"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "day_type_id": "work",
            }
        )

        assert validated["day_type_id"] == "work"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_scheduled_moments_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_scheduled_moments_menu = AsyncMock(
            return_value={"type": "menu"}
        )

        result = await flow.async_step_scheduled_moments(
            {
                "day_type_id": "work",
            }
        )

        assert flow._selected_scheduled_day_type_id == "work"

        flow.async_step_scheduled_moments_menu.assert_awaited_once_with()

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_scheduled_moments_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_scheduled_moments_menu()

        flow.async_show_menu.assert_called_once_with(
            step_id="scheduled_moments_menu",
            menu_options=[
                "add_scheduled_moment",
                "edit_scheduled_moment",
                "remove_scheduled_moment",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_scheduled_moment_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.configuration.moments = (moment,)

        flow._selected_scheduled_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_scheduled_moment()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_scheduled_moment"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "moment_id": "wake_up",
                "time": "07:30:00",
            }
        )

        assert validated["moment_id"] == "wake_up"
        assert validated["time"] == "07:30:00"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_scheduled_moment_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow._selected_scheduled_day_type_id = "work"

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_scheduled_moment(
                {
                    "moment_id": "wake_up",
                    "time": "07:30:00",
                }
            )

        args = runtime.engine.add_scheduled_moment.call_args.args

        assert args[0] == "work"

        scheduled = args[1]

        assert scheduled.moment_id == "wake_up"
        assert scheduled.time_definition.fixed_time == time(7, 30)

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_scheduled_moment_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        scheduled = ScheduledMoment(
            moment_id="wake_up",
            time_definition=TimeDefinition(
                fixed_time=time(7, 30),
            ),
        )

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(scheduled,),
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.get_day_type.return_value = day_type

        runtime.engine.configuration.moments = (moment,)

        flow._selected_scheduled_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_scheduled_moment()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_scheduled_moment"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "moment_id": "wake_up",
            }
        )

        assert validated["moment_id"] == "wake_up"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_scheduled_moment_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow._selected_scheduled_day_type_id = "work"

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow.async_step_edit_scheduled_moment_details = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_edit_scheduled_moment(
            {
                "moment_id": "wake_up",
            }
        )

        assert flow._selected_scheduled_moment_id == "wake_up"

        flow.async_step_edit_scheduled_moment_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_scheduled_moment_details_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        scheduled = ScheduledMoment(
            moment_id="wake_up",
            time_definition=TimeDefinition(
                fixed_time=time(7, 30),
            ),
        )

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(scheduled,),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_scheduled_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_scheduled_moment_details()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_scheduled_moment_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["time"] == "07:30:00"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_scheduled_moment_details_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        scheduled = ScheduledMoment(
            moment_id="wake_up",
            time_definition=TimeDefinition(
                fixed_time=time(7, 30),
            ),
        )

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(scheduled,),
        )

        runtime.engine.get_day_type.return_value = day_type

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_scheduled_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_scheduled_moment_details(
                {
                    "time": "08:15:00",
                }
            )

        args = runtime.engine.update_scheduled_moment.call_args.args

        assert args[0] == "work"

        updated = args[1]

        assert updated.moment_id == "wake_up"
        assert updated.time_definition.fixed_time == time(8, 15)

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_scheduled_moment_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        scheduled = ScheduledMoment(
            moment_id="wake_up",
            time_definition=TimeDefinition(
                fixed_time=time(7, 30),
            ),
        )

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(scheduled,),
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.get_day_type.return_value = day_type

        runtime.engine.configuration.moments = (moment,)

        flow._selected_scheduled_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_scheduled_moment()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_scheduled_moment"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "moment_id": "wake_up",
            }
        )

        assert validated["moment_id"] == "wake_up"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_scheduled_moment_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow._selected_scheduled_day_type_id = "work"

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type

        flow.async_step_remove_scheduled_moment_confirm = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_remove_scheduled_moment(
            {
                "moment_id": "wake_up",
            }
        )

        assert flow._selected_remove_scheduled_moment_id == "wake_up"

        flow.async_step_remove_scheduled_moment_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_scheduled_moment_confirm_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.get_moment.return_value = moment

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_remove_scheduled_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_scheduled_moment_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_scheduled_moment_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Réveil",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_scheduled_moment_not_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.get_moment.return_value = moment

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_remove_scheduled_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_scheduled_moment_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_scheduled_moment.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_scheduled_moment_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        moment = Moment(
            id="wake_up",
            name="Réveil",
        )

        runtime.engine.get_moment.return_value = moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_remove_scheduled_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_scheduled_moment_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_scheduled_moment.assert_called_once_with(
            "work",
            "wake_up",
        )

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_day_type_in_use():
    async def run():
        runtime = MagicMock()
        runtime.storage.async_save = AsyncMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.get_day_type.return_value = day_type
        runtime.engine.remove_day_type.side_effect = ValidationError(
            "Cannot remove a day type used by a week schedule"
        )

        flow._selected_remove_day_type_id = "work"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_day_type_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_day_type.assert_called_once_with("work")

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_day_type_confirm"

        assert call.kwargs["errors"] == {
            "base": "day_type_in_use",
        }

        assert call.kwargs["description_placeholders"] == {
            "name": "Travail",
        }

        runtime.storage.async_save.assert_not_awaited()

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_week_schedules_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_week_schedules()

        flow.async_show_menu.assert_called_once_with(
            step_id="week_schedules",
            menu_options=[
                "add_week_schedule",
                "edit_week_schedule",
                "remove_week_schedule",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_week_schedule_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        work = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        weekend = DayType(
            id="weekend",
            name="Week-end",
            scheduled_moments=(),
        )

        runtime.engine.configuration.day_types = (
            work,
            weekend,
        )

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_week_schedule()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_week_schedule"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "week1",
                "name": "Semaine 1",
                "monday": "work",
                "tuesday": "work",
                "wednesday": "work",
                "thursday": "work",
                "friday": "work",
                "saturday": "weekend",
                "sunday": "weekend",
            }
        )

        assert validated["id"] == "week1"
        assert validated["monday"] == "work"
        assert validated["sunday"] == "weekend"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_week_schedule_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_week_schedule(
                {
                    "id": "week1",
                    "name": "Semaine 1",
                    "monday": "work",
                    "tuesday": "work",
                    "wednesday": "work",
                    "thursday": "work",
                    "friday": "work",
                    "saturday": "weekend",
                    "sunday": "weekend",
                }
            )

        week_schedule = runtime.engine.add_week_schedule.call_args.args[0]

        assert week_schedule.id == "week1"
        assert week_schedule.name == "Semaine 1"
        assert week_schedule.monday == "work"
        assert week_schedule.sunday == "weekend"

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_week_schedule_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.configuration.week_schedules = (week_schedule,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_week_schedule()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_week_schedule"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "week1",
            }
        )

        assert validated["id"] == "week1"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_week_schedule_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_edit_week_schedule_details = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_edit_week_schedule(
            {
                "id": "week1",
            }
        )

        assert flow._selected_week_schedule_id == "week1"

        flow.async_step_edit_week_schedule_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_week_schedule_details_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        runtime.engine.configuration.day_types = (
            DayType(
                id="work",
                name="Travail",
                scheduled_moments=(),
            ),
            DayType(
                id="weekend",
                name="Week-end",
                scheduled_moments=(),
            ),
        )

        flow._selected_week_schedule_id = "week1"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_week_schedule_details()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_week_schedule_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["name"] == "Semaine 1"
        assert validated["monday"] == "work"
        assert validated["saturday"] == "weekend"
        assert validated["sunday"] == "weekend"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_week_schedule_details_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_week_schedule_id = "week1"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_week_schedule_details(
                {
                    "name": "Semaine modifiée",
                    "monday": "work",
                    "tuesday": "work",
                    "wednesday": "work",
                    "thursday": "work",
                    "friday": "work",
                    "saturday": "weekend",
                    "sunday": "weekend",
                }
            )

        updated = runtime.engine.update_week_schedule.call_args.args[0]

        assert updated.id == "week1"
        assert updated.name == "Semaine modifiée"
        assert updated.monday == "work"
        assert updated.sunday == "weekend"

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.configuration.week_schedules = (week_schedule,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_week_schedule()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_week_schedule"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "week1",
            }
        )

        assert validated["id"] == "week1"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_remove_week_schedule_confirm = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_remove_week_schedule(
            {
                "id": "week1",
            }
        )

        assert flow._selected_remove_week_schedule_id == "week1"

        flow.async_step_remove_week_schedule_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_confirm_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        flow._selected_remove_week_schedule_id = "week1"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_week_schedule_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_week_schedule_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Semaine 1",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_not_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        flow._selected_remove_week_schedule_id = "week1"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_week_schedule_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_week_schedule.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_remove_week_schedule_id = "week1"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_week_schedule_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_week_schedule.assert_called_once_with("week1")

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_in_use():
    async def run():
        runtime = MagicMock()
        runtime.storage.async_save = AsyncMock()

        flow = create_flow(runtime=runtime)

        week_schedule = WeekSchedule(
            id="week1",
            name="Semaine 1",
            monday="work",
            tuesday="work",
            wednesday="work",
            thursday="work",
            friday="work",
            saturday="weekend",
            sunday="weekend",
        )

        runtime.engine.get_week_schedule.return_value = week_schedule

        runtime.engine.remove_week_schedule.side_effect = ValidationError(
            "Cannot remove a week schedule used by a cycle"
        )

        flow._selected_remove_week_schedule_id = "week1"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_week_schedule_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_week_schedule.assert_called_once_with("week1")

        call = flow.async_show_form.call_args

        assert call.kwargs["errors"] == {
            "base": "week_schedule_in_use",
        }

        assert call.kwargs["description_placeholders"] == {
            "name": "Semaine 1",
        }

        runtime.storage.async_save.assert_not_awaited()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_cycles_menu():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = ()
        runtime.engine.max_cycles = 1

        flow = create_flow(
            runtime=runtime,
        )
        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_cycles()

        flow.async_show_menu.assert_called_once_with(
            step_id="cycles",
            menu_options=[
                "add_cycle",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_cycle_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        runtime.engine.configuration.week_schedules = ()

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_cycle()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_cycle"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "alternating",
                "name": "Alternance",
                "start_date": "2026-08-31",
                "week_schedule_ids": [],
            }
        )

        assert validated["id"] == "alternating"
        assert validated["name"] == "Alternance"
        assert validated["start_date"] == "2026-08-31"
        assert validated["week_schedule_ids"] == []

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_cycle_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_cycle(
                {
                    "id": "alternating",
                    "name": "Alternance",
                    "start_date": "2026-08-31",
                    "week_schedule_ids": [
                        "week_a",
                        "week_b",
                    ],
                }
            )

        cycle = runtime.engine.add_cycle.call_args.args[0]

        assert cycle.id == "alternating"
        assert cycle.name == "Alternance"
        assert cycle.start_date == date(2026, 8, 31)
        assert cycle.week_schedule_ids == (
            "week_a",
            "week_b",
        )

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_cycle_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(
                "week_a",
                "week_b",
            ),
        )

        runtime.engine.configuration.cycles = (cycle,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_cycle()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_cycle"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "alternating",
            }
        )

        assert validated["id"] == "alternating"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_cycle_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_edit_cycle_details = AsyncMock(return_value={"type": "form"})

        result = await flow.async_step_edit_cycle(
            {
                "id": "alternating",
            }
        )

        assert flow._selected_cycle_id == "alternating"

        flow.async_step_edit_cycle_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_cycle_details_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(
                "week_a",
                "week_b",
            ),
        )

        runtime.engine.get_cycle.return_value = cycle

        runtime.engine.configuration.week_schedules = (
            WeekSchedule(
                id="week_a",
                name="Semaine A",
                monday="work",
                tuesday="work",
                wednesday="work",
                thursday="work",
                friday="work",
                saturday="work",
                sunday="work",
            ),
            WeekSchedule(
                id="week_b",
                name="Semaine B",
                monday="work",
                tuesday="work",
                wednesday="work",
                thursday="work",
                friday="work",
                saturday="work",
                sunday="work",
            ),
        )

        flow._selected_cycle_id = "alternating"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_cycle_details()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_cycle_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["name"] == "Alternance"
        assert validated["start_date"] == "2026-08-31"
        assert validated["week_schedule_ids"] == [
            "week_a",
            "week_b",
        ]

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_cycle_details_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        existing_cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(
                "week_a",
                "week_b",
            ),
        )

        runtime.engine.get_cycle.return_value = existing_cycle

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_cycle_id = "alternating"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_cycle_details(
                {
                    "name": "Nouvelle alternance",
                    "start_date": "2026-09-07",
                    "week_schedule_ids": [
                        "week_b",
                        "week_a",
                    ],
                }
            )

        cycle = runtime.engine.update_cycle.call_args.args[0]

        assert cycle.id == "alternating"
        assert cycle.name == "Nouvelle alternance"
        assert cycle.start_date == date(2026, 9, 7)
        assert cycle.week_schedule_ids == (
            "week_b",
            "week_a",
        )

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_cycle_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(),
        )

        runtime.engine.configuration.cycles = (cycle,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_cycle()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_cycle"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "alternating",
            }
        )

        assert validated["id"] == "alternating"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_cycle_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_remove_cycle_confirm = AsyncMock(return_value={"type": "form"})

        result = await flow.async_step_remove_cycle(
            {
                "id": "alternating",
            }
        )

        assert flow._selected_remove_cycle_id == "alternating"

        flow.async_step_remove_cycle_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_cycle_confirm_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(),
        )

        runtime.engine.get_cycle.return_value = cycle

        flow._selected_remove_cycle_id = "alternating"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_cycle_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_cycle_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Alternance",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_cycle_not_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(),
        )

        runtime.engine.get_cycle.return_value = cycle

        flow._selected_remove_cycle_id = "alternating"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_cycle_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_cycle.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_cycle_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        cycle = Cycle(
            id="alternating",
            name="Alternance",
            start_date=date(2026, 8, 31),
            week_schedule_ids=(),
        )

        runtime.engine.get_cycle.return_value = cycle

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_remove_cycle_id = "alternating"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_cycle_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_cycle.assert_called_once_with("alternating")

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_cycles_menu_below_limit():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = (MagicMock(),)
        runtime.engine.max_cycles = 4

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_cycles()

        flow.async_show_menu.assert_called_once_with(
            step_id="cycles",
            menu_options=[
                "add_cycle",
                "edit_cycle",
                "remove_cycle",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_cycles_menu_at_limit():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = (
            MagicMock(),
            MagicMock(),
        )
        runtime.engine.max_cycles = 2

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_cycles()

        flow.async_show_menu.assert_called_once_with(
            step_id="cycles",
            menu_options=[
                "edit_cycle",
                "remove_cycle",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_cycle_maximum_reached():
    async def run():
        runtime = MagicMock()

        runtime.engine.configuration.week_schedules = ()

        runtime.engine.add_cycle.side_effect = ValidationError(
            "Maximum number of cycles exceeded: 1"
        )

        flow = create_flow(
            runtime=runtime,
        )

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_cycle(
            {
                "id": "c2",
                "name": "Cycle 2",
                "start_date": "2026-08-31",
                "week_schedule_ids": [],
            }
        )

        runtime.engine.add_cycle.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_cycle"

        assert call.kwargs["errors"] == {
            "base": "maximum_cycles_reached",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_calendar_exceptions_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_calendar_exceptions()

        flow.async_show_menu.assert_called_once_with(
            step_id="calendar_exceptions",
            menu_options=[
                "add_calendar_exception",
                "edit_calendar_exception",
                "remove_calendar_exception",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_calendar_exception_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        day_type = DayType(
            id="work",
            name="Travail",
            scheduled_moments=(),
        )

        runtime.engine.configuration.day_types = (day_type,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_calendar_exception()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_calendar_exception"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "holiday",
                "date": "2026-12-25",
                "day_type_id": "work",
                "description": "Noël",
            }
        )

        assert validated["id"] == "holiday"
        assert validated["date"] == "2026-12-25"
        assert validated["day_type_id"] == "work"
        assert validated["description"] == "Noël"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_calendar_exception_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_calendar_exception(
                {
                    "id": "holiday",
                    "date": "2026-12-25",
                    "day_type_id": "work",
                    "description": "Noël",
                }
            )

        calendar_exception = runtime.engine.add_calendar_exception.call_args.args[0]

        assert calendar_exception.id == "holiday"
        assert calendar_exception.date == date(2026, 12, 25)
        assert calendar_exception.day_type_id == "work"
        assert calendar_exception.description == "Noël"

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_edit_calendar_exception_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.configuration.calendar_exceptions = (calendar_exception,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_calendar_exception()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_calendar_exception"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "holiday",
            }
        )

        assert validated["id"] == "holiday"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_calendar_exception_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_edit_calendar_exception_details = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_edit_calendar_exception(
            {
                "id": "holiday",
            }
        )

        assert flow._selected_calendar_exception_id == "holiday"

        flow.async_step_edit_calendar_exception_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_calendar_exception_details_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.get_calendar_exception.return_value = calendar_exception

        runtime.engine.configuration.day_types = (
            DayType(
                id="work",
                name="Travail",
                scheduled_moments=(),
            ),
        )

        flow._selected_calendar_exception_id = "holiday"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_calendar_exception_details()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_calendar_exception_details"

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["date"] == "2026-12-25"
        assert validated["day_type_id"] == "work"
        assert validated["description"] == "Noël"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_calendar_exception_details_create():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.get_calendar_exception.return_value = calendar_exception

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_calendar_exception_id = "holiday"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_calendar_exception_details(
                {
                    "date": "2026-12-26",
                    "day_type_id": "work",
                    "description": "Noël décalé",
                }
            )

        updated = runtime.engine.update_calendar_exception.call_args.args[0]

        assert updated.id == "holiday"
        assert updated.date == date(2026, 12, 26)
        assert updated.day_type_id == "work"
        assert updated.description == "Noël décalé"

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_calendar_exception_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.configuration.calendar_exceptions = (calendar_exception,)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_calendar_exception()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_calendar_exception"

        schema = call.kwargs["data_schema"]

        validated = schema(
            {
                "id": "holiday",
            }
        )

        assert validated["id"] == "holiday"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_calendar_exception_select():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        flow.async_step_remove_calendar_exception_confirm = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_remove_calendar_exception(
            {
                "id": "holiday",
            }
        )

        assert flow._selected_remove_calendar_exception_id == "holiday"

        flow.async_step_remove_calendar_exception_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_calendar_exception_confirm_form():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.get_calendar_exception.return_value = calendar_exception

        flow._selected_remove_calendar_exception_id = "holiday"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_calendar_exception_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_calendar_exception_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "Noël",
        }

        schema = call.kwargs["data_schema"]

        validated = schema({})

        assert validated["confirm"] is False
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_calendar_exception_not_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.get_calendar_exception.return_value = calendar_exception

        flow._selected_remove_calendar_exception_id = "holiday"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_calendar_exception_confirm(
            {
                "confirm": False,
            }
        )

        runtime.engine.remove_calendar_exception.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_calendar_exception_confirmed():
    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)

        calendar_exception = CalendarException(
            id="holiday",
            date=date(2026, 12, 25),
            day_type_id="work",
            description="Noël",
        )

        runtime.engine.get_calendar_exception.return_value = calendar_exception

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow._selected_remove_calendar_exception_id = "holiday"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_calendar_exception_confirm(
                {
                    "confirm": True,
                }
            )

        runtime.engine.remove_calendar_exception.assert_called_once_with("holiday")

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_moment_actions_form():
    async def run():
        runtime = MagicMock()

        runtime.engine.configuration.moments = (
            Moment(
                id="wake_up",
                name="Réveil",
                icon="mdi:alarm",
                actions=(),
            ),
        )

        flow = create_flow(runtime=runtime)

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_moment_actions()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "moment_actions"

        schema = call.kwargs["data_schema"]

        result_schema = schema(
            {
                "moment_id": "wake_up",
            }
        )

        assert result_schema["moment_id"] == "wake_up"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_moment_actions_select():
    async def run():
        runtime = MagicMock()

        flow = create_flow(runtime=runtime)

        flow.async_step_moment_actions_menu = AsyncMock(return_value={"type": "menu"})

        result = await flow.async_step_moment_actions(
            {
                "moment_id": "wake_up",
            }
        )

        assert flow._selected_action_moment_id == "wake_up"

        flow.async_step_moment_actions_menu.assert_awaited_once_with()

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_moment_actions_menu():
    async def run():
        flow = create_flow()

        flow.async_show_menu = MagicMock(return_value={"type": "menu"})

        result = await flow.async_step_moment_actions_menu()

        flow.async_show_menu.assert_called_once_with(
            step_id="moment_actions_menu",
            menu_options=[
                "add_moment_action",
                "edit_moment_action",
                "remove_moment_action",
            ],
        )

        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_add_moment_action_form():
    async def run():
        runtime = MagicMock()

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_add_moment_action()

        runtime.engine.get_moment.assert_called_once_with("wake_up")

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_moment_action"

        schema = call.kwargs["data_schema"]

        result_schema = schema(
            {
                "id": "salon_on",
                "service": "light.turn_on",
                "data": {
                    "entity_id": "light.salon",
                },
            }
        )

        assert result_schema["id"] == "salon_on"
        assert result_schema["service"] == "light.turn_on"
        assert result_schema["data"] == {
            "entity_id": "light.salon",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_moment_action_create():
    async def run():
        runtime = MagicMock()

        existing_action = Action(
            id="existing",
            service="light.turn_off",
            data={
                "entity_id": "light.salon",
            },
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(existing_action,),
        )

        runtime.engine.get_moment.return_value = moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_add_moment_action(
                {
                    "id": "salon_on",
                    "service": "light.turn_on",
                    "data": {
                        "entity_id": "light.salon",
                    },
                }
            )

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == moment.id
        assert updated.name == moment.name
        assert updated.icon == moment.icon

        assert updated.actions == (
            existing_action,
            Action(
                id="salon_on",
                service="light.turn_on",
                data={
                    "entity_id": "light.salon",
                },
            ),
        )

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())


def test_options_flow_edit_moment_action_form():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={
                "entity_id": "light.salon",
            },
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_moment_action()

        runtime.engine.get_moment.assert_called_once_with("wake_up")

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_moment_action"

        schema = call.kwargs["data_schema"]

        result_schema = schema(
            {
                "id": "salon_on",
            }
        )

        assert result_schema["id"] == "salon_on"

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_action_select():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={},
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_step_edit_moment_action_details = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_edit_moment_action(
            {
                "id": "salon_on",
            }
        )

        assert flow._selected_action_id == "salon_on"

        flow.async_step_edit_moment_action_details.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_action_details_form():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={
                "entity_id": "light.salon",
            },
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)

        flow._selected_action_moment_id = "wake_up"
        flow._selected_action_id = "salon_on"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_edit_moment_action_details()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_moment_action_details"

        schema = call.kwargs["data_schema"]

        result_schema = schema({})

        assert result_schema["service"] == "light.turn_on"

        assert result_schema["data"] == {
            "entity_id": "light.salon",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_action_details_create():
    async def run():
        runtime = MagicMock()

        action1 = Action(
            id="salon_on",
            service="light.turn_on",
            data={
                "entity_id": "light.salon",
            },
        )

        action2 = Action(
            id="cuisine_on",
            service="light.turn_on",
            data={
                "entity_id": "light.cuisine",
            },
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(
                action1,
                action2,
            ),
        )

        runtime.engine.get_moment.return_value = moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow = create_flow(runtime=runtime)

        flow._selected_action_moment_id = "wake_up"
        flow._selected_action_id = "salon_on"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_edit_moment_action_details(
                {
                    "service": "light.turn_off",
                    "data": {
                        "entity_id": "light.salon",
                    },
                }
            )

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == moment.id
        assert updated.name == moment.name
        assert updated.icon == moment.icon

        assert updated.actions == (
            Action(
                id="salon_on",
                service="light.turn_off",
                data={
                    "entity_id": "light.salon",
                },
            ),
            action2,
        )

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_action_form():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={"entity_id": "light.salon"},
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_moment_action()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_moment_action"

        schema = call.kwargs["data_schema"]
        result_schema = schema({"id": "salon_on"})

        assert result_schema["id"] == "salon_on"
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_moment_action_select():
    async def run():
        runtime = MagicMock()

        moment = Moment(
            id="wake_up",
            name="Réveil",
            actions=(),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_step_remove_moment_action_confirm = AsyncMock(
            return_value={"type": "form"}
        )

        result = await flow.async_step_remove_moment_action({"id": "salon_on"})

        assert flow._selected_remove_action_id == "salon_on"

        flow.async_step_remove_moment_action_confirm.assert_awaited_once_with()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_moment_action_confirm_form():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={},
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"
        flow._selected_remove_action_id = "salon_on"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_moment_action_confirm()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "remove_moment_action_confirm"

        assert call.kwargs["description_placeholders"] == {
            "name": "salon_on",
        }

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_moment_action_not_confirmed():
    async def run():
        runtime = MagicMock()

        action = Action(
            id="salon_on",
            service="light.turn_on",
            data={},
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"
        flow._selected_remove_action_id = "salon_on"

        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_remove_moment_action_confirm({"confirm": False})

        runtime.engine.update_moment.assert_not_called()

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_remove_moment_action_confirmed():
    async def run():
        runtime = MagicMock()

        removed_action = Action(
            id="salon_on",
            service="light.turn_on",
            data={"entity_id": "light.salon"},
        )

        preserved_action = Action(
            id="cuisine_on",
            service="light.turn_on",
            data={"entity_id": "light.cuisine"},
        )

        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(
                removed_action,
                preserved_action,
            ),
        )

        runtime.engine.get_moment.return_value = moment

        configuration = MagicMock()
        runtime.engine.configuration = configuration

        runtime.storage.async_save = AsyncMock()
        runtime.ha_scheduler.async_schedule_next = AsyncMock()

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"
        flow._selected_remove_action_id = "salon_on"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        with patch(
            "custom_components.day_planner.options_flow." "async_dispatcher_send"
        ) as dispatcher_send:
            result = await flow.async_step_remove_moment_action_confirm(
                {"confirm": True}
            )

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == moment.id
        assert updated.name == moment.name
        assert updated.icon == moment.icon

        # salon_on supprimée, cuisine_on conservée.
        assert updated.actions == (preserved_action,)

        runtime.storage.async_save.assert_awaited_once_with(configuration)

        runtime.resolver.update_configuration.assert_called_once_with(configuration)

        runtime.ha_scheduler.async_schedule_next.assert_awaited_once_with()

        dispatcher_send.assert_called_once_with(
            runtime.hass,
            SIGNAL_PLANNER_UPDATED,
        )

        assert result == {
            "type": "create_entry",
        }

    asyncio.run(run())
