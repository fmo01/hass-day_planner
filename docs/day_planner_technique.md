# Day Planner — Documentation technique

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

### Détails techniques L7-06

`_saveCreateCalendarException()` applique désormais la validation de date et d’unicité aux ajouts ordinaires comme aux duplications. Les méthodes de création et de modification contrôlent l’appartenance du `day_type_id` à la configuration chargée avant l’appel API. Les brouillons sont renseignés avant la validation, ce qui conserve les champs lors du rendu d’une erreur. Le verrou `_loading` existant protège les soumissions et les gestionnaires d’annulation ; les deux boutons Annuler sont également désactivés dans le HTML pendant la requête.

Aucune logique backend de production n’a été modifiée : `PlannerValidator` valide avant remplacement de la configuration, `PlannerEngine` gère déjà l’audit, et les commandes WebSocket transmettent déjà `connection.user.name or connection.user.id`. Les tests supplémentaires du moteur couvrent un ajout à une date déjà occupée, un ajout avec type inconnu et une modification avec type inconnu, en vérifiant la conservation de l’objet de configuration et de l’exception originale.

## L7-05 — Description proposée à la création d’une exception (11 novembre 2026)

L7-04 est validé par l’utilisateur : pytest OK et tests IHM OK sur HA. L7-05 a ensuite été validé sur HA par l’utilisateur.

La commande Ajouter une exception reste le point d’entrée. À son ouverture sur un jour férié dont les données sont disponibles pour le contexte courant, la description est préremplie avec le nom de la fête. Plusieurs noms à la même date sont réunis par « / ». Aucun préfixe en dur n’est ajouté : les noms proviennent des données de jours fériés déjà traduites selon la configuration HA. La description reste modifiable et peut être effacée. Le type de journée doit être choisi explicitement.

Sur une date ordinaire ou lorsque les données sont absentes, en erreur ou devenues obsolètes après un changement de lieu, la description initiale reste vide. Une réponse reçue après l’ouverture du formulaire ne réécrit pas la saisie. Les réserves locales affichées par L7-04 restent consultables dans les détails du jour.

L’examen du code confirme que Modifier existe déjà : il réutilise le type de journée et la description enregistrés, en conservant la date. Aucun second bouton n’est ajouté. Une duplication conserve la description de la source. L’ouverture du formulaire ne crée aucune exception ; l’enregistrement reste explicite et l’annulation utilise le parcours existant.

Validation : **699 tests pytest réussis**, incluant un test lançant **20 tests JavaScript réussis** ; **3 407 instructions Python couvertes sur 3 407 (100 %)**. Les cinq avertissements de dépendances restent inchangés. La couverture Python ne mesure pas le JavaScript. Les tests JS ajoutés couvrent les noms multiples, les données absentes/obsolètes, l’échappement HTML, les réponses tardives, la description personnalisée ou effacée et la conservation de la date/description en modification et duplication. Les validations transversales détaillées restent au périmètre L7-06.

### Implémentation L7-05

`_openCreateCalendarExceptionDialog(date)` initialise un brouillon une seule fois depuis `_currentPublicHolidays()`, qui exclut les réponses ne correspondant plus au contexte. Le gestionnaire du bouton Ajouter appelle cette méthode. Le formulaire et l’enregistrement existants consomment ensuite le brouillon et la saisie utilisateur. Les chemins Modifier et Dupliquer restent distincts et ne calculent pas de suggestion. Aucun changement backend ni nouvelle clé de traduction : aucune nouvelle phrase d’interface n’est introduite. Version console de la carte : 0.2.11.

## L7-04 — Jours fériés dans le calendrier (11 novembre 2026)

L7-03 est validé par le retour utilisateur au redémarrage. Le cache de Montreuil / Seine-Saint-Denis a été relu avec `from_cache: true`, `resolved_at` conservé à 15:30:18 UTC et `last_evaluated` actualisé à 15:36:36 UTC. Le fichier de stockage est resté inchangé pendant cette lecture.

L7-04 affiche un repère avec icône et nom pour les jours fériés de l’année consultée. Le pays et la subdivision disponibles figurent au-dessus du calendrier, avec la portée du calendrier retenu. Le type de journée et les exceptions restent visibles à côté du repère. Le nom complet, la portée nationale/locale et les réserves sont repris dans les détails de la date sélectionnée. Les avertissements locaux, dont le Vendredi saint en Alsace-Moselle, sont ainsi consultables dans les détails.

Sur ordinateur, le survol affiche les informations complètes. Les cases possèdent un libellé accessible et un état de sélection. Au clavier, la sélection d’une date conserve le focus sur la case. Sur petit écran, le libellé peut être tronqué et le texte complet est accessible en sélectionnant le jour. Les états de chargement, les limites de couverture et les erreurs s’affichent au-dessus du planning. Une erreur de consultation propose « Réessayer ».

Les nouveaux textes d’interface utilisent `frontend/translations/fr.json` et `en.json`. Les noms des fêtes proviennent de l’action backend dans la langue configurée de HA, avec le repli déjà défini dans L7-02. L’affichage recharge les données lors d’un changement d’année ou de contexte géographique. Une réponse obsolète est ignorée, y compris lors d’une navigation rapide entre mois.

Validation locale effectuée avec **699 tests Python réussis et 3 407 instructions couvertes sur 3 407 (100 %)**, dont un test qui lance **15 contrôles JavaScript réussis**. La couverture indiquée concerne le backend Python. Les contrôles JavaScript valident la consultation, le rendu HTML, les traductions, les changements de contexte, les erreurs/reprises et l’échappement des textes. La recette visuelle dans HA reste à faire, car le navigateur de vérification n’a pas pu accéder à l’aperçu local. Les contrôles de syntaxe JS et de lint du test Python passent. Les statistiques sont régénérées avec le workflow existant.

La livraison est incrémentale depuis L7-03. Elle comprend les fichiers modifiés et un patch alternatif. Après installation, recharger complètement la page du navigateur, puis vérifier des mois avec fêtes nationales et locales, une date avec exception, le passage décembre/janvier, les détails au clavier et l’affichage mobile.

### Raccordement frontend

`DayPlannerApi.getPublicHolidays(year)` utilise le WebSocket natif HA `call_service` avec `day_planner.get_public_holidays` et `return_response: true`. La réponse `response` est conservée pour l’année et le contexte affichés. Le chargement des fêtes est indépendant de celui du planning. Un compteur de requêtes et une comparaison du contexte écartent les réponses obsolètes.

Le contexte inclut l’année, les langues de l’interface et de HA, le pays/les coordonnées configurés, `zone.home` et l’état du capteur de localisation. La recherche du capteur tolère un renommage de l’entité en utilisant ses attributs Day Planner. Le calendrier fonctionne aussi lorsque le capteur est absent, avec les codes de zone retournés par le calcul. Les données annuelles sont réutilisées tant que le contexte correspond. Les nouveaux noms et messages sont échappés avant insertion dans le HTML.

`test_calendar.py` lance `scripts/tests/frontend/calendar.test.mjs` lorsque Node.js 22+ est présent. L’absence de cette dépendance de test est signalée par un test ignoré. La navigation des mois et les chargements de traductions sont également protégés contre les réponses arrivant dans le désordre.

## L7-03 — Cache persistant de la localisation (11 novembre 2026)

L7-02 a été validé par l’utilisateur sur son installation Home Assistant. L7-03 a ensuite été validé au redémarrage sur l’installation de l’utilisateur.

Day Planner conserve la dernière localisation résolue dans `/config/.storage/day_planner_location`. Au redémarrage, il la réutilise si le pays et les coordonnées du domicile HA correspondent et si la résolution date de moins de 30 jours. Le capteur `binary_sensor.day_planner_location` indique alors `from_cache: true`. `resolved_at` conserve la date de résolution et `last_evaluated` indique la nouvelle évaluation.

À l’expiration ou lors d’un changement de lieu, une nouvelle résolution est déclenchée si aucun cache utilisable ne correspond. En cas d’échec réseau ou HTTP, un nouvel essai a lieu une heure plus tard. Un échec laisse le dernier résultat réussi sur disque. Le planning et les exceptions enregistrées restent utilisables. Les dates de jours fériés se calculent localement pour l’année demandée.

Validation locale avec Python 3.14.10 et HA 2026.10.4 : 698 tests réussis et 100 % de couverture (3 407 instructions). Le test de redémarrage utilise un fichier créé par le véritable stockage HA et deux instances successives. Le réseau est simulé.

Le fichier JSON utilise `Store` de HA avec le schéma de stockage 1, le mode privé et des écritures atomiques. Le contenu comprend le pays configuré, les coordonnées, le pays résolu, les subdivisions, la localité, la source, l’attribution et l’horodatage de résolution. Le pays et les coordonnées comparés sont ceux utilisés pour la requête de géocodage, avec les coordonnées de `zone.home` lorsqu’elles sont disponibles. La durée de validité part de la résolution et la lecture du cache ne la prolonge pas.

Un cache expiré, invalide ou lié à un autre domicile est ignoré. La résolution est publiée en mémoire avant la sauvegarde. Les écritures d’un même résolveur sont sérialisées si le lieu change pendant une écriture. Le minuteur est annulé à la désactivation de l’intégration et remplacé à chaque évaluation. Les échecs de lecture ou d’écriture laissent la résolution en mémoire utilisable.

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


**Contexte historique : version 0.2.0, documentation initiale du 22 octobre 2026 : journalisation du 20 octobre conservée ; généralisation de la traçabilité `Audit` et validations fonctionnelles Home Assistant des 21–22 octobre intégrées. Il ne s’agit pas d’une nouvelle publication.**

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

**Rapport historique complet chiffré communiqué le 21 octobre 2026 : 449 tests réussis, 5 avertissements, 2 146 instructions Python mesurées, aucune non couverte, 100 % de couverture globale (Python 3.14.3, 1,67 s).** L’utilisateur a ensuite confirmé les tests au fil des adaptations Options Flow et les contrôles HA, durant cette période historique. Un rapport plus récent, daté du 7 novembre 2026, est indiqué dans la mise à jour du 8 novembre. La suite n’a pas été exécutée intégralement par l’assistant.

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

## 19. Reprise eedomus : architecture et contrôles de sécurité (v5.16)

| Module | Rôle |
| --- | --- |
| `eedomus_agenda_extract.py` | Chargement et extraction du JSON eedomus, jours, phases, horaires, actions et limites. |
| `eedomus_import.py` | Construction du plan d’import, association au registre HA, conversions, exclusions, nouveaux identifiants et fusion validée. |
| `options_flow.py` | Choix de la box active et du JSON navigateur, prévalidation, confirmation, appel à la persistance et génération de liens d’export. |
| `eedomus_download.py` | Routes HTTP temporaires pour CSV et XLSX, jetons et signature Home Assistant. |
| `eedomus_excel.py` | Construction du classeur OOXML XLSX en mémoire avec les 7 feuilles ; protection contre les chaînes interprétées comme formules. |
| `planner/engine.py` | Application de la configuration fusionnée uniquement après validation. |

### Identification des box et des périphériques

Les entrées sont obtenues par `hass.config_entries.async_entries("eedomus")`. La box sélectionnée doit être activée (`disabled_by is None`) et chargée (`ConfigEntryState.LOADED`). Le nom de provenance `Eedomus (<api_host>)` sert aux **noms ET IDs des nouveaux objets Day Planner**. Le `entry_id` demeure une clé de rattachement technique au registre des entités Home Assistant, sans modification de ses `unique_id`.

Pour un numéro de périphérique eedomus, la recherche peut reconnaître les quatre variantes de `unique_id` associées à l’entrée sélectionnée : `eedomus_<entry_id>_<numéro>`, `eedomus_<entry_id>_<numéro>_<suffixe>`, `<entry_id>_<numéro>` et `<entry_id>_<numéro>_<suffixe>`. Les entités de diagnostic dont le suffixe contient le segment `battery` sont ignorées. On ne réutilise pas d’anciens enregistrements orphelins d’une autre `config_entry`.

Les domaines actuellement convertis en actions sont `climate`, `cover`, `switch`, `light` et `input_boolean`, selon des valeurs reconnues. Les autres associations (par exemple `sensor`) restent **informatives et non bloquantes** ; elles ne génèrent pas d’action. Un moment sans action reste valide et conserve ses `scheduled_moments`. Les cibles absentes, désactivées ou ambiguës sont contrôlées séparément et peuvent interrompre la prévalidation.

### Téléversement, écriture et export

Le fichier JSON choisi via `selector.FileSelector` et l’intégration HA `file_upload` est lu puis supprimé de l’espace temporaire ; aucun fichier d’import n’est requis dans `/config`. Les objets ne sont persistés qu’après confirmation et validation. Le remplacement est limité aux créations antérieures de la même box, y compris les anciens identifiants pré-v5.5 après confirmation explicite ; conserver les objets manuels et les autres box.

Les routes `GET /api/day_planner/eedomus_associations.csv` et `.xlsx` servent respectivement un CSV et un classeur XLSX. Leurs liens sont signés temporairement par Home Assistant et associés à un jeton aléatoire ; les rapports sont générés en mémoire, sans fichier sous `/config/www`. L’export **n’exécute aucun service HA** et ne valide pas la reprise. Les sept feuilles et leurs contenus sont décrits dans [export_xlsx_eedomus.md](export_xlsx_eedomus.md).

### Tests et suivi

Le code de production v5.16 et ses tests existants ont produit **517 tests réussis, 92 %** sur le dernier rapport complet communiqué. Un correctif complémentaire ajoute **55 tests** dans `test_eedomus_agenda_extract.py` (nouveau), `test_eedomus_import.py`, `test_eedomus_excel.py` et `test_options_flow.py`. Les 90 tests ciblés ont été contrôlés dans un environnement de préparation isolé ; la mesure de couverture complète **reste à confirmer** sur la machine de développement avec Home Assistant installé. Aucun `pragma: no cover`, `coverage omit` ou seuil `--cov-fail-under=100` n'est introduit.

La gestion fine des droits HA des gestionnaires désignés reste reportée ; cette évolution ne doit pas être confondue avec un renforcement déjà validé des permissions. Voir [qualification_couverture.md](qualification_couverture.md) et la [roadmap](ROADMAP.md).

## 20. Jours fériés régionaux — résolution géographique L7-01

**Décision technique du 9 novembre 2026 : méthode retenue, non implémentée et non testée dans HA à ce stade.** Évolution du lot 7 (ancienne référence historique L3-14). Les noms de champs et états ci-dessous décrivent le contrat à prévoir, pas une API déjà livrée.

### Entrées et résolution

L’adaptateur Home Assistant devra lire la latitude, la longitude et le pays du domicile à partir des données de configuration HA. La lecture exacte et la prise en compte des modifications du domicile devront être vérifiées avec la version HA cible avant codage. Aucun accès direct aux fichiers internes `.storage` ni nouvelle saisie de lieu dans Day Planner n’est prévu.

**Méthode initiale FR, à reprendre pour le périmètre international :** le prototype utilise en HTTPS l’API publique de découpage administratif :

```text
GET https://geo.api.gouv.fr/communes?lat=<latitude>&lon=<longitude>&fields=nom,code,codeDepartement
```

La réponse permettra de conserver pays, nom et code INSEE de commune, code département, coordonnées sources et état de résolution. Il faudra contrôler la validité des coordonnées, la réponse HTTP, son format et l’unicité d’un résultat exploitable. Une absence de résultat ou une réponse ambiguë ne doit pas conduire à choisir arbitrairement une commune. La langue et le fuseau horaire ne déterminent pas la zone régionale.

Cette API couvre la résolution géographique ; elle ne calcule pas les jours fériés. Les règles nationales, régionales et particularités locales relèvent de L7-02. Le support dépend désormais du lieu de l’installation HA ; le fournisseur géographique international reste à choisir et à vérifier.

### Cache, réseau et changements de localisation

- Prévoir un appel asynchrone avec délai maximal et gestion des erreurs, sans bloquer le fonctionnement du planificateur.
- Mémoriser le résultat avec les coordonnées ayant permis sa résolution pour éviter les requêtes à chaque consultation. Le support de persistance et la stratégie de renouvellement restent à préciser lors de l’implémentation.
- À la modification de la localisation HA, invalider l’association précédente et relancer la résolution. Un ancien résultat ne peut être réutilisé que s’il correspond aux coordonnées actuelles.
- Sans résultat exploitable, exposer un état non résolu pour permettre le message fonctionnel « Zone des jours fériés non déterminée », sans modifier les cycles ou exceptions existants.
- Documenter le transfert des coordonnées à `geo.api.gouv.fr` : la résolution initiale dépend du réseau. Ne pas présenter l’ensemble du dispositif comme intégralement hors ligne.

### Séparation et vérifications à prévoir

La résolution géographique appartient à l’adaptateur HA ; elle ne doit pas devenir une dépendance réseau du moteur métier ni provoquer d’écriture d’exception ou d’exécution d’action. Les valeurs exactes des états, le raccordement au runtime, le stockage du cache et la détection des changements restent à définir sur les sources courantes.

Les tests devront couvrir coordonnées valides/invalides, commune unique, résultat absent/ambigu, erreur réseau, cache correspondant ou périmé et changement de localisation. Ils seront ajoutés aux modules existants pertinents ; les résultats réels seront suivis sous L7-07 et L7-08. Ce cadrage n’atteste aucune nouvelle exécution de tests.

### Sources de l’étude

- [Configuration du domicile Home Assistant](https://www.home-assistant.io/docs/configuration/basic/).
- [Objet hass et configuration](https://contributors.home-assistant.io/core/internals/hass/).
- [API Découpage administratif — communes et recherche par coordonnées](https://geo.api.gouv.fr/decoupage-administratif/communes).

## 21. Jours fériés — calcul local L7-02

**Validation utilisateur du 9 novembre 2026 : cadrage L7-02 retenu ; implémentation et tests restent à effectuer.** Le calcul des dates utilisera localement la bibliothèque Python `holidays`, déjà employée par l’intégration Holiday de Home Assistant. Le calcul ne nécessite pas de requête Internet ; la résolution géographique initiale de L7-01 reste dépendante du réseau.

**Exemples français parmi les correspondances internationales à prévoir :**

| Territoire résolu dans L7-01 | Calendrier à utiliser |
| --- | --- |
| Métropole hors Alsace-Moselle | France (`FR`), sans subdivision |
| Moselle, département 57 | France (`FR`), subdivision `57` |
| Bas-Rhin et Haut-Rhin, départements 67 et 68 | France (`FR`), subdivision Alsace `6AE` |

Les jours nationaux et le 26 décembre en Alsace-Moselle seront affichés. Les jours fériés tombant le week-end seront conservés. Le Vendredi saint sera accompagné de la mention **« application locale à vérifier »** lorsque la condition communale n’est pas établie ; le département seul ne suffit pas à confirmer cette condition. La règle légale vise les communes ayant un temple protestant ou une église mixte. Le choix utilisateur ne signifie pas que cette vérification communale est déjà automatisée.

Aucun affichage ne modifiera le programme ni ne créera d’exception automatiquement. Le choix explicite d’un type de journée et l’enregistrement de l’exception restent nécessaires. Les autres pays et territoires font partie de la cible, selon la couverture réelle des sources et de la version de holidays installée.

### Intégration et vérifications restantes

- Vérifier la version de `holidays` compatible avec la version HA cible et ses subdivisions ; préciser la dépendance dans le manifeste lors de l’implémentation. Ne pas supposer que l’installation de l’intégration Holiday est un prérequis.
- Conserver la distinction entre résolution géographique réseau et calcul local des dates. La bibliothèque ne résout pas la condition communale du Vendredi saint à partir des coordonnées.
- Prévoir les noms français et l’adaptation des libellés aux interfaces existantes ; conserver les noms multiples en cas de coïncidence de fêtes à la même date.
- Comparer les dates fixes et mobiles sur plusieurs années aux données publiques data.gouv.fr, pour la métropole et l’Alsace-Moselle ; inclure les week-ends et le changement d’année. Ces tests n’ont pas encore été exécutés.
- Les données publiques constituent une référence de comparaison ; elles ne sont pas une seconde source réseau obligatoire au fonctionnement quotidien.

### Sources de référence

- [Home Assistant — Holiday](https://www.home-assistant.io/integrations/holiday/).
- [Bibliothèque holidays — France et subdivisions](https://holidays.readthedocs.io/en/latest/auto_gen_docs/france/).
- [data.gouv.fr — Jours fériés en France](https://www.data.gouv.fr/datasets/jours-feries-en-france).
- [Légifrance — dispositions Alsace-Moselle, dont article L3134-13](https://www.legifrance.gouv.fr/codes/id/LEGIARTI000006902635/2026-03-23).

## 22. Cache, actualisation et cas non résolus — L7-03

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

### Points d’implémentation et de contrôle

Le format persistant, son emplacement et son raccordement au runtime seront définis sur les sources courantes. Une réponse réseau ne devra être appliquée que si elle concerne toujours la localisation active ; le mécanisme exact de protection contre les réponses obsolètes reste à implémenter. L’ordonnancement et l’arrêt des nouvelles tentatives devront respecter le chargement et le déchargement de l’intégration.

Les futurs tests devront distinguer redémarrage avec cache correspondant, cache d’un ancien lieu, changement de localisation pendant une requête, échec réseau avec ou sans résultat utilisable, localisation absente/ambiguë et territoire non couvert. Vérifier aussi la navigation entre années, le passage à la nouvelle année sans résolution géographique inutile et la conservation des exceptions. Aucun résultat de test n’est attribué à cette validation de cadrage.

## 23. Affichage des jours fériés — L7-04

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

### Mise en œuvre et vérifications restantes

Le rendu devra juxtaposer l’information fériée et le programme résolu sans changer la priorité des exceptions. Prévoir les informations de nom complet, portée et réserve d’application locale nécessaires à l’affichage ; le contrat API et les composants concernés seront précisés sur les sources frontend courantes. La zone affichée ne doit pas être calculée depuis la langue de l’interface.

Les contrôles devront couvrir une date fériée avec et sans exception, la visibilité du programme, la zone non résolue, le Vendredi saint et l’accès au texte complet sur ordinateur, au clavier et sur mobile. L’accès aux détails ne doit pas reposer uniquement sur le survol. Les libellés et versions des fichiers JS seront traités lors des modifications selon les conventions existantes. Aucun contrôle syntaxique, test automatisé ni essai HA de cet affichage n’a encore été réalisé dans ce cadrage.

## 24. Gestion des exceptions — L7-05

**L7-05 implémenté et testé le 11 novembre 2026 ; recette IHM HA à effectuer.** La commande « Modifier » était déjà présente et est conservée. L’ajout propose désormais les noms des fêtes dans la description ; aucun bouton propre aux jours fériés n’est ajouté.

| État du jour sélectionné | Actions concernées par ce cadrage |
| --- | --- |
| Sans exception | Ajouter une exception avec la commande actuelle. |
| Avec une exception | Modifier et Supprimer ; conserver la suppression actuelle. |

« Modifier » ouvrira le formulaire prérempli avec le type de journée et la description enregistrés, en conservant la date sélectionnée. Il s’agit de modifier l’exception existante, sans en créer une seconde. Les autres commandes déjà validées ne sont pas retirées par ce cadrage.

Pour l’ajout sur une date fériée, préremplir la date sélectionnée et proposer une description modifiable, par exemple « Jour férié : Noël ». Le type de journée restera à choisir explicitement. Lors d’une modification, conserver la description existante ; ne pas la remplacer automatiquement par le nom du jour férié.

La réserve « Application locale à vérifier » du Vendredi saint restera présentée dans les informations du jour lorsque nécessaire. L’ouverture du formulaire ne provoquera aucune écriture ; l’enregistrement nécessitera la validation de l’utilisateur et une annulation restera sans modification. Les validations détaillées et le comportement d’enregistrement retenus dans L7-06 sont décrits ci-dessous.

### Mise en œuvre et vérifications restantes

Examiner les sources courantes de la vue Calendrier et du formulaire pour réutiliser les traitements existants. La modification devra cibler l’identité de l’exception existante et conserver la date ; le préremplissage proposé pour une création fériée ne doit pas écraser les valeurs enregistrées en édition. Le contrat API et le raccordement des commandes seront précisés avant codage. Les règles d’audit existantes devront s’appliquer à la modification.

Vérifier les parcours Ajouter/Modifier/Supprimer, les valeurs préremplies, la conservation d’une description personnalisée, l’annulation sans écriture et l’absence de doublon. Vérifier aussi le maintien des autres commandes déjà validées, ainsi que l’accès clavier/mobile. Aucun code ni résultat de test de cette évolution n’est validé par le présent cadrage.

## 25. Formulaire et enregistrement — L7-06

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

### Raccordement et contrôles à prévoir

Réutiliser les validations et la chaîne de persistance, notification et replanification existantes. Le contrôle d’unicité à la création doit aussi être effectué lors de l’enregistrement, pour traiter une exception apparue après l’ouverture du formulaire. L’édition doit modifier l’objet existant sans suppression/recréation ; elle ne doit pas réinitialiser son audit de création. Appliquer les règles actuelles d’auteur, notamment le nom affiché HA lorsqu’il est disponible, sans migration des historiques.

Normaliser la description facultative vide selon le contrat existant, sans transmettre de valeur incompatible avec son schéma. Conserver les valeurs du formulaire après une erreur plutôt que les reconstruire depuis les valeurs initiales ; rendre l’enregistrement de nouveau disponible une fois l’erreur traitée. Aucun nouveau contrat API ni code n’est déclaré livré par cette décision.

Les futurs contrôles couvriront : type absent ou devenu invalide, création sur une date occupée, description vide/personnalisée, édition sans changement de date ni d’identité, conservation de l’audit de création et actualisation de l’audit de modification, doubles clics, erreur puis correction, annulation et Échap, actualisation après réussite et non-régression de la suppression. Les tests pertinents seront intégrés aux modules actuels ; leurs résultats seront consignés sous L7-07/L7-08.

## 26. Plan de tests et qualité — L7-07

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

### Organisation et preuves attendues

Rattacher les cas aux modules réellement modifiés, sans créer une structure de tests parallèle. Utiliser des réponses géographiques simulées et des dates déterministes ; comparer les calendriers sur plusieurs années avec les références publiques retenues sous L7-02. Distinguer les vérifications automatisables des parcours frontend et des essais HA ; la couverture Python ne mesure pas la couverture JavaScript.

Consigner la version du code contrôlé, l’environnement, les commandes exécutées, les résultats, la couverture et les avertissements. Employer les contrôles de qualité effectivement configurés dans le dépôt au moment de l’implémentation. Ne pas introduire de seuil `--cov-fail-under=100` ni masquer du code pour obtenir le résultat attendu. Les comportements à vérifier ont été validés ; aucun nouveau rapport chiffré n’est produit à cette étape.

## 27. Essais réels HA et documentation finale — L7-08

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

### Traçabilité de la recette

Identifier la version ou le commit du code testé et la version HA ; distinguer le résultat des essais réels des rapports automatisés L7-07. Les anomalies devront rester visibles jusqu’à leur correction et leur nouvelle vérification. Actualiser les descriptions de configuration, dépendances, données persistantes, API et interfaces selon l’implémentation constatée. Ne pas déduire une publication ou une validation en production de la seule réussite d’un essai sur l’instance de test.

### Première implémentation L7-01 préparée le 9 novembre 2026

Base : dépôt `fmo01/hass-day_planner`, branche `main`, commit `0562541cbd339041d46aeb8267971630f32a1f0c` (version publiée 0.3.1). Modifications locales préparées ; aucune publication ni installation HA réelle de ce correctif n’est affirmée.

Le nouveau module `holiday_location.py` lit le pays et les coordonnées courants du domicile HA et interroge `geo.api.gouv.fr` avec la session HTTP partagée et un délai maximal de 10 secondes. Il accepte une commune unique et valide son nom, son code INSEE et son département. Il distingue les états résolu, non résolu et territoire non pris en charge. Les coordonnées invalides, réponses ambiguës ou mal formées, erreurs HTTP/réseau et annulations sont contrôlées. La résolution du territoire ne calcule pas encore les dates fériées.

Le résolveur est disponible dans les données d’exécution (`runtime_data.holiday_location`). Cette première étape ne lance pas de requête au chargement : l’appel sera raccordé au cycle de vie sous L7-03. Cache persistant, reprises et détection automatique des changements de lieu restent à implémenter dans L7-03 ; calcul des dates sous L7-02 et affichage sous L7-04 également à réaliser. Aucun repère férié n’est encore visible dans le calendrier et aucune exception n’est modifiée par ce code.

**Vérifications exécutées :** 44 nouveaux cas intégrés à `scripts/tests/test_runtime.py`, plus contrôle du raccordement dans `test_init.py` ; suite complète **616 tests réussis**, **3 058 instructions couvertes sur 3 058 (100 %)**, **5 avertissements de dépendances**, en **2,06 s**, avec **Python 3.14.9 et Home Assistant 2026.10.4**. Aucun appel géographique réel dans les tests. Contrôles Black, isort profil black et flake8 (120 caractères) sur les fichiers modifiés réussis. Les statistiques de `scripts/tests/README.md` sont régénérées par le code du workflow existant ; le mécanisme automatique GitHub Actions est conservé. Ces résultats ne constituent pas la recette HA L7-08.

### Contrôles de la future entité de localisation

Prévoir une entité de diagnostic alimentée par les données du runtime et les notifications d’évaluation, sans requête réseau depuis les propriétés de l’entité. Les horodatages seront sérialisés en ISO 8601 avec fuseau ; leur format interne et la présentation HA devront être vérifiés lors de l’implémentation. Le champ `from_cache` restera booléen.

Vérifier les transitions première évaluation → résultat exploitable, échec sans cache utilisable, cache correspondant utilisé, changement de pays ou subdivision, et déchargement. Tester les valeurs et la distinction des deux horodatages, les attributs absents lorsqu’ils sont inconnus et la cohérence de `status`/`reason` avec l’état binaire. L’identifiant final reste soumis au registre des entités HA et à un éventuel renommage par l’utilisateur ; définir un unique_id stable lors du raccordement. Aucun test du capteur n’a encore été exécuté.
