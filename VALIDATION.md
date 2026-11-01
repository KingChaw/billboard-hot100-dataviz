# Finalisation UX du dashboard — 1er novembre 2026

Cette section décrit l’état actuel ; les sections suivantes documentent les
interventions antérieures conservées dans le même worktree non commité.

## Changements et périmètre

- Rubrique principale **Explorer les n°1**, route `summary` et grand titre
  inchangés. Le nom **Vue d’ensemble** de Format reste inchangé.
- Accueil sans sous-navigation Synthèse ; les trois titres et trois frises
  originaux (5 + 2 + 4 étapes) sont identiques par comparaison AST. Le bloc
  Repères chiffrés et tout son contenu après la troisième partie sont retirés.
- Navigation sticky unique et commune aux cinq rubriques ; deux niveaux lorsque
  plusieurs sous-pages existent, un seul sur l’accueil. Défilement horizontal
  interne des barres sur mobile, sans espace de sous-navigation vide à l’accueil.
- Phrase historique récurrente et variantes directement équivalentes retirées,
  sans modifier les calculs, filtres, bornes temporelles, points partiels ou survols.
- Correctif minimal d’un défaut préexistant observé à 320 px : Haut recouvrait
  partiellement le CSV. Placement dans le flux sur les deux pages Données,
  comme dans Format. Retour en haut et téléchargement restent disponibles.

## Vérifications

- Avant modification : **53/53 tests Python**.
- Après le dernier correctif CSS : **56/56 tests**, aucun ignoré ou désactivé.
  Les 53 noms de tests sont conservés ; trois nouveaux tests dans
  `tests/test_final_ux.py`. Assertions obsolètes actualisées : accueil atteint
  par la navigation principale, anciens boutons après la partie 3 retirés,
  effectifs 129/81 contrôlés dans la barre latérale. Tous les raccourcis Format
  restants et leurs filtres restent testés ; aucune assertion statistique supprimée.
- **42 scénarios analytiques comparés avant/après**, tous identiques pour les
  figures JSON complètes, tableaux numériques/HTML et filtres. Les guides sont
  identiques sauf la phrase explicitement retirée de Signature sonore, dont la
  suppression précise est prise en compte dans la comparaison.
- Chrome **156.0.8078.74** réel, serveur 8505, profil isolé CDP 9229 :
  **15 observations initiales**, **63 observations principales après**, puis
  **six contrôles Données après correction** aux tailles **320×844, 390×844 et
  1440×900**. Les observations sont issues de sessions successives documentées.
- Les 14 pages, cinq variantes Format, navigation souris/Entrée, mémoire des
  sous-pages et filtre Pop/1980 sont contrôlés à chaque largeur. Les graphiques
  Format conservent leurs dimensions et largeurs utiles ; les KPI de durée
  restent sur une ligne. Aucun débordement horizontal de page, exception
  Streamlit ou chevauchement des barres observé dans les contrôles finaux.
- Les six contrôles Données défilent réellement les tableaux et téléchargent
  les CSV dans le dossier local de recette. Colonnes, ordre et valeurs sont
  comparés à la sélection attendue (129 et 81 titres), sans toucher aux CSV bruts.

Quand le contenu tient dans la fenêtre, il n’y a pas de défilement vertical de
page à provoquer : navigation visible et règle sticky contrôlées, défilement
du tableau Données vérifié séparément. Aucune page longue simulée.

Accueil, hauteur à filtres identiques :

| Largeur | Avant | Après |
|---|---:|---:|
| 320 px | 4 533 px | 1 779 px |
| 390 px | 3 914 px | 1 322 px |
| 1440 px | 2 354 px | 900 px (tient dans la fenêtre) |

## Intégrité et preuves

Worktree `/private/tmp/billboard-hot100-format-son-ux`, branche `refonte-format-son`,
HEAD toujours `ef4a5bc`. Modifications UX précédentes conservées, `c08a252` exclu.
Les fichiers `analysis.py`, `dashboard_data.py`, `charts.py`, `ui.py`, les deux
CSV, les composants et dépendances sont identiques à l’état initial de cette
mission. Le clone initial conserve sa branche, son état Git et ses 359 empreintes.
Aucun commit, push, merge, reset, rebase ou cherry-pick effectué.

[Bilan](livrables/format-son-ux/finalisation/BILAN.md),
[captures](livrables/format-son-ux/finalisation/CAPTURES.md),
[tests avant](livrables/format-son-ux/finalisation/tests-avant.log),
[tests après](livrables/format-son-ux/finalisation/tests-apres.log),
[Chrome principal](livrables/format-son-ux/finalisation/apres-chrome.json),
[Chrome Données](livrables/format-son-ux/finalisation/tables-chrome.json),
[intégrité](livrables/format-son-ux/finalisation/integrite.json).

Limites : viewports mobiles émulés dans Chrome du Mac, sans téléphone physique
ni VoiceOver. Les journaux intermédiaires gardent les erreurs de recette
(événement Entrée/focus de recherche et attente des anciennes cartes), corrigées
avant les résultats finaux ; ils ne sont pas comptés comme des réussites.

---

# Simplification UX de Format & son — validation antérieure du 1er novembre 2026

Cette section décrit l’intervention précédente. Les validations ci-dessous sont
conservées comme historique de la base `ef4a5bc`.

## Périmètre et intégrité

Worktree isolé : `/private/tmp/billboard-hot100-format-son-ux`, branche
`refonte-format-son`, HEAD `ef4a5bc54fffeaee83a37d38819e44fd2c2c7ead`.
`c08a252` n’appartient pas à son historique. Le clone initial demeure sur
`suite-refonte-profils-creation` à `c08a252`, avec le même état Git et les mêmes
359 empreintes de fichiers, y compris ses livrables non suivis.
Aucun commit, push, merge, rebase, reset ou cherry-pick effectué.

Les deux CSV, `analysis.py`, `dashboard_data.py`, `periods.py`, les conventions
de crédits, les composants de navigation/viewport, les dépendances et
`.gitignore` sont identiques à la base par SHA-256. Les changements hors Format
se limitent à l’habillage des six appels de guides existants : aucun texte
réécrit et aucun guide ajouté. Comparaison de **20 scénarios AppTest hors
Format** avant/après : textes, messages, figures JSON, tableaux, filtres et
boutons identiques, avec deux réglages de genre/années.

## Tests Python

```bash
PYTHONPYCACHEPREFIX=/private/tmp/billboard-pycache python3 -m unittest discover -s tests -v
```

- Avant : **47 tests réussis sur 47**.
- Après : **53 tests réussis sur 53**, aucun test ignoré ou désactivé.
- Les **47 noms de tests initiaux** sont conservés ; six tests UX sont ajoutés
  dans `tests/test_format_ux.py` (modes et mesures, persistance, vocabulaire et
  filtres, autres rubriques, Détails/exports, sélections vides/mesures manquantes).
- Attentes d’interface actualisées dans `test_format_sound.py`,
  `test_regression.py` et `test_improvements.py` : un graphique principal,
  accès explicite à l’historique, colonne « Années couvertes », valeurs sans
  commentaire automatique et infobulles sans écart. Vérifications statistiques
  des valeurs, ratios individuels, quartiles, manques et dénominateurs conservées.

Journaux : [avant](livrables/format-son-ux/tests-avant.log),
[après](livrables/format-son-ux/tests-apres.log),
[inventaire des tests conservés](livrables/format-son-ux/tests-conserves.json).

## Chrome réel et mesures

Chrome **156.0.8078.74**, profil de test isolé, CDP **9229**, Streamlit **8505**.
**15 observations avant, 56 observations après**, aux dimensions **320×844,
390×844 et 1440×900**. Trois observations supplémentaires comparent les styles
calculés des guides Format/Âge : mêmes fond, bordure, padding, police,
interligne, marges et titre à chaque largeur.

Les cinq pages et cinq variantes sont contrôlées à chaque largeur, avec accès
réel à Données B après filtre Pop (36 lignes), une puis deux sélections vides,
historique Non renseigné, clic souris sur la navigation fixe, molette, choix
de mesure et de graphique au clavier. Deux survols réels à 1440 px vérifient
118 BPM et 81/81 exploitables, puis 28/81 titres et la couverture de Guitare,
sans écart affiché. Persistance et toutes les mesures sont aussi testées en Python.
Aucune exception Streamlit ni débordement horizontal observé ; largeur utile
minimale des graphiques **153 px** ; valeurs des KPI de durée sur une ligne aux
trois tailles. Les titres sont sous la navigation au début de chaque page.

Comparaison à filtres identiques, modes par défaut et Détails fermé :

| Largeur | Baisse de hauteur des cinq pages | Baisse de distance de défilement |
|---|---:|---:|
| 320 px | 31,4 à 54,4 % | 52,5 à 72,4 % |
| 390 px | 27,5 à 52,8 % | 48,6 à 72,1 % |
| 1440 px | 16,4 à 56,0 % | 38,3 à 84,3 % |

Défauts rencontrés et corrigés : fixation appliquée au bon conteneur Streamlit,
bouton Haut replacé dans le flux Format pour éviter les recouvrements mobiles,
dates historiques alternées sans déplacer les points, singulier « 1 titre » et
message unique pour deux sélections vides. Les tests ont été relancés après la
dernière modification de style des guides. Les historiques et tous les modes
restent accessibles ; les hauteurs finales incluent le bouton Haut.

`tests/format_browser_qa.mjs` délègue à la recette complète
`tests/format_ux_browser_qa.mjs` (argument `apres`, ou `guides` directement dans
la nouvelle recette). Les contrôles précédents sont adaptés à l’affichage
interactif et à la suppression demandée des écarts ; les survols restent exécutés.

[Bilan complet](livrables/format-son-ux/BILAN.md),
[mesures détaillées](livrables/format-son-ux/HAUTEURS.md),
[captures](livrables/format-son-ux/CAPTURES.md),
[observations Chrome finales](livrables/format-son-ux/apres-navigateur.json),
[styles calculés des guides](livrables/format-son-ux/guides-navigateur.json),
[intégrité](livrables/format-son-ux/integrite.json).

Limites : viewports mobiles émulés dans Chrome du Mac, sans essai sur téléphone
physique ni VoiceOver. La recette Chrome couvre les modes principaux ; les
combinaisons exhaustives de mesures sont couvertes en Python. Les anciens
journaux intermédiaires ne constituent pas la recette finale.

---

# Correction des tests Origines — validation historique du 1er novembre 2026

**Suite complète : 47 tests sur 47 réussis**, dont les **15 tests Format & son**.
Cette section décrit l’intervention antérieure ; les sections suivantes conservent
les validations antérieures, y compris leurs échecs désormais corrigés.

## Périmètre et état initial

Le nouveau clone est resté sur `suite-refonte-profils-creation`, sans changement
de branche, commit, push, merge, rebase ou reset. Les modifications locales
présentes au début ont été préservées. Les empreintes de 107 fichiers ont été
conservées avant toute correction pour contrôler le périmètre.

Commande exécutée avant modification puis après correction :

```bash
PYTHONPYCACHEPREFIX=/private/tmp/billboard-pycache python3 -m unittest discover -s tests -v
```

- Avant : **47 tests, 39 réussis, 1 échec et 7 erreurs**.
- Après : **47 tests, tous réussis, aucun échec, erreur ou test ignoré**.
- Les 47 noms de tests sont identiques avant/après : aucun test supprimé,
  désactivé ou renommé ; aucun mock ajouté pour cette correction.

Journaux : [avant](livrables/origines-tests/tests-avant.log) et
[après](livrables/origines-tests/tests-apres.log).

## Les huit diagnostics initiaux et leurs corrections

Les lignes ci-dessous sont celles de l’état initial, conservé dans le journal
avant correction. Les huit diagnostics proviennent d’attentes obsolètes, sans
bug fonctionnel correspondant dans la navigation ou les calculs de l’application.

| Test | Fichier et ligne initiaux | Message | Attente du test | Interface réelle / cause | Correction et couverture conservée |
|---|---|---|---|---|---|
| `DashboardLayout.test_dates_on_all_pages_and_comparison_tables` | `tests/test_dashboard_layout.py:39` | `KeyError: nav_origin_trend` | Parcours d’une route d’évolution séparée. | **Test obsolète.** Évolution est le mode initial de origins ; il n’y a plus de nav_origin_trend. | ROUTE_CASES parcourt origins en Évolution et Composition ; les contrôles de dates/colonnes/infobulles sont conservés dans les deux modes. |
| `DashboardLayout.test_identical_periods_keep_two_series_and_two_data_pages` | `tests/test_dashboard_layout.py:72` | `KeyError: ticktext` | Composition horizontale avec deux périodes sur Y. | **Test obsolète.** origins ouvre Évolution ; la composition actuelle est verticale, avec les périodes sur X. | Sélection explicite de Composition ; vérification des deux libellés X, des trois traces, des parts identiques, des totaux 81/81, du total de 100 % et des deux pages Données. |
| `DashboardLayout.test_sidebar_filters_and_remembered_subpage` | `tests/test_dashboard_layout.py:27` | `AssertionError: origins != origin_trend` | Entrée de rubrique sur origin_trend. | **Test obsolète.** L’entrée actuelle est origins ; la rubrique mémorise aussi la dernière sous-page. | Attente origins ; aller-retour entre rubriques, mémoire de map, de Porto Rico, du mode Composition et du filtre Pop. |
| `NewJourneys.test_added_modes_and_persistent_indicators` | `tests/test_improvements.py:196` | `KeyError: composition_origins` | Ancien sélecteur Comparaison des périodes. | **Test obsolète.** origins_view propose Évolution et Composition. | Les deux modes sont sélectionnés puis retrouvés après navigation ; contrôle des trois séries et de leur type bar/scatter. Les tests Équipes/Âge sont conservés. |
| `NewJourneys.test_country_comparisons_small_territory_and_empty_b` | `tests/test_improvements.py:172` | `KeyError: country_view` | Ancien choix carte/comparaison et nom du pays dans une légende. | **Test obsolète.** Le classement utilise directement deux séries de barres ; choisir un pays affiche deux cartes chiffrées. | Vérification des barres, du remplacement par les cartes Porto Rico, des parts/comptes/totaux calculés sur les lignes réelles, de la persistance et de B vide, puis retour au classement. |
| `DashboardJourneys.test_default_and_every_route` | `tests/test_regression.py:131 ; go_to():100` | `KeyError: nav_origin_trend` | Route supprimée dans la liste des pages. | **Test obsolète.** Deux sous-pages : origins et map ; Évolution/Composition sont deux modes de origins. | go_to accepte origins_view ; ROUTES utilise les routes actuelles et ROUTE_CASES conserve les deux analyses. Les contrôles de figures, Détails et exports restent actifs. |
| `DashboardJourneys.test_empty_one_or_both_periods_all_routes` | `tests/test_regression.py:187 ; go_to():100` | `KeyError: nav_origin_trend` | Parcours de l’ancienne route avec une ou deux périodes vides. | **Test obsolète.** Les deux analyses vivent dans origins. | Les deux modes sont parcourus avec A vide puis A/B vides ; les contrôles des autres rubriques et des tables Données sont conservés. |
| `DashboardJourneys.test_selectors_persist_across_pages` | `tests/test_regression.py:174 ; go_to():100` | `KeyError: nav_origin_trend` | Un sélecteur origin_metric choisissait une des trois catégories. | **Test obsolète.** Les trois catégories sont maintenant tracées simultanément ; le choix persistant est origins_view. | Vérification des trois noms et types de traces dans les deux modes, de leur persistance, des comptes/parts historiques après filtre Pop et de l’indépendance vis-à-vis des périodes de comparaison. Les sélecteurs Format & son restent testés. |

## Vérifications statistiques conservées et renforcées

Les références numériques existantes et les CSV n’ont pas été modifiés.
Les tests vérifient notamment :

- Les trois catégories géographiques exclusives et les origines inconnues ;
  un fixture explicite associe un titre à chacune des quatre catégories.
- Porto Rico seul classé avec les États-Unis, Porto Rico + France classé Mixte,
  et Porto Rico conservé séparément dans la comparaison des territoires.
- Les titres inconnus maintenus au dénominateur : trois catégories connues
  de 1 titre sur 4 donnent chacune 25 %, avec 3 origines exploitables sur 4.
  Une période entièrement inconnue reste indisponible, pas nulle.
- Les comptes, dénominateurs, parts et couvertures de **chaque décennie**,
  sans filtre puis avec Pop ; première et dernière décennies partielles.
- Les trois courbes simultanées, les périodes A/B identiques, chevauchantes
  ou vides, la persistance des filtres, modes et pays, et les parts par pays.
- L’historique sur tout le corpus filtré par genre, indépendant des deux
  périodes de comparaison ; la composition sur les périodes sélectionnées.
- La non-régression de Format & son, de Profils et création et des tableaux/CSV
  de Données, dans la suite complète.

## Problème fonctionnel supplémentaire trouvé dans le navigateur

Le contrôle réel a trouvé un débordement de **16 px** sur Pays et territoires
à 390 px : la sonde invisible `.st-key-chart_viewport`, placée à x = 16 avec
une largeur de 390, poussait le contenu jusqu’à x = 406. Ce problème est distinct
des huit tests obsolètes. Capture conservée :
[pays-mobile-debordement-avant.png](livrables/origines-tests/pays-mobile-debordement-avant.png).

Correction : deux lignes CSS ajoutées dans `theme.py`, actives uniquement quand
le bouton `nav_map` est sélectionné, qui donnent une largeur nulle à la sonde
et masquent son débordement. Aucun changement de calcul, de données, de route,
de widget ou de graphique. Le retrait de ces deux lignes restitue exactement
l’empreinte initiale de `theme.py` : les styles préexistants sont préservés.

## Contrôles navigateur exécutés

```bash
BILLBOARD_CDP_PORT=9228 BILLBOARD_URL=http://127.0.0.1:8504 node tests/browser_qa.mjs origins
```

**14 observations réussies dans Chrome isolé** : Évolution, Composition,
comparaison des pays et Porto Rico à **1440 × 900, 390 × 844 et 320 × 844**
(12 observations), puis une période étudiée vide et deux périodes vides.
Contrôles des types et noms de séries, des axes, de la persistance du mode et du
pays, des exceptions et du débordement horizontal. Les captures des graphiques
mobile ont été inspectées. Aucun débordement ne subsiste dans ces observations.

Rapport : [verification-navigateur.json](livrables/origines-tests/verification-navigateur.json).
Journal : [navigateur.log](livrables/origines-tests/navigateur.log).
Les paramètres d’URL et de port permettent de réutiliser le serveur local avec
un profil Chrome de test. Les anciens sélecteurs Origines ont aussi été retirés
des parcours du script ; le contrôle courant est disponible par le mode `origins`.

Les modes historiques `scenario` et `suite` du script navigateur n’ont pas été
exécutés pendant cette intervention. Le mode historique `scenario` conserve
encore d’anciens contrôles d’exemples de Format & son ; ses contrôles actuels
restent ceux de `test_format_sound.py` et `format_browser_qa.mjs`, inchangés.
Les contrôles mobiles utilisent l’émulation Chrome, sans téléphone physique.

## Fichiers modifiés pendant cette intervention

- `tests/test_regression.py` : navigation, scénarios, persistance et contrôles statistiques.
- `tests/test_dashboard_layout.py` : modes, mémoire de navigation, axes et périodes identiques.
- `tests/test_improvements.py` : comparaison des pays, Porto Rico, inconnus et persistance.
- `tests/browser_qa.mjs` : routes Origines actuelles, paramètres locaux et mode de contrôle ciblé.
- `theme.py` : règle CSS limitée à Pays et territoires pour le débordement mobile observé.
- `VALIDATION.md` : ce diagnostic et les résultats effectivement obtenus.
- `livrables/origines-tests/` : journaux, captures, rapport navigateur et contrôle d’intégrité.

`app.py`, `analysis.py`, `dashboard_data.py`, `charts.py`, `ui.py`, `periods.py`,
les tests et le script dédiés à Format & son, les CSV et tous les livrables de
la refonte précédente restent identiques à leurs empreintes initiales.
La règle CSS ajoutée dépend exclusivement de la sélection de Pays et territoires.
Voir [integrite.json](livrables/origines-tests/integrite.json).

Aucun problème fonctionnel restant observé dans le périmètre vérifié.
Les avertissements de contexte Streamlit et de dépréciation pandas préexistants
restent visibles dans les journaux ; ils n’ont pas été masqués. `git diff --check`
ne signale pas d’erreur. Aucun commit ni push effectué.

---

# Format & son — 1er novembre 2026

Refonte limitée à **Format & son et sa navigation**, dans le nouveau clone,
sur `suite-refonte-profils-creation`, basée sur `refonte-profils-creation`.
Aucun commit, push, merge ou changement de branche. La correction déjà présente
dans `ui.py` a été conservée.

## Tests exécutés sur cette version

Commande équivalente à celle demandée (`python` est absent de ce Mac) :

```bash
PYTHONPYCACHEPREFIX=/private/tmp/billboard-pycache python3 -m unittest discover -s tests -v
```

- Avant modification : **32 tests ; 1 échec et 7 erreurs**, soit 24 réussis.
- Après refonte : **47 tests ; les mêmes 1 échec et 7 erreurs**, soit **39 réussis**.
- **15 nouveaux tests Format & son réussis**, dont un avec toutes les mesures
  manquantes. Aucun test supprimé ou ignoré ; attentes de navigation et de
  nombre de figures adaptées seulement pour Format & son.
- La suite complète **ne passe donc pas intégralement**. Les huit diagnostics
  préexistants ont été comparés par nom : ils sont identiques avant/après.

Journaux conservés : [avant](livrables/format-son/tests-avant.log),
[après](livrables/format-son/tests-apres.log),
[tests ciblés](livrables/format-son/tests-cibles.log).

Les échecs concernent les attentes anciennes des tests d’Origines :
`nav_origin_trend`, `composition_origins`, `country_view`, les axes de composition
et la page mémorisée `origin_trend`. Ces rubriques et leurs contrôles n’ont pas
été modifiés pour faire passer les tests. Les cas concernés restent dans la suite :

- `DashboardLayout.test_dates_on_all_pages_and_comparison_tables` (sous-cas `origin_trend`).
- `DashboardLayout.test_identical_periods_keep_two_series_and_two_data_pages`.
- `DashboardLayout.test_sidebar_filters_and_remembered_subpage`.
- `NewJourneys.test_added_modes_and_persistent_indicators`.
- `NewJourneys.test_country_comparisons_small_territory_and_empty_b`.
- `DashboardJourneys.test_default_and_every_route` (sous-cas `origin_trend`).
- `DashboardJourneys.test_empty_one_or_both_periods_all_routes`.
- `DashboardJourneys.test_selectors_persist_across_pages`.

## Contrôles statistiques et de périmètre

Les tests couvrent les cinq pages, les sélecteurs, les raccourcis depuis la
synthèse, les routes fusionnées et leur mémoire, les filtres, les périodes
vides/identiques/partielles et la persistance des sélections. Ils vérifient :

- **1 177 titres**, une observation par titre ; empreintes des données brutes
  identiques aux références du dépôt.
- Ratio individuel d’introduction avant médiane ; zéro connu, absence, durée
  nulle ou négative ; médianes et quartiles après filtre.
- Historiques indépendants des deux intervalles de comparaison, mais dépendants
  du genre global ; Q1–Q3 et effectifs recalculés.
- Genres : comptes réels, dénominateurs, co-genres, zéro connu versus période
  entièrement inconnue, catégorie manquante séparée et périodes partielles.
- Instrumentation : parts cumulables, effectifs renseignés, écarts en points,
  absence de delta si un côté manque.
- Exemples issus des lignes filtrées, cibles de quartiles, ex æquo déterministes,
  jusqu’à trois titres distincts ; accès à Données avec filtres conservés.

Les blocs applicatifs d’Origines, de Profils et création et de Données sont
identiques à `HEAD`. Le rapport [statistiques.json](livrables/format-son/statistiques.json)
conserve ces contrôles, les empreintes et les statistiques de référence.
`git diff --check` ne signale pas d’erreur.

## Vérification visuelle

**26 contrôles Chrome réussis** : 24 observations (huit scénarios aux trois
largeurs), sans exception ni débordement horizontal, puis deux survols réels
(médiane du tempo et barres d’instrumentation). Les accès à Données retrouvent
les 81 titres de référence à chaque taille. Les axes, légendes, cartes et
petites largeurs ont aussi été inspectés sur les captures.

Rapport final de Chrome : voir `livrables/format-son/verification-navigateur.json`
et les captures du même dossier. Le script reproductible est
`tests/format_browser_qa.mjs`, avec Streamlit sur 8504 et un Chrome isolé sur
9227. Les dimensions visées sont **1440 × 1000, 390 × 844 et 320 × 844**.
Le bilan final des contrôles navigateur figure dans
[le livrable de refonte](livrables/format-son/BILAN.md).

Les rapports ci-dessous concernent les versions antérieures ; leurs nombres
de tests et descriptions d’interface ne sont pas ceux de cette refonte.

---

# Refonte du dashboard — 25 octobre 2026

**33 tests réussis**, journal : [tests-refonte-dashboard.log](livrables/tests-refonte-dashboard.log).
Commande : `PYTHONPYCACHEPREFIX=/private/tmp/billboard-pycache .venv/bin/python -m unittest discover -s tests -v`.

Les parcours existants utilisent désormais la rubrique puis la sous-page. Les
attentes de présentation ont été adaptées aux dates et aux nouveaux intitulés ;
les références numériques, quartiles, données et contrôles d’export sont conservés.
Cinq nouveaux tests couvrent la barre latérale limitée aux filtres, la mémoire
des sous-pages, les libellés sur les 18 vues, les deux séries lors de périodes
identiques, les dates de sélection même sans résultat et les noms des CSV.

Contrôle manuel réel dans Chrome sur le serveur local `127.0.0.1:8502` :
- Ordinateur : bandeau Billboard, filtres à gauche, deux rangées d’onglets,
  synthèse, évolution musicale et distribution des introductions.
- Mode responsive **390 px** : rangées d’onglets horizontales, accès au dernier
  onglet « Genres », ouverture et fermeture du panneau de filtres, textes et cartes.
- Les widgets et graphes observés affichent les dates des deux sélections.

Les anciens rapports et captures ci-dessous documentent l’interface antérieure.
Le script CDP `tests/browser_qa.mjs` a été adapté à la nouvelle navigation, mais
n’a pas été exécuté pendant cette refonte. La vérification visuelle de cette
intervention a utilisé Chrome par l’interface native.

---

# Validation reproduite — 28 septembre 2026

Ce rapport remplace le rapport de travail précédent, conservé dans
`livrables/avant/v2_locale.zip`. Les résultats ci-dessous ont été exécutés
pendant cette intervention ; ils ne sont pas déduits du précédent VALIDATION.

## Tests automatisés

Commande : `.venv/bin/python -m unittest discover -s tests -v`.

**27 tests réussis**, journal complet : `livrables/tests-apres.log`.
Avant modification, les **15 tests existants** avaient été exécutés avec succès
(`livrables/avant/tests.log`). Les attentes modifiées sont justifiées : référence
B 2020–2024, exports contextuels ajoutés, table HTML à ordre stable et correction
analytique de `analysis.py`. L’empreinte du code de préparation n’est plus figée ;
les références statistiques non concernées restent contrôlées.

Vérifications :

1. Empreintes historiques des deux CSV et de `PROPOSITION.md` inchangées.
   Comparaison directe avec l’archive initiale : données, fond de carte,
   `.streamlit/config.toml`, proposition et dépendances identiques.
2. 1 177 titres, 97 thèmes, bornes 1958-08-04 / 2025-01-11, 81 titres récents,
   un titre en 2025, 16 genres Discogs manquants sur 2020–2024.
3. Collaborations : Simon & Garfunkel (3 titres), KC, Supremes ; groupe/duo
   avec ft., Coldplay & BTS ; ambigu et crédit absent indéterminés. Invité
   instrumentiste distinct de l’association. Audit des 250 lignes candidates.
4. Réglages par défaut, périodes identiques et chevauchantes, navigation avec
   A vide, B vide et deux périodes vides ; aucun blocage de l’autre sélection.
5. Vrais zéros vs indicateurs entièrement manquants, tous les titres au
   dénominateur, crédits inconnus et déduplication des noms.
6. Médianes, Q1/Q3 et effectifs des courbes musicales, auteurs, producteurs,
   samples/interpolations/reprises, avec plusieurs filtres ; périodes partielles,
   trous non reliés et bande coupée. La couverture demandée borne réellement les lignes.
7. Classement équilibré malgré effectifs A/B inégaux, symétrie A/B, période
   vide exclue, données non renseignées visibles.
8. Écart 20 % → 25 % = +5 points ; pas de delta si un côté manque ; textes
   neutres pour valeurs égales/indisponibles et scénario d’intro 10 → 11 s.
9. Compositions exclusives à 100 %, inconnus inclus ; pratiques cumulables
   séparées ; carte à échelle commune, tous les ISO et Porto Rico.
10. Tous les parcours initiaux, raccourcis, modes ajoutés, filtres et sélecteurs
    persistants. Réglages décennies/intervalles indépendants.
11. Table/export : mêmes colonnes, lignes, ordre et valeurs, y compris les
    tableaux contextuels son/instrumentation/origines/équipes/collaborations/
    réutilisation. Manquant : libellé « Non disponible » dans la table, cellule
    vide dans le CSV. Les booléens dérivés ont les mêmes libellés français.
12. Boîtes Plotly : Q1/ médiane/Q3 explicitement transmis, conformes à pandas.
    Contrôle de non-régression ciblé sur les intros 2010–2019 et 2020–2024.

Les avertissements `missing ScriptRunContext` sont émis par l’environnement de
test Streamlit, pas des exceptions de l’application. Une dépréciation pandas
sur le remplissage d’un tableau vide peut figurer dans le journal ; la borne
`pandas<3` est conservée. Aucun nouvel avertissement de qualité n’est masqué
dans l’interface.

## Références recalculées

| Période | Titres | Durée médiane (s) | Intro médiane (s) | Q1–Q3 intro (s) |
|---|---:|---:|---:|---|
| 1958–1969 | 226 | 161,5 | 9 | 6–14 |
| 1990–1999 | 140 | 250 | 20 | 14–31 |
| 2000–2009 | 129 | 235 | 17 | 12–23 |
| 2010–2019 | 116 | 223 | 10 | 6,75–15 |
| 2020–2024 | 81 | 200 | 11 | 7–18 |
| 2020–janv. 2025 | 82 | 200 | 10,5 | 7–17,75 |

Le défaut A = 2000–2009 a été conservé ; le scénario A&R choisit explicitement
2010–2019. Les paroles non anglaises sont bien 3/226 et 4/81 pour les références
demandées. Les chiffres des collaborations, modifiés intentionnellement,
sont détaillés dans `livrables/AUDIT_COLLABORATIONS.md`.

## Vérification réelle dans le navigateur

Serveur Streamlit local sur 127.0.0.1:8502 ; Chrome headless avec profil de test
isolé et interface CDP locale. Script conservé : `tests/browser_qa.mjs`.
Aucune publication ni utilisation d’un compte navigateur personnel.

- Parcours de **18 vues** (synthèse, 15 analyses, 2 pages de données), à
  **1440 × 900, 390 × 844 et 320 × 844** : aucune exception et aucun débordement
  horizontal de la page. Le défilement vertical est assumé ; les grands
  tableaux défilent dans leur propre cadre.
- Modes des équipes, des pratiques, carte/comparaison, sélection de Porto Rico
  et compositions alternatives parcourus ; captures à l’appui.
- Fond géographique réellement dessiné depuis `static/world_110m.json`.
  L’échelle commune est vérifiée par les tests ; les petites îles restent
  accessibles par repère et sélecteur.
- Contrôle visuel des titres, légendes, unités, barres et axes sur les captures.
  Un titre d’axe trop long à 320 px a été raccourci ; hauteur des barres augmentée
  pour éviter de comprimer les catégories. Un problème de persistance des
  dimensions du composant lors du redimensionnement a été corrigé : seules
  les préférences, pas l’état des composants graphiques, sont conservées.
  Le script vérifie l’inclinaison de l’axe temporel aux deux petites largeurs.
- Survol réel du losange B de l’intro : « Médiane : 11 s », « Moitié centrale :
  7–18 s », « Moustaches : 0–27 s », « Exploitables : 81 / 81 titres ».
  Les anciens termes anglais de l’infobulle native de boîte ont été remplacés.
- Aide de légende : focus puis touche Entrée, et activation tactile simulée,
  réussis. Navigation et bouton Retour en haut : position principale remise à 0.
- Simulations Chrome **deutéranopie, protanopie, tritanopie** enregistrées.
  Le texte sombre des segments reste lisible ; les catégories gardent leurs
  libellés et leur ordre. Calcul sRGB : contraste minimal 4,68:1 pour ce texte,
  détails dans `livrables/contrastes.json`.
- Téléchargement réel du CSV des trois exemples récents : même ordre, colonnes
  et valeurs que les cellules rendues, avec convention explicite des manquants.

Rapports : `livrables/verification-navigateur-suite.json`,
`livrables/verification-navigateur-scenario.json` et captures dans
`livrables/captures/`. Le rapport `verification-navigateur-ajustements.json`
documente une passe intermédiaire ; la suite finale est la référence pour
le redimensionnement.

## Scénario A&R exécuté par l’agent

Depuis la synthèse neuve : ouvrir A et choisir 2010–2019 (deux actions de menu),
puis « Voir la durée des introductions ». Le message et la carte indiquent
**10 → 11 s, +1 s** ; la boîte et les chiffres expliquent les dispersions
**6,75–15 s** et **7–18 s**. Une baisse de durée totale ne se transforme pas en
affirmation de raccourcissement des intros.

Ouvrir « Titres associés », choisir B puis cocher « Trois exemples » :
**cardigan — Taylor Swift — 7 s ; Life Goes On — BTS — 11 s ; Like That —
Future, Metro Boomin & Kendrick Lamar — 18 s**. Les trois titres sont proches
de Q1, médiane, Q3. Un genre est manquant sur Like That, visible dans la table.

Environ **six activations de contrôles** depuis le défaut, plus défilement et
éventuelle saisie dans le menu ; une septième pour télécharger. Aucun aller-retour
vers Données. Difficultés observées : le graphique peut nécessiter un défilement
sur écran bas, et la table large un défilement interne sur mobile. Les explications
sont accessibles sans mémoriser les valeurs d’une autre page.

Ce parcours est une **vérification de l’agent**. Aucun membre du groupe, A&R réel
ou participant externe n’a effectué un test utilisateur pendant cette tâche.

## Captures avant/après et limites

- Avant : état local sauvegardé, notamment courbe, collaborations, composition
  mobile ; l’intro a été recapturée depuis l’archive initiale lancée séparément
  sur 8503. Ce n’est pas une capture de la première conversation IA.
- Après : captures de l’intro, de son infobulle et des exemples ; pays et île,
  évolutions, genres, compositions, petites largeurs et simulations de couleur.
- Les captures à différentes sélections servent à expliquer les fonctions ;
  leurs valeurs ne doivent pas être comparées sans lire les périodes.
- Pas de test sur téléphone physique, Safari, Firefox ou lecteur d’écran ;
  l’émulation Chrome ne prouve pas une accessibilité universelle.
- 82 crédits composés demeurent indéterminés ; 21 rapprochements internes sont
  des inférences. Aucune vérification biographique exhaustive des origines.
- La proposition linguistique, la finalisation collective du journal et l’accès
  enseignant au mode de remise restent à confirmer par le groupe. Les options
  de fin de projet n’ont pas été développées automatiquement.
