"""Options flow for Day Planner."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_DELETE_DATA_ON_REMOVE,
    DEFAULT_DELETE_DATA_ON_REMOVE,
    SIGNAL_PLANNER_UPDATED,
)
from .domain.moment import Moment

class DayPlannerOptionsFlow(
    config_entries.OptionsFlow,
):
    """Handle Day Planner options."""

    async def async_step_init(
        self,
        user_input=None,
    ):
        """Show Day Planner options menu."""

        return self.async_show_menu(
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

    async def async_step_settings(
        self,
        user_input=None,
    ):
        """Manage Day Planner settings."""

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DELETE_DATA_ON_REMOVE,
                    default=self.config_entry.options.get(
                        CONF_DELETE_DATA_ON_REMOVE,
                        DEFAULT_DELETE_DATA_ON_REMOVE,
                    ),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="settings",
            data_schema=schema,
        )

    async def async_step_moments(
        self,
        user_input=None,
    ):
        """Manage moments."""

        return self.async_show_menu(
            step_id="moments",
            menu_options=[
                "add_moment",
                "edit_moment",
                "remove_moment",
            ],
        )

    async def async_step_add_moment(
        self,
        user_input=None,
    ):
        """Add a moment."""

        if user_input is not None:
            entry = self.config_entry
            runtime = entry.runtime_data

            moment = Moment(
                id=user_input["id"],
                name=user_input["name"],
                icon=user_input.get("icon"),
                actions=(),
            )

            runtime.engine.add_moment(
                moment
            )

            configuration = runtime.engine.configuration

            await runtime.storage.async_save(
                configuration
            )

            runtime.resolver.update_configuration(
                configuration
            )

            await runtime.ha_scheduler.async_schedule_next()

            async_dispatcher_send(
                runtime.hass,
                SIGNAL_PLANNER_UPDATED,
            )

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("name"): str,
                vol.Optional("icon"): str,
            }
        )

        return self.async_show_form(
            step_id="add_moment",
            data_schema=schema,
        )

    async def async_step_edit_moment(
        self,
        user_input=None,
    ):
        """Edit a moment."""

        return self.async_abort(
            reason="not_implemented"
        )

    async def async_step_remove_moment(
        self,
        user_input=None,
    ):
        """Remove a moment."""

        return self.async_abort(
            reason="not_implemented"
        )
