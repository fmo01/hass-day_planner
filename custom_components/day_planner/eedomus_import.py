"""One-shot, read-only eedomus JSON to Day Planner import preparation.

The resulting configuration is built and validated before any storage mutation.
No eedomus network call is issued and no Home Assistant service is executed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any

from .domain.action import Action
from .domain.day_type import DayType
from .domain.metadata import Audit
from .domain.moment import Moment
from .domain.planner_configuration import PlannerConfiguration
from .domain.scheduled_moment import ScheduledMoment
from .domain.time_definition import TimeDefinition
from .domain.week_schedule import WeekSchedule
from .eedomus_agenda_extract import extract, load_export
from .planner.errors import ValidationError
from .planner.validator import PlannerValidator

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


class EedomusImportError(ValueError):
    """An export, mapping or import conflict prevents a safe import."""


@dataclass(frozen=True)
class ImportPlan:
    """Validated, not-yet-applied configuration and user-facing summary."""

    configuration: PlannerConfiguration
    source_entry_id: str
    replace_existing: bool
    had_previous_import: bool
    day_types: int
    moments: int
    scheduled: int
    actions: int
    conditional_rules_not_imported: int
    unresolved_embedded_parameters: int
    mapped_entities: tuple[str, ...]
    # Each skipped command is shown in the confirmation (device, HA entity, reason).
    unsupported_associations: tuple[tuple[str, str, str], ...]
    moments_without_actions: int


def _namespace(box_name: str) -> str:
    """Use the selected box's readable name for every imported Day Planner ID.

    HA entity unique_ids remain a separate namespace and must continue to
    use the eedomus config entry ID to resolve physical devices.
    """
    if not isinstance(box_name, str) or not re.fullmatch(
        r"Eedomus \([A-Za-z0-9.:-]+\)", box_name
    ):
        raise EedomusImportError(
            "Nom de box eedomus invalide : attendu Eedomus (adresse de la box)"
        )
    return f"eedomus_{box_name}_"


def _legacy_namespace(source_entry_id: str) -> str:
    """Recognize objects created by earlier import versions using entry_id."""
    if not source_entry_id or not source_entry_id.isalnum():
        raise EedomusImportError("Identifiant de configuration eedomus invalide")
    return f"eedomus_{source_entry_id}_"


def get_eedomus_entity_map(hass: Any, source_entry_id: str) -> dict[str, Any]:
    """Map exact eedomus module IDs via HA's entity registry.

    It is essential not to construct entity_ids from names: users may rename
    the entities, and several eedomus boxes can have the same peripheral IDs.
    """
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    result: dict[str, list] = {}
    prefixes = (f"eedomus_{source_entry_id}_", f"{source_entry_id}_")
    for entry in er.async_entries_for_config_entry(registry, source_entry_id):
        if entry.platform != "eedomus":
            continue
        # Both HA unique_id naming conventions are supported, with or
        # without the leading "eedomus_", and with or without a type suffix.
        # Scope to the exact config entry before extracting the peripheral ID.
        matching_prefix = next(
            (prefix for prefix in prefixes if entry.unique_id.startswith(prefix)),
            None,
        )
        if matching_prefix is None:
            continue
        rest = entry.unique_id.removeprefix(matching_prefix)
        # Match the *whole* peripheral ID and optional suffix; never match
        # another peripheral with a similar numeric prefix.
        match = re.fullmatch(r"([0-9]+)(?:_([A-Za-z0-9_]+))?", rest)
        if match is None:
            continue
        device_id, suffix = match.groups()
        # Battery entities are auxiliary measurements, never command targets.
        # Exclude "_battery" (including composite suffixes such as
        # "_sensor_battery") without rejecting real actuators from the same
        # eedomus peripheral ID.
        if suffix and "battery" in (part.casefold() for part in suffix.split("_")):
            continue
        result.setdefault(device_id, []).append(entry)
    return result


def _convert_service(raw: dict, entity: Any) -> dict:
    """Translate only direct, confidently mapped commands; otherwise fail."""
    if raw.get("type_action") != "direct":
        raise EedomusImportError(
            f"Commande eedomus non directe: {raw['peripherique']} "
            f"({raw['peripherique_id']})"
        )
    domain = entity.entity_id.partition(".")[0]
    value = str(raw["valeur"])
    state = str(raw.get("etat") or "").casefold()
    if domain == "climate":
        try:
            temperature = float(value)
        except ValueError as exc:
            raise EedomusImportError(f"Consigne chauffage invalide: {value}") from exc
        if not -50 <= temperature <= 80:
            raise EedomusImportError(f"Consigne chauffage hors limite: {value}")
        return {
            "action": "climate.set_temperature",
            "target": {"entity_id": entity.entity_id},
            "data": {"temperature": temperature},
        }
    if domain == "cover":
        if value == "100" and state in ("ouvert", "open"):
            service = "cover.open_cover"
        elif value == "0" and state in ("fermé", "ferme", "closed"):
            service = "cover.close_cover"
        else:
            # A 0/100 eedomus value may have other meanings for a different
            # cover; avoid assuming a percentage without a confirmed label.
            raise EedomusImportError(
                f"Commande volet non reconnue pour « {raw['peripherique']} » "
                f"(ID eedomus {raw['peripherique_id']}, entité HA {entity.entity_id}) : "
                f"valeur {value!r}, état {raw.get('etat')!r}. "
                "Attendu : 100/Ouvert ou 0/Fermé."
            )
        return {"action": service, "target": {"entity_id": entity.entity_id}}
    if domain in ("light", "switch", "input_boolean"):
        if value == "0" and state in (
            "off",
            "désactivé",
            "desactive",
            "éteint",
            "eteint",
        ):
            service = "turn_off"
        elif value in ("1", "100") and state in (
            "on",
            "activé",
            "active",
            "allumé",
            "allume",
        ):
            service = "turn_on"
        elif value == "100" and state in ("ouvert", "ouverte", "open"):
            # eedomus can expose a roller shutter command as a switch/light,
            # rather than a HA cover. Respect the exact 100/Ouvert mapping.
            service = "turn_on"
        elif value == "0" and state in ("fermé", "fermée", "ferme", "fermee", "closed"):
            service = "turn_off"
        else:
            raise EedomusImportError(
                f"Commande binaire non reconnue pour « {raw['peripherique']} » "
                f"(ID eedomus {raw['peripherique_id']}, entité HA {entity.entity_id}) : "
                f"valeur {value!r}, état {raw.get('etat')!r}. "
                "Attendu : 0/Off, 1/On, 100/On ou 0/Fermé, 100/Ouvert."
            )
        return {
            "action": f"{domain}.{service}",
            "target": {"entity_id": entity.entity_id},
        }
    raise EedomusImportError(
        f"Entité {entity.entity_id} non prise en charge pour "
        f"{raw['peripherique']} [{raw['peripherique_id']}]"
    )


def _mapped_action(
    raw: dict, by_device_id: dict[str, list]
) -> tuple[dict | None, list[tuple[str, str, str]]]:
    """Return one safe HA action and all associations that cannot be imported.

    A mapped but unsupported domain/service is informational, not fatal.
    Missing, disabled or ambiguous controllable entities remain fatal to avoid
    guessing a target or silently masking registry errors.
    """
    device_id = str(raw["peripherique_id"])
    label = f"{raw['peripherique']} [{device_id}]"
    # A macro/non-direct command cannot be translated to a HA service.
    if raw.get("type_action") != "direct":
        return None, [
            (label, "—", f"Type d'action non pris en charge : {raw.get('type_action')}")
        ]

    candidates = by_device_id.get(device_id, [])
    supported = {"climate", "cover", "light", "switch", "input_boolean"}
    entries = [e for e in candidates if e.entity_id.partition(".")[0] in supported]
    unsupported = [
        (
            label,
            e.entity_id,
            f"Domaine {e.entity_id.partition('.')[0]} non pris en charge",
        )
        for e in candidates
        if e.entity_id.partition(".")[0] not in supported
    ]
    if not entries and unsupported:
        # An associated sensor or another unsupported entity is *not* an
        # importable command, but the moment must still be created.
        return None, unsupported
    if len(entries) != 1:
        raise EedomusImportError(
            f"{raw['peripherique']} [{device_id}]: "
            f"{len(entries)} entité(s) HA utilisable(s) pour la box choisie"
        )
    if entries[0].disabled_by is not None:
        raise EedomusImportError(f"Entité désactivée : {entries[0].entity_id}")
    try:
        service = _convert_service(raw, entries[0])
    except EedomusImportError as exc:
        # A recognized entity with an unknown command/value is also skipped.
        # The reason is explicit in the confirmation, never silently lost.
        return None, [*unsupported, (label, entries[0].entity_id, str(exc))]
    return service, unsupported


def _audit(old: Any | None, actor: str) -> Audit:
    now = datetime.now(timezone.utc)
    existing = getattr(old, "audit", None)
    if existing is None:
        return Audit(actor, now, actor, now)
    return replace(existing, modified_by=actor, modified_at=now)


def _merged(
    old: tuple, imported: list, prefixes: tuple[str, ...], replace_existing: bool
) -> tuple:
    """Replace this box's current and legacy imports, never manual objects."""
    owned = [item for item in old if item.id.startswith(prefixes)]
    if owned and not replace_existing:
        raise EedomusImportError("Import eedomus existant : confirmation nécessaire")
    remainder = [item for item in old if not item.id.startswith(prefixes)]
    return tuple((*remainder, *imported))


def create_import_plan(
    agenda: dict,
    existing: PlannerConfiguration,
    source_entry_id: str,
    entity_map: dict[str, list],
    *,
    replace_existing: bool = False,
    actor: str = "system",
    max_cycles: int = 3,
    week_name: str | None = None,
) -> ImportPlan:
    """Build a deterministic complete import with no write or side effect."""
    # The box name (from api_host) is part of both the display name and the
    # Day Planner object IDs. Keep the HA config entry ID only for matching
    # HA entities and for recognizing imports made by older versions.
    source_name = week_name.strip() if isinstance(week_name, str) else ""
    prefix = _namespace(source_name)
    legacy_prefix = _legacy_namespace(source_entry_id)
    owned_prefixes = (prefix, legacy_prefix)
    previous = {
        kind: {item.id: item for item in getattr(existing, kind)}
        for kind in ("moments", "day_types", "week_schedules")
    }

    def prior(kind: str, object_id: str) -> Any | None:
        """Find original audit under either the new or the old ID."""
        objects = previous[kind]
        return objects.get(object_id) or objects.get(
            legacy_prefix + object_id.removeprefix(prefix)
        )

    had_previous = any(
        item_id.startswith(owned_prefixes)
        for objects in previous.values()
        for item_id in objects
    )
    if had_previous and not replace_existing:
        raise EedomusImportError("Import eedomus existant : confirmation nécessaire")
    suffix = f" — {source_name}"
    phase_actions = {}
    phase_names = {}
    max_repeat = {}
    for day in agenda["day_types"]:
        seen = {}
        for moment in sorted(
            day["moments"], key=lambda item: (item["heure"], item["phase_id"])
        ):
            if not moment["regle_horaire_active"]:
                raise EedomusImportError(
                    f"Règle horaire désactivée : {moment['regle_horaire_id']}"
                )
            phase = str(moment["phase_id"])
            actions = moment["actions"] if moment["regle_actions_active"] else []
            # Even a phase with no active or compatible actions remains a
            # scheduled Day Planner moment; it may be completed manually.
            signature = tuple(
                (str(a["peripherique_id"]), a["type_action"], str(a["valeur"]))
                for a in actions
            )
            if phase in phase_actions and phase_actions[phase][0] != signature:
                raise EedomusImportError(f"Actions incohérentes pour la phase {phase}")
            phase_actions[phase] = (signature, actions)
            phase_names[phase] = str(moment["phase"])
            seen[phase] = seen.get(phase, 0) + 1
            max_repeat[phase] = max(max_repeat.get(phase, 0), seen[phase])

    moments = []
    mapped_entities: set[str] = set()
    unsupported_associations: set[tuple[str, str, str]] = set()
    for phase, name in sorted(phase_names.items(), key=lambda p: int(p[0])):
        actions = []
        for raw in phase_actions[phase][1]:
            service, skipped = _mapped_action(raw, entity_map)
            unsupported_associations.update(skipped)
            if service is None:
                continue
            mapped_entities.add(
                f"{raw['peripherique']} [{raw['peripherique_id']}] → "
                f"{service['target']['entity_id']}"
            )
            actions.append(
                Action(
                    id=f"{prefix}phase_{phase}_action_{len(actions) + 1}",
                    label=f"{raw['quoi_faire']}{suffix}",
                    sequence=[service],
                )
            )
        for occurrence in range(1, max_repeat[phase] + 1):
            moment_id = f"{prefix}phase_{phase}"
            if occurrence > 1:
                moment_id += f"_repeat_{occurrence}"
            moment_name = (
                name
                + (f" (occurrence {occurrence})" if occurrence > 1 else "")
                + suffix
            )
            # Repeated moments must receive distinct action instances with
            # distinct IDs, though commands remain identical.
            indexed_actions = tuple(
                replace(action, id=f"{moment_id}_action_{index}")
                for index, action in enumerate(actions, 1)
            )
            previous_moment = prior("moments", moment_id)
            moments.append(
                Moment(
                    id=moment_id,
                    name=moment_name,
                    actions=indexed_actions,
                    audit=_audit(previous_moment, actor),
                )
            )

    day_types = []
    for day in agenda["day_types"]:
        day_id = f"{prefix}day_{day['id']}"
        seen = {}
        scheduled = []
        for item in sorted(day["moments"], key=lambda m: (m["heure"], m["phase_id"])):
            phase = str(item["phase_id"])
            seen[phase] = seen.get(phase, 0) + 1
            moment_id = f"{prefix}phase_{phase}"
            if seen[phase] > 1:
                moment_id += f"_repeat_{seen[phase]}"
            scheduled.append(
                ScheduledMoment(
                    moment_id=moment_id,
                    time_definition=TimeDefinition(
                        fixed_time=time.fromisoformat(item["heure"])
                    ),
                )
            )
        day_types.append(
            DayType(
                id=day_id,
                name=day["name"] + suffix,
                scheduled_moments=tuple(scheduled),
                audit=_audit(prior("day_types", day_id), actor),
            )
        )

    by_weekday = {
        int(item["jour_numero"]): int(item["type_journee_id"])
        for item in agenda["week"]
    }
    if sorted(by_weekday) != list(range(1, 8)):
        raise EedomusImportError(
            "La semaine eedomus ne contient pas sept jours distincts"
        )
    week_id = f"{prefix}week"
    week = WeekSchedule(
        id=week_id,
        name=source_name,
        **{
            day: f"{prefix}day_{by_weekday[index]}"
            for index, day in enumerate(WEEKDAYS, 1)
        },
        audit=_audit(prior("week_schedules", week_id), actor),
    )
    merged = replace(
        existing,
        moments=_merged(existing.moments, moments, owned_prefixes, replace_existing),
        day_types=_merged(
            existing.day_types, day_types, owned_prefixes, replace_existing
        ),
        week_schedules=_merged(
            existing.week_schedules, [week], owned_prefixes, replace_existing
        ),
    )
    try:
        PlannerValidator.validate_configuration(merged, max_cycles=max_cycles)
    except (ValueError, ValidationError) as exc:
        raise EedomusImportError(
            f"Configuration Day Planner incompatible : {exc}"
        ) from exc
    return ImportPlan(
        configuration=merged,
        source_entry_id=source_entry_id,
        replace_existing=replace_existing,
        had_previous_import=had_previous,
        day_types=len(day_types),
        moments=len(moments),
        scheduled=sum(len(d.scheduled_moments) for d in day_types),
        actions=sum(len(m.actions) for m in moments),
        conditional_rules_not_imported=sum(
            bool(rule["active"])
            for rule in agenda["regles_conditionnelles_liees_agenda"]
        ),
        unresolved_embedded_parameters=len(agenda["parametres_embarques_non_resolus"]),
        mapped_entities=tuple(sorted(mapped_entities)),
        unsupported_associations=tuple(sorted(unsupported_associations)),
        moments_without_actions=sum(not moment.actions for moment in moments),
    )


def prepare_import(hass: Any, source_entry_id: str, path: Path) -> dict:
    """Parse a temporary JSON uploaded by the Home Assistant file picker."""
    data = load_export(path)
    return extract(data)
