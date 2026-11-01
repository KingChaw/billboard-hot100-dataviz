# Billboard n°1 · observatoire

Application Streamlit / Plotly en français pour un A&R de label indépendant.
Trois questions : évolution musicale, origines des artistes, profils et modes
de création. Analyse strictement descriptive de 1 177 titres n°1.

## Lancer

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows : `.venv\Scripts\activate`. La configuration du fond de carte local est
conservée. Si le service statique n’était pas déjà actif, redémarrer Streamlit
(`server.enableStaticServing = true` dans `.streamlit/config.toml`).
Aucune dépendance applicative supplémentaire.

## Utiliser

- Navigation fixe sous le bandeau dans toutes les rubriques : rubrique, puis
  sous-page. La dernière sous-page de chaque rubrique est mémorisée. La colonne
  gauche contient uniquement les filtres. Sur mobile, les deux barres défilent
  horizontalement dans leur propre espace.
- **Explorer les n°1** est l’accueil : titre « Quels repères offrent les titres
  n°1 ? », puis les trois parcours numérotés Format, Origines, Profils et création.
  Aucun sous-onglet Synthèse ni ancien bloc de repères chiffrés après la partie 3.
- Au départ : **2000–2009 ; référence 2020–2024, 81 titres**. Le menu distingue
  **2020–janv. 2025, 82 titres**, partielle. Les intervalles personnalisés et les
  décennies conservent leurs réglages indépendants.
- Les dates sélectionnées apparaissent dans les widgets, cartes, légendes,
  infobulles, tableaux et noms des CSV. Deux sélections identiques restent distinctes.
- **Format & son** : cinq sous-pages, dans l’ordre **Vue d’ensemble**, **Durée &
  introduction**, **Signature sonore**, **Instrumentation**, **Genres musicaux**.
  Cette sous-page « Vue d’ensemble » conserve son nom. Un seul graphique
  principal à la fois, avec des choix persistants : mesure de la vue d’ensemble,
  **Durée / Introduction / Évolution**, mesure sonore puis **Distribution /
  Évolution**, **Rôle central / Présence**, **Comparer les années / Historique**.
  Les cartes conservent les deux valeurs et leurs effectifs, sans badges d’écart.
  Les instruments centraux et les sections présentes restent deux analyses distinctes.
  Les genres proposent une comparaison simultanée et une évolution historique ;
  « Non renseigné » est affiché à part, sans genre de remplacement.
- Pays : **Carte / Comparaison des périodes**, avec échelle commune et accès aux îles.
  Compositions exclusives : **100 % / Comparaison des périodes**.
- Q3 organisée en profils, équipes de création, réutilisation. Les équipes et
  pratiques ont une comparaison des périodes et une évolution par décennie.
- Dans **Format & son → Détails**, jusqu’à trois exemples issus des titres filtrés,
  proches de Q1, de la médiane et de Q3 pour la mesure sélectionnée. Les raccourcis
  vers **Données** conservent le genre et les années ; recherche et CSV y restent disponibles.
  Définitions, tableaux numériques et méthode sont regroupés dans ce même volet.
- **Détails** pour méthode et approfondissements ; retour en haut disponible.
  Sur mobile, défilement vertical privilégié pour garder les textes lisibles.

Les sources commencent le 4 août 1958 et s’arrêtent le 11 janvier 2025. Un titre
compte une fois selon sa première semaine au n°1. Aucune prédiction de succès
ou recommandation de recrutement. Les crédits composés non résolus restent
indéterminés ; consulter l’audit avant d’interpréter les taux de collaboration.

Dans Format & son, « Année » est un libellé d’interface : **2000–2009 reste une
plage de dix années**. Les intervalles et calculs ne changent pas. Les effectifs
s’affichent en titres et les écarts ne sont plus présentés dans cette rubrique.
Les cartes et distributions portent sur les deux plages d’années
sélectionnées. Les historiques utilisent **toutes les décennies du corpus avec
le filtre de genre actif**, indépendamment des périodes de comparaison.
La part d’introduction est la médiane de `100 * intro_length_sec / length_sec`
calculé titre par titre, avec deux valeurs renseignées et une durée positive.
Les anciennes routes `intro`, `central` et `presence` sont redirigées vers les
pages fusionnées, y compris dans la mémoire de navigation d’une session ouverte.

## Vérifier

```bash
python -m unittest discover -s tests -v
```

Le script facultatif `tests/browser_qa.mjs` vérifie l’application dans un Chrome
local de test avec CDP sur le port 9226 et Streamlit sur 8502 :

```bash
node tests/browser_qa.mjs scenario
node tests/browser_qa.mjs suite
```

Il enregistre des captures et rapports dans `livrables/`. Chrome doit être
lancé avec un profil temporaire distinct et `--remote-debugging-port=9226`.
Ce script de développement ne fait pas partie des dépendances de l’application.
Voir [VALIDATION.md](VALIDATION.md) pour les vérifications réellement exécutées.

Les contrôles spécifiques sont dans `tests/test_format_sound.py` et
`tests/test_format_ux.py` et `tests/test_final_ux.py`. La suite actuelle comporte
**56 tests** : les 53 tests de la simplification UX conservés et trois nouveaux
contrats pour l’accueil, le nom des rubriques et les notes historiques retirées.
`node tests/format_browser_qa.mjs apres` délègue à
`tests/format_ux_browser_qa.mjs` : Chrome de test isolé sur **9229**, application
sur **8505**, contrôles **320 × 844, 390 × 844 et 1440 × 900 px**. Les variables
`BILLBOARD_CDP_PORT` et `BILLBOARD_URL` permettent de changer ces accès.
Résultats avant/après et captures : `livrables/format-son-ux/`. L’ancien bilan
dans `livrables/format-son/` reste une référence historique.
`node tests/format_ux_browser_qa.mjs guides` compare aussi les styles calculés
du guide Format de référence et d’un guide existant hors rubrique aux trois tailles.
`node tests/final_browser_qa.mjs apres` contrôle la navigation fixe globale,
l’accueil et la conservation des interactions aux trois dimensions ; ses
captures et journaux sont dans `livrables/format-son-ux/finalisation/`.

## Fichiers

- `analysis.py`, `collaboration_rules.py` : préparation et qualification des crédits.
- `dashboard_data.py` : agrégats, couverture, classements, comparaisons.
- `app.py`, `ui.py`, `charts.py`, `theme.py`, `periods.py` : parcours, interface, figures.
- `components/` : dimensions des figures et position de lecture ; aucun service externe.
- `static/` : fond de carte local ; `data/` : sources brutes inchangées.
- [METHODES.md](METHODES.md) : définitions et limites.
- [Bilan Format & son](livrables/format-son/BILAN.md) : changements, fichiers,
  résultats de la première refonte du 1er novembre 2026.
- [Bilan de simplification UX](livrables/format-son-ux/BILAN.md) : nouvelle
  présentation interactive, mesures avant/après et recette réellement exécutée.
- [Finalisation UX](livrables/format-son-ux/finalisation/BILAN.md) : accueil
  « Explorer les n°1 », navigation fixe globale et contrôles complémentaires.
- [BILAN.md](livrables/BILAN.md) : suivi de toutes les recommandations.
- [JOURNAL_COMPLEMENT.md](livrables/JOURNAL_COMPLEMENT.md) : rédaction à intégrer au
  journal du groupe et trame de soutenance ; sources et captures associées.
- `livrables/avant/v2_locale.zip` : copie complète de l’état local avant correction.
  `PROPOSITION.md` et les références statistiques historiques sont conservées.

La refonte du dashboard reprend une navigation à deux niveaux et une colonne
réservée aux filtres. Les calculs et données sont conservés. Les résultats actuels,
y compris l’historique des échecs corrigés, sont détaillés dans [VALIDATION.md](VALIDATION.md).
L’accès de l’enseignant au dépôt privé reste à vérifier par le groupe.
