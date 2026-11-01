"""Interface claire : filtres latéraux, deux niveaux d'onglets et cartes sobres."""
import streamlit as st

COLORS = {"Période A": "#6153AD", "Référence B": "#167C80"}
FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
CSS = """
<style>
:root { --surface: #FFFFFF; --line: #E8E8ED; --muted: #686975; --accent: #6153AD; --banner-height: 76px; }
.stApp { background: #FFFFFF; color: #242631; }
[data-testid="stHeader"] { background: transparent; z-index: 1000000; }
[data-testid="stExpandSidebarButton"] { position: fixed; top: 20px; left: 12px; background: #FFFFFF; }
[data-testid="stAppDeployButton"] { display: none; }
.brand-banner { position: fixed; top: 0; left: 0; right: 0; height: var(--banner-height); display: flex; align-items: center; gap: 18px; padding: 0 48px; background: linear-gradient(100deg, #231C52 0%, #4E4598 55%, #167C80 100%); z-index: 999990; pointer-events: none; overflow: hidden; }
/* Sillons de vinyle en filigrane, à droite du bandeau. */
.brand-banner::after { content: ""; position: absolute; right: -60px; top: 50%; width: 260px; height: 260px; transform: translateY(-50%); border-radius: 50%; background: repeating-radial-gradient(circle, rgba(255,255,255,.10) 0 1px, transparent 1px 7px); }
.brand { color: #FFFFFF; font-size: 1.9rem; font-weight: 850; letter-spacing: -.055em; }
.brand b { font-weight: 500; color: #6FD6C0; }
.brand-sub { color: rgba(255,255,255,.78); font-size: .9rem; font-weight: 500; border-left: 1px solid rgba(255,255,255,.35); padding-left: 18px; }
/* Égaliseur animé : quelques barres qui dansent, coupées si l'utilisateur limite les animations. */
.eq { display: flex; align-items: flex-end; gap: 3px; height: 26px; }
.eq i { width: 4px; background: #6FD6C0; border-radius: 2px; animation: eq 1.1s ease-in-out infinite; }
.eq i:nth-child(2) { animation-delay: -.3s; } .eq i:nth-child(3) { animation-delay: -.6s; } .eq i:nth-child(4) { animation-delay: -.9s; } .eq i:nth-child(5) { animation-delay: -.45s; }
@keyframes eq { 0%, 100% { height: 25%; } 50% { height: 100%; } }
@media (prefers-reduced-motion: reduce) { .eq i { animation: none; height: 60%; } }
[data-testid="stHeader"] button, [data-testid="stMainMenu"] button { color: #FFFFFF !important; }
[data-testid="stMainBlockContainer"] { max-width: 1600px; padding: calc(var(--banner-height) - 2px) 40px 24px; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: .65rem; }
[data-testid="stMarkdownContainer"] { margin-bottom: 0; }
.st-key-page_position, .st-key-chart_viewport { position: absolute; height: 0; min-height: 0; margin: 0; }
/* Les sondes invisibles ne doivent pas élargir le viewport mobile. */
.st-key-page_position { width: 0 !important; overflow: hidden; }
[class*="st-key-chart_viewport_format_"] { position: absolute; width: 0 !important; height: 0; min-height: 0; margin: 0; overflow: hidden; }
/* Pays et territoires : la sonde ne doit pas dépasser les marges sur mobile. */
.stApp:has(.st-key-nav_map button[kind="primary"]) .st-key-chart_viewport { width: 0 !important; overflow: hidden; }
[data-testid="stSidebarHeader"] { height: 0; min-height: 0; padding: 0; }
[data-testid="stSidebarHeader"] button { position: absolute; right: 8px; top: 18px; z-index: 2; }
[data-testid="stSidebar"] { top: var(--banner-height); height: calc(100% - var(--banner-height)); background: #F7F7FA; border-right: 1px solid var(--line); }
[data-testid="stSidebar"][aria-expanded="true"] { min-width: 340px; }
[data-testid="stSidebar"][aria-expanded="false"] { min-width: 0 !important; max-width: 0 !important; width: 0 !important; border: 0; visibility: hidden; }
[data-testid="stSidebar"][aria-expanded="false"] * { visibility: hidden !important; }
[data-testid="stSidebarUserContent"] { padding: 0 28px 36px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 1.3rem; }
.filter-heading { font-size: 1.35rem; font-weight: 700; color: #20212A; margin: 0 0 4px; padding: 12px 0 14px; border-bottom: 2px solid var(--line); }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-size: .85rem !important; font-weight: 700; letter-spacing: .08em; color: var(--accent) !important; padding: .35rem 0 .35rem 1rem !important; border-left: 3px solid var(--accent); line-height: 1.1; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: .95rem !important; font-weight: 600; color: #20212A; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p { font-size: .95rem !important; }
[data-testid="stSidebar"] hr { margin: 1rem 0 .4rem; border-color: var(--line); }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #FFFFFF; border-color: #DCDDE5; min-height: 44px; font-size: .95rem; border-radius: 6px; }
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color: var(--accent); }
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
.kpi-grid.compact .kpi { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 36px; padding: 12px 18px; }
.kpi-grid.compact .kpi h3 { margin: 0; }
.kpi-grid.compact .kpi-values { display: flex; gap: 32px; }
.kpi-grid.compact .kpi-value { font-size: 1.3rem; margin: 0; }
.kpi-grid.compact .kpi-foot { margin: 0 0 0 auto; padding: 0; border: 0; }
.st-key-back_top { position: fixed; right: 24px; bottom: 24px; z-index: 1000; width: auto !important; }
.st-key-back_top button { border-radius: 999px; box-shadow: 0 2px 8px rgba(0,0,0,.15); background: #FFFFFF; }
.period-counts { display: grid; gap: 8px; margin: .2rem 0 .4rem; }
.period-counts > div { background: #FFFFFF; border: 1px solid var(--line); border-left: 4px solid #6153AD; border-radius: 6px; padding: 10px 14px; font-size: .9rem !important; color: var(--muted); }
.period-counts > .count-b { border-left-color: #167C80; }
.period-counts span { display: block; font-weight: 600; font-size: .9rem !important; }
.period-counts b { font-size: 1.6rem !important; line-height: 1.2; font-weight: 700; color: #242631; margin-right: .35rem; }
.kpi-grid.alert .kpi { border-left: 4px solid #8A90A0; background: #F6F6F8; }
.kpi-grid.alert .kpi h3 { color: #4A4D5A; font-weight: 600; }
.kpi-grid.alert .kpi-value { color: #4A4D5A; font-size: 1.1rem; }
/* Choix Auteurs / Producteurs : deux boutons centrés, celui sélectionné en couleur. */
.st-key-team_role { width: 100% !important; }
.st-key-team_role [role="radiogroup"] { justify-content: center; gap: 10px; width: 100%; }
.st-key-team_role [data-testid="stRadioOption"] { border: 1.5px solid var(--line); border-radius: 999px; padding: 4px 18px; background: #FFFFFF; cursor: pointer; margin: 0; }
.st-key-team_role [data-testid="stRadioOption"] > div > div:first-child { display: none; }
.st-key-team_role [data-testid="stRadioOption"] p { font-size: .92rem !important; font-weight: 600; color: var(--muted); }
.st-key-team_role [data-testid="stRadioOption"][data-selected="true"] { border-color: var(--accent); background: var(--accent); }
.st-key-team_role [data-testid="stRadioOption"][data-selected="true"] p { color: #FFFFFF; }
/* Frise de parcours (vue d'ensemble) : pastilles numérotées reliées par une ligne. */
.journey { margin: .2rem 0 1rem; }
.journey-title { font-size: .8rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--accent); margin-bottom: .7rem; }
.journey ol { list-style: none; counter-reset: step; display: flex; flex-wrap: wrap; gap: 14px 0; padding: 0; margin: 0; }
.journey li { counter-increment: step; position: relative; flex: 1 1 140px; min-width: 130px; padding: 0 10px 0 0; }
.journey li::before { content: counter(step); display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: var(--accent); color: #FFFFFF; font-weight: 700; font-size: .9rem; position: relative; z-index: 1; margin-bottom: 8px; }
.journey li::after { content: ""; position: absolute; top: 15px; left: 30px; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent), #167C80); opacity: .35; }
.journey li:last-child::after { display: none; }
.journey li b { display: block; font-size: .95rem; color: #20212A; }
.journey li span { display: block; font-size: .82rem; color: var(--muted); line-height: 1.35; margin-top: 2px; }
.titles-scroll { max-height: 380px; overflow: auto; border: 1px solid var(--line); }
.titles-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.titles-table th { position: sticky; top: 0; background: #F6F6F8; text-align: left; }
.titles-table td, .titles-table th { padding: .6rem .8rem; border-bottom: 1px solid var(--line); min-width: 130px; }
.titles-table td { vertical-align: top; }
:focus-visible { outline: 3px solid #6153AD !important; outline-offset: 3px; }
.category-legend { display: flex; flex-wrap: wrap; gap: .4rem 1rem; font-size: .8rem; }
.category-legend i { display: inline-block; width: .65rem; height: .65rem; border-radius: 2px; margin-right: .35rem; }
.category-legend details { max-width: 440px; }
.category-legend.large { justify-content: center; gap: .5rem 2rem; font-size: 1rem; font-weight: 500; padding: .3rem 0; }
.category-legend.large i { width: .9rem; height: .9rem; }
.category-legend summary { cursor: pointer; list-style: none; }
.category-legend details p { font-size: .8rem; color: #555763; margin: .4rem 0; }
/* Aides et exemples réservés à Format & son. */
.format-cards .kpi-values > div:nth-child(2) .kpi-value { color: #167C80; }
.format-reading, [class*="st-key-reading_existing_"] { border-left: 3px solid #C9C4E8; background: #F8F8FB; padding: 12px 16px; font-size: .88rem; color: #555763; }
.format-reading b { color: #4E4598; font-size: .85rem; }
.format-reading p, [class*="st-key-reading_existing_"] p { margin: 4px 0 0; line-height: 1.55; }
[class*="st-key-reading_existing_"] [data-testid="stMarkdownContainer"] { font-size: .88rem; color: #555763; }
[class*="st-key-reading_existing_"] p, [class*="st-key-reading_existing_"] li { font-size: .88rem; line-height: 1.55; }
[class*="st-key-reading_existing_"] strong { color: #4E4598; }
[class*="st-key-reading_existing_"] p:first-child > strong:first-child { font-size: .85rem; }
[data-testid="stLayoutWrapper"]:has(> .st-key-dashboard_navigation) { position: sticky; top: var(--banner-height); z-index: 100; background: #FFFFFF; }
.st-key-dashboard_navigation { gap: 0; box-shadow: 0 3px 5px rgba(36,38,49,.04); }
.stApp:has(.st-key-dashboard_navigation) [data-testid="stMain"] { scroll-padding-top: calc(var(--banner-height) + 116px); }
.stApp:has(.st-key-dashboard_navigation):not(:has(.st-key-secondary_nav)) [data-testid="stMain"] { scroll-padding-top: calc(var(--banner-height) + 58px); }
.stApp:has(.st-key-group_1 button[kind="primary"]) .st-key-back_top,
.stApp:has(.st-key-group_4 button[kind="primary"]) .st-key-back_top { position: static; margin-left: auto; }
.format-cards { gap: 10px; }
.format-cards .kpi { padding: 12px 16px; }
.format-cards .kpi h3 { font-size: .85rem; margin: 0 0 6px; }
.format-cards .kpi-values { gap: 10px; }
.format-cards .kpi-value { margin: 2px 0; }
.format-cards .kpi-count { display: block; color: var(--muted); font-size: .75rem; }
.stApp:has(.st-key-nav_duration button[kind="primary"]) .format-cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.stApp:has(.st-key-nav_duration button[kind="primary"]) .format-cards .kpi-value { font-size: 1.05rem; white-space: nowrap; overflow-wrap: normal; }
.stApp:has(.st-key-nav_format_trend button[kind="primary"]) .format-cards .kpi-value { font-size: 1.15rem; line-height: 1.25; white-space: nowrap; overflow-wrap: normal; }
.stApp .format-chart-title { font-size: 1.3rem; font-weight: 650; padding: 6px 0 4px; margin: 0; line-height: 1.25; }
.format-example { padding: 10px 0; border-bottom: 1px solid var(--line); overflow-wrap: anywhere; font-size: .9rem; }
.format-example > span { display: inline-block; color: #6153AD; font-size: .8rem; margin-right: 10px; }
.format-example small { display: block; color: var(--muted); margin-top: 4px; }
@media (max-width: 767px) {
 :root { --banner-height: 72px; }
 .brand-banner { padding: 0 22px 0 58px; }
 .brand { font-size: 1.55rem; }
 .brand-sub, .eq { display: none; }
 [data-testid="stMainBlockContainer"] { padding: calc(var(--banner-height) + 16px) 16px 24px; }
 [data-testid="stSidebar"][aria-expanded="true"] { position: fixed !important; width: min(320px, 90vw) !important; min-width: 0 !important; max-width: 90vw !important; transform: none !important; }
 .st-key-primary_nav, .st-key-secondary_nav { gap: 1.2rem; }
 .st-key-primary_nav button p, .st-key-secondary_nav button p { font-size: .9rem; }
 .selection { font-size: .77rem; gap: .35rem .8rem; }
 .kpi-grid { grid-template-columns: 1fr; }
 .kpi { padding: 18px; }
 .kpi-value { font-size: 1.4rem; }
 .format-cards .kpi { padding: 10px 12px; }
 .stApp:has(.st-key-nav_duration button[kind="primary"]) .format-cards { grid-template-columns: 1fr; }
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
