from unittest.mock import MagicMock, patch

import asyncio

from custom_components.day_planner.config_flow import (
    DayPlannerConfigFlow,
)
from custom_components.day_planner.const import (
    DOMAIN,
    NAME,
)


def test_config_flow_user():
    async def run():
        flow = DayPlannerConfigFlow()

        with patch.object(
            flow,
            "async_set_unique_id",
        ) as set_unique_id, patch.object(
            flow,
            "_abort_if_unique_id_configured",
        ) as abort_if_configured, patch.object(
            flow,
            "async_create_entry",
        ) as create_entry:

            create_entry.return_value = {
                "type": "create_entry",
            }

            result = await flow.async_step_user()

            set_unique_id.assert_awaited_once_with(DOMAIN)
            abort_if_configured.assert_called_once_with()
            create_entry.assert_called_once_with(
                title=NAME,
                data={},
            )

            assert result == {
                "type": "create_entry",
            }

    asyncio.run(run())


def test_config_flow_options_flow():
    config_entry = MagicMock()

    flow = DayPlannerConfigFlow()

    options_flow = flow.async_get_options_flow(
        config_entry
    )

    assert options_flow.__class__.__name__ == (
        "DayPlannerOptionsFlow"
    )

