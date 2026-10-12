from custom_components.day_planner.integration_info import (
    INTEGRATION_VERSION, integration_attributes)


def test_integration_attributes():
    assert integration_attributes() == {
        "integration": "Day Planner",
        "integration_version": INTEGRATION_VERSION,
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
    }
