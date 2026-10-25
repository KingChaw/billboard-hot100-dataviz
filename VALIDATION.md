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
