#!/usr/bin/env python3
"""Extraction ponctuelle de l'agenda eedomus depuis un export JSON local.

Usage :
    python3 eedomus_agenda_extract.py export_eedomus.json
    python3 eedomus_agenda_extract.py export_eedomus.json -o agenda.json --csv agenda.csv

Produit un JSON et un CSV : types de journée, semaine type, phases, heures et
« quoi faire » (actions sur périphériques). Préserve séparément les règles
conditionnelles liées à l'agenda ; ne les transforme pas en actions certaines.

Aucun accès réseau, aucune synchronisation, aucune écriture sur eedomus ou HA.
La sortie ne reprend pas les paramètres privés des périphériques, URL ou clés.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from datetime import time
from pathlib import Path


class ExportFormatError(ValueError):
    """L'export n'a pas la structure attendue."""


def load_export(path: Path) -> dict:
    raw = path.read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    result = json.loads(content)
    if not isinstance(result, dict) or not isinstance(result.get("tables"), list):
        raise ExportFormatError("Le JSON ne contient pas la liste 'tables'")
    return result


def get_table(export: dict, name: str) -> list[dict]:
    found = [t for t in export["tables"] if t.get("table") == name]
    if len(found) != 1 or not isinstance(found[0].get("lines"), list):
        raise ExportFormatError(f"Table absente ou dupliquée : {name}")
    return found[0]["lines"]


def subtable(row: dict, name: str) -> list[dict]:
    found = [t for t in row.get("subtables", []) if t.get("table") == name]
    if len(found) != 1:
        raise ExportFormatError(f"Sous-table absente ou dupliquée : {name}")
    return found[0]["lines"]


def hhmmss(raw: str) -> str:
    try:
        value = time.fromisoformat(raw)
    except (ValueError, TypeError) as exc:
        raise ExportFormatError(f"Heure invalide : {raw!r}") from exc
    if value.tzinfo is not None or value.microsecond:
        raise ExportFormatError(f"Heure non prise en charge : {raw!r}")
    return value.strftime("%H:%M:%S")


def find_module(modules: list[dict], name: str, purpose: str) -> dict:
    exact = [m for m in modules if m.get("custom_name", "").casefold() == name.casefold()]
    if not exact:
        exact = [m for m in modules if m.get("utilisation_id") == purpose]
    if len(exact) != 1:
        raise ExportFormatError(f"Impossible d'identifier le périphérique : {name}")
    return exact[0]


def states(module: dict) -> dict[str, str]:
    rows = subtable(module, "zb_controller_module_value_descr")
    result = {str(row["value"]): row["state"] for row in rows}
    if not result or len(result) != len(rows):
        raise ExportFormatError("Valeurs de périphérique vides ou dupliquées")
    return result


def ordered_rows(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: int(x.get("order_by", "0")))


def extract(export: dict) -> dict:
    modules_list = get_table(export, "zb_controller_module")
    modules = {m["controller_module_id"]: m for m in modules_list}
    if len(modules) != len(modules_list):
        raise ExportFormatError("Identifiants de périphérique dupliqués")

    day_module = find_module(modules_list, "Journée en cours", "18")
    phase_module = find_module(modules_list, "Phase de la journée", "34")
    day_mid, phase_mid = (
        day_module["controller_module_id"],
        phase_module["controller_module_id"],
    )
    day_states, phase_states = states(day_module), states(phase_module)
    week_rows = get_table(export, "zb_controller_week")
    schedule_rows = get_table(export, "zb_controller_week_day_phase")
    rules = get_table(export, "zb_controller_rule")

    def action_details(action: dict) -> dict:
        mid = str(action["controller_module_id"])
        module = modules.get(mid)
        kind = str(action["action_type"])
        raw_value = str(action["action"])
        name = (module.get("custom_name") or module.get("full_name") or mid) if module else f"Inconnu ({mid})"
        resolved = None
        if module is not None and kind == "direct":
            try:
                resolved = states(module).get(raw_value)
            except ExportFormatError:
                # Un module numérique peut n'avoir aucune liste d'états.
                resolved = None
        if kind == "macro":
            macro_name = None
            if module is not None:
                for macro in subtable(module, "zb_controller_module_macro"):
                    if str(macro.get("macro_id")) == raw_value:
                        macro_name = macro.get("name")
                        break
            readable = f"Exécuter macro {macro_name or raw_value} sur {name}"
        elif kind == "direct":
            readable = f"{name} → {resolved if resolved is not None else raw_value}"
        else:
            readable = f"{name} → {kind} ({raw_value})"
        return {
            "peripherique_id": mid,
            "peripherique": name,
            "type_action": kind,
            "valeur": raw_value,
            "etat": resolved,
            "quoi_faire": readable,
        }

    # Règles horaires : une règle type 3 choisit le type de journée et
    # affecte une phase à l'heure donnée. Ne pas déduire le lien du nom du titre.
    timed_rules: dict[tuple[str, str, str], dict] = {}
    phase_rules: dict[str, dict] = {}
    conditional_rules = []
    for rule in rules:
        criteria = subtable(rule, "zb_rule_criteria")
        actions = subtable(rule, "zb_rule_action")
        crons = subtable(rule, "zb_rule_cron")
        rtype = str(rule["rule_type_id"])
        if (
            rtype == "3"
            and len(criteria) == len(actions) == len(crons) == 1
            and str(criteria[0]["controller_module_id"]) == day_mid
            and criteria[0]["criteria"] == "=="
            and str(actions[0]["controller_module_id"]) == phase_mid
            and actions[0]["action_type"] == "direct"
        ):
            cron = crons[0]
            key = (
                str(criteria[0]["target"]),
                str(actions[0]["action"]),
                f"{int(cron['hour']):02}:{int(cron['minute']):02}:00",
            )
            if key in timed_rules:
                raise ExportFormatError(f"Règle horaire dupliquée pour {key}")
            timed_rules[key] = rule
            continue

        # Une règle type 5 avec critère de transition de phase déclenche le
        # « quoi faire » sur les périphériques. Pour chaque phase, une seule.
        if (
            rtype == "5"
            and len(criteria) == 1
            and str(criteria[0]["controller_module_id"]) == phase_mid
            and criteria[0]["criteria"] == "=="
            and criteria[0]["type"] == "d"
            and not crons
        ):
            phase = str(criteria[0]["target"])
            if phase in phase_rules:
                raise ExportFormatError(f"Plusieurs règles directes pour la phase {phase}")
            phase_rules[phase] = rule
            continue

        # Règles supplémentaires impliquant phase ou type de journée : leur
        # logique ET/OU et d'autres critères doivent être conservés intacts.
        if not any(str(c["controller_module_id"]) in (day_mid, phase_mid) for c in criteria):
            continue
        decoded_criteria = []
        for c in sorted(criteria, key=lambda x: int(x.get("criteria_order", 0))):
            mid = str(c["controller_module_id"])
            module = modules.get(mid)
            target = str(c["target"])
            if mid == day_mid:
                target_name = day_states.get(target, target)
            elif mid == phase_mid:
                target_name = phase_states.get(target, target)
            elif module is not None:
                try:
                    target_name = states(module).get(target, target)
                except ExportFormatError:
                    target_name = target
            else:
                target_name = target
            decoded_criteria.append(
                {
                    "ordre": int(c.get("criteria_order", 0)),
                    "peripherique_id": mid,
                    "peripherique": (
                        (module.get("custom_name") or module.get("full_name") or mid) if module else f"Inconnu ({mid})"
                    ),
                    "operateur": c["criteria"],
                    "valeur": target,
                    "valeur_libelle": target_name,
                    "liaison": c.get("operation"),
                    "type_critere": c.get("type"),
                }
            )
        conditional_rules.append(
            {
                "id": str(rule["rule_id"]),
                "nom": rule["name"],
                "active": rule["active"] == "1",
                "type_regle": rtype,
                "conditions": decoded_criteria,
                "horaires_ou_crons": [
                    {
                        "jour_semaine": c["day_of_week"],
                        "heure": c["hour"],
                        "minute": c["minute"],
                    }
                    for c in crons
                ],
                "actions": [action_details(a) for a in ordered_rows(actions)],
            }
        )

    days = {
        k: {"id": int(k), "name": name, "moments": []}
        for k, name in sorted(day_states.items(), key=lambda x: int(x[0]))
    }
    used_timed_rules = set()
    for scheduled in schedule_rows:
        day_id = str(scheduled["day_type_id"])
        phase_id = str(scheduled["phase_id"])
        at = hhmmss(scheduled["start_time"])
        if day_id not in days or phase_id not in phase_states:
            raise ExportFormatError(f"Type de journée / phase inconnu : {day_id}/{phase_id}")
        key = (day_id, phase_id, at)
        rule = timed_rules.get(key)
        if rule is None:
            raise ExportFormatError(f"Règle horaire introuvable : {key}")
        used_timed_rules.add(key)
        phase_rule = phase_rules.get(phase_id)
        if phase_rule is None:
            raise ExportFormatError(f"Règle d'actions introuvable pour la phase {phase_id}")
        phase_actions = (
            [action_details(a) for a in ordered_rows(subtable(phase_rule, "zb_rule_action"))]
            if phase_rule["active"] == "1"
            else []
        )
        days[day_id]["moments"].append(
            {
                "heure": at,
                "phase_id": int(phase_id),
                "phase": phase_states[phase_id],
                "regle_horaire_id": str(rule["rule_id"]),
                "regle_horaire_active": rule["active"] == "1",
                "regle_actions_id": str(phase_rule["rule_id"]),
                "regle_actions_active": phase_rule["active"] == "1",
                "quoi_faire": [a["quoi_faire"] for a in phase_actions],
                "actions": phase_actions,
            }
        )

    extra_timed = set(timed_rules) - used_timed_rules
    if extra_timed:
        raise ExportFormatError(f"Règles horaires non reliées : {len(extra_timed)}")
    for value in days.values():
        value["moments"].sort(key=lambda x: (x["heure"], x["phase_id"]))

    weekday_names = (
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
        "Dimanche",
    )
    week = []
    seen = set()
    for row in week_rows:
        index = int(row["day_of_week"])
        day_id = str(row["day_type_id"])
        if index not in range(1, 8) or index in seen or day_id not in days:
            raise ExportFormatError(f"Jour de la semaine ou type invalide : {index}/{day_id}")
        seen.add(index)
        week.append(
            {
                "jour_numero": index,
                "jour": weekday_names[index - 1],
                "type_journee_id": int(day_id),
                "type_journee": days[day_id]["name"],
            }
        )
    week.sort(key=lambda row: row["jour_numero"])
    if len(week) != 7:
        raise ExportFormatError("La semaine type n'a pas exactement sept jours")

    # Certains paramètres codés dans l'état eedomus ne correspondent pas à
    # une action directe : conserver le code sans lui inventer une signification.
    unknown_embedded = []
    for state in subtable(phase_module, "zb_controller_module_value_descr"):
        phase_id = str(state["value"])
        embedded = json.loads(state.get("http_params") or "[]")
        rule = phase_rules.get(phase_id)
        if not rule:
            continue
        expected = {
            (str(a["controller_module_id"]), str(a["action"]))
            for a in subtable(rule, "zb_rule_action")
            if a["action_type"] == "direct"
        }
        if not isinstance(embedded, list):
            raise ExportFormatError(f"Paramètres de phase invalides : {phase_id}")
        for pair in embedded:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ExportFormatError(f"Paramètre de phase invalide : {phase_id}")
            pid, value = str(pair[0]), str(pair[1])
            if (pid, value) not in expected:
                unknown_embedded.append(
                    {
                        "phase_id": int(phase_id),
                        "phase": phase_states[phase_id],
                        "cible_brute": pid,
                        "valeur_brute": value,
                        "note": "Paramètre interne non identifié comme une action directe de la règle de phase",
                    }
                )

    return {
        "schema": "eedomus-agenda-extract-v2",
        "export_time": export.get("export_time"),
        "phases": [{"id": int(k), "name": v} for k, v in sorted(phase_states.items(), key=lambda x: int(x[0]))],
        "day_types": list(days.values()),
        "week": week,
        "regles_conditionnelles_liees_agenda": sorted(conditional_rules, key=lambda x: x["nom"].casefold()),
        "parametres_embarques_non_resolus": unknown_embedded,
        "notes": [
            "Extraction ponctuelle en lecture seule, sans automatisation ni synchronisation",
            "Les actions sont celles des règles de phase actives ; leur exécution dépend des conditions eedomus",
            "Les règles conditionnelles supplémentaires restent séparées : ne pas les exécuter systématiquement",
            "Aucune exception de calendrier n'est prise en charge",
        ],
    }


def make_csv(agenda: dict) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        (
            "ID type journée",
            "Type journée",
            "Jours semaine",
            "Heure",
            "Phase",
            "Quoi faire",
            "Règle horaire ID",
            "Règle horaire active",
            "Règle actions ID",
            "Règle actions active",
        )
    )
    for day in agenda["day_types"]:
        used = ", ".join(row["jour"] for row in agenda["week"] if row["type_journee_id"] == day["id"])
        for moment in day["moments"]:
            writer.writerow(
                (
                    day["id"],
                    day["name"],
                    used,
                    moment["heure"],
                    moment["phase"],
                    " | ".join(moment["quoi_faire"]),
                    moment["regle_horaire_id"],
                    int(moment["regle_horaire_active"]),
                    moment["regle_actions_id"],
                    int(moment["regle_actions_active"]),
                )
            )
    return buffer.getvalue()


def write_if_changed(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_text(encoding="utf-8-sig") == content:
        return
    tmp = destination.with_name(destination.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("export", type=Path, help="Export eedomus JSON (UTF-8 ou Windows-1252)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("agenda_eedomus.json"),
        help="JSON de sortie",
    )
    parser.add_argument("--csv", type=Path, default=Path("agenda_eedomus.csv"), help="CSV de sortie")
    args = parser.parse_args()
    if args.output.resolve() == args.csv.resolve() or args.export.resolve() in (
        args.output.resolve(),
        args.csv.resolve(),
    ):
        parser.error("Les fichiers d'entrée et de sortie doivent être différents")
    try:
        agenda = extract(load_export(args.export))
        write_if_changed(args.output, json.dumps(agenda, ensure_ascii=False, indent=2) + "\n")
        write_if_changed(args.csv, make_csv(agenda))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Erreur : {exc}\n")
    print("Export :", agenda["export_time"])
    print("Types de journée :", len(agenda["day_types"]))
    print("Jours dans la semaine type :", len(agenda["week"]))
    print("Phases :", len(agenda["phases"]))
    print("Horaires programmés :", sum(len(d["moments"]) for d in agenda["day_types"]))
    print(
        "Règles supplémentaires liées à l'agenda :",
        len(agenda["regles_conditionnelles_liees_agenda"]),
    )
    print("Paramètres non résolus :", len(agenda["parametres_embarques_non_resolus"]))
    print("JSON :", args.output)
    print("CSV :", args.csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
