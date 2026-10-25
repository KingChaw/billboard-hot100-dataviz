"""Contrôles ciblés des corrections de l’itération de septembre 2026."""
import io
import math
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

from analysis import binary_shares, credits, origin_group, prepare, select
from collaboration_rules import qualify_credits
from dashboard_data import CREDITS, REUSE, comparison_rows, decades, overlap_message, ranked_categories
from charts import binary_frame, share_frame, stacked, trend, distribution
from ui import metric_message, selection_table
from test_regression import go_to, ROOT, ROUTES, title_rows, TableParser


class Corrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = prepare()

    def test_collaboration_review_and_incomplete_evidence(self):
        d = self.df
        simon = d[d.artist.str.strip().eq('Simon & Garfunkel')]
        self.assertEqual(len(simon), 3)
        self.assertTrue(simon.artist_format.eq('Duo').all())
        self.assertTrue(simon.collaboration_credit.eq(False).all())
        for artist in ['KC & the Sunshine Band', 'Diana Ross & The Supremes']:
            rows = d[d.artist.str.strip().eq(artist)]
            self.assertGreater(len(rows), 0)
            self.assertTrue(rows.collaboration_credit.eq(False).all())
        for title in ['My Universe', 'Party Rock Anthem', 'Moves Like Jagger']:
            self.assertTrue(d[d.song.str.strip().eq(title)].collaboration_credit.all())
        synthetic = pd.DataFrame({'artist': ['Band & Unknown', None, 'Simon & Garfunkel ft. Guest', 'A ft. B']})
        result = qualify_credits(synthetic)
        self.assertTrue(pd.isna(result.iloc[0].collaboration_credit))
        self.assertTrue(pd.isna(result.iloc[1].collaboration_credit))
        self.assertTrue(result.iloc[2].collaboration_credit)
        self.assertTrue(result.iloc[3].collaboration_credit)
        # Un instrumentiste invité ne doit jamais suffire à établir un co-crédit.
        shallow = d[d.song.str.strip().eq('Shallow')].iloc[0]
        self.assertIn('Guitar', shallow.featured_artists)
        self.assertFalse(shallow.collaboration_status.startswith('Mention explicite'))

    def test_reference_coverage_and_nonmonotonic_values(self):
        self.assertEqual(len(self.df), 1177)
        self.assertEqual(len(pd.read_csv(ROOT / 'data/topics.csv')), 97)
        self.assertEqual(self.df.date.min().strftime('%Y-%m-%d'), '1958-08-04')
        self.assertEqual(self.df.date.max().strftime('%Y-%m-%d'), '2025-01-11')
        for years, median in [((1958,1969),161.5),((1990,1999),250),((2010,2019),223),((2020,2024),200)]:
            self.assertEqual(select(self.df, years).length_sec.median(), median)
        a, b = select(self.df, (2010,2019)), select(self.df, (2020,2024))
        self.assertEqual((a.intro_length_sec.median(), b.intro_length_sec.median()), (10,11))
        self.assertEqual((len(b), b.discogs_genre.isna().sum()), (81,16))
        self.assertEqual(len(select(self.df, (2025,2025))), 1)
        self.assertEqual(select(self.df,(1958,1969)).foreign_language.sum(),3)
        self.assertEqual(b.foreign_language.sum(),4)
        self.assertTrue(b.cdr_genre.isna().all())

    def test_empty_period_keeps_columns_after_genre_filter(self):
        empty = select(self.df, (2026, 2026), 'Pop')
        self.assertTrue(empty.empty)
        self.assertIn('date', empty.columns)
        self.assertEqual(empty.columns.tolist(), self.df.columns.tolist())

    def test_missing_zero_and_denominator(self):
        d = pd.DataFrame({'sample':[1, 0, float('nan')]})
        shares = binary_shares(d,['sample'],{'sample':'Sample'}).iloc[0]
        self.assertEqual(shares['renseignés'],2)
        self.assertAlmostEqual(shares.part,100/3)
        self.assertTrue(math.isnan(binary_shares(d.iloc[:0],['sample'],{'sample':'Sample'}).iloc[0].part))
        self.assertTrue(math.isnan(binary_shares(d.iloc[2:],['sample'],{'sample':'Sample'}).iloc[0].part))
        self.assertEqual(binary_shares(d.iloc[1:2],['sample'],{'sample':'Sample'}).iloc[0].part,0)
        self.assertEqual(credits('A; a ;B;Unknown'), 2)
        self.assertTrue(pd.isna(credits('Unknown')))

    def test_equal_period_weights_and_empty_period(self):
        # Le décompte cumulé placerait X (90) devant Y (10), les parts équilibrées font l’inverse.
        rows = [{'catégorie':'X','période':'A','part':90,'effectif':90},
                {'catégorie':'Y','période':'A','part':10,'effectif':10},
                {'catégorie':'Y','période':'B','part':100,'effectif':1}]
        data = pd.DataFrame(rows)
        self.assertEqual(ranked_categories(data,1),['Y','Non renseigné'])
        self.assertEqual(ranked_categories(data[data['période'].eq('A')],1),['X','Non renseigné'])
        self.assertEqual(ranked_categories(data.iloc[:0]), ['Non renseigné'])
        swapped = data.assign(période=data['période'].map({'A':'B','B':'A'}))
        self.assertEqual(ranked_categories(data),ranked_categories(swapped))

    def test_temporal_credits_reuse_gaps_and_partial_labels(self):
        for genre in ['Tous les genres','Pop','Non renseigné']:
            d = select(self.df,(1958,2025),genre)
            for col in CREDITS:
                result = decades(d,column=col,coverage=(1958,2025))
                self.assertEqual(result.iloc[0].label,'1958–1959')
                self.assertEqual(result.iloc[-1].label,'2020–janv. 2025')
                for row in result.itertuples():
                    values = select(d,(row.start,row.end))[col].dropna()
                    self.assertEqual(row.valid,len(values))
                    if len(values):
                        self.assertEqual(row.value,values.median())
                        self.assertEqual(row.q1,values.quantile(.25))
                        self.assertEqual(row.q3,values.quantile(.75))
                    else:
                        self.assertTrue(pd.isna(row.value))
            for col in REUSE:
                result = decades(d,binary=col,coverage=(1958,2025))
                for row in result.itertuples():
                    data = select(d,(row.start,row.end))
                    self.assertEqual(row.total,len(data))
                    self.assertEqual(row.valid,data[col].count())
                    if row.valid:
                        self.assertAlmostEqual(row.value,100*data[col].eq(1).sum()/len(data))
        d = self.df.copy()
        d.loc[d.year.between(1980,1989),'length_sec'] = float('nan')
        result = decades(d,column='length_sec')
        fig = trend(result,'s',(1984,1992),(2020,2024))
        self.assertFalse(fig.data[-1].connectgaps)
        for trace in fig.data[:-1]:
            xs = list(trace.x)
            self.assertFalse(min(xs) < 1984.5 < max(xs))
        self.assertFalse(fig.layout.shapes)  # Pas d’aplats pouvant assimiler A/B aux décennies.
        restricted = decades(self.df,column='length_sec',coverage=(1965,1974))
        self.assertEqual(restricted.total.sum(),len(select(self.df,(1965,1974))))

    def test_absolute_points_unavailable_and_neutral_messages(self):
        a=self.df.iloc[:5].copy(); b=self.df.iloc[:4].copy()
        a['sample']=[1,0,0,0,0]; b['sample']=[1,0,0,0]
        frames={'Période A':a,'Référence B':b}
        data=binary_frame(frames,{'sample':'Sample'})
        self.assertEqual(comparison_rows(data,frames,['Sample']).iloc[0]['B − A (points)'],5)
        frames['Période A']=a.iloc[:0]
        data=binary_frame(frames,{'sample':'Sample'})
        self.assertTrue(pd.isna(comparison_rows(data,frames,['Sample']).iloc[0]['B − A (points)']))
        frames={'Période A':a,'Référence B':a}
        self.assertIn('identiques',metric_message(frames,'length_sec','Durée','s'))
        frames['Référence B']=a.iloc[:0]
        self.assertIn('indisponible',metric_message(frames,'length_sec','Durée','s'))
        self.assertIsNone(overlap_message((2010,2019),(2020,2024)))
        self.assertIn('identiques',overlap_message((2020,2024),(2020,2024)))
        self.assertIn('chevauchent',overlap_message((2015,2022),(2020,2024)))

    def test_origins_and_representative_titles(self):
        self.assertEqual(origin_group(['United States','Puerto Rico']),'États-Unis uniquement (dont Porto Rico)')
        self.assertEqual(origin_group(['France','Germany']),'Hors États-Unis uniquement')
        self.assertEqual(origin_group(['Colombia','United States']),'Mixte États-Unis / autres')
        bruno=self.df[self.df.song.str.strip().eq("We Don't Talk About Bruno")].iloc[0]
        self.assertEqual(bruno.origins,['Colombia','United States'])
        self.assertIn('Columbia',bruno.artist_place_of_origin)  # Export brut inchangé.

    def test_displayed_box_quartiles_match_calculated_values(self):
        frames={'Période A':select(self.df,(2010,2019)), 'Référence B':select(self.df,(2020,2024))}
        fig=distribution(frames,'intro_length_sec','s',points=False)
        boxes=[trace for trace in fig.data if trace.type=='box']
        self.assertEqual(len(boxes),2)
        self.assertEqual(boxes[0].q1[0],6.75)
        self.assertEqual(boxes[1].q1[0],7)
        self.assertEqual(boxes[1].median[0],11)
        self.assertEqual(boxes[1].q3[0],18)


class NewJourneys(unittest.TestCase):
    def setUp(self):
        self.app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    def go(self,route):
        go_to(self.app, route)
        self.assertFalse(self.app.exception,[e.message for e in self.app.exception])

    def test_country_comparisons_small_territory_and_empty_b(self):
        self.go('map')
        self.app.radio(key='country_view').set_value('Comparaison des périodes').run()
        self.app.selectbox(key='map_country').set_value('Porto Rico').run()
        self.assertFalse(self.app.exception)
        self.assertIn('Porto Rico',' '.join(c.value for c in self.app.caption))
        self.go('intro'); self.go('map')
        self.assertEqual(self.app.radio(key='country_view').value,'Comparaison des périodes')
        self.assertEqual(self.app.selectbox(key='map_country').value,'Porto Rico')
        self.app.radio(key='mode').set_value('Intervalles d’années').run()
        self.app.slider(key='years_b').set_value((1958,1959)).run()
        self.app.selectbox(key='genre').set_value('Non renseigné').run()
        self.assertFalse(self.app.exception, [e.message for e in self.app.exception])
        self.app.slider(key='years_a').set_value((2020,2024)).run()
        for route in ROUTES:
            self.go(route)

    def test_added_modes_and_persistent_indicators(self):
        for route, key in [('teams','teams_view'),('ages','ages_view')]:
            self.go(route)
            self.app.radio(key=key).set_value('Évolution par décennie').run()
            self.assertFalse(self.app.exception)
            self.go('summary'); self.go(route)
            self.assertEqual(self.app.radio(key=key).value,'Évolution par décennie')
        for route in ['origins']:
            self.go(route)
            self.app.radio(key='composition_'+route).set_value('Comparaison des périodes').run()
            self.assertFalse(self.app.exception)

    def test_ar_scenario_context_csv_and_overlap_warning(self):
        self.app.selectbox(key='decade_a').set_value(2010).run()
        self.go('intro')
        text=' '.join(x.value for x in self.app.markdown)
        self.assertIn('10 à 11 s',text)
        self.go('data_b')
        with patch('streamlit.download_button',wraps=st.download_button) as download:
            self.app.text_input(key='search_data_b').input('cardigan').run()
            raw=download.call_args.args[1]
        csv=pd.read_csv(io.BytesIO(raw))
        self.assertEqual(csv['Titre'].str.strip().tolist(),['cardigan'])
        self.assertEqual(title_rows(self.app)[1:],csv.astype(object).where(csv.notna(), 'Non disponible').astype(str).values.tolist())
        self.app.selectbox(key='decade_a').set_value('recent').run()
        self.assertIn('identiques',' '.join(x.value for x in self.app.warning))
        self.app.selectbox(key='decade_b').set_value(2020).run()
        self.assertIn('2025',' '.join(x.value for x in self.app.warning))
        self.assertIn('chevauchent',' '.join(x.value for x in self.app.warning))

if __name__=='__main__':
    unittest.main()
