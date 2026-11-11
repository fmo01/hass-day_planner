# Day Planner — Planification des journées pour Home Assistant

[![Tests](https://img.shields.io/github/actions/workflow/status/fmo01/hass-day_planner/tests.yml?label=Tests&style=for-the-badge)](https://github.com/fmo01/hass-day_planner/actions/workflows/tests.yml)
[![HACS + Hassfest](https://img.shields.io/github/actions/workflow/status/fmo01/hass-day_planner/validate.yml?label=HACS%20%2B%20Hassfest&style=for-the-badge)](https://github.com/fmo01/hass-day_planner/actions/workflows/validate.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://www.hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/fmo01/hass-day_planner?style=for-the-badge&color=blue)](https://github.com/fmo01/hass-day_planner/releases/latest)
[![Téléchargements cumulés](https://img.shields.io/github/downloads/fmo01/hass-day_planner/total?label=Total%20downloads&style=for-the-badge&color=green)](https://github.com/fmo01/hass-day_planner/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-lightgrey.svg?style=for-the-badge)](LICENSE)

**Day Planner** est une intégration Home Assistant qui permet de construire des plannings réutilisables et de déclencher des actions aux moments prévus de la journée.

Elle s'organise autour de **moments** (avec leurs actions), de **types de journée** (avec leurs horaires), de **semaines types**, de **cycles** et d'**exceptions de calendrier**. Un panneau de gestion, accessible depuis le menu latéral de Home Assistant, permet de consulter et de modifier ces éléments.

## Migration d’eedomus vers Home Assistant

Si tu migres d’eedomus vers Home Assistant, Day Planner peut être utilisé en complément de l’intégration [hass-eedomus de Dan4Jer](https://github.com/Dan4Jer/hass-eedomus) ou de [mon fork de hass-eedomus](https://github.com/fmo01/hass-eedomus), que je maintiens pour faciliter cette migration.

hass-eedomus rend les périphériques eedomus accessibles dans Home Assistant. Day Planner complète cette intégration en permettant de reprendre l’agenda eedomus et de retrouver ses phases et les actions compatibles dans Home Assistant.

Day Planner peut également être utilisé seul pour créer une planification directement dans Home Assistant.


## 📥 Installation

### Prérequis

- **Home Assistant 2026.4.0 ou version ultérieure**, conformément au fichier `hacs.json` du dépôt.
- **HACS**, pour l'installation recommandée. Il n'est pas nécessaire pour une installation manuelle.

Sur Home Assistant **2026.11 et versions ultérieures**, HACS est intégré au **Marketplace**. Pour les versions précédentes, consultez le [guide officiel HACS](https://www.hacs.xyz/docs/use/) afin de l'installer et le configurer.

### Méthode 1 — Via HACS (recommandée)

Cliquez sur le bouton pour ouvrir le dépôt Day Planner dans HACS :

[![Ajouter Day Planner dans HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fmo01&repository=hass-day_planner&category=integration)

Si le bouton ne fonctionne pas :

1. Ouvrez **HACS / Marketplace** dans Home Assistant (selon votre version).
2. Ajoutez le dépôt personnalisé `https://github.com/fmo01/hass-day_planner` dans la catégorie **Intégration**.
3. Recherchez **Day Planner** et téléchargez l'intégration.
4. **Redémarrez Home Assistant**.

### Méthode 2 — Installation manuelle

1. Téléchargez la [dernière version de Day Planner](https://github.com/fmo01/hass-day_planner/releases/latest).
2. Copiez le dossier `custom_components/day_planner` de l'archive dans le répertoire de configuration de Home Assistant.
3. Vérifiez l'arborescence suivante :

   ```text
   <config>/custom_components/day_planner/
   ```

4. **Redémarrez Home Assistant**.

## ⚙️ Configuration

Une fois l'intégration installée et Home Assistant redémarré, cliquez sur le bouton ci-dessous pour ouvrir l'assistant d'ajout :

[![Ajouter l'intégration Day Planner dans Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=day_planner)

Si le bouton ne fonctionne pas :

1. Dans Home Assistant, ouvrez **Paramètres → Appareils et services**.
2. Sélectionnez **Ajouter une intégration**.
3. Recherchez **Day Planner**, puis validez l'ajout.
4. Ouvrez **Day Planner** dans le menu latéral (chemin `/day-planner`) pour accéder au panneau de gestion.

Dans **Paramètres → Appareils et services → Day Planner → Configurer**, les options permettent notamment de gérer l'affichage du panneau latéral, le nombre maximal de cycles et le comportement des données lors du retrait de l'intégration.

### Premiers pas

1. Créez des **moments** et associez-leur les actions Home Assistant souhaitées.
2. Créez des **types de journée** et planifiez les moments aux horaires voulus.
3. Définissez une **semaine type** en attribuant un type de journée à chacun des sept jours.
4. Créez un **cycle** à partir d'une ou plusieurs semaines types et définissez sa date de début.
5. Consultez le **calendrier** et ajoutez les exceptions nécessaires.

Les actions sont déclenchées aux horaires calculés par Day Planner, selon le planning actif.

### Mise à jour

- **Via HACS** : installez les versions proposées par HACS, puis redémarrez Home Assistant si nécessaire.
- **Installation manuelle** : remplacez les fichiers dans `custom_components/day_planner/`, puis redémarrez Home Assistant.
- Consultez le [journal des modifications](CHANGELOG.md) avant une mise à jour.

## 🗓️ Reprise ponctuelle d’un agenda eedomus

L'assistant **Configurer → Reprise agenda eedomus** permet d'importer un export JSON d'une **box eedomus active** déjà configurée dans Home Assistant. Le fichier est choisi directement depuis votre ordinateur ; il n'est pas nécessaire de le déposer dans `/config`.

L'assistant présente les correspondances entre périphériques eedomus et entités Home Assistant, ainsi qu'un aperçu des semaines, types de journée, moments, horaires et actions qui seront créés. Les domaines non pris en charge, notamment `sensor`, sont signalés sans empêcher la création des moments concernés. Une association absente ou ambiguë reste une erreur bloquante.

Les objets créés dans Day Planner utilisent le nom de box **`Eedomus (<hôte>)`** ; les identifiants des entités de l'intégration eedomus dans Home Assistant restent inchangés.

Cette opération est **ponctuelle** : elle ne met pas en place de synchronisation, ne crée pas automatiquement de cycle ou d'exception et ne déclenche aucune action Home Assistant pendant la reprise. La confirmation permet également de copier les associations et de télécharger un rapport CSV ou **Excel (.xlsx) à sept onglets**.

**Documentation détaillée :** [guide de reprise eedomus](docs/reprise_eedomus.md) et [contenu du classeur Excel](docs/export_xlsx_eedomus.md).

## 🧪 Tests et validation

Les tests automatisés sont exécutés par les workflows GitHub Actions indiqués dans le bandeau. Pour lancer localement la suite avec le rapport de couverture :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio -p pytest_cov scripts/tests/ \
  --cov=custom_components/day_planner --cov-report=term-missing -q
```

Voir [la documentation des tests](scripts/tests/README.md) et [le suivi de la couverture](docs/qualification_couverture.md).

## 📚 Documentation

- [Documentation fonctionnelle](docs/day_planner_fonctionnel.md)
- [Documentation technique](docs/day_planner_technique.md)
- [Reprise eedomus : guide utilisateur et limites](docs/reprise_eedomus.md)
- [Export Excel eedomus : structure des sept onglets](docs/export_xlsx_eedomus.md)
- [Tests et validation](docs/qualification_couverture.md)
- [Roadmap](docs/ROADMAP.md)

## Licence

Distribué sous licence [GPL-3.0](LICENSE).
