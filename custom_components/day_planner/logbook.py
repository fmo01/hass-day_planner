"""Attribute Home Assistant state changes to Day Planner actions in Logbook."""

from collections.abc import Callable

from homeassistant.components.logbook import (
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
    LOGBOOK_ENTRY_SOURCE,
)
from homeassistant.core import Event, HomeAssistant, callback

from .const import DOMAIN, EVENT_DAY_PLANNER_ACTION, EVENT_DAY_PLANNER_ACTION_RESULT


def _action_identity(data: dict) -> tuple[str, str, str]:
    """Return the action name, label and readable moment suffix."""

    action_id = str(data.get("action_id") or "inconnue")
    label = str(data.get("action_label") or action_id)
    # Keep the internal ID visible when it differs from the public label.
    action_name = label if action_id == label else f"{label} (id : {action_id})"
    moment_name = data.get("moment_name")
    suffix = f" (moment : {moment_name})" if moment_name else ""
    return action_name, label, suffix


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable,
) -> None:
    """Register origin and anomaly events for Logbook."""

    @callback
    def describe_action_started(event: Event) -> dict[str, str]:
        """Describe an action as the *origin* of its subsequent state changes."""

        action_name, label, suffix = _action_identity(event.data)
        requested_service = event.data.get("requested_service")
        service_detail = (
            f" ; service demandé : {requested_service}" if requested_service else ""
        )
        return {
            LOGBOOK_ENTRY_NAME: f"Day Planner — action {action_name}",
            LOGBOOK_ENTRY_MESSAGE: (
                f"a déclenché l'action '{label}'{suffix}{service_detail}"
            ),
            LOGBOOK_ENTRY_SOURCE: f"Day Planner — action {action_name}",
        }

    @callback
    def describe_action_result(event: Event) -> dict[str, str]:
        """Show only execution anomalies, not another success entry."""

        action_name, label, suffix = _action_identity(event.data)
        status = event.data.get("status")
        if status == "failed":
            message = f"échec de l'action '{label}'{suffix}"
        else:
            missing = ", ".join(event.data.get("missing_entities") or [])
            detail = missing or "cible(s) signalée(s) par Home Assistant"
            message = (
                f"action '{label}' avec cible(s) indisponible(s) : " f"{detail}{suffix}"
            )
        return {
            LOGBOOK_ENTRY_NAME: f"Day Planner — action {action_name}",
            LOGBOOK_ENTRY_MESSAGE: message,
        }

    async_describe_event(DOMAIN, EVENT_DAY_PLANNER_ACTION, describe_action_started)
    async_describe_event(
        DOMAIN, EVENT_DAY_PLANNER_ACTION_RESULT, describe_action_result
    )
