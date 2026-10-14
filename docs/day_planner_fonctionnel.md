# Day Planner — Documentation fonctionnelle

**Version publiée de référence : 0.2.0. Documentation actualisée le 14 octobre 2026 à partir du code relu et des corrections confirmées par l'utilisateur.**

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

Ces règles sont vérifiées dans les tests Python pour Europe/Paris. Le rafraîchissement réel des entités à minuit et les scénarios de redémarrage/rechargement dans Home Assistant restent à confirmer dans L1-06.

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
- La traçabilité auteur/date des modifications n'est pas intégrée aux objets persistés, malgré la présence d'une classe `Audit` dans `metadata.py`.
- Aucun rattrapage général après un arrêt ; le traitement du changement d’heure au printemps constitue le cas particulier décrit plus haut.

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

La couverture est mesurée sans seuil bloquant. Elle ne garantit pas à elle seule le comportement réel de l'intégration et ne mesure pas la couverture du frontend JavaScript.

**L1-06 reste en cours.** À confirmer dans Home Assistant : rafraîchissement des capteurs et du calendrier à minuit, puis redémarrage/rechargement près d'un déclenchement, sans doublon ni rattrapage général. Les essais utiliseront des actions de test sans effet sur les appareils. Ils ne nécessitent pas de modifier l'horloge système.
