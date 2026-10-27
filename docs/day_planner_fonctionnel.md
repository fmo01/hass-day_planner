# Day Planner — Documentation fonctionnelle

**Version publiée de référence : 0.2.0. Documentation actualisée le 22 octobre 2026 : traçabilité des cinq objets métier et contrôles fonctionnels Home Assistant confirmés. Les travaux réalisés après la publication 0.2.0 ne constituent pas une nouvelle release.**

## 1. Présentation

Day Planner est une intégration Home Assistant destinée à gérer un planning journalier et hebdomadaire.

Elle permet de définir des **moments**, des **types de journée**, des horaires associés aux moments, des **types de semaine**, des **cycles** et des **exceptions de calendrier**.

Le planificateur calcule les événements à venir et déclenche les actions associées aux moments aux heures prévues.

## 2. Concepts

### Moment

Un moment représente un événement logique de la journée : Réveil, Départ, Retour, Coucher, Nuit, etc.

Il possède un `id`, un `name`, une `icon` facultative et une liste d'`actions`. Le moment ne définit pas son heure. Ses actions sont communes à toutes ses utilisations dans les types de journée.

### Type de journée

Un type de journée représente une journée particulière : Travail, Télétravail, Week-end, Vacances, Garde ou Absence.

Il contient une liste de moments planifiés. Un même moment peut avoir une heure différente selon le type de journée.

| Type de journée : Télétravail | Moment |
| --- | --- |
| 08:00 | Réveil |
| 09:00 | Début travail |
| 12:00 | Déjeuner |
| 18:00 | Fin travail |
| 23:00 | Coucher |

### Traçabilité des modifications

Les **Moments**, **Types de journée**, **Semaines types**, **Cycles** et **Exceptions du calendrier** conservent des informations d'audit facultatives :

| Champ | Signification |
| --- | --- |
| `created_by` | Auteur enregistré lors de la création suivie par Day Planner. |
| `created_at` | Date et heure de cette création. |
| `modified_by` | Auteur de la dernière modification. |
| `modified_at` | Date et heure de la dernière modification. |

La modification d'une **Action** actualise l'audit de son **Moment parent** ; la modification de l'horaire ou le retrait d'un **Moment planifié** actualise l'audit de son **Type de journée parent**. Les objets simplement référencés par une Semaine type, un Cycle ou une Exception conservent leur propre historique inchangé.

Dans le panneau Day Planner (WebSocket) et dans les services HA, le nom affiché de l'utilisateur est privilégié, à défaut son identifiant ; si aucun utilisateur n'est identifiable, `"system"` est utilisé par les services. Les formulaires **Configurer / Options** enregistrent explicitement `"system"` comme auteur.

**Aucune migration des anciens objets n'est réalisée.** Les données dépourvues de champ `audit` restent accessibles. Leur premier changement crée un audit à partir de la date et de l'auteur de cette modification, sans inventer une date de création antérieure. L'audit est stocké avec la configuration ; son affichage détaillé directement dans l'interface graphique reste à qualifier.

### Moment planifié

Un `ScheduledMoment` associe un moment à une définition d'heure (`TimeDefinition`). La seule définition actuellement disponible est une heure fixe (`fixed_time`). Les horaires se règlent dans les types de journée.

### Type de semaine

Un `WeekSchedule` associe chacun des sept jours à un type de journée. Par exemple : Travail du lundi au vendredi, Week-end le samedi et le dimanche.

### Cycle

Un cycle enchaîne de 1 à 4 types de semaine et répète cette séquence. Il possède une date de début, obligatoirement un lundi.

Pour une date donnée, le cycle applicable est celui dont la date de début est la plus récente parmi les cycles déjà commencés. Il reste applicable jusqu'au début d'un cycle plus récent. Deux cycles ne peuvent pas commencer à la même date.

Le nombre maximal de cycles enregistrés est réglable de 1 à 4, avec une valeur par défaut de 3. Cette limite est distincte du nombre de semaines composant chaque cycle.

Avant le début du premier cycle, aucun type de journée n'est déterminé à partir des cycles. Une exception peut toutefois définir le type de journée de cette date.

### Exception de calendrier

Une exception remplace le type de journée normalement prévu pour une date donnée. Elle est prioritaire sur les cycles, sans modifier leur séquence.

Elle contient `id`, `date`, `day_type_id` et une `description` facultative. Une seule exception est autorisée par date.

Exemple : `01/01/2027 → Jour férié`.

Les exceptions se gèrent dans le calendrier du panneau ou dans les options de l'intégration.

### Actions

Chaque action possède un identifiant, un libellé et une séquence de script Home Assistant. Si aucun libellé n'est fourni à la construction de l'action, son identifiant est utilisé.

Exemple de données d'une action :

```yaml
id: allumer_salon
label: Allumer le salon
sequence:
  - service: light.turn_on
    target:
      entity_id: light.salon
```

À l'heure prévue, les actions du moment sont exécutées dans leur ordre de définition. Si une action échoue, l'erreur est journalisée et les actions suivantes sont tentées. Le prochain événement est ensuite replanifié.

#### Retrouver l'origine d'un changement d'état dans le Journal de bord

Depuis le correctif du **20 octobre 2026**, Day Planner déclare l'origine de chaque action **avant** d'exécuter les services Home Assistant, pour que le Journal de bord puisse rattacher les changements d'état à l'**action Day Planner précise**, et non simplement au service appelé.

Exemple testé dans Home Assistant :

```yaml
id: XX1
label: XX1 test
sequence:
  - action: input_boolean.turn_off
    target:
      entity_id: input_boolean.day_planner_test
```

Déclenchée par le moment **Retour Travail**, cette action a produit les deux activités suivantes dans le Journal de bord :

| Activité | Ce que l'on voit |
| --- | --- |
| **Day Planner — action XX1 test (id : XX1)** | « a déclenché l'action 'XX1 test' (moment : Retour Travail) ; service demandé : input_boolean.turn_off → input_boolean.day_planner_test ». C'est l'événement d'origine. |
| **Day Planner Test — Activé → Désactivé** | Le changement d'état est attribué à **Day Planner — action XX1 test (id : XX1)**. C'est la conséquence vérifiée dans HA. |

Dans le détail de la première activité, **« Aucune cause n'a été enregistrée pour cette activité »** est normal : l'événement Day Planner de départ n'a pas de cause parente connue. Cela n'empêche pas la seconde activité de référencer correctement cette action comme origine.

**À distinguer :** « service demandé » décrit l'action configurée, pas la réussite d'une commande physique. L'origine peut ne pas être conservée lorsqu'une intégration effectue ensuite une opération asynchrone indépendante. En cas d'anomalie d'exécution, une activité Day Planner supplémentaire peut indiquer l'échec ou une cible indisponible ; il n'y a pas d'entrée de résultat supplémentaire à chaque succès.

#### Entités absentes et journaux techniques

Day Planner signale dans ses propres journaux, au niveau **ERROR**, les cibles statiques absentes ou indisponibles ainsi que les avertissements HA correspondants détectés pendant l'action. Le `WARNING` original de Home Assistant reste présent. Les séquences conditionnelles et les cibles dynamiques ne sont pas toutes prévisibles avant exécution.

Dans les journaux techniques HA, les niveaux utilisés sont : `DEBUG` (détails), `INFO` (programmation et exécutions), `WARNING` (bilan d'anomalie) et `ERROR` (entité manquante ou échec). Pour activer les détails :

```yaml
logger:
  default: warning
  logs:
    custom_components.day_planner: debug
```

Compléter un bloc `logger:` existant plutôt que le dupliquer. Les traces techniques n'apparaissent pas comme telles dans l'export du Journal de bord. Voir la documentation technique pour les limites de détection.

Les événements déjà passés ne sont pas rattrapés lors du démarrage ou d'une replanification, hors traitement spécifique de l'heure supprimée au printemps.

### Moments simultanés et changements d'heure

Tous les moments programmés au même instant sont exécutés une fois, dans l'ordre du planning, par un seul rappel Home Assistant.

Pour les horaires fixes, la règle de changement d'heure retenue est celle du cron de Debian :

| Situation | Règle d'exécution |
| --- | --- |
| Printemps : 02:00 devient 03:00 en Europe/Paris | Les moments de l'heure supprimée sont exécutés au premier instant valide, à 03:00, dans leur ordre horaire d'origine. |
| Moment normalement prévu à 03:00 ce même jour | Il est inclus dans le même groupe que les moments rattrapés. |
| Automne : l'heure 02:00–03:00 est répétée | Chaque moment est exécuté au premier passage uniquement. |
| Redémarrage ou rechargement après un événement passé | Aucun rattrapage général. L'exception de rattrapage concerne uniquement l'heure supprimée par le changement d'heure. |

Ces règles de changement d’heure sont vérifiées dans les tests Python pour Europe/Paris. Les sept contrôles fonctionnels L1-06 (dont passage de minuit et redémarrage avant un déclenchement) ont été validés dans Home Assistant par l’utilisateur le 22 octobre 2026. Le cas distinct d’un événement manqué pendant un arrêt demeure à confirmer en situation réelle (L1-11).

## 3. Règles de cohérence

- Les identifiants des moments, types de journée, types de semaine, cycles et exceptions doivent être uniques entre ces collections.
- Un moment planifié doit référencer un moment existant.
- Un même moment ne peut pas apparaître deux fois dans un même type de journée.
- Chaque cycle contient de 1 à 4 références à des types de semaine existants.
- Les dates de début des cycles sont des lundis et sont uniques.
- Le nombre de cycles respecte la limite configurée.
- Chaque exception référence un type de journée existant et sa date est unique.
- Dans un moment, les identifiants d'actions sont non vides et uniques ; leurs séquences sont non vides.
- La suppression d'un moment utilisé par un type de journée est refusée.
- La suppression d'un type de journée utilisé par une semaine ou une exception est refusée.
- La suppression d'un type de semaine utilisé par un cycle est refusée.

Les sept associations d'un type de semaine doivent désigner des types de journée existants. Le validateur métier contrôle désormais chacune de ces références et refuse une journée inconnue avant d'accepter la configuration.

## 4. Configuration Home Assistant

### Création et gestion

Day Planner utilise une unique Config Entry Home Assistant, créée depuis **Paramètres → Appareils et services → Ajouter une intégration**. Le planning initial est vide ; les moments définis dans les constantes ne sont pas automatiquement ajoutés.

Le panneau `/day-planner` propose cinq vues : calendrier, moments, types de journée, types de semaine et cycles. Il permet de gérer les objets du planning, les horaires et les actions des moments. Les exceptions sont gérées dans le calendrier.

Le menu **Configurer** propose également des formulaires de gestion et un lien vers le panneau.

Pour construire un premier planning : créer les moments, définir les types de journée et leurs horaires, associer les journées aux types de semaine, puis créer un cycle commençant un lundi. Ajouter ensuite les exceptions nécessaires.

### Paramètres

| Paramètre | Valeur par défaut | Fonction |
| --- | --- | --- |
| `show_sidebar_panel` | `true` | Affiche le panneau dans le menu latéral. Le masquer conserve l'accès direct à `/day-planner`. |
| `max_cycles` | `3` | Limite le nombre de cycles enregistrés, de 1 à 4. Une valeur inférieure au nombre de cycles existants est refusée. |
| `delete_data_on_remove` | `false` | Supprime les données persistantes lors du retrait de l'intégration si activé. |

Les changements de paramètres déclenchent un rechargement de l'intégration.

### Entités

Les identifiants ci-dessous sont ceux visés par l'intégration ; ils peuvent varier selon le registre Home Assistant.

| Entité | Fonction |
| --- | --- |
| `sensor.day_planner_next_event` | Nom du prochain moment, avec `moment_id` et `scheduled_at` en attributs. |
| `sensor.day_planner_current_day_type` | Type de journée courant ; attributs de date, cycle, type de semaine et exception. |
| `sensor.day_planner_current_moment` | Dernier moment atteint dans la journée courante. |
| `calendar.day_planner_planning` | Événements du planning, représentés chacun par une durée d'une minute. |

Le moment courant correspond au dernier moment atteint du jour, jusqu'au suivant. Avant le premier moment du jour, aucun moment courant n'est retourné ; le moment de la veille n'est pas reporté. La durée d'une minute concerne les événements du calendrier.

## 5. Suppression

Les données sont stockées dans `/config/.storage/day_planner.storage`.

Par défaut, le retrait de l'intégration conserve ces données. Si `delete_data_on_remove` est activé, le stockage est supprimé au retrait de la Config Entry.

## 6. Limites actuelles

- Seules les heures fixes sont disponibles.
- Aucune synchronisation Google Calendar n'est implémentée.
- Le calendrier Home Assistant expose les événements. La modification des exceptions passe par Day Planner, ses options ou ses interfaces de programmation.
- La traçabilité existe dans les données persistées. Son affichage détaillé dans les écrans de gestion n’est pas encore qualifié ; elle ne constitue pas un journal indépendant des suppressions.
- Aucun rattrapage général après un arrêt ; le traitement du changement d’heure au printemps constitue le cas particulier décrit plus haut.
- L'attribution Logbook repose sur le contexte propagé par Home Assistant ; elle peut être perdue lors d'une confirmation différée par une autre intégration.

## 7. État de validation

Résultat local communiqué par l'utilisateur le **14 octobre 2026** :

| Mesure | Résultat |
| --- | --- |
| Tests réussis | 407 |
| Instructions Python mesurées | 1 908 |
| Instructions non couvertes | 0 |
| Couverture Python | 100 % |
| Avertissements | 5 |
| Durée | 1,22 s |
| Python | 3.14.3 |

La suite inclut les tests des moments simultanés, des références des sept jours, du passage de minuit et trois tests de changement d'heure. Une exécution GitHub Actions confirmée par l'utilisateur à **12:15:34 Europe/Paris** rapporte également **407 tests réussis, 1 908 instructions et 100 % de couverture**, sous Python 3.14.8. Ces résultats sont des instantanés datés ; ils n'ont pas été réexécutés intégralement par l'assistant et précèdent le dernier nettoyage de version/changelog. Les prochains rapports automatiques font référence pour les nouveaux commits.

**Résultat le plus récent, communiqué le 20 octobre 2026 : couverture Python globale de 100 % confirmée par l'utilisateur** après ajout des tests liés à l'exécuteur d'actions et au Journal de bord. Le rapport intermédiaire indiquait 2 093 instructions, dont 9 non couvertes (99 %, exécuteur à 93 %) ; les nouveaux tests ont été validés et l'utilisateur a confirmé le retour à 100 %. Le nombre exact de tests de cette dernière exécution complète n'a pas été communiqué. Les 407 tests du tableau ci-dessus correspondent uniquement au résultat historique du 14 octobre.

**Dernier rapport complet chiffré du 21 octobre 2026 : 449 tests réussis, 2 146 instructions Python mesurées, 0 non couverte, 100 % de couverture, 5 avertissements, en 1,67 s sous Python 3.14.3.** L’utilisateur a confirmé les tests après les dernières adaptations et réalisé les contrôles fonctionnels en HA les 22 octobre : Moments et Actions, Types de journée et Moments planifiés, Semaines types, Cycles et Exceptions du calendrier. La suite complète n’a pas été relancée par l’assistant et aucun nouveau rapport de comptage ultérieur n’est disponible.

Le test réel du Journal de bord du 20 octobre confirme également l'attribution de la désactivation de `input_boolean.day_planner_test` à l'action `XX1` du moment `Retour Travail`.

La couverture est mesurée sans seuil bloquant. Elle ne garantit pas à elle seule le comportement réel de l'intégration et ne mesure pas la couverture du frontend JavaScript.

**L1-06 est clôturé le 22 octobre 2026** sur les sept scénarios fonctionnels HA confirmés : action sur deux helpers avec traces, deux moments simultanés, replanification après changement d’horaire, exception, changement de cycle, passage de minuit et redémarrage avant déclenchement. **L1-11 demeure à confirmer** pour un événement dont l’horaire est passé pendant un arrêt HA ; les tests Python décrivent le non-rattrapage général attendu. Aucun essai réel distinct de ce dernier cas n’est affirmé.
