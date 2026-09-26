# Billboard n°1 · prototype de dataviz

Application interactive en français pour comparer les titres ayant atteint le n°1 du Billboard Hot 100. Les deux CSV fournis sont inclus dans `data/`. L'application lit `billboard.csv` ; `topics.csv` reste disponible pour la traçabilité, mais ne sert pas aux questions analytiques retenues.

## Lancement

```bash
git clone https://github.com/KingChaw/billboard-hot100-dataviz.git
cd billboard-hot100-dataviz
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Sous Windows : `.venv\Scripts\activate` à la place de `source .venv/bin/activate`.

Utiliser la barre latérale pour choisir deux intervalles d'années ou deux décennies et, éventuellement, un genre commun. Trois vues couvrent le format/son, les origines et les artistes/crédits. Le tableau des titres en bas de page reflète toujours les filtres actifs. Les périodes vides sont signalées.

Le fichier `PROPOSITION.md` documente le diagnostic, les choix graphiques, les constats et les limites. L'application ne nécessite ni API, ni modèle d'IA.
