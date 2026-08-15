"""Options flow for Day Planner."""

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_DELETE_DATA_ON_REMOVE, DEFAULT_DELETE_DATA_ON_REMOVE


class DayPlannerOptionsFlow(
    config_entries.OptionsFlow,
):
    """Handle Day Planner options."""

    async def async_step_init(
        self,
        user_input=None,
    ):
        """Manage options."""

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
            step_id="init",
            data_schema=schema,
        )
