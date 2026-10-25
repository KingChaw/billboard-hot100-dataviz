"""Interface claire : filtres latéraux, deux niveaux d'onglets et cartes sobres."""
import streamlit as st

COLORS = {"Période A": "#6153AD", "Référence B": "#167C80"}
FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
CSS = """
<style>
:root { --surface: #FFFFFF; --line: #E8E8ED; --muted: #686975; --accent: #6153AD; --banner-height: 100px; }
.stApp { background: #FFFFFF; color: #242631; }
[data-testid="stHeader"] { background: transparent; z-index: 1000000; }
[data-testid="stExpandSidebarButton"] { position: fixed; top: 20px; left: 12px; background: #FFFFFF; }
[data-testid="stAppDeployButton"] { display: none; }
.brand-banner { position: fixed; top: 0; left: 0; right: 0; height: var(--banner-height); display: flex; align-items: center; padding: 0 48px; background: #FFFFFF; border-bottom: 1px solid var(--line); z-index: 999990; pointer-events: none; }
.brand { color: #4E4598; font-size: 2rem; font-weight: 850; letter-spacing: -.055em; }
.brand b { font-weight: 500; }
[data-testid="stMainBlockContainer"] { max-width: 1600px; padding: calc(var(--banner-height) + 24px) 40px 24px; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: .65rem; }
[data-testid="stMarkdownContainer"] { margin-bottom: 0; }
.st-key-page_position, .st-key-chart_viewport { position: absolute; height: 0; min-height: 0; margin: 0; }
[data-testid="stSidebarHeader"] { height: 0; min-height: 0; padding: 0; }
[data-testid="stSidebarHeader"] button { position: absolute; right: 8px; top: 18px; z-index: 2; }
[data-testid="stSidebar"] { top: var(--banner-height); height: calc(100% - var(--banner-height)); background: #FFFFFF; border-right: 1px solid var(--line); }
[data-testid="stSidebar"][aria-expanded="true"] { min-width: 300px; }
[data-testid="stSidebar"][aria-expanded="false"] { min-width: 0 !important; max-width: 0 !important; width: 0 !important; border: 0; visibility: hidden; }
[data-testid="stSidebar"][aria-expanded="false"] * { visibility: hidden !important; }
[data-testid="stSidebarUserContent"] { padding: 0 26px 30px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .8rem; }
.filter-heading { font-size: 1.15rem; font-weight: 600; margin: 0 -26px 12px; padding: 22px 26px; border-bottom: 1px solid var(--line); }
[data-testid="stSidebar"] h2 { font-size: .95rem; font-weight: 700; letter-spacing: .035em; padding: .4rem 0; }
[data-testid="stSidebar"] hr { margin: .65rem 0; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #FAFAFC; border-color: var(--line); }
/* Chaque rangée garde ses boutons sur une ligne ; seul le rail défile. */
.st-key-primary_nav, .st-key-secondary_nav { border-bottom: 1px solid var(--line); padding: 0; min-width: 0; max-width: 100%; flex-wrap: nowrap !important; overflow-x: auto; gap: 1.5rem; scrollbar-width: thin; }
.st-key-primary_nav [data-testid="stHorizontalBlock"],
.st-key-secondary_nav [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; overflow-x: auto; gap: 1.5rem; scrollbar-width: thin; padding-bottom: 0; }
.st-key-primary_nav [data-testid="stElementContainer"],
.st-key-secondary_nav [data-testid="stElementContainer"] { flex: 0 0 auto; width: max-content; }
.st-key-primary_nav button, .st-key-secondary_nav button { border: 0 !important; border-bottom: 4px solid transparent !important; border-radius: 0; background: transparent !important; color: var(--muted) !important; padding: .65rem 0 1rem; min-height: 48px; box-shadow: none !important; white-space: nowrap; }
.st-key-primary_nav button p, .st-key-secondary_nav button p { font-size: .98rem; }
.st-key-primary_nav button[kind="primary"], .st-key-secondary_nav button[kind="primary"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; font-weight: 650; }
.st-key-primary_nav button:hover, .st-key-secondary_nav button:hover { color: var(--accent) !important; }
h1, h2, h3 { letter-spacing: -.025em; color: #20212A; }
.stApp h1 { font-size: clamp(1.45rem, 2.2vw, 2rem); padding: .35rem 0; font-weight: 700; }
.stApp h2 { font-size: 1.2rem; padding: 1rem 0 .5rem; }
.stApp h3 { font-size: 1.05rem; padding: .5rem 0 .25rem; }
[data-testid="stCaptionContainer"] p { color: var(--muted); }
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 2px; background: #FFFFFF; }
[data-testid="stPlotlyChart"] { border: 1px solid var(--line); border-radius: 2px; }
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button { border-radius: 3px; }
.selection { display: flex; flex-wrap: wrap; gap: .5rem 1.4rem; align-items: center; font-size: .85rem; padding: .65rem 0; border-bottom: 1px solid var(--line); background: #FFFFFF; }
.selection small { color: var(--muted); margin-left: .45rem; }
.period-a { color: #6153AD; } .period-b { color: #167C80; }
.kpi-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.kpi-grid.single { grid-template-columns: 1fr; }
.kpi { border: 1px solid var(--line); border-radius: 1px; background: #FFFFFF; padding: 22px; min-width: 0; }
.kpi h3 { color: var(--muted); font-size: .95rem; font-weight: 500; padding: 0; margin: 0 0 18px; }
.kpi-values { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.kpi-values > div { min-width: 0; overflow-wrap: anywhere; }
.period-label { font-size: .8rem; font-weight: 600; }
.kpi-value { color: #4E4598; font-size: clamp(1.2rem, 2vw, 1.8rem); font-weight: 650; margin: .3rem 0; }
.kpi-foot { font-size: .78rem; line-height: 1.6; color: var(--muted); margin-top: 14px; padding-top: 12px; border-top: 1px solid #F0F0F4; }
.titles-scroll { max-height: 380px; overflow: auto; border: 1px solid var(--line); }
.titles-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.titles-table th { position: sticky; top: 0; background: #F6F6F8; text-align: left; }
.titles-table td, .titles-table th { padding: .6rem .8rem; border-bottom: 1px solid var(--line); min-width: 130px; }
.titles-table td { vertical-align: top; }
:focus-visible { outline: 3px solid #6153AD !important; outline-offset: 3px; }
.category-legend { display: flex; flex-wrap: wrap; gap: .4rem 1rem; font-size: .8rem; }
.category-legend i { display: inline-block; width: .65rem; height: .65rem; border-radius: 2px; margin-right: .35rem; }
.category-legend details { max-width: 440px; }
.category-legend summary { cursor: pointer; list-style: none; }
.category-legend details p { font-size: .8rem; color: #555763; margin: .4rem 0; }
@media (max-width: 767px) {
 :root { --banner-height: 72px; }
 .brand-banner { padding: 0 22px 0 58px; }
 .brand { font-size: 1.55rem; }
 [data-testid="stMainBlockContainer"] { padding: calc(var(--banner-height) + 16px) 16px 24px; }
 [data-testid="stSidebar"][aria-expanded="true"] { position: fixed !important; width: min(320px, 90vw) !important; min-width: 0 !important; max-width: 90vw !important; transform: none !important; }
 .st-key-primary_nav, .st-key-secondary_nav { gap: 1.2rem; }
 .st-key-primary_nav button p, .st-key-secondary_nav button p { font-size: .9rem; }
 .selection { font-size: .77rem; gap: .35rem .8rem; }
 .kpi-grid { grid-template-columns: 1fr; }
 .kpi { padding: 18px; }
 .kpi-value { font-size: 1.4rem; }
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
