# Day Planner — Documentation technique

**Version publiée de référence : 0.2.0 (`manifest.json`). Documentation actualisée le 22 octobre 2026 : journalisation du 20 octobre conservée ; généralisation de la traçabilité `Audit` et validations fonctionnelles Home Assistant des 21–22 octobre intégrées. Il ne s’agit pas d’une nouvelle publication.**

*Portée : ce guide décrit les comportements validés par l’utilisateur jusqu’au 22 octobre. Les sources Python de `Ha DayPlanner/python` dans la bibliothèque peuvent être antérieures à ces changements : la documentation n’atteste pas leur actualisation et ne les remplace pas.*

## 1. Architecture

Les formulaires Home Assistant, les services et l'API WebSocket modifient la configuration via le moteur métier. Le runtime sauvegarde les modifications, actualise le résolveur, replanifie le prochain événement et informe les entités.

| Composant | Responsabilité |
| --- | --- |
| `PlannerEngine` / `PlannerValidator` | Manipulation et validation de la configuration. |
| `PlannerResolver` | Cycle, type de semaine, type de journée et exception applicables à une date. |
| `PlannerScheduler` | Événements d'une date, prochain événement, événement actif et moment courant. |
| `HomeAssistantScheduler` | Enregistrement et annulation du prochain rappel Home Assistant. |
| `ActionExecutor` | Exécution des actions des moments via `Script`, vérification des cibles explicites, journalisation et transmission du contexte d’exécution. |
| `logbook.py` | Description des événements Day Planner dans le Journal de bord et affichage de l’origine des changements d’état. |
| `DayPlannerStorage` | Persistance via Home Assistant `Store`. |
| `DayPlannerRuntimeData` | Composants actifs et synchronisation après modification. |
| Frontend / panneau | Gestion graphique utilisant l'API WebSocket. |
| Plateformes sensor/calendar | Exposition du planning à Home Assistant. |

## 2. Arborescence

Les principaux modules se trouvent dans `custom_components/day_planner/` :

- Intégration : `__init__.py`, `const.py`, `manifest.json`, `integration_info.py`.
- Configuration : `config_flow.py`, `options_flow.py`, `strings.json`, `translations/`.
- Interfaces : `services.py`, `services.yaml`, `schemas.py`, `websocket_api.py`.
- Exécution et journalisation : `runtime.py`, `ha_scheduler.py`, `action_executor.py`, `logbook.py`.
- Persistance : `storage.py`.
- Entités : `sensor.py`, `calendar.py`.
- Présentation : `frontend.py`, `panel.py`, `frontend/`.
- Domaine : `domain/` contenant les modèles et leurs conversions.
- Planificateur : `planner/engine.py`, `validator.py`, `resolver.py`, `scheduler.py`, `errors.py`, `protocols.py`.

Le frontend contient `day-planner-panel.js`, `day-planner-card.js`, `api.js`, `i18n.js`, `styles.js`, `utils.js`, `components/timeline.js` et les vues calendrier, moments, types de journée, types de semaine et cycles.

Les traductions du frontend (`frontend/translations/`) sont distinctes des traductions de l'intégration Home Assistant (`translations/`).

Les tests sont regroupés dans `scripts/tests/`, avec désormais 19 fichiers de tests incluant `test_logbook.py` (en plus des tests du domaine, moteur, validateur, résolveur, ordonnanceurs, exécuteur, stockage, runtime, initialisation, flows, services, WebSocket, entités et panneau).

## 3. Modèle de domaine

| Modèle | Champs |
| --- | --- |
| `Moment` | `id`, `name`, `icon=None`, `actions=()`, `audit=None`. |
| `DayType` | `id`, `name`, `scheduled_moments`, `audit=None`. |
| `ScheduledMoment` | `moment_id`, `time_definition`. |
| `TimeDefinition` | `fixed_time: time`. |
| `WeekSchedule` | `id`, `name`, sept références : `monday` à `sunday`, `audit=None`. |
| `Cycle` | `id`, `name`, `start_date: date`, `week_schedule_ids`, `audit=None`. |
| `CalendarException` | `id`, `date: date`, `day_type_id`, `description=None`, `audit=None`. |
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

`domain/metadata.py` définit `Audit` avec quatre champs : `created_by`, `created_at`, `modified_by` et `modified_at`. Depuis les évolutions validées les 21–22 octobre 2026, les cinq objets métier principaux (`Moment`, `DayType`, `WeekSchedule`, `Cycle`, `CalendarException`) exposent `audit: Audit | None = None` et sérialisent conditionnellement ce champ via `to_dict()` / `from_dict()`. Les horodatages sont au format ISO 8601, en UTC lors de leur génération.

L'audit est créé à l'ajout et mis à jour lors d'une édition. `PlannerEngine` centralise les fonctions `_create_audit()`, `_update_audit()`, `_with_created_audit()` et `_with_updated_audit()` ; les modifications conservent `created_by` et `created_at` lorsqu'ils existaient. Pour un objet ancien dont `audit` est absent ou nul, une première modification initialise l'audit **à la date de cette modification** : il ne faut pas interpréter ces données comme la création historique réelle.

Les `Action` d'un Moment et les `ScheduledMoment` d'un Type de journée ne portent pas d'audit distinct : leurs ajouts, modifications et retraits actualisent l'audit de leur objet parent. La suppression d'un objet racine ne laisse pas d'enregistrement d'audit persistant spécifique.

**Aucune migration ni reconstitution rétroactive des anciens audits n'est réalisée.** Un objet sans `audit` reste lisible ; son champ absent n'est pas ajouté automatiquement à la lecture.

## 4. PlannerConfiguration

Le conteneur racine possède cinq tuples : `moments`, `day_types`, `week_schedules`, `cycles`, `calendar_exceptions`.

`PlannerConfiguration.empty()` crée une configuration vide. `to_dict()` et `from_dict()` assurent la conversion des objets persistés. `has_data()` indique si au moins une collection contient des données.

Les actions sont imbriquées dans les moments ; elles ne constituent pas une collection racine.

## 5. PlannerEngine

Le moteur fournit les opérations get/add/update/remove pour les moments, types de journée, types de semaine, cycles et exceptions, ainsi que les opérations sur les moments planifiés.

Les mutations construisent une nouvelle configuration avec `dataclasses.replace`, la valident, puis remplacent la configuration du moteur. Les suppressions contrôlent les dépendances : moment utilisé par une journée, journée utilisée par une semaine ou une exception, semaine utilisée par un cycle.

Le constructeur reçoit `max_cycles`, dont la valeur par défaut est 3. Les méthodes `add_*()` et `update_*()` des cinq objets principaux acceptent `modified_by="system"` et délèguent la mise à jour des champs d’audit aux fonctions centralisées ; les références, contraintes métier et contrôles de suppression ne changent pas.

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

L'exécuteur utilise `homeassistant.helpers.script.Script`. Il journalise les erreurs d'une action et poursuit avec les suivantes : un échec ne bloque pas les autres actions du moment.

### Attribution des actions dans le Journal de bord — 20 octobre 2026

`ActionExecutor.async_execute_action()` crée un `homeassistant.core.Context`, puis émet l'événement **`day_planner_action` avant** l'appel à `Script.async_run(context=context)`, **en transmettant le même contexte**. Home Assistant peut ainsi relier un changement d'état ultérieur à l'action Day Planner plutôt qu'au seul service invoqué.

`logbook.py` enregistre deux types d'événements :

| Événement | Rôle | Présence dans le Journal de bord |
| --- | --- | --- |
| `day_planner_action` | Origine d'une exécution (`action_id`, `action_label`, `moment_id`, `moment_name`, `status=started`, éventuellement `requested_service`). | Une entrée à chaque action lancée. |
| `day_planner_action_result` | Résultat anormal avec `status=failed` ou `missing_targets`, liste des `missing_entities` et avertissements HA. | Entrée supplémentaire **uniquement en cas d'anomalie** ; pas de seconde entrée en cas de succès. |

Les constantes `EVENT_DAY_PLANNER_ACTION` et `EVENT_DAY_PLANNER_ACTION_RESULT` sont déclarées dans `const.py`.

Les clés renvoyées par les descriptions Logbook sont :

- `LOGBOOK_ENTRY_NAME` : intitulé de l'événement (ex. `Day Planner — action XX1 test (id : XX1)`).
- `LOGBOOK_ENTRY_MESSAGE` : détail de l'activité, avec moment et service demandé lorsqu'ils sont connus.
- `LOGBOOK_ENTRY_SOURCE` : libellé d'origine qui peut être repris pour expliquer le changement d'état d'une autre entité. **Cette clé ne crée pas le lien causal** : celui-ci dépend du `Context` partagé entre l'événement et le script Home Assistant.

Exemple validé dans l'interface Home Assistant le **20 octobre 2026** : l'action `XX1` (`XX1 test`), dans le moment `Retour Travail`, demande `input_boolean.turn_off` sur `input_boolean.day_planner_test`. Le Journal de bord présente **deux activités attendues** :

1. `Day Planner — action XX1 test (id : XX1)` : événement source, avec la description du service demandé.
2. `Day Planner Test : Activé → Désactivé` : changement d'état dont la cause affichée est `Day Planner — action XX1 test (id : XX1)`.

Sur la première activité, « Aucune cause n'a été enregistrée pour cette activité » signifie qu'aucun contexte **parent** n'est enregistré pour l'événement initial. Ce n'est pas une erreur d'exécution. Le changement d'état est, lui, attribué à l'action Day Planner.

`requested_service` est affiché seulement lorsque la séquence comprend **un unique appel littéral à un service**, avec une cible `entity_id` explicite et non ambiguë. Sa description ne prouve pas la modification d'état. Des intégrations exécutant des opérations indirectes ou différées peuvent perdre l'attribution si elles créent un nouveau contexte.

### Contrôle des entités cibles et niveaux de logs — 20 octobre 2026

Avant l'exécution, l'exécuteur contrôle les `entity_id` statiques des étapes directes de service (`target.entity_id`, `data.entity_id` ou `service_data.entity_id`). Les cibles absentes de `hass.states` ou à l'état `unavailable` produisent une trace **ERROR** Day Planner, avec action, moment, service, étape et entité. `unknown` n'est pas automatiquement assimilé à `unavailable`. Les cibles issues d'un template et les branches conditionnelles imbriquées ne sont pas pré-évaluées.

Pendant `Script.async_run`, les avertissements de `homeassistant.helpers.service` qui signalent des entités manquantes ou indisponibles sont recopiés en **ERROR** sous `custom_components.day_planner.action_executor` lorsque leur émission appartient au contexte actif de l'action. Le `WARNING` original de Home Assistant est conservé ; il n'est pas transformé ni supprimé. Cette interception temporaire, basée sur un `ContextVar`, ne couvre pas les traitements différés réalisés dans une autre tâche après la fin du script.

| Niveau | Usage dans Day Planner |
| --- | --- |
| `DEBUG` | Recherche et annulation des rappels, étapes d'action, contrôles de cibles, moments sans actions. |
| `INFO` | Chargement / déchargement, programmation, début et fin des moments ou actions. |
| `WARNING` | Bilan d'une action terminée avec des cibles manquantes ou des avertissements HA. |
| `ERROR` | Entité absente ou indisponible, avertissement HA repris, échec d'action, erreur inattendue de déclenchement. |

Exemple de configuration du journal technique Home Assistant (compléter le bloc `logger:` existant sans en créer un second) :

```yaml
logger:
  default: warning
  logs:
    custom_components.day_planner: debug
```

Pour limiter le volume, remplacer `debug` par `info`. Les messages techniques apparaissent dans les **journaux Home Assistant**, distincts des événements d'activité du **Journal de bord**.


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

Les mutations de configuration utilisent le runtime pour sauvegarder et synchroniser. L'écouteur `_async_options_updated()` recharge l'entrée lors d'un changement d'options. Le flux d’options transmet explicitement `modified_by="system"` pour les créations/modifications des cinq objets et pour les opérations sur les éléments imbriqués : aucun utilisateur HA fiable n’est disponible dans ce flux.

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

Les objets référencés doivent déjà exister. Lors des opérations de création et modification, les services obtiennent l’auteur par `_async_get_actor_name(call)` à partir de `call.context.user_id` et du registre d’authentification HA. Ils privilégient le nom affiché, sinon l’identifiant, sinon `"system"`. Le paramètre `modified_by` est transmis **à la méthode du moteur dans l’opération `_execute()`**, et non à `_execute()` lui-même.

### WebSocket

Le frontend utilise l'API WebSocket, enregistrée par `async_setup_websocket_api()` :

- `day_planner/get_configuration` et `day_planner/get_calendar` ;
- commandes add/update/remove pour les six familles ci-dessus ;
- `day_planner/add_moment_action`, `day_planner/update_moment_action`, `day_planner/remove_moment_action`.

Les schémas WebSocket sont définis dans `websocket_api.py`. Ils diffèrent parfois des services : les services utilisent notamment `id`, tandis que les commandes WebSocket utilisent `moment_id`, `day_type_id`, etc. Lors d’une création ou modification, les handlers transmettent `modified_by=connection.user.name or connection.user.id`. L’ajout, l’édition et la suppression d’une Action passent par `update_moment()` et actualisent donc l’audit du Moment.

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

**Mise à jour du 20 octobre 2026 :** le résultat intermédiaire de l'utilisateur indiquait **2 093 instructions**, dont **9 non couvertes**, soit **99 % au total**, avec `action_executor.py` à 93 % (131 instructions, 9 manquantes). Après ajout des tests complémentaires, l'utilisateur a confirmé : **« ok 100% »**. Ce 100 % est le résultat le plus récent communiqué ; le nombre final de tests exécutés, leur durée et le détail du nouveau rapport complet ne sont pas fournis. Les résultats chiffrés du 14 octobre restent conservés comme historique et ne doivent pas être confondus avec le rapport du 20 octobre.

Un contrôle ciblé simulant Home Assistant, exécuté lors de la préparation des tests du 20 octobre, a produit **19 tests réussis**, avec **100 %** de couverture pour `action_executor.py` (131/131 instructions) et `logbook.py` (31/31). Il ne remplace pas la suite complète exécutée par l'utilisateur.

**Dernier rapport complet chiffré communiqué le 21 octobre 2026 : 449 tests réussis, 5 avertissements, 2 146 instructions Python mesurées, aucune non couverte, 100 % de couverture globale (Python 3.14.3, 1,67 s).** L’utilisateur a ensuite confirmé les tests au fil des adaptations Options Flow et les contrôles HA, sans nouveau rapport chiffré complet partagé. La suite n’a pas été exécutée par l’assistant.

Les ajouts sont intégrés aux fichiers existants :

- `test_validator.py` : références inconnues pour chacun des sept jours.
- `test_engine.py` et `test_validator.py` : données cohérentes avec les références renforcées.
- `test_scheduler.py` : moments simultanés, passage de minuit et trois scénarios DST Europe/Paris.
- `test_ha_scheduler.py` : exécution de tous les moments simultanés, replanification et protection contre les doublons.
- `test_action_executor.py` : attribution du contexte, ordre de l'événement source avant le service, détection d'entités manquantes, avertissements HA corrélés, séquences/cibles ambiguës, répétitions et poursuite après un échec. Les neuf lignes initialement non couvertes sont visées (41, 43, 49, 92, 95, 108, 110, 134 et 153 de la version du 20 octobre).
- `test_logbook.py` : descriptions des événements d'origine et d'anomalie, `LOGBOOK_ENTRY_NAME`, `LOGBOOK_ENTRY_MESSAGE`, `LOGBOOK_ENTRY_SOURCE`, ainsi que l'absence de source sur l'événement d'anomalie.

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
- 20 octobre : attribution causale de l'action Day Planner au changement d'état confirmée dans le Journal de bord avec `XX1` et `input_boolean.day_planner_test` ; compléments de journalisation et tests validés, couverture globale 100 % reconfirmée par l'utilisateur.
- 21–22 octobre : audit ajouté et testé pour les cinq modèles, puis propagation de l’auteur dans `PlannerEngine`, WebSocket, services et Options Flow ; validations fonctionnelles HA confirmées pour Moments/Actions, Types de journée/Moments planifiés, Semaines types, Cycles et Exceptions.

### Essais réels Home Assistant — L1-06 clôturé le 22/10/2026

| Essai | Observation | Statut |
| --- | --- | --- |
| Action pilotant deux helpers | Les deux cibles sont commandées ; traces présentes dans les logs et événements. | Validé par l’utilisateur |
| Deux moments distincts simultanés | Les deux moments sont déclenchés à l’heure commune. | Validé par l’utilisateur |
| Modification d’horaire | Exécution au nouvel horaire sans exécution supplémentaire à l’ancien. | Validé par l’utilisateur |
| Exception de calendrier | Le type exceptionnel remplace le planning ordinaire et reprogramme les actions. | Validé par l’utilisateur |
| Changement de cycle | Recalcul et replanification du planning actif. | Validé par l’utilisateur |
| Passage de minuit | Continuité du planning au changement de journée. | Validé par l’utilisateur |
| Redémarrage avant un déclenchement | Programmation conservée et exécution unique. | Validé par l’utilisateur |
| Redémarrage après l’heure d’un événement manqué pendant un arrêt | Non-rattrapage général attendu, conformément aux tests Python. | À confirmer en situation réelle (L1-11) |

La validation du 22 octobre se fonde sur les confirmations de tests effectués par l’utilisateur dans Home Assistant, sans nouvelle exécution de la suite Python par l’assistant. L’essai du non-rattrapage après une interruption couvrant un événement reste séparé : il ne doit pas être assimilé au redémarrage avant déclenchement déjà validé. Un ancien rappel était prévu pour le **15 octobre 2026 vers 18 h, Europe/Paris** ; cette mention historique ne présume pas de son exécution.

### Autres points de suivi

Le workflow du 13 octobre cible bien Day Planner, déclare ses dépendances de test et transmet les échecs pytest. Les constats historiques contraires sont dépassés.

**L1-07 est terminé**, selon confirmation utilisateur : filtres alignés sur `tests.yml`, présentation du générateur corrigée et exécution GitHub Actions réussie avec mise à jour du README. Les rapports sont conservés sans seuil bloquant.

**L1-09 est terminé**, selon confirmation utilisateur : le manifeste indique 0.2.0, l'ancienne constante `VERSION = "0.0.2"` est supprimée et le changelog ne conserve qu'une entrée 0.1.0, datée du 10 octobre 2026 et restaurée d'après le tag existant.

La classe `Audit` est désormais sérialisée sur les cinq objets principaux ; les trois interfaces de mutation sont raccordées. Les tests et contrôles fonctionnels ont été validés par l’utilisateur. La présentation explicite de ces métadonnées dans les écrans de gestion n’est pas encore confirmée et reste distincte de leur présence dans le stockage.

### Version et publication

- `manifest.json` fournit la version publiée ; `integration_info.py` lit ce manifeste pour les attributs communs des entités.
- `STORAGE_VERSION = 1` concerne le format du stockage et la version du Config Flow concerne le format de la Config Entry. Ces valeurs sont distinctes de la version publiée 0.2.0.
- `semantic-release` utilise les tags Git et l'historique des commits pour déterminer la prochaine release. Une version cible de roadmap ne constitue pas une release réalisée.
- La publication 0.2.0 a réussi après rétablissement de l'ascendance de la release 0.1.0 dans `main`, en conservant le tag publié.
- Le workflow de release récupère l'historique complet avec `fetch-depth: 0`. Son lancement manuel utilise `workflow_dispatch:`, au même niveau que `push:`.
- Le changement de version ne valide pas automatiquement les lots fonctionnels : les travaux `Audit` ont été confirmés **après** la publication 0.2.0 ; ils ne sont pas déclarés livrés dans cette version.

## 18. Évolutions prévues

- Définitions horaires avancées au-delà de `fixed_time`.
- Synchronisation avec Google Calendar.
- Éventuelle présentation détaillée de la traçabilité dans le panneau et les formulaires (à qualifier) ; le mécanisme auteur/horodatage est désormais implémenté dans les données.
- Poursuite des contrôles de cohérence et fiabilisation des vérifications CI et du frontend.

Ces évolutions doivent conserver la séparation entre domaine, moteur, persistance et adaptateurs Home Assistant.
