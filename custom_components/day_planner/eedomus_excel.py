"""Produce a seven-sheet Excel import report, using only Python stdlib.

The XLSX package is assembled in memory; no user export is written to disk.
Every value is written as a literal string (or a number for counters), never
as a formula or executable content.
"""

from __future__ import annotations

import re
from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
_CONTENT = "http://schemas.openxmlformats.org/package/2006/content-types"
_XML = "http://www.w3.org/XML/1998/namespace"
_COLS = ("Périphérique eedomus (ID)", "Entité Home Assistant", "Statut", "Motif")


def _xml(element: ET.Element) -> bytes:
    """Serialize an Office Open XML part with a declaration."""
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def _text(value) -> str:
    """Keep XML-valid Excel cell text within Excel's 32,767 char limit."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value))[:32767]


def _cell(row: ET.Element, address: str, value, header: bool = False) -> None:
    """Write a cell safely; literal strings cannot become spreadsheet formulas."""
    attributes = {"r": address}
    if header:
        attributes["s"] = "1"
    if type(value) is int:
        attributes["t"] = "n"
        cell = ET.SubElement(row, f"{{{_MAIN}}}c", attributes)
        ET.SubElement(cell, f"{{{_MAIN}}}v").text = str(value)
    else:
        attributes["t"] = "str"
        cell = ET.SubElement(row, f"{{{_MAIN}}}c", attributes)
        text = ET.SubElement(cell, f"{{{_MAIN}}}v")
        text.text = _text(value)


def _sheet(rows: list[tuple], widths: tuple[int, ...], filter_table: bool) -> bytes:
    """Render a worksheet with header styling, widths, filters and a frozen top row."""
    sheet = ET.Element(f"{{{_MAIN}}}worksheet")
    views = ET.SubElement(sheet, f"{{{_MAIN}}}sheetViews")
    view = ET.SubElement(views, f"{{{_MAIN}}}sheetView", {"workbookViewId": "0"})
    ET.SubElement(
        view,
        f"{{{_MAIN}}}pane",
        {
            "ySplit": "1",
            "topLeftCell": "A2",
            "activePane": "bottomLeft",
            "state": "frozen",
        },
    )
    columns = ET.SubElement(sheet, f"{{{_MAIN}}}cols")
    for index, width in enumerate(widths, 1):
        ET.SubElement(
            columns,
            f"{{{_MAIN}}}col",
            {
                "min": str(index),
                "max": str(index),
                "width": str(width),
                "customWidth": "1",
            },
        )
    data = ET.SubElement(sheet, f"{{{_MAIN}}}sheetData")
    for index, values in enumerate(rows, 1):
        row = ET.SubElement(
            data,
            f"{{{_MAIN}}}row",
            {
                "r": str(index),
                **({"ht": "32", "customHeight": "1"} if index == 1 else {}),
            },
        )
        for column, value in enumerate(values):
            _cell(row, f"{chr(65 + column)}{index}", value, header=index == 1)
    if filter_table and rows:
        ET.SubElement(
            sheet,
            f"{{{_MAIN}}}autoFilter",
            {
                "ref": f"A1:{chr(64 + len(widths))}{len(rows)}",
            },
        )
    return _xml(sheet)


def _styles() -> bytes:
    """Define default text and blue/white column headings."""
    stylesheet = ET.Element(f"{{{_MAIN}}}styleSheet")
    fonts = ET.SubElement(stylesheet, f"{{{_MAIN}}}fonts", {"count": "2"})
    for bold in (False, True):
        font = ET.SubElement(fonts, f"{{{_MAIN}}}font")
        ET.SubElement(font, f"{{{_MAIN}}}sz", {"val": "11"})
        if bold:
            ET.SubElement(font, f"{{{_MAIN}}}b")
            ET.SubElement(font, f"{{{_MAIN}}}color", {"rgb": "FFFFFFFF"})
        ET.SubElement(font, f"{{{_MAIN}}}name", {"val": "Aptos"})
    fills = ET.SubElement(stylesheet, f"{{{_MAIN}}}fills", {"count": "3"})
    ET.SubElement(
        ET.SubElement(fills, f"{{{_MAIN}}}fill"),
        f"{{{_MAIN}}}patternFill",
        {"patternType": "none"},
    )
    ET.SubElement(
        ET.SubElement(fills, f"{{{_MAIN}}}fill"),
        f"{{{_MAIN}}}patternFill",
        {"patternType": "gray125"},
    )
    fill = ET.SubElement(
        ET.SubElement(fills, f"{{{_MAIN}}}fill"),
        f"{{{_MAIN}}}patternFill",
        {"patternType": "solid"},
    )
    ET.SubElement(fill, f"{{{_MAIN}}}fgColor", {"rgb": "FF24466C"})
    ET.SubElement(fill, f"{{{_MAIN}}}bgColor", {"indexed": "64"})
    borders = ET.SubElement(stylesheet, f"{{{_MAIN}}}borders", {"count": "1"})
    border = ET.SubElement(borders, f"{{{_MAIN}}}border")
    for side in ("left", "right", "top", "bottom", "diagonal"):
        ET.SubElement(border, f"{{{_MAIN}}}{side}")
    style_xfs = ET.SubElement(stylesheet, f"{{{_MAIN}}}cellStyleXfs", {"count": "1"})
    ET.SubElement(
        style_xfs,
        f"{{{_MAIN}}}xf",
        {"numFmtId": "0", "fontId": "0", "fillId": "0", "borderId": "0"},
    )
    xfs = ET.SubElement(stylesheet, f"{{{_MAIN}}}cellXfs", {"count": "2"})
    ET.SubElement(
        xfs,
        f"{{{_MAIN}}}xf",
        {"numFmtId": "0", "fontId": "0", "fillId": "0", "borderId": "0", "xfId": "0"},
    )
    header = ET.SubElement(
        xfs,
        f"{{{_MAIN}}}xf",
        {
            "numFmtId": "0",
            "fontId": "1",
            "fillId": "2",
            "borderId": "0",
            "xfId": "0",
            "applyFont": "1",
            "applyFill": "1",
            "applyAlignment": "1",
        },
    )
    ET.SubElement(
        header, f"{{{_MAIN}}}alignment", {"wrapText": "1", "vertical": "center"}
    )
    cell_styles = ET.SubElement(stylesheet, f"{{{_MAIN}}}cellStyles", {"count": "1"})
    ET.SubElement(
        cell_styles,
        f"{{{_MAIN}}}cellStyle",
        {"name": "Normal", "xfId": "0", "builtinId": "0"},
    )
    return _xml(stylesheet)


def _workbook(names: tuple[str, ...]) -> bytes:
    book = ET.Element(f"{{{_MAIN}}}workbook")
    sheets = ET.SubElement(book, f"{{{_MAIN}}}sheets")
    for index, name in enumerate(names, 1):
        ET.SubElement(
            sheets,
            f"{{{_MAIN}}}sheet",
            {
                "name": name,
                "sheetId": str(index),
                f"{{{_REL}}}id": f"rId{index}",
            },
        )
    return _xml(book)


def _relationships(links: list[tuple[str, str, str]]) -> bytes:
    root = ET.Element(f"{{{_PKG}}}Relationships")
    for ident, relation, target in links:
        ET.SubElement(
            root,
            f"{{{_PKG}}}Relationship",
            {
                "Id": ident,
                "Type": f"{_REL}/{relation}",
                "Target": target,
            },
        )
    return _xml(root)


def _content_types(sheet_count: int) -> bytes:
    # Use a local default namespace without changing global ElementTree state.
    types = ET.Element("Types", {"xmlns": _CONTENT})
    for extension, mime in (
        ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
        ("xml", "application/xml"),
    ):
        ET.SubElement(
            types,
            "Default",
            {
                "Extension": extension,
                "ContentType": mime,
            },
        )
    paths = [
        (
            "/xl/workbook.xml",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
        ),
        (
            "/xl/styles.xml",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml",
        ),
    ]
    paths += [
        (
            f"/xl/worksheets/sheet{i}.xml",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml",
        )
        for i in range(1, sheet_count + 1)
    ]
    for path, mime in paths:
        ET.SubElement(
            types,
            "Override",
            {
                "PartName": path,
                "ContentType": mime,
            },
        )
    return _xml(types)


def _imported_moments(plan, host: str) -> list:
    """Return only the moments of the selected box, never manual HA objects."""
    prefix = f"eedomus_Eedomus ({host})_phase_"
    configuration = getattr(plan, "configuration", None)
    if configuration is None:
        return []
    return sorted(
        (item for item in configuration.moments if item.id.startswith(prefix)),
        key=lambda item: item.id,
    )


def _moment_actions(plan, host: str) -> list[tuple]:
    """Display created moments and actual HA actions, including empty moments."""
    rows = [
        (
            "Identifiant du moment",
            "Moment",
            "Identifiant de l'action",
            "Action",
            "Service Home Assistant",
            "Entité cible",
            "Statut",
        )
    ]
    for moment in _imported_moments(plan, host):
        if not moment.actions:
            rows.append(
                (moment.id, moment.name, "", "", "", "", "Sans action compatible")
            )
            continue
        for action in moment.actions:
            sequences = action.sequence or []
            if not sequences:
                rows.append(
                    (
                        moment.id,
                        moment.name,
                        action.id,
                        action.label,
                        "",
                        "",
                        "Aucune commande",
                    )
                )
            for sequence in sequences:
                target = sequence.get("target") or {}
                entity = target.get("entity_id", "") if isinstance(target, dict) else ""
                if isinstance(entity, (list, tuple)):
                    entity = ", ".join(str(item) for item in entity)
                rows.append(
                    (
                        moment.id,
                        moment.name,
                        action.id,
                        action.label,
                        sequence.get("action", ""),
                        entity,
                        "Prise en charge",
                    )
                )
    return rows


def _day_type_schedules(plan, host: str) -> list[tuple]:
    """List all scheduled occurrences, not just distinct moments."""
    rows = [
        ("Type de journée (ID)", "Type de journée", "Horaire", "Moment", "Moment (ID)")
    ]
    prefix = f"eedomus_Eedomus ({host})_day_"
    names = {item.id: item.name for item in _imported_moments(plan, host)}
    configuration = getattr(plan, "configuration", None)
    if configuration is None:
        return rows
    days = sorted(
        (item for item in configuration.day_types if item.id.startswith(prefix)),
        key=lambda item: item.id,
    )
    for day in days:
        occurrences = sorted(
            day.scheduled_moments,
            key=lambda item: (str(item.time_definition.fixed_time), item.moment_id),
        )
        if not occurrences:
            rows.append((day.id, day.name, "", "", ""))
        for item in occurrences:
            at = item.time_definition.fixed_time
            display_time = at.isoformat(timespec="seconds") if at is not None else ""
            rows.append(
                (
                    day.id,
                    day.name,
                    display_time,
                    names.get(item.moment_id, ""),
                    item.moment_id,
                )
            )
    return rows


def _not_imported(plan, agenda: dict | None) -> list[tuple]:
    """Explain *all* exclusions in the selected JSON, with explicit provenance."""
    rows = [("Catégorie", "Identifiant eedomus", "Élément", "Détails", "Motif")]
    for label, entity, reason in plan.unsupported_associations:
        rows.append(("Association / action", "", label, entity, reason))
    if agenda is None:
        if plan.conditional_rules_not_imported:
            rows.append(
                (
                    "Règles conditionnelles",
                    "",
                    "Détail indisponible",
                    plan.conditional_rules_not_imported,
                    "Non reprises : seules les actions directes des phases sont importées",
                )
            )
        if plan.unresolved_embedded_parameters:
            rows.append(
                (
                    "Paramètres internes",
                    "",
                    "Détail indisponible",
                    plan.unresolved_embedded_parameters,
                    "Non identifiés comme actions directes",
                )
            )
        return rows
    for rule in agenda.get("regles_conditionnelles_liees_agenda", ()):
        if not rule.get("active"):
            continue
        details = (
            f"{len(rule.get('conditions') or [])} condition(s), "
            f"{len(rule.get('actions') or [])} action(s)"
        )
        rows.append(
            (
                "Règle conditionnelle",
                str(rule.get("id", "")),
                rule.get("nom", ""),
                details,
                "Règle conditionnelle active hors du périmètre de reprise",
            )
        )
    for item in agenda.get("parametres_embarques_non_resolus", ()):
        detail = f"Cible : {item.get('cible_brute', '')} ; valeur : {item.get('valeur_brute', '')}"
        rows.append(
            (
                "Paramètre interne",
                str(item.get("phase_id", "")),
                item.get("phase", ""),
                detail,
                item.get("note", "Non identifié comme action directe"),
            )
        )
    return rows


def xlsx_bytes(plan, host: str, agenda: dict | None = None) -> bytes:
    """Build the selected eedomus box report from the *validated* import plan."""
    supported = []
    for association in plan.mapped_entities:
        peripheral, sep, entity = association.rpartition(" → ")
        if not sep:
            peripheral, entity = association, ""
        supported.append((peripheral, entity, "Pris en charge", ""))
    unsupported = [
        (peripheral, entity, "Ignoré", reason)
        for peripheral, entity, reason in plan.unsupported_associations
    ]
    summary = [
        ("Indicateur", "Valeur"),
        ("Box eedomus", f"Eedomus ({host})"),
        ("Types de journée", plan.day_types),
        ("Moments", plan.moments),
        ("Horaires", plan.scheduled),
        ("Actions compatibles", plan.actions),
        ("Moments sans action", plan.moments_without_actions),
        ("Associations compatibles", len(supported)),
        ("Associations ignorées", len(unsupported)),
        ("Règles conditionnelles non reprises", plan.conditional_rules_not_imported),
        ("Paramètres internes non repris", plan.unresolved_embedded_parameters),
        ("Reprise déjà présente", "Oui" if plan.had_previous_import else "Non"),
        ("Exécution d'appareils pendant l'import", "Aucune"),
    ]
    tabs = (
        ("Résumé", summary, (44, 45), False),
        (
            "Toutes associations",
            [_COLS, *supported, *unsupported],
            (37, 58, 21, 64),
            True,
        ),
        ("Prises en charge", [_COLS, *supported], (37, 58, 21, 64), True),
        ("Ignorées", [_COLS, *unsupported], (37, 58, 21, 64), True),
        (
            "Éléments non repris",
            _not_imported(plan, agenda),
            (28, 23, 48, 60, 66),
            True,
        ),
        (
            "Moments et actions",
            _moment_actions(plan, host),
            (54, 45, 61, 55, 32, 54, 27),
            True,
        ),
        (
            "Journées et horaires",
            _day_type_schedules(plan, host),
            (50, 45, 16, 45, 54),
            True,
        ),
    )
    memory = BytesIO()
    with ZipFile(memory, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types(len(tabs)))
        archive.writestr(
            "_rels/.rels",
            _relationships(
                [
                    ("rId1", "officeDocument", "xl/workbook.xml"),
                ]
            ),
        )
        archive.writestr("xl/workbook.xml", _workbook(tuple(tab[0] for tab in tabs)))
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            _relationships(
                [
                    (f"rId{i}", "worksheet", f"worksheets/sheet{i}.xml")
                    for i in range(1, len(tabs) + 1)
                ]
                + [(f"rId{len(tabs) + 1}", "styles", "styles.xml")]
            ),
        )
        archive.writestr("xl/styles.xml", _styles())
        for index, (_, rows, widths, filter_table) in enumerate(tabs, 1):
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml",
                _sheet(rows, widths, filter_table),
            )
    return memory.getvalue()
