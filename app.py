"""Billboard n°1 — python -m streamlit run app.py."""
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from analysis import DATA, prepare, select
from charts import (bars, binary_frame, distribution, origins_trend, points, render, share_frame,
                    stacked, trend, format_bars, genre_trend, genre_frame)
from dashboard_data import (AXES, METRICS, ORIGINS, ORIGIN_HELP, CREDITS, REUSE,
                            country_frame, decades, overlap_message, ranked_categories, comparison_rows,
                            FORMAT_METRICS, SOUND_HELP)
from periods import date_label, period_labels, display_comparison
from theme import apply_theme
from ui import (TABLE_LABELS as TABLE_COLUMNS, category_legend, category_message, coverage_note, details, kpi_cards, median_card,
                metric_message, number, numeric_summary, numeric_table, selection_table, share_card,
                shares_summary, simple_comparison, short_median_card, short_share_card, show_table,
                format_cards, reading_note, format_examples)

st.set_page_config(page_title="Billboard #1", page_icon="🎵", layout="wide", initial_sidebar_state="expanded")
apply_theme()
position = components.declare_component("page_position", path=str(Path(__file__).parent / "components" / "navigation"))


@st.cache_data
def load(source_version):
    return prepare(DATA)


try:
    # Lu une seule fois : field_values() le réutilise au lieu de relire l'horodatage.
    SOURCE_VERSION = DATA.stat().st_mtime_ns
    # Invalider aussi les données préparées lorsque les règles de crédit évoluent.
    all_data = load((SOURCE_VERSION, (DATA.parent.parent / "analysis.py").stat().st_mtime_ns,
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
    "Format & son": [("format_trend", "Vue d’ensemble"), ("duration", "Durée & introduction"),
                     ("sound", "Signature sonore"), ("instrumentation", "Instrumentation"),
                     ("genres", "Genres musicaux")],
    "Origines des artistes": [("origins", "Composition et évolution"), ("map", "Pays et territoires")],
    "Profils et création": [("ages", "Âge"), ("formats", "Seul ou à plusieurs"), ("teams", "Équipes"),
                               ("reuse", "Samples et reprises")],
    "Données": [("data_a", "Titres de la période étudiée"), ("data_b", "Titres de la période de référence")],
}
TITLES = {route: label for entries in NAV.values() for route, label in entries}
TITLES.update(summary="Quels repères offrent les titres n°1 ?", format_trend="Comment le format et le son des n°1 évoluent-ils ?",
              duration="Quelle place donner au morceau et à son introduction ?",
              sound="Quelle signature sonore caractérise les n°1 ?", ages="À quel âge les artistes décrochent-ils un n°1 ?",
              teams="Combien de personnes faut-il pour écrire et produire un n°1 ?",
              reuse="Les n°1 s’appuient-ils davantage sur des morceaux existants ?",
              instrumentation="Quels instruments portent le morceau et enrichissent l’arrangement ?",
              genres="Quels genres sont associés aux titres n°1 ?",
              origins="Comment se répartissent les origines, et comment évoluent-elles ?",
              formats="Seul ou à plusieurs : comment se fait un n°1 ?",
              map="Quels pays et territoires sont associés aux n°1 ?")

# Préserver la position et la mémoire de rubrique des sessions ouvertes avant la fusion.
LEGACY_FORMAT_ROUTES = {"intro": "duration", "central": "instrumentation", "presence": "instrumentation"}
st.session_state.route = LEGACY_FORMAT_ROUTES.get(st.session_state.route, st.session_state.route)
remembered_format = st.session_state.get("last_routes", {}).get("Format & son")
if remembered_format in LEGACY_FORMAT_ROUTES:
    st.session_state.last_routes["Format & son"] = LEGACY_FORMAT_ROUTES[remembered_format]
# Une route inconnue depuis l’ouverture de la session y subsiste : navigation() échouerait.
if st.session_state.route not in TITLES:
    st.session_state.route = "summary"
    st.session_state.pop("last_routes", None)


def navigate(route):
    route = LEGACY_FORMAT_ROUTES.get(route, route)
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


def journey(title, steps):
    """Parcours d'un onglet en frise : étapes numérotées reliées dans l'ordre de lecture."""
    html = f'<div class="journey"><div class="journey-title">{escape(title)}</div><ol>'
    for name, question in steps:
        html += f'<li><b>{escape(name)}</b><span>{escape(question)}</span></li>'
    st.markdown(html + '</ol></div>', unsafe_allow_html=True)


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


st.markdown('<div class="brand-banner"><span class="eq"><i></i><i></i><i></i><i></i><i></i></span>'
            '<span class="brand">Billboard <b>#1</b></span>'
            '<span class="brand-sub">Les n°1 du Hot 100 · repères pour un label indépendant</span></div>', unsafe_allow_html=True)

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
    # Effectifs remplis plus bas, une fois les périodes filtrées : visibles sur toutes les pages.
    counts_slot = st.empty()
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
counts_slot.markdown('<div class="period-counts">' + "".join(
    f'<div class="count-{suffix}"><span class="period-{suffix}">{labels[p]}</span><b>{len(d)}</b> titres</div>'
    for (p, d), suffix in zip(frames.items(), "ab")) + '</div>', unsafe_allow_html=True)
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
# Définitions reprises dans Détails depuis ORIGIN_HELP, avec repli littéral.
ORIGIN_FALLBACK = {"Uniquement États-Unis": "toutes les origines renseignées du titre sont américaines",
                   "Mixte": "au moins une origine américaine et au moins une origine étrangère sur le même titre",
                   "Uniquement hors États-Unis": "aucune origine américaine renseignée"}
ORIGIN_CATEGORIES = [f"{label} : {text}" for label in list(ORIGINS.values())[:3]
                     if (text := ORIGIN_HELP.get(label) or ORIGIN_FALLBACK.get(label))] + [
    "Un titre figure dans une seule catégorie ; les trois parts couvrent donc tous les titres dont l’origine est renseignée."]
BASED = {"vocally_based": "Voix", "guitar_based": "Guitare", "piano_keyboard_based": "Piano / claviers", "bass_based": "Basse"}
PRESENT = {"orchestral_strings": "Cordes orchestrales", "horns_winds": "Cuivres / vents"}
BOX_NOTE = "La médiane partage les valeurs en deux moitiés. Q1–Q3 contient la moitié centrale des valeurs ; ce n’est pas un intervalle de confiance."
TREND_NOTE = "Courbe : périodes indiquées sur l’axe. Cartes de comparaison : vos intervalles exacts, parfois différents des décennies. Même filtre de genre."
PARTIAL_NOTE = "Cercles ouverts : couverture partielle. 1958 débute le 4 août ; 2025 s’arrête au 11 janvier. L’agrégat 2020–janv. 2025 diffère de la référence 2020–2024."
filtered = select(all_data, (first, last), genre)


# Colonnes de data/billboard.csv utilisées par chaque vue, rappelées en tête de Détails.
SOURCES = {
    "duration": ["length_sec", "intro_length_sec"],
    "instrumentation": [*BASED, *PRESENT], "genres": ["discogs_genre"],
    "map": ["artist_place_of_origin"], "ages": ["front_person_age", "discogs_genre"],
    "formats": ["artist", "artist_structure"], "reuse": ["sample", "interpolation", "cover"],
}


def sources(route):
    if route == "sound":
        return [st.session_state.get("sonic", "bpm")]
    if route == "teams":
        return ["producers" if st.session_state.get("team_role") == "Producteurs" else "songwriters_w_o_interpolation_sample_credits"]
    if route == "format_trend":
        metric = st.session_state.get("evolution_metric", "length_sec")
        return list(dict.fromkeys(["length_sec", "intro_length_sec", "bpm", "danceability"]
                                  + ([] if metric == "intro_ratio" else [metric])))
    if route == "origins":
        # La vue chronologique n'utilise pas la langue des paroles.
        if st.session_state.get("origins_view", "Évolution") == "Évolution":
            return ["artist_place_of_origin"]
        return ["artist_place_of_origin", "foreign_language"]
    return SOURCES.get(route, [])


@st.cache_data
def raw_data(source_version):
    return pd.read_csv(DATA)


def field_values(column):
    """Valeurs possibles d'une colonne source, décrites à partir du fichier brut."""
    described = {
        "artist_structure": "0 = groupe, 1 = solo, 2 = duo ; +0,5 si un invité est répertorié (0,5 · 1,5 · 2,5)",
        "artist": "crédit complet tel qu’affiché par Billboard, ex. « Rihanna feat. Drake », « Lady Gaga & Bruno Mars »",
        "discogs_genre": "un ou plusieurs genres séparés par « ; », ex. « Rock;Pop »",
        "artist_place_of_origin": "un ou plusieurs pays séparés par « ; », ex. « Canada;United States »",
        "songwriters": "noms séparés par « ; », ex. « Janice Johnson;Perry Kibble »",
        "songwriters_w_o_interpolation_sample_credits": "noms séparés par « ; », sans les auteurs crédités au titre d’un sample ou d’une interpolation",
        "producers": "noms séparés par « ; »",
    }
    values = raw_data(SOURCE_VERSION)[column]
    known = values.dropna()
    if column in described:
        text = described[column]
    elif set(known.unique()) <= {0, 1}:
        text = "0 = non, 1 = oui"
    elif pd.api.types.is_numeric_dtype(known):
        text = f"nombre, de {number(known.min())} à {number(known.max())}"
    else:
        text = f"texte, ex. « {known.iloc[0]} »"
    missing = int(values.isna().sum())
    return text + (f" ; vide = non renseigné ({missing} titre{'s' if missing > 1 else ''})" if missing else "")


def detail_block(columns=None, notes=(), essentials=False):
    used = sources(route)
    source_note = ("**Données Billboard utilisées** · titres datés par `date` (1re semaine au n°1)\n\n"
                   "| Colonne | Valeurs possibles |\n|---|---|\n"
                   + "\n".join(f"| `{c}` | {field_values(c)} |" for c in used)) if used else None
    return details(frames, all_data, genre, columns, notes, essentials, footer=source_note)


def trend_notes(data, captions=True):
    """Alertes de fiabilité toujours visibles ; notes de méthode optionnelles."""
    if captions:
        st.caption(TREND_NOTE)
        st.caption(PARTIAL_NOTE)
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


FORMAT_HISTORY_NOTE = ("Historique : tous les titres du corpus filtré par genre, sur l’ensemble des décennies de 1958 à janvier 2025. "
                       "Les cartes et distributions comparent uniquement les deux périodes sélectionnées.")
INTRO_RATIO_NOTE = ("Part de l’introduction : 100 × intro_length_sec / length_sec, calculée pour chaque titre avec deux valeurs renseignées "
                    "et une durée totale strictement positive. La médiane porte sur ces ratios individuels, pas sur le ratio des médianes. "
                    "Une introduction de zéro seconde est une valeur connue ; une valeur manquante reste exclue.")
FORMAT_BOX_NOTES = [BOX_NOTE, "Quartiles pandas par interpolation linéaire ; moustaches à 1,5 intervalle interquartile. "
                    "Toutes les valeurs exploitables contribuent aux calculs, même si les points extrêmes sont masqués.",
                    FORMAT_HISTORY_NOTE, PARTIAL_NOTE]


def format_history(metric, key):
    label, unit = FORMAT_METRICS[metric]
    data = decades(filtered, column=metric, coverage=(first, last))
    st.caption(FORMAT_HISTORY_NOTE)
    render(trend(data, unit, years_a, years_b, y_title=f"{label} ({unit})"), key)
    st.caption(PARTIAL_NOTE)
    trend_notes(data, captions=False)
    return data


def format_data_links():
    for period, target in zip(frames, ("data_a", "data_b")):
        shortcut("Explorer les titres · " + labels[period], target)


if route == "summary":
    # Parcours de chaque onglet en tête ; les anciens repères chiffrés restent en bas pour mémoire.
    st.subheader("1 · Comment les caractéristiques musicales évoluent-elles ?")
    journey("Format & son · des repères à l’écoute", [
        ("Vue d’ensemble", "Quels repères ont évolué ?"),
        ("Durée & introduction", "Quelle place pour l’introduction ?"),
        ("Signature sonore", "Quel tempo, quelle énergie ?"),
        ("Instrumentation", "Qu’est-ce qui porte l’arrangement ?"),
        ("Genres musicaux", "Quels genres sont associés aux n°1 ?")])
    st.subheader("2 · D’où viennent les artistes associés aux n°1 ?")
    journey("Origines des artistes · de la composition au pays", [
        ("Composition et évolution", "Américains, mixtes ou hors États-Unis ? Et comment ça bouge ?"),
        ("Pays et territoires", "De quels pays viennent les artistes ?")])
    st.subheader("3 · Comment les profils et les modes de création évoluent-ils ?")
    journey("Profils et création · de l’artiste aux coulisses du morceau", [
        ("Âge", "Qui est l’artiste ?"),
        ("Seul ou à plusieurs", "Avec qui sort-il le titre ?"),
        ("Équipes", "Combien de personnes l’ont écrit et produit ?"),
        ("Samples et reprises", "À partir de quoi est-il fait ?")])

    st.divider()
    st.subheader("Repères chiffrés (ancienne synthèse, gardée pour mémoire)")
    kpi_cards([median_card(frames, "length_sec", "Durée médiane", is_duration=True),
               median_card(frames, "intro_length_sec", "Introduction médiane", is_duration=True)], frames)
    st.write("Trois lectures pour situer un projet artistique : caractéristiques musicales, origines, profils et création. Chaque titre compte une fois, à sa première semaine au n°1.")
    st.caption("Observatoire descriptif des seuls n°1 : aucune recette du succès, prédiction ou norme de production. Fichier : 4 août 1958–11 janvier 2025.")
    st.markdown("**1 · Caractéristiques musicales**")
    st.write(metric_message(frames, "length_sec", "Durée", "s") + " " + metric_message(frames, "intro_length_sec", "Introduction", "s"))
    left, right = st.columns(2)
    with left:
        shortcut("Explorer la durée et l’introduction", "duration")
    with right:
        shortcut("Ouvrir la vue d’ensemble de Format & son", "format_trend")
    st.markdown("**2 · Origines**")
    # ORIGINS : clés = valeurs brutes de origin_group, valeurs = libellés affichés.
    us_only, non_us_only = list(ORIGINS)[0], list(ORIGINS)[2]
    kpi_cards([share_card(frames, ORIGINS[us_only], lambda d: d.origin_group.eq(us_only), lambda d: d.origins.map(bool)),
               share_card(frames, ORIGINS[non_us_only], lambda d: d.origin_group.eq(non_us_only), lambda d: d.origins.map(bool))], frames)
    left, right = st.columns(2)
    with left:
        shortcut("Voir la composition et l’évolution", "origins")
    with right:
        shortcut("Comparer les pays et territoires", "map")
    st.markdown("**3 · Profils et création**")
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

elif route == "format_trend":
    essentials = ["length_sec", "intro_length_sec", "bpm", "danceability"]
    format_cards(frames, essentials)
    st.subheader("Évolution historique")
    metric = st.selectbox("Caractéristique à explorer", list(FORMAT_METRICS),
                          format_func=lambda c: FORMAT_METRICS[c][0], key="evolution_metric")
    label, unit = FORMAT_METRICS[metric]
    data = format_history(metric, "format_overview_history")
    reading_note(BOX_NOTE + " La courbe décrit des décennies, les cartes vos deux sélections. Ces repères servent à situer un projet artistique, sans prédire son succès.")
    st.subheader("Poursuivre l’exploration")
    for row in [[("duration", "Durée & introduction", "Comparer la longueur des morceaux et la place de leur introduction."),
                 ("sound", "Signature sonore", "Explorer tempo, énergie, dansabilité, acoustique et niveau sonore.")],
                [("instrumentation", "Instrumentation", "Distinguer ce qui structure le morceau de ce qui enrichit l’arrangement."),
                 ("genres", "Genres musicaux", "Comparer les genres Discogs et suivre leur présence au fil des décennies.")]]:
        for slot, (target, title, description) in zip(st.columns(2), row):
            with slot:
                shortcut(title, target)
                st.caption(description)
    with detail_block({c: FORMAT_METRICS[c][0] for c in dict.fromkeys(essentials + [metric])},
                      FORMAT_BOX_NOTES + [INTRO_RATIO_NOTE]):
        st.markdown("**Mesure sélectionnée · " + label + "**")
        numeric_table(frames, metric, unit)
        temporal_table(data)
        if metric in SOUND_HELP:
            st.write(SOUND_HELP[metric])
        format_examples(frames, metric)
        format_data_links()

elif route in ("ages", "teams"):
    # Profils et création : KPI A/B compact puis graphique. Le reste va dans Détails.
    if route == "ages":
        metric, label, unit = "front_person_age", "Âge médian", "ans"
        notes = ["L’âge retenu est celui de l’artiste principal au moment du n°1 ; pour un groupe, celui de son leader (moyenne s’ils sont plusieurs)."]
    else:
        role = st.radio("Équipe", ["Auteurs", "Producteurs"], horizontal=True, key="team_role", label_visibility="collapsed")
        metric = "writers_original" if role == "Auteurs" else "producer_count"
        label, unit = f"{role} (médiane)", "personnes"
        notes = []
    view = st.radio("Affichage", ["Comparaison des périodes", "Évolution par décennie"], horizontal=True,
                    key="teams_view" if route == "teams" else "ages_view", label_visibility="collapsed")
    kpi_cards([short_median_card(frames, metric, label, unit)], frames, compact=True)
    for name, d in zip(labels.values(), frames.values()):
        if 0 < d[metric].count() < 10:
            st.warning(f"{name} : {d[metric].count()} valeurs seulement, prudence.")
    if view == "Évolution par décennie":
        data = decades(filtered, column=metric, coverage=(first, last))
        render(trend(data, unit, years_a, years_b, y_title=AXES[metric]), f"{route}_trend", height=540)
    else:
        render(distribution(frames, metric, unit), route, height=460)
        values = frames["Référence B"][metric].dropna()
        # Guide écrit dans les mots de la mesure affichée : âge des artistes, nombre d'auteurs ou de producteurs.
        if route == "ages":
            low = "les artistes les plus jeunes et les plus âgés"
            example = (f"*Ex. : en {labels['Référence B']}, la moitié des artistes avaient entre {number(values.quantile(.25))} "
                       f"et {number(values.quantile(.75))} ans au moment de leur n°1.*")
            median = f"la moitié des artistes avaient {number(values.median())} ans ou moins au moment de leur n°1, l’autre moitié {number(values.median())} ans ou plus"
        else:
            who = "auteurs" if metric == "writers_original" else "producteurs"
            low = f"les n°1 avec le moins et le plus de {who}"
            example = (f"*Ex. : en {labels['Référence B']}, la moitié des n°1 comptent entre {number(values.quantile(.25))} "
                       f"et {number(values.quantile(.75))} {who}.*")
            median = f"la moitié des n°1 comptent {number(values.median())} {who} ou moins, l’autre moitié {number(values.median())} ou plus"
        if not len(values):
            example, median = "", "la valeur du milieu"
        st.markdown(f"""
**Comment lire la boîte** · une boîte par période.
- **Le trait au milieu de la boîte** : la médiane ; en {labels['Référence B']}, {median}. Le losange rappelle la même valeur.
- **La boîte** : la moitié des n°1, ceux du milieu (Q1–Q3). {example}
- **Les traits verticaux (moustaches)** : jusqu’où vont {low}, hors cas extrêmes.
- **Les points isolés** : les cas extrêmes, très au-dessus ou très en dessous des autres.{" Ceux qui sortent du cadre sont listés en haut, après ▲." if route == "ages" else ""}

Une boîte plus haute indique des valeurs plus élevées ; une boîte plus étirée, des n°1 plus différents entre eux.
""")
    with detail_block({metric: label}, notes, essentials=True):
        numeric_table(frames, metric, unit)
        if view == "Évolution par décennie":
            temporal_table(data)
        if route == "ages":
            st.markdown("**Âge par genre**")
            for period, d in frames.items():
                grouped = d.explode("genres").groupby("genres").front_person_age.agg(["median", "count"])
                st.caption(labels[period])
                st.dataframe(grouped[grouped["count"] >= 5].sort_values("count", ascending=False).head(12)
                             .rename(columns={"median": "Âge médian (ans)", "count": "Exploitables"}).rename_axis("Genre"), width="stretch")

elif route in ("formats", "reuse"):
    if route == "formats":
        order = ["Solo", "Duo ou groupe constitué", "Featuring", "Co-signature"]
        if any(d.credit_type.eq("Non renseigné").any() for d in frames.values()):
            order.append("Non renseigné")
        data = share_frame(frames, "credit_type")
        category_legend(order, large=True)
        render(stacked(frames, "credit_type", order, vertical=True), route, height=580)
        st.markdown("""
**Comment lire les 4 cases** · chaque n°1 est rangé dans une seule case.
- **Solo** : un seul artiste au crédit, sans invité. *Ex. : Taylor Swift, Harry Styles.*
- **Duo ou groupe constitué** : un groupe ou un duo qui existe en tant que tel, avec un nom et une carrière commune. *Ex. : Maroon 5, Coldplay, Silk Sonic (Bruno Mars et Anderson .Paak réunis sous un seul nom).*
- **Featuring** : un artiste principal invite un autre artiste sur son titre ; le crédit contient « feat. ». *Ex. : Rihanna feat. Drake.*
- **Co-signature** : deux artistes ou plus, chacun avec sa propre carrière, signent le titre à égalité ; le crédit contient « & ». *Ex. : Ariana Grande & Justin Bieber.*
""")
        notes = []
    else:
        columns = REUSE
        data = binary_frame(frames, columns)
        notes = []
        # Une pratique quasi absente des deux périodes écrase l'échelle : on la donne en clair.
        rare = [label for label in columns.values() if data[data["catégorie"].eq(label)].part.fillna(0).max() < 3]
        shown = [label for label in columns.values() if label not in rare]
        render(points(data, frames, shown, y_title="Pratique"), route, height=140 + 90 * len(shown))
        for label in rare:
            counts = data[data["catégorie"].eq(label)].set_index("période").reindex(list(frames))
            kpi_cards([(f"{label} · quasi absente des n°1",
                        [f"{int(r.effectif)} titre{'s' if r.effectif > 1 else ''} ({number(r.part)} %)" for r in counts.itertuples()],
                        None)], frames, compact=True, tone="alert")
        st.markdown("**Comment lire les flèches** · vers la droite, la pratique progresse ; vers la gauche, elle recule. "
                    "Plus la flèche est longue, plus l’écart entre les deux périodes est grand.")
        st.markdown("""
**Les 3 pratiques** · un même titre peut en cumuler plusieurs, le total ne fait donc pas 100 %.
- **Sample** : un extrait d’un enregistrement existant est repris tel quel dans le morceau. *Ex. : Not Like Us, Kendrick Lamar.*
- **Interpolation** : une mélodie ou des paroles d’un autre titre sont rejouées ou réécrites, sans reprendre l’enregistrement. *Ex. : A Bar Song (Tipsy), Shaboozey.*
- **Reprise** : une nouvelle version d’un titre existant. *Ex. : Lady Marmalade, Christina Aguilera, Lil’ Kim, Mýa & Pink.*
""")
    with detail_block(notes=notes, essentials=True):
        simple_comparison(data, frames, order if route == "formats" else list(columns.values()),
                          "Type de crédit" if route == "formats" else "Pratique")

elif route == "duration":
    format_cards(frames, ["length_sec", "intro_length_sec", "intro_ratio"])
    st.write(metric_message(frames, "length_sec", "Durée totale", "s") + " "
             + metric_message(frames, "intro_length_sec", "Introduction", "s"))
    st.caption("Un écart entre médianes ne signifie pas que tous les titres évoluent dans le même sens.")
    st.subheader("Durée totale · comparaison des distributions")
    render(distribution(frames, "length_sec", "s", points=False), "format_duration_distribution")
    st.subheader("Introduction · comparaison des distributions")
    render(distribution(frames, "intro_length_sec", "s", points=False), "format_intro_distribution")
    st.subheader("Évolution historique")
    metric = st.selectbox("Mesure à suivre", ["length_sec", "intro_length_sec", "intro_ratio"],
                          format_func=lambda c: FORMAT_METRICS[c][0], key="duration_metric")
    data = format_history(metric, "format_duration_history")
    reading_note(BOX_NOTE + " Les deux distributions ont des échelles distinctes, en secondes. "
                 "La part de l’introduction rapporte son temps à celui du morceau, titre par titre ; sa médiane s’exprime en %.")
    with detail_block({c: FORMAT_METRICS[c][0] for c in ["length_sec", "intro_length_sec", "intro_ratio"]},
                      FORMAT_BOX_NOTES + [INTRO_RATIO_NOTE, "L’introduction peut inclure un hook initial ; sa durée ne mesure pas nécessairement l’attente avant la voix."]):
        for column in ["length_sec", "intro_length_sec", "intro_ratio"]:
            st.markdown("**" + FORMAT_METRICS[column][0] + "**")
            numeric_table(frames, column, FORMAT_METRICS[column][1])
        temporal_table(data)
        format_examples(frames, metric)
        format_data_links()

elif route == "sound":
    metric = st.selectbox("Caractéristique sonore", list(SOUND_HELP),
                          format_func=lambda c: METRICS[c][0], key="sonic")
    label, unit = METRICS[metric]
    format_cards(frames, [metric])
    st.write(metric_message(frames, metric, label, unit))
    st.subheader("Distribution · comparaison des périodes")
    render(distribution(frames, metric, unit), "format_sound_distribution")
    st.subheader("Évolution historique")
    data = format_history(metric, "format_sound_history")
    reading_note(SOUND_HELP[metric] + " " + BOX_NOTE)
    with detail_block({metric: label}, FORMAT_BOX_NOTES + [SOUND_HELP[metric],
                      "Énergie, dansabilité et caractère acoustique : scores Spotify sur 100 dans le fichier. BPM et dB conservent leur propre échelle."]):
        numeric_table(frames, metric, unit)
        temporal_table(data)
        format_examples(frames, metric)
        format_data_links()

elif route == "instrumentation":
    st.caption("Un rôle central décrit ce qui porte le morceau. Une présence décrit une couleur de l’arrangement, sans présumer un rôle central.")
    results = []
    for title, columns, key in [("Ce qui structure le morceau", BASED, "format_central_bars"),
                                ("Ce qui est présent dans l’arrangement", PRESENT, "format_presence_bars")]:
        st.subheader(title)
        data, order = binary_frame(frames, columns), list(columns.values())
        st.write(category_message(data, frames, order))
        render(format_bars(data, frames, order), key)
        shares_summary(data, frames, order)
        for period, frame in frames.items():
            small = [f"{label} ({frame[c].count()})" for c, label in columns.items() if 0 < frame[c].count() < 10]
            if small:
                st.warning(labels[period] + " · moins de 10 valeurs renseignées : " + ", ".join(small) + ". Prudence.")
        results.append((title, data, order))
    reading_note("Ces indicateurs sont cumulables : un titre peut avoir une voix et une basse centrales, avec des cordes présentes. "
                 "Les parts ne forment pas une répartition à 100 %. Chaque barre rapporte les titres concernés à tous les titres filtrés de sa période ; "
                 "le survol précise les effectifs et l’écart en points (référence − étudiée).")
    with detail_block({**BASED, **PRESENT}, ["Sources binaires : 1 = oui, 0 = non ; vide = inconnu. Un indicateur entièrement manquant est indisponible, pas nul.",
                      "Les valeurs inconnues restent dans le dénominateur ; les taux ne portent donc pas uniquement sur les titres renseignés.",
                      "Rôle central et présence ne mesurent ni la complexité ni la qualité musicale."]):
        for title, data, order in results:
            st.markdown("**" + title + "**")
            simple_comparison(data, frames, order, "Instrument / section")
        format_data_links()

elif route == "genres":
    view = st.radio("Lecture des genres", ["Comparaison des périodes", "Évolution historique"],
                    horizontal=True, key="genres_view")
    st.caption("Plusieurs genres Discogs peuvent être associés à un titre : additionner leurs parts peut dépasser 100 %. Aucune autre source ne complète les genres manquants.")
    coverage_note(frames, column="discogs_genre", label="Couverture Discogs des deux sélections")
    data = genre_frame(frames)
    order = ranked_categories(data[data["catégorie"].ne("Non renseigné")], missing=None)
    temporal = None
    if view == "Comparaison des périodes":
        st.subheader("Genres les plus représentés")
        st.caption("Top 9 selon la moyenne des parts des périodes disponibles, avec le même poids pour chaque période.")
        if order:
            st.write(category_message(data, frames, order))
            render(format_bars(data, frames, order), "format_genres_bars")
            shares_summary(data, frames, order)
        else:
            st.info("Aucun genre musical renseigné dans les deux périodes sélectionnées.")
        st.subheader("À part · genres non renseignés")
        kpi_cards([share_card(frames, "Non renseigné", lambda d: d.genres.map(lambda g: g == ["Non renseigné"]))], frames, tone="format-cards")
        reading_note("Chaque barre indique la part de tous les titres de la période associés au genre. "
                     "Le survol donne les effectifs et l’écart en points (référence − étudiée). Les titres sans genre figurent séparément et restent au dénominateur.")
    else:
        selected_genre = st.selectbox("Genre à suivre dans le temps", all_genres, key="genre_history")
        temporal = decades(filtered, genre=selected_genre, coverage=(first, last))
        st.caption(FORMAT_HISTORY_NOTE)
        render(genre_trend(temporal, selected_genre, years_a, years_b), "format_genres_history")
        st.caption(PARTIAL_NOTE)
        trend_notes(temporal, captions=False)
        if genre != "Tous les genres":
            st.caption("Filtre global actif : « " + genre + " ». La courbe décrit les co-genres de ces titres ; suivre le genre filtré lui-même donne 100 % dans chaque décennie renseignée.")
        reading_note("Chaque point rapporte les titres associés au genre choisi à tous les titres filtrés de la décennie. "
                     "Le survol donne le nombre de titres concernés et le dénominateur. Cercles ouverts : périodes partielles. "
                     "Une décennie sans genre exploitable est laissée sans point ; « Non renseigné » suit les absences de genre, sans en inventer.")
    with detail_block({"discogs_genre": "Genre Discogs"}, [
            "Genres multiples séparés par point-virgule, nettoyés et dédupliqués par titre. Seul discogs_genre est utilisé ; jamais cdr_genre.",
            "Classement équilibré entre périodes disponibles, égalités alphabétiques. Une catégorie absente d’une période renseignée vaut zéro ; une période vide est indisponible.",
            "Pour un genre musical, une période ou décennie dont tous les genres manquent est indisponible. La part de « Non renseigné » reste calculable sur tous les titres.",
            FORMAT_HISTORY_NOTE, PARTIAL_NOTE]):
        if temporal is not None:
            temporal_table(temporal)
        else:
            simple_comparison(data, frames, sorted(data["catégorie"].unique()) or ["Non renseigné"], "Genre Discogs")
        format_data_links()

elif route == "origins":
    column, order = "origin_group", list(ORIGINS.values())
    # Clé brute retrouvée depuis le libellé : origin_group ne contient pas les libellés.
    unclassified = next((key for key, label in ORIGINS.items() if label == "Non classable"), None)
    if unclassified is None or not any(d.origin_group.eq(unclassified).any() for d in frames.values()):
        order = [label for label in order if label != "Non classable"]
    view = st.radio("Analyse des origines", ["Évolution", "Composition"],
                    horizontal=True, key="origins_view", label_visibility="collapsed")
    category_legend(order, ORIGIN_HELP)
    if view == "Évolution":
        series = [(ORIGINS[key], decades(filtered, origin=key, coverage=(first, last)))
                  for key in list(ORIGINS)[:3]]
        render(origins_trend(series), "origin_trend", height=480)
        st.markdown("""
**Comment lire** · une courbe par catégorie, chaque titre comptant dans une seule d'entre elles.
- **Les cercles ouverts** signalent une période incomplète.
- **Une courbe interrompue** signale une période sans origine exploitable.
- Ce qui compte n'est pas le niveau d'une courbe, mais **l'écart entre les trois**.
""")
        # Une seule alerte, sur la borne basse des trois parts, appariée par libellé de période.
        by_period = pd.concat([d.set_index("label").valid for _, d in series], axis=1).min(axis=1)
        coverage = series[0][1].assign(valid=series[0][1].label.map(by_period)).dropna(subset=["valid"])
        trend_notes(coverage.astype({"valid": int}), captions=False)
    else:
        data = share_frame(frames, column)
        data["catégorie"] = data["catégorie"].replace(ORIGINS)
        # Même hauteur que la courbe ; 480 px laissent son étiquette au segment à 5 %.
        render(stacked(frames, column, order, vertical=True), "origins", height=480)
        st.markdown("**Comment lire les barres** · une barre par période, représentant tous ses titres "
                    "dont l’origine est renseignée. Les trois catégories sont exclusives : chaque titre "
                    "figure dans une seule, et les trois parts couvrent donc l’ensemble. Leur définition "
                    "exacte est dans la légende au-dessus, et dans Détails.")
    if any(d.origins.map(bool).sum() < len(d) for d in frames.values()):
        coverage_note(frames, list_column="origins", label="Origines exploitables")
    with detail_block(notes=[ORIGIN_NOTE] + ([TREND_NOTE] if view == "Évolution" else ORIGIN_CATEGORIES),
                      essentials=True):
        if view == "Évolution":
            for label, data in series:
                st.markdown(f"**{label}**")
                temporal_table(data)
        else:
            st.dataframe(display_comparison(comparison_rows(data, frames, order), frames),
                         hide_index=True, width="stretch")
            st.markdown("**Paroles non anglaises**")
            st.caption("22 titres sur tout le fichier, et la langue n’est pas précisée : effectif trop "
                       "faible pour en conclure quoi que ce soit.")
            kpi_cards([share_card(frames, "Présence de paroles non anglaises",
                                  lambda d: d.foreign_language.eq(1), lambda d: d.foreign_language.notna())], frames)

elif route == "map":
    data = country_frame(frames, all_data)
    comparisons = data.rename(columns={"pays": "catégorie"})
    # Sélecteur en tête : choisir un pays remplace le classement par deux cartes chiffrées.
    country = st.selectbox("Retrouver un pays ou territoire", ["Tous"] + sorted(data.pays.unique()), key="map_country")
    order = [country] if country != "Tous" else ranked_categories(comparisons, limit=10, missing=None)
    # Carte choroplèthe écartée : les États-Unis saturaient l'échelle. world_map() reste
    # dans charts.py comme trace de l'arbitrage.
    if country != "Tous":
        # Une seule catégorie ne fait pas un graphique : deux chiffres suffisent.
        rows = data[data.pays.eq(country)].set_index("période").reindex(list(frames))
        kpi_cards([(f"{country} · part des titres n°1",
                    [f"{number(r.part)} % ({int(r.effectif)}/{int(r.total)} titres)" if pd.notna(r.part) else "Non disponible"
                    for r in rows.itertuples()], None)], frames, compact=True)
        shares_summary(comparisons, frames, [country])
    else:
        render(bars(comparisons, frames, order), route)
        st.markdown("**Comment lire les barres** · les dix pays les plus représentés, classés sur la "
                    "moyenne des deux périodes à poids égaux. Un titre peut être associé à plusieurs "
                    "pays : le total dépasse donc 100 %.")
    with detail_block(notes=[ORIGIN_NOTE,
                        "Un titre peut être associé à plusieurs pays : le total dépasse 100 %. Un pays documenté mais absent de la sélection vaut zéro.",
                        "« Unites States » est normalisé en United States. « Columbia » est normalisé en Colombia sur le titre We Don't Talk About Bruno : correction étayée par les biographies Disney du casting, sans vérification exhaustive de chaque origine du casting."],
                    essentials=True):
        coverage_note(frames, list_column="origins", label="Origines exploitables")
        st.dataframe(display_comparison(comparison_rows(comparisons, frames, sorted(data.pays.unique())), frames),
                    hide_index=True, width="stretch")

elif route in ("data_a", "data_b"):
    period = "Période A" if route == "data_a" else "Référence B"
    data = frames[period].sort_values(["date", "song", "artist"], kind="stable")
    query = st.text_input("Rechercher un titre ou un artiste", key=f"search_{route}")
    if query.strip():
        data = data[data.song.str.contains(query.strip(), case=False, regex=False, na=False)
                    | data.artist.str.contains(query.strip(), case=False, regex=False, na=False)]
    view = selection_table(data, [*TABLE_COLUMNS, "front_person_age", "artist_format", "collaboration", "writers_original",
                                  "producer_count", "sample", "interpolation", "cover"])
    show_table(view, route, labels[period])


def back_top():
    st.session_state.scroll_token += 1


st.button("Haut", key="back_top", icon=":material/arrow_upward:", on_click=back_top, help="Retour en haut de la page")
