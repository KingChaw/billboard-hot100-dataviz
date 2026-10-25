"""Non-régression du V2 et parcours Streamlit, sans dépendance de test ajoutée."""
import hashlib
import io
import json
from pathlib import Path
import unittest
from html.parser import HTMLParser

import pandas as pd
from streamlit.testing.v1 import AppTest

from analysis import binary_shares, category_shares, prepare, select
from ui import duration, selection_table
from periods import period_labels

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / 'tests/v2_baseline.json').read_text())



class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cell, self.row = [], None, None
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        elif tag in ('th', 'td'): self.cell = ''
    def handle_data(self, text):
        if self.cell is not None: self.cell += text
    def handle_endtag(self, tag):
        if tag in ('th', 'td'):
            self.row.append(self.cell.strip()); self.cell = None
        elif tag == 'tr': self.rows.append(self.row)


def title_rows(app):
    parser = TableParser()
    for element in app.get('html'):
        body = element.proto.body
        if 'titles-table' in body:
            parser.feed(body)
    return parser.rows


class AnalyticalRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = prepare()

    def test_source_files_unchanged(self):
        for path, expected in BASELINE['hashes'].items():
            if path == 'analysis.py':
                # Préparation corrigée : tester ses résultats plutôt que figer l’erreur.
                continue
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_default_results_identical(self):
        for period, years in [('A', (1958, 1969)), ('B', (2020, 2024))]:
            d, ref = select(self.df, years), BASELINE['periods'][period]
            self.assertEqual(len(d), ref['n'])
            for c, value in ref['medians'].items():
                self.assertEqual(d[c].median(), value)
                self.assertEqual(int(d[c].count()), ref['valid'][c])
            self.assertEqual(d.origin_group.value_counts().to_dict(), ref['origins'])
            self.assertEqual(d.artist_format.value_counts().to_dict(), ref['formats'])
            self.assertEqual(category_shares(d, 'genres').to_dict('records'), ref['genres'])
            binary = ['foreign_language', 'sample', 'interpolation', 'cover']
            self.assertEqual(binary_shares(d, binary, {c: c for c in binary}).to_dict('records'), ref['binary'])

    def test_export_exact_values(self):
        for years, genre in [((1958, 1969), 'Tous les genres'), ((2020, 2024), 'Pop'), ((2020, 2024), 'Non renseigné')]:
            d = select(self.df, years, genre)
            view = selection_table(d)
            self.assertEqual(view.shape, (len(d), 7))
            pd.testing.assert_series_equal(view['Durée (s)'], d.length_sec, check_names=False)
            pd.testing.assert_series_equal(view['Intro (s)'], d.intro_length_sec, check_names=False)
            exported = pd.read_csv(io.BytesIO(view.to_csv(index=False).encode('utf-8-sig')))
            self.assertEqual(exported['Titre'].tolist(), d.song.tolist())
            self.assertEqual(exported['Date'].tolist(), d.date.dt.strftime('%Y-%m-%d').tolist())
            self.assertEqual(exported['Artiste'].tolist(), d.artist.tolist())

    def test_display_preserves_half_second_and_missing(self):
        self.assertEqual(duration(161.5), '2 min 41,5 s')
        self.assertEqual(duration(200), '3 min 20 s')
        self.assertEqual(duration(float('nan')), 'Non disponible')


def go_to(app, route):
    groups = [
        ['summary'],
        ['format_trend', 'duration', 'intro', 'sound', 'central', 'presence', 'genres'],
        ['origin_trend', 'origins', 'map'],
        ['ages', 'formats', 'collabs', 'teams', 'reuse'],
        ['data_a', 'data_b'],
    ]
    group = next(i for i, routes in enumerate(groups) if route in routes)
    app.button(key=f'group_{group}').click().run()
    app.button(key='nav_' + route).click().run()


ROUTES = ['format_trend', 'duration', 'intro', 'sound', 'central', 'presence', 'genres',
          'origin_trend', 'origins', 'map', 'ages', 'formats', 'collabs', 'teams', 'reuse']


class DashboardJourneys(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        self.clean()

    def clean(self):
        self.assertFalse(self.app.exception, [x.message for x in self.app.exception])

    def go(self, route):
        go_to(self.app, route)
        self.clean()

    def chart(self):
        return json.loads(self.app.get('plotly_chart')[0].proto.spec)

    def test_default_and_every_route(self):
        self.assertEqual(self.app.radio(key='mode').value, 'Décennies')
        self.assertEqual(self.app.selectbox(key='decade_a').value, 2000)
        self.assertEqual(self.app.selectbox(key='decade_b').value, 'recent')
        self.assertIn('129 titres', ' '.join(m.value for m in self.app.markdown))
        self.assertIn('81 titres', ' '.join(m.value for m in self.app.markdown))
        for route in ROUTES:
            with self.subTest(route=route):
                self.go(route)
                self.assertEqual(len(self.app.get('plotly_chart')), 1)
                self.assertTrue(self.app.get('download_button'))
                detail = [e for e in self.app.expander if e.label == 'Détails']
                self.assertEqual(len(detail), 1)
                self.assertFalse(detail[0].proto.expanded)
        for route in ['data_a', 'data_b']:
            self.go(route)
            self.assertFalse(self.app.get('plotly_chart'))
            self.assertTrue(self.app.get('download_button'))
        self.assertIn('Titres associés', (ROOT / 'ui.py').read_text())

    def test_all_shortcuts_preserve_filters(self):
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.selectbox(key='decade_a').set_value(1980).run()
        for route in ['duration', 'intro', 'origins', 'map', 'ages', 'teams']:
            self.go('summary')
            self.app.button(key='shortcut_' + route).click().run()
            self.clean()
            self.assertEqual(self.app.session_state['route'], route)
            self.assertEqual(self.app.selectbox(key='genre').value, 'Pop')
            self.assertEqual(self.app.selectbox(key='decade_a').value, 1980)

    def test_modes_keep_independent_choices_and_overlap(self):
        self.app.selectbox(key='decade_a').set_value(1980).run()
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((2020, 2024)).run()
        self.app.slider(key='years_b').set_value((2020, 2024)).run()
        self.go('data_a')
        first = title_rows(self.app)
        self.go('data_b')
        self.assertEqual(first, title_rows(self.app))
        self.assertEqual(len(first) - 1, 81)
        self.app.radio(key='mode').set_value('Décennies').run()
        self.assertEqual(self.app.selectbox(key='decade_a').value, 1980)
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.assertEqual(self.app.slider(key='years_a').value, (2020, 2024))

    def test_selectors_persist_across_pages(self):
        for route, key, values in [
            ('sound', 'sonic', ['energy', 'danceability', 'acousticness', 'loudness_d_b', 'bpm']),
            ('teams', 'credit', ['writers_all', 'producer_count', 'writers_original']),
            ('format_trend', 'evolution_metric', ['length_sec', 'intro_length_sec', 'bpm', 'energy', 'danceability', 'acousticness', 'loudness_d_b']),
            ('origin_trend', 'origin_metric', ['États-Unis uniquement (dont Porto Rico)', 'Mixte États-Unis / autres', 'Hors États-Unis uniquement'])]:
            self.go(route)
            for value in values:
                self.app.selectbox(key=key).set_value(value).run()
                self.clean()
            self.go('summary')
            self.go(route)
            self.assertEqual(self.app.selectbox(key=key).value, values[-1])

    def test_empty_one_or_both_periods_all_routes(self):
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1958, 1959)).run()
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        for route in ROUTES + ['data_a', 'summary']:
            self.go(route)
        self.go('data_a')
        self.assertEqual(len(title_rows(self.app)) - 1, 0)
        self.app.slider(key='years_b').set_value((1958, 1959)).run()
        for route in ROUTES + ['data_b', 'summary']:
            self.go(route)

    def test_missing_metric_is_not_zero(self):
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1959, 1959)).run()
        self.app.slider(key='years_b').set_value((1960, 1969)).run()
        self.app.selectbox(key='genre').set_value('Jazz').run()
        self.go('teams')
        self.app.selectbox(key='credit').set_value('producer_count').run()
        self.clean()
        self.assertIn('Non disponible', json.dumps(self.chart()))

    def test_download_matches_displayed_rows(self):
        from unittest.mock import patch
        import streamlit as st
        self.app.selectbox(key='genre').set_value('Pop').run()
        for route in ['data_a', 'data_b']:
            with patch('streamlit.download_button', wraps=st.download_button) as download:
                self.go(route)
                csv = pd.read_csv(io.BytesIO(download.call_args.args[1]))
            rows = title_rows(self.app)
            self.assertEqual(rows[0], list(csv.columns))
            # Même sélection, ordre et précision que le HTML, y compris les valeurs manquantes.
            expected = csv.astype(object).where(csv.notna(), 'Non disponible').astype(str).values.tolist()
            self.assertEqual(rows[1:], expected)



class NewAggregates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = prepare()
        cls.frames = {'Période A': select(cls.df, (2000, 2009)), 'Référence B': select(cls.df, (2020, 2025))}

    def test_decade_values_from_real_rows(self):
        from dashboard_data import decades, ORIGINS, METRICS
        for genre in ['Tous les genres', 'Pop']:
            data = select(self.df, (1958, 2025), genre)
            for column in METRICS:
                result = decades(data, column=column, coverage=(1958, 2025)).set_index('decade')
                for decade in [1960, 2000, 2020]:
                    vals = select(data, (decade, decade + 9))[column].dropna()
                    self.assertAlmostEqual(result.loc[decade, 'value'], vals.median())
                    self.assertAlmostEqual(result.loc[decade, 'q1'], vals.quantile(.25))
                    self.assertAlmostEqual(result.loc[decade, 'q3'], vals.quantile(.75))
                self.assertTrue(result.loc[1950, 'partial'])
                self.assertTrue(result.loc[2020, 'partial'])
                self.assertFalse(result.loc[2000, 'partial'])
            for origin in list(ORIGINS)[:3]:
                result = decades(data, origin=origin, coverage=(1958, 2025)).set_index('decade')
                d = select(data, (2000, 2009))
                self.assertAlmostEqual(result.loc[2000, 'value'], 100 * d.origin_group.eq(origin).sum() / len(d))

    def test_stacked_totals_include_unknowns(self):
        from charts import stacked
        from dashboard_data import ORIGINS
        d = self.df.iloc[:4].copy()
        d['origin_group'] = list(ORIGINS)
        d['artist_format'] = ['Groupe', 'Duo', 'Solo', 'Non renseigné']
        frames = {'Période A': d, 'Référence B': d.iloc[:2]}
        for col, order in [('origin_group', list(ORIGINS.values())), ('artist_format', d.artist_format.tolist())]:
            fig = stacked(frames, col, order)
            for i in range(2):
                self.assertAlmostEqual(sum(trace.x[i] for trace in fig.data), 100)
                self.assertTrue(all(trace.y[i] == list(frames)[i] for trace in fig.data))
            self.assertEqual(fig.data[-1].x[0], 25)

    def test_map_shared_scale_country_shares_and_unknowns(self):
        from dashboard_data import country_frame
        from charts import world_map
        data = country_frame(self.frames, self.df)
        self.assertTrue(data.iso.notna().all())
        self.assertAlmostEqual(world_map(data, 'Période A').data[0].zmax, world_map(data, 'Référence B').data[0].zmax)
        for period, d in self.frames.items():
            for _, row in data[data['période'].eq(period)].iterrows():
                count = d.origins.map(lambda origins: row.source in origins).sum()
                self.assertEqual(row.effectif, count)
                self.assertAlmostEqual(row.part, count * 100 / len(d))
        self.assertTrue(data.part.eq(0).any())
        missing = self.df.iloc[:2].copy()
        missing['origins'] = [[], []]
        unavailable = country_frame({'Période A': missing, 'Référence B': self.df.iloc[:0]}, self.df)
        self.assertTrue(unavailable.part.isna().all())
        self.assertTrue((data.iso == 'PRI').any())

    def test_nonexclusive_points_and_missing_binary(self):
        from charts import binary_frame, points
        d = self.df.iloc[:3].copy()
        d['sample'], d['interpolation'], d['cover'] = 1, 1, float('nan')
        frames = {'Période A': d, 'Référence B': d}
        columns = {'sample': 'Sample', 'interpolation': 'Interpolation', 'cover': 'Reprise'}
        data = binary_frame(frames, columns)
        self.assertTrue(data[data['catégorie'].eq('Reprise')].part.isna().all())
        self.assertEqual(data.part.sum(), 400)
        fig = points(data, frames, list(columns.values()))
        self.assertEqual([t.name for t in fig.data if t.showlegend is not False], list(period_labels(frames).values()))


if __name__ == '__main__':
    unittest.main()
