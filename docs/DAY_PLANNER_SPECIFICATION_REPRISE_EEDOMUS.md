# Day Planner — Reprise de l'agenda eedomus

**Spécification fonctionnelle consolidée v2.1 — 8 novembre 2026 (historique des règles antérieures conservé)**
**Statut :** fonctionnalités de reprise et d’aperçu testées progressivement sur Home Assistant ; documentation consolidée à la v5.16, recette globale et couverture 100 % non encore confirmées sur le nouvel ensemble de tests.
**Source de référence :** export eedomus du 1er novembre 2026.

## 1. Objectif

Importer **une seule fois** un agenda eedomus existant dans Day Planner, sans synchronisation, sans action réseau sur la box et sans modification des données eedomus.

La reprise crée dans Day Planner :

- une **semaine nommée d’après la box eedomus sélectionnée**, par exemple `Eedomus (192.20.55.30)` ;
- les **types de journée**, **moments** et **actions** nommés avec la même provenance lisible ;
- les **phases** converties en moments ;
- leurs **heures** converties en moments planifiés ;
- les **commandes directes** converties en actions HA, avec leurs entités cibles.

Elle ne crée **ni cycle, ni exception**. La semaine n'est pas automatiquement activée.

## 2. Parcours de l'utilisateur

1. Dans Home Assistant, ouvrir **Paramètres → Appareils et services → Day Planner → Configurer → Reprise agenda eedomus**.
2. Day Planner examine les **entrées de configuration eedomus actives** : `disabled_by is None` et `state == ConfigEntryState.LOADED`.
   - **aucune box configurée** : la reprise est indisponible ;
   - **box configurées mais aucune active** : un message d'activation est présenté ;
   - **une seule box active** : elle est choisie **automatiquement** et son nom est affiché ;
   - **plusieurs box actives** : l'utilisateur **sélectionne la box concernée** dans une liste utilisant son titre HA et son `entry_id`.
3. Le formulaire rappelle le lien officiel d'export : **[Import / Export eedomus](https://secure.eedomus.com/import_export)**.
4. L'utilisateur clique sur **Parcourir…** et choisit sur son ordinateur un export **JSON**. **Aucune copie manuelle sous `/config` n'est demandée** ; HA gère le fichier temporaire du sélecteur natif.
5. Day Planner affiche, **avant toute écriture**, les jours, moments, horaires et actions à créer, avec les associations d'entités HA, les limites et les erreurs éventuelles.
6. L'utilisateur confirme la création ou, si une reprise de **la même box** existe déjà, confirme explicitement son remplacement. L'annulation ne modifie rien.

**Il n'y a pas de téléchargement automatique depuis la box** : le lien permet de récupérer le JSON sur le site eedomus, puis le bouton Parcourir l'envoie à Home Assistant.

**Stockage du fichier :** la copie du JSON téléversée dans HA est temporaire et supprimée après l'analyse. Aucun fichier de conversion n'est automatiquement créé. Seuls les objets Day Planner sont persistés après confirmation dans le stockage interne `/config/.storage/day_planner.storage`. Le JSON d'origine reste sur le poste de l'utilisateur. En cas de contrôle refusé, il faut sélectionner à nouveau le fichier.

## 3. Comment reconnaître une box eedomus

Home Assistant conserve les installations eedomus sous la forme d'entrées `core.config_entries`. L'intégration Day Planner doit lire ces objets **par l'API interne `hass.config_entries.async_entries("eedomus")`**, pas en ouvrant ou en modifiant le fichier `.storage/core.config_entries`.

**Exemple de box :**

| Propriété | Exemple |
|---|---|
| `domain` | `eedomus` |
| `title` | `Eedomus (192.20.55.30) - Eedomus API Mode` |
| `entry_id` | `01KWFVW58SZD6W6WHB5YRHNDY9` |
| `unique_id` de la config entry | `eedomus_192.20.55.30` |

**Les identifiants des objets créés par Day Planner reprennent la chaîne `Eedomus (<api_host>)`**, obtenue depuis `data.api_host`. Une box sans `api_host` est refusée afin d'éviter des identifiants génériques. Le `entry_id` est encore utilisé **uniquement** pour identifier la configuration HA source, chercher ses entités et reconnaître les anciennes reprises. Il n'apparaît plus dans les nouveaux identifiants Day Planner. Les informations `api_user` et `api_secret` ne sont ni demandées, ni affichées, ni utilisées pour la reprise.

## 4. Rechercher la correspondance eedomus → entité HA

Pour chaque commande trouvée dans le JSON, on connaît l'identifiant de périphérique eedomus (ex. `3463520`). On interroge le **registre des entités Home Assistant**, limité à la box choisie et à la plateforme `eedomus`.

Quatre formes de `unique_id` doivent être acceptées, avec ou sans le préfixe littéral `eedomus_`, et avec ou sans suffixe de type :

```text
eedomus_<entry_id>_<id_eedomus>
eedomus_<entry_id>_<id_eedomus>_<suffixe_de_type>
<entry_id>_<id_eedomus>
<entry_id>_<id_eedomus>_<suffixe_de_type>
```

**Exemple :**

```text
entry_id HA       : 01KWFVW58SZD6W6WHB5YRHNDY9
périphérique      : 3463520
unique_id HA      : eedomus_01KWFVW58SZD6W6WHB5YRHNDY9_3463520_climate
ou                : eedomus_01KWFVW58SZD6W6WHB5YRHNDY9_3463520
ou                : 01KWFVW58SZD6W6WHB5YRHNDY9_3463520_climate
ou                : 01KWFVW58SZD6W6WHB5YRHNDY9_3463520
entity_id         : climate.thermostat_salle_a_manger
```

Les variantes comportant un suffixe `_battery` (y compris `..._sensor_battery` et `..._battery_level`) sont **exclues**, même si elles appartiennent à la bonne box et au même périphérique. L'entité principale reste candidate.

La correspondance doit porter sur **l'identifiant numérique complet**, sans apparier par préfixe (`3463520` ne doit pas correspondre à `34635201`). Le suffixe du type est variable ou absent. Le `entity_id` est lu dans le registre et peut avoir été renommé par l'utilisateur.

Pour convertir la commande, Day Planner tient compte du domaine réel de l'entité (`climate`, `cover`, `light`, `switch`, `input_boolean`). Les cibles **absentes, désactivées ou ambiguës** bloquent la reprise. En revanche, une entité présente mais d’un **domaine ou d’une commande non pris en charge** est signalée comme **ignorée** ; le moment et ses horaires restent créés même sans action compatible. Aucun service ni périphérique n’est deviné.

Exemple de conversion : « thermostat eedomus `3463520`, valeur `22.5` » → `climate.set_temperature`, cible `climate.thermostat_salle_a_manger`, donnée `temperature: 22.5`.

**Volets exposés en entités HA binaires :** le JSON de référence indique `Cmd 1 Volet Séjour (795317)` avec `100 = Ouvert` et `0 = Fermé`. Si l'entité HA correspondante est `switch`, `light` ou `input_boolean`, le convertisseur utilise respectivement `turn_on` ou `turn_off`. Si l'entité est `cover`, il utilise `cover.open_cover` ou `cover.close_cover`. Les valeurs qui ne peuvent pas être interprétées sont refusées avec la valeur, le libellé, l'ID périphérique et l'entité HA dans le diagnostic.

## 5. Objets créés dans Day Planner

| Objet Day Planner | Règle |
|---|---|
| Semaine type | `Eedomus (192.20.55.30)` |
| Type de journée | `Journée de travail — Eedomus (192.20.55.30)` |
| Moment | `Couché — Eedomus (192.20.55.30)` |
| Moment répété | `Couché (occurrence 2) — Eedomus (192.20.55.30)` |
| Action rattachée au moment | `Thermostat Salle a manger → 22.5°C — Eedomus (192.20.55.30)` |
| Moment planifié | Une occurrence pour chaque association journée + phase + heure ; ne possède pas de nom indépendant |

**Règle générale de nommage :** conserver le nom métier eedomus et lui ajouter ` — Eedomus (<api_host>)` pour chaque type de journée, moment et action. La semaine utilise exactement `Eedomus (<api_host>)`. La provenance lisible est calculée depuis la box HA sélectionnée. L'absence de `api_host` empêche l'import.

**Identifiants Day Planner :** semaine, journées, moments et actions utilisent tous le préfixe littéral `eedomus_Eedomus (<api_host>)_` :

```text
eedomus_Eedomus (192.20.55.30)_week
eedomus_Eedomus (192.20.55.30)_day_1
eedomus_Eedomus (192.20.55.30)_phase_7
eedomus_Eedomus (192.20.55.30)_phase_7_action_1
```

Les **`unique_id` du registre des entités Home Assistant eedomus** (cf. §4) continuent à contenir le `entry_id`. Il ne faut pas les modifier : ce sont deux espaces d'identifiants distincts.

Lors du remplacement confirmé, le correctif reconnaît les identifiants actuels **et ceux des anciennes versions** (`eedomus_<entry_id>_...`), supprime seulement les anciens objets appartenant à cette box et reprend leurs métadonnées d'audit. Une référence externe (cycle, exception) qui deviendrait invalide doit bloquer l'import. La simple installation ne renomme ni ne renumérote les objets déjà stockés.

**Précaution :** puisque l'adresse fait maintenant partie de l'identifiant Day Planner, changer `api_host` change l'identité des objets. Le remplacement après un changement d'adresse n'est pas automatiquement assimilable à l'ancienne reprise ; il faut vérifier/retirer les anciens objets. Deux configurations eedomus actives ayant le même `api_host` sont refusées pour éviter les collisions.

**Phases répétées dans une journée :** préserver chaque heure. Si Day Planner interdit de programmer deux fois le même identifiant de moment dans une journée, créer des moments distincts pour les occurrences supplémentaires, avec les mêmes actions. Cela ne concerne pas la présence de deux événements à la même heure.

### Contrôle de l'export du 1er novembre

- Dernier export vérifié : **1er novembre 2026 à 18:02:44** (`eedomus_export_morin01_2026.11.01 (1).json`).
- 9 types de journée, 8 phases distinctes, 7 affectations hebdomadaires, **41 horaires**.
- La semaine est inchangée par rapport au 29 octobre. Dans **Journée de travail**, les phases « Couché » de 06:25 et 07:54 ont été supprimées et « Lever » a été avancé de 06:26 à 06:25.
- La phase **Couché** n'apparaît plus qu'à **00:00** dans cette journée : **aucune phase répétée** dans une même journée du dernier export.
- Sur ce jeu de données, la reprise prévoit **8 moments Day Planner** et **10 actions HA directes**. La règle de création de moments supplémentaires en cas de répétition reste conservée.
- Les **7 règles conditionnelles actives** identifiées ne sont pas ajoutées aux moments comme actions systématiques. Elles sont signalées dans le bilan.

## 6. Confirmation et remplacement

- **Première reprise pour la box** : créer les objets avec préfixe `eedomus_Eedomus (<api_host>)_`.
- **Reprise déjà présente pour cette box** : reconnaître le préfixe actuel et le préfixe historique `eedomus_<entry_id>_` ; exiger une confirmation explicite pour la substitution.
- **Ne pas modifier** les éléments manuels ou provenant d'une autre box eedomus.
- **Ne pas supprimer silencieusement** des objets déjà référencés dans un cycle ou dans une exception ; dans ce cas, refuser la reprise et indiquer le blocage.
- Construire et valider la configuration complète **avant** de l'enregistrer. Ne déclencher aucune action HA lors de la création.
- Conserver les métadonnées d'audit initiales des objets remplacés ; renseigner l'auteur de modification lorsque disponible.

La suppression indépendante de l'import n'est pas incluse dans ce correctif ; le traitement demandé est la **création ou le remplacement** après confirmation.

## 7. Ce qui reste hors périmètre

- Synchronisation régulière ou téléchargement réseau automatique ;
- Création automatique d'un cycle ou gestion d'exceptions eedomus ;
- Conversion automatique de macros eedomus et de règles conditionnelles complexes ;
- Modification de la box eedomus ;
- Exécution d'un service HA pendant l'import.

## 8. Critères de réception

1. Aucun / un / plusieurs enregistrements `eedomus` : comportement conforme du choix de box.
2. Le lien d'export est visible et conduit à `https://secure.eedomus.com/import_export`.
3. Le sélecteur ouvre la fenêtre système pour choisir le JSON, sans demander de chemin `/config`.
4. Les `unique_id` **avec ou sans préfixe `eedomus_`, avec ou sans suffixe** sont associés correctement, sans collision entre box ni entre IDs proches ; les entités `_battery` sont exclues.
5. Le dernier export du 1er novembre (18:02:44) est retrouvé : 9 journées, 41 horaires, sans répétition ; la règle de reprise des répétitions reste testée.
6. Les actions directes sont converties en services HA seulement lorsque l'entité et l'état sont déterminés.
7. Le bilan signale distinctement les règles conditionnelles non reprises.
8. Une première reprise n'écrase pas les données manuelles.
9. Une seconde reprise nécessite une confirmation de remplacement et ne touche que la box choisie.
10. Annulation ou erreur : pas de configuration partiellement importée ; pas d'exécution d'actions HA.
11. Tous les noms affichés **et tous les identifiants Day Planner créés** (semaine, journée, moment, action) reprennent la chaîne `Eedomus (<api_host>)`. Les anciens identifiants utilisant `entry_id` sont reconnus lors d'un remplacement confirmé.
12. Les contrôles Python, traductions, tests unitaires, non-régression et essais dans HA OS sont exécutés avant validation finale.

## 9. État de réalisation

La **reconstruction complète v5** prépare : sélection conditionnelle de box, téléversement JSON, recherche de `unique_id` avec ou sans suffixe en excluant `_battery`, extraction de l'agenda, prévalidation et remplacement confirmé. La lecture et l'extraction du JSON du 1er novembre ont été vérifiées localement ; la correspondance d'identifiants, notamment l'exclusion `_battery`, a été exercée avec un registre simulé (7 tests isolés).

**Non validé ici :** tests intégrés dans le venv Home Assistant, interface réelle du navigateur, correspondance des entités installées, couverture complète, Black, isort, flake8 et tests d'installation HA OS. Ce document décrit le comportement prévu et le correctif préparé, pas un déploiement testé.

## Évolution v1.4 — correctif v5.2

- Box configurées mais désactivées ou dont le chargement a échoué exclues du sélecteur.
- Commandes `100/Ouvert` et `0/Fermé` reconnues sur les entités HA binaires.
- Diagnostic de conversion affiché dans le formulaire avec la cause exacte.
- Clarification du cycle de vie du JSON téléversé et du stockage des objets Day Planner.
- Tests isolés du convertisseur et du moteur : 76 réussis. Quatre scénarios du flux testés avec doubles de composants, sans HA réel ; recette HA OS et suite intégrée à effectuer.

## Évolution v1.6 — correctif v5.4

- Étend le nommage basé sur `Eedomus (<api_host>)` de la semaine **aux types de journée, aux moments, aux occurrences répétées et aux libellés d'actions**.
- Les identifiants techniques de tous les objets restent fondés sur le `entry_id` et ne changent pas.
- Lors d'une nouvelle importation ou d'un remplacement confirmé, tous les noms sont calculés à partir de la box actuellement sélectionnée.
- Tests isolés importeur et moteur : **78 réussis**, avec deux tests spécifiques au nommage de tous les objets et au remplacement. Les tests Home Assistant intégrés et la couverture du projet restent à exécuter sur l'installation cible.

## Évolution v1.7 — correctif v5.5

- Remplace le préfixe `eedomus_<entry_id>_` dans **tous les IDs internes Day Planner importés** par `eedomus_Eedomus (<api_host>)_`, en conservant le nom affiché issu de la box.
- Ne modifie **pas** les `unique_id` du registre des entités HA : la recherche des périphériques continue avec le `entry_id` et exclut `_battery`.
- Détecte les anciens imports `eedomus_<entry_id>_` et leur impose une confirmation de remplacement ; les créations manuelles sont préservées.
- Refuse une box sans `api_host` et plusieurs configurations eedomus actives pointant vers une adresse identique.
- Test de conversion sur l'export du 1er novembre à 18:02 : **9 journées, 8 moments, 41 horaires, 10 actions** ; remplacement identique sans doublons.
- Tests du convertisseur, moteur, validateur et résolveur : **127 passés avec registre HA simulé** ; tests intégrés sur HA OS à relancer.

## Ajout v1.8 — variantes de `unique_id` du registre HA

Le préfixe `eedomus_` est maintenant facultatif pour la **recherche d'entités Home Assistant**. Le filtre sur la `config_entry` et la plateforme `eedomus` reste obligatoire ; l'identifiant numérique eedomus est comparé dans son intégralité. Les suffixes contenant le segment `_battery` sont exclus. Si plusieurs entités actionnables correspondent au même ID, la reprise est refusée plutôt que de choisir arbitrairement.

Cette évolution ne change ni les identifiants des objets Day Planner (`eedomus_Eedomus (<api_host>)_...`), ni les `unique_id` détenus par Home Assistant.


## Règle v1.9 — Associations incompatibles et moments sans action

Les commandes ciblant une entité Home Assistant dont le domaine ne fait pas partie des domaines acceptés par Day Planner, ou dont la commande ne peut pas être convertie sans ambiguïté, ne sont pas importées comme actions. Elles sont toutes recensées dans la confirmation, avec l’identifiant périphérique eedomus, l’entité HA et le motif. Les autres actions compatibles sont conservées.

Une phase eedomus crée **toujours un moment Day Planner** (et ses créneaux horaires), même si aucune action active ou compatible ne reste ; le moment possède alors une liste d’actions vide. Les erreurs de résolution des identifiants (aucune association ou plusieurs cibles compatibles), de désactivation et d’incohérence structurelle restent bloquantes.


## Règle v2.0 — Télécharger les associations depuis Home Assistant

Dans **Confirmer la reprise eedomus**, Day Planner doit afficher, sous le tableau des correspondances, un lien cliquable marqué **📥 Télécharger les associations (CSV pour Excel)**. Le lien n'est pas un fichier produit par ChatGPT ni un export eedomus : il permet d'obtenir **à la demande** un CSV de l'aperçu de reprise courant, directement depuis Home Assistant.

Le fichier contient les associations reconnues **et** ignorées, avec trois colonnes : `Périphérique eedomus (ID)` ; `Entité Home Assistant` ; `Statut / motif`. Il est enregistré en UTF-8 avec BOM, avec un séparateur `;`, et utilise le nom d'hôte de la box choisie dans le nom du fichier. Les champs sont protégés des formules de tableur. Le tableau TSV copiable existant reste disponible.

L'intégration met à disposition une route HTTP dédiée (`/api/day_planner/eedomus_associations.csv`), accessible uniquement par **un lien signé Home Assistant temporaire** et un jeton aléatoire non devinable. Le lien expire au bout de 15 minutes ; aucune copie du tableau n'est enregistrée sous `/config` ni dans la configuration Day Planner. L'action de téléchargement ne valide ni ne déclenche l'import.

Les tests doivent couvrir le CSV, son encodage, les caractères particuliers, le nom de fichier, l'expiration, la protection de la route et la présence du lien dans la confirmation.

## Complément v2.1 — classeur sept onglets, interface et couverture (8 novembre 2026)

La v5.16 conserve le lien CSV et ajoute un export XLSX **généré en mémoire**, lisible par Excel, avec **sept onglets** : **Résumé**, **Toutes associations**, **Prises en charge**, **Ignorées**, **Éléments non repris**, **Moments et actions**, **Journées et horaires**. Les données proviennent du plan d’import validé et de son JSON extrait ; les onglets ne doivent pas importer les objets manuels du planner. Voir `export_xlsx_eedomus.md`.

La zone de copie des associations est **sélectionnable** (`Ctrl+A` / `Ctrl+C`) : les précédents champs `read_only` provoquaient un curseur d’interdiction dans le frontend. Les traductions ne doivent pas contenir de balises HTML non autorisées (erreur `INVALID_TAG` antérieure). Les liens de téléchargement restent signés et temporaires ; l’ouverture par clic simple n’est pas garantie dans toutes les versions du routeur de Home Assistant.

**Exigence de validation :** viser 100 % de couverture sans exclusions ou seuil bloquant. Dernier rapport global transmis avant complément : **517 tests, 2 990 instructions, 243 non couvertes, 92 %**. 55 nouveaux tests de couverture ont été préparés et vérifiés de façon ciblée ; seule une nouvelle exécution complète permettra d’attester **100 % global**.

**Évolution différée :** préserver les sept feuilles actuelles. À très long terme (lot 7 de la roadmap), envisager en priorité les **propriétés du fichier XLSX lui-même** (titre, auteur, description, sujet, mots-clés), puis seulement d’éventuelles retouches de feuilles. Rien de cela n'est implémenté au titre de la v5.16.
