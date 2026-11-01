"""Contrats statistiques et parcours de la refonte Format & son uniquement."""
import json
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

from analysis import introduction_ratios, prepare, select
from charts import binary_frame, format_bars, genre_trend, genre_frame
from dashboard_data import FORMAT_METRICS, SOUND_HELP, comparison_rows, decades, quartile_examples
from test_regression import FORMAT_ROUTES, ROOT, go_to, title_rows


class FormatStatistics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = prepare()

    def test_individual_ratios_before_median(self):
        d = pd.DataFrame({'length_sec': [100, 200, 1000], 'intro_length_sec': [10, 40, 50]})
        ratios = introduction_ratios(d)
        self.assertEqual(ratios.tolist(), [10, 20, 5])
        self.assertEqual(ratios.median(), 10)
        self.assertNotEqual(ratios.median(), 100 * d.intro_length_sec.median() / d.length_sec.median())

    def test_ratio_missing_zero_and_invalid_duration(self):
        d = pd.DataFrame({'length_sec': [100, 0, -5, None, 100, 100],
                          'intro_length_sec': [0, 5, 5, 5, None, 20]}, index=list('abcdef'))
        ratios = introduction_ratios(d)
        self.assertEqual(ratios.index.tolist(), list('abcdef'))
        self.assertEqual(ratios.dropna().to_dict(), {'a': 0, 'f': 20})
        self.assertTrue(introduction_ratios(d.iloc[:0]).empty)
        self.assertTrue(introduction_ratios(d.iloc[1:5]).isna().all())

    def test_corpus_and_filtered_ratio_history(self):
        self.assertEqual(len(self.data), 1177)
        for genre in ['Tous les genres', 'Pop', 'Non renseigné']:
            data = select(self.data, (1958, 2025), genre)
            pd.testing.assert_series_equal(data.intro_ratio, introduction_ratios(data), check_names=False)
            history = decades(data, column='intro_ratio', coverage=(1958, 2025))
            self.assertEqual(history.total.sum(), len(data))
            for row in history.itertuples():
                ratios = introduction_ratios(select(data, (row.start, row.end))).dropna()
                self.assertEqual(row.valid, len(ratios))
                if len(ratios):
                    self.assertEqual(row.value, ratios.median())
                    self.assertEqual(row.q1, ratios.quantile(.25))
                    self.assertEqual(row.q3, ratios.quantile(.75))

    def test_genre_history_counts_missing_partial_and_filter(self):
        for global_genre in ['Tous les genres', 'Pop', 'Non renseigné']:
            data = select(self.data, (1958, 2025), global_genre)
            for genre in ['Rock', 'Pop', 'Non renseigné']:
                history = decades(data, genre=genre, coverage=(1958, 2025))
                self.assertTrue(history.iloc[0].partial)
                self.assertTrue(history.iloc[-1].partial)
                for row in history.itertuples():
                    d = select(data, (row.start, row.end))
                    count = d.genres.map(lambda g: genre in g).sum()
                    self.assertEqual(row.count, count)
                    self.assertEqual(row.total, len(d))
                    if row.valid:
                        self.assertAlmostEqual(row.value, 100 * count / len(d))
                    else:
                        self.assertTrue(pd.isna(row.value))
                fig = genre_trend(history, genre, (2000, 2009), (2020, 2024))
                self.assertFalse(fig.data[-1].connectgaps)
                self.assertIn('titres', fig.data[-1].hovertemplate)
                self.assertEqual(fig.layout.yaxis.range, (0, 100))

    def test_genre_missing_is_unavailable_known_absence_is_zero(self):
        d = self.data.iloc[:2].copy()
        d['genres'] = [['Non renseigné'], ['Non renseigné']]
        history = decades(d, genre='Rock', coverage=(1958, 2025))
        self.assertTrue(history.value.isna().all())
        missing = decades(d, genre='Non renseigné', coverage=(1958, 2025))
        self.assertEqual(missing.iloc[0].value, 100)
        known = d.copy()
        known['genres'] = [['Rock', 'Pop'], ['Pop']]
        frames = {'Période A': d, 'Référence B': known}
        compared = comparison_rows(genre_frame(frames), frames, ['Rock', 'Non renseigné'])
        self.assertTrue(pd.isna(compared.iloc[0]['A (%)']))
        self.assertTrue(pd.isna(compared.iloc[0]['B − A (points)']))
        self.assertEqual(compared.iloc[1]['A (%)'], 100)
        self.assertEqual(compared.iloc[0]['B (%)'], 50)
        d['genres'] = [['Pop'], ['Pop']]
        history = decades(d, genre='Rock', coverage=(1958, 2025))
        self.assertEqual(history.iloc[0].value, 0)
        empty = decades(d.iloc[:0], genre='Rock', coverage=(1958, 2025))
        self.assertTrue(empty.value.isna().all())

    def test_instrument_counts_denominators_deltas_and_missing(self):
        a, b = self.data.iloc[:4].copy(), self.data.iloc[:2].copy()
        a['guitar_based'], b['guitar_based'] = [1, 1, 0, float('nan')], [1, 0]
        a['bass_based'], b['bass_based'] = 1, 1
        frames = {'Période A': a, 'Référence B': b}
        columns = {'guitar_based': 'Guitare', 'bass_based': 'Basse'}
        data = binary_frame(frames, columns)
        table = comparison_rows(data, frames, ['Guitare', 'Basse'])
        self.assertEqual(table.iloc[0]['A (%)'], 50)
        self.assertEqual(table.iloc[0]['A · renseignés'], 3)
        self.assertEqual(table.iloc[0]['B − A (points)'], 0)
        self.assertGreater(data.part.sum(), 200)  # Les instruments se cumulent.
        fig = format_bars(data, frames, ['Guitare', 'Basse'])
        self.assertEqual(len(fig.data), 2)
        self.assertEqual(fig.data[0].customdata[0][0], 2)
        self.assertIn('Écart', fig.data[0].hovertemplate)
        a['guitar_based'] = float('nan')
        unavailable = comparison_rows(binary_frame(frames, columns), frames, ['Guitare'])
        self.assertTrue(pd.isna(unavailable.iloc[0]['A (%)']))
        self.assertTrue(pd.isna(unavailable.iloc[0]['B − A (points)']))

    def test_examples_use_filtered_rows_quartiles_and_stable_ties(self):
        data = select(self.data, (2020, 2024), 'Pop')
        rows = quartile_examples(data, 'intro_length_sec')
        self.assertEqual(len(rows), 3)
        self.assertEqual(len({r['index'] for r in rows}), 3)
        for row, q in zip(rows, [.25, .5, .75]):
            self.assertIn(row['index'], data.index)
            self.assertEqual(row['cible'], data.intro_length_sec.quantile(q))
            self.assertEqual(row['value'], data.loc[row['index'], 'intro_length_sec'])
        tied = data.iloc[:4].copy()
        tied['intro_length_sec'] = 7
        self.assertEqual(quartile_examples(tied, 'intro_length_sec'),
                         quartile_examples(tied.iloc[::-1], 'intro_length_sec'))
        self.assertEqual(len(quartile_examples(data.iloc[:1], 'intro_length_sec')), 1)
        self.assertEqual(quartile_examples(data.iloc[:0], 'intro_length_sec'), [])


class FormatJourneys(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)

    def clean(self):
        self.assertFalse(self.app.exception, [e.message for e in self.app.exception])

    def go(self, route):
        go_to(self.app, route)
        self.clean()

    def history_table(self):
        return next(t.value for t in self.app.dataframe if 'Période couverte' in t.value)

    def test_five_pages_order_questions_details_reading_and_charts(self):
        expected = ['Vue d’ensemble', 'Durée & introduction', 'Signature sonore', 'Instrumentation', 'Genres musicaux']
        for route, count in zip(FORMAT_ROUTES, [1, 3, 2, 2, 1]):
            self.go(route)
            self.assertEqual([b.label for b in self.app.button if b.key.startswith('nav_')], expected)
            self.assertTrue(self.app.title[0].value.endswith('?'))
            self.assertEqual(len(self.app.get('plotly_chart')), count)
            self.assertEqual(len([e for e in self.app.expander if e.label == 'Détails']), 1)
            self.assertIn('Comment lire', ' '.join(m.value for m in self.app.markdown))
            self.assertFalse(self.app.get('download_button'))

    def test_legacy_routes_and_memories_are_migrated(self):
        for old, new in [('intro', 'duration'), ('central', 'instrumentation'), ('presence', 'instrumentation')]:
            self.app.session_state['route'] = old
            self.app.session_state['last_routes'] = {'Format & son': old}
            self.app.run()
            self.clean()
            self.assertEqual(self.app.session_state['route'], new)
            self.assertEqual(self.app.session_state['last_routes']['Format & son'], new)
            self.go('summary')
            self.app.button(key='group_1').click().run()
            self.assertEqual(self.app.session_state['route'], new)
        self.app.session_state['route'] = 'obsolete_route'
        self.app.run()
        self.assertEqual(self.app.session_state['route'], 'summary')

    def test_summary_overview_exploration_and_data_shortcuts_preserve_filters(self):
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.selectbox(key='decade_a').set_value(1980).run()
        self.app.button(key='shortcut_format_trend').click().run()
        self.assertEqual(self.app.session_state['route'], 'format_trend')
        for target in FORMAT_ROUTES[1:]:
            self.go('format_trend')
            self.app.button(key='shortcut_' + target).click().run()
            self.clean()
            self.assertEqual(self.app.session_state['route'], target)
        for target in ['data_a', 'data_b']:
            self.go('duration')
            self.app.button(key='shortcut_' + target).click().run()
            self.clean()
            self.assertEqual(self.app.selectbox(key='genre').value, 'Pop')
            self.assertEqual(self.app.selectbox(key='decade_a').value, 1980)
            expected = select(prepare(), (1980, 1989) if target == 'data_a' else (2020, 2024), 'Pop')
            self.assertEqual(len(title_rows(self.app)) - 1, len(expected))

    def test_measure_choices_and_genre_modes_persist(self):
        for route, key, options in [('format_trend', 'evolution_metric', FORMAT_METRICS),
                                    ('duration', 'duration_metric', ['length_sec', 'intro_length_sec', 'intro_ratio']),
                                    ('sound', 'sonic', SOUND_HELP)]:
            self.go(route)
            for value in options:
                self.app.selectbox(key=key).set_value(value).run()
                self.clean()
            selected = self.app.selectbox(key=key).value
            self.go('summary')
            self.go(route)
            self.assertEqual(self.app.selectbox(key=key).value, selected)
        self.go('genres')
        self.app.radio(key='genres_view').set_value('Évolution historique').run()
        self.app.selectbox(key='genre_history').set_value('Rock').run()
        self.go('summary')
        self.go('genres')
        self.assertEqual(self.app.radio(key='genres_view').value, 'Évolution historique')
        self.assertEqual(self.app.selectbox(key='genre_history').value, 'Rock')

    def test_period_filters_change_comparison_but_not_history(self):
        self.go('duration')
        before = self.history_table().copy()
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1984, 1992)).run()
        self.app.slider(key='years_b').set_value((2020, 2020)).run()
        pd.testing.assert_frame_equal(before, self.history_table())
        spec = json.loads(self.app.get('plotly_chart')[0].proto.spec)
        boxes = [t for t in spec['data'] if t['type'] == 'box']
        for box, years in zip(boxes, [(1984, 1992), (2020, 2020)]):
            self.assertEqual(box['median'][0], select(prepare(), years).length_sec.median())
        self.app.selectbox(key='genre').set_value('Pop').run()
        expected = decades(select(prepare(), (1958, 2025), 'Pop'), column='length_sec', coverage=(1958, 2025))
        pd.testing.assert_series_equal(self.history_table()['Médiane / part (%)'], expected.value, check_names=False)

    def test_genre_modes_respect_global_filter_and_missing_category(self):
        self.go('genres')
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        self.assertIn('100 %', ' '.join(m.value for m in self.app.markdown))
        self.app.radio(key='genres_view').set_value('Évolution historique').run()
        self.app.selectbox(key='genre_history').set_value('Non renseigné').run()
        table = self.history_table()
        self.assertTrue(table['Médiane / part (%)'].dropna().eq(100).all())
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.selectbox(key='genre_history').set_value('Pop').run()
        self.assertTrue(self.history_table()['Médiane / part (%)'].dropna().eq(100).all())
        self.app.selectbox(key='genre_history').set_value('Rock').run()
        expected = decades(select(prepare(), (1958, 2025), 'Pop'), genre='Rock', coverage=(1958, 2025))
        self.assertEqual(self.history_table()['Titres concernés'].tolist(), expected['count'].tolist())

    def test_empty_identical_partial_periods_and_dynamic_comment(self):
        self.app.selectbox(key='decade_a').set_value(2010).run()
        self.go('duration')
        self.assertIn('10 à 11 s', ' '.join(m.value for m in self.app.markdown))
        self.app.selectbox(key='decade_a').set_value('recent').run()
        self.assertIn('médianes identiques', ' '.join(m.value for m in self.app.markdown))
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1958, 1959)).run()
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        for route in FORMAT_ROUTES:
            self.go(route)
        self.app.slider(key='years_b').set_value((1958, 1959)).run()
        for route in FORMAT_ROUTES:
            self.go(route)
        self.go('genres')
        self.app.radio(key='genres_view').set_value('Évolution historique').run()
        self.clean()
        self.app.selectbox(key='genre').set_value('Tous les genres').run()
        self.app.slider(key='years_b').set_value((2025, 2025)).run()
        for route in FORMAT_ROUTES:
            self.go(route)
        self.assertIn('2025', ' '.join(w.value for w in self.app.warning))

    def test_entirely_missing_measures_remain_unavailable(self):
        synthetic = prepare()
        columns = [*FORMAT_METRICS, 'vocally_based', 'guitar_based', 'piano_keyboard_based',
                   'bass_based', 'orchestral_strings', 'horns_winds']
        synthetic[columns] = float('nan')
        st.cache_data.clear()
        try:
            with patch('analysis.prepare', return_value=synthetic):
                self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
                for route in FORMAT_ROUTES[:-1]:
                    self.go(route)
                    self.assertIn('Non disponible', ' '.join(m.value for m in self.app.markdown)
                                  + ' '.join(str(t.value) for t in self.app.dataframe))
        finally:
            st.cache_data.clear()


if __name__ == '__main__':
    unittest.main()
