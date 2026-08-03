from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, NAME


class DayPlannerConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle Day Planner configuration."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup."""

        if user_input is not None:
            return self.async_create_entry(
                title=NAME,
                data={},
            )

        return self.async_show_form(
            step_id="user",
        )
