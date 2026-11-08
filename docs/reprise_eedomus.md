# Day Planner — Guide de reprise ponctuelle de l’agenda eedomus

**État : 8 novembre 2026 · Développement de référence : v5.16 sur Day Planner 0.2.3.** Les correctifs v5.x ne sont pas des releases officielles.

## Avant de commencer

À partir du site [Import / Export eedomus](https://secure.eedomus.com/import_export), récupérer le JSON sur l'ordinateur. Ne pas placer ce fichier potentiellement sensible dans `/config/www` ou dans un dossier public. La reprise est ponctuelle et **ne synchronise pas** l'agenda eedomus après l'import.

## Dans Home Assistant

1. Ouvrir **Paramètres → Appareils et services → Day Planner → Configurer → Reprise agenda eedomus**.
2. Sélectionner la box eedomus **active et chargée** (sélection automatique s’il n’y en a qu’une).
3. Choisir le JSON avec le sélecteur de fichiers du navigateur Home Assistant.
4. Examiner le résumé et le **tableau d’associations**, avec les entités compatibles et ignorées.
5. Facultativement, sélectionner/copier le tableau (`Ctrl+A`, puis `Ctrl+C`) ou demander le rapport **CSV/XLSX** avant toute importation.
6. Confirmer la création ; en cas de reprise de la même box déjà présente, confirmer explicitement son remplacement.

La semaine porte le nom **`Eedomus (<api_host>)`** ; cette provenance est réutilisée dans les noms et identifiants Day Planner de ses journées, moments et actions. Les entités et `unique_id` de l'intégration eedomus dans HA demeurent inchangés.

## Éléments créés et non repris

| Élément | Traitement |
| --- | --- |
| Semaine et types de journée | Création à partir de l'export. |
| Phases / moments | Créés même **sans action compatible**, avec leurs horaires. |
| Actions directes compatibles | Converties vers les services HA autorisés : `climate`, `cover`, `light`, `switch`, `input_boolean`. |
| `sensor` et autres domaines non acceptés | **Ignorés comme actions**, avec affichage de l'entité et de la raison ; ne bloquent pas à eux seuls. |
| Entités `_battery` | Écartées des associations candidates. |
| Cible absente, désactivée ou ambiguë | Prévalidation bloquante, sans action arbitraire ni écriture partielle. |
| Règles conditionnelles et paramètres internes non reconnus | **Non repris** ; signalés dans le récapitulatif et l’export Excel. |
| Cycle / exception | **Non créés** ; la semaine importée doit être affectée ultérieurement si nécessaire. |

Les associations sont recherchées dans le registre des entités de la **configuration eedomus sélectionnée** : `unique_id` avec ou sans préfixe `eedomus_`, avec ou sans suffixe, toujours comparé sur le véritable numéro de périphérique. Les entités orphelines d'anciennes configurations ne sont pas réutilisées comme cibles.

Le JSON téléversé est temporaire, puis supprimé après analyse. Les objets créés sont persistés dans la configuration Day Planner après confirmation. Aucune commande n'est exécutée sur les appareils lors de la reprise.

## Rapports et limites

La confirmation présente un tableau unique avec **statut / motif** et un champ copiable. Le CSV est disponible à l’ancienne route ; le classeur **XLSX sept onglets** contient un résumé, toutes les associations, les associations prises en charge, les ignorées, les éléments non repris, les moments/actions et les journées/horaires.

Les téléchargements utilisent des liens signés temporaires et ne déposent pas de fichiers dans `/config`. Le routeur frontend Home Assistant peut intercepter un clic normal selon l’environnement ; le comportement réel du clic doit être vérifié sur l’instance. Les données du dernier export testé (1er novembre à 18:02) étaient **9 types, 8 moments, 41 horaires et 10 actions directes**, avant prise en compte des incompatibilités propres aux entités HA installées.

## Recette

Contrôler la box sélectionnée, les périphériques `sensor` visibles comme ignorés, l’absence d’action sur un moment qui n’a plus d’action compatible, le téléchargement XLSX à sept feuilles, l'absence d’écriture avant confirmation, et le remplacement limité à la même box.

**Couverture :** dernière exécution complète communiquée : 517 tests réussis, 92 %, 243 lignes manquantes sur 2 990. Le complément préparé doit être revalidé en suite complète avant d’annoncer 100 %.

Voir [spécification technique détaillée](DAY_PLANNER_SPECIFICATION_REPRISE_EEDOMUS.md), [export XLSX](export_xlsx_eedomus.md) et [roadmap](ROADMAP.md).
