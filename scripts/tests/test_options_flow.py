import asyncio
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry, ConfigEntryState

from custom_components.day_planner.const import (
    CONF_DELETE_DATA_ON_REMOVE,
    CONF_MAX_CYCLES,
    DEFAULT_DELETE_DATA_ON_REMOVE,
    DEFAULT_MAX_CYCLES,
    DOMAIN,
)
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.calendar_exception import CalendarException
from custom_components.day_planner.domain.cycle import Cycle
from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.domain.scheduled_moment import ScheduledMoment
from custom_components.day_planner.domain.time_definition import TimeDefinition
from custom_components.day_planner.domain.week_schedule import WeekSchedule
from custom_components.day_planner.eedomus_import import EedomusImportError
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
    flow._eedomus_csv_download_url = MagicMock(
        return_value="/api/day_planner/eedomus_associations.csv?authSig=test"
    )
    flow._eedomus_xlsx_download_url = MagicMock(
        return_value="/api/day_planner/eedomus_associations.xlsx?authSig=test"
    )

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
                "management",
                "moments",
                "day_types",
                "week_schedules",
                "cycles",
                "calendar_exceptions",
                "settings",
                "import_eedomus",
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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        user_input = {
            "id": "wake_up",
            "name": "Réveil",
            "icon": "mdi:alarm",
        }

        result = await flow.async_step_add_moment(user_input)

        moment = runtime.engine.add_moment.call_args.args[0]

        assert moment.id == "wake_up"
        assert moment.name == "Réveil"
        assert moment.icon == "mdi:alarm"
        assert moment.actions == ()

        runtime.engine.add_moment.assert_called_once()

        runtime.async_configuration_updated.assert_awaited_once_with()

        flow.async_create_entry.assert_called_once_with(
            title="",
            data=flow.config_entry.options,
        )

        assert result == {"type": "create_entry"}
        assert runtime.engine.add_moment.call_args.kwargs == {
            "modified_by": "system",
        }

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
            sequence=[
                {
                    "action": "light.turn_on",
                    "target": {
                        "entity_id": "light.salon",
                    },
                }
            ],
        )

        current_moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(existing_action,),
        )

        runtime.engine.get_moment.return_value = current_moment

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

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

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {
            "type": "create_entry",
        }

        assert runtime.engine.update_moment.call_args.kwargs == {
            "modified_by": "system",
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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_remove_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        result = await flow.async_step_remove_moment_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_moment.assert_called_once_with("wake_up")

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}

        assert runtime.engine.add_day_type.call_args.kwargs == {
            "modified_by": "system",
        }

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_day_type_id = "work"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_edit_day_type_details(
            {
                "name": "Travail modifié",
            }
        )

        updated = runtime.engine.update_day_type.call_args.args[0]

        assert updated.id == "work"
        assert updated.name == "Travail modifié"
        assert updated.scheduled_moments == scheduled_moments

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}
        assert runtime.engine.update_day_type.call_args.kwargs == {
            "modified_by": "system",
        }

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_remove_day_type_id = "work"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_day_type_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_day_type.assert_called_once_with("work")

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}

        assert runtime.engine.add_scheduled_moment.call_args.kwargs == {
            "modified_by": "system",
        }

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_scheduled_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}
        assert runtime.engine.update_scheduled_moment.call_args.kwargs == {
            "modified_by": "system",
        }

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_scheduled_day_type_id = "work"
        flow._selected_remove_scheduled_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_scheduled_moment_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_scheduled_moment.assert_called_once_with(
            "work",
            "wake_up",
            modified_by="system",
        )

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_day_type_in_use():
    async def run():
        runtime = MagicMock()
        runtime.async_configuration_updated = AsyncMock()
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

        runtime.async_configuration_updated = AsyncMock()

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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        assert runtime.engine.add_week_schedule.call_args.kwargs == {
            "modified_by": "system",
        }

        assert week_schedule.id == "week1"
        assert week_schedule.name == "Semaine 1"
        assert week_schedule.monday == "work"
        assert week_schedule.sunday == "weekend"

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_week_schedule_id = "week1"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        assert runtime.engine.update_week_schedule.call_args.kwargs == {
            "modified_by": "system",
        }

        assert updated.id == "week1"
        assert updated.name == "Semaine modifiée"
        assert updated.monday == "work"
        assert updated.sunday == "weekend"

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_remove_week_schedule_id = "week1"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_week_schedule_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_week_schedule.assert_called_once_with("week1")

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {"type": "create_entry"}

    asyncio.run(run())


def test_options_flow_remove_week_schedule_in_use():
    async def run():
        runtime = MagicMock()
        runtime.async_configuration_updated = AsyncMock()

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

        runtime.async_configuration_updated = AsyncMock()

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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        assert runtime.engine.add_cycle.call_args.kwargs == {
            "modified_by": "system",
        }

        assert cycle.id == "alternating"
        assert cycle.name == "Alternance"
        assert cycle.start_date == date(2026, 8, 31)
        assert cycle.week_schedule_ids == (
            "week_a",
            "week_b",
        )

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_cycle_id = "alternating"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

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

        assert runtime.engine.update_cycle.call_args.kwargs == {
            "modified_by": "system",
        }

        assert cycle.id == "alternating"
        assert cycle.name == "Nouvelle alternance"
        assert cycle.start_date == date(2026, 9, 7)
        assert cycle.week_schedule_ids == (
            "week_b",
            "week_a",
        )

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_remove_cycle_id = "alternating"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_cycle_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_cycle.assert_called_once_with("alternating")

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_add_calendar_exception(
            {
                "id": "holiday",
                "date": "2026-12-25",
                "day_type_id": "work",
                "description": "Noël",
            }
        )

        calendar_exception = runtime.engine.add_calendar_exception.call_args.args[0]

        assert runtime.engine.add_calendar_exception.call_args.kwargs == {
            "modified_by": "system",
        }

        assert calendar_exception.id == "holiday"
        assert calendar_exception.date == date(2026, 12, 25)
        assert calendar_exception.day_type_id == "work"
        assert calendar_exception.description == "Noël"

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_calendar_exception_id = "holiday"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_edit_calendar_exception_details(
            {
                "date": "2026-12-26",
                "day_type_id": "work",
                "description": "Noël décalé",
            }
        )

        updated = runtime.engine.update_calendar_exception.call_args.args[0]

        assert runtime.engine.update_calendar_exception.call_args.kwargs == {
            "modified_by": "system",
        }

        assert updated.id == "holiday"
        assert updated.date == date(2026, 12, 26)
        assert updated.day_type_id == "work"
        assert updated.description == "Noël décalé"

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        runtime.async_configuration_updated = AsyncMock()

        flow._selected_remove_calendar_exception_id = "holiday"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_calendar_exception_confirm(
            {
                "confirm": True,
            }
        )

        runtime.engine.remove_calendar_exception.assert_called_once_with("holiday")

        runtime.async_configuration_updated.assert_awaited_once_with()

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

        sequence = [
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ]

        result_schema = schema(
            {
                "id": "salon_on",
                "label": "Allumer le salon",
                "sequence": sequence,
            }
        )

        assert result_schema["id"] == "salon_on"
        assert result_schema["label"] == "Allumer le salon"
        assert result_schema["sequence"] == sequence

        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_add_moment_action_create():
    async def run():
        runtime = MagicMock()

        existing_action = Action(
            id="existing",
            sequence=[
                {
                    "action": "light.turn_off",
                    "target": {
                        "entity_id": "light.salon",
                    },
                }
            ],
        )
        moment = Moment(
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(existing_action,),
        )

        runtime.engine.get_moment.return_value = moment

        runtime.async_configuration_updated = AsyncMock()

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        result = await flow.async_step_add_moment_action(
            {
                "id": "salon_on",
                "label": "Allumer le salon",
                "sequence": [
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
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
                label="Allumer le salon",
                sequence=[
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
        )

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {
            "type": "create_entry",
        }

        assert runtime.engine.update_moment.call_args.kwargs == {
            "modified_by": "system",
        }

    asyncio.run(run())


def test_options_flow_edit_moment_action_form():
    async def run():
        runtime = MagicMock()

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
            sequence=[
                {
                    "action": "light.turn_on",
                }
            ],
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

        assert result_schema["sequence"] == [
            {
                "action": "light.turn_on",
                "target": {
                    "entity_id": "light.salon",
                },
            }
        ]
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_edit_moment_action_details_create():
    async def run():
        runtime = MagicMock()

        action1 = Action(
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

        action2 = Action(
            id="cuisine_on",
            sequence=[
                {
                    "action": "light.turn_on",
                    "target": {
                        "entity_id": "light.cuisine",
                    },
                }
            ],
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

        runtime.async_configuration_updated = AsyncMock()

        flow = create_flow(runtime=runtime)

        flow._selected_action_moment_id = "wake_up"
        flow._selected_action_id = "salon_on"

        flow.async_create_entry = MagicMock(
            return_value={
                "type": "create_entry",
            }
        )

        result = await flow.async_step_edit_moment_action_details(
            {
                "label": "Éteindre le salon",
                "sequence": [
                    {
                        "action": "light.turn_off",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            }
        )

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == moment.id
        assert updated.name == moment.name
        assert updated.icon == moment.icon

        assert updated.actions == (
            Action(
                id="salon_on",
                label="Éteindre le salon",
                sequence=[
                    {
                        "action": "light.turn_off",
                        "target": {
                            "entity_id": "light.salon",
                        },
                    }
                ],
            ),
            action2,
        )

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {
            "type": "create_entry",
        }

        assert runtime.engine.update_moment.call_args.kwargs == {
            "modified_by": "system",
        }

    asyncio.run(run())


def test_options_flow_remove_moment_action_form():
    async def run():
        runtime = MagicMock()

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
            sequence=[
                {
                    "action": "light.turn_on",
                    "target": {
                        "entity_id": "light.salon",
                    },
                }
            ],
        )

        preserved_action = Action(
            id="cuisine_on",
            sequence=[
                {
                    "action": "light.turn_on",
                    "target": {
                        "entity_id": "light.cuisine",
                    },
                }
            ],
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

        runtime.async_configuration_updated = AsyncMock()

        flow = create_flow(runtime=runtime)
        flow._selected_action_moment_id = "wake_up"
        flow._selected_remove_action_id = "salon_on"

        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_remove_moment_action_confirm({"confirm": True})

        updated = runtime.engine.update_moment.call_args.args[0]

        assert updated.id == moment.id
        assert updated.name == moment.name
        assert updated.icon == moment.icon

        # salon_on supprimée, cuisine_on conservée.
        assert updated.actions == (preserved_action,)

        runtime.async_configuration_updated.assert_awaited_once_with()

        assert result == {
            "type": "create_entry",
        }
        assert runtime.engine.update_moment.call_args.kwargs == {
            "modified_by": "system",
        }

    asyncio.run(run())


def test_options_flow_add_moment_action_empty_sequence():
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

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_add_moment_action(
            {
                "id": "salon_on",
                "sequence": [],
            }
        )

        # Aucune modification ne doit être effectuée.
        runtime.engine.update_moment.assert_not_called()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "add_moment_action"

        assert call.kwargs["errors"] == {
            "sequence": "action_sequence_required",
        }

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_edit_moment_action_empty_sequence():
    async def run():
        runtime = MagicMock()

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
            id="wake_up",
            name="Réveil",
            icon="mdi:alarm",
            actions=(action,),
        )

        runtime.engine.get_moment.return_value = moment

        flow = create_flow(runtime=runtime)

        flow._selected_action_moment_id = "wake_up"
        flow._selected_action_id = "salon_on"

        flow.async_show_form = MagicMock(
            return_value={
                "type": "form",
            }
        )

        result = await flow.async_step_edit_moment_action_details(
            {
                "sequence": [],
            }
        )

        # L'action existante ne doit surtout pas être modifiée.
        runtime.engine.update_moment.assert_not_called()

        flow.async_show_form.assert_called_once()

        call = flow.async_show_form.call_args

        assert call.kwargs["step_id"] == "edit_moment_action_details"

        assert call.kwargs["errors"] == {
            "sequence": "action_sequence_required",
        }

        assert result == {
            "type": "form",
        }

    asyncio.run(run())


def test_options_flow_management_link():
    async def run():
        flow = create_flow()
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        flow.async_create_entry = MagicMock()

        result = await flow.async_step_management()

        call = flow.async_show_form.call_args
        assert call.kwargs["step_id"] == "management"
        assert call.kwargs["description_placeholders"] == {"url": "/day-planner"}
        assert call.kwargs["data_schema"]({}) == {}
        flow.async_create_entry.assert_not_called()
        assert result == {"type": "form"}

    asyncio.run(run())


def test_options_flow_management_returns_to_menu():
    async def run():
        flow = create_flow()
        flow.async_step_init = AsyncMock(return_value={"type": "menu"})
        result = await flow.async_step_management({})
        flow.async_step_init.assert_awaited_once_with()
        assert result == {"type": "menu"}

    asyncio.run(run())


def test_options_flow_settings_preserves_other_options():
    async def run():
        runtime = MagicMock()
        runtime.engine.configuration.cycles = ()
        flow = create_flow(
            options={
                CONF_DELETE_DATA_ON_REMOVE: True,
                CONF_MAX_CYCLES: 3,
                "show_sidebar_panel": True,
                "other_option": "keep",
            },
            runtime=runtime,
        )
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        await flow.async_step_settings({"show_sidebar_panel": False})
        flow.async_create_entry.assert_called_once_with(
            title="",
            data={
                CONF_DELETE_DATA_ON_REMOVE: True,
                CONF_MAX_CYCLES: 3,
                "show_sidebar_panel": False,
                "other_option": "keep",
            },
        )

    asyncio.run(run())


def test_eedomus_import_flow_requires_configured_box():
    async def run():
        flow = create_flow()
        flow.hass.config_entries.async_entries.return_value = []
        flow.async_abort = MagicMock(return_value={"type": "abort"})
        result = await flow.async_step_import_eedomus()
        assert result == {"type": "abort"}
        flow.async_abort.assert_called_once_with(reason="eedomus_not_configured")

    asyncio.run(run())


def test_eedomus_import_flow_prompts_for_source_and_json_upload():
    async def run():
        flow = create_flow()
        box = MagicMock()
        box.entry_id = "01TEST"
        box.title = "eedomus maison"
        box.domain = "eedomus"
        box.disabled_by = None
        box.state = ConfigEntryState.LOADED
        flow.hass.config_entries.async_entries.return_value = [box]
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus()
        assert result == {"type": "form"}
        assert flow.async_show_form.call_args.kwargs["step_id"] == "import_eedomus"
        schema = flow.async_show_form.call_args.kwargs["data_schema"]
        selectors = {key.schema: value for key, value in schema.schema.items()}
        assert "json_upload" in selectors
        assert "source_entry_id" not in selectors  # Only one box: auto-select.
        assert "json_path" not in selectors
        assert selectors["json_upload"].selector_type == "file"
        placeholders = flow.async_show_form.call_args.kwargs["description_placeholders"]
        assert "eedomus maison" in placeholders["selected_box"]
        assert placeholders["box_count"] == "1"

    asyncio.run(run())


def test_eedomus_import_confirmation_persists_once():
    async def run():
        from custom_components.day_planner.domain.planner_configuration import (
            PlannerConfiguration,
        )

        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        runtime.async_configuration_updated = AsyncMock()
        flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.configuration = PlannerConfiguration.empty()
        plan.had_previous_import = False
        flow._eedomus_import_source = "01TEST"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(
            runtime.engine.configuration
        )
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        result = await flow.async_step_import_eedomus_confirm(
            {"confirm": True, "replace_existing": False}
        )
        assert result == {"type": "create_entry"}
        runtime.engine.replace_configuration.assert_called_once_with(plan.configuration)
        runtime.async_configuration_updated.assert_awaited_once()

    asyncio.run(run())


def test_eedomus_import_confirmation_blocks_unapproved_replacement():
    async def run():
        from custom_components.day_planner.domain.planner_configuration import (
            PlannerConfiguration,
        )

        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.had_previous_import = True
        plan.day_types = 9
        plan.moments = 10
        plan.scheduled = 43
        plan.actions = 12
        plan.conditional_rules_not_imported = 7
        plan.unresolved_embedded_parameters = 1
        plan.mapped_entities = ("3463520 → climate.thermostat_salle_a_manger",)
        flow._eedomus_import_source = "01TEST"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(
            runtime.engine.configuration
        )
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus_confirm(
            {"confirm": True, "replace_existing": False}
        )
        assert result == {"type": "form"}
        assert flow.async_show_form.call_args.kwargs["errors"] == {
            "base": "eedomus_replace_required"
        }
        runtime.engine.replace_configuration.assert_not_called()

    asyncio.run(run())


def test_eedomus_import_browser_upload_consumed_from_ha_temp(tmp_path):
    """The browser JSON is read through HA's upload handler, not /config."""
    from contextlib import contextmanager
    from unittest.mock import patch

    async def run():
        flow = create_flow()
        uploaded = tmp_path / "export.json"
        uploaded.write_text('{"tables": []}', encoding="utf-8")
        flow.hass.async_add_executor_job = AsyncMock(side_effect=lambda job: job())

        @contextmanager
        def fake_upload(hass, file_id):
            assert hass is flow.hass
            assert file_id == "UPLOAD_TOKEN"
            yield uploaded

        with patch(
            "custom_components.day_planner.options_flow.process_uploaded_file",
            fake_upload,
        ), patch(
            "custom_components.day_planner.options_flow.prepare_import",
            return_value={"day_types": []},
        ) as mock_prepare:
            result = await flow._eedomus_read_upload("UPLOAD_TOKEN", "01TEST")
        assert result == {"day_types": []}
        assert mock_prepare.call_args.args[1:] == ("01TEST", uploaded)

    asyncio.run(run())


def test_eedomus_import_selected_browser_json_reaches_confirmation():
    """The picker value is an uploaded file ID, never a server file path."""
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        box = MagicMock()
        box.entry_id = "01TEST"
        box.domain = "eedomus"
        box.title = "eedomus maison"
        box.domain = "eedomus"
        box.disabled_by = None
        box.state = ConfigEntryState.LOADED
        flow.hass.config_entries.async_entries.return_value = [box]
        flow.hass.config_entries.async_get_entry.return_value = box
        agenda = {"day_types": []}
        flow._eedomus_read_upload = AsyncMock(return_value=agenda)
        flow._eedomus_plan = AsyncMock(return_value=MagicMock())
        flow.async_step_import_eedomus_confirm = AsyncMock(
            return_value={"type": "confirmation"}
        )

        result = await flow.async_step_import_eedomus(
            {"source_entry_id": "01TEST", "json_upload": "UPLOAD_TOKEN"}
        )
        assert result == {"type": "confirmation"}
        flow._eedomus_read_upload.assert_awaited_once_with("UPLOAD_TOKEN", "01TEST")
        flow._eedomus_plan.assert_awaited_once_with("01TEST", agenda)
        assert flow._eedomus_import_agenda is agenda
        assert flow._eedomus_import_source == "01TEST"

    asyncio.run(run())


def test_eedomus_import_multiple_boxes_requires_selection():
    async def run():
        flow = create_flow()
        first = MagicMock(
            entry_id="A1",
            title="Box 1",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
        )
        second = MagicMock(
            entry_id="B2",
            title="Box 2",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
        )
        flow.hass.config_entries.async_entries.return_value = [first, second]
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        await flow.async_step_import_eedomus()
        schema = flow.async_show_form.call_args.kwargs["data_schema"]
        selectors = {key.schema: value for key, value in schema.schema.items()}
        assert "source_entry_id" in selectors
        assert "json_upload" in selectors
        assert (
            flow.async_show_form.call_args.kwargs["description_placeholders"][
                "box_count"
            ]
            == "2"
        )

    asyncio.run(run())


def test_eedomus_import_single_box_uses_its_entry_id():
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        box = MagicMock(
            entry_id="ONEBOX",
            domain="eedomus",
            title="Box maison",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
        )
        flow.hass.config_entries.async_entries.return_value = [box]
        flow.hass.config_entries.async_get_entry.return_value = box
        agenda = {"day_types": []}
        flow._eedomus_read_upload = AsyncMock(return_value=agenda)
        flow._eedomus_plan = AsyncMock()
        flow.async_step_import_eedomus_confirm = AsyncMock(
            return_value={"type": "confirmation"}
        )
        result = await flow.async_step_import_eedomus({"json_upload": "UPLOAD_TOKEN"})
        assert result == {"type": "confirmation"}
        flow._eedomus_read_upload.assert_awaited_once_with("UPLOAD_TOKEN", "ONEBOX")
        assert flow._eedomus_import_source == "ONEBOX"
        assert flow._eedomus_configuration_digest == flow._eedomus_digest(
            runtime.engine.configuration
        )

    asyncio.run(run())


def test_eedomus_import_only_enabled_loaded_boxes_are_proposed():
    """Disabled, not-loaded and failed eedomus entries are never offered."""

    async def run():
        flow = create_flow()
        boxes = [
            MagicMock(
                entry_id="DISABLED",
                title="Off",
                domain="eedomus",
                disabled_by="user",
                state=ConfigEntryState.NOT_LOADED,
            ),
            MagicMock(
                entry_id="FAILED",
                title="Error",
                domain="eedomus",
                disabled_by=None,
                state=ConfigEntryState.SETUP_ERROR,
            ),
            MagicMock(
                entry_id="ACTIVE",
                title="Active",
                domain="eedomus",
                disabled_by=None,
                state=ConfigEntryState.LOADED,
            ),
        ]
        flow.hass.config_entries.async_entries.return_value = boxes
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus()
        assert result == {"type": "form"}
        schema = flow.async_show_form.call_args.kwargs["data_schema"]
        fields = {key.schema for key in schema.schema}
        assert fields == {"json_upload"}
        description = flow.async_show_form.call_args.kwargs["description_placeholders"]
        assert description["box_count"] == "1"
        assert "ACTIVE" in description["selected_box"]

    asyncio.run(run())


def test_eedomus_import_rejects_all_inactive_boxes():
    async def run():
        flow = create_flow()
        flow.hass.config_entries.async_entries.return_value = [
            MagicMock(
                domain="eedomus", disabled_by="user", state=ConfigEntryState.NOT_LOADED
            )
        ]
        flow.async_abort = MagicMock(return_value={"type": "abort"})
        result = await flow.async_step_import_eedomus()
        assert result == {"type": "abort"}
        flow.async_abort.assert_called_once_with(reason="eedomus_not_active")

    asyncio.run(run())


def test_eedomus_import_filters_multiple_boxes_to_active_only():
    async def run():
        flow = create_flow()
        boxes = [
            MagicMock(
                entry_id="ONE",
                title="One",
                domain="eedomus",
                disabled_by=None,
                state=ConfigEntryState.LOADED,
            ),
            MagicMock(
                entry_id="TWO",
                title="Two",
                domain="eedomus",
                disabled_by=None,
                state=ConfigEntryState.LOADED,
            ),
            MagicMock(
                entry_id="DISABLED",
                title="Disabled",
                domain="eedomus",
                disabled_by="user",
                state=ConfigEntryState.NOT_LOADED,
            ),
        ]
        flow.hass.config_entries.async_entries.return_value = boxes
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        await flow.async_step_import_eedomus()
        kwargs = flow.async_show_form.call_args.kwargs
        assert kwargs["description_placeholders"]["box_count"] == "2"
        selectors = {
            key.schema: value for key, value in kwargs["data_schema"].schema.items()
        }
        assert "source_entry_id" in selectors
        options = selectors["source_entry_id"].config["options"]
        assert {opt["value"] for opt in options} == {"ONE", "TWO"}

    asyncio.run(run())


def test_eedomus_import_explains_failed_command_without_saving():
    async def run():
        flow = create_flow()
        box = MagicMock(
            entry_id="BOX",
            title="Box",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
        )
        flow.hass.config_entries.async_entries.return_value = [box]
        flow.hass.config_entries.async_get_entry.return_value = box
        flow._eedomus_read_upload = AsyncMock(return_value={"day_types": []})
        flow._eedomus_plan = AsyncMock(
            side_effect=EedomusImportError(
                "Commande refusée pour [795317] sur switch.volet"
            )
        )
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus({"json_upload": "TOKEN"})
        assert result == {"type": "form"}
        kwargs = flow.async_show_form.call_args.kwargs
        assert kwargs["errors"]["base"] == "eedomus_import_invalid"
        assert "795317" in kwargs["description_placeholders"]["details"]
        assert "switch.volet" in kwargs["description_placeholders"]["details"]
        assert "Aucune donnée" in kwargs["description_placeholders"]["details"]

    asyncio.run(run())


def test_eedomus_import_plan_uses_selected_box_host_as_week_name():
    """The title of the week comes from the selected HA box, not its entry ID."""
    import asyncio

    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)
        box = MagicMock(
            entry_id="BOXID",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            title="Eedomus (192.20.55.30) - Eedomus API Mode",
            data={"api_host": "192.20.55.30"},
        )
        flow.hass.config_entries.async_get_entry.return_value = box
        flow._eedomus_actor = AsyncMock(return_value="Utilisateur Test")
        with patch(
            "custom_components.day_planner.options_flow.get_eedomus_entity_map",
            return_value={},
        ), patch(
            "custom_components.day_planner.options_flow.create_import_plan",
            return_value=MagicMock(),
        ) as make_plan:
            await flow._eedomus_plan("BOXID", {"day_types": []})
        assert make_plan.call_args.kwargs["week_name"] == "Eedomus (192.20.55.30)"
        assert make_plan.call_args.args[2] == "BOXID"

    asyncio.run(run())


def test_eedomus_import_plan_rejects_missing_host():
    """IP-based IDs require the api_host of the selected HA box."""
    import asyncio

    async def run():
        runtime = MagicMock()
        flow = create_flow(runtime=runtime)
        box = MagicMock(
            entry_id="BOXID",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            title="Eedomus (maison) - Eedomus API Mode",
            data={},
        )
        flow.hass.config_entries.async_get_entry.return_value = box
        flow._eedomus_actor = AsyncMock(return_value="Utilisateur Test")
        with patch(
            "custom_components.day_planner.options_flow.create_import_plan"
        ) as make_plan:
            try:
                await flow._eedomus_plan("BOXID", {"day_types": []})
            except EedomusImportError as exc:
                assert "api_host" in str(exc)
            else:
                raise AssertionError("An import without api_host must be refused")
            make_plan.assert_not_called()

    asyncio.run(run())


def test_eedomus_import_plan_blocks_same_address_across_active_boxes():
    """IP-based IDs must not silently merge two HA config entries."""
    import asyncio

    async def run():
        flow = create_flow(runtime=MagicMock())
        box = MagicMock(
            entry_id="BOX1",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            data={"api_host": "192.20.55.30"},
        )
        other = MagicMock(
            entry_id="BOX2",
            domain="eedomus",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            data={"api_host": " 192.20.55.30 "},
        )
        flow.hass.config_entries.async_get_entry.return_value = box
        flow.hass.config_entries.async_entries.return_value = [box, other]
        try:
            await flow._eedomus_plan("BOX1", {"day_types": []})
        except EedomusImportError as exc:
            assert "Plusieurs intégrations eedomus actives" in str(exc)
        else:
            raise AssertionError("Two active boxes with the same host must be rejected")

    asyncio.run(run())


def test_eedomus_confirmation_mappings_markdown_table():
    """The confirmation displays one HA entity per Markdown table row."""
    flow = create_flow()
    mappings = (
        "Cmd 1 Volet Séjour [795317] → switch.cmd_1_volet_sejour_salle_a_manger",
        "Cmd 5 Volet Cuisine [795535] → switch.cmd_5_volet_cuisine_cuisine",
        "Guirlande [746271] → light.guirlande_salle_a_manger",
        "Thermostat Salle a manger [3463520] → climate.thermostat_salle_a_manger",
    )
    assert flow._eedomus_mappings_table(mappings) == "\n".join(
        (
            "| Cmd 1 Volet Séjour [795317] | `switch.cmd_1_volet_sejour_salle_a_manger` | Pris en charge |",
            "| Cmd 5 Volet Cuisine [795535] | `switch.cmd_5_volet_cuisine_cuisine` | Pris en charge |",
            "| Guirlande [746271] | `light.guirlande_salle_a_manger` | Pris en charge |",
            "| Thermostat Salle a manger [3463520] | `climate.thermostat_salle_a_manger` | Pris en charge |",
        )
    )


def test_eedomus_confirmation_mappings_empty_and_escaped():
    """Empty or unusual entity mappings cannot corrupt the table."""
    flow = create_flow()
    assert flow._eedomus_mappings_table(()) == "| — | — | Aucune association |"
    assert flow._eedomus_mappings_table(
        ("Interrupteur | entrée [123] → switch.test",)
    ) == (r"| Interrupteur \| entrée [123] | `switch.test` | Pris en charge |")
    assert flow._eedomus_mappings_table(("Sans correspondance",)) == (
        "| Sans correspondance | `—` | Pris en charge |"
    )


def test_eedomus_confirmation_mappings_includes_sensor_in_main_table():
    """The unsupported sensor must be visible beside compatible mappings."""
    flow = create_flow()
    rows = flow._eedomus_mappings_table(
        ("Guirlande [746271] → light.guirlande_salle_a_manger",),
        (
            (
                "Cmd 1 Volet Séjour [795317]",
                "sensor.cmd_1_volet_sejour_salle_a_manger",
                "Domaine sensor non pris en charge",
            ),
        ),
    )
    assert "`light.guirlande_salle_a_manger` | Pris en charge |" in rows
    assert (
        "| Cmd 1 Volet Séjour [795317] | "
        "`sensor.cmd_1_volet_sejour_salle_a_manger` | "
        "Ignoré : Domaine sensor non pris en charge |"
    ) in rows
    assert len(rows.splitlines()) == 2


def test_eedomus_confirmation_uses_mapping_table_in_form():
    """The form passes formatted table rows to the translation placeholder."""
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.had_previous_import = False
        plan.day_types = 9
        plan.moments = 8
        plan.scheduled = 41
        plan.actions = 10
        plan.conditional_rules_not_imported = 7
        plan.unresolved_embedded_parameters = 1
        plan.mapped_entities = ("Guirlande [746271] → light.guirlande_salle_a_manger",)
        plan.unsupported_associations = ()
        flow._eedomus_import_source = "01TEST"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(
            runtime.engine.configuration
        )
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_show_form = MagicMock(return_value={"type": "form"})

        await flow.async_step_import_eedomus_confirm()
        placeholders = flow.async_show_form.call_args.kwargs["description_placeholders"]
        assert placeholders["mappings"] == (
            "| Guirlande [746271] | `light.guirlande_salle_a_manger` | Pris en charge |"
        )

    asyncio.run(run())


def test_eedomus_confirmation_unsupported_table_and_empty_moment_count():
    """Unsupported matches are visible while actionless moments are counted."""
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    flow = create_flow()
    rows = (
        (
            "Cmd 1 Volet Séjour [795317]",
            "sensor.cmd_1_volet",
            "Domaine sensor non pris en charge",
        ),
    )
    assert flow._eedomus_unsupported_table(rows) == (
        "| Cmd 1 Volet Séjour [795317] | `sensor.cmd_1_volet` | Domaine sensor non pris en charge |"
    )
    assert flow._eedomus_unsupported_table(()) == "| — | — | — |"

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        active_flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.had_previous_import = False
        plan.day_types = 9
        plan.moments = 8
        plan.scheduled = 41
        plan.actions = 7
        plan.moments_without_actions = 1
        plan.conditional_rules_not_imported = 7
        plan.unresolved_embedded_parameters = 1
        plan.mapped_entities = ()
        plan.unsupported_associations = rows
        active_flow._eedomus_import_source = "01TEST"
        active_flow._eedomus_import_agenda = {"day_types": []}
        active_flow._eedomus_configuration_digest = active_flow._eedomus_digest(
            runtime.engine.configuration
        )
        active_flow._eedomus_plan = AsyncMock(return_value=plan)
        active_flow.async_show_form = MagicMock(return_value={"type": "form"})
        await active_flow.async_step_import_eedomus_confirm()
        placeholders = active_flow.async_show_form.call_args.kwargs[
            "description_placeholders"
        ]
        assert placeholders["unsupported_count"] == "1"
        assert "sensor.cmd_1_volet" in placeholders["mappings"]
        assert "Ignoré : Domaine sensor non pris en charge" in placeholders["mappings"]
        assert "sensor.cmd_1_volet" in placeholders["unsupported"]
        assert "1 moment(s) sans action compatible" in placeholders["summary"]

    asyncio.run(run())


def test_eedomus_confirmation_copy_table_excel_tsv():
    """The read-only clipboard table contains all accepted and skipped mappings."""
    flow = create_flow()
    tsv = flow._eedomus_copy_table(
        (
            "Guirlande [746271] → light.guirlande_salle_a_manger",
            "Thermostat [3463520] → climate.thermostat_salle_a_manger",
        ),
        (
            (
                "Cmd 1 Volet [795317]",
                "sensor.cmd_1_volet",
                "Domaine sensor non pris en charge",
            ),
        ),
    )
    rows = [line.split("\t") for line in tsv.splitlines()]
    assert rows[0] == [
        "Périphérique eedomus (ID)",
        "Entité Home Assistant",
        "Statut / motif",
    ]
    assert rows[1] == [
        "Guirlande [746271]",
        "light.guirlande_salle_a_manger",
        "Pris en charge",
    ]
    assert rows[2][1] == "climate.thermostat_salle_a_manger"
    assert rows[3] == [
        "Cmd 1 Volet [795317]",
        "sensor.cmd_1_volet",
        "Ignoré : Domaine sensor non pris en charge",
    ]


def test_eedomus_confirmation_copy_table_defensive_and_empty():
    """Bad text cannot inject lines, extra columns or formulas in Excel."""
    flow = create_flow()
    assert flow._eedomus_copy_table((), ()).splitlines() == [
        "Périphérique eedomus (ID)\tEntité Home Assistant\tStatut / motif"
    ]
    tsv = flow._eedomus_copy_table(
        ('=HYPERLINK("https://example.test") [1] → light.test',),
        (("Macro\tA\n[2]", "@malicious", "+danger\nnewline"),),
    )
    rows = [line.split("\t") for line in tsv.splitlines()]
    assert len(rows) == 3
    assert all(len(row) == 3 for row in rows)
    assert rows[1][0].startswith("'=")
    assert rows[2][0] == "Macro A [2]"
    assert rows[2][1] == "'@malicious"
    assert rows[2][2].startswith("Ignoré : +danger")
    assert flow._eedomus_copy_table(("Sans flèche",), ()).splitlines()[1] == (
        "Sans flèche	—	Pris en charge"
    )


def test_eedomus_confirmation_copy_field_selectable_and_ignored():
    """Copying does not alter the pending import or require confirmation."""
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.had_previous_import = False
        plan.day_types = 9
        plan.moments = 8
        plan.scheduled = 41
        plan.actions = 9
        plan.moments_without_actions = 0
        plan.conditional_rules_not_imported = 7
        plan.unresolved_embedded_parameters = 1
        plan.mapped_entities = ("Guirlande [746271] → light.guirlande",)
        plan.unsupported_associations = (
            ("Volet [795317]", "sensor.volet", "Domaine non pris en charge"),
        )
        flow._eedomus_import_source = "BOX"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(
            runtime.engine.configuration
        )
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        await flow.async_step_import_eedomus_confirm()
        schema = flow.async_show_form.call_args.kwargs["data_schema"]
        selectors = {key.schema: value for key, value in schema.schema.items()}
        copy = selectors["associations_excel"]
        assert copy.config["multiline"] is True
        assert copy.config.get("read_only") is not True
        assert "Guirlande" in schema({})["associations_excel"]
        assert "sensor.volet" in schema({})["associations_excel"]
        assert schema({})["confirm"] is False
        # Changing the copy field alone must not trigger import.
        await flow.async_step_import_eedomus_confirm(
            {
                "associations_excel": "CHANGED BY USER",
                "confirm": False,
                "replace_existing": False,
            }
        )
        assert runtime.engine.replace_configuration.call_count == 0
        assert flow.async_show_form.call_args.kwargs["errors"]["base"] == (
            "eedomus_confirm_required"
        )

    asyncio.run(run())


def test_eedomus_confirmation_has_direct_xlsx_link_in_home_assistant():
    """The download URL appears inside the HA confirmation dialog."""
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        plan = MagicMock()
        plan.had_previous_import = False
        plan.day_types = 9
        plan.moments = 8
        plan.scheduled = 41
        plan.actions = 2
        plan.moments_without_actions = 6
        plan.conditional_rules_not_imported = 7
        plan.unresolved_embedded_parameters = 1
        plan.mapped_entities = ("Guirlande [746271] → light.guirlande_salle_a_manger",)
        plan.unsupported_associations = (
            ("Volet [795317]", "sensor.volet", "Domaine sensor non pris en charge"),
        )
        flow._eedomus_import_source = "BOX"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(
            runtime.engine.configuration
        )
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        box = MagicMock()
        box.data = {"api_host": "192.20.55.30"}
        flow.hass.config_entries.async_get_entry.return_value = box
        await flow.async_step_import_eedomus_confirm()
        placeholders = flow.async_show_form.call_args.kwargs["description_placeholders"]
        assert placeholders["download_url"].startswith("/api/day_planner/")
        assert placeholders["download_url"].endswith(".xlsx?authSig=test")
        assert 'target="_blank"' in placeholders["download_link"]
        assert (
            'href="/api/day_planner/eedomus_associations.xlsx'
            in placeholders["download_link"]
        )
        flow._eedomus_xlsx_download_url.assert_called_once_with(
            flow.hass, plan, "192.20.55.30", flow._eedomus_import_agenda
        )

    asyncio.run(run())


def test_eedomus_confirmation_excel_link_uses_safe_translation_placeholder():
    """ICU translations do not support raw HTML links in flow descriptions."""
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "custom_components/day_planner"
    for filename in ("strings.json", "translations/en.json", "translations/fr.json"):
        data = json.loads((root / filename).read_text(encoding="utf-8"))
        description = data["options"]["step"]["import_eedomus_confirm"]["description"]
        assert "{download_url}" in description
        assert "{download_link}" in description
        assert "<a " not in description
        assert "</a>" not in description
        assert "target=" not in description


def test_eedomus_actor_uses_ha_user_name_and_id_fallbacks():
    """Audit actor must be a readable HA name, never a fabricated identity."""

    async def run():
        flow = create_flow()
        flow.context = {}
        assert await flow._eedomus_actor() == "system"
        flow.context = {"user_id": "user-42"}
        flow.hass.auth.async_get_user = AsyncMock(
            return_value=type("User", (), {"name": "Alice", "id": "user-42"})()
        )
        assert await flow._eedomus_actor() == "Alice"
        flow.hass.auth.async_get_user = AsyncMock(
            return_value=type("User", (), {"name": "", "id": "user-42"})()
        )
        assert await flow._eedomus_actor() == "user-42"
        flow.hass.auth.async_get_user = AsyncMock(return_value=None)
        assert await flow._eedomus_actor() == "user-42"

    asyncio.run(run())


def test_eedomus_upload_rejects_wrong_extension_and_oversized_file():
    """Reject unacceptable files in the executor before attempting to parse them."""
    from contextlib import nullcontext
    from types import SimpleNamespace

    from custom_components.day_planner import options_flow as options_module

    async def run():
        flow = create_flow()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=lambda func: func())
        not_json = SimpleNamespace(suffix=".txt", is_file=lambda: True)
        oversized = SimpleNamespace(
            suffix=".json",
            is_file=lambda: True,
            stat=lambda: SimpleNamespace(st_size=20 * 1024 * 1024 + 1),
        )
        not_file = SimpleNamespace(suffix=".json", is_file=lambda: False)
        for path, expected_error in (
            (not_json, "format JSON"),
            (oversized, "20 Mo"),
            (not_file, "introuvable"),
        ):
            with patch.object(
                options_module, "process_uploaded_file", return_value=nullcontext(path)
            ):
                with pytest.raises(EedomusImportError, match=expected_error):
                    await flow._eedomus_read_upload("UPLOAD_TOKEN", "BOX")
        valid = SimpleNamespace(
            suffix=".JSON",
            is_file=lambda: True,
            stat=lambda: SimpleNamespace(st_size=120),
        )
        with patch.object(
            options_module, "process_uploaded_file", return_value=nullcontext(valid)
        ), patch.object(
            options_module, "prepare_import", return_value={"phases": []}
        ) as prepare:
            assert await flow._eedomus_read_upload("UPLOAD_TOKEN", "BOX") == {
                "phases": []
            }
        prepare.assert_called_once_with(flow.hass, "BOX", valid)

    import pytest

    asyncio.run(run())


def test_eedomus_plan_rejects_inactive_or_absent_selected_box():
    async def run():
        flow = create_flow(runtime=MagicMock())
        flow.hass.config_entries.async_get_entry.return_value = None
        with pytest.raises(EedomusImportError, match="désactivée ou non chargée"):
            await flow._eedomus_plan("BOX", {})

        box = MagicMock(
            domain="eedomus", disabled_by="user", state=ConfigEntryState.NOT_LOADED
        )
        flow.hass.config_entries.async_get_entry.return_value = box
        with pytest.raises(EedomusImportError, match="désactivée ou non chargée"):
            await flow._eedomus_plan("BOX", {})

    import pytest

    asyncio.run(run())


def test_eedomus_plan_blocks_duplicate_active_host_without_mapping():
    async def run():
        flow = create_flow(runtime=MagicMock())
        box = MagicMock(
            domain="eedomus",
            entry_id="ONE",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            data={"api_host": "192.20.55.30"},
        )
        duplicate = MagicMock(
            domain="eedomus",
            entry_id="TWO",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            data={"api_host": "192.20.55.30"},
        )
        flow.hass.config_entries.async_get_entry.return_value = box
        flow.hass.config_entries.async_entries.return_value = [box, duplicate]
        with pytest.raises(
            EedomusImportError, match="Plusieurs intégrations eedomus actives"
        ):
            await flow._eedomus_plan("ONE", {})

    import pytest

    asyncio.run(run())


def test_eedomus_preflight_rejects_unlisted_and_disabled_box_selection():
    async def run():
        flow = create_flow()
        a = MagicMock(
            domain="eedomus",
            entry_id="A",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            title="Box A",
        )
        b = MagicMock(
            domain="eedomus",
            entry_id="B",
            disabled_by=None,
            state=ConfigEntryState.LOADED,
            title="Box B",
        )
        flow.hass.config_entries.async_entries.return_value = [a, b]
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        for invalid in ("ANOTHER", "A"):
            if invalid == "A":
                flow.hass.config_entries.async_get_entry.return_value = MagicMock(
                    domain="eedomus",
                    disabled_by="user",
                    state=ConfigEntryState.NOT_LOADED,
                )
            result = await flow.async_step_import_eedomus(
                {
                    "source_entry_id": invalid,
                    "json_upload": "UPLOAD_TOKEN",
                }
            )
            assert result == {"type": "form"}
            assert (
                flow.async_show_form.call_args.kwargs["errors"]["base"]
                == "eedomus_import_invalid"
            )
        flow._eedomus_read_upload = AsyncMock()
        flow._eedomus_read_upload.assert_not_awaited()

    asyncio.run(run())


def test_eedomus_download_static_methods_use_download_module():
    from custom_components.day_planner import options_flow as options_module

    with patch.object(
        options_module, "create_eedomus_csv_link", return_value="signed.csv"
    ) as csv_link:
        assert (
            DayPlannerOptionsFlow._eedomus_csv_download_url("HA", "TSV", "HOST")
            == "signed.csv"
        )
        csv_link.assert_called_once_with("HA", "TSV", "HOST")
    with patch.object(
        options_module, "create_eedomus_xlsx_link", return_value="signed.xlsx"
    ) as xlsx_link:
        assert (
            DayPlannerOptionsFlow._eedomus_xlsx_download_url(
                "HA", "PLAN", "HOST", {"day_types": []}
            )
            == "signed.xlsx"
        )
        xlsx_link.assert_called_once_with("HA", "PLAN", "HOST", {"day_types": []})


def test_eedomus_confirmation_without_preflight_reopens_import():
    async def run():
        flow = create_flow()
        flow.async_step_import_eedomus = AsyncMock(return_value={"type": "import"})
        assert await flow.async_step_import_eedomus_confirm() == {"type": "import"}
        flow.async_step_import_eedomus.assert_awaited_once()

    asyncio.run(run())


def test_eedomus_confirmation_concurrent_change_is_rejected_before_write():
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        runtime.engine.configuration = PlannerConfiguration.empty()
        flow = create_flow(runtime=runtime)
        flow._eedomus_import_source = "BOX"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = "previous_digest"
        flow._eedomus_plan = AsyncMock(return_value=MagicMock())
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus_confirm({"confirm": True})
        assert result == {"type": "form"}
        assert flow.async_show_form.call_args.kwargs["errors"] == {
            "base": "eedomus_import_changed"
        }
        runtime.engine.replace_configuration.assert_not_called()

    asyncio.run(run())


def test_eedomus_confirmation_handles_failed_save_and_failed_rollback():
    from custom_components.day_planner.domain.planner_configuration import (
        PlannerConfiguration,
    )

    async def run():
        runtime = MagicMock()
        previous = PlannerConfiguration.empty()
        runtime.engine.configuration = previous
        runtime.async_configuration_updated = AsyncMock(
            side_effect=[RuntimeError("persist"), RuntimeError("rollback")]
        )
        flow = create_flow(runtime=runtime)
        flow._eedomus_import_source = "BOX"
        flow._eedomus_import_agenda = {"day_types": []}
        flow._eedomus_configuration_digest = flow._eedomus_digest(previous)
        plan = MagicMock()
        plan.configuration = MagicMock()
        plan.had_previous_import = False
        plan.day_types = 1
        plan.moments = 1
        plan.scheduled = 1
        plan.actions = 0
        plan.moments_without_actions = 1
        plan.conditional_rules_not_imported = 0
        plan.unresolved_embedded_parameters = 0
        plan.mapped_entities = ()
        plan.unsupported_associations = ()
        flow._eedomus_plan = AsyncMock(return_value=plan)
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        result = await flow.async_step_import_eedomus_confirm({"confirm": True})
        assert result == {"type": "form"}
        assert (
            flow.async_show_form.call_args.kwargs["errors"]["base"]
            == "eedomus_import_failed"
        )
        assert runtime.engine.replace_configuration.call_count == 2
        assert runtime.engine.replace_configuration.call_args.args == (previous,)
        assert runtime.async_configuration_updated.await_count == 2

    asyncio.run(run())
