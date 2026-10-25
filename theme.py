"""Palette commune et interface compacte, sans police externe."""
import streamlit as st

COLORS = {"Période A": "#4C9AFF", "Référence B": "#FFB454"}
FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
CSS = """
<style>
:root { --surface: #14171C; --line: #292F38; --muted: #A7AFBA; }
.stApp { background: #0B0D10; color: #F5F7FA; }
[data-testid="stMainBlockContainer"] { max-width: 1500px; padding: 2.75rem 2rem .6rem; }
[data-testid="stHeader"] { background: transparent; height: 2.5rem; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: .65rem; }
/* Streamlit retire 1rem sous le Markdown : avec nos petits espacements,
   cette marge négative faisait remonter titres et boutons sur les cartes. */
[data-testid="stMarkdownContainer"] { margin-bottom: 0; }
[data-testid="stSidebar"] { background: #101318; border-right: 1px solid var(--line); }
[data-testid="stSidebarUserContent"] { padding-top: 1rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .45rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] { background: transparent; }
[data-testid="stSidebar"] [data-testid="stButton"] button { text-align: left; justify-content: flex-start; padding: .25rem .6rem; min-height: 2rem; }
[data-testid="stSidebar"] [data-testid="stButton"] p { font-size: .87rem; }
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] p { color: #0B0D10; }
[data-testid="stSidebar"] h2 { font-size: 1rem; }
[data-testid="stSidebar"] hr { margin: .4rem 0; }
h1, h2, h3 { letter-spacing: -.025em; }
.stApp h1 { font-size: clamp(1.4rem, 2.2vw, 2rem); padding: .1rem 0 .3rem; }
.stApp h2 { font-size: 1.1rem; padding: .25rem 0; }
.stApp h3 { font-size: 1rem; }
[data-testid="stCaptionContainer"] p { color: var(--muted); }
[data-testid="stExpander"] { border-radius: 10px; background: #101318; }
[data-testid="stPlotlyChart"] { border-radius: 12px; }
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button { border-radius: 8px; }
.brand { font-size: 1.5rem; font-weight: 850; letter-spacing: -.05em; margin-bottom: .3rem; }
.brand span { color: #F293B6; }
.selection { display: flex; flex-wrap: wrap; gap: .5rem 1.2rem; align-items: center; font-size: .85rem; padding: .65rem .9rem; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
.selection small { color: var(--muted); margin-left: .4rem; }
.period-a { color: #4C9AFF; } .period-b { color: #FFB454; }
.kpi-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
.kpi-grid.single { grid-template-columns: 1fr; }
.kpi { border: 1px solid var(--line); border-radius: 12px; background: var(--surface); padding: .8rem 1rem; min-width: 0; }
.kpi h3 { font-size: .9rem; font-weight: 600; padding: 0; margin: 0 0 .45rem; }
.kpi-values { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
.kpi-values > div { min-width: 0; overflow-wrap: anywhere; }
.period-label { font-size: .8rem; font-weight: 650; }
.kpi-value { font-size: clamp(1.05rem, 1.8vw, 1.55rem); font-weight: 750; }
.kpi-foot { font-size: .85rem; color: var(--muted); margin-top: .35rem; }
.titles-scroll { max-height: 380px; overflow: auto; border: 1px solid #505B6C; border-radius: 8px; }
.titles-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.titles-table th { position: sticky; top: 0; background: #202630; text-align: left; }
.titles-table td, .titles-table th { padding: .6rem .8rem; border-bottom: 1px solid #505B6C; min-width: 130px; }
.titles-table td { vertical-align: top; }
:focus-visible { outline: 3px solid #FFB454 !important; outline-offset: 3px; }
.category-legend { display: flex; flex-wrap: wrap; gap: .4rem 1rem; font-size: .8rem; }
.category-legend button { border: 0; background: none; padding: .2rem 0; color: #F5F7FA; text-align: left; cursor: help; font: inherit; }
.category-legend i { display: inline-block; width: .65rem; height: .65rem; border-radius: 2px; margin-right: .35rem; }
.category-legend details { max-width: 440px; }
.category-legend summary { cursor: pointer; list-style: none; }
.category-legend details p { font-size: .8rem; color: #CDD2DB; margin: .4rem 0; }
@media (max-width: 767px) {
 [data-testid="stMainBlockContainer"] { padding: 2.7rem .75rem 1rem; }
 .selection { font-size: .77rem; gap: .35rem .8rem; padding: .5rem; }
 .kpi-grid { grid-template-columns: 1fr; }
 .kpi-value { font-size: 1.35rem; }
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
