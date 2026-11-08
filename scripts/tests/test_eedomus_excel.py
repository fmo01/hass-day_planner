"""Excel workbook regression tests for Day Planner's eedomus export."""

from datetime import time
from io import BytesIO
from types import SimpleNamespace
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from custom_components.day_planner.eedomus_excel import xlsx_bytes

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _plan():
    return SimpleNamespace(
        mapped_entities=(
            "Guirlande [746271] → light.guirlande_salle_a_manger",
            "Thermostat [3463520] → climate.thermostat_salle_a_manger",
        ),
        unsupported_associations=(
            (
                "Cmd 1 Volet [795317]",
                "sensor.volet",
                "Domaine sensor non pris en charge",
            ),
            ("=HYPERLINK('bad')", "sensor.other", "Incompatible\x00."),
        ),
        day_types=9,
        moments=8,
        scheduled=41,
        actions=10,
        moments_without_actions=1,
        conditional_rules_not_imported=7,
        unresolved_embedded_parameters=1,
        had_previous_import=True,
    )


def test_eedomus_excel_is_valid_xlsx_with_seven_sheets_and_filters():
    content = xlsx_bytes(_plan(), "192.20.55.30")
    assert content.startswith(b"PK")
    with ZipFile(BytesIO(content)) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert "xl/styles.xml" in names
        assert "[Content_Types].xml" in names
        for path in names:
            if path.endswith((".xml", ".rels")) or path == "[Content_Types].xml":
                ET.fromstring(archive.read(path))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        tabs = [
            entry.attrib["name"] for entry in workbook.findall(f".//{{{_MAIN}}}sheet")
        ]
        assert tabs == [
            "Résumé",
            "Toutes associations",
            "Prises en charge",
            "Ignorées",
            "Éléments non repris",
            "Moments et actions",
            "Journées et horaires",
        ]
        summary = archive.read("xl/worksheets/sheet1.xml").decode()
        all_rows = archive.read("xl/worksheets/sheet2.xml").decode()
        included = archive.read("xl/worksheets/sheet3.xml").decode()
        ignored = archive.read("xl/worksheets/sheet4.xml").decode()
        assert "Eedomus (192.20.55.30)" in summary
        assert "41" in summary
        assert "Guirlande" in included and "Guirlande" in all_rows
        assert "Cmd 1 Volet" in ignored and "Cmd 1 Volet" in all_rows
        assert "Guirlande" not in ignored
        assert "sensor.volet" not in included
        assert "autoFilter" in all_rows
        assert "pane" in all_rows
        assert 't="str"' in all_rows
        assert "<ns0:f>" not in ignored
        assert "Incompatible." in ignored
        assert "&#x0;" not in ignored


def test_eedomus_excel_empty_associations_keeps_tabs_and_moment_summary():
    plan = _plan()
    plan.mapped_entities = ()
    plan.unsupported_associations = ()
    report = xlsx_bytes(plan, "test-box")
    with ZipFile(BytesIO(report)) as archive:
        assert "xl/worksheets/sheet7.xml" in archive.namelist()
        assert b"Moments sans action" in archive.read("xl/worksheets/sheet1.xml")
        ignored = ET.fromstring(archive.read("xl/worksheets/sheet4.xml"))
        rows = ignored.findall(f".//{{{_MAIN}}}row")
        assert len(rows) == 1


def test_eedomus_excel_reports_real_objects_and_unimported_details():
    """The three added sheets detail this box's objects, not other HA items."""
    host = "192.20.55.30"
    prefix = f"eedomus_Eedomus ({host})_"

    def moment(id_suffix, name, actions):
        return SimpleNamespace(id=prefix + id_suffix, name=name, actions=actions)

    action = SimpleNamespace(
        id=prefix + "phase_5_action_1",
        label="Thermostat → 22°C",
        sequence=[
            {
                "action": "climate.set_temperature",
                "target": {"entity_id": "climate.thermostat_salle_a_manger"},
                "data": {"temperature": 22.0},
            }
        ],
    )
    first = moment("phase_5", "Couché — Eedomus (192.20.55.30)", (action,))
    empty = moment("phase_7", "avant levé — Eedomus (192.20.55.30)", ())
    manual = moment("manual", "Élément manuel", ())
    day = SimpleNamespace(
        id=prefix + "day_1",
        name="Journée de travail — Eedomus (192.20.55.30)",
        scheduled_moments=(
            SimpleNamespace(
                moment_id=first.id,
                time_definition=SimpleNamespace(fixed_time=time(0, 0)),
            ),
            SimpleNamespace(
                moment_id=empty.id,
                time_definition=SimpleNamespace(fixed_time=time(6, 10)),
            ),
        ),
    )
    other_day = SimpleNamespace(
        id="manual_day", name="Journée manuelle", scheduled_moments=()
    )
    plan = _plan()
    plan.configuration = SimpleNamespace(
        moments=(first, empty, manual), day_types=(day, other_day)
    )
    agenda = {
        "regles_conditionnelles_liees_agenda": [
            {
                "id": "123",
                "nom": "Règle chauffage",
                "active": True,
                "conditions": [1],
                "actions": [1],
            },
            {
                "id": "124",
                "nom": "Règle inactive",
                "active": False,
                "conditions": [],
                "actions": [],
            },
        ],
        "parametres_embarques_non_resolus": [
            {
                "phase_id": 7,
                "phase": "avant levé",
                "cible_brute": "42",
                "valeur_brute": "100",
                "note": "Paramètre interne non résolu",
            },
        ],
    }
    content = xlsx_bytes(plan, host, agenda)
    with ZipFile(BytesIO(content)) as archive:
        assert archive.testzip() is None
        excluded = archive.read("xl/worksheets/sheet5.xml").decode()
        actions = archive.read("xl/worksheets/sheet6.xml").decode()
        hours = archive.read("xl/worksheets/sheet7.xml").decode()
        assert "Règle chauffage" in excluded
        assert "Règle inactive" not in excluded
        assert "Paramètre interne non résolu" in excluded
        assert "sensor.volet" in excluded
        assert "climate.set_temperature" in actions
        assert "Sans action compatible" in actions
        assert "Élément manuel" not in actions
        assert "Journée de travail" in hours
        assert "00:00:00" in hours and "06:10:00" in hours
        assert "Journée manuelle" not in hours
        for sheet, last_col in ((excluded, "E"), (actions, "G"), (hours, "E")):
            assert "autoFilter" in sheet
            assert f"{last_col}" in sheet


def test_eedomus_excel_uses_summary_when_agenda_details_are_missing():
    plan = _plan()
    content = xlsx_bytes(plan, "192.20.55.30")
    with ZipFile(BytesIO(content)) as archive:
        excluded = archive.read("xl/worksheets/sheet5.xml").decode()
        assert "Détail indisponible" in excluded
        assert "sensor.volet" in excluded


def test_eedomus_excel_handles_empty_sequences_and_days_without_schedules():
    host = "192.20.55.30"
    prefix = f"eedomus_Eedomus ({host})_"
    sequence_less_action = SimpleNamespace(
        id=prefix + "phase_4_action_1",
        label="Action incomplète",
        sequence=[],
    )
    action_with_multiple_targets = SimpleNamespace(
        id=prefix + "phase_4_action_2",
        label="Deux volets",
        sequence=[
            {
                "action": "switch.turn_on",
                "target": {"entity_id": ["switch.a", "switch.b"]},
            }
        ],
    )
    moment = SimpleNamespace(
        id=prefix + "phase_4",
        name="Soirée",
        actions=(sequence_less_action, action_with_multiple_targets),
    )
    empty_day = SimpleNamespace(
        id=prefix + "day_3", name="Journée libre", scheduled_moments=()
    )
    unspecified = SimpleNamespace(
        moment_id=moment.id,
        time_definition=SimpleNamespace(fixed_time=None),
    )
    other_day = SimpleNamespace(
        id=prefix + "day_4",
        name="Journée spéciale",
        scheduled_moments=(unspecified,),
    )
    plan = _plan()
    plan.configuration = SimpleNamespace(
        moments=(moment,), day_types=(empty_day, other_day)
    )
    report = xlsx_bytes(
        plan,
        host,
        {
            "regles_conditionnelles_liees_agenda": [],
            "parametres_embarques_non_resolus": [],
        },
    )
    with ZipFile(BytesIO(report)) as archive:
        action_xml = archive.read("xl/worksheets/sheet6.xml").decode()
        day_xml = archive.read("xl/worksheets/sheet7.xml").decode()
        assert "Aucune commande" in action_xml
        assert "switch.a, switch.b" in action_xml
        assert "Journée libre" in day_xml
        assert "Journée spéciale" in day_xml


def test_eedomus_excel_supports_associations_without_arrow():
    """Defensive legacy display labels still generate valid XLSX cells."""
    plan = _plan()
    plan.mapped_entities = ("Périphérique sans séparateur",)
    xlsx = xlsx_bytes(plan, "192.20.55.30")
    with ZipFile(BytesIO(xlsx)) as archive:
        xml = archive.read("xl/worksheets/sheet3.xml").decode()
    assert "Périphérique sans séparateur" in xml
