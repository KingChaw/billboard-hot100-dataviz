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

PERIODS = list(COLORS)
CATEGORY_COLORS = {
    "Uniquement États-Unis": "#547CC6", "Mixte": "#BC83C9",
    "Uniquement hors États-Unis": "#5AB7A5", "Non classable": "#737D8D",
    "Groupe": "#547CC6", "Duo": "#BC83C9", "Solo": "#5AB7A5", "Non renseigné": "#737D8D",
}
_viewport = components.declare_component("chart_viewport", path=str(Path(__file__).parent / "components" / "viewport"))


def style(fig, height=430):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#14171C", plot_bgcolor="#14171C",
        font=dict(family=FONT, color="#F5F7FA", size=13), height=height,
        margin=dict(l=16, r=24, t=48, b=44),
        legend=dict(title_text="", orientation="h", x=0, y=1.02, yanchor="bottom", font=dict(size=12),
                    traceorder="normal", itemclick=False, itemdoubleclick=False),
        hoverlabel=dict(bgcolor="#191D24", font=dict(family=FONT, size=13), bordercolor="#505B6C"),
        separators=", ", bargap=.4, bargroupgap=.12, boxmode="group", dragmode=False,
    )
    fig.update_xaxes(automargin=True, showgrid=False, zeroline=False, title_font_size=12, fixedrange=True)
    fig.update_yaxes(automargin=True, gridcolor="#292F38", zeroline=False, title_font_size=12, fixedrange=True)
    return fig


def render(fig, key):
    viewport = _viewport(page=key, key="chart_viewport", default={"height": 430, "width": 1200})
    fig.update_layout(height=max(380, viewport["height"]))
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


def empty_note(fig, text="Aucune valeur exploitable pour cette sélection"):
    fig.add_annotation(text=text, xref="paper", yref="paper", x=.5, y=.5, showarrow=False)


def distribution(frames, column, unit, points="outliers"):
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
                             lowerfence=[lower], upperfence=[upper], name=period,
                             marker_color=COLORS[period], line_width=2, width=.45,
                             boxpoints=False, hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=[period], y=[median], mode="markers", name=period,
                                 marker=dict(color=COLORS[period], size=12, symbol="diamond"), showlegend=False,
                                 customdata=[[len(values), len(data), q1, q3, lower, upper]],
                                 hovertemplate=period + "<br>Médiane : %{y} " + unit
                                 + "<br>Moitié centrale : %{customdata[2]}–%{customdata[3]} " + unit
                                 + "<br>Moustaches : %{customdata[4]}–%{customdata[5]} " + unit
                                 + "<br>Exploitables : %{customdata[0]} / %{customdata[1]} titres<extra></extra>"))
        if points:
            outliers = values[(values < lower) | (values > upper)]
            fig.add_trace(go.Scatter(x=[period] * len(outliers), y=outliers, mode="markers", showlegend=False,
                                     marker=dict(color=COLORS[period], size=5),
                                     hovertemplate=period + "<br>Valeur : %{y} " + unit + "<extra></extra>"))
    style(fig)
    fig.update_layout(showlegend=False, margin_t=20)
    fig.update_xaxes(categoryorder="array", categoryarray=PERIODS)
    fig.update_yaxes(title=AXES.get(column, unit))
    if column != "loudness_d_b":
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
    fig.update_xaxes(range=[0, 105], title="Titres (%)", ticksuffix=" %", tickvals=[0, 25, 50, 75, 100],
                     showgrid=True, gridcolor="#292F38")
    fig.update_yaxes(title=None, showgrid=False, categoryorder="array", categoryarray=order, autorange="reversed",
                     tickmode="array", tickvals=order,
                     ticktext=["<br>".join(textwrap.wrap(label, width=22, break_long_words=False)) for label in order])
    return fig


def bars(data, frames, order):
    data = aligned_shares(data, frames, order)
    fig = go.Figure()
    # Trace et position A puis B, du haut vers le bas dans chaque catégorie.
    for i, period in enumerate(PERIODS):
        d = data[data["période"].eq(period)]
        fig.add_trace(go.Bar(x=d.part, y=d["catégorie"], name=period, orientation="h",
                            marker_color=COLORS[period], offsetgroup=str(i),
                            customdata=d[["effectif", "total"]],
                            text=d.part, texttemplate="%{x:.1f} %", textposition="outside",
                            textfont_size=11, constraintext="none", cliponaxis=False,
                            hovertemplate=period + " · %{y}<br>%{x:.1f} %<br>%{customdata[0]:.0f} / %{customdata[1]} titres<extra></extra>"))
        for _, row in d[d.part.isna()].iterrows():
            fig.add_annotation(x=2, y=row["catégorie"], text=f"{period} : non disponible", xanchor="left",
                               yshift=9 if i == 0 else -9, font_size=11, showarrow=False)
    share_axes(fig, order)
    fig.update_layout(barmode="group", bargap=.2)
    fig.update_xaxes(range=[0, 112])
    return fig


def points(data, frames, order):
    data = aligned_shares(data, frames, order)
    fig = go.Figure()
    # Liaison descriptive ; les catégories ne constituent jamais une partition.
    for category in order:
        pair = data[data["catégorie"].eq(category)].set_index("période").reindex(PERIODS)
        if pair.part.notna().all():
            fig.add_trace(go.Scatter(x=pair.part, y=[category, category], mode="lines",
                                     line=dict(color="#707989", width=3), showlegend=False, hoverinfo="skip"))
    for i, period in enumerate(PERIODS):
        d = data[data["période"].eq(period)]
        fig.add_trace(go.Scatter(x=d.part, y=d["catégorie"], name=period, mode="markers+text",
                                 marker=dict(color=COLORS[period], size=12, symbol="circle" if i == 0 else "diamond"),
                                 text=[f"{v:.1f} %".replace(".", ",") if pd.notna(v) else "" for v in d.part],
                                 textposition="top center" if i == 0 else "bottom center", cliponaxis=False,
                                 customdata=d[["effectif", "total", "renseignés"]],
                                 hovertemplate=period + " · %{y}<br>%{x:.1f} %<br>%{customdata[0]} / %{customdata[1]} titres<br>%{customdata[2]} valeurs renseignées<extra></extra>"))
        for _, row in d[d.part.isna()].iterrows():
            fig.add_annotation(x=50, y=row["catégorie"], yshift=14 if i == 0 else -14,
                               text=f"{period} : non disponible", showarrow=False)
    share_axes(fig, order)
    fig.update_xaxes(range=[-5, 105])
    return fig


def stacked(frames, column, order):
    fig = go.Figure()
    for category in order:
        shares, counts = [], []
        for period in PERIODS:
            d = frames[period]
            labels = d[column].replace(ORIGINS) if column == "origin_group" else d[column].fillna("Non renseigné")
            n = int(labels.eq(category).sum())
            counts.append([n, len(d)])
            shares.append(100 * n / len(d) if len(d) else np.nan)
        fig.add_trace(go.Bar(x=shares, y=PERIODS, name=category, orientation="h", width=.5,
                            marker_color=CATEGORY_COLORS[category], customdata=counts,
                            text=[f"{v:.1f} %".replace(".", ",") if pd.notna(v) and v >= 6 else "" for v in shares],
                            textposition="inside", insidetextanchor="middle", textfont_color="#0B0D10",
                            hovertemplate=category + " · %{y}<br>%{x:.1f} %<br>%{customdata[0]} / %{customdata[1]} titres<extra></extra>"))
    style(fig)
    fig.update_layout(barmode="stack", showlegend=False, margin_t=20, uniformtext=dict(minsize=11, mode="hide"))
    fig.update_xaxes(range=[0, 100], ticksuffix=" %", title="Titres (%)", dtick=25)
    fig.update_yaxes(categoryorder="array", categoryarray=PERIODS, autorange="reversed", showgrid=False)
    for period in PERIODS:
        if frames[period].empty:
            fig.add_annotation(x=50, y=period, text="Sélection vide", showarrow=False)
    return fig


def trend(data, unit, years_a, years_b, median=True):
    fig = go.Figure()
    if median:
        # Un polygone par séquence renseignée : la bande ne traverse jamais un trou.
        runs = data.value.notna().ne(data.value.notna().shift()).cumsum()
        first_band = True
        for _, segment in data[data.value.notna()].groupby(runs):
            fig.add_trace(go.Scatter(x=segment.position, y=segment.q1, mode="lines", line_width=0,
                                     showlegend=False, hoverinfo="skip", connectgaps=False))
            fig.add_trace(go.Scatter(x=segment.position, y=segment.q3, mode="lines", line_width=0,
                                     fill="tonexty", fillcolor="rgba(181,190,205,.20)",
                                     name="Moitié centrale (Q1–Q3)", showlegend=first_band,
                                     hoverinfo="skip", connectgaps=False))
            first_band = False
    fig.add_trace(go.Scatter(x=data.position, y=data.value, mode="lines+markers", name="Médiane" if median else "Part des titres",
                             line=dict(color="#E2E7EE", width=2),
                             marker=dict(size=9, symbol=["circle-open" if p else "circle" for p in data.partial]),
                             connectgaps=False, customdata=data[["label", "valid", "total", "q1", "q3"]],
                             hovertemplate="%{customdata[0]}<br>%{y:.1f} " + unit
                             + "<br>Valeurs exploitables : %{customdata[1]} / %{customdata[2]}"
                             + ("<br>Q1–Q3 : %{customdata[3]:.1f} – %{customdata[4]:.1f} " + unit if median else "") + "<extra></extra>"))
    style(fig)
    fig.update_xaxes(title="Périodes agrégées", tickmode="array", tickvals=data.position,
                     ticktext=data.label, tickangle=-30, range=[data.position.min() - 3, data.position.max() + 3],
                     showgrid=True, gridcolor="#292F38")
    fig.update_layout(margin_b=85)
    fig.update_yaxes(title=unit)
    if not median:
        fig.update_yaxes(range=[0, 100], ticksuffix=" %")
    elif unit == "score / 100":
        fig.update_yaxes(range=[0, 100])
    elif unit != "dB":
        fig.update_yaxes(rangemode="tozero")
    if data.value.notna().sum() == 0:
        empty_note(fig)
    return fig


def world_map(data, period, selected_country=None):
    selected = data[data["période"].eq(period)]
    max_share = data.part.max()
    maximum = max(1, float(max_share)) if pd.notna(max_share) else 100
    fig = go.Figure(go.Choropleth(
        locations=selected.iso, z=selected.part, locationmode="ISO-3", zmin=0, zmax=maximum,
        colorscale=[[0, "#263D56"], [.15, "#376A9A"], [.5, "#589FDB"], [1, "#B9E4FF"]],
        marker_line_color="#101318", marker_line_width=.6,
        colorbar=dict(title="Titres (%)", thickness=12, len=.7, ticksuffix=" %"),
        customdata=selected[["pays", "effectif", "total"]],
        hovertemplate="%{customdata[0]}<br>%{customdata[1]} / %{customdata[2]} titres<br>%{z:.1f} %<extra></extra>",
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
                                     text=[f"{row.pays} · {int(row.effectif)} / {int(row.total)} titres · {row.part:.1f} %"],
                                     hovertemplate="%{text}<extra></extra>"))
    if selected_country:
        row = selected[selected.pays.eq(selected_country)].iloc[0]
        fig.add_trace(go.Scattergeo(locations=[row.iso], locationmode="ISO-3", mode="markers",
                                     marker=dict(size=15, color="#FFB454", symbol="circle-open", line_width=2),
                                     showlegend=False, hoverinfo="skip"))
    style(fig)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), geo=dict(
        projection_type="natural earth", bgcolor="#14171C", showframe=False, showcoastlines=False,
        showland=True, landcolor="#737D8D", showcountries=True, countrycolor="#232A33"))
    if selected.part.notna().sum() == 0:
        empty_note(fig, "Aucune origine exploitable pour cette période")
    return fig
