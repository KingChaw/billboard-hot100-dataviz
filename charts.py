"""Une figure par analyse ; valeurs, unités et conventions A/B communes."""
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from analysis import binary_shares, category_shares
from dashboard_data import ORIGINS, AXES
from theme import COLORS, FONT
from periods import period_labels

PERIODS = list(COLORS)
CATEGORY_COLORS = {
    "Uniquement États-Unis": "#5C1F3E", "Mixte": "#A85C85",
    "Uniquement hors États-Unis": "#E0BACE", "Non classable": "#B9BEC8",
    "Groupe": "#4266A8", "Duo": "#92609D", "Solo": "#287C6C", "Non renseigné": "#626D7D",
    "Duo ou groupe constitué": "#4266A8", "Featuring": "#92609D", "Co-signature": "#B8642E",
}
_viewport = components.declare_component("chart_viewport", path=str(Path(__file__).parent / "components" / "viewport"))


def style(fig, height=430):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family=FONT, color="#242631", size=13), height=height,
        margin=dict(l=16, r=24, t=48, b=44),
        legend=dict(title_text="", orientation="h", x=0, y=1.02, yanchor="bottom", font=dict(size=12),
                    traceorder="normal", itemclick=False, itemdoubleclick=False),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(family=FONT, size=13, color="#242631"), bordercolor="#DCDDE5"),
        separators=", ", bargap=.4, bargroupgap=.12, boxmode="group", dragmode=False,
    )
    fig.update_xaxes(automargin=True, showgrid=False, zeroline=False, title_font_size=12, fixedrange=True)
    fig.update_yaxes(automargin=True, gridcolor="#ECECF1", zeroline=False, title_font_size=12, fixedrange=True)
    return fig


def render(fig, key, height=None):
    # Hauteur fixe : pas de mesure de la fenêtre, donc pas de cadre de mesure ni de défilement.
    viewport = {"height": height, "width": 1200} if height else _viewport(page=key, key="chart_viewport", default={"height": 430, "width": 1200})
    fig.update_layout(height=height or max(380, viewport["height"]))
    if fig.layout.barmode == "group":
        categories = len(fig.layout.yaxis.categoryarray or [])
        fig.update_layout(height=max(380, viewport["height"], 120 + 44 * categories))
    if viewport["width"] < 768:
        fig.update_layout(font_size=13, margin=dict(l=8, r=24, t=65, b=55), legend_font_size=12)
        fig.update_xaxes(nticks=5, title_font_size=12, tickfont_size=11)
        fig.update_yaxes(title_font_size=12, tickfont_size=11)
        if fig.layout.barmode == "group":
            # Garder une ligne lisible pour chaque pourcentage A/B, même à 320 px.
            categories = len(fig.layout.yaxis.categoryarray or [])
            fig.update_layout(height=max(viewport["height"], 120 + 48 * categories))
        if key in ("format_trend", "origin_trend", "teams_trend", "reuse_trend"):
            fig.update_xaxes(tickangle=-55 if viewport["width"] < 400 else -35,
                             ticks="outside", ticklen=6, tickcolor="rgba(0,0,0,0)")
            fig.update_layout(margin_b=65)
    st.plotly_chart(fig, key=f"chart_{key}", use_container_width=True, theme=None,
                    config={"displayModeBar": False, "responsive": True, "scrollZoom": False,
                            "topojsonURL": "app/static/"})


def number_fr(value):
    return f"{value:.1f}".rstrip("0").rstrip(".").replace(".", ",")


def empty_note(fig, text="Aucune valeur exploitable pour cette sélection"):
    fig.add_annotation(text=text, xref="paper", yref="paper", x=.5, y=.5, showarrow=False)


def distribution(frames, column, unit, points="outliers"):
    labels = period_labels(frames)
    fig = go.Figure()
    for period in PERIODS:
        data = frames[period]
        values = data[column].dropna()
        if values.empty:
            fig.add_trace(go.Scatter(x=[period], y=[None], mode="markers", showlegend=False, hoverinfo="skip"))
            fig.add_annotation(x=period, y=.5, yref="paper", text="Non disponible", showarrow=False)
            continue
        q1, median, q3 = values.quantile([.25, .5, .75])
        iqr = q3 - q1
        inside = values[values.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
        lower, upper = inside.min(), inside.max()
        # Quartiles pandas explicites : Plotly « linear » utilise une autre convention
        # sur certains effectifs (ex. 81 intros récentes : Q1 6,75 au lieu de 7).
        fig.add_trace(go.Box(x=[period], q1=[q1], median=[median], q3=[q3],
                             lowerfence=[lower], upperfence=[upper], name=labels[period],
                             marker_color=COLORS[period], line_width=2, width=.6,
                             boxpoints=False, hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=[period], y=[median], mode="markers", name=labels[period],
                                 marker=dict(color=COLORS[period], size=12, symbol="diamond"), showlegend=False,
                                 customdata=[[len(values), len(data), q1, q3, lower, upper]],
                                 hovertemplate=labels[period] + "<br>Médiane : %{y} " + unit
                                 + "<br>Moitié centrale : %{customdata[2]}–%{customdata[3]} " + unit
                                 + "<br>Moustaches : %{customdata[4]}–%{customdata[5]} " + unit
                                 + "<br>Exploitables : %{customdata[0]} / %{customdata[1]} titres<extra></extra>"))
        if points:
            outliers = values[(values < lower) | (values > upper)]
            fig.add_trace(go.Scatter(x=[period] * len(outliers), y=outliers, mode="markers", showlegend=False,
                                     marker=dict(color=COLORS[period], size=5),
                                     hovertemplate=labels[period] + "<br>Valeur : %{y} " + unit + "<extra></extra>"))
    style(fig)
    fig.update_layout(showlegend=False, margin_t=20)
    fig.update_xaxes(categoryorder="array", categoryarray=PERIODS, tickmode="array", tickvals=PERIODS, ticktext=list(labels.values()),
                     title="Période")
    fig.update_yaxes(title=AXES.get(column, unit))
    if column == "front_person_age":
        # Une boîte n'a pas besoin de partir de 0 : l'axe suit les âges observés pour étaler les écarts.
        # L'axe suit les moustaches : les boîtes occupent la hauteur. Les âges au-delà sont listés en haut.
        bounds = []
        for period in PERIODS:
            values = frames[period][column].dropna()
            if len(values):
                q1, q3 = values.quantile([.25, .75])
                bounds.append(values[values.between(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))].agg(["min", "max"]))
        if bounds:
            low, top = min(b["min"] for b in bounds) - 2, max(b["max"] for b in bounds) + 3
            fig.update_yaxes(range=[low, top], dtick=5)
            for period in PERIODS:
                above = sorted(frames[period][column].dropna()[lambda v: v > top])
                if above:
                    fig.add_annotation(x=period, y=top, yshift=-10, showarrow=False, font=dict(color=COLORS[period], size=12),
                                       text="▲ " + " · ".join(number_fr(v) for v in above) + " ans")
    elif column != "loudness_d_b":
        fig.update_yaxes(rangemode="tozero")
    if column in ("energy", "danceability", "acousticness"):
        fig.update_yaxes(range=[-2, 102], tickvals=[0, 25, 50, 75, 100])
    if column.startswith("writers_") or column == "producer_count":
        fig.update_yaxes(dtick=1)
    return fig


def share_frame(frames, column):
    parts = [category_shares(data, column).assign(période=period, total=len(data), renseignés=len(data))
             for period, data in frames.items() if len(data)]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["catégorie", "effectif", "part", "période", "total", "renseignés"])


def binary_frame(frames, columns):
    data = pd.concat([binary_shares(frame, list(columns), columns).assign(période=period, total=len(frame))
                      for period, frame in frames.items()], ignore_index=True)
    data.loc[data["renseignés"].eq(0) | data.total.eq(0), "part"] = np.nan
    return data


def aligned_shares(data, frames, order):
    parts = []
    for period in PERIODS:
        subset = data[data["période"].eq(period)].set_index("catégorie").reindex(order)
        absent = subset["effectif"].isna()
        subset.loc[absent, ["effectif", "part"]] = 0
        subset["total"], subset["période"] = len(frames[period]), period
        if "renseignés" not in subset:
            subset["renseignés"] = len(frames[period])
        subset["renseignés"] = subset["renseignés"].fillna(len(frames[period]))
        if not len(frames[period]):
            subset["part"] = np.nan
        parts.append(subset.rename_axis("catégorie").reset_index())
    return pd.concat(parts, ignore_index=True)


def share_axes(fig, order):
    style(fig)
    fig.update_xaxes(range=[0, 105], title="Titres n°1 (%)", ticksuffix=" %", tickvals=[0, 25, 50, 75, 100],
                     showgrid=True, gridcolor="#ECECF1")
    fig.update_yaxes(title=None, showgrid=False, categoryorder="array", categoryarray=order, autorange="reversed",
                     tickmode="array", tickvals=order,
                     ticktext=["<br>".join(textwrap.wrap(label, width=22, break_long_words=False)) for label in order])
    return fig


def bars(data, frames, order):
    data = aligned_shares(data, frames, order)
    labels = period_labels(frames)
    fig = go.Figure()
    # Trace et position A puis B, du haut vers le bas dans chaque catégorie.
    for i, period in enumerate(PERIODS):
        d = data[data["période"].eq(period)]
        fig.add_trace(go.Bar(x=d.part, y=d["catégorie"], name=labels[period], orientation="h",
                            marker_color=COLORS[period], offsetgroup=str(i),
                            customdata=d[["effectif", "total"]],
                            text=d.part, texttemplate="%{x:.1f} %", textposition="outside",
                            textfont_size=11, constraintext="none", cliponaxis=False,
                            hovertemplate=labels[period] + " · %{y}<br>%{x:.1f} %<br>%{customdata[0]:.0f} / %{customdata[1]} titres<extra></extra>"))
        for _, row in d[d.part.isna()].iterrows():
            fig.add_annotation(x=2, y=row["catégorie"], text=f"{labels[period]} : non disponible", xanchor="left",
                               yshift=9 if i == 0 else -9, font_size=11, showarrow=False)
    share_axes(fig, order)
    fig.update_layout(barmode="group", bargap=.2)
    fig.update_xaxes(range=[0, 112])
    return fig


def points(data, frames, order, y_title=None):
    data = aligned_shares(data, frames, order)
    labels = period_labels(frames)
    fig = go.Figure()
    # Arrow chart (séance 4) : une flèche de A vers B montre le sens et l'amplitude du changement.
    for category in order:
        pair = data[data["catégorie"].eq(category)].set_index("période").reindex(PERIODS)
        if pair.part.notna().all() and pair.part.iloc[0] != pair.part.iloc[1]:
            fig.add_annotation(x=pair.part.iloc[1], y=category, ax=pair.part.iloc[0], ay=category, xref="x", yref="y",
                               axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1.4, arrowwidth=2.5,
                               arrowcolor="#8A90A0", standoff=9, startstandoff=7, text="")
    for i, period in enumerate(PERIODS):
        d = data[data["période"].eq(period)]
        fig.add_trace(go.Scatter(x=d.part, y=d["catégorie"], name=labels[period], mode="markers+text",
                                 marker=dict(color=COLORS[period], size=14, symbol="circle" if i == 0 else "diamond"),
                                 text=[f"{v:.1f} %".replace(".", ",") if pd.notna(v) else "" for v in d.part],
                                 textposition="top center" if i == 0 else "bottom center", cliponaxis=False,
                                 customdata=d[["effectif", "total", "renseignés"]],
                                 hovertemplate=labels[period] + " · %{y}<br>%{x:.1f} %<br>%{customdata[0]} / %{customdata[1]} titres<br>%{customdata[2]} valeurs renseignées<extra></extra>"))
        for _, row in d[d.part.isna()].iterrows():
            fig.add_annotation(x=50, y=row["catégorie"], yshift=14 if i == 0 else -14,
                               text=f"{labels[period]} : non disponible", showarrow=False)
    share_axes(fig, order)
    # Base zéro, maximum adapté aux valeurs ; une demi-ligne de marge en haut et en bas.
    top = min(100, max(25, 10 * np.ceil((data.part.max() if data.part.notna().any() else 90) / 10 + 1)))
    fig.update_xaxes(range=[-top * .06, top], tickvals=None, dtick=10 if top <= 50 else 25)
    fig.update_yaxes(autorange=False, range=[len(order) - .4, -.6], title=y_title)
    fig.update_layout(margin_t=60, legend=dict(y=1.12, x=.5, xanchor="center"))
    return fig

def readable_text(color):
    """Texte foncé sur fond clair, blanc sur fond sombre."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return "#242631" if 0.2126 * r + 0.7152 * g + 0.0722 * b > .5 else "#FFFFFF"

def stacked(frames, column, order, vertical=False):
    labels = period_labels(frames)
    fig = go.Figure()
    for category in order:
        shares, counts = [], []
        for period in PERIODS:
            d = frames[period]
            categories = d[column].replace(ORIGINS) if column == "origin_group" else d[column].fillna("Non renseigné")
            n = int(categories.eq(category).sum())
            counts.append([n, len(d)])
            shares.append(100 * n / len(d) if len(d) else np.nan)
        position = dict(x=PERIODS, y=shares) if vertical else dict(x=shares, y=PERIODS, orientation="h")
        fig.add_trace(go.Bar(**position, name=category, width=.5,
                            marker_color=CATEGORY_COLORS[category], customdata=[[*count, labels[p]] for count, p in zip(counts, PERIODS)],
                            text=[f"{v:.1f} %".replace(".", ",") if pd.notna(v) and v > 0 else "" for v in shares],
                            textposition="inside", insidetextanchor="middle", textangle=0,
                            textfont=dict(color=readable_text(CATEGORY_COLORS[category]), size=12),
                            hovertemplate=category + " · %{customdata[2]}<br>%{" + ("y" if vertical else "x") + ":.1f} %<br>%{customdata[0]} / %{customdata[1]} titres<extra></extra>"))
    style(fig)
    fig.update_layout(barmode="stack", showlegend=False, margin_t=20, uniformtext=dict(minsize=11, mode="show"))
    share_axis, period_axis = (fig.update_yaxes, fig.update_xaxes) if vertical else (fig.update_xaxes, fig.update_yaxes)
    share_axis(range=[0, 100], ticksuffix=" %", title="Titres n°1 (%)", dtick=25)
    # Ticks transparents : un peu d'air entre le libellé de période et les barres.
    period_axis(title="Période", categoryorder="array", categoryarray=PERIODS, showgrid=False,
                tickmode="array", tickvals=PERIODS, ticktext=list(labels.values()),
                ticks="outside", ticklen=12, tickcolor="rgba(0,0,0,0)")
    if not vertical:
        fig.update_yaxes(autorange="reversed")
    for period in PERIODS:
        if frames[period].empty:
            fig.add_annotation(x=period if vertical else 50, y=50 if vertical else period, text="Sélection vide", showarrow=False)
    return fig


def trend(data, unit, years_a, years_b, median=True, y_title=None):
    fig = go.Figure()
    if median:
        # Un polygone par séquence renseignée : la bande ne traverse jamais un trou.
        runs = data.value.notna().ne(data.value.notna().shift()).cumsum()
        first_band = True
        for _, segment in data[data.value.notna()].groupby(runs):
            fig.add_trace(go.Scatter(x=segment.position, y=segment.q1, mode="lines", line_width=0,
                                     showlegend=False, hoverinfo="skip", connectgaps=False))
            fig.add_trace(go.Scatter(x=segment.position, y=segment.q3, mode="lines", line_width=0,
                                     fill="tonexty", fillcolor="rgba(97,83,173,.12)",
                                     name="Zone où se trouve la moitié des n°1 (Q1–Q3)", showlegend=first_band,
                                     hoverinfo="skip", connectgaps=False))
            first_band = False
    fig.add_trace(go.Scatter(x=data.position, y=data.value, mode="lines+markers", name="Médiane" if median else "Part des titres",
                             line=dict(color="#6153AD", width=2),
                             marker=dict(size=9, symbol=["circle-open" if p else "circle" for p in data.partial]),
                             connectgaps=False, customdata=data[["label", "valid", "total", "q1", "q3"]],
                             hovertemplate="%{customdata[0]}<br>%{y:.1f} " + unit
                             + "<br>Valeurs exploitables : %{customdata[1]} / %{customdata[2]}"
                             + ("<br>La moitié des n°1 (Q1–Q3) entre %{customdata[3]:.1f} et %{customdata[4]:.1f} " + unit if median else "") + "<extra></extra>"))
    style(fig)
    fig.update_xaxes(title="Périodes agrégées", tickmode="array", tickvals=data.position,
                     ticktext=data.label, tickangle=-30, range=[data.position.min() - 3, data.position.max() + 3],
                     showgrid=True, gridcolor="#ECECF1")
    fig.update_layout(margin_b=85)
    fig.update_yaxes(title=y_title or unit)
    if not median:
        fig.update_yaxes(range=[0, 100], ticksuffix=" %")
    elif unit == "score / 100":
        fig.update_yaxes(range=[0, 100])
    elif unit != "dB":
        fig.update_yaxes(rangemode="tozero")
    if data.value.notna().sum() == 0:
        empty_note(fig)
    return fig


def world_map(data, period, selected_country=None, label=None):
    selected = data[data["période"].eq(period)]
    max_share = data.part.max()
    maximum = max(1, float(max_share)) if pd.notna(max_share) else 100
    fig = go.Figure(go.Choropleth(
        locations=selected.iso, z=selected.part, locationmode="ISO-3", zmin=0, zmax=maximum,
        colorscale=[[0, "#F0EFFA"], [.15, "#C9C4E8"], [.5, "#8C81C5"], [1, "#493C91"]],
        marker_line_color="#FFFFFF", marker_line_width=.6,
        colorbar=dict(title="Titres (%)", thickness=12, len=.7, ticksuffix=" %"),
        customdata=selected[["pays", "effectif", "total"]],
        hovertemplate=(label or "Période sélectionnée") + "<br>%{customdata[0]}<br>%{customdata[1]} / %{customdata[2]} titres<br>%{z:.1f} %<extra></extra>",
    ))
    # Repères ponctuels : même les petites îles absentes du fond à cette échelle restent accessibles.
    small = {"PRI": (18.22, -66.59), "BRB": (13.19, -59.54), "TTO": (10.69, -61.22)}
    for iso, (lat, lon) in small.items():
        rows = selected[selected.iso.eq(iso)]
        if rows.empty or pd.isna(rows.iloc[0].part):
            continue
        row = rows.iloc[0]
        fig.add_trace(go.Scattergeo(lat=[lat], lon=[lon], mode="markers", showlegend=False,
                                     marker=dict(size=7, color=[row.part], colorscale=fig.data[0].colorscale, cmin=0, cmax=maximum,
                                                 line=dict(color="#F5F7FA", width=.5)),
                                     text=[f"{label or 'Période sélectionnée'} · {row.pays} · {int(row.effectif)} / {int(row.total)} titres · {row.part:.1f} %"],
                                     hovertemplate="%{text}<extra></extra>"))
    if selected_country:
        row = selected[selected.pays.eq(selected_country)].iloc[0]
        fig.add_trace(go.Scattergeo(locations=[row.iso], locationmode="ISO-3", mode="markers",
                                    marker=dict(size=15, color="#A65313", symbol="circle-open", line_width=2),
                                    showlegend=False, hoverinfo="skip"))
    style(fig)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), geo=dict(
        projection_type="natural earth", bgcolor="#FFFFFF", showframe=False, showcoastlines=False,
        showland=True, landcolor="#DADBE2", showcountries=True, countrycolor="#FFFFFF"))
    if selected.part.notna().sum() == 0:
        empty_note(fig, "Aucune origine exploitable pour cette période")
    return fig

def origins_trend(series, height=430):
    """Les trois parts exclusives sur une même frise ; leur comparaison est le message."""
    fig = go.Figure()
    for label, data in series:
        fig.add_trace(go.Scatter(
            x=data.position, y=data.value, mode="lines+markers", name=label,
            line=dict(color=CATEGORY_COLORS[label], width=2.5),
            marker=dict(size=9, symbol=["circle-open" if p else "circle" for p in data.partial]),
            connectgaps=False, customdata=data[["label", "valid", "total"]],
            hovertemplate=label + "<br>%{customdata[0]}<br>%{y:.1f} %"
                        + "<br>Valeurs exploitables : %{customdata[1]} / %{customdata[2]}<extra></extra>"))
    style(fig, height)
    fig.update_layout(showlegend=False)
    axis = series[0][1]
    fig.update_xaxes(title="Périodes agrégées", tickmode="array", tickvals=axis.position,
                    ticktext=axis.label, tickangle=-30,
                    range=[axis.position.min() - 3, axis.position.max() + 3],
                    showgrid=True, gridcolor="#ECECF1")
    fig.update_layout(margin_b=85)
    fig.update_yaxes(title="Part des titres n°1 (%)", range=[0, 100], ticksuffix=" %", dtick=25)
    return fig