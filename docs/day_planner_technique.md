# Day Planner — Documentation technique

**Version de référence : 0.1.0 (`manifest.json`)**

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

Le contrôle systématique des sept références de types de journée d'un `WeekSchedule` manque actuellement dans le validateur métier. Les séquences d'actions ne font pas l'objet d'une validation complète de script par ce validateur.

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

Le ZIP de référence contient 18 fichiers `test_*.py` et 365 fonctions de test, hors expansion des tests paramétrés. Ce décompte statique ne garantit ni leur réussite ni une couverture donnée.

Dans un environnement compatible, installer les dépendances de développement et `pytest-cov`, puis lancer :

```bash
PYTHONPATH=. python3 -m pytest scripts/tests/ \
  --cov=custom_components/day_planner \
  --cov-report=term-missing -q
```

`requirements-dev.txt` du ZIP ne déclare pas `pytest-cov`. Le workflow fourni utilise Python 3.14.

Publier le résultat avec la date, la version du code et les versions Python, Home Assistant, pytest et pytest-cov. L'ancien résultat « 97 tests, 477 instructions, 100 % » ne doit pas être utilisé comme résultat actuel.

## 17. État technique de référence

La version 0.1.0 contient CRUD, stockage, résolution des jours, calcul des événements, exécution des actions, calendrier, capteurs et interface de gestion.

La relecture documentaire du 12 octobre 2026 n'inclut pas une exécution des tests. Les points suivants restent à corriger ou vérifier :

- `const.py` indique `VERSION = "0.0.2"`, contrairement au manifeste 0.1.0.
- Le contrôle des références des jours des types de semaine est incomplet dans le validateur.
- La traçabilité `Audit` n'est pas intégrée à la persistance.
- Le workflow `tests.yml` conserve des vérifications eedomus et masque l'échec de pytest avec `|| echo ...` ; un statut vert ne garantit donc pas la réussite des tests Day Planner.
- `requirements-dev.txt` conserve un commentaire hass-eedomus et omet pytest-cov.
- Le changelog contient deux entrées 0.1.0, datées des 11 et 12 octobre 2026 ; la date de publication doit être vérifiée avant fusion.

## 18. Évolutions prévues

- Définitions horaires avancées au-delà de `fixed_time`.
- Synchronisation avec Google Calendar.
- Traçabilité des modifications : auteur et horodatage.
- Complément du contrôle des références et fiabilisation des vérifications CI.

Ces évolutions doivent conserver la séparation entre domaine, moteur, persistance et adaptateurs Home Assistant.
