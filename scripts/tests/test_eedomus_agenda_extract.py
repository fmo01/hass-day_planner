"""Exhaustive validation of eedomus JSON extraction (no HA connection needed).

Exercises actual conversion paths, malformed exports and CLI. The synthetic
source has the same table/subtable layout as a native eedomus JSON export.
"""

import json
import runpy
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from custom_components.day_planner import eedomus_agenda_extract as agenda_extract


def table(name, rows):
    return {"table": name, "lines": rows}


def rule(rule_id, rule_type, criterion, actions, crons=(), *, active="1", name=None):
    return {
        "rule_id": str(rule_id),
        "rule_type_id": str(rule_type),
        "name": name or f"Rule {rule_id}",
        "active": active,
        "subtables": [
            table("zb_rule_criteria", list(criterion)),
            table("zb_rule_action", list(actions)),
            table("zb_rule_cron", list(crons)),
        ],
    }


def criterion(module, target, *, criteria="==", kind="d", order=0, operation="AND"):
    return {
        "controller_module_id": str(module),
        "target": str(target),
        "criteria": criteria,
        "type": kind,
        "criteria_order": str(order),
        "operation": operation,
    }


def action(module, value, kind="direct", order=0):
    return {
        "controller_module_id": str(module),
        "action": str(value),
        "action_type": kind,
        "order_by": str(order),
    }


def module(module_id, name, states=None, *, use="0", macros=None, http_params=None):
    rows = []
    for key, name_value in (states or {}).items():
        record = {"value": str(key), "state": name_value}
        if http_params is not None:
            record["http_params"] = http_params.get(str(key), "[]")
        rows.append(record)
    subtables = [table("zb_controller_module_value_descr", rows)]
    if macros is not None:
        subtables.append(table("zb_controller_module_macro", macros))
    return {
        "controller_module_id": str(module_id),
        "custom_name": name,
        "full_name": name,
        "utilisation_id": use,
        "subtables": subtables,
    }


def export_fixture():
    modules = [
        module(10, "Journée en cours", {"1": "Travail", "2": "Repos"}, use="18"),
        module(
            20,
            "Phase de la journée",
            {"5": "Lever", "6": "Couché"},
            use="34",
            http_params={"5": '[["30", "100"], ["999", "42"]]'},
        ),
        module(30, "Guirlande", {"0": "Off", "100": "On"}),
        module(40, "Consigne chauffage", {}),
        module(50, "Macro", {}, macros=[{"macro_id": "12", "name": "Bonne nuit"}]),
    ]
    week = [{"day_of_week": str(i), "day_type_id": "1"} for i in range(1, 8)]
    times = [
        {"day_type_id": "1", "phase_id": "5", "start_time": "06:30:00"},
        {"day_type_id": "1", "phase_id": "6", "start_time": "22:00:00"},
    ]
    timed = [
        rule(
            100,
            3,
            [criterion(10, 1)],
            [action(20, 5)],
            [{"hour": "6", "minute": "30", "day_of_week": "1"}],
        ),
        rule(
            101,
            3,
            [criterion(10, 1)],
            [action(20, 6)],
            [{"hour": "22", "minute": "0", "day_of_week": "1"}],
        ),
    ]
    phases = [
        rule(
            200,
            5,
            [criterion(20, 5)],
            [action(30, 100, order=2), action(40, 22, order=1)],
        ),
        rule(201, 5, [criterion(20, 6)], [action(30, 0)], active="0"),
    ]
    conditional = rule(
        300,
        7,
        [
            criterion(20, 5, kind="e", order=3),
            criterion(30, 100, kind="e", order=1),
            criterion(777, 3, kind="e", order=2),
        ],
        [action(50, 12, kind="macro", order=0), action(30, 0, kind="unknown", order=1)],
        [{"hour": "7", "minute": "0", "day_of_week": "-1"}],
        name="Extra conditional",
    )
    other = rule(400, 7, [criterion(30, 100, kind="e")], [action(30, 0)])
    return {
        "export_time": "2026-11-01 18:02:44",
        "tables": [
            table("zb_controller_module", modules),
            table("zb_controller_week", week),
            table("zb_controller_week_day_phase", times),
            table("zb_controller_rule", timed + phases + [conditional, other]),
        ],
    }


def rows(data, name):
    return next(t["lines"] for t in data["tables"] if t["table"] == name)


def nested(obj, name):
    return next(t["lines"] for t in obj["subtables"] if t["table"] == name)


def test_extract_full_valid_export_with_conditional_macro_unknown_actions():
    result = agenda_extract.extract(export_fixture())
    assert result["schema"] == "eedomus-agenda-extract-v2"
    assert len(result["phases"]) == 2 and len(result["day_types"]) == 2
    assert len(result["week"]) == 7
    work = result["day_types"][0]
    assert [moment["heure"] for moment in work["moments"]] == ["06:30:00", "22:00:00"]
    assert work["moments"][0]["quoi_faire"] == [
        "Consigne chauffage → 22",
        "Guirlande → On",
    ]
    assert work["moments"][1]["actions"] == []
    conditional = result["regles_conditionnelles_liees_agenda"]
    assert len(conditional) == 1 and conditional[0]["id"] == "300"
    assert conditional[0]["conditions"][0]["peripherique"] == "Guirlande"
    assert conditional[0]["conditions"][1]["peripherique"] == "Inconnu (777)"
    assert conditional[0]["conditions"][2]["valeur_libelle"] == "Lever"
    assert conditional[0]["actions"][0]["quoi_faire"] == "Exécuter macro Bonne nuit sur Macro"
    assert conditional[0]["actions"][1]["quoi_faire"] == "Guirlande → unknown (0)"
    assert conditional[0]["horaires_ou_crons"] == [{"jour_semaine": "-1", "heure": "7", "minute": "0"}]
    assert result["parametres_embarques_non_resolus"] == [
        {
            "phase_id": 5,
            "phase": "Lever",
            "cible_brute": "999",
            "valeur_brute": "42",
            "note": "Paramètre interne non identifié comme une action directe de la règle de phase",
        }
    ]
    assert len(result["notes"]) == 4
    csv_data = agenda_extract.make_csv(result)
    assert csv_data.count("\n") == 3
    assert "Consigne chauffage" in csv_data
    assert "Travail" in csv_data
    assert "Lundi" in csv_data
    assert "Couché" in csv_data


def test_helper_lookups_and_sorting():
    data = export_fixture()
    assert len(agenda_extract.get_table(data, "zb_controller_week")) == 7
    assert agenda_extract.subtable(rows(data, "zb_controller_rule")[0], "zb_rule_action")
    modules = rows(data, "zb_controller_module")
    assert agenda_extract.find_module(modules, "JOURNÉE EN COURS", "nonexistent") is modules[0]
    assert agenda_extract.find_module(modules, "absent", "34") is modules[1]
    assert agenda_extract.states(modules[0]) == {"1": "Travail", "2": "Repos"}
    sorted_rows = agenda_extract.ordered_rows([{"order_by": "11"}, {"order_by": "2"}])
    assert sorted_rows[0]["order_by"] == "2"
    assert agenda_extract.hhmmss("09:01:08") == "09:01:08"


@pytest.mark.parametrize("bad", ["not an hour", None, "25:00:00", "12:00:00+02:00", "12:00:00.100000"])
def test_bad_time(bad):
    with pytest.raises(agenda_extract.ExportFormatError, match="Heure"):
        agenda_extract.hhmmss(bad)


@pytest.mark.parametrize(
    "table_name",
    [
        "zb_controller_module",
        "zb_controller_week",
        "zb_controller_week_day_phase",
        "zb_controller_rule",
    ],
)
def test_missing_and_duplicate_table(table_name):
    data = export_fixture()
    data["tables"] = [row for row in data["tables"] if row["table"] != table_name]
    with pytest.raises(agenda_extract.ExportFormatError, match="Table absente"):
        agenda_extract.extract(data)
    data = export_fixture()
    source = next(row for row in data["tables"] if row["table"] == table_name)
    data["tables"].append(deepcopy(source))
    with pytest.raises(agenda_extract.ExportFormatError, match="dupliquée"):
        agenda_extract.extract(data)


def test_malformed_subtables_and_helper_errors():
    data = export_fixture()
    module_row = rows(data, "zb_controller_module")[0]
    with pytest.raises(agenda_extract.ExportFormatError, match="Sous-table"):
        agenda_extract.subtable(module_row, "unknown")
    module_row["subtables"].append(deepcopy(module_row["subtables"][0]))
    with pytest.raises(agenda_extract.ExportFormatError, match="Sous-table"):
        agenda_extract.states(module_row)
    module_row["subtables"].pop()
    module_row["subtables"][0]["lines"] = []
    with pytest.raises(agenda_extract.ExportFormatError, match="vides"):
        agenda_extract.states(module_row)
    module_row["subtables"][0]["lines"] = [
        {"value": "1", "state": "A"},
        {"value": "1", "state": "B"},
    ]
    with pytest.raises(agenda_extract.ExportFormatError, match="dupliquées"):
        agenda_extract.states(module_row)


@pytest.mark.parametrize(
    "mutation,pattern",
    [
        (
            lambda d: rows(d, "zb_controller_module").append(deepcopy(rows(d, "zb_controller_module")[0])),
            "dupliqués",
        ),
        (
            lambda d: rows(d, "zb_controller_module")[0].update(custom_name="Autre", utilisation_id="999"),
            "identifier",
        ),
        (
            lambda d: rows(d, "zb_controller_week_day_phase")[0].update(phase_id="999"),
            "inconnu",
        ),
        (
            lambda d: rows(d, "zb_controller_week_day_phase")[0].update(day_type_id="999"),
            "inconnu",
        ),
        (
            lambda d: rows(d, "zb_controller_week_day_phase")[0].update(start_time="bad"),
            "Heure",
        ),
        (
            lambda d: rows(d, "zb_controller_week_day_phase")[0].update(start_time="06:31:00"),
            "introuvable",
        ),
        (
            lambda d: rows(d, "zb_controller_rule")[0]["subtables"][2]["lines"][0].update(hour="7"),
            "introuvable",
        ),
        (
            lambda d: rows(d, "zb_controller_rule").append(deepcopy(rows(d, "zb_controller_rule")[0])),
            "dupliquée",
        ),
        (
            lambda d: rows(d, "zb_controller_rule").append(deepcopy(rows(d, "zb_controller_rule")[2])),
            "Plusieurs règles directes",
        ),
        (
            lambda d: rows(d, "zb_controller_rule")[2].update(rule_type_id="1"),
            "introuvable pour la phase",
        ),
        (
            lambda d: rows(d, "zb_controller_week")[0].update(day_of_week="8"),
            "invalide",
        ),
        (
            lambda d: rows(d, "zb_controller_week")[0].update(day_type_id="999"),
            "invalide",
        ),
        (
            lambda d: rows(d, "zb_controller_week")[0].update(day_of_week="2"),
            "invalide",
        ),
        (lambda d: rows(d, "zb_controller_week").pop(), "sept jours"),
        (
            lambda d: nested(rows(d, "zb_controller_module")[1], "zb_controller_module_value_descr")[0].update(
                http_params='"not-list"'
            ),
            "invalides",
        ),
        (
            lambda d: nested(rows(d, "zb_controller_module")[1], "zb_controller_module_value_descr")[0].update(
                http_params='["not-pair"]'
            ),
            "invalide",
        ),
    ],
)
def test_reject_invalid_export(mutation, pattern):
    data = export_fixture()
    mutation(data)
    with pytest.raises(agenda_extract.ExportFormatError, match=pattern):
        agenda_extract.extract(data)


def test_extra_timed_rule_is_rejected():
    data = export_fixture()
    rows(data, "zb_controller_week_day_phase").pop()
    with pytest.raises(agenda_extract.ExportFormatError, match="non reliées"):
        agenda_extract.extract(data)


def test_unknown_embedded_parameter_ignored_when_no_phase_rule():
    data = export_fixture()
    rows(data, "zb_controller_rule")[2]["subtables"][0]["lines"][0]["type"] = "e"
    # This now leaves phase 5 with no rule: extraction should reject missing rule.
    with pytest.raises(agenda_extract.ExportFormatError, match="introuvable"):
        agenda_extract.extract(data)


def test_macros_fallback_and_unknown_module_in_conditional_rule():
    data = export_fixture()
    conditional = rows(data, "zb_controller_rule")[4]
    nested(conditional, "zb_rule_action")[0]["action"] = "1234"
    nested(conditional, "zb_rule_action").append(action(888, 1, order=3))
    out = agenda_extract.extract(data)["regles_conditionnelles_liees_agenda"][0]
    assert out["actions"][0]["quoi_faire"] == "Exécuter macro 1234 sur Macro"
    assert out["actions"][2]["quoi_faire"] == "Inconnu (888) → 1"


def test_load_export_utf8_bom_cp1252_and_errors(tmp_path):
    file = tmp_path / "export.json"
    value = {"tables": []}
    file.write_bytes(b"\xef\xbb\xbf" + json.dumps(value).encode())
    assert agenda_extract.load_export(file) == value
    file.write_bytes('{"tables": [], "name": "é"}'.encode("cp1252"))
    assert agenda_extract.load_export(file)["name"] == "é"
    for raw in (b"[]", b"{}", b'{"tables": "no"}'):
        file.write_bytes(raw)
        with pytest.raises(agenda_extract.ExportFormatError, match="tables"):
            agenda_extract.load_export(file)


def test_write_if_changed_handles_duplicates(tmp_path):
    dest = tmp_path / "nested" / "file.txt"
    agenda_extract.write_if_changed(dest, "hello")
    assert dest.read_text() == "hello"
    stat = dest.stat().st_mtime_ns
    agenda_extract.write_if_changed(dest, "hello")
    assert dest.stat().st_mtime_ns == stat
    agenda_extract.write_if_changed(dest, "bonjour")
    assert dest.read_text() == "bonjour"
    assert not dest.with_name("file.txt.tmp").exists()


def test_main_writes_outputs_and_reports_stats(tmp_path, monkeypatch, capsys):
    exported = tmp_path / "raw.json"
    output = tmp_path / "exported.json"
    csv_path = tmp_path / "exported.csv"
    exported.write_text(json.dumps(export_fixture()), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["extract.py", str(exported), "-o", str(output), "--csv", str(csv_path)],
    )
    assert agenda_extract.main() == 0
    text = capsys.readouterr().out
    assert "Types de journée : 2" in text
    assert "Paramètres non résolus : 1" in text
    assert output.exists() and csv_path.exists()
    assert json.loads(output.read_text())["schema"] == "eedomus-agenda-extract-v2"
    assert agenda_extract.main() == 0


@pytest.mark.parametrize("mode", ["same_outputs", "input_conflict", "bad_export"])
def test_main_rejects_invalid_files(tmp_path, monkeypatch, mode):
    exported = tmp_path / "raw.json"
    output = tmp_path / "out.json"
    exported.write_text(json.dumps(export_fixture()))
    if mode == "same_outputs":
        arguments = [str(exported), "-o", str(output), "--csv", str(output)]
    elif mode == "input_conflict":
        arguments = [str(exported), "-o", str(exported)]
    else:
        exported.write_text("not json")
        arguments = [str(exported)]
    monkeypatch.setattr(sys, "argv", ["extract.py", *arguments])
    with pytest.raises(SystemExit):
        agenda_extract.main()


def test_conditional_day_criterion_numeric_module_without_state_list():
    data = export_fixture()
    conditional = rows(data, "zb_controller_rule")[4]
    nested(conditional, "zb_rule_criteria").extend(
        (
            criterion(10, 1, kind="e", order=4),
            criterion(40, 25, kind="e", order=5),
        )
    )
    result = agenda_extract.extract(data)["regles_conditionnelles_liees_agenda"][0]
    criteria = result["conditions"]
    assert criteria[-2]["valeur_libelle"] == "Travail"
    assert criteria[-1]["valeur_libelle"] == "25"


def test_embedded_parameter_on_unreferenced_phase_is_not_reinterpreted():
    data = export_fixture()
    phase = rows(data, "zb_controller_module")[1]
    nested(phase, "zb_controller_module_value_descr").append(
        {"value": "7", "state": "Unused", "http_params": '[["777", "3"]]'}
    )
    result = agenda_extract.extract(data)
    assert result["phases"][-1] == {"id": 7, "name": "Unused"}
    assert len(result["parametres_embarques_non_resolus"]) == 1


def test_command_line_entrypoint(tmp_path, monkeypatch):
    export_path = tmp_path / "input.json"
    output = tmp_path / "out.json"
    csv_path = tmp_path / "out.csv"
    export_path.write_text(json.dumps(export_fixture()))
    monkeypatch.setattr(
        sys,
        "argv",
        ["extract.py", str(export_path), "-o", str(output), "--csv", str(csv_path)],
    )
    with pytest.raises(SystemExit) as result:
        runpy.run_path(str(Path(agenda_extract.__file__)), run_name="__main__")
    assert result.value.code == 0
    assert csv_path.is_file() and output.is_file()
