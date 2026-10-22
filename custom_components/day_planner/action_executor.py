"""Execute Day Planner actions through the Home Assistant script engine."""

import logging
from collections.abc import Mapping
from contextvars import ContextVar
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers.script import Script

from .const import EVENT_DAY_PLANNER_ACTION, EVENT_DAY_PLANNER_ACTION_RESULT
from .domain.action import Action
from .domain.moment import Moment

_LOGGER = logging.getLogger(__name__)
_SERVICE_LOGGER = logging.getLogger("homeassistant.helpers.service")
_ACTIVE_ACTION: ContextVar[object | None] = ContextVar(
    "day_planner_active_action", default=None
)


class _HAServiceWarningHandler(logging.Handler):
    """Mirror only matching HA service target warnings for the active action.

    A ContextVar avoids attributing another concurrent action's warning to
    this one. The handler is attached only during the script execution.
    """

    def __init__(self, marker: object, action: Action, moment: Moment | None):
        super().__init__(level=logging.WARNING)
        self.marker = marker
        self.action_id = action.id
        self.moment_name = moment.name if moment is not None else "exécution directe"
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Re-log this specific HA warning as a Day Planner error."""

        if _ACTIVE_ACTION.get() is not self.marker:
            return
        if record.name != "homeassistant.helpers.service":
            return
        message = record.getMessage()
        if (
            "Referenced entities " not in message
            or "are missing or not currently available" not in message
        ):
            return

        self.messages.append(message)
        _LOGGER.error(
            "Avertissement Home Assistant repris en ERROR Day Planner : "
            "action='%s', moment='%s' : %s",
            self.action_id,
            self.moment_name,
            message,
        )


def _static_entity_ids(value: Any) -> tuple[str, ...]:
    """Return literal entity IDs, ignoring templates and non-string values."""

    if isinstance(value, str):
        values = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        return ()

    return tuple(
        entity_id.strip()
        for entity_id in values
        if isinstance(entity_id, str)
        and entity_id.strip()
        and "{{" not in entity_id
        and "{%" not in entity_id
    )


def _simple_requested_service(action: Action) -> str | None:
    """Describe a single literal service call, without guessing dynamic targets.

    This is only a human-readable description of the requested call; the
    actual execution and state change remain Home Assistant's responsibility.
    """

    if len(action.sequence) != 1:
        return None
    step = action.sequence[0]
    if not isinstance(step, Mapping):
        return None
    service = step.get("action", step.get("service"))
    if not isinstance(service, str) or "." not in service:
        return None
    target = step.get("target")
    data = step.get("data", step.get("service_data"))
    target_ids: list[str] = []
    if isinstance(target, Mapping):
        target_ids.extend(_static_entity_ids(target.get("entity_id")))
    if isinstance(data, Mapping):
        target_ids.extend(_static_entity_ids(data.get("entity_id")))
    # If a target is templated, an area/device/label, or not an entity, do
    # not claim to know the actual targets ahead of execution.
    if not target_ids:
        return None
    if isinstance(target, Mapping) and set(target) - {"entity_id"}:
        return None
    if not all("." in entity_id for entity_id in target_ids):
        return None
    return f"{service} → {', '.join(dict.fromkeys(target_ids))}"


class ActionExecutor:
    """Execute a moment's actions and report observable execution errors."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the action executor."""

        self._hass = hass

    def _check_static_targets(
        self, action: Action, moment: Moment | None
    ) -> tuple[str, ...]:
        """Report unavailable targets of direct service steps only.

        HA may log a warning without raising when a target is unavailable.
        Do not inspect conditional/nested sequences: they may not execute.
        """

        missing: set[str] = set()
        moment_name = moment.name if moment is not None else "<direct>"

        for index, step in enumerate(action.sequence, start=1):
            if not isinstance(step, Mapping):
                continue

            service = step.get("action", step.get("service"))
            if not isinstance(service, str) or "." not in service:
                continue

            targets: list[str] = []
            target = step.get("target")
            if isinstance(target, Mapping):
                targets.extend(_static_entity_ids(target.get("entity_id")))

            data = step.get("data", step.get("service_data"))
            if isinstance(data, Mapping):
                targets.extend(_static_entity_ids(data.get("entity_id")))

            for entity_id in dict.fromkeys(targets):
                state = self._hass.states.get(entity_id)
                if state is None or state.state == STATE_UNAVAILABLE:
                    if entity_id in missing:
                        continue
                    missing.add(entity_id)
                    reason = "absente" if state is None else "indisponible"
                    _LOGGER.error(
                        "Cible %s (%s) : action='%s', moment='%s', "
                        "service='%s', étape=%s, entity_id='%s'",
                        reason,
                        "Home Assistant signale normalement un WARNING",
                        action.id,
                        moment_name,
                        service,
                        index,
                        entity_id,
                    )
                else:
                    _LOGGER.debug(
                        "Cible vérifiée : action='%s', service='%s', "
                        "entity_id='%s', état='%s'",
                        action.id,
                        service,
                        entity_id,
                        state.state,
                    )

        return tuple(sorted(missing))

    async def async_execute_action(
        self,
        action: Action,
        *,
        moment: Moment | None = None,
    ) -> None:
        """Execute one action; logbook events share the script context."""

        moment_id = moment.id if moment is not None else None
        moment_name = moment.name if moment is not None else None

        _LOGGER.info(
            "Début action Day Planner : id='%s', libellé='%s', moment='%s'",
            action.id,
            action.label,
            moment_name or "exécution directe",
        )
        _LOGGER.debug(
            "Action '%s' : %d étape(s) à exécuter", action.id, len(action.sequence)
        )

        missing = self._check_static_targets(action, moment)
        context = Context()
        script = Script(
            self._hass,
            action.sequence,
            f"Day Planner action: {action.id}",
            "day_planner",
        )

        status = "completed"
        marker = object()
        token = _ACTIVE_ACTION.set(marker)
        service_warning_handler = _HAServiceWarningHandler(marker, action, moment)
        _SERVICE_LOGGER.addHandler(service_warning_handler)
        try:
            # IMPORTANT: fire the origin BEFORE any service call, with exactly
            # the Context passed to Script. Logbook can then resolve the
            # subsequent entity state change to this Day Planner action.
            self._hass.bus.async_fire(
                EVENT_DAY_PLANNER_ACTION,
                {
                    "action_id": action.id,
                    "action_label": action.label,
                    "moment_id": moment_id,
                    "moment_name": moment_name,
                    "status": "started",
                    "requested_service": _simple_requested_service(action),
                },
                context=context,
            )
            await script.async_run(context=context)
            if missing or service_warning_handler.messages:
                status = "missing_targets"
                _LOGGER.warning(
                    "Fin de l'action '%s' : %d cible(s) statique(s) absente(s) "
                    "ou indisponible(s) ; %d avertissement(s) HA",
                    action.id,
                    len(missing),
                    len(service_warning_handler.messages),
                )
            else:
                _LOGGER.info("Fin de l'action Day Planner '%s'", action.id)
        except Exception:
            status = "failed"
            _LOGGER.debug("Le script de l'action '%s' a levé une exception", action.id)
            raise
        finally:
            _SERVICE_LOGGER.removeHandler(service_warning_handler)
            _ACTIVE_ACTION.reset(token)
            if status != "completed":
                # Keep the origin event first in this Context. The additional
                # entry is reserved for errors and unavailable targets.
                self._hass.bus.async_fire(
                    EVENT_DAY_PLANNER_ACTION_RESULT,
                    {
                        "action_id": action.id,
                        "action_label": action.label,
                        "moment_id": moment_id,
                        "moment_name": moment_name,
                        "status": status,
                        "missing_entities": list(missing),
                        "ha_warnings": list(service_warning_handler.messages),
                    },
                    context=context,
                )

    async def async_execute_moment(self, moment: Moment) -> None:
        """Run every action; a failure must not prevent subsequent actions."""

        _LOGGER.info(
            "Début moment Day Planner : '%s' (id='%s'), %d action(s)",
            moment.name,
            moment.id,
            len(moment.actions),
        )

        if not moment.actions:
            _LOGGER.debug("Moment '%s' : aucune action à exécuter", moment.id)

        errors = 0
        for action in moment.actions:
            try:
                await self.async_execute_action(action, moment=moment)
            except Exception:
                errors += 1
                _LOGGER.exception(
                    "Échec de l'action Day Planner '%s' pour le moment '%s' "
                    "(id='%s') ; poursuite des autres actions",
                    action.id,
                    moment.name,
                    moment.id,
                )

        if errors:
            _LOGGER.error(
                "Fin du moment '%s' : %d action(s) en échec sur %d",
                moment.name,
                errors,
                len(moment.actions),
            )
        else:
            _LOGGER.info("Fin du moment Day Planner '%s'", moment.name)
