"""Shared entity helpers for Day Planner."""

import json
from pathlib import Path

from .const import INTEGRATION_NAME, RELEASE_URL


_MANIFEST_PATH = Path(__file__).with_name("manifest.json")

with _MANIFEST_PATH.open(
    encoding="utf-8",
) as manifest_file:
    _MANIFEST = json.load(manifest_file)

INTEGRATION_VERSION = _MANIFEST["version"]


def integration_attributes() -> dict:
    """Return common Day Planner attributes."""

    return {
        "integration": INTEGRATION_NAME,
        "integration_version": INTEGRATION_VERSION,
        "release_url": RELEASE_URL,
    }
