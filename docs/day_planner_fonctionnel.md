# Day Planner — Documentation fonctionnelle

## L7-07 — Qualification automatisée transversale (11 novembre 2026)

L7-06 est validé sur HA par l’utilisateur. L7-07 complète les tests existants et les contrôles de qualité. Aucun code de production n’est modifié : carte 0.2.12, utils.js et i18n.js 0.1.1 inchangés. L7-08 reste à réaliser pour la recette finale et la clôture du lot 7.

Deux tests transversaux supplémentaires ont été intégrés aux modules existants : consultation des années 2026, 2027 et 2028 après une seule résolution géographique, puis déplacement hors ligne sans réutilisation des jours fériés de l’ancien lieu ; et consultation des fêtes suivie de l’ajout, de la modification et de la suppression d’une exception, sur ces mêmes années. Le planning reste celui du cycle lors de la simple consultation. L’exception enregistrée est appliquée, son audit de création est conservé en modification et sa suppression restaure le cycle.

| Bloc vérifié | Tests concernés |
| --- | --- |
| Pays, subdivisions, ambiguïtés, erreurs réseau, cache et redémarrage | `test_runtime.py`, `test_sensor.py`, `test_init.py` |
| Dates fixes/mobiles, fêtes observées, fêtes locales, plusieurs pays et années | `test_runtime.py` |
| Réponse HA native et consultation sans écriture | `test_services.py` |
| Exception, audit et retour au cycle | `test_engine.py`, `test_resolver.py`, `test_websocket_api.py` |
| Rendu, traductions, changements de lieu/année, réponses tardives, erreurs/reprise, formulaires | `scripts/tests/frontend/calendar.test.mjs` |

Résultat complet : **704 tests pytest réussis**, **26 tests JavaScript réussis**, **3 407 instructions Python couvertes sur 3 407 (100 %)**, cinq avertissements de dépendances et aucun test ignoré dans cette exécution. Le total pytest inclut un seul lanceur pour les 26 tests JS ; la couverture Python ne mesure pas le JavaScript. Les statistiques du README des tests sont régénérées à partir des rapports avec le code du workflow existant.

Contrôles réussis sur `custom_components/day_planner` et `scripts/tests` : Black, isort, flake8 (120 colonnes), syntaxe de tous les modules JavaScript frontend, lecture des JSON de l’intégration et contrôle des espaces du patch. Une correction de mise en forme seulement a été appliquée à `test_engine.py`. Ruff reste indisponible dans l’environnement local ; il n’a pas été exécuté. Les tests réseau utilisent des réponses simulées. Aucune nouvelle validation navigateur réel, HA, HACS ou hassfest n’est attribuée à ce lot ; les essais IHM antérieurs sont les validations utilisateur L7-04 à L7-06.

La livraison contient uniquement les tests et la documentation modifiés, avec un patch depuis L7-06. Aucun fichier n’est à recopier dans `custom_components` sur HA et aucun redémarrage n’est nécessaire pour cette livraison. La recette finale L7-08 doit encore consolider les essais ordinateur/mobile/clavier, les années, le redémarrage et les cas de localisation/réseau sur l’installation de test.

## L7-06 — Validation et enregistrement des exceptions (11 novembre 2026)

L7-05 a été validé sur HA par l’utilisateur, avec les versions console corrigées `utils.js v0.1.1` et `i18n.js v0.1.1`. L7-06 a ensuite été validé sur HA par l’utilisateur.

En ajout comme en duplication, une date invalide ou une date possédant déjà une exception est refusée avant l’appel au serveur. En ajout comme en modification, un type de journée doit être choisi et doit appartenir à la configuration chargée. Le backend contrôle également le type et l’unicité de la date : une configuration devenue obsolète côté navigateur ne permet pas d’écraser une exception ou de référencer un type supprimé.

La description est facultative et peut rester vide, même sur un jour férié. Les champs sont conservés dans le brouillon après un refus de validation ou un échec du serveur. La suggestion de fête n’est pas réinjectée. Une nouvelle tentative reste possible. La modification garde l’identité et la date de l’exception ; le moteur conserve les métadonnées de création et actualise celles de modification avec le nom affiché HA, ou l’identifiant si aucun nom n’est disponible. Aucune migration d’audit n’est ajoutée.

Pendant l’enregistrement, les boutons Enregistrer/Créer et Annuler sont désactivés et les appels répétés sont ignorés. Échap ne ferme pas le formulaire pendant la requête. Avant enregistrement, Annuler et Échap ferment le formulaire sans écriture. Après réussite, la configuration et le calendrier sont rechargés. La suppression conserve son parcours existant.

Les messages de date invalide, de doublon et de type devenu inconnu sont définis dans les fichiers de traduction frontend FR et EN. La carte affiche désormais **0.2.12** ; les autres modules JavaScript ne sont pas modifiés par ce lot.

Validation locale : **702 tests pytest réussis**, incluant un lanceur de **26 tests JavaScript réussis**, et **100 % de couverture Python (3 407 instructions)**. Les cinq avertissements proviennent des dépendances. Les tests JS couvrent les validations FR/EN, les doublons, les saisies après erreur et la reprise, le double enregistrement, Annuler et Échap. Trois cas supplémentaires du moteur vérifient qu’un refus conserve la configuration et les métadonnées d’audit. Les tests d’audit et de transmission du nom affiché déjà présents restent réussis. La couverture annoncée ne mesure pas le JavaScript ; les tests de modale utilisent des objets DOM simulés et ne remplacent pas la recette visuelle HA. Syntaxe JS, JSON, flake8 et application du patch vérifiés. Ruff n’est pas installé dans l’environnement de vérification ; aucun résultat Ruff n’est revendiqué.

## L7-05 — Description proposée à la création d’une exception (11 novembre 2026)

L7-04 est validé par l’utilisateur : pytest OK et tests IHM OK sur HA. L7-05 a ensuite été validé sur HA par l’utilisateur.

La commande Ajouter une exception reste le point d’entrée. À son ouverture sur un jour férié dont les données sont disponibles pour le contexte courant, la description est préremplie avec le nom de la fête. Plusieurs noms à la même date sont réunis par « / ». Aucun préfixe en dur n’est ajouté : les noms proviennent des données de jours fériés déjà traduites selon la configuration HA. La description reste modifiable et peut être effacée. Le type de journée doit être choisi explicitement.

Sur une date ordinaire ou lorsque les données sont absentes, en erreur ou devenues obsolètes après un changement de lieu, la description initiale reste vide. Une réponse reçue après l’ouverture du formulaire ne réécrit pas la saisie. Les réserves locales affichées par L7-04 restent consultables dans les détails du jour.

L’examen du code confirme que Modifier existe déjà : il réutilise le type de journée et la description enregistrés, en conservant la date. Aucun second bouton n’est ajouté. Une duplication conserve la description de la source. L’ouverture du formulaire ne crée aucune exception ; l’enregistrement reste explicite et l’annulation utilise le parcours existant.

Validation : **699 tests pytest réussis**, incluant un test lançant **20 tests JavaScript réussis** ; **3 407 instructions Python couvertes sur 3 407 (100 %)**. Les cinq avertissements de dépendances restent inchangés. La couverture Python ne mesure pas le JavaScript. Les tests JS ajoutés couvrent les noms multiples, les données absentes/obsolètes, l’échappement HTML, les réponses tardives, la description personnalisée ou effacée et la conservation de la date/description en modification et duplication. Les validations transversales détaillées restent au périmètre L7-06.

## L7-04 — Jours fériés dans le calendrier (11 novembre 2026)

L7-03 est validé par le retour utilisateur au redémarrage. Le cache de Montreuil / Seine-Saint-Denis a été relu avec `from_cache: true`, `resolved_at` conservé à 15:30:18 UTC et `last_evaluated` actualisé à 15:36:36 UTC. Le fichier de stockage est resté inchangé pendant cette lecture.

L7-04 affiche un repère avec icône et nom pour les jours fériés de l’année consultée. Le pays et la subdivision disponibles figurent au-dessus du calendrier, avec la portée du calendrier retenu. Le type de journée et les exceptions restent visibles à côté du repère. Le nom complet, la portée nationale/locale et les réserves sont repris dans les détails de la date sélectionnée. Les avertissements locaux, dont le Vendredi saint en Alsace-Moselle, sont ainsi consultables dans les détails.

Sur ordinateur, le survol affiche les informations complètes. Les cases possèdent un libellé accessible et un état de sélection. Au clavier, la sélection d’une date conserve le focus sur la case. Sur petit écran, le libellé peut être tronqué et le texte complet est accessible en sélectionnant le jour. Les états de chargement, les limites de couverture et les erreurs s’affichent au-dessus du planning. Une erreur de consultation propose « Réessayer ».

Les nouveaux textes d’interface utilisent `frontend/translations/fr.json` et `en.json`. Les noms des fêtes proviennent de l’action backend dans la langue configurée de HA, avec le repli déjà défini dans L7-02. L’affichage recharge les données lors d’un changement d’année ou de contexte géographique. Une réponse obsolète est ignorée, y compris lors d’une navigation rapide entre mois.

Validation locale effectuée avec **699 tests Python réussis et 3 407 instructions couvertes sur 3 407 (100 %)**, dont un test qui lance **15 contrôles JavaScript réussis**. La couverture indiquée concerne le backend Python. Les contrôles JavaScript valident la consultation, le rendu HTML, les traductions, les changements de contexte, les erreurs/reprises et l’échappement des textes. La recette visuelle dans HA reste à faire, car le navigateur de vérification n’a pas pu accéder à l’aperçu local. Les contrôles de syntaxe JS et de lint du test Python passent. Les statistiques sont régénérées avec le workflow existant.

La livraison est incrémentale depuis L7-03. Elle comprend les fichiers modifiés et un patch alternatif. Après installation, recharger complètement la page du navigateur, puis vérifier des mois avec fêtes nationales et locales, une date avec exception, le passage décembre/janvier, les détails au clavier et l’affichage mobile.

## L7-03 — Cache persistant de la localisation (11 novembre 2026)

L7-02 a été validé par l’utilisateur sur son installation Home Assistant. L7-03 a ensuite été validé au redémarrage sur l’installation de l’utilisateur.

Day Planner conserve la dernière localisation résolue dans `/config/.storage/day_planner_location`. Au redémarrage, il la réutilise si le pays et les coordonnées du domicile HA correspondent et si la résolution date de moins de 30 jours. Le capteur `binary_sensor.day_planner_location` indique alors `from_cache: true`. `resolved_at` conserve la date de résolution et `last_evaluated` indique la nouvelle évaluation.

À l’expiration ou lors d’un changement de lieu, une nouvelle résolution est déclenchée si aucun cache utilisable ne correspond. En cas d’échec réseau ou HTTP, un nouvel essai a lieu une heure plus tard. Un échec laisse le dernier résultat réussi sur disque. Le planning et les exceptions enregistrées restent utilisables. Les dates de jours fériés se calculent localement pour l’année demandée.

Validation locale avec Python 3.14.10 et HA 2026.10.4 : 698 tests réussis et 100 % de couverture (3 407 instructions). Le test de redémarrage utilise un fichier créé par le véritable stockage HA et deux instances successives. Le réseau est simulé.

## L7-02 — calcul local des jours fériés (10 novembre 2026)

État courant : L7-01 v3 installé par l’utilisateur, tests annoncés à 100 %, rechargement HA sans erreur et changement de lieu vérifié sur plusieurs lieux. Les pays et les scénarios de panne testés ne sont pas précisés. L7-02 a ensuite été validé par l’utilisateur sur son installation HA. Les notes antérieures ci-dessous restent conservées comme historique.

### Cache mémoire et cache persistant à la livraison de L7-02

Le cache actuel conserve en mémoire la résolution géographique pour un même contexte pays/coordonnées ; il disparaît au redémarrage. Un cache persistant sauvegardera ces données dans le stockage de HA pour les retrouver après redémarrage, avec contrôle du contexte, de l’âge et de la validité. Un changement de lieu devra invalider l’ancien résultat ; aucune exception ne sera réécrite. Cette persistance, la durée de validité et les reprises espacées restent à réaliser dans L7-03. L7-02 ne les ajoute pas.

### Consultation et résultats

Dans **Outils de développement → Actions**, exécuter :

```yaml
action: day_planner.get_public_holidays
data:
  year: 2027
```

L’action retourne l’année, le pays, la subdivision retenue, la langue, la source/version, le statut et les dates avec leurs noms et leur portée. `ready` signifie que la sélection de calendrier prise en charge est complète ; `partial` signifie que seules les dates nationales sont disponibles faute de subdivision exploitable ; `unsupported` signale un pays ou une année non pris en charge ; `unavailable` signale notamment une localisation indisponible ou modifiée pendant le calcul. `reason_detail` et `warning_details` donnent les explications traduites. Une réserve locale peut accompagner une date même lorsque le statut est `ready`.

Aucun nouveau capteur n’est créé : `binary_sensor.day_planner_location` continue de décrire la localisation. Aucun jour férié n’est encore affiché dans la vue calendrier (L7-04) ; aucune exception ni action planifiée n’est créée ou modifiée. Dans un script/une automatisation, l’appel utilise `response_variable: jours_feries` pour exploiter la réponse.

### Règles et limites

Le calcul utilise **holidays==0.108**, en local et hors de la boucle événementielle ; il ne contacte pas de service de jours fériés. La localisation initiale conserve le géocodeur de L7-01. Le pays et les subdivisions viennent de l’installation HA, jamais de la langue ou du fuseau. Les codes ISO et leurs parents sont confrontés aux subdivisions réellement supportées. Une province belge ne permet pas de déduire arbitrairement une communauté linguistique : le résultat reste national et `partial`. Une localité correspondant exactement à un calendrier spécifique de la bibliothèque peut être utilisée (ex. Augsburg).

Les départements français 67/68 sont associés à `6AE`, la Moselle à `57`. Grand Est seul reste ambigu ; les jours nationaux sont retournés avec un statut incomplet. Le Vendredi saint en Alsace-Moselle porte une réserve explicite : la condition d’applicabilité communale n’est pas vérifiée. Les territoires pris en charge dépendent de la bibliothèque, sans promesse de couverture communale universelle.

Les noms sont ceux de holidays dans la langue HA si supportée, sinon dans la langue par défaut du calendrier (anglais en dernier recours). Les libellés de l’action et explications utilisent `strings.json` et `translations/en.json`, `translations/fr.json`. Les jours observés/reportés sont inclus (`observed: true`), les noms coïncidant à une même date sont préservés, et seules les dates appartenant à l’année demandée sont retournées. Les années hors plage du calendrier sont signalées explicitement.

### Validation et livraison

**686 tests réussis ; 3 342 instructions couvertes sur 3 342, soit 100 % ; 5 avertissements de dépendances ; 6,48 s.** Environnement : Python 3.14.10, Home Assistant 2026.10.4, holidays 0.108. Les contrôles incluent plusieurs pays, les niveaux géographiques parents, les dates mobiles, les coïncidences, les jours observés, les dimanches suédois ordinaires exclus, les limites de support, les changements de contexte, les traductions et un appel réel du registre de services HA avec réponse. Ces tests locaux ne remplacent pas la recette sur l’installation de l’utilisateur. L’actualisation automatique des statistiques via le workflow existant est conservée.

Livraison incrémentale **depuis L7-01 v3 déjà installé** : ZIP des seuls fichiers ajoutés/modifiés, avec patch alternatif et instructions. Installer les fichiers puis redémarrer HA pour charger la nouvelle dépendance et l’action ; aucune nouvelle release GitHub/HACS n’est déclarée.

## Correctif L7-01 v3 — traductions natives Home Assistant

**10 novembre 2026 : correction demandée par l’utilisateur après identification de textes français en dur dans L7-01 v2.** La localisation internationale et l’identifiant `binary_sensor.day_planner_location` sont conservés.

- Le nom du capteur utilise désormais `translation_key = "location"` et `has_entity_name = True`, sans `_attr_name` en français dans le Python.
- `strings.json` contient les textes sources anglais. Les fichiers HA `translations/en.json` et `translations/fr.json` fournissent le nom, les libellés des attributs, les trois statuts et les onze motifs d’échec sous `entity.binary_sensor.location`.
- Le nom affiché est « Day Planner — Localisation » en français et « Day Planner — Location » en anglais. L’identifiant et les codes `status`/`reason` restent stables pour les automatisations.
- L’attribut lisible `reason_detail` utilise les ressources natives chargées par `async_get_translations`, dans la langue de HA au chargement de l’intégration, avec le repli anglais assuré par HA. Aucun dictionnaire de messages français ni repli textuel français n’est conservé dans le Python.
- Les noms de pays, subdivisions et localités restent des données fournies par le géocodeur et le référentiel ISO ; la marque de l’intégration et l’attribution de la source restent leurs noms propres.

**Validation locale : 622 tests réussis, 3 203 instructions couvertes sur 3 203 (100 %), 5 avertissements de dépendances, 2,03 s ; Python 3.14.10 et HA 2026.10.4.** Les nouveaux contrôles emploient le véritable chargeur de traductions HA sur les fichiers JSON livrés, vérifient les noms et motifs en FR/EN, le repli anglais, la parité des clés et la couverture de tous les motifs émis par le résolveur. Les contrôles Black/isort/flake8 des fichiers modifiés passent. Statistiques de tests régénérées avec le code du workflow existant ; actualisation automatique conservée.

Livraison : ZIP cumulatif des fichiers ajoutés/modifiés et `.patch` depuis la base GitHub main `0562541cbd339041d46aeb8267971630f32a1f0c`, sans nécessité d’installer v1 ou v2. Les essais réels HA/Photon et les travaux L7-02/L7-03 restent distincts ; cette correction ne constitue pas une nouvelle publication.

## Reconstruction L7-01 v2 — localisation internationale et capteur

**Paquet complet reconstruit à la demande de l’utilisateur, qui n’a rien installé du premier paquet.** `day_planner_L7-01_v2.zip` remplace le prototype FR : il ne nécessite aucun fichier ni patch de la première livraison. Base du dépôt : main `0562541cbd339041d46aeb8267971630f32a1f0c`, manifeste 0.3.1 ; aucune nouvelle release GitHub/HACS n’est déclarée.

### Fonctionnement implémenté

- Pays et coordonnées issus du domicile HA : coordonnées de `zone.home` lorsqu’elles sont disponibles, sinon configuration générale HA. Aucun nouveau réglage de lieu, ni localisation par IP, téléphone ou navigateur.
- Recherche internationale via **Photon / OpenStreetMap** (`https://photon.komoot.io/reverse`), sans clé API. Les coordonnées sont transmises à ce service lors d’une recherche ; son attribution est exposée dans le capteur. La disponibilité et la précision dépendent du service et des données OSM, sans garantie mondiale de résolution de toutes les subdivisions.
- Pays/subdivisions normalisés avec **pycountry 26.2.16**. Correspondance par code ISO complet ou nom normalisé exact ; pas de choix par similarité approximative. Les pays hors de France ne sont plus exclus. Un pays incohérent avec la configuration HA, des résultats administratifs contradictoires ou une subdivision non identifiée produisent un motif explicite.
- Évaluation initiale en arrière-plan et nouvelles évaluations lors des changements de configuration du domicile ou de `zone.home`. Requêtes HTTP asynchrones, délai maximal de 10 secondes ; lecture du référentiel ISO hors de la boucle événementielle. Les réponses devenues obsolètes ne sont pas publiées ; les tâches et écouteurs sont annulés au déchargement.
- Réutilisation **en mémoire** d’un résultat réussi pour le même contexte pays/coordonnées. Le cache persistant entre redémarrages, les tentatives espacées après panne et la durée de validité restent à implémenter sous L7-03. Aucune interrogation périodique du géocodeur n’est ajoutée.

### Capteur disponible

`binary_sensor.day_planner_location` — **Day Planner — Localisation**, entité de diagnostic. Activé si la résolution géographique est exploitable ; désactivé après une évaluation non résolue ; indisponible avant la première évaluation, pour un résultat invalidé par changement de domicile ou après déchargement.

Attributs : `integration`, `integration_version`, `release_url`, `last_evaluated`, `country_code`, `country_name`, `subdivision_code`, `subdivision_name`, `locality`, `subdivisions`, `source`, `attribution`, `from_cache`, `resolved_at`, `status`, `reason` et `reason_detail`. Ce dernier donne une explication lisible en français. Les dates ISO 8601 comportent leur fuseau ; `resolved_at` reste distinct de la dernière évaluation lorsqu’un résultat mémorisé est réutilisé.

Une évaluation peut être demandée avec l’action HA `homeassistant.update_entity` ciblant ce capteur. Les propriétés du capteur ne font aucun appel réseau. L’identifiant proposé est stable, sous réserve du registre HA et d’un renommage utilisateur.

**Limite de L7-01 :** le capteur indique la résolution géographique, pas encore la disponibilité exacte des règles de calendrier de L7-02. Les subdivisions identifiées sont exposées pour cette étape suivante. Le paquet ne calcule ni n’affiche encore les jours fériés et ne crée/modifie aucune exception.

### Vérifications et essais restants

Suite complète : **620 tests réussis**, **3 201 instructions couvertes sur 3 201 (100 %)**, **5 avertissements de dépendances**, **2,11 s**, Python **3.14.10**, Home Assistant **2026.10.4**. Cas simulés multi-pays : France, Allemagne, Suisse, États-Unis, Belgique, Australie, Canada, Japon et Vatican ; erreurs, ambiguïtés, cache mémoire, changement de domicile, réponses obsolètes, déchargement et capteur vérifiés. Tests intégrés aux modules existants `test_runtime.py`, `test_sensor.py` et `test_init.py`.

Black, isort profil black et flake8 (120 caractères) vérifiés sur les fichiers Python modifiés. Les statistiques du README des tests sont régénérées avec le code du workflow existant ; le mécanisme automatique après tests reste conservé. `pycountry` est déclaré à la fois dans le manifeste pour HA et dans les dépendances de développement utilisées par la CI.

**Aucune installation ni recette HA réelle n’est affirmée.** Les essais HTTP réels sur coordonnées publiques n’ont pas abouti dans l’environnement de préparation (résolution DNS du service inaccessible) ; les tests automatisés utilisent des réponses simulées. La première installation devra vérifier l’accès effectif à Photon, le résultat local et l’entité de diagnostic.

Sources techniques : [Photon — API](https://github.com/komoot/photon/blob/master/docs/api-v1.md), [conditions du serveur public](https://github.com/komoot/photon#demo-server), [référentiel pycountry](https://pypi.org/project/pycountry/).

Les sections antérieures ci-dessous restent le cadrage et l’historique ; ce bilan v2 remplace leurs mentions de fournisseur international encore à choisir, de capteur non implémenté et de prototype FR comme seule réalisation.

## Capteur de diagnostic « Day Planner — Localisation »

**Choix validé par l’utilisateur le 9 novembre 2026 ; capteur à implémenter et à tester.** Identifiant proposé : `binary_sensor.day_planner_location`. Nom affiché : **Day Planner — Localisation**. Le nom et l’identifiant ne contiennent pas « holiday ». Le capteur décrit la localisation utilisée par Day Planner, pour le lieu de l’installation HA quel que soit le pays.

| État | Signification |
| --- | --- |
| Activé (`on` / vrai) | Pays et zone nécessaires à l’utilisation prévue déterminés et exploitables. Une subdivision n’est requise que lorsque les règles du territoire l’exigent. |
| Désactivé (`off` / faux) | Informations manquantes, ambiguës, incohérentes ou non prises en charge ; motif disponible dans les attributs. |
| Indisponible | Première évaluation non encore effectuée ou intégration déchargée. |

| Attribut | Contenu prévu |
| --- | --- |
| `integration` | `Day Planner`. |
| `last_evaluated` | Date et heure de la dernière évaluation, avec fuseau. |
| `country_code` / `country_name` | Code et nom du pays. |
| `subdivision_code` / `subdivision_name` | Code et nom de la région, province, canton ou autre subdivision pertinente. |
| `locality` | Commune ou localité, si disponible. |
| `source` | Fournisseur géographique utilisé. |
| `from_cache` | Booléen indiquant si le résultat utilisé provient du cache. |
| `resolved_at` | Date et heure de la résolution géographique utilisée, avec fuseau. |
| `status` / `reason` | État détaillé et motif explicatif lorsque nécessaire. |

`last_evaluated` et `resolved_at` sont distincts : une évaluation récente peut réutiliser une résolution plus ancienne conservée en cache. Ne pas inventer de pays, subdivision ou localité lorsque l’information manque.

Rattachement : **L7-01** pour les données géographiques et leur exposition ; **L7-03** pour les évaluations, le cache et l’actualisation ; **L7-07/L7-08** pour les contrôles et essais HA. Les huit sous-lots restent conservés, sans renumérotation.

Ce capteur ne répond pas à la question « aujourd’hui est-il férié ? ». Aucun second capteur n’est ajouté par cette validation. Cette décision a été mise en œuvre dans la reconstruction v2 décrite en tête ; les essais réels dans HA restent à effectuer.

## Portée corrigée du lot 7 — installation Home Assistant, tous pays

**Clarification explicite de l’utilisateur le 9 novembre 2026 : le lot 7 et ses sous-lots dépendent du lieu de l’installation HA et ne sont pas réservés à la France.** Cette décision remplace les limites France / Alsace-Moselle du cadrage initial. Les règles de création assistée, de modification, de cache et de protection du planning déjà retenues restent applicables.

| Sous-lot | Conséquence de la correction |
| --- | --- |
| L7-01 | Résoudre le pays et les subdivisions pertinentes depuis la configuration du domicile HA. Modèle géographique générique ; commune/département français ne sont plus des champs universellement obligatoires. Reprendre le fournisseur géographique et supprimer l’exclusion de principe des autres pays et territoires. |
| L7-02 | Choisir dynamiquement le pays et la subdivision compatibles avec la version installée de holidays. Les correspondances FR/57/6AE deviennent des exemples de règles locales, pas la configuration unique du moteur. |
| L7-03 | Identifier le cache par les coordonnées et le contexte pays/subdivision ; gérer aussi les changements de pays. Un support manquant doit correspondre à une limite réelle des sources, pas au simple fait d’être hors de France. |
| L7-04 | Afficher le pays et la subdivision effectivement déterminés ; aucun libellé de zone figé sur France/Alsace/Moselle. |
| L7-05 et L7-06 | Réutiliser le parcours d’exception pour toutes les installations : ajout, modification, suppression et description proposée depuis le nom du jour férié. Aucun réglage de lieu supplémentaire. |
| L7-07 et L7-08 | Tester plusieurs pays et subdivisions, leurs changements, les limites de couverture et les libellés ; conserver les cas nationaux et Alsace-Moselle comme exemples parmi d’autres. |

**Support et limites :** viser les pays et subdivisions disponibles dans les sources choisies et dans la version de holidays installée ; ne pas promettre une précision communale complète partout. Si une subdivision est nécessaire mais non déterminée, l’indiquer explicitement et ne pas présenter un calendrier national comme un calendrier régional complet. Une incohérence entre pays HA et résultat géographique doit être signalée, sans choix arbitraire. La langue et le fuseau horaire ne déterminent pas le territoire.

**État de réalisation :** le ZIP `day_planner_L7-01.zip` précédemment fourni reste un prototype FR et doit être repris. Ses 616 tests et sa couverture 100 % attestent uniquement ce prototype ; ils ne valident pas le fonctionnement international. Aucun nouveau code de résolution mondiale ni nouveau fournisseur n’est déclaré implémenté par cette correction documentaire. Le choix du service a été repris dans la reconstruction v2 décrite en tête : Photon ; sa vérification réelle dans HA reste à effectuer.

> **Ajout documentaire du 9 novembre 2026 :** cadrage L7-01 du lot 7 consigné en fin de document ; réalisation et validation restent à effectuer. Les états historiques ci-dessous conservent leur date de référence.

> **État au 8 novembre 2026.** Base de développement : Day Planner 0.2.3, avec les modifications locales de reprise eedomus **v5.16**. Ces numéros `v5.x` sont ceux des correctifs de travail, pas des versions publiées de l’intégration. Le dernier rapport pytest **complet communiqué** (7 novembre) donne **517 tests réussis, 2 990 instructions, 243 non couvertes, 92 % de couverture**. Un complément de **55 tests** a été préparé et validé de façon ciblée ; **le 100 % global reste à confirmer par la prochaine exécution complète**.


**Contexte historique : version 0.2.0, documentation initiale du 22 octobre 2026 : traçabilité des cinq objets métier et contrôles fonctionnels Home Assistant confirmés. Les travaux réalisés après la publication 0.2.0 ne constituent pas une nouvelle release.**

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

**Rapport historique complet chiffré du 21 octobre 2026 : 449 tests réussis, 2 146 instructions Python mesurées, 0 non couverte, 100 % de couverture, 5 avertissements, en 1,67 s sous Python 3.14.3.** L’utilisateur a confirmé les tests après les dernières adaptations et réalisé les contrôles fonctionnels en HA les 22 octobre : Moments et Actions, Types de journée et Moments planifiés, Semaines types, Cycles et Exceptions du calendrier. La suite complète n’a pas été relancée par l’assistant pour cette période historique ; un rapport plus récent du 7 novembre 2026 est indiqué dans la mise à jour du 8 novembre.

Le test réel du Journal de bord du 20 octobre confirme également l'attribution de la désactivation de `input_boolean.day_planner_test` à l'action `XX1` du moment `Retour Travail`.

La couverture est mesurée sans seuil bloquant. Elle ne garantit pas à elle seule le comportement réel de l'intégration et ne mesure pas la couverture du frontend JavaScript.

**L1-06 est clôturé le 22 octobre 2026** sur les sept scénarios fonctionnels HA confirmés : action sur deux helpers avec traces, deux moments simultanés, replanification après changement d’horaire, exception, changement de cycle, passage de minuit et redémarrage avant déclenchement. **L1-11 demeure à confirmer** pour un événement dont l’horaire est passé pendant un arrêt HA ; les tests Python décrivent le non-rattrapage général attendu. Aucun essai réel distinct de ce dernier cas n’est affirmé.

## 8. Reprise ponctuelle d’un agenda eedomus (v5.16)

Depuis **Paramètres → Appareils et services → Day Planner → Configurer → Reprise agenda eedomus**, sélectionner une box eedomus **active** puis un export JSON sur l’ordinateur. Si une seule box est active, sa sélection est automatique. Le formulaire affiche le résumé et les associations avant toute écriture.

- Les **semaines types, types de journée, moments, actions et identifiants Day Planner** portent la provenance lisible `Eedomus (<adresse de la box>)`. Les identifiants des entités existantes dans Home Assistant ne sont pas modifiés.
- Les commandes de domaines non compatibles (dont `sensor`) sont **identifiées comme ignorées**, mais les moments sont créés même s’ils ne possèdent aucune action compatible. Les horaires sont conservés.
- L’absence d’association ou une association ambiguë, notamment plusieurs cibles compatibles, interdit l’import plutôt que d’inventer la cible ; les entités de diagnostic `_battery` sont exclues de la recherche.
- Les **règles conditionnelles eedomus** et paramètres internes non interprétés ne sont pas convertis en actions Day Planner ; ils sont annoncés dans le récapitulatif.
- Une reprise précédente de la **même box** peut être remplacée après confirmation ; aucune création manuelle ni reprise d’une autre box ne doit être effacée.
- La reprise **ne crée ni cycle ni exception**, ne planifie pas automatiquement une semaine dans un cycle et ne commande aucun appareil au moment de l’import.
- Le JSON d’origine reste sur le poste ; la copie téléversée par le formulaire est temporaire.

**Rapports disponibles :** tableau des associations avec statut, zone de copie par sélection du texte, CSV et fichier **XLSX à 7 onglets**. Le fichier est constitué en mémoire, avant même la confirmation de création. Son téléchargement passe par un lien temporaire Home Assistant ; selon le frontend, la navigation des liens peut nécessiter une ouverture externe. Les fichiers ne sont pas stockés sous `/config`.

La référence de test de l’export du **1er novembre 2026 à 18:02** contient **9 types de journée, 8 moments, 41 horaires et 10 actions directes** lorsque les entités correspondantes sont compatibles. Ces chiffres ne sont pas des valeurs fixes : le résultat réel dépend du JSON et des entités actives.

Voir [le guide détaillé de reprise](reprise_eedomus.md) et [l’export Excel](export_xlsx_eedomus.md).

## 9. Validation de la reprise et couverture

Dernière mesure de suite complète fournie (7 novembre 2026) : **517 tests réussis, 92 %** (2 990 instructions, 243 non couvertes). Le complément préparé cible la couverture intégrale de l’extracteur et des cas limites d’import, d’export Excel et de flux d’options ; le résultat global de 100 % doit être confirmé par une nouvelle exécution avec Home Assistant. Les tests isolés ne valent pas recette de bout en bout.

## 10. Jours fériés régionaux — lot 7, cadrage L7-01

**Décision du 9 novembre 2026 : méthode retenue, à implémenter et à tester.** Cette section décrit une évolution prévue ; elle n’atteste pas sa disponibilité dans la version installée. L’ancienne référence de roadmap L3-14 est conservée comme historique ; le suivi détaillé relève désormais de L7-01 à L7-08.

### Localisation utilisée

Day Planner utilisera la localisation du domicile configurée dans Home Assistant, sans nouveau réglage de pays, région ou adresse dans Day Planner. La position du téléphone, du navigateur ou d’une personne ne sera pas utilisée.

Le pays et les subdivisions seront déterminés à partir du domicile configuré dans HA. La précision nécessaire dépend du pays et des règles de jours fériés. `geo.api.gouv.fr` n’est qu’une piste propre à la France ; le service géographique doit être repris pour couvrir le périmètre international corrigé ci-dessus.

### Connexion et actualisation

La détermination initiale du territoire nécessitera une connexion Internet et transmettra les coordonnées du domicile au service géographique public. Le résultat sera mémorisé pour éviter un appel à chaque affichage. Une modification de la localisation HA entraînera une nouvelle détermination du territoire.

Si la localisation est absente, ambiguë ou non résolue, Day Planner indiquera « Zone des jours fériés non déterminée ». Un résultat mémorisé ne sera réutilisable que s’il correspond toujours aux coordonnées actuelles. Le planning continuera de fonctionner et les exceptions déjà enregistrées seront conservées.

### Limite de cette étape

L7-01 détermine le territoire ; le choix de source et les règles retenues dans L7-02 sont décrits ci-dessous. L’affichage et la création assistée relèvent des sous-lots suivants : un jour férié affiché ne modifiera pas le programme. Une exception nécessitera le choix explicite d’un type de journée et l’enregistrement par l’utilisateur. Le parcours retenu dans L7-05 réutilise les commandes existantes et les complète par « Modifier », sans bouton spécifique aux jours fériés. Aucune création automatique en masse n’est retenue.

## 11. Jours fériés — source et règles retenues L7-02

**Validation utilisateur du 9 novembre 2026 : cadrage L7-02 retenu ; implémentation et tests restent à effectuer.** Le calcul des dates utilisera localement la bibliothèque Python `holidays`, déjà employée par l’intégration Holiday de Home Assistant. Le calcul ne nécessite pas de requête Internet ; la résolution géographique initiale de L7-01 reste dépendante du réseau.

**Exemples français parmi les correspondances internationales à prévoir :**

| Territoire résolu dans L7-01 | Calendrier à utiliser |
| --- | --- |
| Métropole hors Alsace-Moselle | France (`FR`), sans subdivision |
| Moselle, département 57 | France (`FR`), subdivision `57` |
| Bas-Rhin et Haut-Rhin, départements 67 et 68 | France (`FR`), subdivision Alsace `6AE` |

Les jours nationaux et le 26 décembre en Alsace-Moselle seront affichés. Les jours fériés tombant le week-end seront conservés. Le Vendredi saint sera accompagné de la mention **« application locale à vérifier »** lorsque la condition communale n’est pas établie ; le département seul ne suffit pas à confirmer cette condition. La règle légale vise les communes ayant un temple protestant ou une église mixte. Le choix utilisateur ne signifie pas que cette vérification communale est déjà automatisée.

Aucun affichage ne modifiera le programme ni ne créera d’exception automatiquement. Le choix explicite d’un type de journée et l’enregistrement de l’exception restent nécessaires. Les autres pays et territoires font partie de la cible, selon la couverture réelle des sources et de la version de holidays installée.

## 12. Gestion des données et cas non résolus — L7-03

**Cadrage L7-03 validé par l’utilisateur le 9 novembre 2026 ; implémentation et tests à effectuer.**

| Situation | Comportement retenu |
| --- | --- |
| Premier démarrage | Résoudre la commune et le département depuis la localisation HA, puis enregistrer le résultat. |
| Redémarrage HA | Réutiliser le résultat enregistré si les coordonnées correspondent toujours. |
| Changement de localisation | Invalider l’ancienne zone et relancer la résolution ; ignorer toute réponse encore en cours pour l’ancien lieu. |
| Échec réseau avec cache correspondant | Conserver la zone connue et prévoir des tentatives ultérieures espacées. |
| Échec sans cache utilisable | Afficher « Zone des jours fériés non déterminée », sans bloquer le planning. |
| Localisation absente ou ambiguë | Ne pas choisir arbitrairement une zone ni ajouter de réglage de lieu dans Day Planner. |
| Pays ou subdivision non couverts par les sources | Indiquer la limite réelle de support, sans exclusion systématique des pays autres que la France. |
| Changement d’année | Calculer localement les nouvelles dates sans nouvelle recherche géographique du seul fait de ce changement. |

Les dates seront calculées pour l’année affichée dans le calendrier, y compris lors de la consultation d’une année précédente ou suivante. Le cache géographique sera persistant et séparé des objets de planning ; il conservera les coordonnées sources et la date de résolution.

**Points encore ouverts :** durée de validité du cache, éventuel renouvellement périodique et délais précis entre les nouvelles tentatives. Aucun délai chiffré n’est arrêté par ce cadrage.

**Les exceptions déjà enregistrées resteront inchangées**, même après un changement de domicile ou une actualisation des jours fériés. Ces règles ne créent aucune exception et ne déclenchent aucune action.

## 13. Affichage des jours fériés — L7-04

**Cadrage L7-04 validé par l’utilisateur le 9 novembre 2026 ; affichage à implémenter et à tester.**

| Élément | Présentation retenue |
| --- | --- |
| Jour férié | Repère avec une icône et son nom, par exemple Noël. |
| Journée programmée | Type de journée visible avec ses informations habituelles. |
| Exception existante | Exception identifiable et prioritaire pour le programme appliqué ; repère férié visible à côté. |
| Détails | Nom complet et portée nationale ou locale, accessibles au survol, au clavier et sur mobile. |
| Vendredi saint | Mention « Application locale à vérifier » lorsque la condition communale n’est pas établie. |
| Zone utilisée | Pays et subdivision réellement déterminés au-dessus du calendrier ; libellés dynamiques adaptés au lieu HA. France, Alsace et Moselle sont des exemples. |
| Zone non déterminée | Message au-dessus du calendrier, sans gêner la consultation du planning. |

Le repère utilisera une icône et un libellé afin de ne pas dépendre uniquement de la couleur. Sur mobile, le nom pourra être abrégé visuellement avec accès au texte complet.

L’affichage restera informatif : il ne modifiera pas le type de journée et ne créera aucune exception. L7-04 portait sur l’affichage. Le cadrage L7-05 ci-dessous retient ensuite le parcours d’exception existant, complété par « Modifier », sans bouton spécifique aux jours fériés.

## 14. Gestion des exceptions — L7-05

**L7-05 implémenté et testé le 11 novembre 2026 ; recette IHM HA à effectuer.** La commande « Modifier » était déjà présente et est conservée. L’ajout propose désormais les noms des fêtes dans la description ; aucun bouton propre aux jours fériés n’est ajouté.

| État du jour sélectionné | Actions concernées par ce cadrage |
| --- | --- |
| Sans exception | Ajouter une exception avec la commande actuelle. |
| Avec une exception | Modifier et Supprimer ; conserver la suppression actuelle. |

« Modifier » ouvrira le formulaire prérempli avec le type de journée et la description enregistrés, en conservant la date sélectionnée. Il s’agit de modifier l’exception existante, sans en créer une seconde. Les autres commandes déjà validées ne sont pas retirées par ce cadrage.

Pour l’ajout sur une date fériée, préremplir la date sélectionnée et proposer une description modifiable, par exemple « Jour férié : Noël ». Le type de journée restera à choisir explicitement. Lors d’une modification, conserver la description existante ; ne pas la remplacer automatiquement par le nom du jour férié.

La réserve « Application locale à vérifier » du Vendredi saint restera présentée dans les informations du jour lorsque nécessaire. L’ouverture du formulaire ne provoquera aucune écriture ; l’enregistrement nécessitera la validation de l’utilisateur et une annulation restera sans modification. Les validations détaillées et le comportement d’enregistrement retenus dans L7-06 sont décrits ci-dessous.

## 15. Formulaire et enregistrement — L7-06

**L7-06 implémenté et testé automatiquement le 11 novembre 2026 ; recette IHM HA à effectuer.**

| Élément | Ajout | Modification |
| --- | --- | --- |
| Date | Préremplie avec le jour sélectionné. | Date de l’exception conservée. |
| Type de journée | Choix obligatoire. | Valeur actuelle préremplie et modifiable. |
| Description | Proposition modifiable si jour férié ; vide sinon. | Description enregistrée conservée et modifiable. |

La description reste facultative, y compris pour un jour férié. La proposition de description à la création peut être effacée ; elle ne doit pas être réinjectée automatiquement après une erreur.

### Validation et enregistrement

- Vérifier que le type de journée choisi existe toujours.
- Refuser une création si une exception existe déjà à cette date, sans l’écraser.
- Modifier l’exception existante en conservant son identité et ses métadonnées de création ; actualiser les métadonnées de modification selon les règles actuelles du projet.
- Empêcher les doubles enregistrements pendant la requête.
- Après réussite, actualiser le calendrier et le planning.

En cas d’erreur, conserver toutes les saisies dans leurs champs et afficher le message dans le formulaire. Annuler ou fermer avec Échap ne provoquera aucune écriture.

La suppression conserve son parcours actuel. Le caractère férié reste informatif : seule l’exception enregistrée change le programme de la journée.

## 16. Plan de tests et qualité — L7-07

**Plan L7-07 exécuté le 11 novembre 2026 : 704 tests pytest, 26 tests JavaScript, couverture Python 100 %.** Les essais réels finaux restent suivis séparément sous L7-08.

| Bloc | Contrôles prévus |
| --- | --- |
| Localisation | Pays et subdivisions correctement résolus dans plusieurs pays, réponse absente ou ambiguë, coordonnées invalides, incohérence de pays et limites réelles de support. |
| Cache et réseau | Réutilisation après redémarrage, changement de lieu, réponse devenue obsolète, panne réseau avec ou sans cache. |
| Jours fériés | Plusieurs pays et subdivisions pris en charge ; dates fixes et mobiles, jours observés selon les règles locales, week-ends et réserves locales. Conserver les cas français et Alsace-Moselle. |
| Changement d’année | Calcul de l’année consultée, passage à janvier, absence de recherche géographique inutile. |
| Exceptions | Ajout, modification, suppression, description vide, refus des doublons, conservation de l’identité et de l’audit de création. |
| Formulaire | Saisies conservées après erreur, correction puis enregistrement, double clic, Annuler et Échap. |
| Planning | Aucun changement dû au seul affichage férié ; application d’une exception enregistrée et retour au cycle après suppression. |

Les tests Python seront intégrés de préférence aux modules existants de `scripts/tests/`. Les réponses réseau seront simulées pour que la suite ne dépende pas du service géographique.

Après les contrôles ciblés : suite complète, mesure de couverture avec objectif de 100 % sans seuil bloquant, contrôle syntaxique du frontend et vérifications de qualité du dépôt. Les essais réels dans Home Assistant sur ordinateur et mobile seront suivis séparément sous L7-08.

## 17. Essais réels HA et documentation finale — L7-08

**Plan d’essais L7-08 validé par l’utilisateur le 9 novembre 2026 ; essais réels non encore réalisés.** Ces essais seront effectués après implémentation et contrôles du lot 7.

| Essai réel dans Home Assistant | Résultat attendu |
| --- | --- |
| Calendrier sur ordinateur et mobile | Jours fériés lisibles, type de journée et exceptions toujours visibles. |
| Clavier et détails | Navigation possible et accès au nom complet, à la portée et aux réserves locales. |
| Ajouter une exception | Date préremplie, description proposée modifiable, type de journée à choisir. |
| Modifier une exception | Valeurs enregistrées préremplies, date conservée, modification correctement appliquée. |
| Annuler ou fermer avec Échap | Aucune modification enregistrée. |
| Supprimer une exception | Retour au programme du cycle ; repère férié toujours présent. |
| Redémarrer HA | Zone mémorisée réutilisée et exceptions conservées. |
| Réseau indisponible ou changement de lieu | Comportements conformes à L7-03, sans blocage du planning. |
| Consulter une autre année | Dates recalculées correctement pour l’année affichée. |

Les essais nécessitant un changement de localisation ou une simulation de panne seront réalisés sur une instance de test.

Pour chaque contrôle, conserver la version testée, le résultat et les éventuelles anomalies. Les documentations fonctionnelle et technique seront ensuite ajustées au comportement réellement livré, avec ses limites.

Le lot 7 sera clôturé après réussite des contrôles L7-07 et validation des essais L7-08. La validation de ce plan termine le cadrage des huit sous-lots ; elle ne clôture pas leur réalisation et n’atteste aucune nouvelle publication. Les points techniques encore ouverts, dont la durée de validité du cache et son éventuel renouvellement périodique, restent à préciser avant les modifications concernées.

### Première implémentation L7-01 préparée le 9 novembre 2026

Base : dépôt `fmo01/hass-day_planner`, branche `main`, commit `0562541cbd339041d46aeb8267971630f32a1f0c` (version publiée 0.3.1). Modifications locales préparées ; aucune publication ni installation HA réelle de ce correctif n’est affirmée.

Le nouveau module `holiday_location.py` lit le pays et les coordonnées courants du domicile HA et interroge `geo.api.gouv.fr` avec la session HTTP partagée et un délai maximal de 10 secondes. Il accepte une commune unique et valide son nom, son code INSEE et son département. Il distingue les états résolu, non résolu et territoire non pris en charge. Les coordonnées invalides, réponses ambiguës ou mal formées, erreurs HTTP/réseau et annulations sont contrôlées. La résolution du territoire ne calcule pas encore les dates fériées.

Le résolveur est disponible dans les données d’exécution (`runtime_data.holiday_location`). Cette première étape ne lance pas de requête au chargement : l’appel sera raccordé au cycle de vie sous L7-03. Cache persistant, reprises et détection automatique des changements de lieu restent à implémenter dans L7-03 ; calcul des dates sous L7-02 et affichage sous L7-04 également à réaliser. Aucun repère férié n’est encore visible dans le calendrier et aucune exception n’est modifiée par ce code.

**Vérifications exécutées :** 44 nouveaux cas intégrés à `scripts/tests/test_runtime.py`, plus contrôle du raccordement dans `test_init.py` ; suite complète **616 tests réussis**, **3 058 instructions couvertes sur 3 058 (100 %)**, **5 avertissements de dépendances**, en **2,06 s**, avec **Python 3.14.9 et Home Assistant 2026.10.4**. Aucun appel géographique réel dans les tests. Contrôles Black, isort profil black et flake8 (120 caractères) sur les fichiers modifiés réussis. Les statistiques de `scripts/tests/README.md` sont régénérées par le code du workflow existant ; le mécanisme automatique GitHub Actions est conservé. Ces résultats ne constituent pas la recette HA L7-08.
