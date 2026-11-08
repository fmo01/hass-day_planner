# Day Planner — Export XLSX eedomus (v5.16, documentation consolidée au 8 novembre 2026)

**Base :** v5.15 de la reprise ponctuelle eedomus.

Ce correctif conserve le téléchargement `.xlsx` depuis **Home Assistant → Day Planner → Reprise agenda eedomus → Confirmer**. Il ajoute **3 onglets**, pour un total de **7**, sans modifier l'import des moments ni déclencher de service HA.

| Onglet | Contenu |
|---|---|
| Résumé | Box, nombres de journées, moments, horaires et actions ; limites de la reprise |
| Toutes associations | Entités eedomus ↔ Home Assistant et statut |
| Prises en charge | Associations acceptées |
| Ignorées | Associations non supportées et motifs |
| **Éléments non repris** | Règles conditionnelles actives non reprises (ID, nom, nombres de conditions/actions), paramètres internes non résolus (phase, cible, valeur), associations/commandes incompatibles (avec motif) |
| **Moments et actions** | Chaque moment créé et chaque action effectivement intégrée dans Day Planner : IDs, libellés, service, entité cible ; les moments sans action restent présents |
| **Journées et horaires** | Tous les types de journée importés, chaque moment planifié et son horaire, y compris les occurrences répétées et celles sans action |

Les objets manuels et ceux d'autres box ne figurent pas dans les nouveaux tableaux « Moments et actions » et « Journées et horaires ». Les heures proviennent des `scheduled_moments` de la configuration **validée**, tandis que les éléments non repris proviennent du **JSON extrait** associé à la box sélectionnée.

Le fichier est généré en mémoire par Day Planner, puis servi via le lien signé et temporaire existant ; aucun XLSX n'est déposé dans `/config`. Le comportement du clic et la navigation du frontend ne sont pas changés.

## Installation depuis la v5.15

Depuis la racine du dépôt, après sauvegarde :

```bash
unzip -o day_planner_eedomus_v5_16_trois_onglets.zip -d .
```

Redémarrer Home Assistant, choisir la box et le JSON, puis télécharger le classeur depuis la confirmation. Vérifier la présence des **7 onglets**.

## Vérifications

Le test du classeur confirme les 7 onglets, les trois nouveaux tableaux, les filtres adaptés à leur nombre de colonnes, la conservation des moments sans action et l'exclusion des objets manuels. Les tests de téléchargement et du formulaire ont été mis à jour pour transmettre le JSON à la génération du rapport.

Pour la suite complète sur ton environnement Home Assistant :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio -p pytest_cov scripts/tests/ \
  --cov=custom_components/day_planner --cov-report=term-missing -q
```

La validation complète HA OS et la couverture globale à 100 % restent à exécuter sur ton installation.

## Règles de maintenance et amélioration différée

Le classeur est généré pour **la box et le JSON sélectionnés** dans la confirmation de reprise, sans import préalable ni écriture permanente du fichier sur le serveur. Les tableaux comptabilisent aussi les associations ignorées et les moments sans action. Les identifiants Day Planner générés à partir de `Eedomus (<api_host>)` restent distincts des identifiants du registre HA.

**Statut actuel : conserver les sept onglets tels quels.** Le **lot 7 de la roadmap** prévoit seulement à très long terme l'enrichissement **des propriétés/métadonnées du fichier XLSX** (titre, sujet, auteur, description, mots-clés), et éventuellement des retouches aux feuilles. Ce travail n'est pas inclus dans la v5.16.

**Couverture :** le dernier rapport global utilisateur annonce 517 tests, 92 % ; 55 tests de complément ont été préparés, mais le 100 % global n'est pas encore attesté par une nouvelle exécution entière.
