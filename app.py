"""Tableau de bord Billboard n°1 — lancer avec streamlit run app.py."""
import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import DATA, binary_shares, category_shares, prepare, select


st.set_page_config(page_title="Billboard n°1 · Repères A&R", layout="wide")
COLORS = {"Période A": "#2764A5", "Référence B": "#E3853E"}
st.title("Billboard Hot 100 · titres n°1")
st.caption("Repères descriptifs pour un directeur artistique · un titre compte une fois, à sa première semaine au n°1")


@st.cache_data
def load():
    return prepare(DATA)


try:
    all_data = load()
except (FileNotFoundError, ValueError, KeyError) as exc:
    st.error(f"Lecture impossible de data/billboard.csv : {exc}")
    st.stop()

all_genres = sorted(set(all_data["genres"].explode().dropna()))
with st.sidebar:
    st.header("Comparer deux périodes")
    mode = st.radio("Découpage", ["Intervalles d’années", "Décennies"], horizontal=True)
    if mode == "Intervalles d’années":
        years_a = st.slider("Période A", 1958, 2025, (1958, 1969))
        years_b = st.slider("Référence B", 1958, 2025, (2020, 2024))
    else:
        decs = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
        a = st.selectbox("Décennie A", decs, index=0, format_func=lambda d: f"{d}s")
        b = st.selectbox("Décennie B", decs, index=7, format_func=lambda d: f"{d}s")
        years_a = (max(1958, a), min(2025, a + 9))
        years_b = (max(1958, b), min(2025, b + 9))
    genre = st.selectbox("Genre Discogs (même filtre pour les deux)", ["Tous les genres"] + all_genres)
    page = st.radio("Vue", ["1 · Format et son", "2 · Origines", "3 · Artistes et création"])
    st.caption("2025 est incomplet (un seul titre). La décennie 1950 commence en août 1958.")

a_df, b_df = select(all_data, years_a, genre), select(all_data, years_b, genre)
frames = {"Période A": a_df, "Référence B": b_df}
st.subheader(f"A : {years_a[0]}–{years_a[1]} ({len(a_df)} titres)  ·  B : {years_b[0]}–{years_b[1]} ({len(b_df)} titres)")
if years_a[1] == 2025 or years_b[1] == 2025:
    st.warning("2025 s’arrête au 11 janvier et ne représente pas une année complète.")
if years_a[0] == 1958 or years_b[0] == 1958:
    st.caption("La série débute le 4 août 1958 : cette première année est partielle.")
if min(len(a_df), len(b_df)) == 0:
    st.warning("Au moins une sélection ne comporte aucun titre. Élargissez les années ou retirez le filtre de genre.")
    st.stop()
if min(len(a_df), len(b_df)) < 10:
    st.warning("Au moins une période contient moins de 10 titres : ses pourcentages sont fragiles.")
if genre != "Tous les genres":
    st.info("Le filtre porte sur les catégories Discogs renseignées : les titres sans genre ne peuvent entrer dans ce sous-ensemble.")


def plot(fig, key):
    fig.update_layout(template="plotly_white", legend_title_text="", margin=dict(t=38, b=35))
    st.plotly_chart(fig, key=key)


def long_numeric(columns, labels):
    parts = []
    for period, data in frames.items():
        for col in columns:
            d = data[[col, "song"]].dropna().copy()
            d["mesure"] = labels[col]
            d["valeur"] = d[col]
            d["période"] = period
            parts.append(d[["mesure", "valeur", "période", "song"]])
    return pd.concat(parts, ignore_index=True)


def share_frame(column):
    return pd.concat([category_shares(data, column).assign(période=name)
                      for name, data in frames.items()], ignore_index=True)


def binary_frame(columns, labels):
    return pd.concat([binary_shares(data, columns, labels).assign(période=name)
                      for name, data in frames.items()], ignore_index=True)


def quality(columns):
    st.caption("Valeurs exploitables (A / B) : " + "; ".join(
        f"{label} {a_df[col].notna().sum()}/{len(a_df)} · {b_df[col].notna().sum()}/{len(b_df)}"
        for col, label in columns.items()))


def bars(data, x, y, title, key, horizontal=False):
    if horizontal:
        fig = px.bar(data, x=y, y=x, color="période", barmode="group", orientation="h",
                     color_discrete_map=COLORS, hover_data=["effectif"] if "effectif" in data else None,
                     title=title)
        fig.update_xaxes(range=[0, 100], title="% des titres de la période")
    else:
        fig = px.bar(data, x=x, y=y, color="période", barmode="group",
                     color_discrete_map=COLORS, hover_data=["effectif"] if "effectif" in data else None,
                     title=title)
        fig.update_yaxes(range=[0, 100], title="% des titres de la période")
    plot(fig, key)


if page.startswith("1"):
    st.header("1 · Format et caractéristiques musicales")
    st.write("Comparer les formats et la diversité des titres n°1 selon leur date de première arrivée au sommet.")
    measures = {"length_sec": "Durée (s)", "intro_length_sec": "Intro avant couplet/refrain (s)"}
    quality(measures)
    cols = st.columns(2)
    for col, (metric, label) in zip(cols, measures.items()):
        with col:
            values = [f"{data[metric].median():.0f} s (n={data[metric].count()})" for data in frames.values()]
            st.metric(label + " · A / B", " / ".join(values))
    length = long_numeric(list(measures), measures)
    plot(px.box(length, x="mesure", y="valeur", color="période", points=False,
                color_discrete_map=COLORS, title="Dispersion des durées (secondes)"), "length_box")
    st.caption("L’introduction inclut parfois un hook initial, selon le dictionnaire.")
    sonic = {"bpm": "Tempo (BPM)", "energy": "Énergie (0–100)",
             "danceability": "Dansabilité (0–100)", "acousticness": "Acoustique (0–100)",
             "loudness_d_b": "Niveau sonore (dB)"}
    metric = st.selectbox("Caractéristique sonore à comparer", list(sonic), format_func=sonic.get)
    quality({metric: sonic[metric]})
    plot(px.box(long_numeric([metric], sonic), x="période", y="valeur", color="période",
                points="outliers", color_discrete_map=COLORS,
                title=f"Distribution · {sonic[metric]}"), "sonic_box")
    st.caption("Les scores Spotify sont sur 0–100 dans ce fichier ; les BPM et dB gardent leurs propres unités.")
    based = {"guitar_based": "Guitare centrale", "piano_keyboard_based": "Piano/claviers centraux",
             "vocally_based": "Voix centrale", "bass_based": "Basse centrale"}
    present = {"orchestral_strings": "Cordes présentes", "horns_winds": "Cuivres/vents présents"}
    with st.expander("Instrumentation · rôle central et présence"):
        bars(binary_frame(list(based), based), "catégorie", "part", "Rôle central dans l’arrangement", "based", True)
        bars(binary_frame(list(present), present), "catégorie", "part", "Présence de sections", "present", True)
        st.caption("Indicateurs simultanés. Leur somme peut dépasser 100 % ; ils ne mesurent pas la complexité.")
    g = share_frame("genres")
    top = g.groupby("catégorie")["effectif"].sum().nlargest(9).index.tolist()
    top += ["Non renseigné"] if "Non renseigné" not in top else []
    bars(g[g["catégorie"].isin(top)], "catégorie", "part", "Genres Discogs · catégories principales", "genre", True)
    st.caption("Un titre peut relever de plusieurs genres : chaque part = titres du genre / tous les titres de la période. Les parts peuvent dépasser 100 % au total.")
    st.caption("Genres non renseignés (A / B) : " + " / ".join(str(data.discogs_genre.isna().sum()) for data in frames.values()))

elif page.startswith("2"):
    st.header("2 · Origines des artistes")
    st.write("Pays de naissance associés aux titres, selon la codification du fichier ; ce n’est ni la nationalité ni la langue chantée.")
    group = pd.concat([data.origin_group.value_counts().rename_axis("catégorie").reset_index(name="effectif")
                       .assign(période=period, part=lambda d: d.effectif * 100 / len(data))
                       for period, data in frames.items()], ignore_index=True)
    bars(group, "catégorie", "part", "Partition exclusive des origines", "origin_group", True)
    countries = share_frame("origins")
    top = countries.groupby("catégorie")["effectif"].sum().nlargest(9).index.tolist()
    bars(countries[countries["catégorie"].isin(top)], "catégorie", "part", "Pays/territoires les plus présents", "countries", True)
    st.caption("Un titre peut associer plusieurs pays : chaque part = titres associés au pays / tous les titres de la période ; somme potentiellement > 100 %.")
    fl = binary_frame(["foreign_language"], {"foreign_language": "Paroles non anglaises (même partielles)"})
    bars(fl, "catégorie", "part", "Paroles non anglaises (indicateur complémentaire)", "language")
    st.caption("Le champ ne précise pas la langue. La base entière ne signale que 22 titres ; prudence sur les petits groupes.")
    with st.expander("Croisement des origines et paroles non anglaises"):
        for period, data in frames.items():
            counts = data.groupby("origin_group")["foreign_language"].agg(["size", "sum"])
            counts.columns = ["Titres", "Paroles non anglaises"]
            st.write(period, counts)
    st.caption("Corrections : ‘Unites States’ → United States ; ‘Columbia’ → Colombia (à valider sur la ligne). Porto Rico reste visible séparément et est inclus dans les origines américaines pour la partition.")

else:
    st.header("3 · Artistes et création")
    st.write("Les âges et les crédits sont calculés par titre ; un même artiste peut apparaître plusieurs fois.")
    quality({"front_person_age": "Âge", "writers_all": "Auteurs (tous crédits)",
             "writers_original": "Auteurs hors samples/interpolations", "producer_count": "Producteurs"})
    st.caption("Âge du frontperson ou chef de groupe (moyenne si plusieurs), pas nécessairement celui du chanteur principal ; les décimales sont conservées.")
    plot(px.box(long_numeric(["front_person_age"], {"front_person_age": "Âge (années)"}),
                x="période", y="valeur", color="période", points="outliers",
                color_discrete_map=COLORS, title="Distribution de l’âge renseigné"), "age")
    formats = pd.concat([data.artist_format.value_counts().rename_axis("catégorie").reset_index(name="effectif")
                         .assign(période=period, part=lambda d: 100 * d.effectif / len(data))
                         for period, data in frames.items()], ignore_index=True)
    bars(formats, "catégorie", "part", "Format de l’artiste · catégories exclusives", "formats")
    indicators = pd.concat([
        pd.DataFrame({"catégorie": ["Invité répertorié (structure +0,5)", "Plusieurs artistes au crédit"],
                      "effectif": [int(data.listed_guest.eq(True).sum()), int(data.collaboration_credit.sum())],
                      "part": [100 * data.listed_guest.eq(True).sum() / len(data), 100 * data.collaboration_credit.sum() / len(data)],
                      "période": period}) for period, data in frames.items()], ignore_index=True)
    bars(indicators, "catégorie", "part", "Deux repères distincts de collaboration", "collaborations", True)
    st.caption("« Invité » vient de artist_structure et peut désigner un instrumentiste. « Plusieurs artistes au crédit » repère certains séparateurs dans artist : approximation à vérifier, pas un taux de featuring commercial.")
    credit = st.selectbox("Taille d’équipe (personnes distinctes par titre)",
                          ["writers_original", "writers_all", "producer_count"],
                          format_func={"writers_original": "Auteurs hors crédits samples/interpolations",
                                       "writers_all": "Auteurs tous crédits", "producer_count": "Producteurs"}.get)
    plot(px.box(long_numeric([credit], {credit: "Personnes distinctes"}), x="période", y="valeur",
                color="période", color_discrete_map=COLORS, points="outliers",
                title="Dispersion de la taille d’équipe"), "credits")
    st.caption("Les listes sont séparées par « ; », harmonisées pour les espaces/casse et dédupliquées. « Unknown » compte comme valeur manquante.")
    use = {"sample": "Sample", "interpolation": "Interpolation", "cover": "Reprise"}
    bars(binary_frame(list(use), use), "catégorie", "part", "Réutilisation de musique antérieure", "reuse")
    st.caption("Ces trois indicateurs peuvent se cumuler sur un titre ; dénominateur = tous les titres de la période.")
    with st.expander("Explorations secondaires · artistes et âge par genre"):
        st.caption("Classement par chaîne de crédit complète, sans attribution individuelle des collaborations.")
        for period, data in frames.items():
            st.write(period, data.artist.value_counts().head(10))
        for period, data in frames.items():
            subset = data.explode("genres").groupby("genres").front_person_age.agg(["median", "count"])
            st.write(period + " · âge par genre (n ≥ 5)", subset[subset["count"] >= 5].sort_values("count", ascending=False).head(12))

with st.expander("Titres correspondant aux filtres"):
    period = st.radio("Liste", list(frames), horizontal=True)
    view = frames[period][["song", "artist", "date", "discogs_genre", "artist_place_of_origin", "length_sec", "intro_length_sec"]].copy()
    view["date"] = view["date"].dt.date
    st.dataframe(view, width="stretch", hide_index=True)
    st.download_button("Télécharger cette sélection (CSV)", view.to_csv(index=False).encode("utf-8-sig"),
                       f"billboard_selection_{period.replace(' ', '_')}.csv", "text/csv")

with st.expander("Méthode et limites"):
    st.markdown("""**Unité :** un titre du CSV, sans pondération par `weeks_at_number_one`.
La `date` est la première semaine au n°1. Les périodes peuvent se chevaucher et affichent alors les mêmes titres.

**Parts :** effectif de titres possédant la catégorie / tous les titres filtrés de la période. Les genres et pays sont à réponses multiples ; leurs parts ne s'additionnent pas à 100 %. Les pourcentages de partition des origines et de format utilisent des catégories exclusives.

**Qualité :** les valeurs manquantes ne sont jamais assimilées à zéro. `cdr_genre` est absent pour 2020–2025 ; seule la classification `discogs_genre` est utilisée. La géographie des groupes et des collaborations mérite une revue manuelle ; Porto Rico est un territoire américain, présenté séparément dans les pays. La qualité des crédits et des indicateurs sonores dépend de la source.

**Périmètre :** ces observations décrivent les titres n°1 de ce fichier et ne mesurent ni les causes du succès, ni tous les titres sortis ou tous les marchés.

**Étape ultérieure :** un éventuel assistant IA pourrait recevoir uniquement les agrégats calculés et les titres filtrés, puis en résumer les constats avec dénominateurs et réserves. Il ne serait pas nécessaire au fonctionnement du tableau de bord.""")
