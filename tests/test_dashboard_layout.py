"""Parcours de la navigation et libellés des sélections, sans modifier les calculs."""
import io
import json
import re
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

from periods import date_label, period_labels, display_comparison
from test_regression import ROOT, ROUTES, go_to


class DashboardLayout(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)

    def test_sidebar_filters_and_remembered_subpage(self):
        self.assertFalse(self.app.sidebar.button)
        self.assertEqual([s.label for s in self.app.sidebar.selectbox],
                         ['Période étudiée', 'Période de référence', 'Genre Discogs'])
        self.app.selectbox(key='genre').set_value('Pop').run()
        go_to(self.app, 'intro')
        self.app.button(key='group_2').click().run()
        self.assertEqual(self.app.session_state['route'], 'origin_trend')
        self.app.button(key='group_1').click().run()
        self.assertEqual(self.app.session_state['route'], 'intro')
        self.assertEqual(self.app.selectbox(key='genre').value, 'Pop')
        self.assertEqual([b.key for b in self.app.button if b.key.startswith('nav_')],
                         ['nav_' + r for r in ROUTES[:7]])

    def test_dates_on_all_pages_and_comparison_tables(self):
        self.app.selectbox(key='decade_a').set_value(2010).run()
        forbidden = re.compile(r'Période A|Référence B|A/B|B − A|\ben A\b|\ben B\b|\bA et B\b')
        for route in ['summary', *ROUTES, 'data_a', 'data_b']:
            with self.subTest(route=route):
                go_to(self.app, route)
                self.assertFalse(self.app.exception)
                visible = ' '.join(x.value for x in self.app.markdown)
                self.assertIsNone(forbidden.search(visible))
                for widget in [*self.app.radio, *self.app.selectbox]:
                    self.assertIsNone(forbidden.search(widget.label))
                    self.assertIsNone(forbidden.search(str(widget.options)))
                for table in self.app.dataframe:
                    self.assertIsNone(forbidden.search(str(table.value.columns.tolist())))
                    self.assertNotIn('− A', str(table.value.columns.tolist()))
                    if 'Période' in table.value:
                        self.assertIsNone(forbidden.search(str(table.value['Période'].tolist())))
                for chart in self.app.get('plotly_chart'):
                    spec = json.loads(chart.proto.spec)
                    for trace in spec['data']:
                        for field in ('name', 'hovertemplate', 'text'):
                            self.assertIsNone(forbidden.search(str(trace.get(field, ''))))
                    for axis in ('xaxis', 'yaxis'):
                        self.assertIsNone(forbidden.search(str(spec['layout'].get(axis, {}).get('ticktext', ''))))
        self.assertEqual(self.app.button(key='nav_data_a').label, '2010 – 2019')
        self.assertEqual(self.app.button(key='nav_data_b').label, '2020 – 2024')

    def test_identical_periods_keep_two_series_and_two_data_pages(self):
        self.app.selectbox(key='decade_a').set_value('recent').run()
        go_to(self.app, 'intro')
        spec = json.loads(self.app.get('plotly_chart')[0].proto.spec)
        boxes = [trace for trace in spec['data'] if trace['type'] == 'box']
        self.assertEqual(len(boxes), 2)
        self.assertEqual([t['name'] for t in boxes],
                         ['2020 – 2024 · étudiée', '2020 – 2024 · référence'])
        self.assertEqual(boxes[0]['median'], boxes[1]['median'])
        go_to(self.app, 'origins')
        spec = json.loads(self.app.get('plotly_chart')[0].proto.spec)
        self.assertEqual(len(spec['layout']['yaxis']['ticktext']), 2)
        self.assertEqual(spec['data'][0]['customdata'][0][2], '2020 – 2024 · étudiée')
        go_to(self.app, 'data_b')
        self.assertNotEqual(self.app.button(key='nav_data_a').label,
                            self.app.button(key='nav_data_b').label)

    def test_selected_bounds_survive_empty_filter_and_csv_uses_dates(self):
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1958, 1959)).run()
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        with patch('streamlit.download_button', wraps=st.download_button) as download:
            go_to(self.app, 'data_a')
            filename = download.call_args.args[2]
            exported = pd.read_csv(io.BytesIO(download.call_args.args[1]))
        self.assertTrue(exported.empty)
        self.assertEqual(filename, 'billboard_1958_1959.csv')
        self.assertEqual(self.app.button(key='nav_data_a').label, '1958 – 1959')
        self.assertIn('1958 – 1959', self.app.title[0].value)

    def test_partial_dates_and_empty_period_identity(self):
        self.assertEqual(date_label((2020, 2025)), '2020 – janv. 2025')
        self.assertEqual(date_label((2025, 2025)), 'janv. 2025')
        frames = {key: pd.DataFrame() for key in ['Période A', 'Référence B']}
        for frame in frames.values():
            frame.attrs['period_years'] = (1958, 1959)
        labels = period_labels(frames)
        self.assertEqual(len(set(labels.values())), 2)
        self.assertTrue(all('1958 – 1959' in text for text in labels.values()))
        table = pd.DataFrame({'A (%)': [20], 'B (%)': [25], 'B − A (points)': [5]})
        shown = display_comparison(table, frames)
        self.assertEqual(shown.columns[-1],
                         'Écart (points) · 1958 – 1959 · référence − 1958 – 1959 · étudiée')
        self.assertEqual(shown.iloc[0, -1], 5)
        self.assertEqual(table.columns[-1], 'B − A (points)')


if __name__ == '__main__':
    unittest.main()
