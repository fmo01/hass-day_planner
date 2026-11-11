# Day Planner — Roadmap et suivi d’avancement

## L7-08 — Validation finale et clôture du lot 7 (11 novembre 2026)

**Lot 7 clôturé et validé fonctionnellement sur l’installation de l’utilisateur.** Après validation de L7-01 à L7-06, l’utilisateur a confirmé L7-07 (« Validé »), puis la recette finale (« j’ai testé ok »). Cette clôture documentaire consigne son retour ; elle ne constitue pas une nouvelle exécution de tests ni une nouvelle publication.

La validation HA est un retour global de l’utilisateur. Aucun relevé détaillé supplémentaire par pays, navigateur, appareil ou scénario de panne n’a été fourni lors de cette confirmation ; ces détails ne sont pas inventés. Les résultats automatisés et les limites de couverture géographique restent distincts de la recette réelle.

Bilan de référence L7-07 : **704 tests pytest réussis**, dont un lanceur de **26 tests JavaScript réussis**, **100 % de couverture Python (3 407 instructions)** et cinq avertissements de dépendances. Black, isort, flake8, syntaxe JavaScript et lecture des JSON ont été vérifiés ; Ruff n’a pas été exécuté dans l’environnement local. Le pourcentage de couverture concerne exclusivement le Python.

Le périmètre livré comprend la localisation issue de HA avec Photon/OpenStreetMap, le capteur de diagnostic, la persistance de la dernière localisation résolue dans `/config/.storage/day_planner_location`, le calcul local des fêtes selon le pays et les subdivisions pris en charge, leur affichage informatif et la création assistée d’exceptions. La consultation d’un jour férié ne modifie jamais le planning : seule une exception enregistrée le fait. Le cache reste conservé, avec une validité de 30 jours et une reprise après une heure en cas d’échec réseau/HTTP, selon L7-03.

Référence frontend de la livraison validée : carte **0.2.12**, `utils.js` **0.1.1**, `i18n.js` **0.1.1**. Cette livraison L7-08 modifie uniquement la roadmap et les documentations. Aucun fichier de production, aucune version d’intégration et aucune publication GitHub/HACS ne sont modifiés. Les autres lots, notamment l’étude mypy, conservent leur suivi propre.

Les sections datées de cadrage et les résultats intermédiaires sont conservés pour la traçabilité. Le présent bilan et le tableau de suivi actualisé font référence pour le statut final ; les formulations anciennes « à réaliser » décrivent l’état à leur date.

## L7-07 — Qualification automatisée transversale (11 novembre 2026)

L7-06 est validé sur HA par l’utilisateur. L7-07 complète les tests existants et les contrôles de qualité. Aucun code de production n’est modifié : carte 0.2.12, utils.js et i18n.js 0.1.1 inchangés. L7-08 a ensuite été validé par l’utilisateur ; le lot 7 est clôturé.

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

**Mise à jour : 9 novembre 2026. Version de référence publiée : Day Planner 0.3.1 (release GitHub datée du 8/11/2026), installée sur Home Assistant de production selon confirmation utilisateur du 9/11. La 0.3.0 (8/11) a livré la reprise ponctuelle des agendas eedomus et l’export XLSX ; la 0.3.1 corrige la conformité HACS. L6-08 terminé pour la préparation/publication. L6-10 clôturé le 09/11 : l’utilisateur confirme les contrôles fonctionnels en production, la reprise eedomus et l’export XLSX. Dernier résultat Python local communiqué le 8/11 : 572 tests réussis, 2 990 instructions couvertes sur 2 990 (100 %), 5 avertissements de dépendances, Python 3.14.3 ; Black, isort profil black et flake8 conformes. Les essais d’installation/mise à jour/retrait sur HAOS de test (L6-07) et les décisions de report antérieures restent conservés. Ce document met à jour le suivi, sans créer de nouvelle publication.**

La roadmap conserve les **six lots de la première version** et ajoute un **lot 7 dédié aux jours fériés régionaux et à la création assistée d’exceptions**, découpé en sous-lots suivis séparément. Les sept étapes de finalisation des vues sont rattachées aux lots concernés, avec leurs statuts conservés. Les numéros des lots sont des repères stables ; les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Les sept essais fonctionnels prévus pour L1-06 sont validés le 22 octobre ; L3-06 est clôturé le 23 octobre après validation des contrôles d’erreurs et d’annulation ; L3-07 est clôturé le 24 octobre après les validations sur ordinateur et mobile. L3-08 a été qualifié le 24 octobre : chargement des fichiers frontend avec rechargement simple après mise à jour/redémarrage et droits CRUD des non-administrateurs constatés. La délégation fine des droits reste volontairement reportée à L3-12. L1-11 a été validé en conditions réelles le 26 octobre ; L3-10 est terminé le 28 octobre : Moments validés le 27 octobre (Enregistrer et Annuler) ; Actions validées en HA pour les essais 4 et 5 ; Types de journée, Semaines types, Cycles et Exceptions validés. Duplication des Moments planifiés retirée le 27 octobre (la création standard reste disponible). Les essais HA n’impliquent pas une nouvelle exécution complète des tests Python. L6-03 est validé le 29 octobre : 12 fichiers JS et 2 JSON syntaxiquement valides, contrôle de navigation, amélioration Types de journée (tri, compteurs, dépendances, i18n FR/EN), puis affichage des détails au survol validé.

Les statuts des vues proviennent des essais HA confirmés par l’utilisateur jusqu’au 19 octobre. Les constats techniques combinent la relecture historique du ZIP et celle des 14 fichiers frontend actualisés, puis du dernier day-planner-card.js du 19 octobre. La vérification finale des six corrections est une relecture du code et un contrôle syntaxique ; les simulations de doubles appels ont été effectuées sur la version précédente. Les versions cibles restent indicatives, sans date de publication engagée.

## 1. Principes

- Un seul profil et une seule configuration Day Planner.
- Horaires définis dans les types de journée ; actions associées aux moments.
- Exceptions gérées depuis le calendrier.
- Logique métier séparée des interfaces Home Assistant.
- Nouveaux tests ajoutés de préférence dans les fichiers existants correspondant aux modules concernés.
- Moments considérés comme terminés et figés : une modification nécessite un défaut identifié ou une dépendance concrète d'un autre bloc.
- Couverture mesurée et suivie, avec un objectif de 100 %, sans seuil bloquant dans les commandes ni dans la CI.

### Priorité de l'i18n

**L'i18n n'est pas prioritaire et ne bloque pas la validation des blocs.** Lorsqu'un fichier ou un dialogue doit être retouché pour une raison fonctionnelle, son i18n peut être traitée à cette occasion. Les traductions existantes sont conservées.

Les mentions d'i18n dans les blocs suivants décrivent donc des ajustements opportunistes, pas une campagne de traduction dédiée. Les libellés encore en français en dur seront recensés lors du passage transversal ; leur traduction n'impose pas de rouvrir les moments figés.

## 2. État du socle

### Présent dans la version relue

- Gestion des moments, actions, types de journée, moments planifiés, semaines types, cycles et exceptions.
- Résolution du planning, calcul des événements, planification Home Assistant et exécution des actions.
- Stockage persistant, trois capteurs et un calendrier Home Assistant.
- Panneau de gestion, carte Lovelace, services et API WebSocket.
- Horaires fixes.

### Corrections intégrées depuis la première relecture

- Couverture ciblant `custom_components/day_planner`.
- Suppression des anciennes vérifications de fichiers eedomus dans le workflow de tests.
- Échec de pytest désormais transmis à la CI.
- Dépendances de test et de couverture ajoutées.
- Assertions des capteurs et du calendrier utilisant `INTEGRATION_VERSION`.
- Tableau de couverture distinguant package et composant.
- README des tests en français, guides et roadmap intégrés au dépôt.

**Dernier rapport complet chiffré communiqué par l’utilisateur le 29 octobre 2026 : 449 tests réussis, 2 154 instructions mesurées, 0 non couverte, 100 % de couverture Python, 5 avertissements, 2,26 s, Python 3.14.3.** Ce nouveau résultat suit la mise en forme Black/isort et les vérifications flake8. **Résultat historique du 21 octobre 2026 conservé :** 449 tests, 2 146 instructions mesurées, 0 non couverte, 100 %, 5 avertissements, 1,67 s. Le 20 octobre, le retour à 100 % après compléments `action_executor.py` et `logbook.py` avait déjà été confirmé. **Résultat historique du 14 octobre :** 407 tests réussis, 1 908 instructions mesurées, aucune non couverte, 100 % de couverture Python, 5 avertissements, 1,22 s, Python 3.14.3. Ces résultats ne sont pas des exécutions de la suite complète par l'assistant. Aucun seuil bloquant de couverture n'est souhaité.

**Résultat historique du 13 octobre :** le README des tests annonce **394 tests réussis, 1 877 lignes mesurées et 100 % de couverture**, au **13 octobre 2026 à 15:28:05 Europe/Paris**. La relecture a vérifié la cohérence de ce tableau et les générateurs de rapports avec des données synthétiques ; elle n'a pas réexécuté la suite complète.

## 3. Vue d’ensemble des lots

| Lot | Intitulé | Version cible indicative | Avancement actuel |
| --- | --- | --- | --- |
| 1 | Stabiliser le socle | Corrections livrées en 0.2.0 | Corrections fonctionnelles, workflow et versions/changelog terminés ; L1-06 validé le 22/10 et L1-11 validé le 26/10 après arrêt couvrant un événement. |
| 2 | Intégrer les Metadata / `Audit` | À définir après 0.2.0 | Modèles, moteur, persistance et trois interfaces validés ; présentation détaillée des métadonnées dans l’interface restant à qualifier. |
| 3 | Simplifier la gestion quotidienne | 0.3.1 publiée | En cours ; les cinq vues sont validées. Formulaires (L3-06), clavier/mobile (L3-07) validés ; L3-08 qualifié (cache OK, permissions existantes constatées). Attribution fine des droits reportée (L3-12). Duplication (L3-10) terminée le 28/10 : six familles validées en HA ; bouton Dupliquer des Moments planifiés retiré sur décision du 27/10. L6-03 validé le 29/10 ; L6-04 validé le 29/10 (lint, HACS, hassfest et tests CI). L6-07 validé le 30/10 (quatre scénarios) ; L6-08 publié en 0.3.1 le 8/11, installation en production confirmée le 9/11 ; L6-10 validé en production le 9/11, reprise eedomus et export XLSX compris. |
| 4 | Ajouter les horaires avancés | 0.4.0 | À planifier ; périmètre à préciser. |
| 5 | Ajouter une source de calendrier externe | 0.5.0 | À planifier ; règles de synchronisation à définir. |
| 6 | Qualifier la première version stable | 1.0.0 | À préparer après consolidation du périmètre retenu. |
| 7 | Jours fériés régionaux et création assistée d’exceptions | Clôturé — validé sur HA | L7-01 à L7-08 validés ; 704 pytest, 26 JS et 100 % Python. Clôture documentaire le 11/11/2026, sans nouvelle publication. |
| 8 | Typage progressif avec mypy | À définir | Étude initiale terminée. Corrections fichier par fichier à planifier, puis décision sur l’intégration à la CI. |


Les lots 4 et 5 peuvent être inversés selon les besoins. La 1.0 peut être qualifiée avec calendrier interne et horaires fixes, sans attendre ces extensions.

## 4. Tableau permanent de suivi d’avancement

**Ce tableau est conservé et mis à jour au fil du projet, sans suppression de lignes.** Les identifiants sont stables et ne sont jamais réutilisés. Une tâche terminée reste visible. Les nouvelles tâches sont ajoutées avec un nouvel identifiant.

Les colonnes statut, reste à faire, preuve et date peuvent être actualisées. Une tâche abandonnée passe à « Abandonné », une tâche reportée à « Reporté » ; la raison est conservée. Un changement de périmètre est consigné dans le journal en fin de document. Aucun pourcentage n'est déduit des lignes : les tâches n'ont pas toutes la même taille.

Statuts : **Terminé**, **Terminé et figé**, **Presque terminé**, **En cours**, **À faire**, **À planifier**, **À confirmer**, **Reporté**, **Abandonné**. « Terminé » décrit une tâche précise ; il ne signifie pas que tout le lot est validé.

| ID | Lot | Tâche / périmètre | Statut | Reste à faire / prochaine action | Preuve / origine du statut | Mise à jour |
| --- | --- | --- | --- | --- | --- | --- |
| L1-01 | 1 | Ciblage Day Planner et transmission des échecs pytest | Terminé | Conserver lors des prochaines adaptations. | Workflow relu. | 13/10/2026 |
| L1-02 | 1 | Dépendances de tests et couverture | Terminé | Suivre leur compatibilité. | requirements-dev.txt relu. | 13/10/2026 |
| L1-03 | 1 | Assertions de version et tableau par package | Terminé | Conserver la génération automatique. | Tests relus ; générateurs vérifiés avec XML synthétiques. | 13/10/2026 |
| L1-04 | 1 | Références des sept jours des semaines types | Terminé | Maintenir les contrôles et tests des sept jours ; L3-03 est maintenant clôturé. | Validation métier du 14/10 ; essais HA des semaines types confirmés par l’utilisateur. | 19/10/2026 |
| L1-05 | 1 | Moments simultanés | Terminé | Maintenir les tests de non-régression dans les fichiers existants. | Deux nouveaux tests réussis ; 29 tests des planificateurs passés, puis suite complète de 403 tests réussie, selon les résultats utilisateur. | 14/10/2026 |
| L1-06 | 1 | Transitions temporelles et rechargement | Terminé | Conserver les validations et tests de non-régression. L’essai distinct après arrêt est validé dans L1-11. | 22/10, sept scénarios HA confirmés successivement par l’utilisateur : action sur deux helpers (logs et événements), deux moments distincts simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement. Contrôles Python minuit/DST antérieurs conservés. | 22/10/2026 |
| L1-07 | 1 | Filtres et présentation du workflow | Terminé | Conserver les rapports et la mise à jour automatique du README, sans seuil bloquant. | Exécution tests.yml réussie confirmée par l'utilisateur ; README généré le 14/10 à 12:15:34 : 407 tests, 1 908 instructions, 100 %. | 14/10/2026 |
| L1-08 | 1 | Seuil de couverture imposé en CI | Abandonné | Ne pas ajouter de seuil bloquant ; conserver la mesure et les rapports de couverture. | Décision explicite de l'utilisateur le 14/10 : refus de --cov-fail-under=100. L'objectif de couverture reste suivi. | 14/10/2026 |
| L1-09 | 1 | Versions et changelog | Terminé | Maintenir le manifeste comme référence ; laisser semantic-release gérer les prochaines versions. | Utilisateur : L1-09 terminé. Manifeste 0.2.0 ; ancienne constante supprimée ; entrée 0.1.0 du 10/10 restaurée d'après le tag et doublons retirés. | 14/10/2026 |
| L1-10 | 1 | Journalisation et attribution des actions Day Planner | Terminé (fonctionnement validé) | Conserver les tests de non-régression et contrôler les cas d’intégrations tierces à exécution différée. | 20/10 : deux activités Logbook observées ; `input_boolean.day_planner_test` désactivé avec cause « Day Planner — action XX1 test (id : XX1) ». Journaux DEBUG/INFO/WARNING/ERROR, cibles manquantes et contexte commun couverts par les tests. | 20/10/2026 |
| L1-11 | 1 | Non-rattrapage après arrêt couvrant un événement | Terminé | Maintenir ce comportement et les tests de non-régression. | Test HA réel confirmé le 26/10/2026 : arrêt avant un événement, redémarrage après l’horaire, aucune exécution rétroactive ; reprise de la programmation future. Distinct du redémarrage avant événement validé sous L1-06. | 26/10/2026 |
| L2-01 | 2 | Modèle Metadata et règles auteur/horodatage | Terminé | Conserver le modèle `Audit` et ses règles ; aucune substitution de classe requise. | 21–22/10 : `Audit` intégré aux cinq objets, dates UTC/ISO, création et modification centralisées dans `PlannerEngine`, anciens objets acceptés sans migration ; tests utilisateur confirmés. | 22/10/2026 |
| L2-02 | 2 | Persistance, migration et interfaces Metadata | En cours | Persistance et trois interfaces validées ; qualifier l’affichage explicite de l’audit dans le panneau / les options. **Aucune migration des anciennes données n’est prévue** dans ce chantier. | 21–22/10 : sérialisation conditionnelle et mutations WebSocket, Services et Options Flow adaptées ; tests Python et essais HA validés. | 22/10/2026 |
| L2-03 | 2 | Validation fonctionnelle de la traçabilité des cinq objets | Terminé | Maintenir les tests et contrôles après modification du moteur ou du frontend. | 22/10 : utilisateur confirme successivement Moments/Actions, Types de journée/Moments planifiés, Semaines types, Cycles et Exceptions ; champs d’audit vérifiés après création et modification. | 22/10/2026 |
| L3-01 | 3 | Moments | Terminé et figé | Maintenir les tests de non-régression. | Statut utilisateur : CRUD, groupes d'actions, détails, traduction HA, i18n, comptages, erreurs. | 13/10/2026 |
| L3-02 | 3 | Types de journée | Terminé | Maintenir les comportements validés ; aucun nouveau travail fonctionnel prévu sur cette vue. | Essais utilisateur HA : CRUD, dépendances et conservation des saisies de création, renommage et moments planifiés. Boutons et gardes relus. | 19/10/2026 |
| L3-03 | 3 | Semaines types | Terminé | Maintenir les sept affectations, la conservation des saisies et les messages dans les dialogues. | Quatre essais HA confirmés : création invalide, modification invalide, CRUD et suppression refusée si utilisée par un cycle ; visibilité des erreurs validée. | 19/10/2026 |
| L3-04 | 3 | Cycles | Terminé | Maintenir le CRUD, les brouillons, les messages i18n et les protections relues ; comportement temporel réel suivi dans L1-06. | Essais HA des cycles tous confirmés le 18/10 ; corrections complémentaires de robustesse relues le 19/10 dans le dernier fichier syntaxiquement valide. | 19/10/2026 |
| L3-05 | 3 | Calendrier / Exceptions | Terminé | Maintenir le remplacement du programme par une exception et le retour au cycle après suppression ; L1-06 reste distinct. | Tous les essais HA confirmés le 19/10 : CRUD, description facultative vide, conservation des saisies, type appliqué et retour au programme après suppression. | 19/10/2026 |
| L3-06 | 3 | Cohérence transversale des modales et messages | Terminé | Maintenir les contrôles de non-régression ; toute nouvelle fenêtre doit respecter les comportements validés. Aucun contrôle de fermeture par croix : les fenêtres testées ne disposent pas de croix. | 22–23/10 : utilisateur confirme message explicite au dépassement de la limite des cycles, conservation des saisies après erreur, correction puis enregistrement, annulation sans mutation et absence de croix. Corrections JS relues le 19/10 ; aucun test supplémentaire inventé. | 23/10/2026 |
| L3-07 | 3 | Nettoyage CSS/JS, accessibilité et responsive | Terminé (contrôles convenus) | Maintenir la navigation au clavier et le rendu mobile lors des évolutions ; les travaux généraux de rationalisation CSS/JS, si nécessaires, restent transversaux et ne rouvrent pas la validation acquise. | 23/10 : après les correctifs L3-07 v2/v3, utilisateur confirme le retour des clics et saisies, le focus initial dans le premier champ, la navigation clavier correcte et la gestion du fond. 24/10 : essai réel sur mobile validé et fermeture par Échap confirmée. Fonctionnement constaté dans HA ; aucune nouvelle exécution complète des tests automatisés n’est impliquée. | 24/10/2026 |
| L3-08 | 3 | Cache/versioning frontend et permissions actuelles | Terminé (contrôles convenus) | Maintenir le comportement constaté jusqu’à la définition des droits fins en L3-12. | 24/10 : après mise à jour et redémarrage, simple rechargement suffisant (pas de Ctrl+Maj+R) ; compte non-administrateur testé : consultation, ajout, modification et suppression possibles. | 24/10/2026 |
| L3-09 | 3 | i18n restante | Reporté | Traiter opportunément lorsqu'un composant est retouché ; ne bloque pas un lot. | Priorité utilisateur. | 13/10/2026 |
| L3-10 | 3 | Dupliquer les six familles retenues en complément de modifier/supprimer (Moments planifiés exclus sur décision) | **Terminé** | Maintenir les six duplications validées et les comportements Annuler/erreurs ; non-régression frontend à poursuivre sous L6-03 et vérification des droits/audits selon les règles existantes. | 27/10 : **duplication d’un Moment validée dans HA, y compris Enregistrer et Annuler**. 27/10 : **duplication d’une Action confirmée en HA** : test 4 Enregistrer OK, test 5 Annuler OK. 27/10 : **Types de journée confirmés dans HA (tous les essais convenus OK)** : copie des affectations et horaires, annulation. **Moments planifiés : décision utilisateur du 27/10, bouton Dupliquer retiré de la timeline et de la fenêtre d’édition.** Le test dans HA a confirmé que le bouton ouvrait un simple formulaire d’ajout d’un autre Moment, peu pertinent comme duplication ; annulation complète du patch de cette fonctionnalité. Ajouter/Modifier/Supprimer restent disponibles. 28/10 : **Semaines types validées dans HA (tous les essais demandés OK)** ; duplication des Cycles validée en HA (test OK signalé par l’utilisateur). 28/10 : duplication des Exceptions validée en HA (tous les tests convenus OK), après les Cycles. Les six familles retenues sont donc validées ; aucune nouvelle exécution Python ni publication n’est déduite de ces essais. | 28/10/2026 |
| L3-11 | 3 | Ajout guidé des moments prédéfinis | À planifier | Conserver comme amélioration future indépendante de L3-10 ; en préciser le parcours après consolidation. | Sous-sujet préexistant à L3-10, conservé lors de sa scission le 22/10/2026. | 22/10/2026 |
| L3-13 | 3 | Reprise ponctuelle des agendas eedomus | **Livré et validé en production avec 0.3.1** | Maintenir la reprise à la demande via Options Flow, l’aperçu des associations et l’export XLSX ; surveiller les anomalies en production. Pas de synchronisation récurrente implicite. Les enrichissements futurs du classeur XLSX restent reportés. | 8/11 : publication GitHub 0.3.0 (commit fonctionnel `feat(eedomus)`), comprenant la reprise et l’export XLSX. Avant publication, tests locaux incluant le nouveau code : 572 réussis, 100 %. **09/11 : utilisateur confirme le fonctionnement en production de la reprise eedomus et de l’export XLSX sur 0.3.1.** | 09/11/2026 |
| L3-12 | 3 | Gestion déléguée des droits (gestionnaires/lecteurs) | Reporté | Réexaminer après finalisation des autres fonctionnalités : délégation par utilisateur, droit de modifier les actions HA, protection API/WebSocket et services. | Étude d’impact du 24/10, décision utilisateur le même jour de reporter l’évolution sans changer les droits actuels. | 24/10/2026 |
| L3-14 | 3 | Jours fériés régionaux et création assistée d’exceptions (niveau B) — référence historique | Reporté vers le lot 7 | Poursuivre dans L7-01 à L7-08 ; ligne et identifiant conservés, sans double suivi opérationnel. | 09/11 : cadrage initial conservé ; demande utilisateur de créer un lot 7 dédié pour détailler les sous-lots. Aucune mise en œuvre validée. | 09/11/2026 |
| L4-01 | 4 | Horaires avancés | À planifier | Définir règles, indisponibilités, passages de date et compatibilité. | Évolution conservée. | 13/10/2026 |
| L5-01 | 5 | Source de calendrier externe | À planifier | Définir source, correspondances, priorités et synchronisation. | Évolution conservée. | 13/10/2026 |
| L6-01 | 6 | Résultat de couverture de référence | Terminé | Actualiser après chaque exécution pertinente ; conserver les résultats précédents. | **08/11 : 572 tests réussis, 2 990 instructions, 0 non couverte, 100 %, 5 avertissements en 2,09 s, Python 3.14.3**, avec les modules de reprise eedomus. Historique 29/10 : 449 tests, 2 154 instructions, 100 % ; résultats antérieurs conservés au journal. | 08/11/2026 |
| L6-02 | 6 | Validation backend et WebSocket/API après corrections | Terminé (suite locale) | Relancer en cas de nouveau changement ; distinguer exécution locale et workflow de la publication. | 08/11 : 572 tests Python réussis, 100 % de couverture après changements eedomus ; Black/isort/flake8 conformes. Les validations temporelles précédentes restent acquises. Résultat historique du 29/10 : 449 tests, 100 %. | 08/11/2026 |
| L6-03 | 6 | Tests ciblés frontend et essais visuels | **Terminé (contrôles convenus)** | Maintenir les régressions testées et réexaminer si de nouvelles modifications frontend interviennent. Ne pas assimiler les essais HA à une exécution complète des tests Python. | 28/10 : 12 JS et 2 JSON vérifiés sans erreur ; navigation des cinq vues et refus de suppression métier constatés. 28–29/10 : correctif Types de journée sur ZIP 0.2.3, tri « Ajouter un Moment » validé, compteurs présents, suppression et informations de dépendance vérifiées, traductions FR/EN confirmées. 29/10 : infobulles au survol et fermeture automatique validées par l’utilisateur (« test ok »). Version JS de référence après correctif : card 0.2.9, styles 0.7. | 29/10/2026 |
| L6-04 | 6 | HACS et lint/format | **Terminé** | Maintenir Black, isort (`--profile black`), flake8 et les quatre workflows CI sur les prochaines évolutions. | 29/10 : fichiers formatés ; configuration `pyproject.toml` ajoutée pour compatibilité Black/isort. Suite complète locale : **449 tests**, **2 154 instructions**, **100 %**, 5 avertissements, 2,26 s, Python 3.14.3. **Confirmation utilisateur GitHub Actions : Lint & Formatting OK, HACS Validate OK, Validate with hassfest OK et Run Tests OK.** | 29/10/2026 |
| L6-05 | 6 | Documentation actualisée dans le dépôt | Terminé | Corriger ensuite les constats devenus obsolètes et le texte sur les plugins. | Documentation intégrée dans le ZIP relu. | 13/10/2026 |
| L6-06 | 6 | Cohérence finale de la documentation | Terminé | Intégrer les fichiers actualisés au dépôt ; maintenir les guides au fil des prochaines évolutions. | Documentation alignée sur 0.2.0, résultat GitHub Actions du 14/10 à 12:15:34, L1-07/L1-09 terminés, L1-06 alors en cours (état historique du 14/10) ; fichiers préparés pour intégration. | 14/10/2026 |
| L6-07 | 6 | Installation, mise à jour et retrait | **Terminé (4 scénarios sur 4)** | Maintenir ces quatre essais lors d’une évolution du stockage ou des mécanismes d’intégration. Aucun nouveau test sur la production n’est demandé. | **29/10** : installation neuve sur HAOS vierge et persistance au redémarrage confirmées. **30/10** : mise à jour 0.2.2 → état courant validée (« ok » utilisateur) ; retrait et réinstallation avec conservation des données validés (« ok ») ; **retrait avec suppression volontaire**, absence des données anciennes et réinstallation vierge validés par le dernier « ok » utilisateur. Les retours ne sont pas de nouveaux rapports automatisés. | 30/10/2026 |
| L6-08 | 6 | Préparation d’une version propre | **Terminé (publication 0.3.1)** | Maintenir notes de publication et traçabilité des correctifs ; suivre la validation de fonctionnement en production via L6-10. | 08/11 : 0.3.0 publiée avec `feat(eedomus): ajouter la reprise des agendas et l’export XLSX` ; puis 0.3.1 publiée avec correction de conformité HACS (GitHub release `97bc997`). 09/11 : utilisateur confirme installation de 0.3.1 en production. Suite locale avant publication : 572 tests, 100 %. Pas de confirmation ici de chaque workflow CI à ce tag, ni des fonctionnalités testées en production. | 09/11/2026 |
| L6-09 | 6 | Tests de régression de l’exécution et du Journal de bord | Terminé | Maintenir les nouveaux cas lors des évolutions de scripts et des mises à jour HA. | 20/10 : 19 tests ciblés réussis en simulation, modules `action_executor.py` et `logbook.py` à 100 % ciblés ; couverture globale 100 % confirmée ensuite par l’utilisateur. | 20/10/2026 |
| L6-10 | 6 | Validation post-installation en production de la 0.3.1 | **Terminé** | Maintenir une surveillance normale des anomalies ; conserver les contrôles non destructifs pour les versions futures. | **09/11 : utilisateur confirme « tous est validé en production ainsi que la reprise eedomus, l’export xlsx ok »** après installation de la version 0.3.1. Contrôles de production et parcours eedomus/XLSX validés selon son retour ; aucun nouvel essai automatisé ni import supplémentaire attribué à cette confirmation. | 09/11/2026 |
| L7-01 | 7 | Localisation HA et résolution de la zone | Validé par l’utilisateur sur plusieurs lieux | Conserver la recette des changements de lieu ; poursuivre les cas de panne dans L7-07/L7-08. | 10/11 : installation, rechargement sans erreur et changements de lieux confirmés ; pays non précisés. | 10/11/2026 |
| L7-02 | 7 | Source et calcul des jours fériés | Validé sur HA | Poursuivre avec le cache de localisation puis l’affichage dans le calendrier. | 11/11 : validation utilisateur. La livraison L7-02 avait 686 tests à 100 %. | 11/11/2026 |
| L7-03 | 7 | Cycle de vie des données et cas non résolus | Validé au redémarrage sur HA | Conserver les contrôles d’expiration et de panne dans la recette transversale. | 11/11 : fichier créé puis relu, from_cache true, date de résolution conservée et date d’évaluation actualisée. | 11/11/2026 |
| L7-04 | 7 | Affichage dans le calendrier | Validé sur HA | Conserver les contrôles de non-régression. | 11/11 : pytest et tests IHM confirmés OK par l’utilisateur. | 11/11/2026 |
| L7-05 | 7 | Gestion des exceptions existante et description proposée | Validé sur HA | Conserver les tests de non-régression. | 11/11 : lot validé par l’utilisateur, versions utils.js et i18n.js corrigées à 0.1.1. | 11/11/2026 |
| L7-06 | 7 | Formulaire et enregistrement de l’exception | Validé sur HA | Conserver les tests de non-régression. | 11/11 : validation utilisateur de la carte 0.2.12. | 11/11/2026 |
| L7-07 | 7 | Tests et contrôles de qualité | Validé par l’utilisateur | Conserver les contrôles de non-régression. | 11/11 : suite validée ; 704 pytest, 26 JS, 100 % Python. Ruff non exécuté localement. | 11/11/2026 |
| L7-08 | 7 | Validation HA et documentation | Validé — clôturé | Maintenir la documentation lors des évolutions. | 11/11 : retour utilisateur « j’ai testé ok » ; recette finale acceptée et clôture consignée. | 11/11/2026 |
| L8-01 | 8 | Étude mypy et mesure de départ | Terminé | Refaire la mesure sur la branche de travail incluant L7 avant les corrections. | 136 diagnostics dans 14 fichiers sur 40, dont 110 côté WebSocket et services. Avec `--check-untyped-defs` : 193 diagnostics dans 15 fichiers. | 11/11/2026 |
| L8-02 | 8 | Corriger le typage du stockage, du journal et de l’exécution des actions | À planifier | Traiter `logbook.py`, `storage.py` et `action_executor.py` fichier par fichier. | 4 diagnostics dans l’étude initiale. | 11/11/2026 |
| L8-03 | 8 | Corriger le typage des modèles, du moteur et des modules eedomus | À planifier | Préciser les types de sérialisation, les contraintes génériques et les structures d’import et d’export. | 22 diagnostics dans l’étude initiale. | 11/11/2026 |
| L8-04 | 8 | Qualifier les schémas WebSocket et services | À planifier | Vérifier le contrat Voluptuous/Probatio et la compatibilité avec la version minimale de Home Assistant prise en charge. | 92 diagnostics WebSocket et 18 services. Compatibilité constatée sur un schéma WebSocket représentatif. | 11/11/2026 |
| L8-05 | 8 | Décider du contrôle mypy dans GitHub Actions | À planifier | Refaire la mesure, valider la suite de tests puis décider du périmètre et du caractère bloquant. | Étude locale initiale. | 11/11/2026 |


## 5. Lot 1 — Stabiliser le socle

**Statut : partiellement réalisé.** Les corrections déjà intégrées restent enregistrées dans le tableau.

### Intégrité et comportement temporel

- **Terminé le 14/10/2026 :** contrôle des sept références des semaines types et tests des journées inconnues. La finalisation de la vue reste suivie dans le lot 3.


- Exécuter les tests backend existants et les tests WebSocket/API.
- Compléter les fichiers existants pour les corrections apportées.
- Ajouter des tests frontend ciblés si les interactions modifiées le justifient, puis effectuer les essais visuels nécessaires.
- **Terminé le 14/10/2026 :** correction et tests des moments simultanés ; tous les moments d'un même horaire sont traités par le rappel. Conserver les tests de non-régression, sans rouvrir la vue Moments.
- **Terminé le 22/10/2026 (L1-06) :** sept essais réels HA validés : action sur deux helpers et traces, deux moments simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement.
- **Terminé le 26/10/2026 (L1-11) :** test réel confirmé d’un événement manqué pendant un arrêt HA : aucun rattrapage rétroactif, reprise de la planification future. Les autres cas d’erreur et de rappels annulés restent couverts par les tests existants.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les scénarios HA de L1-06 sont validés le 22/10 ; les passages DST restent fondés sur les tests Python, sans essai réel supplémentaire annoncé.

### Ajustements CI et cohérence de version


- **Terminé (L1-07) :** filtres du workflow corrigés et exécution GitHub Actions réussie.
- **Abandonné le 14/10/2026 :** ajout d'un seuil bloquant de couverture. Conserver les mesures et rapports, sans option imposant un seuil.
- **Terminé (L1-07), selon confirmation utilisateur :** présentation du générateur revue, mise à jour du README validée par une exécution du workflow.
- **Terminé le 29/10/2026 (L6-04) :** Black, isort profil black, flake8 et les quatre workflows GitHub Actions (Lint & Formatting, HACS Validate, Validate with hassfest, Run Tests) confirmés OK par l’utilisateur. Conserver ces vérifications en CI.
- **Terminé (L1-09), selon confirmation utilisateur :** manifeste 0.2.0, ancienne constante de version supprimée ; historique du changelog corrigé, avec une seule entrée 0.1.0 datée du 10/10/2026.
- Actualiser les guides et la roadmap : retirer les constats devenus faux sur la CI et les dépendances.
- **Correction prise en compte selon l'utilisateur :** le README décrit le chargement explicite des plugins et identifie les blocs produits par GitHub Actions. Maintenir cette cohérence lors de la validation documentaire finale.
- Préparer une version propre avec notes de release, limites connues et résultats datés.

### Critères de sortie

La configuration invalide est refusée, les événements simultanés sont exécutés correctement et les scénarios temporels retenus sont vérifiés. La CI transmet les échecs et produit les rapports attendus. Les nouvelles vérifications complètent les fichiers de tests existants.

## 6. Lot 2 — Intégrer les Metadata

**Statut : en cours — cœur de la traçabilité validé, qualification d’affichage restant à préciser.**

Le modèle existant `Audit` est conservé (sans renommage imposé vers `Metadata`). Les cinq objets racine persistés portent un audit facultatif avec auteur/date de création et de modification, et les fonctions d’actualisation sont centralisées dans `PlannerEngine`. Les changements d’`Action` et de `ScheduledMoment` actualisent leur parent ; les objets référencés ne changent pas. WebSocket et services privilégient le nom affiché de l’utilisateur, sinon son identifiant ; les Options Flow utilisent `"system"`.

Les données historiques sans audit restent compatibles ; **aucune migration ni invention d’auteur ou de date historique**. En cas de première édition d’un ancien objet, l’audit commence à cette édition. La persistance et les mutations ont été validées par tests et essais Home Assistant du 22 octobre ; il reste à décider ou qualifier l’affichage direct de ces champs dans le panneau et les formulaires. Les essais de reprise/redémarrage avant déclenchement sont validés en L1-06 ; le non-rattrapage d’un événement passé pendant l’arrêt est suivi séparément en L1-11.

## 7. Lot 3 — Simplifier la gestion quotidienne

Les étapes ci-dessous conservent l’ordre demandé pour les vues. Les travaux i18n restent opportunistes.

### 3A. Moments

**Statut : terminé et figé, selon l'état communiqué.**

Périmètre terminé : CRUD, groupes d'actions, détails, traduction Home Assistant, i18n, comptages et gestion des erreurs.

Conserver cette vue comme référence pour les comportements communs des autres vues. Les tests de non-régression restent inclus dans la validation finale. Aucun nettoyage ou travail i18n isolé n'est prévu sur ce bloc.

### 3B. Types de journée

**Statut : terminé ; clôture confirmée par les essais utilisateur.**

CRUD, dépendances, boutons et conservation des saisies validés. Les actions ci-dessous sont conservées comme périmètre de contrôle historique ; elles ne constituent plus une attente sur L3-02.

Périmètre déjà traité : CRUD, moments planifiés, dialogues, validations, i18n, adaptation aux petits écrans, timeline et nettoyage de `day-types-view.js`.

#### Reste à faire

- Effectuer un dernier contrôle global du code actuel et de ses interactions avec la carte et l'API.
- Vérifier l'édition des horaires, les ajouts/suppressions et la cohérence de la timeline après sauvegarde.
- Effectuer un passage de formatage si nécessaire.
- Traiter une traduction uniquement si le fichier ou dialogue est déjà retouché.

#### Critère de sortie

Les parcours de gestion des journées et de leurs moments planifiés sont cohérents, sans régression connue. Le code est relu et formaté si nécessaire. Une traduction restante ne bloque pas la clôture.

### 3C. Semaines types

**Statut : terminé ; quatre essais HA et affichage des erreurs dans les dialogues validés.**

Les travaux ci-dessous sont conservés comme périmètre de référence et de non-régression.

#### Travaux

- Relire et finaliser création, modification et suppression.
- Vérifier l'affectation des sept jours à des types de journée existants.
- **Terminé le 14/10/2026 (L1-04) :** validation métier des références des semaines. Conserver cette règle pendant les retouches de la vue ; vérifier la présentation des erreurs dans l'interface.
- Vérifier les dépendances avec les cycles et expliquer les suppressions bloquées.
- Harmoniser les dialogues, les erreurs et le comportement sur petits écrans.
- Nettoyer le code de la vue et les interactions associées.
- Compléter l'i18n uniquement au fil des retouches.

#### Critères de sortie

- Les sept affectations sont conservées après sauvegarde et rechargement.
- Une journée inconnue est refusée par les différents chemins de modification.
- Une semaine utilisée par un cycle ne peut pas être supprimée et l'interface explique pourquoi.
- Les parcours principaux restent utilisables sur ordinateur et mobile.
- Les tests concernés sont complétés dans `test_validator.py`, `test_engine.py`, `test_websocket_api.py` et les tests de services/options selon les changements.

### 3D. Cycles

**Statut : terminé ; essais HA validés le 18 octobre et corrections de robustesse relues le 19 octobre.**

Les travaux ci-dessous restent le périmètre de référence. Les essais temporels du planificateur sont suivis séparément dans L1-06.

#### Travaux

- Relire et finaliser création, modification et suppression.
- Vérifier la séquence ordonnée de 1 à 4 semaines types.
- Vérifier la date de début un lundi et l'unicité des dates de début.
- Distinguer clairement le nombre de semaines d'un cycle de la limite du nombre de cycles enregistrés.
- Vérifier références, dépendances, erreurs et cohérence de la résolution du cycle applicable.
- Finaliser l'UX des formulaires et l'affichage sur petits écrans.
- Compléter l'i18n lors des retouches nécessaires.

#### Critères de sortie

Un cycle valide est sauvegardé et résolu correctement ; les entrées invalides sont refusées avec une erreur compréhensible. Les limites et dépendances sont cohérentes entre interface, services, WebSocket et moteur.

### 3E. Calendrier / Exceptions

**Statut : terminé ; tous les essais fonctionnels HA confirmés le 19 octobre.**

La description reste facultative ; une chaîne vide est transmise à l’API. Les brouillons conservent les saisies après erreur. Création, modification, effacement de description et suppression avec retour au cycle sont validés. Les travaux ci-dessous restent le périmètre de référence ; la qualification transversale reste ouverte ; L1-06 est clôturé le 22/10.

#### Travaux

- Finaliser la vue calendrier, la navigation et les détails du jour sélectionné.
- Vérifier création, modification et suppression des exceptions.
- Vérifier la priorité des exceptions et l'unicité d'une exception par date.
- Montrer le contexte issu des cycles et le type de journée effectivement appliqué.
- Vérifier les mises à jour après changement d'un cycle, d'une semaine ou d'une journée.
- Vérifier la cohérence entre timeline, calendrier Home Assistant et événements exécutés.
- Finaliser l'adaptation aux petits écrans ; traiter l'i18n lors des retouches.

#### Critères de sortie

L'ajout, l'édition et le retrait d'une exception actualisent correctement le planning. La vue et les entités présentent un contexte cohérent, y compris sans cycle applicable.

### 3F. Passage transversal final

**Statut : L3-06 terminé le 23/10, L3-07 et L3-08 qualifiés le 24/10 ; droits avancés reportés en L3-12.** Première série de six corrections terminée et vérifiée sur le dernier fichier le 19 octobre : protection de l’édition cycle lors des actualisations HA, gardes des cinq opérations restantes, désactivation des boutons cycles, rendu final des exceptions, gestionnaire de suppression cycle unique et ordre des validations de date. Les contrôles syntaxiques passent. Aucun nouveau résultat de suite Python ni essai complet clavier/mobile/cache/permissions n’est déduit de cette relecture.

#### Travaux

- Recenser les onglets en français en dur et les messages généraux : « Chargement… », erreurs globales et navigation. Traduire lorsque les composants sont déjà retouchés ; ne pas en faire une condition de sortie.
- Réduire les doublons CSS/JS identifiés sans rouvrir inutilement les vues figées.
- **L3-06 terminé :** cohérence des messages, conservation des champs après erreur, correction/enregistrement et annulation sans effet. Les fenêtres testées n’ont pas de croix de fermeture (contrôle non applicable). Maintenir cette garantie lors des futures évolutions.
- **L3-07 terminé le 24/10 :** anomalie initiale de focus/Tab/Échap constatée sur tous les formulaires. Premier correctif régressif (clic/saisie bloqués et navigation basculant vers le navigateur), puis correctifs v2/v3 validés progressivement par l’utilisateur dans Home Assistant : clic/saisie rétablis, focus initial dans le premier champ, navigation clavier correcte, affichage mobile OK et Échap opérationnel. Les regressions du premier correctif ne doivent pas être réintroduites. Conserver le retour du focus et les cas de sélecteurs complexes dans les vérifications de non-régression si les formulaires évoluent.
- Maintenir l’accessibilité validée (focus initial, navigation clavier et Échap) ; vérifier les éventuels nouveaux libellés et boutons au fil des modifications.
- Affichage mobile des fenêtres testé et validé le 24/10 ; poursuivre les contrôles spécifiques de la carte Lovelace si elle évolue (L6-03).
- **L3-08 validé :** après mise à jour et redémarrage HA, le frontend charge les fichiers actualisés avec un rechargement simple de la page. Conserver les tests de non-régression.
- **L3-08 qualifié :** compte HA non administrateur testé en consultation, ajout, modification et suppression. La création de profils gestionnaires / lecteurs et le contrôle côté backend sont reportés à L3-12.

#### Critère de sortie

Les vues ont des comportements communs cohérents et restent accessibles. La mise à jour du frontend ne laisse pas un ancien code en cache dans les scénarios vérifiés. Les écarts i18n non traités restent recensés.

### 3G. Duplication de tous les objets — L3-10

**Statut : Terminé le 28 octobre 2026, après démarrage le 27 octobre.** La duplication des Moments (avec reprise des actions) est **validée dans Home Assistant pour l’enregistrement et l’annulation**. La duplication d’une Action dans le même Moment et celle des Types de journée (affectations et horaires) ont également été validées en HA. La duplication des Moments planifiés a été retirée du périmètre sur décision utilisateur du 27/10 : le bouton ouvrait un formulaire d’ajout d’un autre Moment, sans véritable copie du Moment source. La création ordinaire reste disponible. **La duplication des Semaines types et celle des Cycles sont validées en HA le 28/10.** La duplication des **Exceptions de calendrier** est validée en HA le 28/10, comme les cinq autres familles retenues. Ajout demandé le 22 octobre 2026. Cette fonctionnalité complète les commandes de gestion existantes (« Éditer/Modifier » et « Supprimer ») sans rouvrir les validations déjà acquises. Cette clôture porte sur les essais fonctionnels HA communiqués, et non sur une nouvelle livraison ou une suite Python complète.

#### Périmètre de l'action « Dupliquer »

- **Moments :** créer un nouveau moment à partir d'un existant ; reprendre son nom, son icône et ses actions. Générer de nouveaux identifiants pour le moment et pour les actions copiées. Les références des journées vers le moment source restent inchangées.
- **Actions d'un moment :** dupliquer une action (libellé et séquence Home Assistant) dans le même moment, avec un identifiant d'action distinct ; aucune exécution lors de la copie.
- **Types de journée :** reprendre les horaires et les moments planifiés dans un nouveau type de journée ; copier les entrées enfants avec de nouveaux identifiants si nécessaire, tout en conservant les références vers les moments existants.
- **Moments planifiés : exclus de « Dupliquer »** sur décision utilisateur du 27/10. Conserver l’ajout, la modification et la suppression. Le même `moment_id` ne peut pas être affecté deux fois à une journée ; le bouton ajouté ouvrait simplement la création d’une autre affectation, ce qui ne constitue pas la duplication souhaitée.
- **Semaines types :** reprendre les sept affectations de types de journée dans une nouvelle semaine, sans copier physiquement les types de journée référencés.
- **Cycles :** reprendre la séquence ordonnée des semaines types ; exiger une nouvelle date de début valide (lundi et date distincte), respecter le nombre maximal de cycles configuré et les références existantes.
- **Exceptions de calendrier :** reprendre type de journée et description, mais exiger une autre date afin d'éviter deux exceptions pour la même journée.

#### Comportement commun attendu

1. Afficher « Dupliquer » à côté des actions existantes de gestion, dans les écrans concernés. Préremplir un formulaire de création à partir de la source et laisser corriger les valeurs avant validation (nom, date, heure, autres champs selon l'objet).
2. Créer un **nouvel objet distinct** : identifiants uniques et métadonnées d'audit de création fraîches (acteur et horodatage courants), sans reprendre l'historique `Audit` de la source.
3. Conserver l'objet source, ses références et les liens existants ; une copie ne doit pas déplacer, modifier ou supprimer la source, ni déclencher immédiatement les actions Home Assistant.
4. Utiliser les mêmes règles métier et contrôles de référence que la création normale ; signaler les collisions d'identifiant, de date, les limites de cycles et les références invalides. Conserver le formulaire prérempli si la création échoue.
5. Réutiliser la chaîne de persistance, notification et replanification habituelle après réussite ; actualiser les vues. Une annulation ne doit rien écrire.
6. Compléter les tests existants (`test_engine.py`, `test_validator.py`, `test_websocket_api.py`, tests services/options concernés) et les parcours HA, avec non-régression des opérations Modifier et Supprimer.

#### Critères de sortie

Les six familles retenues (Moments, Actions, Types de journée, Semaines types, Cycles et Exceptions) sont duplicables depuis leur gestion ; les Moments planifiés restent gérés via Ajouter/Modifier/Supprimer, avec des identifiants valides, sans modifier la source, avec un nouvel audit ; les cas de limites, erreurs API, annulation, dépendances et rafraîchissement sont testés. Les éléments de structure réutilisables restent des références ; les contenus enfants propres à une copie sont indépendants.

### 3H. Référence historique des jours fériés — L3-14

Le périmètre et les décisions de L3-14 sont repris dans le **lot 7**, avec un suivi détaillé sous **L7-01 à L7-08**. La ligne L3-14 reste conservée dans le tableau permanent pour la traçabilité.

### Améliorations ultérieures conservées

L'ajout guidé des moments prédéfinis reste distinct (L3-11). Import/export, profils multiples et synchronisation bidirectionnelle ne font pas partie du périmètre immédiat.


## 8. Lot 4 — Ajouter les horaires avancés

**Statut : à planifier ; périmètre à préciser.**


Faire évoluer `TimeDefinition` au-delà de `fixed_time`, avec un premier périmètre à préciser, par exemple lever/coucher du soleil et décalages. Définir les horaires indisponibles, les passages de date et la cohérence entre calcul, affichage et exécution.

Validation attendue : compatibilité des horaires fixes et résultats cohérents dans toutes les interfaces.

## 9. Lot 5 — Ajouter une source de calendrier externe

**Statut : à planifier.**


Prévoir une source externe, notamment Google Calendar, après définition des règles de correspondance et de synchronisation. La première version en lecture seule et la priorité locale → externe → cycle restent des propositions à valider.

Définir conflits, événements sur plusieurs jours, fuseaux horaires, origine des exceptions, absence de doublons et comportement en cas d'indisponibilité. Une synchronisation ne doit pas altérer les exceptions locales.

## 10. Lot 6 — Qualifier la première version stable

**Statut : validation finale à réaliser après consolidation des vues et corrections nécessaires du lot 1.**

### Travaux


- Exécuter les tests backend existants et les tests WebSocket/API.
- Compléter les fichiers existants pour les corrections apportées.
- Ajouter des tests frontend ciblés si les interactions modifiées le justifient, puis effectuer les essais visuels nécessaires.
- **Terminé le 14/10/2026 :** correction et tests des moments simultanés ; tous les moments d'un même horaire sont traités par le rappel. Conserver les tests de non-régression, sans rouvrir la vue Moments.
- **Terminé le 22/10/2026 (L1-06) :** sept essais réels HA validés : action sur deux helpers et traces, deux moments simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement.
- **Terminé le 26/10/2026 (L1-11) :** test réel confirmé d’un événement manqué pendant un arrêt HA : aucun rattrapage rétroactif, reprise de la planification future. Les autres cas d’erreur et de rappels annulés restent couverts par les tests existants.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les scénarios HA de L1-06 sont validés le 22/10 ; les passages DST restent fondés sur les tests Python, sans essai réel supplémentaire annoncé.


- **Terminé (L1-07) :** filtres du workflow corrigés et exécution GitHub Actions réussie.
- **Abandonné le 14/10/2026 :** ajout d'un seuil bloquant de couverture. Conserver les mesures et rapports, sans option imposant un seuil.
- **Terminé (L1-07), selon confirmation utilisateur :** présentation du générateur revue, mise à jour du README validée par une exécution du workflow.
- **Terminé le 29/10/2026 (L6-04) :** Black, isort profil black, flake8 et les quatre workflows GitHub Actions (Lint & Formatting, HACS Validate, Validate with hassfest, Run Tests) confirmés OK par l’utilisateur. Conserver ces vérifications en CI.
- **Terminé (L1-09), selon confirmation utilisateur :** manifeste 0.2.0, ancienne constante de version supprimée ; historique du changelog corrigé, avec une seule entrée 0.1.0 datée du 10/10/2026.
- Actualiser les guides et la roadmap : retirer les constats devenus faux sur la CI et les dépendances.
- **Correction prise en compte selon l'utilisateur :** le README décrit le chargement explicite des plugins et identifie les blocs produits par GitHub Actions. Maintenir cette cohérence lors de la validation documentaire finale.
- Préparer une version propre avec notes de release, limites connues et résultats datés.

- Tester les migrations sur des copies de configurations réalistes.
- Prévoir une période d’observation de deux semaines avec un planning représentatif si nécessaire à la qualification.
- Fixer le périmètre exact de la version stable et la compatibilité déclarée.

### Critères de sortie


- Suite complète réussie ; couverture mesurée et rapportée, avec un objectif de 100 % sans exclusions artificielles. Aucun seuil bloquant de couverture n'est imposé.
- Aucun défaut connu provoquant perte de données ou déclenchement incorrect dans le périmètre retenu.
- Parcours CRUD, modales et affichages validés sur ordinateur et mobile.
- Installation neuve, mise à jour et retrait avec/sans suppression vérifiés.
- Vérifications HACS et lint/format réussies ; documentation cohérente avec la version livrée.
- Les traductions non prioritaires ne bloquent pas la publication ; elles restent suivies.

## 11. Lot 7 — Jours fériés régionaux et création assistée d’exceptions

**Statut : clôturé le 11 novembre 2026, validation utilisateur sur HA.** Les huit sous-lots sont conservés. Le bilan de clôture en tête du document remplace le statut initial ; les cadrages ci-dessous restent la référence historique. Aucune nouvelle version publiée n’est attribuée à cette clôture.

### Sous-lots et ordre de travail proposé

Les identifiants ci-dessous servent de points de suivi indépendants ; chaque sous-lot pourra être détaillé sans renuméroter les précédents.

| Sous-lot | Périmètre à détailler | Résultat attendu avant clôture |
| --- | --- | --- |
| L7-01 — Localisation HA et résolution de la zone | Étudier les données HA disponibles et la résolution de la zone du domicile HA dans les pays pris en charge ; préciser source, précision, réseau éventuel et cache. Aucun réglage de lieu supplémentaire. | Méthode de résolution documentée et limites explicites. |
| L7-02 — Source et calcul des jours fériés | Choisir et vérifier la source ou bibliothèque ; définir les règles nationales et régionales, particularités locales, dates fixes et mobiles sur plusieurs années. | Source retenue et règles vérifiées. |
| L7-03 — Cycle de vie des données et cas non résolus | Définir localisation absente ou ambiguë, indisponibilité éventuelle, changement du domicile HA et renouvellement annuel ; conserver les exceptions enregistrées. | Comportements de repli et actualisation définis puis vérifiés. |
| L7-04 — Affichage dans le calendrier | Présenter nom du jour férié, repère visuel et zone déterminée, avec détails au survol, au clavier et sur mobile ; préserver la lisibilité des exceptions. | Affichage lisible et accessible validé. |
| L7-05 — Gestion des exceptions existante et ajout de Modifier | Réutiliser Ajouter/Supprimer ; ajouter Modifier avec valeurs existantes et date conservée ; préremplir la création fériée sans bouton dédié. | Parcours retenu le 09/11 ; implémentation et vérifications restantes. |
| L7-06 — Formulaire et enregistrement de l’exception | Préremplir la date et proposer une description modifiable ; choix explicite du type de journée, validation avant écriture, annulation sans mutation et gestion des exceptions existantes sans doublon ni écrasement automatique. | Création, annulation et exception préexistante vérifiées. |
| L7-07 — Tests et contrôles de qualité | Compléter les tests des modules existants : zone, dates, changement d’année/lieu, erreurs, création et annulation ; Black/isort/flake8 conformes et couverture suivie sans seuil imposé. | Résultats des contrôles et couverture consignés. |
| L7-08 — Validation HA et documentation | Vérifier affichage et création assistée dans HA sur ordinateur/mobile, absence de changement de planning au simple affichage ; mettre à jour documentation et suivi selon résultats réels. | Essais HA confirmés et documentation actualisée. |

**Enchaînement proposé :** préciser L7-01 et L7-02, puis L7-03 ; réaliser l’affichage L7-04 ; étudier L7-05 avant de réaliser L7-06. Compléter L7-07 au fil des modifications et terminer par L7-08. Le découpage initial ne fixait aucun fournisseur, bibliothèque ou bouton. Depuis le cadrage validé du 09/11, geo.api.gouv.fr est retenu pour L7-01 et holidays pour L7-02 ; L7-05 retient le parcours existant complété par Modifier, sans bouton spécifique aux jours fériés.

### Cadrages L7-01 et L7-02 validés le 9 novembre 2026

L7-01 : résolution de la commune et du département depuis les coordonnées du domicile HA via `geo.api.gouv.fr`, cache lié aux coordonnées et état non résolu en cas d’échec ; méthode documentée, à implémenter.

**Validation utilisateur du 9 novembre 2026 : cadrage L7-02 retenu ; implémentation et tests restent à effectuer.** Le calcul des dates utilisera localement la bibliothèque Python `holidays`, déjà employée par l’intégration Holiday de Home Assistant. Le calcul ne nécessite pas de requête Internet ; la résolution géographique initiale de L7-01 reste dépendante du réseau.

**Exemples français parmi les correspondances internationales à prévoir :**

| Territoire résolu dans L7-01 | Calendrier à utiliser |
| --- | --- |
| Métropole hors Alsace-Moselle | France (`FR`), sans subdivision |
| Moselle, département 57 | France (`FR`), subdivision `57` |
| Bas-Rhin et Haut-Rhin, départements 67 et 68 | France (`FR`), subdivision Alsace `6AE` |

Les jours nationaux et le 26 décembre en Alsace-Moselle seront affichés. Les jours fériés tombant le week-end seront conservés. Le Vendredi saint sera accompagné de la mention **« application locale à vérifier »** lorsque la condition communale n’est pas établie ; le département seul ne suffit pas à confirmer cette condition. La règle légale vise les communes ayant un temple protestant ou une église mixte. Le choix utilisateur ne signifie pas que cette vérification communale est déjà automatisée.

Aucun affichage ne modifiera le programme ni ne créera d’exception automatiquement. Le choix explicite d’un type de journée et l’enregistrement de l’exception restent nécessaires. Les autres pays et territoires font partie de la cible, selon la couverture réelle des sources et de la version de holidays installée.

### Cadrage L7-03 validé le 9 novembre 2026

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

### Cadrage L7-04 validé le 9 novembre 2026

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

### Cadrage L7-05 validé le 9 novembre 2026

**L7-05 implémenté et testé le 11 novembre 2026 ; recette IHM HA à effectuer.** La commande « Modifier » était déjà présente et est conservée. L’ajout propose désormais les noms des fêtes dans la description ; aucun bouton propre aux jours fériés n’est ajouté.

| État du jour sélectionné | Actions concernées par ce cadrage |
| --- | --- |
| Sans exception | Ajouter une exception avec la commande actuelle. |
| Avec une exception | Modifier et Supprimer ; conserver la suppression actuelle. |

« Modifier » ouvrira le formulaire prérempli avec le type de journée et la description enregistrés, en conservant la date sélectionnée. Il s’agit de modifier l’exception existante, sans en créer une seconde. Les autres commandes déjà validées ne sont pas retirées par ce cadrage.

Pour l’ajout sur une date fériée, préremplir la date sélectionnée et proposer une description modifiable, par exemple « Jour férié : Noël ». Le type de journée restera à choisir explicitement. Lors d’une modification, conserver la description existante ; ne pas la remplacer automatiquement par le nom du jour férié.

La réserve « Application locale à vérifier » du Vendredi saint restera présentée dans les informations du jour lorsque nécessaire. L’ouverture du formulaire ne provoquera aucune écriture ; l’enregistrement nécessitera la validation de l’utilisateur et une annulation restera sans modification. Les validations détaillées et le comportement d’enregistrement retenus dans L7-06 sont décrits ci-dessous.

### Cadrage L7-06 validé le 9 novembre 2026

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

### Plan de tests L7-07 validé le 9 novembre 2026

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

### Plan d’essais L7-08 validé le 9 novembre 2026

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

### Décisions retenues

- **Aucun nouveau paramétrage de lieu dans Day Planner.** Utiliser la localisation du domicile déclarée dans Home Assistant comme source pour déterminer la zone des jours fériés. Ne pas utiliser la position du navigateur, du téléphone ou d’une personne.
- **Précision selon le lieu de l’installation HA, tous pays.** Distinguer pays, subdivisions et particularités locales selon les sources disponibles. France / Alsace-Moselle restent des cas de test, sans limitation géographique du projet. Ne pas déduire le territoire de la langue ou du seul fuseau horaire.
- **Niveau B : affichage et création assistée.** Le caractère férié est une information du calendrier ; il ne modifie pas le type de journée résolu et n’exécute aucune action sans exception créée et enregistrée explicitement.
- **Étape 2 : parcours existant retenu sous L7-05.** Conserver Ajouter/Supprimer et ajouter Modifier pour une exception existante. Aucun bouton spécifique aux jours fériés ; le formulaire actuel sera prérempli à la création sur une date fériée, sans remplacer la description en édition.

### Étape 1 — Détermination de la zone et affichage

1. Examiner les données réellement disponibles dans la configuration HA et la méthode permettant d’en déduire la zone régionale. Si une résolution à partir de coordonnées est nécessaire, préciser la source, sa fiabilité, le besoin réseau éventuel et sa mise en cache avant d’implémenter. Le calcul des jours et la détermination géographique sont deux sujets distincts ; ne pas promettre un fonctionnement intégralement hors ligne sans vérification.
2. Prévoir la conduite à tenir si la localisation est absente, ambiguë ou non résolue : indiquer que les jours fériés régionaux ne sont pas déterminés, sans inventer de région ni ajouter un champ de lieu. Le planning existant doit continuer de fonctionner.
3. Afficher les jours fériés dans la vue Calendrier avec leur nom et un repère visuel lisible, sans masquer les exceptions existantes. Rendre les détails accessibles au survol, au clavier et sur mobile ; indiquer la zone déterminée.
4. Étudier la réaction à une modification de la localisation du domicile HA et le renouvellement des données lors d’un changement d’année. Ne pas réécrire automatiquement les exceptions déjà enregistrées.

### Étape 2 — Création assistée d’une exception

- Depuis la date sélectionnée, réutiliser la commande actuelle Ajouter une exception ; si une exception existe, proposer Modifier et conserver Supprimer. Aucun bouton spécifique aux jours fériés.
- Date préremplie ; nom du jour férié présenté ; description préremplie proposée et modifiable, par exemple « Jour férié : Noël ».
- Type de journée choisi explicitement par l’utilisateur. Création effective uniquement à la validation ; annulation sans écriture.
- Si une exception existe déjà pour la date, la conserver et rendre son état visible ; aucune création en double ni écrasement automatique. Toute modification suit le parcours habituel avec validation explicite.

### Hors périmètre de cette évolution

- Génération en masse ou automatique des exceptions d’une année (niveau C non retenu).
- Ajout d’un réglage manuel de pays/région dans Day Planner.
- Modification automatique des plannings, cycles et exceptions déjà créés.
- Choix d’un fournisseur international non vérifié : le fournisseur géographique reste à reprendre ; la portée internationale est explicitement confirmée par l’utilisateur.

### Critères de validation prévus

- Localisation HA exploitée sans nouveau paramétrage ; cas nationaux et régionaux de plusieurs pays contrôlés, dont France / Alsace-Moselle, y compris particularités locales et limites de la source choisie.
- Source et règles des jours fériés vérifiées lors de l’étude technique ; dates fixes et mobiles testées sur plusieurs années.
- Cas localisation manquante/ambiguë, changement de lieu et changement d’année gérés explicitement.
- Absence de modification de planning par le simple affichage d’un jour férié ; création, annulation et exception existante testées.
- Libellés FR/EN, navigation clavier/mobile et versions des JS modifiés pris en compte lorsqu’un fichier est retouché.
- Tests ajoutés dans les modules existants pertinents, compatibilité Black/isort/flake8 sans nouvelles règles ignore, couverture suivie sans seuil imposé.

## 11 bis. Lot 8 — Typage progressif avec mypy

**Statut : étude initiale terminée, mise en œuvre à planifier.** L’ordre proposé commence par le stockage, le journal et l’exécution des actions. Il se poursuit par les modèles, le moteur et eedomus, puis par les interfaces Home Assistant.

La mesure de départ porte sur le commit GitHub `0562541` formaté avec Ruff, avec Python 3.14.10, Home Assistant 2026.10.4 et mypy 2.4.1. L’analyse standard relève 136 diagnostics dans 14 fichiers sur 40. Le mode `--check-untyped-defs` relève 193 diagnostics dans 15 fichiers. La base mesurée précède les ajouts L7 locaux et le périmètre exclut `scripts/tests/`. Refaire la mesure sur la branche de travail avant de commencer les corrections.

Les 110 diagnostics des schémas WebSocket et services demandent une qualification distincte. Home Assistant expose des types Probatio et fournit une compatibilité Voluptuous à l’exécution. Vérifier les deux interfaces et la version minimale prise en charge avant de modifier les imports ou les schémas.

Traiter les corrections fichier par fichier et privilégier les annotations précises sans exclusions globales. Conserver le comportement et les données existantes, y compris l’audit. Exécuter Ruff et les tests ciblés dans les modules actuels à chaque étape, puis la suite complète avant validation d’un lot de corrections. L’objectif de couverture reste 100 %, sans `--cov-fail-under=100`. Maintenir mypy en analyse locale pendant cette phase et décider séparément de son activation dans la CI.

## 12. Mise à jour du suivi et journal conservé

À chaque mise à jour :

1. Lire la version courante et conserver toutes les lignes et tous les identifiants du tableau.
2. Actualiser les statuts uniquement avec une indication utilisateur ou un résultat vérifié ; préciser leur origine.
3. Actualiser le reste à faire, la preuve et la date des lignes concernées.
4. Ajouter les nouveaux points avec un identifiant inédit, sans renuméroter les précédents.
5. Ajouter une entrée au journal ci-dessous pour les changements significatifs ; les entrées historiques restent conservées.
6. Conserver les points terminés, reportés ou abandonnés avec leur décision. Si une tâche est scindée, conserver sa ligne et référencer les nouvelles lignes.

Les critères des lots peuvent être précisés et de nouvelles tâches ajoutées. Les travaux décidés ne sont pas retirés silencieusement. Le suivi hebdomadaire reprend les changements significatifs du tableau.

| Date | Mise à jour / décision |
| --- | --- |
| 12/10/2026 | Création de la roadmap initiale en six lots. |
| 13/10/2026 | Relecture du nouveau ZIP : adaptations CI et tests intégrées ; défauts de références des semaines et de moments simultanés reproduits. |
| 13/10/2026 | Statuts utilisateur intégrés : moments terminés et figés ; journées presque terminées ; semaines, cycles puis calendrier à finaliser. i18n non prioritaire. |
| 13/10/2026 | Retour à la structure en six lots ; création du tableau permanent avec identifiants stables et règle de conservation des lignes. |
| 14/10/2026 | L1-04 et L1-05 passent à Terminé : références des sept jours validées et moments simultanés corrigés. Données des anciens tests adaptées ; 29 tests des planificateurs réussis. |
| 14/10/2026 | Nouveau résultat utilisateur de référence : 403 tests réussis, 1 896 instructions mesurées, aucune non couverte, 100 % de couverture, 5 avertissements en 1,22 s. L6-01 actualisé et L6-02 terminé pour cet état du code. |
| 14/10/2026 | L1-08 passe à Abandonné : seuil bloquant de couverture refusé par l'utilisateur. Mesure et rapports conservés, sans seuil bloquant dans les commandes ni dans la CI. |
| 14/10/2026 | Calcul autour de minuit et trois tests de changement d'heure réussis. Règle retenue : rattrapage au printemps à la première heure valide et exécution unique au premier passage en automne ; pas de rattrapage général après un arrêt. |
| 14/10/2026 | Résultat utilisateur actualisé : 407 tests réussis, 1 908 instructions mesurées, aucune non couverte, 100 %, 5 avertissements en 1,22 s. L1-06 passe à En cours : essais réels HA encore à confirmer. |
| 14/10/2026 | Rappel créé pour les essais réels HA le 15 octobre vers 18 h (Europe/Paris). Documentation et suivi actualisés, sans suppression des lignes. |

| 14/10/2026 | L1-07 terminé : workflow tests.yml exécuté avec succès et README généré à 12:15:34 ; 407 tests, 1 908 instructions et 100 % de couverture. |
| 14/10/2026 | Publication 0.2.0 réussie après rétablissement du lien avec l'historique de la release 0.1.0. La version publiée devient 0.2.0 ; cela ne valide pas le lot Metadata. |
| 14/10/2026 | L1-09 terminé selon confirmation utilisateur : référence de version dans le manifeste et nettoyage du changelog d'après le tag 0.1.0 du 10 octobre. L1-06 reste En cours pour les essais réels HA. |

| 14/10/2026 | L6-06 : documentation alignée sur la version publiée 0.2.0 et le résultat GitHub Actions à 12:15:34. Les guides distinguent Python local 3.14.3 et CI 3.14.8, clôturent L1-07/L1-09 et conservent les essais HA ouverts. Fichiers préparés pour intégration au dépôt. |

| 19/10/2026 | L3-02 et L3-03 clôturés d’après les essais HA : saisies conservées, CRUD, dépendances et erreurs visibles. |
| 19/10/2026 | L3-04 clôturé : essais des cycles validés le 18/10, puis corrections de robustesse vérifiées dans le fichier du 19/10. |
| 19/10/2026 | L3-05 clôturé après confirmation de tous les essais HA : description dans le champ, description vide acceptée, édition et suppression, exception appliquée puis retour au cycle. |
| 19/10/2026 | Relecture de 14 fichiers frontend : 12 JS et 2 JSON syntaxiquement valides. Six corrections transversales relues dans le dernier day-planner-card.js ; L3-06, L3-07 et L6-03 restent en cours pour leurs contrôles restants. |
| 19/10/2026 | L1-06 explicitement maintenu en cours. Les 407 tests Python et 100 % de couverture restent le résultat communiqué du 14/10, sans nouvelle exécution. Aucun rappel créé ou reprogrammé dans cette mise à jour. |
| 20/10/2026 | L1-10 : journalisation renforcée des actions et cibles indisponibles ; avertissements `homeassistant.helpers.service` recopiés en ERROR Day Planner sans supprimer le WARNING HA. Événement `day_planner_action` avant le service et contexte partagé pour l’attribution Logbook. |
| 20/10/2026 | Validation fonctionnelle Logbook : événement source « Day Planner — action XX1 test (id : XX1) », puis transition de `input_boolean.day_planner_test` de Activé à Désactivé avec cette action comme cause. Le message « Aucune cause... » sur l’événement racine est normal. |
| 20/10/2026 | L6-09 et L6-01 : ajout de tests des branches défensives (9 lignes manquantes sur 2 093 instructions au rapport intermédiaire) ; 19 tests ciblés réussis en simulation et 100 % de couverture globale confirmé par l’utilisateur. Nombre exact de tests du dernier rapport non communiqué. L1-06 conserve son statut En cours. |
| 21/10/2026 | Audit étendu aux modèles `Moment`, `WeekSchedule`, `Cycle` et `CalendarException`, après `DayType` ; fonctions centralisées dans `PlannerEngine`. Validation progressive des tests dans les fichiers existants, sans patch et sans migration. Dernier rapport complet chiffré : 449 tests, 2 146 instructions, 0 non couverte, 100 % de couverture. |
| 21–22/10/2026 | WebSocket et services HA transmettent l’auteur réel lorsqu’il est disponible ; Options Flow utilise explicitement `"system"`. Création/modification d’Actions et Moments planifiés attribuées à leur parent. Tests validés successivement. |
| 22/10/2026 | Contrôles fonctionnels Home Assistant confirmés par l’utilisateur pour Moments, Actions, Types de journée, Moments planifiés, Semaines types, Cycles et Exceptions. L2-01 et L2-03 terminés ; L2-02 reste ouvert uniquement pour l’affichage détaillé des métadonnées et qualification associée. Aucune migration d’audit. |
| 22/10/2026 | Extension fonctionnelle décidée : opération « Dupliquer » sur toutes les familles gérées (Moments, Actions, Types de journée, Moments planifiés, Semaines types, Cycles et Exceptions), en complément des opérations de modification/suppression. L3-10 élargi ; création de L3-11 pour conserver le sujet historique des moments prédéfinis guidés. Statut : À planifier ; aucun code déclaré modifié. |
| 22/10/2026 | **L1-06 clôturé** après confirmation utilisateur des sept scénarios HA (deux helpers et traces, deux moments simultanés, replanification horaire, exception, changement de cycle, passage à minuit, redémarrage avant événement). Le test de non-rattrapage après un arrêt couvrant un événement n’a pas été annoncé : suivi explicite L1-11 « À confirmer » ; aucune nouvelle exécution de pytest attribuée à cette validation. L3-06 devient la prochaine priorité. |

| 23/10/2026 | **L3-06 clôturé** après retours utilisateurs : affichage du message de limite à 4 cycles, conservation des saisies lors d’une erreur, possibilité de corriger puis enregistrer, annulation sans modification. Pas de croix de fermeture sur les fenêtres : contrôle non applicable, sans nouveau test requis. Prochaine priorité L3-07 (focus, clavier, libellés et responsive), en lien avec L6-03. |

| 22–23/10/2026 | **L3-07 : défaut de navigation clavier identifié sur l'ensemble des formulaires modaux.** Les onglets de fond reçoivent le focus avant la fenêtre ; Échap ne ferme pas. Patch commun préparé, contrôle syntaxique et `git apply --check` réussis sur le JS de la bibliothèque (19/10). Essais HA indispensables avant validation ou clôture du lot. |

| 24/10/2026 | **L3-07 clôturé** après validation utilisateur dans HA : souris et saisie fonctionnent après correction v2, focus initial correct avec v3, navigation Tab/Maj+Tab correcte, affichage mobile réel OK, touche Échap opérationnelle. Le premier patch avait bloqué clic et saisie et ne doit pas être réintroduit. L3-08 est le prochain point à traiter. Aucun nouveau total pytest n’est attribué à ces essais manuels. |

| 24/10/2026 | **L3-08 qualifié** : simple rechargement après mise à jour/redémarrage HA fonctionne ; un compte non administrateur peut consulter, ajouter, modifier et supprimer. Étude d’impact des droits fins réalisée ; **L3-12 reporté** par décision utilisateur jusqu’à la finalisation des autres fonctionnalités. Aucun changement de permissions. |

| 26/10/2026 | **L1-11 clôturé** après confirmation utilisateur du test HA : événement tombant pendant un arrêt non rattrapé au redémarrage, prochain événement futur replanifié et continuité assurée. **L3-10** devient le prochain chantier ; aucune duplication annoncée comme implémentée. |
| 27/10/2026 | **L3-10 en cours** : premier patch ciblé Moments + copie des actions préparé à partir du JS de bibliothèque du 19/10 enrichi des correctifs L3-07 v1/v2/v3. Contrôles de syntaxe, application et scénarios isolés Node réussis ; en attente des essais Home Assistant. Aucun test Python supplémentaire ni livraison confirmée. |
| 27/10/2026 | **L3-10 — Moments confirmés en HA** par l’utilisateur : duplication avec enregistrement ou annulation OK. Nouvelle étape **Actions isolées** : patch JS ciblé préparé pour `day-planner-card.js` et testé hors HA (bouton, séquence clonée, collisions d’identifiants, sauvegarde, annulation, erreurs). Essai réel et contrôle de non-régression restent à faire avant validation de cette étape. |

| 27/10/2026 | **L3-10 — Actions confirmées en HA** : utilisateur indique tests 4 et 5 OK (duplication enregistrée et annulation sans création). Nouveau patch **Types de journée** préparé, réutilisant les commandes WebSocket d’ajout et suppression ; reprise des affectations et de leurs heures, sans créer les Moments référencés, avec tentative de nettoyage d’une copie partielle. Syntaxe et tests isolés Node vérifiés, essai HA à faire. |

| 27/10/2026 | **L3-10 — Types de journée validés en HA** : tous les tests convenus sont OK selon l’utilisateur (copie, sauvegarde, annulation). Étape suivante **Moments planifiés** : la validation du backend interdit de réutiliser le même `moment_id` dans une journée. Patch uniquement `day-planner-card.js` : bouton Dupliquer dans la fenêtre d’édition, heure préremplie, sélection d’un autre Moment non utilisé ; bouton désactivé si aucun disponible. Aucun changement du backend ni du Moment source. Syntaxe et tests isolés Node OK ; essai HA requis. |

| 27/10/2026 | **L3-10 — décision de retrait de « Dupliquer » pour les Moments planifiés.** Test utilisateur dans la timeline : la duplication proposée ouvrait l’ajout d’un autre Moment et d’un horaire, sans véritable duplication de l’affectation. Demande explicite : supprimer ce bouton. Retour au comportement antérieur via patch inverse ne touchant que `day-planner-card.js` ; Moments, Actions et Types de journée conservés. **Retrait confirmé OK dans HA** le 27 octobre. |

| 27/10/2026 | **L3-10 — duplication des Semaines types à tester dans HA.** Nouveau patch ciblé dans `day-planner-card.js` et `views/week-schedules-view.js`. Le bouton Dupliquer ouvre le formulaire de création avec un nouvel identifiant, un libellé suffixé « (copie) » et les 7 types de journée référencés ; il ne recopie pas les types de journée eux-mêmes et réutilise l'API d'ajout. Contrôle de syntaxe JS, de patch et scénarios isolés Node (affichage, préremplissage, collisions, enregistrement, annulation, erreur API) réussis. Aucune modification Python ; essai réel HA encore nécessaire. |

| 28/10/2026 | **L3-10 — Semaines types validées en HA** : tous les essais demandés ont réussi (sept affectations recopiées, copie indépendante, enregistrement et annulation). **Duplication des Cycles à tester** : patch frontend ciblé (`day-planner-card.js`, `views/cycles-view.js`) ; nouveau nom et ID, mêmes références ordonnées aux semaines types, date de début laissée vide afin d'exiger un lundi distinct ; création via l'API existante, respect des validations et limites backend. Contrôles syntaxiques et tests isolés Node réussis. Aucun changement Python ; essai HA requis. |
| 28/10/2026 | **L3-10 — Duplication des Cycles validée en HA** : utilisateur confirme « test ok » après le patch de duplication. **Exceptions de calendrier à tester** : patch frontend ciblé (`day-planner-card.js`, `views/calendar-view.js`), ajout du bouton Dupliquer dans les actions de l'exception du jour sélectionné ; copie du type de journée et de la description ; nouvelle date obligatoire, unique, sans reprise de la date source ; ID créé selon le schéma actuel `exception-AAAA-MM-JJ`. Après enregistrement, affichage du mois et de la nouvelle date. Refus des dates invalides ou occupées, conservation des champs après erreur, annulation sans écriture. Syntaxe, contrôle du patch et 10 tests isolés Node validés ; essai HA encore requis, pas de modification backend. |


| 28/10/2026 | **L3-10 clôturé** après validation HA de la duplication des Exceptions de calendrier (« test OK » de l’utilisateur). La duplication des six familles retenues est désormais validée : Moments, Actions, Types de journée, Semaines types, Cycles et Exceptions. La duplication des Moments planifiés reste délibérément supprimée. Aucun nouveau total pytest ni publication affirmé. Prochaine priorité : L6-03, contrôles transversaux frontend et non-régression après cumul des patchs, puis L6-04, HACS et lint/format. |
| 28/10/2026 | **L6-03 : syntaxe du frontend contrôlée** par l’utilisateur : 12 fichiers `.js` et 2 fichiers `.json` valides. Navigation entre les vues contrôlée ; suppression refusée pour un Type de journée référencé par une Semaine type ou une exception, protections backend conservées. |
| 29/10/2026 | **L6-03 : Types de journée validés dans HA** après correctifs fondés sur le ZIP 0.2.3 : ordre alphabétique dans Ajouter un Moment OK ; compteurs et détails des utilisations présents ; refus de suppression avec références OK ; multilingue FR/EN OK. Ergonomie initiale des détails au clic signalée comme peu pratique, remplacée par infobulles au survol ; dernier test utilisateur « test ok ». L6-03 passe à **Terminé**. Les versions frontend modifiées ont été incrémentées (card 0.2.9, styles 0.7) sans modification du manifeste ni nouvelle publication. |
| 29/10/2026 | **L6-04 démarre** : trois workflows du ZIP 0.2.3 identifiés (Lint & Formatting, HACS Validate, Validate with hassfest) ; exécution locale en lecture seule de Black/isort/flake8 puis vérification des workflows GitHub Actions à effectuer. Les résultats ne sont pas encore confirmés. |
| 29/10/2026 | **L6-04 — Formatage local et tests Python validés.** Black a identifié cinq fichiers à reformater ; l’utilisateur a corrigé les imports en harmonisant isort via `--profile black` et un `pyproject.toml`, puis confirmé la réussite de Black, isort et flake8 pour tous les fichiers. La suite complète a réussi : **449 tests**, **2 154 instructions**, **0 manquante**, **100 % de couverture**, **5 avertissements**, **2,26 s**, **Python 3.14.3**. Le résultat du 21/10 (2 146 instructions) reste conservé. **HACS Validate, hassfest et workflows GitHub Actions restent à confirmer** ; aucune clôture anticipée. |

| 29/10/2026 | **L6-04 clôturé sur confirmation utilisateur GitHub Actions** : 1) Lint & Formatting OK ; 2) HACS Validate OK ; 3) Validate with hassfest OK ; 4) Run Tests OK. Le formatage local Black/isort/flake8 et les 449 tests Python à 100 % avaient déjà été validés. Aucune nouvelle release ni version publiée n’est déduite de ces succès. **Prochaine priorité : L6-07 (installation, mise à jour, retrait) en environnement de test.** |

| 29/10/2026 | **L6-07 — lancement de la qualification installation neuve.** Scénario HA de test documenté à partir du ZIP source 0.2.3 relu : installation depuis l’état actuel du dépôt (L6-03 intégré), config entry unique, configuration initialement vide, création du stockage, panneau, trois capteurs et calendrier. Éléments attendus identifiés par lecture de `__init__.py`, `config_flow.py`, `storage.py`, `sensor.py` et `calendar.py`. **Tests manuels encore à effectuer ; aucune modification du code.** La mise à jour et le retrait suivront. |

| 29/10/2026 | **L6-07 — installation neuve validée en conditions réelles** : l’utilisateur confirme l’installation réussie sur un HAOS vierge de Day Planner et l’ensemble des résultats attendus, y compris intégration unique, panneau, configuration vide, 3 capteurs, calendrier, stockage, absence d’erreur de chargement et persistance d’un Moment au redémarrage. Le scénario 1 est clos ; le scénario 2 (mise à jour 0.2.2 vers état actuel 0.2.3 + correctifs) est préparé, sans exécution annoncée. Le retrait reste à tester. |

| 30/10/2026 | **L6-07 — mise à jour 0.2.2 → 0.2.3 + correctifs confirmée « ok »** par l’utilisateur. Aucun log détaillé n’a été transmis ; validation retenue comme confirmation du scénario 2, après installation neuve validée le 29/10. **Prochain scénario documenté** : retrait avec conservation des données, option `delete_data_on_remove=False`, puis réinstallation sur HAOS de test et contrôle de la reprise des objets. La suppression volontaire sera testée séparément. |
| 30/10/2026 | **L6-07 — retrait avec conservation validé en HAOS de test** : réponse « ok » de l’utilisateur après le scénario 3 (option `delete_data_on_remove=False`, retrait puis réinstallation et récupération des objets). **Scénario 4 préparé :** retrait avec suppression volontaire (`delete_data_on_remove=True`), sauvegarde obligatoire, vérification de la disparition du fichier de stockage puis configuration vierge après réinstallation. Rien de destructif ne doit être réalisé sur la production. Aucune modification Python ni nouvelle publication. |

| 30/10/2026 | **L6-07 clôturé** : quatrième essai sur HAOS de test confirmé « ok » par l’utilisateur, après retrait avec option de suppression volontaire et réinstallation sur configuration vide. Les quatre scénarios sont désormais validés ; aucun nouveau résultat pytest ni release n’en découle. **L6-08 passe En cours** : préparation documentaire de la publication à partir du ZIP 0.2.3 et du dépôt courant, contrôle des tags et de semantic-release avant décision. |

### Contrôles L6-04 — bilan final au 29 octobre 2026

- **Terminé en local :** Black/isort/flake8. Les cinq fichiers initialement refusés par `black --check` ont été formatés ; conflit de style d’import résolu via `--profile black` dans les commandes isort et via `pyproject.toml` (profil black). L’utilisateur confirme tous les fichiers conformes.
- **Terminé en local :** suite pytest complète après formatage, **449 tests réussis, 2 154 instructions, 0 manque, 100 %**, 5 warnings en 2,26 s (Python 3.14.3). Pas de seuil `--cov-fail-under=100` imposé.
- **Terminé en CI le 29/10 :** `Lint & Formatting`, `HACS Validate`, `Validate with hassfest`, `Run Tests` : **tous OK**, selon confirmation de l’utilisateur sur GitHub Actions.
- **L6-04 clôturé :** maintenir ces contrôles à chaque évolution ; tout échec ultérieur sera traité fichier par fichier.


### L6-07 — installation, mise à jour et retrait : quatre scénarios validés (clôturé)

- **Validé sur HAOS de test** : tous les résultats du scénario d’installation neuve ont été confirmés par l’utilisateur, y compris conservation d’un Moment après redémarrage.
- **Retour du 30/10** : réponse « ok » à la procédure de mise à jour 0.2.2 → code courant, retenue comme validation du scénario 2 (pas de détail de journal fourni).
- **Validé le 30/10** : retrait avec conservation des données et réinstallation ; l’utilisateur répond « ok » à la procédure complète du scénario 3.
- **Validé le 30/10** : retrait avec suppression volontaire sur HAOS isolé sauvegardé ; disparition des anciennes données et réinstallation avec configuration vide, confirmé par « ok » utilisateur. Aucun essai destructif sur la production.
- **Aucune évolution du code** attribuée à cette validation.

| 08/11/2026 | **L6-08 — Publication 0.3.0** sur GitHub : reprise des agendas eedomus et export XLSX via `feat(eedomus)`. Dernier contrôle local fourni : 572 tests, 2 990 instructions, aucune non couverte, 100 % ; Black/isort/flake8 OK. Une validation hassfest a signalé une URL codée dans `strings.json` et `translations/en.json` ainsi qu’un avertissement `CONFIG_SCHEMA`, corrigés dans la suite de publication. |
| 08/11/2026 | **L6-08 — Publication 0.3.1** sur GitHub, correctif de conformité HACS eedomus ; référence GitHub `97bc997`, changelog « eedomus: mise en conformités HACS ». Ne pas assimiler cette publication à une validation fonctionnelle de toutes les fonctions en production. |
| 09/11/2026 | **0.3.1 installée sur la production** selon confirmation utilisateur. L6-08 passe Terminé pour la livraison ; **L6-10 ajouté** pour des vérifications non destructives de fonctionnement après mise à jour. Les tests HAOS isolés de L6-07 restent acquis ; aucune opération destructrice n’est planifiée en production. |
| 09/11/2026 | **L6-10 clôturé après retour de production** : l’utilisateur confirme tous les contrôles de fonctionnement de Day Planner 0.3.1, la reprise des agendas eedomus et l’export XLSX. Il s’agit d’une validation réelle déclarée par l’utilisateur, non d’une nouvelle exécution pytest. Le travail futur d’enrichissement des propriétés/métadonnées XLSX reste hors du périmètre actuel. |

| 09/11/2026 | **L3-14 ajouté à la roadmap : jours fériés régionaux pour faciliter les journées d’exception.** Choix utilisateur : aucun réglage de lieu supplémentaire, localisation déduite de celle déclarée dans HA ; niveau régional France / Alsace-Moselle ; **niveau B** (affichage et création assistée). Le bouton ou l’accès à la création en étape 2 reste à étudier. Génération automatique non retenue. Aucun code, aucune nouvelle publication ni réouverture des validations de production. |

| 09/11/2026 | **Lot 7 créé à la demande de l’utilisateur** pour détailler les sous-lots des jours fériés régionaux et de la création assistée d’exceptions. Périmètre L3-14 transféré sans changement des décisions ; ligne historique conservée et renvoyée vers L7-01 à L7-08. Ajout du lot à la vue d’ensemble, du découpage et des critères de suivi. Aucune implémentation ni validation technique déduite de cette réorganisation. |

| 09/11/2026 | **Cadrages L7-01 et L7-02 validés.** Localisation HA résolue via geo.api.gouv.fr et mémorisée ; calcul local avec holidays, FR national / 57 / 6AE. Vendredi saint : mention « application locale à vérifier » si condition communale non établie ; conservation des dates de week-end, aucune exception automatique. Décisions tracées dans les documentations fonctionnelle et technique. Compatibilité de version, implémentation et tests restent à faire ; aucun code ni test nouveau validé. |

| 09/11/2026 | **Cadrage L7-03 validé par l’utilisateur.** Cache persistant séparé du planning, lié aux coordonnées avec date de résolution ; nouvelle résolution après changement de lieu et rejet des réponses obsolètes ; reprises réseau espacées, états non résolu/hors périmètre ; calcul local pour l’année affichée. Exceptions existantes conservées. Durée de validité, renouvellement périodique et délais des reprises restent ouverts. Roadmap et deux documentations actualisées ; aucune implémentation ni exécution de tests déduite de cette validation. |

| 09/11/2026 | **Cadrage L7-04 validé par l’utilisateur.** Repère férié avec icône et libellé, maintien du type de journée et de l’exception prioritaire ; détails accessibles au survol/clavier/mobile, nom complet disponible sur mobile, zone ou message non résolu au-dessus du calendrier, réserve locale pour le Vendredi saint. Affichage informatif, accès à la création à étudier sous L7-05. Décisions tracées dans les deux documentations ; implémentation et tests à faire. |

| 09/11/2026 | **Cadrage L7-05 validé après ajustement utilisateur.** Réutiliser la gestion actuelle Ajouter/Supprimer et ajouter Modifier pour une exception existante ; formulaire prérempli avec valeurs enregistrées et date conservée. Préremplissage férié réservé à la création, description existante conservée en édition. Aucun bouton dédié aux jours fériés. Roadmap et documentations fonctionnelle/technique actualisées ; réalisation et tests à faire. |

| 09/11/2026 | **Cadrage L7-06 validé par l’utilisateur.** Formulaire ajout/édition avec date conservée en modification, type obligatoire et toujours valide, description facultative ; refus des créations en doublon, identité et audit de création conservés en édition, audit de modification actualisé, protection contre doubles enregistrements et actualisation après réussite. Saisies conservées dans leurs champs après erreur ; Annuler/Échap sans écriture. Suppression actuelle conservée. Décisions tracées dans les deux documentations ; implémentation et tests à effectuer. |

| 09/11/2026 | **Plan de tests L7-07 validé par l’utilisateur.** Couvrir localisation, cache et réseau simulé, jours fériés, années, exceptions, formulaire et non-régression du planning. Tests Python dans les modules existants de scripts/tests/ de préférence ; contrôles ciblés puis suite complète, objectif de couverture 100 % sans seuil bloquant, syntaxe frontend et qualité du dépôt. Essais réels HA séparés sous L7-08. Décisions tracées dans les deux documentations ; tests non encore exécutés. |

| 09/11/2026 | **Plan d’essais L7-08 validé ; cadrage des huit sous-lots du lot 7 consigné.** Recette HA ordinateur/mobile/clavier, parcours exceptions, redémarrage, réseau/localisation et consultation d’années ; changements de lieu et simulations de panne sur instance de test. Tracer version, résultats et anomalies, puis adapter les documentations au comportement livré. Clôture après réussite L7-07 et validation L7-08. Implémentation, tests et essais restent à faire ; points techniques ouverts conservés. |

| 09/11/2026 | **Première brique L7-01 implémentée localement sur main 0562541.** Nouveau résolveur géographique, états explicites et raccordement au runtime ; 44 nouveaux cas dans test_runtime.py. Suite complète 616 tests, 3 058 instructions, 100 %, 5 avertissements, HA 2026.10.4/Python 3.14.9 ; formatage/lint des fichiers modifiés OK. README tests régénéré avec le code du workflow existant. Cache et activation automatique reportés à leur implémentation L7-03 ; calcul L7-02, affichage L7-04 et recette HA restent à faire. Aucune nouvelle publication ni installation réelle. |

| 09/11/2026 | **Correction explicite du périmètre par l’utilisateur : tous les sous-lots du lot 7 dépendent du lieu de l’installation HA, sans restriction à la France.** Pays et subdivisions dynamiques, adaptateurs et tests multi-pays à prévoir ; Alsace-Moselle comme cas particulier. Le ZIP L7-01 fourni et ses 616 tests restent une preuve historique du prototype FR, à reprendre pour la cible internationale. Fournisseur géographique international à étudier ; aucune implémentation mondiale ni nouveau test annoncé. |

| 09/11/2026 | **Capteur de diagnostic de localisation validé par l’utilisateur.** Nom « Day Planner — Localisation », identifiant proposé binary_sensor.day_planner_location, sans holiday. État exploitable/non exploitable et disponibilité ; attributs integration, last_evaluated, country_code/name, subdivision_code/name, locality, source, from_cache, resolved_at, status/reason. Rattaché à L7-01/L7-03, contrôles L7-07/L7-08. Aucun second capteur ni implémentation attribués à cette validation. |

| 09/11/2026 | **L7-01 reconstruit en v2 complète, sans installation préalable.** Photon/OSM international, référentiel pycountry, évaluation en arrière-plan, suivi du domicile, cache mémoire et capteur Day Planner — Localisation. 620 tests, 3 201 instructions, 100 %, 5 avertissements ; tests HTTP simulés, service réel non validé dans cet environnement, recette HA à réaliser. Calcul L7-02, cache persistant/reprises L7-03 et affichage restent à faire. Premier ZIP FR remplacé ; aucune release ni installation réelle annoncée. |

| 10/11/2026 | **Correctif L7-01 v3 — i18n native après signalement utilisateur.** Nom via translation_key/has_entity_name ; libellés, statuts et motifs dans strings.json et translations/en.json/fr.json ; reason_detail chargé avec le helper HA. Identifiant et codes conservés. 622 tests, 3 203 instructions, 100 %, 5 avertissements ; chargeur réel de traductions HA vérifié en FR/EN et repli anglais. ZIP fichiers ajoutés/modifiés et patch cumulatif ; recette HA toujours à faire. |

| 11/11/2026 | **Ajout du lot 8 — Typage progressif avec mypy.** Étude initiale terminée, corrections fichier par fichier à planifier et décision CI après qualification. Les 110 diagnostics WebSocket/services sont suivis séparément. |

## 13. Prochaine étape

**Version 0.3.1 publiée le 08/11/2026, installée et validée en production le 09/11, reprise eedomus et export XLSX compris.** L6-10 est terminé. **L1-06 est Terminé (22/10/2026)** et **L1-11 est Terminé (26/10/2026)** sur la base des essais réels HA rapportés par l’utilisateur. Les validations L3-06 et L3-07 restent acquises. L3-08 a été qualifié le 24/10 : cache/frontend fonctionnel et droits existants constatés, sans modification des permissions.

1. **L3-10 : terminé le 28/10/2026.** Les six familles retenues ont été validées en HA, dernière en date : Exceptions de calendrier (tous les tests convenus OK). La duplication des Moments planifiés demeure exclue et son bouton supprimé avec confirmation HA. Ne pas confondre validation fonctionnelle et nouvelle publication.
2. **L3-12 : reporté.** Étude d'impact du 24/10 conservée ; attribution des droits de gestion aux utilisateurs nommés et lecture seule pour les autres à rediscuter une fois les autres fonctionnalités finalisées. Ne pas changer les droits actuels.
3. **L6-03 et L6-04 terminés le 29/10.** Non-régression frontend validée ; Black, isort profil black et flake8 conformes ; suite Python locale à 449 tests réussis et 100 % de couverture ; les quatre workflows GitHub Actions (`Lint & Formatting`, `HACS Validate`, `Validate with hassfest`, `Run Tests`) confirmés OK par l’utilisateur.
4. **L6-07 terminé le 30/10 : quatre scénarios validés sur HAOS de test.** Installation vierge, mise à jour 0.2.2 vers état courant, retrait avec conservation et réinstallation, retrait avec suppression volontaire puis configuration vierge. Les validations proviennent des retours utilisateur ; aucun essai destructif en production.
5. **L6-08 — terminé le 09/11 :** versions 0.3.0 et 0.3.1 publiées le 08/11 ; 0.3.1 installée en production le 09/11. Publication indépendante des contrôles détaillés post-installation.
6. **L6-10 — terminé le 09/11 :** fonctionnement global de la 0.3.1, reprise eedomus et export XLSX validés en production selon retour utilisateur. Reprendre les contrôles si une nouvelle version modifie ces fonctionnalités.
7. **Lot 7 — clôturé le 11 novembre 2026 :** localisation HA internationale, cache persistant, fêtes informatives et exceptions assistées validés. Conserver la non-régression ; aucune tâche de réalisation restante dans ce lot.
8. **L3-11 et L2-02 :** conserver respectivement la création guidée des moments et l'éventuel affichage des métadonnées dans les écrans, sans les confondre avec L3-10.

Les validations manuelles d’octobre, dont L6-03 le 29/10, ne comptaient pas comme de nouveaux tests automatisés. **Une nouvelle exécution complète Python a ensuite été communiquée par l’utilisateur le 29/10 : 449 tests réussis, 2 154 instructions, 100 % de couverture. Les quatre workflows CI ont ensuite été confirmés OK le même jour.**

Les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. L3-10 est clôturé, mais les tâches reportées ou à planifier du lot 3 et la qualification finale du lot 6 restent distinctes.

Le ZIP de travail historique du 28/10 contenait un `manifest.json` en 0.2.3 ; il ne représente plus la publication courante. **Dernière publication vérifiée : 0.3.1 sur GitHub (08/11/2026) ; installation et fonctionnement en production confirmés (09/11/2026), notamment reprise eedomus et export XLSX.** Les jalons historiques 0.2.0–0.2.4 et 0.3.0 sont conservés. L’audit métier est implémenté et validé **après la publication 0.2.0**, sans être déclaré livré dans cette dernière. Le lot Metadata reste ouvert pour l’éventuel affichage détaillé ; horaires avancés et calendrier externe conservent leurs statuts. L’i18n reste non prioritaire ; les traductions existantes sont conservées.


## Décision de clôture — 11 novembre 2026

**Clôture du lot 7.** L7-07 confirmé « Validé », puis recette finale HA confirmée « j’ai testé ok ». Roadmap et documentations actualisées ; aucune nouvelle publication.
