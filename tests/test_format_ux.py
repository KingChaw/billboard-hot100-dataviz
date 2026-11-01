"""Contrats UX Format & son, sans modifier les conventions statistiques."""
import json
import re
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

from analysis import prepare, select
from dashboard_data import FORMAT_METRICS, SOUND_HELP
from test_regression import ROOT, FORMAT_ROUTES, go_to, title_rows


class CompactFormat(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)

    def go(self, route):
        go_to(self.app, route)
        self.clean()

    def clean(self):
        self.assertFalse(self.app.exception, [e.message for e in self.app.exception])

    def text(self):
        return ' '.join(x.value for x in [*self.app.markdown, *self.app.caption, *self.app.info, *self.app.warning]
                        if not x.value.lstrip().startswith('<style>'))

    def compact(self):
        self.clean()
        self.assertEqual(len(self.app.get('plotly_chart')), 1)
        visible = self.text()
        for x in [*self.app.radio, *self.app.selectbox, *self.app.slider]:
            visible += ' ' + x.label + ' ' + str(getattr(x, 'options', ''))
        for table in self.app.dataframe:
            visible += ' ' + str(table.value.columns.tolist())
        for chart in self.app.get('plotly_chart'):
            spec = json.loads(chart.proto.spec)
            for trace in spec['data']:
                visible += ' ' + str({k: trace.get(k) for k in ['name', 'hovertemplate', 'texttemplate']})
            for axis in ['xaxis', 'yaxis']:
                visible += ' ' + str(spec['layout'].get(axis, {}).get('title', ''))
        self.assertNotRegex(visible, r'(?i)écart|période|\bn\s*=')

    def test_defaults_and_every_graph_remain_accessible(self):
        for route in FORMAT_ROUTES:
            self.go(route)
            self.compact()
        self.go('duration')
        for view in ['Durée', 'Introduction', 'Évolution']:
            self.app.radio(key='duration_view').set_value(view).run()
            self.compact()
            if view == 'Évolution':
                for metric in ['length_sec', 'intro_length_sec', 'intro_ratio']:
                    self.app.selectbox(key='duration_metric').set_value(metric).run()
                    self.compact()
                    table = next(t.value for t in self.app.dataframe if 'Médiane' in t.value)
                    for actual, years in zip(table['Médiane'], [(2000, 2009), (2020, 2024)]):
                        self.assertEqual(actual, select(prepare(), years)[metric].median())
        self.go('sound')
        for metric in SOUND_HELP:
            self.app.selectbox(key='sonic').set_value(metric).run()
            for view in ['Distribution', 'Évolution']:
                self.app.radio(key='sound_view').set_value(view).run()
                self.compact()
        self.go('instrumentation')
        for view, count in [('Rôle central', 4), ('Présence', 2)]:
            self.app.radio(key='instrument_view').set_value(view).run()
            self.compact()
            spec = json.loads(self.app.get('plotly_chart')[0].proto.spec)
            self.assertEqual(len(spec['layout']['yaxis']['categoryarray']), count)
        self.go('genres')
        self.app.radio(key='genres_view').set_value('Évolution historique').run()
        self.app.selectbox(key='genre_history').set_value('Rock').run()
        self.compact()

    def test_new_modes_and_measures_persist(self):
        choices=[('duration','duration_view','Évolution'),('sound','sound_view','Évolution'),
                 ('instrumentation','instrument_view','Présence')]
        for route,key,value in choices:
            self.go(route);self.app.radio(key=key).set_value(value).run()
        self.go('duration');self.app.selectbox(key='duration_metric').set_value('intro_ratio').run()
        self.go('sound');self.app.selectbox(key='sonic').set_value('loudness_d_b').run()
        self.go('summary')
        for route,key,value in choices:
            self.go(route);self.assertEqual(self.app.radio(key=key).value,value)
        self.go('duration');self.assertEqual(self.app.selectbox(key='duration_metric').value,'intro_ratio')
        self.go('sound');self.assertEqual(self.app.selectbox(key='sonic').value,'loudness_d_b')

    def test_year_wording_preserves_filters_between_sections(self):
        self.go('duration')
        self.assertEqual(self.app.selectbox(key='decade_a').label,'Année étudiée')
        self.app.selectbox(key='decade_a').set_value(1980).run()
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1984,1992)).run()
        self.go('map')
        self.assertEqual(self.app.slider(key='years_a').label,'Période étudiée')
        self.assertEqual(self.app.slider(key='years_a').value,(1984,1992))
        self.go('sound')
        self.assertEqual(self.app.slider(key='years_a').label,'Année étudiée')
        self.assertEqual(self.app.slider(key='years_a').value,(1984,1992))
        self.assertEqual(self.app.selectbox(key='genre').value,'Pop')
        self.app.radio(key='mode').set_value('Décennies').run()
        self.assertEqual(self.app.selectbox(key='decade_a').value,1980)

    def test_other_sections_keep_original_origins_and_deltas(self):
        self.go('origins')
        self.assertEqual(self.app.radio(key='origins_view').options,['Évolution','Composition'])
        self.assertEqual([b.label for b in self.app.button if b.key.startswith('nav_')],
                         ['Composition et évolution','Pays et territoires'])
        self.assertIn('Ce qui compte',self.text())
        self.go('map');self.app.selectbox(key='map_country').set_value('Porto Rico').run()
        self.assertIn('Écart',self.text())
        self.assertEqual(self.app.selectbox(key='decade_a').label,'Période étudiée')
        self.go('ages');self.assertIn('Une boîte plus haute',self.text())
        self.assertIn('Comment lire la boîte',self.text())

    def test_details_keep_values_examples_and_data_exports(self):
        self.go('duration');self.app.radio(key='duration_view').set_value('Introduction').run()
        self.app.radio(key='format_examples_period').set_value('Référence B').run()
        text=self.text()
        for title in ['cardigan','Life Goes On','Like That']:
            self.assertIn(title,text)
        self.assertNotIn('Écart',text)
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.selectbox(key='decade_a').set_value(1980).run()
        self.app.button(key='shortcut_data_b').click().run()
        self.clean()
        self.assertEqual(len(title_rows(self.app))-1,len(select(prepare(),(2020,2024),'Pop')))
        self.assertTrue(self.app.get('download_button'))
        self.assertEqual(self.app.selectbox(key='decade_a').value,1980)

    def test_all_modes_with_empty_and_entirely_missing_values(self):
        self.go('duration');self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_a').set_value((1958,1959)).run()
        self.app.slider(key='years_b').set_value((1958,1959)).run()
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        for route,key,values in [('duration','duration_view',['Durée','Introduction','Évolution']),
                                 ('sound','sound_view',['Distribution','Évolution']),
                                 ('instrumentation','instrument_view',['Rôle central','Présence']),
                                 ('genres','genres_view',['Comparaison des périodes','Évolution historique'])]:
            self.go(route)
            for value in values:
                self.app.radio(key=key).set_value(value).run();self.clean()
                self.assertLessEqual(len(self.app.get('plotly_chart')),1)
                self.assertTrue(self.app.info)
        missing=prepare();missing[list(FORMAT_METRICS)]=float('nan')
        st.cache_data.clear()
        try:
            with patch('analysis.prepare',return_value=missing):
                self.app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
                for route,key in [('duration','duration_view'),('sound','sound_view')]:
                    self.go(route)
                    for view in self.app.radio(key=key).options:
                        self.app.radio(key=key).set_value(view).run();self.clean()
                        self.assertIn('Non disponible',self.text())
                        self.assertEqual(len(self.app.get('plotly_chart')),1)
        finally:
            st.cache_data.clear()


if __name__=='__main__':unittest.main()
