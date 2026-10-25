"""Billboard n°1 — python -m streamlit run app.py."""
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from analysis import DATA, prepare, select
from charts import bars, binary_frame, distribution, points, render, share_frame, stacked, trend, world_map
from dashboard_data import (METRICS, ORIGINS, ORIGIN_HELP, CREDITS, REUSE, collaboration_frame,
                            country_frame, decades, overlap_message, ranked_categories, comparison_rows)
from periods import date_label, period_labels, display_comparison
from theme import apply_theme
from ui import (category_legend, category_message, coverage_note, details, header, kpi_cards, median_card, metric_message,
                number, numeric_summary, numeric_table, selection_table, share_card, shares_summary, show_table, title_explorer)

st.set_page_config(page_title="Billboard #1", page_icon="🎵", layout="wide", initial_sidebar_state="expanded")
apply_theme()
position = components.declare_component("page_position", path=str(Path(__file__).parent / "components" / "navigation"))


@st.cache_data
def load(source_version):
    return prepare(DATA)


try:
    # Invalider aussi les données préparées lorsque les règles de crédit évoluent.
    all_data = load((DATA.stat().st_mtime_ns, (DATA.parent.parent / "analysis.py").stat().st_mtime_ns,
                     (DATA.parent.parent / "collaboration_rules.py").stat().st_mtime_ns))
except (FileNotFoundError, ValueError, KeyError) as exc:
    st.error(f"Lecture impossible de data/billboard.csv : {exc}")
    st.stop()

first, last = int(all_data.year.min()), int(all_data.year.max())
decs = list(range(first // 10 * 10, last // 10 * 10 + 1, 10))
clamp = lambda d: (max(first, d), min(last, d + 9))
defaults = {"route": "summary", "mode": "Décennies", "decade_a": 2000, "decade_b": "recent",
            "genre": "Tous les genres", "years_a": (2000, 2009), "years_b": (2020, 2024), "scroll_token": 0}
# Les widgets absents d’une page ne doivent pas effacer les réglages de l’utilisateur.
for key in list(st.session_state):
    # Les composants doivent recevoir leurs nouvelles dimensions du navigateur.
    # Les réassigner ici figerait leur valeur précédente après un redimensionnement.
    if key != "page_position" and not key.startswith(("nav_", "group_", "shortcut_", "export_", "back_top", "chart_")):
        st.session_state[key] = st.session_state[key]
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

NAV = {
    "Vue d’ensemble": [("summary", "Synthèse")],
    "Format & son": [("format_trend", "Évolution musicale"), ("duration", "Durée des titres"),
                         ("intro", "Durée des introductions"), ("sound", "Caractéristiques sonores"),
                         ("central", "Rôle central"), ("presence", "Présence de sections"), ("genres", "Genres")],
    "Origines des artistes": [("origin_trend", "Évolution des origines"), ("origins", "Composition des origines"),
                                 ("map", "Pays et territoires")],
    "Profils et création": [("ages", "Âges renseignés"), ("formats", "Groupe, duo ou solo"),
                               ("collabs", "Collaborations"), ("teams", "Équipes de création"),
                               ("reuse", "Réutilisation musicale")],
    "Données": [("data_a", "Titres de la période étudiée"), ("data_b", "Titres de la période de référence")],
}
TITLES = {route: label for entries in NAV.values() for route, label in entries}
TITLES.update(summary="Quels repères offrent les titres n°1 ?", format_trend="Comment les caractéristiques musicales évoluent-elles ?",
              origin_trend="Comment les origines associées aux n°1 évoluent-elles ?",
              duration="Comment la durée des titres varie-t-elle ?", intro="Comment la durée des introductions varie-t-elle ?",
              sound="Comment le profil sonore varie-t-il ?", ages="Quels âges sont renseignés pour les artistes ?",
              teams="Les équipes de création se sont-elles agrandies ?", reuse="Comment les pratiques de réutilisation évoluent-elles ?",
              collabs="Quelles associations d’artistes apparaissent au crédit ?",
              central="Quels instruments structurent les titres n°1 ?", presence="Quelles sections instrumentales sont présentes ?",
              genres="Quels genres sont associés aux titres n°1 ?", origins="Comment se répartissent les origines ?",
              formats="Comment se répartissent les formats d’artistes ?", map="Quels pays et territoires sont associés aux n°1 ?")


def navigate(route):
    st.session_state.route = route
    for group, entries in NAV.items():
        if route in dict(entries):
            st.session_state.setdefault("last_routes", {})[group] = route
            break


def open_group(group):
    routes = dict(NAV[group])
    remembered = st.session_state.get("last_routes", {}).get(group)
    navigate(remembered if remembered in routes else next(iter(routes)))


def navigation(labels):
    active_group = next(group for group, entries in NAV.items() if st.session_state.route in dict(entries))
    st.session_state.setdefault("last_routes", {})[active_group] = st.session_state.route
    with st.container(key="primary_nav", horizontal=True, gap="small"):
        for index, group in enumerate(NAV):
            st.button(group, key=f"group_{index}", on_click=open_group, args=(group,),
                      type="primary" if group == active_group else "tertiary", width="content")
    with st.container(key="secondary_nav", horizontal=True, gap="small"):
        for route, title in NAV[active_group]:
            if route in ("data_a", "data_b"):
                title = labels["Période A" if route == "data_a" else "Référence B"]
            st.button(title, key=f"nav_{route}", on_click=navigate, args=(route,), width="content",
                      type="primary" if st.session_state.route == route else "tertiary")


def shortcut(label, route):
    st.button(label, key=f"shortcut_{route}", on_click=navigate, args=(route,), width="stretch")


def period_label(option):
    if option == "recent":
        return date_label((2020, 2024))
    a, b = clamp(option)
    if a == 1958:
        return date_label((a, b)) + " · dès le 4 août"
    if b == 2025:
        return date_label((a, b)) + " · partielle"
    return date_label((a, b))


st.markdown('<div class="brand-banner"><span class="brand">Billboard <b>#1</b></span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="filter-heading">Filtres</div>', unsafe_allow_html=True)
    st.subheader("PÉRIODES")
    mode = st.radio("Découpage", ["Décennies", "Intervalles d’années"], key="mode")
    if mode == "Décennies":
        options = [*decs, "recent"]
        a = st.selectbox("Période étudiée", options, format_func=period_label, key="decade_a")
        b = st.selectbox("Période de référence", options, format_func=period_label, key="decade_b")
        years_a = (2020, 2024) if a == "recent" else clamp(a)
        years_b = (2020, 2024) if b == "recent" else clamp(b)
    else:
        years_a = st.slider("Période étudiée", first, last, key="years_a")
        years_b = st.slider("Période de référence", first, last, key="years_b")
    overlap = overlap_message(years_a, years_b)
    if overlap:
        st.warning(overlap)
    if any(y[0] <= 1958 <= y[1] for y in (years_a, years_b)):
        st.caption("1958 : à partir du 4 août seulement.")
    if any(y[0] <= 2025 <= y[1] for y in (years_a, years_b)):
        st.warning("2025 : un seul titre, jusqu’au 11 janvier. Période partielle.")
    st.divider()
    st.subheader("GENRES")
    all_genres = sorted(set(all_data.genres.explode().dropna()))
    genre = st.selectbox("Genre Discogs", ["Tous les genres"] + all_genres, key="genre")
    if genre == "Non renseigné":
        st.caption("« Non renseigné » = absence de genre Discogs ; ce n’est pas un genre musical.")
    elif genre != "Tous les genres":
        st.caption("Ce filtre exclut les titres sans genre Discogs. Même filtre pour les deux périodes et les courbes.")

frames = {"Période A": select(all_data, years_a, genre), "Référence B": select(all_data, years_b, genre)}
for key, years in zip(frames, (years_a, years_b)):
    frames[key].attrs["period_years"] = tuple(years)
labels = period_labels(frames)
TITLES.update(data_a=f"Titres · {labels['Période A']}", data_b=f"Titres · {labels['Référence B']}")
navigation(labels)
route = st.session_state.route
position(route=route, token=st.session_state.scroll_token, key="page_position")
header(years_a, years_b, frames, genre)
st.title(TITLES[route])
for label, data in frames.items():
    if data.empty:
        st.info(f"{labels[label]} : aucun titre pour cette sélection. Les résultats de l’autre période restent consultables.")
    elif len(data) < 10:
        st.warning(f"{labels[label]} : {len(data)} titres seulement. Petits effectifs : prudence ; 10 titres n’est pas un seuil de fiabilité statistique.")
if any(y[0] <= 2025 <= y[1] for y in (years_a, years_b)):
    st.caption("Couverture partielle de 2025 : arrêt au 11 janvier ; différente de la référence 2020–2024.")
if any(y[0] <= 1958 <= y[1] for y in (years_a, years_b)):
    st.caption("1958 est partielle : le fichier commence le 4 août.")

AGE_NOTE = "Âge du frontperson ou chef de groupe, éventuellement moyenne s’ils sont plusieurs. Ce n’est ni l’âge individuel de tous les membres, ni nécessairement celui du chanteur principal. Les décimales sont conservées."
CREDIT_NOTE = "Personnes distinctes par titre : noms séparés par « ; », espaces et casse harmonisés, puis déduplication. « Unknown » est une information manquante."
ORIGIN_NOTE = "Origines = pays de naissance renseignés, distincts de la nationalité, de la langue ou du marché. Porto Rico est regroupé avec les États-Unis pour la composition, et reste distinct sur la carte."
BASED = {"guitar_based": "Guitare centrale", "piano_keyboard_based": "Piano/claviers centraux", "vocally_based": "Voix centrale", "bass_based": "Basse centrale"}
PRESENT = {"orchestral_strings": "Cordes présentes", "horns_winds": "Cuivres/vents présents"}
BOX_NOTE = "La médiane partage les valeurs en deux moitiés. Q1–Q3 contient la moitié centrale des valeurs ; ce n’est pas un intervalle de confiance."
TREND_NOTE = "Courbe : périodes indiquées sur l’axe. Cartes de comparaison : vos intervalles exacts, parfois différents des décennies. Même filtre de genre."
filtered = select(all_data, (first, last), genre)
title_metric = None
title_frames = frames
# Colonnes source des explorations contextuelles, fixées dans chaque branche.
title_columns = ["discogs_genre", "length_sec", "intro_length_sec"]


def detail_block(columns=None, notes=()):
    return details(frames, all_data, genre, columns, notes)


def trend_notes(data):
    st.caption(TREND_NOTE)
    st.caption("Cercles ouverts : couverture partielle. 1958 débute le 4 août ; 2025 s’arrête au 11 janvier. L’agrégat 2020–janv. 2025 diffère de la référence 2020–2024.")
    small = data[(data.valid > 0) & (data.valid < 10)]
    if len(small):
        st.warning("Moins de 10 valeurs exploitables : " + ", ".join(f"{r.label} ({r.valid}/{r.total})" for r in small.itertuples()) + ". Prudence.")
    missing = data[data.valid.eq(0)]
    if len(missing):
        st.caption("Périodes sans valeur exploitable, non reliées : " + ", ".join(missing.label))


def temporal_table(data):
    keep = [c for c in ["label", "value", "q1", "q3", "count", "valid", "total", "partial"] if c in data]
    st.dataframe(data[keep].rename(columns={"label": "Période couverte", "value": "Médiane / part (%)", "q1": "Q1", "q3": "Q3",
                                          "count": "Titres concernés", "valid": "Exploitables", "total": "Titres", "partial": "Partielle"}), hide_index=True, width="stretch")


if route == "summary":
    kpi_cards([median_card(frames, "length_sec", "Durée médiane", is_duration=True),
               median_card(frames, "intro_length_sec", "Introduction médiane", is_duration=True)], frames)
    st.write("Trois lectures pour situer un projet artistique : caractéristiques musicales, origines, profils et création. Chaque titre compte une fois, à sa première semaine au n°1.")
    st.caption("Observatoire descriptif des seuls n°1 : aucune recette du succès, prédiction ou norme de production. Fichier : 4 août 1958–11 janvier 2025.")
    st.subheader("1 · Comment les caractéristiques musicales évoluent-elles ?")
    st.write(metric_message(frames, "length_sec", "Durée", "s") + " " + metric_message(frames, "intro_length_sec", "Introduction", "s"))
    left, right = st.columns(2)
    with left:
        shortcut("Voir la durée des titres", "duration")
    with right:
        shortcut("Voir la durée des introductions", "intro")
    st.subheader("2 · D’où viennent les artistes associés aux n°1 ?")
    kpi_cards([share_card(frames, "Uniquement États-Unis", lambda d: d.origin_group.eq(next(iter(ORIGINS))), lambda d: d.origins.map(bool)),
               share_card(frames, "Uniquement hors États-Unis", lambda d: d.origin_group.eq("Hors États-Unis uniquement"), lambda d: d.origins.map(bool))], frames)
    left, right = st.columns(2)
    with left:
        shortcut("Voir la composition des origines", "origins")
    with right:
        shortcut("Comparer les pays et territoires", "map")
    st.subheader("3 · Comment les profils et les modes de création évoluent-ils ?")
    st.write(metric_message(frames, "writers_original", "Auteurs hors samples/interpolations", "personnes"))
    kpi_cards([median_card(frames, "front_person_age", "Âge médian du frontperson", "ans"),
               median_card(frames, "writers_original", "Auteurs hors samples/interpolations · médiane", "personnes")], frames)
    left, right = st.columns(2)
    with left:
        shortcut("Voir la dispersion des âges", "ages")
    with right:
        shortcut("Voir les équipes de création", "teams")
    with detail_block(notes=[AGE_NOTE, CREDIT_NOTE, ORIGIN_NOTE]):
        pass

elif route in ("format_trend", "origin_trend"):
    if route == "format_trend":
        metric = st.selectbox("Indicateur", list(METRICS), format_func=lambda c: METRICS[c][0], key="evolution_metric")
        label, unit = METRICS[metric]
        numeric_summary(frames, metric, label, unit)
        data = decades(filtered, column=metric, coverage=(first, last))
        title_columns += [metric]
        title_metric = metric
        median = True
    else:
        metric = st.selectbox("Composition", list(ORIGINS)[:3], format_func=ORIGINS.get, key="origin_metric")
        kpi_cards([share_card(frames, ORIGINS[metric], lambda d: d.origin_group.eq(metric), lambda d: d.origins.map(bool))], frames)
        data = decades(filtered, origin=metric, coverage=(first, last))
        unit, median = "%", False
        title_columns = ["artist_place_of_origin", "origin_group", "foreign_language"]
    trend_notes(data)
    render(trend(data, unit, years_a, years_b, median=median), route)
    if median:
        st.caption(BOX_NOTE)
    with detail_block(notes=[BOX_NOTE if median else ORIGIN_HELP[ORIGINS[metric]]]):
        if median:
            numeric_table(frames, metric, unit)
        temporal_table(data)

elif route in ("duration", "intro", "sound", "ages", "teams"):
    notes = [BOX_NOTE, "Les moustaches s’étendent aux valeurs dans 1,5 intervalle interquartile. Toutes les valeurs exploitables contribuent aux calculs."]
    view = "Distribution des périodes"
    if route in ("duration", "intro"):
        metric = "length_sec" if route == "duration" else "intro_length_sec"
        label, unit = METRICS[metric]
        notes += ["Durée et introduction ont des échelles distinctes ; Les deux périodes partagent la même échelle dans chaque vue. L’introduction peut inclure un hook initial."]
    elif route == "sound":
        metric = st.selectbox("Indicateur sonore", list(METRICS)[2:], format_func=lambda c: METRICS[c][0], key="sonic")
        label, unit = METRICS[metric]
        notes += ["Énergie, dansabilité et caractère acoustique : scores Spotify de 0 à 100. BPM et dB gardent leurs unités."]
    elif route == "ages":
        metric, label, unit = "front_person_age", "Âge renseigné", "ans"
        st.caption(AGE_NOTE)
    else:
        metric = st.selectbox("Personnes distinctes par titre", list(CREDITS), format_func=CREDITS.get, key="credit")
        label, unit = CREDITS[metric], "personnes"
        view = st.radio("Lecture des équipes", ["Distribution des périodes", "Évolution par décennie"], horizontal=True, key="teams_view")
        notes += [CREDIT_NOTE]
    numeric_summary(frames, metric, label, unit)
    if view == "Évolution par décennie":
        data = decades(filtered, column=metric, coverage=(first, last))
        trend_notes(data)
        render(trend(data, unit, years_a, years_b), "teams_trend")
    else:
        render(distribution(frames, metric, unit, points=False if route in ("duration", "intro") else "outliers"), route)
        st.caption("Survoler le losange de chaque boîte pour les chiffres, également accessibles dans Détails.")
    st.caption(BOX_NOTE)
    title_metric = metric
    title_columns += [metric]
    if route in ("ages", "teams"):
        title_columns = ["front_person_age", "artist_format", "listed_guest", "collaboration_credit", "collaboration_status",
                         "featured_artists", "songwriters", "songwriters_w_o_interpolation_sample_credits", "producers", *CREDITS, *REUSE]
    with detail_block({metric: label}, notes):
        numeric_table(frames, metric, unit)
        if view == "Évolution par décennie":
            temporal_table(data)
        if route == "ages":
            st.markdown("**Âge par genre · au moins 5 valeurs exploitables**")
            for period, d in frames.items():
                grouped = d.explode("genres").groupby("genres").front_person_age.agg(["median", "count"])
                st.caption(labels[period])
                st.dataframe(grouped[grouped["count"] >= 5].sort_values("count", ascending=False).head(12)
                             .rename(columns={"median": "Âge médian (ans)", "count": "Exploitables"}).rename_axis("Genre"), width="stretch")

elif route in ("central", "presence", "genres"):
    columns = BASED if route == "central" else PRESENT
    if route == "genres":
        data = share_frame(frames, "genres")
        order = ranked_categories(data)
        coverage_note(frames, column="discogs_genre", label="Couverture des genres Discogs")
        st.caption("Top 9 selon la moyenne des parts des deux périodes : chaque période disponible pèse autant. « Non renseigné » reste visible. Les genres se cumulent ; le total peut dépasser 100 %.")
        notes = ["Une période vide est exclue du classement. Les absences de catégorie dans une période non vide valent zéro. En cas d’égalité, ordre alphabétique. Toutes les catégories sont disponibles ci-dessous et dans le filtre."]
        columns = {"discogs_genre": "Genre Discogs"}
        title_columns = ["discogs_genre", "length_sec", "intro_length_sec"]
    else:
        data, order = binary_frame(frames, columns), list(columns.values())
        st.caption("Indicateurs cumulables ; tous les titres filtrés au dénominateur. Le rôle central se distingue de la présence d’une section et ne mesure pas la complexité musicale.")
        for col, label in columns.items():
            coverage_note(frames, column=col, label=label)
        notes = ["Rôle central : l’instrument ou la voix structure l’arrangement. Présence de sections : cordes ou cuivres/vents présents, sans présumer un rôle central."]
        title_columns += list(columns)
    st.write(category_message(data, frames, order))
    render(bars(data, frames, order), route)
    with detail_block(columns, notes):
        all_order = sorted(data["catégorie"].unique())
        st.dataframe(display_comparison(comparison_rows(data, frames, all_order), frames), hide_index=True, width="stretch")

elif route in ("origins", "formats"):
    if route == "origins":
        column, order = "origin_group", list(ORIGINS.values())
        notes = [ORIGIN_NOTE, "Une seule catégorie par titre, y compris les non classables."]
        category_legend(order, ORIGIN_HELP)
        coverage_note(frames, list_column="origins", label="Origines exploitables")
        title_columns = ["artist_place_of_origin", "origin_group", "foreign_language"]
    else:
        column, order = "artist_format", ["Groupe", "Duo", "Solo", "Non renseigné"]
        notes = ["Format indépendant des invités et des associations au crédit. Codes source : 0 groupe, 1 solo, 2 duo ; +0,5 invité. Les inconnus restent dans le total."]
        category_legend(order)
        coverage_note(frames, column="artist_structure", label="Format d’artiste")
        title_columns = ["front_person_age", "artist_format", "listed_guest", "featured_artists", "collaboration_credit", "collaboration_status"]
    view = st.radio("Lecture de la composition", ["Composition à 100 %", "Comparaison des périodes"], horizontal=True, key=f"composition_{route}")
    data = share_frame(frames, column)
    if column == "origin_group":
        data["catégorie"] = data["catégorie"].replace(ORIGINS)
    st.write(category_message(data, frames, order))
    if view == "Composition à 100 %":
        render(stacked(frames, column, order), route)
        st.caption("Chaque barre représente tous les titres d’une période. Pour comparer précisément chaque catégorie, choisir « Comparaison des périodes ».")
    else:
        render(points(data, frames, order), route)
        shares_summary(data, frames, order)
    if route == "origins":
        with st.expander("Complément proposé · paroles non anglaises"):
            st.caption("Réintégration proposée, arbitrage collectif ouvert : le cadrage conserve cet indicateur. Il ne précise pas la langue ; origine et langue sont distinctes.")
            kpi_cards([share_card(frames, "Présence de paroles non anglaises", lambda d: d.foreign_language.eq(1), lambda d: d.foreign_language.notna())], frames)
            st.caption("Peu de titres concernés : éviter les conclusions générales sur les langues.")
            for period, d in frames.items():
                st.caption(labels[period] + " · croisement descriptif avec les origines")
                st.dataframe(d.assign(présence=d.foreign_language.map({0: "Non", 1: "Oui"}).fillna("Non renseigné"))
                             .groupby(["origin_group", "présence"]).size().rename("Titres").rename_axis(["Origines", "Paroles non anglaises"]), width="stretch")
    with detail_block(notes=notes):
        st.dataframe(display_comparison(comparison_rows(data, frames, order), frames), hide_index=True, width="stretch")

elif route == "map":
    data = country_frame(frames, all_data)
    view = st.radio("Lecture des pays", ["Carte", "Comparaison des périodes"], horizontal=True, key="country_view")
    country = st.selectbox("Retrouver un pays ou territoire", ["Tous"] + sorted(data.pays.unique()), key="map_country")
    coverage_note(frames, list_column="origins", label="Origines exploitables")
    st.caption("Pays associés / tous les titres filtrés. Un titre peut compter dans plusieurs pays ; origine, nationalité, langue et marché sont distincts.")
    comparisons = data.rename(columns={"pays": "catégorie"})
    st.write(category_message(comparisons, frames, [country] if country != "Tous" else ranked_categories(comparisons, limit=10, missing=None)))
    if view == "Carte":
        period = st.radio("Période affichée", list(frames), format_func=labels.get, horizontal=True, key="map_period")
        st.caption("Violet très clair : 0 % · Gris : absence de données · Échelle commune aux deux périodes")
        render(world_map(data, period, None if country == "Tous" else country, label=labels[period]), route)
    else:
        order = [country] if country != "Tous" else ranked_categories(comparisons, limit=10, missing=None)
        st.caption("10 pays selon la moyenne des parts des deux périodes, à poids égaux. Le sélecteur et Détails donnent accès à tous les territoires.")
        render(bars(comparisons, frames, order), route)
    if country != "Tous":
        rows = data[data.pays.eq(country)]
        for r in rows.itertuples():
            st.caption(f"{labels[r.période]} · {country} : {number(r.part)} % · {r.effectif}/{r.total} titres" if pd.notna(r.part) else f"{labels[r.période]} · {country} : non disponible")
        shares_summary(comparisons, frames, [country])
    title_columns = ["artist_place_of_origin", "origin_group", "foreign_language"]
    # Le choix d’un pays est aussi appliqué à la sélection contextuelle des titres.
    if country != "Tous":
        source = data[data.pays.eq(country)].source.iloc[0]
        title_frames = {p: d.loc[d.origins.map(lambda values: source in values).astype(bool)]
                        for p, d in frames.items()}
    with detail_block(notes=[ORIGIN_NOTE, "Un pays documenté mais absent de la sélection vaut zéro. Gris : pays non documenté ou aucune origine exploitable.",
                             "« Unites States » est normalisé en United States. « Columbia » est normalisé en Colombia sur le titre We Don't Talk About Bruno : correction étayée par les biographies Disney du casting, sans vérification exhaustive de chaque origine du casting.",
                             "Carte : localiser ; barres à base commune : comparer. Les petites îles restent accessibles par repère et sélecteur."]):
        st.dataframe(display_comparison(comparison_rows(comparisons, frames, sorted(data.pays.unique())), frames), hide_index=True, width="stretch")

elif route in ("collabs", "reuse"):
    if route == "collabs":
        data = collaboration_frame(frames)
        columns = {"listed_guest": "Invité répertorié", "collaboration_credit": "Association d’artistes au crédit"}
        st.caption("Invité répertorié ≠ featuring commercial : il peut être instrumentiste. Une association au crédit est distincte du format solo/duo/groupe.")
        st.caption("Associations : mentions explicites, cas documentés ou inférences à partir de crédits distincts du corpus. Les crédits composés non résolus restent indéterminés, jamais négatifs.")
        notes = ["Un séparateur seul ne suffit pas. Formations documentées, dont Simon & Garfunkel, exclues ; Coldplay & BTS et les groupes/duos avec ft. restent inclus. Voir le détail de chaque titre et livrables/AUDIT_COLLABORATIONS.md."]
        for col, label in columns.items():
            coverage_note(frames, column=col, label=label)
        title_columns = ["front_person_age", "artist_format", "listed_guest", "featured_artists", "collaboration_credit", "collaboration_status", "collaboration_evidence"]
        view = "Comparaison des périodes"
    else:
        columns = REUSE
        data = binary_frame(frames, columns)
        view = st.radio("Lecture des pratiques", ["Comparaison des périodes", "Évolution par décennie"], horizontal=True, key="reuse_view")
        st.caption("Sample, interpolation et reprise peuvent se cumuler. Parts sur tous les titres filtrés ; aucun total à 100 %.")
        notes = ["Écart entre la référence et la période étudiée, en points de pourcentage. Par exemple 20 % → 25 % = +5 points. Aucune variation relative calculée sur une base nulle."]
        title_columns = ["artist_format", "songwriters", "songwriters_w_o_interpolation_sample_credits", "producers", *CREDITS, *REUSE]
    if view == "Évolution par décennie":
        metric = st.selectbox("Pratique", list(REUSE), format_func=REUSE.get, key="reuse_metric")
        kpi_cards([share_card(frames, REUSE[metric], lambda d: d[metric].eq(1), lambda d: d[metric].notna())], frames)
        temporal = decades(filtered, binary=metric, coverage=(first, last))
        trend_notes(temporal)
        render(trend(temporal, "%", years_a, years_b, median=False), "reuse_trend")
    else:
        st.write(category_message(data, frames, list(columns.values())))
        render(points(data, frames, list(columns.values())), route)
        shares_summary(data, frames, list(columns.values()))
        if route == "reuse":
            for col, label in columns.items():
                coverage_note(frames, column=col, label=label)
    st.caption("Dénominateur : tous les titres filtrés. Les cas indéterminés limitent la comparaison même s’ils ne sont pas comptés au numérateur.")
    with detail_block(columns, notes):
        st.dataframe(display_comparison(comparison_rows(data, frames, list(columns.values())), frames), hide_index=True, width="stretch")
        if view == "Évolution par décennie":
            temporal_table(temporal)

elif route in ("data_a", "data_b"):
    period = "Période A" if route == "data_a" else "Référence B"
    view = selection_table(frames[period].sort_values(["date", "song", "artist"], kind="stable"))
    show_table(view, route, labels[period])
    with detail_block(notes=["Le tableau et le CSV proviennent du même objet, sans arrondir les valeurs. Le nombre de semaines au n°1 n’est pas un décompte de semaines situées dans la période filtrée."]):
        st.markdown("**Artistes les plus représentés**")
        st.caption("Classement par crédit complet et par titre, sans décompte d’artistes uniques.")
        st.dataframe(frames[period].artist.value_counts().head(10).rename_axis("Artiste / crédit complet").rename("Titres"), width="stretch")

if not route.startswith("data_"):
    title_explorer(title_frames, title_columns, route, title_metric)


def back_top():
    st.session_state.scroll_token += 1


st.button("↑ Retour en haut", key="back_top", on_click=back_top)
