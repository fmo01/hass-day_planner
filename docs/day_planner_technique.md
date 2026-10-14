# Day Planner — Documentation technique

**Version publiée de référence : 0.2.0 (`manifest.json`). Documentation actualisée le 14 octobre 2026 avec les corrections confirmées par l'utilisateur.**

## 1. Architecture

Les formulaires Home Assistant, les services et l'API WebSocket modifient la configuration via le moteur métier. Le runtime sauvegarde les modifications, actualise le résolveur, replanifie le prochain événement et informe les entités.

| Composant | Responsabilité |
| --- | --- |
| `PlannerEngine` / `PlannerValidator` | Manipulation et validation de la configuration. |
| `PlannerResolver` | Cycle, type de semaine, type de journée et exception applicables à une date. |
| `PlannerScheduler` | Événements d'une date, prochain événement, événement actif et moment courant. |
| `HomeAssistantScheduler` | Enregistrement et annulation du prochain rappel Home Assistant. |
| `ActionExecutor` | Exécution des actions des moments via `Script`. |
| `DayPlannerStorage` | Persistance via Home Assistant `Store`. |
| `DayPlannerRuntimeData` | Composants actifs et synchronisation après modification. |
| Frontend / panneau | Gestion graphique utilisant l'API WebSocket. |
| Plateformes sensor/calendar | Exposition du planning à Home Assistant. |

## 2. Arborescence

Les principaux modules se trouvent dans `custom_components/day_planner/` :

- Intégration : `__init__.py`, `const.py`, `manifest.json`, `integration_info.py`.
- Configuration : `config_flow.py`, `options_flow.py`, `strings.json`, `translations/`.
- Interfaces : `services.py`, `services.yaml`, `schemas.py`, `websocket_api.py`.
- Exécution : `runtime.py`, `ha_scheduler.py`, `action_executor.py`.
- Persistance : `storage.py`.
- Entités : `sensor.py`, `calendar.py`.
- Présentation : `frontend.py`, `panel.py`, `frontend/`.
- Domaine : `domain/` contenant les modèles et leurs conversions.
- Planificateur : `planner/engine.py`, `validator.py`, `resolver.py`, `scheduler.py`, `errors.py`, `protocols.py`.

Le frontend contient `day-planner-panel.js`, `day-planner-card.js`, `api.js`, `i18n.js`, `styles.js`, `utils.js`, `components/timeline.js` et les vues calendrier, moments, types de journée, types de semaine et cycles.

Les traductions du frontend (`frontend/translations/`) sont distinctes des traductions de l'intégration Home Assistant (`translations/`).

Les tests sont regroupés dans `scripts/tests/`, avec 18 fichiers couvrant domaine, moteur, validateur, résolveur, ordonnanceurs, exécuteur, stockage, runtime, initialisation, flows, services, WebSocket, entités et panneau.

## 3. Modèle de domaine

| Modèle | Champs |
| --- | --- |
| `Moment` | `id`, `name`, `icon=None`, `actions=()`. |
| `DayType` | `id`, `name`, `scheduled_moments`. |
| `ScheduledMoment` | `moment_id`, `time_definition`. |
| `TimeDefinition` | `fixed_time: time`. |
| `WeekSchedule` | `id`, `name` et sept références : `monday` à `sunday`. |
| `Cycle` | `id`, `name`, `start_date: date`, `week_schedule_ids`. |
| `CalendarException` | `id`, `date: date`, `day_type_id`, `description=None`. |
| `ResolvedDayContext` | `date`, `day_type`, `cycle_id`, `week_schedule_id`, `calendar_exception_id`. |
| `ScheduledEvent` | `scheduled_at: datetime`, `moment`. |

Ces modèles sont des dataclasses `frozen=True, slots=True`. Leurs collections métier sont généralement des tuples. Les dates et heures persistées utilisent les conversions ISO correspondantes, dont `time.isoformat()` et `time.fromisoformat()` pour les horaires.

### Action

```python
@dataclass(frozen=True, slots=True)
class Action:
    id: str
    sequence: list[dict[str, Any]]
    label: str | None = None
```

Lorsque `label` vaut `None` à la construction, il prend la valeur de `id`. Les actions sont stockées dans `Moment.actions` ; chaque action est sérialisée avec `id`, `label` et `sequence`.

Le gel des dataclasses ne rend pas immuables les listes et dictionnaires imbriqués, notamment `sequence`.

### Metadata

`domain/metadata.py` définit encore une dataclass mutable nommée `Audit`, avec `created_by`, `created_at`, `modified_by`, `modified_at`. Elle n'est pas raccordée aux modèles persistés. La présence de cette classe ne constitue pas une traçabilité opérationnelle des modifications.

## 4. PlannerConfiguration

Le conteneur racine possède cinq tuples : `moments`, `day_types`, `week_schedules`, `cycles`, `calendar_exceptions`.

`PlannerConfiguration.empty()` crée une configuration vide. `to_dict()` et `from_dict()` assurent la conversion des objets persistés. `has_data()` indique si au moins une collection contient des données.

Les actions sont imbriquées dans les moments ; elles ne constituent pas une collection racine.

## 5. PlannerEngine

Le moteur fournit les opérations get/add/update/remove pour les moments, types de journée, types de semaine, cycles et exceptions, ainsi que les opérations sur les moments planifiés.

Les mutations construisent une nouvelle configuration avec `dataclasses.replace`, la valident, puis remplacent la configuration du moteur. Les suppressions contrôlent les dépendances : moment utilisé par une journée, journée utilisée par une semaine ou une exception, semaine utilisée par un cycle.

Le constructeur reçoit `max_cycles`, dont la valeur par défaut est 3.

### Résolution et calcul des événements

`PlannerResolver` choisit le cycle ayant la date de début la plus récente parmi ceux déjà commencés. L'index de semaine est calculé par :

```python
((target_date - cycle.start_date).days // 7) % len(cycle.week_schedule_ids)
```

Il sélectionne le type de journée du jour de semaine et applique ensuite l'exception éventuelle. Une exception peut aussi fournir un type de journée sans cycle applicable.

`PlannerScheduler.events_for_date()` combine la date et les heures fixes, puis trie les événements. `next_event()` recherche un événement strictement futur jusqu'à 366 jours après la date courante par défaut, celle-ci étant incluse dans la recherche.

`current_event()` considère une occurrence active pendant une minute. `current_moment()` retourne le dernier événement atteint dans la journée courante, sans reporter celui de la veille.

### Normalisation temporelle et groupe d'événements

- `events_for_date()` construit les occurrences à partir des horaires locaux du modèle.
- `_normalize_scheduled_at()` ajoute le fuseau de référence aux occurrences sans fuseau. Une heure inexistante est avancée à la première minute locale valide ; `fold=0` sélectionne le premier passage d'une heure répétée.
- La validité d'une heure locale est contrôlée par un aller-retour local → UTC → local.
- `_comparison_time()` convertit les dates avec fuseau en UTC pour comparer les instants réels, notamment pendant l'heure répétée. Les dates sans fuseau restent inchangées.
- `next_event()`, `current_event()` et `current_moment()` utilisent ces comparaisons. La fenêtre d'une minute de `current_event()` est évaluée sur le temps réellement écoulé.
- `events_at()` retourne toutes les occurrences dont l'instant d'exécution normalisé correspond à l'instant demandé. Cela inclut les occurrences de l'heure supprimée et celles normalement prévues au premier instant valide.
- `HomeAssistantScheduler` capture ce groupe lors de la programmation et exécute ses moments dans un seul rappel, avant de replanifier dans le bloc `finally`. La protection contre un double appel du même rappel reste conservée.

Cette règle vise les horaires fixes et les changements d'heure testés avec Europe/Paris, sans implémenter une syntaxe crontab générale. L'exécution et le rendu réel du calendrier Home Assistant autour de ces transitions restent à vérifier sur l'installation cible.

## 6. Validation

`PlannerValidator` vérifie :

- l'unicité des identifiants entre les cinq collections racines ;
- les références aux moments et l'absence de doublons dans un type de journée ;
- de 1 à 4 semaines par cycle et leurs références ;
- le début des cycles un lundi et l'unicité de leurs dates de début ;
- le nombre maximal de cycles ;
- les références aux types de journée des exceptions et l'unicité de leurs dates ;
- des identifiants d'actions non vides et uniques dans chaque moment ;
- des séquences d'actions non vides.

`_validate_week_schedules()` contrôle les sept références de types de journée de chaque `WeekSchedule`. Une référence inconnue lève `ValidationError` et la nouvelle configuration n'est pas acceptée. Les séquences d'actions ne font toujours pas l'objet d'une validation complète de script par ce validateur.

Les erreurs métier utilisent `ValidationError` et `NotFoundError`, dérivées de `PlannerError`.

## 7. Stockage

`DayPlannerStorage` encapsule `Store(hass, STORAGE_VERSION, STORAGE_KEY)` avec :

```python
STORAGE_VERSION = 1
STORAGE_KEY = "day_planner.storage"
```

Le fichier est `/config/.storage/day_planner.storage`. `async_load()` retourne une configuration vide en l'absence de données ; `async_save()` sérialise la configuration ; `async_delete()` supprime le stockage.

L'ancien chemin `day_planner_configuration` n'est pas celui utilisé par cette version. Aucune migration de cet ancien chemin n'est mise en œuvre par `storage.py`.

## 8. Runtime

`DayPlannerRuntimeData` contient `hass`, `storage`, `engine`, `resolver`, `scheduler`, `action_executor`, `ha_scheduler`. Il est placé dans `entry.runtime_data`.

`async_configuration_updated()` :

1. sauvegarde `engine.configuration` ;
2. actualise le résolveur ;
3. replanifie le prochain événement ;
4. émet le signal `day_planner_updated`.

Les entités écoutent ce signal pour actualiser leur état. Le calendrier actualise aussi ses abonnés aux événements.

## 9. Initialisation

`async_setup()` enregistre les commandes WebSocket et les chemins statiques du frontend.

`async_setup_entry()` :

1. crée le stockage et charge la configuration ;
2. sauvegarde la configuration si elle ne contient pas de données ;
3. crée moteur, résolveur, ordonnanceur métier, exécuteur et ordonnanceur Home Assistant ;
4. place les composants dans le runtime ;
5. ajoute l'écouteur de changement des options ;
6. initialise les services ;
7. migre les anciens identifiants d'entités concernés ;
8. charge les plateformes sensor et calendar ;
9. planifie le prochain événement ;
10. enregistre le panneau.

Les moments de `DEFAULT_MOMENTS` ne sont pas automatiquement injectés dans la configuration vide.

L'ordonnanceur Home Assistant annule le précédent rappel avant de planifier le suivant avec `async_track_point_in_time`. Lors du rappel, il exécute les actions du moment et replanifie dans un bloc `finally`. Les événements passés ne sont pas rattrapés. Une protection empêche le même rappel d'exécuter deux fois son moment.

L'exécuteur utilise `homeassistant.helpers.script.Script`. Il journalise les erreurs d'une action et poursuit avec les suivantes.

## 10. Déchargement

`async_unload_entry()` décharge les plateformes sensor/calendar. Si ce déchargement réussit, il annule le rappel planifié et retire le panneau. Il retourne le résultat du déchargement des plateformes.

## 11. Suppression

`async_remove_entry()` lit `delete_data_on_remove`, désactivé par défaut. Si cette option est activée, il appelle `DayPlannerStorage.async_delete()`.

## 12. Config Flow

Le flow est en version 1. Il utilise `DOMAIN` comme identifiant unique, refuse une seconde configuration et crée une entrée de titre `Day Planner`, avec des données initiales vides. Il ne demande aucun paramètre initial.

## 13. Options Flow

Le menu propose un accès à la gestion graphique, les moments et leurs actions, les types de journée et leurs moments planifiés, les types de semaine, les cycles, les exceptions et les paramètres.

| Paramètre | Défaut | Contraintes |
| --- | --- | --- |
| `show_sidebar_panel` | `true` | Masquer le lien latéral conserve le panneau à `/day-planner`. |
| `delete_data_on_remove` | `false` | Contrôle la suppression du stockage au retrait. |
| `max_cycles` | `3` | De 1 à 4 ; ne peut pas devenir inférieur au nombre de cycles enregistrés. |

Les mutations de configuration utilisent le runtime pour sauvegarder et synchroniser. L'écouteur `_async_options_updated()` recharge l'entrée lors d'un changement d'options.

## 14. Services

Les 18 services du domaine `day_planner` fournissent `add_*`, `update_*` et `remove_*` pour six familles : `moment`, `day_type`, `scheduled_moment`, `week_schedule`, `cycle`, `calendar_exception`.

`_get_runtime(hass)` récupère le runtime. `_execute()` applique l'opération et appelle `async_configuration_updated()`. Il traduit les erreurs métier en `HomeAssistantError`. Les schémas sont définis dans `schemas.py` et les descriptions dans `services.yaml`.

Exemple de service :

```yaml
action: day_planner.add_scheduled_moment
data:
  day_type_id: travail
  moment_id: reveil
  time: "07:00:00"
```

Les objets référencés doivent déjà exister.

### WebSocket

Le frontend utilise l'API WebSocket, enregistrée par `async_setup_websocket_api()` :

- `day_planner/get_configuration` et `day_planner/get_calendar` ;
- commandes add/update/remove pour les six familles ci-dessus ;
- `day_planner/add_moment_action`, `day_planner/update_moment_action`, `day_planner/remove_moment_action`.

Les schémas WebSocket sont définis dans `websocket_api.py`. Ils diffèrent parfois des services : les services utilisent notamment `id`, tandis que les commandes WebSocket utilisent `moment_id`, `day_type_id`, etc.

### Frontend et panneau

`frontend.py` sert les fichiers à `/day_planner/frontend`. `panel.py` enregistre le panneau `/day-planner`, dont le module `day-planner-panel.js` réutilise `day-planner-card.js`.

Pour utiliser la carte dans Lovelace, ajouter la ressource module JavaScript `/day_planner/frontend/day-planner-card.js`, puis une carte :

```yaml
type: custom:day-planner-card
```

Le panneau enregistre son module indépendamment des ressources Lovelace. Les textes du frontend disposent de traductions française et anglaise.

## 15. Séparation domaine / Home Assistant

Les modèles métier et le calcul du planning sont séparés des adaptateurs Home Assistant : stockage, flows, services, WebSocket, ordonnanceur HA, exécution et entités.

Le planificateur importe actuellement certaines constantes de l'intégration. La séparation vise à limiter les dépendances Home Assistant et à permettre des tests ciblés du métier.

## 16. Tests

Résultat local communiqué par l'utilisateur le **14 octobre 2026** : **407 tests réussis**, **1 908 instructions mesurées**, **0 non couverte**, **100 %**, **5 avertissements**, en **1,22 s**, sous **Python 3.14.3**. La suite complète n'a pas été réexécutée par l'assistant.

Résultat GitHub Actions communiqué par l'utilisateur, **14 octobre 2026 à 12:15:34 Europe/Paris** : **407 tests réussis, 1 908 instructions et 100 % de couverture**. Environnement généré : Python 3.14.8, pytest 9.0.3, pytest-cov 7.1.0, pytest-homeassistant-custom-component 0.13.372. Ces chiffres précèdent le dernier nettoyage de la constante de version et du changelog ; les prochains rapports mesureront l'état des nouveaux commits.

Les ajouts sont intégrés aux fichiers existants :

- `test_validator.py` : références inconnues pour chacun des sept jours.
- `test_engine.py` et `test_validator.py` : données cohérentes avec les références renforcées.
- `test_scheduler.py` : moments simultanés, passage de minuit et trois scénarios DST Europe/Paris.
- `test_ha_scheduler.py` : exécution de tous les moments simultanés, replanification et protection contre les doublons.

Commande de référence, sans seuil bloquant :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio \
  -p pytest_cov \
  scripts/tests/ \
  --cov=custom_components/day_planner \
  --cov-report=term-missing \
  -q
```

Le chargement automatique des plugins est désactivé ; les deux plugins nécessaires sont chargés explicitement. Les dépendances de test et de couverture sont déclarées dans `requirements-dev.txt` du ZIP du 13 octobre.

Les rapports sont suivis sans seuil de couverture bloquant, conformément à la décision utilisateur. Les résultats chiffrés restent des instantanés datés et ne constituent pas une couverture du frontend JavaScript.

## 17. État technique de référence

### Corrections confirmées

- Contrôle des sept références des semaines types.
- Exécution de tous les moments simultanés dans un rappel.
- Calcul autour de minuit : le prochain événement appartient au bon jour et le moment de la veille n'est pas reporté.
- Calcul des changements d'heure selon la règle retenue : au printemps les moments manqués sont regroupés au premier instant valide ; en automne seule la première occurrence est exécutée.
- Suite complète Python réussie selon le rapport utilisateur du 14 octobre.

### Essais réels restant à confirmer — L1-06

| Essai | Observation attendue | Statut |
| --- | --- | --- |
| Passage de minuit | Type de journée, moment courant, prochain événement et calendrier se mettent à jour dans HA. | À confirmer |
| Rechargement avant un déclenchement | Ancien rappel annulé, nouveau rappel actif ; une seule exécution de chaque moment prévu. | À confirmer |
| Redémarrage avant un déclenchement | Seuls les événements encore futurs sont programmés ; pas de doublon. | À confirmer |
| Retour après un événement passé | Absence de rattrapage général des événements survenus pendant l'arrêt. | À confirmer |

Ces essais se feront avec des actions de test sans effet sur les appareils, sans modifier l'horloge système. Un rappel est prévu le **15 octobre 2026 vers 18 h, Europe/Paris**. L1-06 ne sera clôturé qu'après confirmation des essais réels.

### Autres points de suivi

Le workflow du 13 octobre cible bien Day Planner, déclare ses dépendances de test et transmet les échecs pytest. Les constats historiques contraires sont dépassés.

**L1-07 est terminé**, selon confirmation utilisateur : filtres alignés sur `tests.yml`, présentation du générateur corrigée et exécution GitHub Actions réussie avec mise à jour du README. Les rapports sont conservés sans seuil bloquant.

**L1-09 est terminé**, selon confirmation utilisateur : le manifeste indique 0.2.0, l'ancienne constante `VERSION = "0.0.2"` est supprimée et le changelog ne conserve qu'une entrée 0.1.0, datée du 10 octobre 2026 et restaurée d'après le tag existant.

La classe `Audit` n'est pas encore intégrée à la persistance ; le lot Metadata reste à planifier.

### Version et publication

- `manifest.json` fournit la version publiée ; `integration_info.py` lit ce manifeste pour les attributs communs des entités.
- `STORAGE_VERSION = 1` concerne le format du stockage et la version du Config Flow concerne le format de la Config Entry. Ces valeurs sont distinctes de la version publiée 0.2.0.
- `semantic-release` utilise les tags Git et l'historique des commits pour déterminer la prochaine release. Une version cible de roadmap ne constitue pas une release réalisée.
- La publication 0.2.0 a réussi après rétablissement de l'ascendance de la release 0.1.0 dans `main`, en conservant le tag publié.
- Le workflow de release récupère l'historique complet avec `fetch-depth: 0`. Son lancement manuel utilise `workflow_dispatch:`, au même niveau que `push:`.
- Le changement de version ne valide pas automatiquement les lots fonctionnels : Metadata n'est pas considéré comme livré en 0.2.0.

## 18. Évolutions prévues

- Définitions horaires avancées au-delà de `fixed_time`.
- Synchronisation avec Google Calendar.
- Traçabilité des modifications : auteur et horodatage.
- Poursuite des contrôles de cohérence et fiabilisation des vérifications CI et du frontend.

Ces évolutions doivent conserver la séparation entre domaine, moteur, persistance et adaptateurs Home Assistant.
