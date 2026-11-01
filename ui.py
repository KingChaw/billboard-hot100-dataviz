"""Présentation française, rappel compact et détails repliés."""
from contextlib import contextmanager
from html import escape

import pandas as pd
import streamlit as st

from periods import period_labels, difference_label, export_slug
from charts import CATEGORY_COLORS
from dashboard_data import FEATURING, METRICS, FORMAT_METRICS, CREDITS, comparison_rows, quartile_examples


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
    labels = period_labels(frames)
    for (period, data), years, suffix in zip(frames.items(), [years_a, years_b], ["a", "b"]):
        items.append(f'<span><b class="period-{suffix}">{escape(labels[period])}</b>'
                     f'<small>{len(data)} titres</small></span>')
    items.append(f'<span>{escape(genre)}</span>')
    st.markdown('<div class="selection">' + ''.join(items) + '</div>', unsafe_allow_html=True)


def kpi_cards(cards, frames, compact=False, tone=None):
    html = ('<div class="kpi-grid' + (' single' if len(cards) == 1 else '') + (' compact' if compact else '')
            + (f' {tone}' if tone else '') + '">')
    for title, values, foot in cards:
        html += f'<article class="kpi"><h3>{escape(title)}</h3><div class="kpi-values">'
        for value, label, suffix in zip(values, period_labels(frames).values(), ["a", "b"]):
            html += (f'<div><span class="period-label period-{suffix}">{escape(label)}</span>'
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
    foot = f"Écart : non disponible ({difference_label(frames)})"
    if pd.notna(delta):
        foot = f"Écart : {'+' if delta > 0 else ''}{number(delta)} {'s' if is_duration else unit} ({difference_label(frames)})"
    counts = [f"{p} : {d[column].count()}/{len(d)} exploitables" for p, d in zip(period_labels(frames).values(), frames.values())]
    foot += " · " + " · ".join(counts)
    return title, values, foot


def share_card(frames, title, predicate, valid_predicate=None):
    values, parts, counts = [], [], []
    for label, data in zip(period_labels(frames).values(), frames.values()):
        valid = int(valid_predicate(data).sum()) if valid_predicate else len(data)
        count = int(predicate(data).sum())
        share = 100 * count / len(data) if len(data) and valid else float("nan")
        parts.append(share)
        counts.append(f"{label} : {count}/{len(data)} titres · {valid} renseignés")
        values.append(number(share) + (" %" if pd.notna(share) else ""))
    delta = parts[1] - parts[0]
    foot = "Écart : " + (f"{'+' if delta > 0 else ''}{number(delta)} points" if pd.notna(delta) else "non disponible")
    foot += f" ({difference_label(frames)})"
    return title, values, foot + " · " + " · ".join(counts)


def sign(value):
    return ("+" if value > 0 else "") + number(value)


def short_median_card(frames, column, title, unit):
    """Carte A/B réduite à l'essentiel : valeurs, unité, n."""
    values = [number(d[column].median()) + f" {unit}" if d[column].notna().any() else "Non disponible" for d in frames.values()]
    return title, values, None


def short_share_card(frames, title, predicate):
    values = [number(100 * predicate(d).sum() / len(d)) + " %" if len(d) else "Non disponible" for d in frames.values()]
    return title, values, None


def metric_message(frames, column, label, unit):
    a, b = [d[column].dropna().median() if d[column].notna().any() else float("nan") for d in frames.values()]
    if pd.isna(a) or pd.isna(b):
        return f"{label} : comparaison indisponible ; au moins une période n’a aucune valeur exploitable."
    studied, reference = period_labels(frames).values()
    if a == b:
        return f"{label} : médianes identiques, {number(a)} {unit} pour {studied} et {reference}."
    return (f"{label} : la médiane passe de {number(a)} à {number(b)} {unit} "
            f"(écart : {'+' if b > a else ''}{number(b - a)} {unit} ; {reference} − {studied}).")


def numeric_summary(frames, column, label, unit):
    st.write(metric_message(frames, column, label, unit))
    kpi_cards([median_card(frames, column, label + " · médiane", unit)], frames)
    notes = []
    for name, data in zip(period_labels(frames).values(), frames.values()):
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
        rows.append({"Période": period_labels(frames)[period], "Unité": unit, "Médiane": values.median(),
                     "Q1": values.quantile(.25), "Q3": values.quantile(.75),
                     "Minimum": values.min(), "Maximum": values.max(),
                     "Exploitables": len(values), "Titres": len(data)})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def format_cards(frames, columns):
    """Cartes et alertes de couverture pour les seules pages Format & son."""
    cards = []
    for column in columns:
        label, unit = FORMAT_METRICS[column]
        title, values, foot = median_card(frames, column, label + " · médiane", unit,
                                         is_duration=column == "length_sec")
        if column == "intro_ratio":
            foot = foot.replace(" % (", " points (")
        if unit == "score / 100":
            values = [value.replace(" score / 100", " / 100") for value in values]
            foot = foot.replace(" score / 100 (", " points de score (")
        cards.append((title, values, foot))
    kpi_cards(cards, frames, tone="format-cards")
    for name, data in zip(period_labels(frames).values(), frames.values()):
        small = [f"{FORMAT_METRICS[c][0]} : {data[c].count()}" for c in columns if 0 < data[c].count() < 10]
        if small:
            st.warning(name + " · moins de 10 valeurs exploitables (" + ", ".join(small) + "). Prudence.")


def reading_note(text):
    st.markdown('<aside class="format-reading"><b>Comment lire</b><p>' + escape(text) + '</p></aside>',
                unsafe_allow_html=True)


def format_examples(frames, column):
    """Écoute contextuelle compacte, sans reconstruire la table de Données."""
    label, unit = FORMAT_METRICS[column]
    st.markdown("**Quelques titres pour situer les écarts**")
    period = st.radio("Période des exemples", list(frames), format_func=period_labels(frames).get,
                      key="format_examples_period", horizontal=True)
    examples = quartile_examples(frames[period], column)
    if not examples:
        st.caption("Aucune valeur exploitable pour proposer un exemple dans cette période.")
    for row in examples:
        value = duration(row["value"]) if column == "length_sec" else number(row["value"]) + " " + unit
        st.markdown('<div class="format-example"><span>' + escape(row["repère"]) + '</span><b>'
                    + escape(str(row["song"]).strip()) + '</b> · ' + escape(str(row["artist"]))
                    + '<small>' + escape(label + " : " + value + " · cible : " + number(row["cible"]) + " " + unit)
                    + '</small></div>', unsafe_allow_html=True)
    st.caption("Titres les plus proches des quartiles de cette sélection ; jusqu’à trois titres distincts. Aucun jugement de qualité.")


def shares_summary(data, frames, order):
    table = comparison_rows(data, frames, order)
    notes = []
    for row in table.to_dict("records"):
        delta = row["B − A (points)"]
        text = f"{'+' if delta > 0 else ''}{number(delta)} points" if pd.notna(delta) else "comparaison indisponible"
        notes.append(f"{row['Indicateur']} : {text}")
    st.caption(f"Écart ({difference_label(frames)}) · " + " · ".join(notes))
    return table


def simple_comparison(data, frames, order, first_column):
    """Tableau lisible pour un A&R : part, effectif et écart en points."""
    table = comparison_rows(data, frames, order)
    st.dataframe(pd.DataFrame({
        first_column: table["Indicateur"],
        **{name: [f"{number(p)} % ({c} titre{'s' if c > 1 else ''})" for p, c in zip(table[f"{x} (%)"], table[f"{x} · titres concernés"])]
           for x, name in zip("AB", period_labels(frames).values())},
        "Écart (points)": [f"{sign(v)}" if pd.notna(v) else "Non disponible" for v in table["B − A (points)"]]}),
        hide_index=True, width="stretch")


def category_message(data, frames, order):
    table = comparison_rows(data, frames, order)
    if table.empty or table["B − A (points)"].notna().sum() == 0:
        return "Comparaison indisponible : au moins une période n’a pas de valeur exploitable."
    valid = table.dropna(subset=["B − A (points)"])
    if valid["B − A (points)"].eq(0).all():
        return "Les parts des catégories comparables sont identiques pour les deux périodes."
    row = valid.loc[valid["B − A (points)"].abs().idxmax()]
    delta = row["B − A (points)"]
    studied, reference = period_labels(frames).values()
    return (f"Parmi les catégories affichées, l’écart le plus grand concerne « {row['Indicateur']} » : "
            f"{number(row['A (%)'])} % pour {studied}, {number(row['B (%)'])} % pour {reference} "
            f"({'+' if delta > 0 else ''}{number(delta)} points).")


def coverage_note(frames, column=None, label="Données", list_column=None):
    notes = []
    for name, data in zip(period_labels(frames).values(), frames.values()):
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


def category_legend(categories, help_text=None, large=False):
    """Aide native au survol, au clavier et au toucher directement dans la légende."""
    html = '<div class="category-legend' + (' large' if large else '') + '">'
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
            rows.append({"Indicateur": label, "Période": period_labels(frames)[period], "Exploitables": valid,
                         "Manquantes": len(data) - valid, "Titres": len(data)})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


@contextmanager
def details(frames, all_data, genre, columns=None, notes=(), essentials=False, footer=None):
    with st.expander("Détails", expanded=False):
        if essentials:
            for note in notes:
                st.markdown(note)
            yield
            if footer:
                st.markdown(footer)
            return
        with st.container(height=260, border=False):
            quality(frames, columns or {})
            st.markdown("Les médianes utilisent les valeurs exploitables, sans remplacer les valeurs manquantes par zéro. "
                        "Les parts utilisent tous les titres filtrés de la période, sans pondération par le nombre de semaines au n°1.")
            for note in notes:
                st.markdown(note)
            start, end = all_data.date.min(), all_data.date.max()
            st.caption(f"Couverture du fichier : {start:%d/%m/%Y}–{end:%d/%m/%Y}. Première et dernière années partielles. "
                       "Les décennies marquées * sont incomplètes. Les deux intervalles sélectionnés peuvent se chevaucher.")
            if min(map(len, frames.values())) < 10:
                st.caption("Au moins une période contient moins de 10 titres : les parts sont sensibles aux petits effectifs.")
            if genre == "Non renseigné":
                st.caption("« Non renseigné » retient les titres sans genre Discogs exploitable ; ce n’est pas un genre musical.")
            elif genre != "Tous les genres":
                st.caption("Le filtre Discogs s’applique aux deux périodes et aux courbes ; les titres sans genre sont exclus.")
            yield
            if footer:
                st.markdown(footer)


TABLE_LABELS = {"song": "Titre", "artist": "Artiste", "date": "Date", "discogs_genre": "Genre",
                "artist_place_of_origin": "Origine", "length_sec": "Durée (s)", "intro_length_sec": "Intro (s)"}
EXTRA_LABELS = {**{c: f"{label} ({unit})" for c, (label, unit) in METRICS.items()},
                **CREDITS, "front_person_age": "Âge (ans)", "artist_format": "Format",
                "listed_guest": "Invité répertorié", "featured_artists": "Invités (crédits source)",
                "collaboration_credit": "Association au crédit", "collaboration_status": "Qualification du crédit",
                "collaboration_evidence": "Justification du crédit", "collaboration": "Collaboration", "foreign_language": "Paroles non anglaises",
                "songwriters": "Auteurs (noms)", "songwriters_w_o_interpolation_sample_credits": "Auteurs hors réutilisation (noms)",
                "producers": "Producteurs (noms)", "sample": "Sample", "interpolation": "Interpolation", "cover": "Reprise",
                "origin_group": "Composition des origines", "guitar_based": "Guitare centrale",
                "piano_keyboard_based": "Piano/claviers centraux", "vocally_based": "Voix centrale", "bass_based": "Basse centrale",
                "orchestral_strings": "Cordes présentes", "horns_winds": "Cuivres/vents présents"}


def selection_table(data, columns=None):
    """Un seul DataFrame pour le tableau et le CSV, avec la précision d'origine."""
    columns = list(dict.fromkeys(columns or TABLE_LABELS))
    view = data[[c for c in columns if c != "collaboration"]].copy()
    if "collaboration" in columns:
        view.insert(columns.index("collaboration"), "collaboration", None)
    view["date"] = view["date"].dt.date
    if "collaboration" in view:
        collaboration = data.collaboration_credit.map({True: "Co-signature", False: "Non"}).astype(object)
        collaboration[data.collaboration_status.eq(FEATURING)] = "Featuring"
        view["collaboration"] = collaboration.fillna("Non renseigné")
    for column in ("sample", "interpolation", "cover"):
        if column in view:
            view[column] = view[column].map({1: "Oui", 0: "Non"}).fillna("Non renseigné")
    for column in ("listed_guest", "collaboration_credit"):
        if column in view:
            view[column] = view[column].map({True: "Oui", False: "Non"}).fillna("Indéterminé")
    return view.rename(columns={**EXTRA_LABELS, **TABLE_LABELS})


def show_table(view, key, period=None):
    if view.empty:
        st.info("Aucun titre pour cette sélection.")
    # Table native HTML sans tri client caché : l’ordre reste celui de l’export.
    # str préserve la précision numérique, y compris les demi-secondes et les âges.
    html = view.to_html(index=False, escape=True, na_rep="Non disponible", float_format=str,
                        classes="titles-table", border=0)
    st.html('<div class="titles-scroll" role="region" aria-label="Titres de la sélection" tabindex="0">' + html + '</div>')
    st.download_button("Télécharger cette sélection (CSV)", view.to_csv(index=False).encode("utf-8-sig"),
                       f"billboard_{export_slug(period or key)}.csv", "text/csv", key=f"export_{key}")
