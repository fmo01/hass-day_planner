"""Day Planner frontend registration."""

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

FRONTEND_URL = "/day_planner/frontend"

FRONTEND_PATH = (
    Path(__file__).parent
    / "frontend"
)


async def async_setup_frontend(
    hass: HomeAssistant,
) -> None:
    """Register Day Planner frontend files."""

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                FRONTEND_URL,
                str(FRONTEND_PATH),
                False,
            )
        ]
    )

