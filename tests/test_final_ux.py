"""Contrats de finalisation : accueil, navigation commune et notes historiques."""
import unittest
from streamlit.testing.v1 import AppTest
from test_regression import ROOT, go_to


class FinalDashboardUX(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)

    def test_home_keeps_three_complete_journeys_only(self):
        self.assertEqual(self.app.title[0].value, 'Quels repères offrent les titres n°1 ?')
        self.assertEqual(len(self.app.subheader), 5)  # Trois parties + les deux en-têtes de filtres.
        journeys = [x.value for x in self.app.markdown if 'class="journey"' in x.value]
        self.assertEqual(len(journeys), 3)
        self.assertEqual([j.count('<li>') for j in journeys], [5, 2, 4])
        self.assertIn('Genres musicaux', journeys[0])
        self.assertIn('Pays et territoires', journeys[1])
        self.assertIn('Samples et reprises', journeys[2])
        self.assertFalse(self.app.get('plotly_chart'))
        self.assertFalse(self.app.expander)
        self.assertFalse([b for b in self.app.button if b.key.startswith(('nav_', 'shortcut_'))])
        visible = ' '.join(x.value for x in self.app.markdown)
        for removed in ['Repères chiffrés', 'ancienne synthèse', 'Trois lectures pour situer', 'Écart :']:
            self.assertNotIn(removed, visible)

    def test_primary_name_and_home_route_preserve_other_navigation(self):
        self.assertEqual([b.label for b in self.app.button if b.key.startswith('group_')],
                         ['Explorer les n°1', 'Format & son', 'Origines des artistes', 'Profils et création', 'Données'])
        self.app.selectbox(key='genre').set_value('Pop').run()
        self.app.selectbox(key='decade_a').set_value(1980).run()
        go_to(self.app, 'genres')
        self.assertEqual(self.app.button(key='nav_format_trend').label, 'Vue d’ensemble')
        self.app.button(key='group_0').click().run()
        self.assertEqual(self.app.session_state['route'], 'summary')
        self.assertFalse([b for b in self.app.button if b.key.startswith('nav_')])
        self.app.button(key='group_1').click().run()
        self.assertEqual(self.app.session_state['route'], 'genres')
        self.assertEqual(self.app.selectbox(key='genre').value, 'Pop')
        self.assertEqual(self.app.selectbox(key='decade_a').value, 1980)
        self.assertFalse(self.app.exception)

    def test_repeated_history_explanation_is_absent_in_all_history_modes(self):
        for route, key, view in [('format_trend', None, None), ('duration', 'duration_view', 'Évolution'),
                                  ('sound', 'sound_view', 'Évolution'), ('genres', 'genres_view', 'Évolution historique'),
                                  ('origins', 'origins_view', 'Évolution'), ('ages', 'ages_view', 'Évolution par décennie'),
                                  ('teams', 'teams_view', 'Évolution par décennie')]:
            go_to(self.app, route)
            if key:
                self.app.radio(key=key).set_value(view).run()
            self.assertFalse(self.app.exception)
            text = ' '.join(x.value for x in [*self.app.markdown, *self.app.caption])
            self.assertNotRegex(text, r'Historique\s*:\s*1958|indépendant des années comparées|Courbe : périodes indiquées|Les années comparées ne bornent pas cet historique')
            self.assertEqual(len(self.app.get('plotly_chart')), 1)
            tables = [t.value for t in self.app.dataframe if 'Partielle' in t.value]
            self.assertTrue(tables)
            for table in tables:
                self.assertEqual(int(table['Partielle'].sum()), 2)


if __name__ == '__main__':
    unittest.main()
