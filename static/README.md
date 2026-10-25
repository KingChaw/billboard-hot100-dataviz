# Fond de carte local

`world_110m.json` est le fond TopoJSON distribué par Plotly :
https://cdn.plot.ly/world_110m.json (récupéré le 28 septembre 2026).

Géométrie Natural Earth (domaine public), utilisée par Plotly pour les cartes
`geo`. Le fichier est servi par Streamlit via `app/static/`, avec
`server.enableStaticServing = true`. Aucun appel à un service cartographique
externe n'est nécessaire à l'exécution.
