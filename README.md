# Day Planner — Daily scheduling for Home Assistant

**English** | [Français](README.fr.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/fmo01/hass-day_planner/tests.yml?label=Tests&style=for-the-badge)](https://github.com/fmo01/hass-day_planner/actions/workflows/tests.yml)
[![HACS + Hassfest](https://img.shields.io/github/actions/workflow/status/fmo01/hass-day_planner/validate.yml?label=HACS%20%2B%20Hassfest&style=for-the-badge)](https://github.com/fmo01/hass-day_planner/actions/workflows/validate.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://www.hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/fmo01/hass-day_planner?style=for-the-badge&color=blue)](https://github.com/fmo01/hass-day_planner/releases/latest)
[![Total downloads](https://img.shields.io/github/downloads/fmo01/hass-day_planner/total?label=Total%20downloads&style=for-the-badge&color=green)](https://github.com/fmo01/hass-day_planner/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-lightgrey.svg?style=for-the-badge)](LICENSE)

**Day Planner** is a Home Assistant integration that lets you build reusable schedules and trigger actions at planned times throughout the day.

It uses **moments** with their actions, **day types** with their scheduled times, **week schedules**, **cycles**, and **calendar exceptions**. You can view and edit all of these from the Day Planner panel in the Home Assistant sidebar.

## Migrating from eedomus to Home Assistant

If you are migrating from eedomus to Home Assistant, you can use Day Planner alongside [Dan4Jer’s hass-eedomus integration](https://github.com/Dan4Jer/hass-eedomus) or [my fork of hass-eedomus](https://github.com/fmo01/hass-eedomus), which I maintain to make that migration easier.

hass-eedomus makes your eedomus devices available in Home Assistant. Day Planner lets you import the eedomus agenda, including its phases and compatible actions.

You can also use Day Planner on its own to create schedules directly in Home Assistant.

## 📥 Installation

### Requirements

- **Home Assistant 2026.10.4 or later**, as specified in the repository’s `hacs.json`.
- **HACS** for the recommended installation method. Manual installation works without HACS.

On Home Assistant **2026.11 and later**, HACS is available through the **Marketplace**. For earlier versions, follow the [official HACS guide](https://www.hacs.xyz/docs/use/) to install and configure HACS.

### Method 1 — Install through HACS (recommended)

Use this button to open the Day Planner repository in HACS.

[![Add Day Planner to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fmo01&repository=hass-day_planner&category=integration)

If the button does not work:

1. Open **HACS** or the **Marketplace** in Home Assistant, depending on your version.
2. Add `https://github.com/fmo01/hass-day_planner` as a custom repository in the **Integration** category.
3. Search for **Day Planner** and download the integration.
4. **Restart Home Assistant**.

### Method 2 — Install manually

1. Download the [latest Day Planner release](https://github.com/fmo01/hass-day_planner/releases/latest).
2. Copy the `custom_components/day_planner` folder from the archive into your Home Assistant configuration directory.
3. Check that the resulting path is:

   ```text
   <config>/custom_components/day_planner/
   ```

4. **Restart Home Assistant**.

## ⚙️ Configuration

Once you have installed the integration and restarted Home Assistant, use this button to open the setup wizard.

[![Add the Day Planner integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=day_planner)

If the button does not work:

1. In Home Assistant, go to **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Day Planner** and confirm.
4. Open **Day Planner** in the sidebar (path `/day-planner`) to access the management panel.

Under **Settings → Devices & services → Day Planner → Configure**, you can control whether the sidebar panel appears, set the maximum number of cycles, and choose what happens to your data when you remove the integration.

### Getting started

1. Create **moments** and add the Home Assistant actions you want them to run.
2. Create **day types** and schedule your moments at the desired times.
3. Create a **week schedule** by assigning a day type to each of the seven days.
4. Create a **cycle** from one or more week schedules and set its start date.
5. Review the **calendar** and add any exceptions you need.

Day Planner runs actions at the times determined by the active schedule.

### Updating

- **HACS** — Install the update in HACS, then restart Home Assistant if needed.
- **Manual installation** — Replace the files in `custom_components/day_planner/`, then restart Home Assistant.
- Read the [changelog](CHANGELOG.md) before updating.

## 🗓️ One-time eedomus agenda import

Use **Configure → Import eedomus agenda** to import a JSON export from an **active eedomus box** already configured in Home Assistant. Select the file directly from your computer. There is no need to put it in `/config`.

The wizard shows how eedomus devices map to Home Assistant entities and previews the week schedules, day types, moments, scheduled times, and actions it will create. It flags unsupported domains such as `sensor` and still creates the affected moments. A missing or ambiguous mapping blocks the import.

Day Planner names the imported items **`Eedomus (<host>)`**. The eedomus integration’s entity IDs in Home Assistant stay the same.

This is a one-time import. It runs without ongoing synchronization, automatic creation of cycles or exceptions, or execution of Home Assistant actions. On the confirmation screen, you can also copy the mappings or download a CSV report or a **seven-sheet Excel (.xlsx) workbook**.

See the [eedomus import guide](docs/reprise_eedomus.md) and [Excel workbook contents](docs/export_xlsx_eedomus.md) in French.

## 🧪 Tests and validation

The GitHub Actions workflows linked above run the automated tests. To run the suite locally with a coverage report, use:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio -p pytest_cov scripts/tests/ \
  --cov=custom_components/day_planner --cov-report=term-missing -q
```

See the [test documentation](scripts/tests/README.md) and [coverage tracking](docs/qualification_couverture.md).

## 📚 Documentation

- [Functional documentation (French)](docs/day_planner_fonctionnel.md)
- [Technical documentation (French)](docs/day_planner_technique.md)
- [eedomus import guide and limitations (French)](docs/reprise_eedomus.md)
- [eedomus Excel export and its seven worksheets (French)](docs/export_xlsx_eedomus.md)
- [Tests and validation (French)](docs/qualification_couverture.md)
- [Roadmap (French)](docs/ROADMAP.md)

## License

Distributed under the [GPL-3.0 license](LICENSE).
