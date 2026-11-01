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
                format_cards, reading_note, format_examples, format_missing_genres, existing_reading)

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
    "Vue d’ensemble": [("summary", "Explorer les n°1")],
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

FORMAT_ROUTES = ("format_trend", "duration", "sound", "instrumentation", "genres")
is_format = st.session_state.route in FORMAT_ROUTES


def format_words(text):
    return (text.replace("PÉRIODES", "ANNÉES").replace("Périodes", "Années").replace("périodes", "années")
            .replace("Période", "Année").replace("période", "année"))


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
    def rows():
        with st.container(key="primary_nav", horizontal=True, gap="small"):
            for index, group in enumerate(NAV):
                # Le nom interne de la rubrique reste stable pour les sessions ouvertes.
                title = "Explorer les n°1" if group == "Vue d’ensemble" else group
                st.button(title, key=f"group_{index}", on_click=open_group, args=(group,),
                          type="primary" if group == active_group else "tertiary", width="content")
        if len(NAV[active_group]) > 1:
            with st.container(key="secondary_nav", horizontal=True, gap="small"):
                for route, title in NAV[active_group]:
                    if route in ("data_a", "data_b"):
                        title = labels["Période A" if route == "data_a" else "Référence B"]
                    st.button(title, key=f"nav_{route}", on_click=navigate, args=(route,), width="content",
                              type="primary" if st.session_state.route == route else "tertiary")
    with st.container(key="dashboard_navigation"):
        rows()


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
    st.subheader("ANNÉES" if is_format else "PÉRIODES")
    mode = st.radio("Découpage", ["Décennies", "Intervalles d’années"], key="mode")
    if mode == "Décennies":
        options = [*decs, "recent"]
        a = st.selectbox("Année étudiée" if is_format else "Période étudiée", options, format_func=period_label, key="decade_a")
        b = st.selectbox("Année de référence" if is_format else "Période de référence", options, format_func=period_label, key="decade_b")
        years_a = (2020, 2024) if a == "recent" else clamp(a)
        years_b = (2020, 2024) if b == "recent" else clamp(b)
    else:
        years_a = st.slider("Année étudiée" if is_format else "Période étudiée", first, last, key="years_a")
        years_b = st.slider("Année de référence" if is_format else "Période de référence", first, last, key="years_b")
    # Effectifs remplis plus bas, une fois les périodes filtrées : visibles sur toutes les pages.
    counts_slot = st.empty()
    overlap = overlap_message(years_a, years_b)
    if overlap:
        st.warning(format_words(overlap) if is_format else overlap)
    if any(y[0] <= 1958 <= y[1] for y in (years_a, years_b)):
        st.caption("1958 : à partir du 4 août seulement.")
    if any(y[0] <= 2025 <= y[1] for y in (years_a, years_b)):
        st.warning("2025 : un seul titre, jusqu’au 11 janvier. " + ("Année partielle." if is_format else "Période partielle."))
    st.divider()
    st.subheader("GENRES")
    all_genres = sorted(set(all_data.genres.explode().dropna()))
    genre = st.selectbox("Genre Discogs", ["Tous les genres"] + all_genres, key="genre")
    if genre == "Non renseigné":
        st.caption("« Non renseigné » = absence de genre Discogs ; ce n’est pas un genre musical.")
    elif genre != "Tous les genres":
        text = "Ce filtre exclut les titres sans genre Discogs. Même filtre pour les deux périodes et les courbes."
        st.caption(format_words(text) if is_format else text)

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
if is_format and genre != "Tous les genres":
    st.caption("Genre Discogs : " + genre)
for label, data in frames.items():
    if data.empty:
        if is_format and all(d.empty for d in frames.values()):
            if label == next(iter(frames)):
                st.info("Aucun titre pour ces deux années et ce genre.")
        else:
            text = f"{labels[label]} : aucun titre pour cette sélection. Les résultats de l’autre période restent consultables."
            st.info(format_words(text) if is_format else text)
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
        st.caption(PARTIAL_NOTE)
    small = data[(data.valid > 0) & (data.valid < 10)]
    if len(small):
        st.warning("Moins de 10 valeurs exploitables : " + ", ".join(f"{r.label} ({r.valid}/{r.total})" for r in small.itertuples()) + ". Prudence.")
    missing = data[data.valid.eq(0)]
    if len(missing):
        st.caption("Périodes sans valeur exploitable, non reliées : " + ", ".join(missing.label))


def temporal_table(data, for_format=False):
    keep = [c for c in ["label", "value", "q1", "q3", "count", "valid", "total", "partial"] if c in data]
    if for_format and "count" in data:
        keep = [c for c in keep if c not in ("q1", "q3")]
    st.dataframe(data[keep].rename(columns={"label": "Années couvertes" if for_format else "Période couverte", "value": "Médiane / part (%)", "q1": "Q1", "q3": "Q3",
                                          "count": "Titres concernés", "valid": "Exploitables", "total": "Titres", "partial": "Partielle"}), hide_index=True, width="stretch")


INTRO_RATIO_NOTE = ("Part de l’introduction : 100 × intro_length_sec / length_sec, calculée pour chaque titre avec deux valeurs renseignées "
                    "et une durée totale strictement positive. La médiane porte sur ces ratios individuels, pas sur le ratio des médianes. "
                    "Une introduction de zéro seconde est une valeur connue ; une valeur manquante reste exclue.")
FORMAT_BOX_NOTES = [BOX_NOTE, "Quartiles pandas par interpolation linéaire ; moustaches à 1,5 intervalle interquartile. "
                    "Toutes les valeurs exploitables contribuent aux calculs, même si les points extrêmes sont masqués.",
                    PARTIAL_NOTE]


def format_history(metric, key):
    label, unit = FORMAT_METRICS[metric]
    data = decades(filtered, column=metric, coverage=(first, last))
    render(trend(data, unit, years_a, years_b, y_title=f"{label} ({unit})"), key)
    format_history_notes(data)
    return data


def format_data_links():
    for period, target in zip(frames, ("data_a", "data_b")):
        shortcut("Explorer les titres · " + labels[period], target)


def format_history_notes(data):
    small = data[(data.valid > 0) & (data.valid < 10)]
    if len(small):
        st.warning("Moins de 10 valeurs : " + ", ".join(f"{r.label} ({r.valid}/{r.total})" for r in small.itertuples()))
    missing = data[data.valid.eq(0)]
    if len(missing):
        st.caption("Années sans valeur exploitable : " + ", ".join(missing.label))


def format_title(text):
    st.markdown('<h2 class="format-chart-title">' + escape(text) + '</h2>', unsafe_allow_html=True)


def format_selection():
    st.caption(" · ".join(f"{labels[p]} : {len(d)} titres" for p, d in frames.items()))


def format_comparison_table(data, order):
    table = comparison_rows(data, frames, order).drop(columns="B − A (points)")
    st.dataframe(display_comparison(table, frames), hide_index=True, width="stretch")


FORMAT_METHOD = ["Boîte : moitié centrale Q1–Q3 ; losange : médiane ; moustaches : 1,5 intervalle interquartile. Q1–Q3 n’est pas un intervalle de confiance.",
                 "Médianes sur les valeurs connues ; parts sur tous les titres filtrés. Début : 4 août 1958 ; fin : 11 janvier 2025."]


if route == "summary":
    # L’accueil se limite aux trois parcours, avec leurs étapes originales.
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

elif route == "format_trend":
    essentials = ["length_sec", "intro_length_sec", "bpm", "danceability"]
    format_cards(frames, essentials)
    metric = st.selectbox("Mesure", list(FORMAT_METRICS),
                          format_func=lambda c: FORMAT_METRICS[c][0], key="evolution_metric")
    label, unit = FORMAT_METRICS[metric]
    format_title(label + " · évolution")
    data = format_history(metric, "format_overview_history")
    reading_note("Courbe : médiane par décennie ; bande : moitié centrale Q1–Q3. Les cartes comparent les années choisies.")
    with detail_block(notes=FORMAT_METHOD + [format_words(PARTIAL_NOTE)], essentials=True):
        numeric_table(frames, metric, unit, period_column="Année")
        temporal_table(data, for_format=True)
        if metric in SOUND_HELP:
            st.caption(SOUND_HELP[metric])
        if metric == "intro_ratio":
            st.caption(INTRO_RATIO_NOTE)
        format_examples(frames, metric)
        # Raccourcis conservés dans le volet, la navigation reste accessible au-dessus.
        for target, title in NAV["Format & son"][1:]:
            shortcut(title, target)
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
        existing_reading(f"""
**Comment lire la boîte** · une boîte par période.
- **Le trait au milieu de la boîte** : la médiane ; en {labels['Référence B']}, {median}. Le losange rappelle la même valeur.
- **La boîte** : la moitié des n°1, ceux du milieu (Q1–Q3). {example}
- **Les traits verticaux (moustaches)** : jusqu’où vont {low}, hors cas extrêmes.
- **Les points isolés** : les cas extrêmes, très au-dessus ou très en dessous des autres.{" Ceux qui sortent du cadre sont listés en haut, après ▲." if route == "ages" else ""}

Une boîte plus haute indique des valeurs plus élevées ; une boîte plus étirée, des n°1 plus différents entre eux.
""", key=route)
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
        existing_reading("""
**Comment lire les 4 cases** · chaque n°1 est rangé dans une seule case.
- **Solo** : un seul artiste au crédit, sans invité. *Ex. : Taylor Swift, Harry Styles.*
- **Duo ou groupe constitué** : un groupe ou un duo qui existe en tant que tel, avec un nom et une carrière commune. *Ex. : Maroon 5, Coldplay, Silk Sonic (Bruno Mars et Anderson .Paak réunis sous un seul nom).*
- **Featuring** : un artiste principal invite un autre artiste sur son titre ; le crédit contient « feat. ». *Ex. : Rihanna feat. Drake.*
- **Co-signature** : deux artistes ou plus, chacun avec sa propre carrière, signent le titre à égalité ; le crédit contient « & ». *Ex. : Ariana Grande & Justin Bieber.*
""", key=route)
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
        existing_reading("**Comment lire les flèches** · vers la droite, la pratique progresse ; vers la gauche, elle recule. "
                    "Plus la flèche est longue, plus l’écart entre les deux périodes est grand.", key=route)
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
    view = st.radio("Graphique", ["Durée", "Introduction", "Évolution"], horizontal=True, key="duration_view")
    data = None
    if view == "Évolution":
        metric = st.selectbox("Mesure à suivre", ["length_sec", "intro_length_sec", "intro_ratio"],
                              format_func=lambda c: FORMAT_METRICS[c][0], key="duration_metric")
        format_title(FORMAT_METRICS[metric][0] + " · évolution")
        data = format_history(metric, "format_duration_history")
        reading_note("Médiane par décennie ; bande Q1–Q3. Le ratio d’introduction est calculé titre par titre.")
    else:
        metric = "length_sec" if view == "Durée" else "intro_length_sec"
        format_title(FORMAT_METRICS[metric][0] + " · distribution")
        render(distribution(frames, metric, "s", points=False), "format_duration_distribution")
        reading_note("Losange : médiane ; boîte : moitié centrale Q1–Q3. Axe en secondes, propre à la mesure choisie.")
    with detail_block(notes=FORMAT_METHOD + ["Ratio par titre : 100 × introduction / durée, avec durée > 0 et deux valeurs connues. Un zéro est conservé ; un manque est exclu.",
                      "L’introduction peut inclure un hook ; elle ne mesure pas nécessairement l’attente avant la voix.", format_words(PARTIAL_NOTE)], essentials=True):
        numeric_table(frames, metric, FORMAT_METRICS[metric][1], period_column="Année")
        if data is not None:
            temporal_table(data, for_format=True)
        format_examples(frames, metric)
        format_data_links()

elif route == "sound":
    metric = st.selectbox("Mesure", list(SOUND_HELP), format_func=lambda c: METRICS[c][0], key="sonic",
                          help=SOUND_HELP[st.session_state.get("sonic", "bpm")])
    label, unit = METRICS[metric]
    format_cards(frames, [metric])
    view = st.radio("Graphique", ["Distribution", "Évolution"], horizontal=True, key="sound_view")
    format_title(label + (" · distribution" if view == "Distribution" else " · évolution"))
    data = None
    if view == "Distribution":
        render(distribution(frames, metric, unit), "format_sound_distribution")
        reading_note("Losange : médiane ; boîte : moitié centrale Q1–Q3 ; points isolés : valeurs extrêmes.")
    else:
        data = format_history(metric, "format_sound_history")
        reading_note("Médiane par décennie ; bande Q1–Q3.")
    with detail_block(notes=[SOUND_HELP[metric], *FORMAT_METHOD, format_words(PARTIAL_NOTE)], essentials=True):
        numeric_table(frames, metric, unit, period_column="Année")
        if data is not None:
            temporal_table(data, for_format=True)
        format_examples(frames, metric)
        format_data_links()

elif route == "instrumentation":
    view = st.radio("Analyse", ["Rôle central", "Présence"], horizontal=True, key="instrument_view")
    columns = BASED if view == "Rôle central" else PRESENT
    title = "Ce qui structure le morceau" if view == "Rôle central" else "Ce qui est présent dans l’arrangement"
    format_title(title)
    format_selection()
    data, order = binary_frame(frames, columns), list(columns.values())
    render(format_bars(data, frames, order), "format_instrument_bars")
    for period, frame in frames.items():
        small = [f"{label} ({frame[c].count()})" for c, label in columns.items() if 0 < frame[c].count() < 10]
        if small:
            st.warning(labels[period] + " · moins de 10 valeurs renseignées : " + ", ".join(small) + ". Prudence.")
    reading_note("Central : porte le morceau ; présent : enrichit l’arrangement. Parts cumulables, sur tous les titres ; elles peuvent dépasser 100 %.")
    with detail_block(notes=["1 = oui ; 0 = non ; vide = inconnu. Tous les titres filtrés restent au dénominateur. Un indicateur entièrement inconnu est indisponible.",
                      "Rôle central et présence ne mesurent ni la complexité ni la qualité musicale."], essentials=True):
        format_comparison_table(data, order)
        format_data_links()

elif route == "genres":
    view = st.radio("Graphique", ["Comparaison des périodes", "Évolution historique"],
                    format_func=lambda v: "Comparer les années" if v == "Comparaison des périodes" else "Historique",
                    horizontal=True, key="genres_view")
    data = genre_frame(frames)
    order = ranked_categories(data[data["catégorie"].ne("Non renseigné")], missing=None)
    temporal = None
    if view == "Comparaison des périodes":
        format_title("Genres les plus représentés")
        format_selection()
        if order:
            render(format_bars(data, frames, order), "format_genres_bars")
        else:
            st.info("Aucun genre musical renseigné dans les deux années sélectionnées.")
        format_missing_genres(frames)
        reading_note("Top 9 à poids égal entre les deux sélections. Genres cumulables ; titres sans genre affichés à part et conservés au dénominateur.")
    else:
        selected_genre = st.selectbox("Genre à suivre", all_genres, key="genre_history")
        format_title(selected_genre + " · évolution")
        temporal = decades(filtered, genre=selected_genre, coverage=(first, last))
        render(genre_trend(temporal, selected_genre, years_a, years_b), "format_genres_history")
        format_history_notes(temporal)
        reading_note("Part des titres associés au genre choisi, par décennie. Un filtre global suit ses co-genres ; le genre filtré lui-même vaut 100 % s’il est renseigné.")
    with detail_block(notes=["Discogs seul ; genres multiples dédupliqués par titre. Top 9 : moyenne des parts disponibles, poids égaux, égalités alphabétiques.",
            "Absence connue = zéro ; sélection vide ou genre musical entièrement inconnu = indisponible. Non renseigné reste calculable sur tous les titres.",
            format_words(PARTIAL_NOTE)], essentials=True):
        coverage_note(frames, column="discogs_genre", label="Couverture Discogs")
        if temporal is not None:
            temporal_table(temporal, for_format=True)
        else:
            format_comparison_table(data, sorted(data["catégorie"].unique()) or ["Non renseigné"])
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
        existing_reading("""
**Comment lire** · une courbe par catégorie, chaque titre comptant dans une seule d'entre elles.
- **Les cercles ouverts** signalent une période incomplète.
- **Une courbe interrompue** signale une période sans origine exploitable.
- Ce qui compte n'est pas le niveau d'une courbe, mais **l'écart entre les trois**.
""", key=route)
        # Une seule alerte, sur la borne basse des trois parts, appariée par libellé de période.
        by_period = pd.concat([d.set_index("label").valid for _, d in series], axis=1).min(axis=1)
        coverage = series[0][1].assign(valid=series[0][1].label.map(by_period)).dropna(subset=["valid"])
        trend_notes(coverage.astype({"valid": int}), captions=False)
    else:
        data = share_frame(frames, column)
        data["catégorie"] = data["catégorie"].replace(ORIGINS)
        # Même hauteur que la courbe ; 480 px laissent son étiquette au segment à 5 %.
        render(stacked(frames, column, order, vertical=True), "origins", height=480)
        existing_reading("**Comment lire les barres** · une barre par période, représentant tous ses titres "
                    "dont l’origine est renseignée. Les trois catégories sont exclusives : chaque titre "
                    "figure dans une seule, et les trois parts couvrent donc l’ensemble. Leur définition "
                    "exacte est dans la légende au-dessus, et dans Détails.", key=route)
    if any(d.origins.map(bool).sum() < len(d) for d in frames.values()):
        coverage_note(frames, list_column="origins", label="Origines exploitables")
    with detail_block(notes=[ORIGIN_NOTE] + ([] if view == "Évolution" else ORIGIN_CATEGORIES),
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
        existing_reading("**Comment lire les barres** · les dix pays les plus représentés, classés sur la "
                    "moyenne des deux périodes à poids égaux. Un titre peut être associé à plusieurs "
                    "pays : le total dépasse donc 100 %.", key=route)
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
