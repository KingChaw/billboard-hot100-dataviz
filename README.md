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

- Navigation → Comparaison → Filtres, dans la barre latérale.
- Au départ : **A 2000–2009 ; B 2020–2024, 81 titres**. Le menu distingue
  **2020–janv. 2025, 82 titres**, partielle. Les intervalles personnalisés et les
  décennies conservent leurs réglages indépendants.
- Courbes, boîtes à moustaches séparées pour durée/intro, sélecteurs sonores,
  barres d’instruments et genres ; couverture Discogs visible.
- Pays : **Carte / Comparaison A/B**, avec échelle commune et accès aux îles.
  Compositions exclusives : **100 % / Comparaison A/B**.
- Q3 organisée en profils, équipes de création, réutilisation. Les équipes et
  pratiques ont une lecture A/B et une évolution par décennie.
- **Titres associés · tableau et CSV** dans chaque analyse : recherche et
  exemples proches des quartiles. Tableau/export identiques, précision conservée.
- **Détails** pour méthode et approfondissements ; retour en haut disponible.
  Sur mobile, défilement vertical privilégié pour garder les textes lisibles.

Les sources commencent le 4 août 1958 et s’arrêtent le 11 janvier 2025. Un titre
compte une fois selon sa première semaine au n°1. Aucune prédiction de succès
ou recommandation de recrutement. Les crédits composés non résolus restent
indéterminés ; consulter l’audit avant d’interpréter les taux de collaboration.

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

## Fichiers

- `analysis.py`, `collaboration_rules.py` : préparation et qualification des crédits.
- `dashboard_data.py` : agrégats, couverture, classements, comparaisons.
- `app.py`, `ui.py`, `charts.py`, `theme.py` : parcours, interface, figures.
- `components/` : dimensions des figures et position de lecture ; aucun service externe.
- `static/` : fond de carte local ; `data/` : sources brutes inchangées.
- [METHODES.md](METHODES.md) : définitions et limites.
- [BILAN.md](livrables/BILAN.md) : suivi de toutes les recommandations.
- [JOURNAL_COMPLEMENT.md](livrables/JOURNAL_COMPLEMENT.md) : rédaction à intégrer au
  journal du groupe et trame de soutenance ; sources et captures associées.
- `livrables/avant/v2_locale.zip` : copie complète de l’état local avant correction.
  `PROPOSITION.md` et les références statistiques historiques sont conservées.

Travail effectué à partir du projet local fourni, sans récupération d’une
ancienne version GitHub, publication, modification du dépôt distant ou écriture
dans le Google Doc. La copie locale n’a pas été comparée à un ZIP externe non
joint à cette demande. L’accès de l’enseignant au mode de remise choisi reste
à vérifier par le groupe.
