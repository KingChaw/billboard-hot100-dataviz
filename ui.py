"""Présentation française, rappel compact et détails repliés."""
from contextlib import contextmanager
from html import escape

import pandas as pd
import streamlit as st

from charts import CATEGORY_COLORS
from dashboard_data import METRICS, CREDITS, comparison_rows


def number(value, digits=1):
    if pd.isna(value):
        return "Non disponible"
    return f"{value:,.{digits}f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",") if digits else f"{value:,.0f}".replace(",", " ")


def duration(value):
    if pd.isna(value):
        return "Non disponible"
    minutes, seconds = divmod(float(value), 60)
    return f"{int(minutes)} min {number(seconds)} s" if minutes else f"{number(seconds)} s"


def header(years_a, years_b, frames, genre):
    items = []
    for (period, data), years, suffix in zip(frames.items(), [years_a, years_b], ["a", "b"]):
        items.append(f'<span><b class="period-{suffix}">{"A" if suffix == "a" else "B"} · {years[0]}–{years[1]}</b>'
                     f'<small>{len(data)} titres</small></span>')
    items.append(f'<span>{escape(genre)}</span>')
    st.markdown('<div class="selection">' + ''.join(items) + '</div>', unsafe_allow_html=True)


def kpi_cards(cards):
    html = '<div class="kpi-grid' + (' single' if len(cards) == 1 else '') + '">'
    for title, values, foot in cards:
        html += f'<article class="kpi"><h3>{escape(title)}</h3><div class="kpi-values">'
        for value, label, suffix in zip(values, ["A", "B"], ["a", "b"]):
            html += (f'<div><span class="period-label period-{suffix}">{label}</span>'
                     f'<div class="kpi-value">{escape(value)}</div></div>')
        html += '</div>' + (f'<div class="kpi-foot">{escape(foot)}</div>' if foot else '') + '</article>'
    st.markdown(html + '</div>', unsafe_allow_html=True)


def median_card(frames, column, title, unit="", is_duration=False):
    values, medians = [], []
    for data in frames.values():
        value = data[column].dropna().median()
        medians.append(value)
        values.append(duration(value) if is_duration else number(value) + (f" {unit}" if pd.notna(value) else ""))
    delta = medians[1] - medians[0]
    foot = "Écart B − A : non disponible"
    if pd.notna(delta):
        foot = f"B − A : {'+' if delta > 0 else ''}{number(delta)} {'s' if is_duration else unit}"
    counts = [f"{p} : {d[column].count()}/{len(d)} exploitables" for p, d in zip(("A", "B"), frames.values())]
    foot += " · " + " · ".join(counts)
    return title, values, foot


def share_card(frames, title, predicate, valid_predicate=None):
    values, parts, counts = [], [], []
    for label, data in zip(("A", "B"), frames.values()):
        valid = int(valid_predicate(data).sum()) if valid_predicate else len(data)
        count = int(predicate(data).sum())
        share = 100 * count / len(data) if len(data) and valid else float("nan")
        parts.append(share)
        counts.append(f"{label} : {count}/{len(data)} titres · {valid} renseignés")
        values.append(number(share) + (" %" if pd.notna(share) else ""))
    delta = parts[1] - parts[0]
    foot = "B − A : " + (f"{'+' if delta > 0 else ''}{number(delta)} points" if pd.notna(delta) else "non disponible")
    return title, values, foot + " · " + " · ".join(counts)


def metric_message(frames, column, label, unit):
    a, b = [d[column].dropna().median() if d[column].notna().any() else float("nan") for d in frames.values()]
    if pd.isna(a) or pd.isna(b):
        return f"{label} : comparaison indisponible ; au moins une période n’a aucune valeur exploitable."
    if a == b:
        return f"{label} : médianes identiques, {number(a)} {unit} en A et B."
    return (f"{label} : la médiane passe de {number(a)} à {number(b)} {unit} "
            f"(B − A : {'+' if b > a else ''}{number(b - a)} {unit}).")


def numeric_summary(frames, column, label, unit):
    st.write(metric_message(frames, column, label, unit))
    kpi_cards([median_card(frames, column, label + " · médiane", unit)])
    notes = []
    for name, data in zip(("A", "B"), frames.values()):
        values = data[column].dropna()
        if len(values):
            notes.append(f"{name} · moitié centrale : {number(values.quantile(.25))}–{number(values.quantile(.75))} {unit}")
        if 0 < len(values) < 10:
            st.warning(f"{name} : seulement {len(values)} valeurs exploitables ; comparaison fragile.")
    if notes:
        st.caption(" · ".join(notes))


def numeric_table(frames, column, unit):
    rows = []
    for period, data in frames.items():
        values = data[column].dropna()
        rows.append({"Période": period, "Unité": unit, "Médiane": values.median(),
                     "Q1": values.quantile(.25), "Q3": values.quantile(.75),
                     "Minimum": values.min(), "Maximum": values.max(),
                     "Exploitables": len(values), "Titres": len(data)})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def shares_summary(data, frames, order):
    table = comparison_rows(data, frames, order)
    notes = []
    for row in table.to_dict("records"):
        delta = row["B − A (points)"]
        text = f"{'+' if delta > 0 else ''}{number(delta)} points" if pd.notna(delta) else "comparaison indisponible"
        notes.append(f"{row['Indicateur']} : {text}")
    st.caption("B − A · " + " · ".join(notes))
    return table


def category_message(data, frames, order):
    table = comparison_rows(data, frames, order)
    if table.empty or table["B − A (points)"].notna().sum() == 0:
        return "Comparaison indisponible : au moins une période n’a pas de valeur exploitable."
    valid = table.dropna(subset=["B − A (points)"])
    if valid["B − A (points)"].eq(0).all():
        return "Les parts des catégories comparables sont identiques en A et B."
    row = valid.loc[valid["B − A (points)"].abs().idxmax()]
    delta = row["B − A (points)"]
    return (f"Parmi les catégories affichées, l’écart le plus grand concerne « {row['Indicateur']} » : "
            f"{number(row['A (%)'])} % en A, {number(row['B (%)'])} % en B "
            f"({'+' if delta > 0 else ''}{number(delta)} points).")


def coverage_note(frames, column=None, label="Données", list_column=None):
    notes = []
    for name, data in zip(("A", "B"), frames.values()):
        if list_column:
            valid = int(data[list_column].map(bool).sum())
        elif column == "discogs_genre":
            valid = int(data.genres.map(lambda x: x != ["Non renseigné"]).sum())
        else:
            valid = int(data[column].notna().sum())
        notes.append(f"{name} : {valid}/{len(data)} renseignés, {len(data) - valid} manquants ou indéterminés")
        if 0 < valid < 10:
            st.warning(f"{name} · {label} : {valid} valeurs renseignées, prudence avec ce petit effectif.")
    st.caption(label + " · " + " · ".join(notes))


def category_legend(categories, help_text=None):
    """Aide native au survol, au clavier et au toucher directement dans la légende."""
    html = '<div class="category-legend">'
    for category in categories:
        label = f'<i style="background:{CATEGORY_COLORS[category]}"></i>{escape(category)}'
        if help_text and category in help_text:
            text = escape(help_text[category])
            html += f'<details><summary title="{text}">{label} ⓘ</summary><p>{text}</p></details>'
        else:
            html += f'<span>{label}</span>'
    st.markdown(html + '</div>', unsafe_allow_html=True)


def quality(frames, columns):
    rows = []
    for col, label in columns.items():
        for period, data in frames.items():
            valid = int(data[col].notna().sum())
            rows.append({"Indicateur": label, "Période": period, "Exploitables": valid,
                         "Manquantes": len(data) - valid, "Titres": len(data)})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


@contextmanager
def details(frames, all_data, genre, columns=None, notes=()):
    with st.expander("Détails", expanded=False):
        with st.container(height=260, border=False):
            quality(frames, columns or {})
            st.markdown("Les médianes utilisent les valeurs exploitables, sans remplacer les valeurs manquantes par zéro. "
                        "Les parts utilisent tous les titres filtrés de la période, sans pondération par le nombre de semaines au n°1.")
            for note in notes:
                st.markdown(note)
            start, end = all_data.date.min(), all_data.date.max()
            st.caption(f"Couverture du fichier : {start:%d/%m/%Y}–{end:%d/%m/%Y}. Première et dernière années partielles. "
                       "Les décennies marquées * sont incomplètes. Les intervalles A et B peuvent se chevaucher.")
            if min(map(len, frames.values())) < 10:
                st.caption("Au moins une période contient moins de 10 titres : les parts sont sensibles aux petits effectifs.")
            if genre == "Non renseigné":
                st.caption("« Non renseigné » retient les titres sans genre Discogs exploitable ; ce n’est pas un genre musical.")
            elif genre != "Tous les genres":
                st.caption("Le filtre Discogs s’applique aux deux périodes et aux courbes ; les titres sans genre sont exclus.")
            yield


TABLE_LABELS = {"song": "Titre", "artist": "Artiste", "date": "Date", "discogs_genre": "Genre",
                "artist_place_of_origin": "Origine", "length_sec": "Durée (s)", "intro_length_sec": "Intro (s)"}
EXTRA_LABELS = {**{c: f"{label} ({unit})" for c, (label, unit) in METRICS.items()},
                **CREDITS, "front_person_age": "Âge renseigné (ans)", "artist_format": "Format",
                "listed_guest": "Invité répertorié", "featured_artists": "Invités (crédits source)",
                "collaboration_credit": "Association au crédit", "collaboration_status": "Qualification du crédit",
                "collaboration_evidence": "Justification du crédit", "foreign_language": "Paroles non anglaises",
                "songwriters": "Auteurs (noms)", "songwriters_w_o_interpolation_sample_credits": "Auteurs hors réutilisation (noms)",
                "producers": "Producteurs (noms)", "sample": "Sample", "interpolation": "Interpolation", "cover": "Reprise",
                "origin_group": "Composition des origines", "guitar_based": "Guitare centrale",
                "piano_keyboard_based": "Piano/claviers centraux", "vocally_based": "Voix centrale", "bass_based": "Basse centrale",
                "orchestral_strings": "Cordes présentes", "horns_winds": "Cuivres/vents présents"}


def selection_table(data, columns=None):
    """Un seul DataFrame pour le tableau et le CSV, avec la précision d'origine."""
    columns = list(dict.fromkeys(columns or TABLE_LABELS))
    view = data[columns].copy()
    view["date"] = view["date"].dt.date
    for column in ("listed_guest", "collaboration_credit"):
        if column in view:
            view[column] = view[column].map({True: "Oui", False: "Non"}).fillna("Indéterminé")
    return view.rename(columns={**EXTRA_LABELS, **TABLE_LABELS})


def representative_titles(data, metric):
    """Trois titres distincts proches de Q1, médiane, Q3 ; règle stable, non extrêmes."""
    valid = data[data[metric].notna()].sort_values(["date", "song", "artist"], kind="stable")
    chosen = []
    for q in (.25, .5, .75):
        available = valid.loc[~valid.index.isin(chosen)]
        if not available.empty:
            idx = (available[metric] - valid[metric].quantile(q)).abs().idxmin()
            chosen.append(idx)
    return valid.loc[chosen]


def title_explorer(frames, columns, key, metric=None):
    with st.expander("Titres associés · tableau et CSV", expanded=False):
        period = st.radio("Titres de la période", list(frames), horizontal=True, key=f"titles_period_{key}")
        query = st.text_input("Rechercher un titre ou un artiste", key=f"titles_query_{key}")
        data = frames[period]
        if query.strip():
            data = data[data.song.str.contains(query.strip(), case=False, regex=False, na=False)
                        | data.artist.str.contains(query.strip(), case=False, regex=False, na=False)]
        if metric and st.checkbox("Trois exemples proches de Q1, de la médiane et de Q3", key=f"examples_{key}"):
            data = representative_titles(data, metric)
            st.caption("Ordre : proche de Q1, puis de la médiane, puis de Q3. Titres distincts ; jusqu’à trois selon la disponibilité. Ces exemples ne résument pas à eux seuls la période.")
        else:
            data = data.sort_values(["date", "song", "artist"], kind="stable")
        view = selection_table(data, ["song", "artist", "date", *columns])
        show_table(view, f"selection_{key}")


def show_table(view, key):
    st.caption(f"{len(view)} titres affichés · même ordre, colonnes et valeurs dans le CSV. Date = première semaine au n°1.")
    st.download_button("Télécharger cette sélection (CSV)", view.to_csv(index=False).encode("utf-8-sig"),
                       f"billboard_{key}.csv", "text/csv", key=f"export_{key}")
    if view.empty:
        st.info("Aucun titre pour cette sélection.")
    # Table native HTML sans tri client caché : l’ordre reste celui de l’export.
    # str préserve la précision numérique, y compris les demi-secondes et les âges.
    html = view.to_html(index=False, escape=True, na_rep="Non disponible", float_format=str,
                        classes="titles-table", border=0)
    st.html('<div class="titles-scroll" role="region" aria-label="Titres de la sélection" tabindex="0">' + html + '</div>')
