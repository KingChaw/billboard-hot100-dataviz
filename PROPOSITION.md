# Proposition initiale · Billboard Hot 100 n°1

## 1. Diagnostic des données

Les fichiers fournis contiennent **1 177 lignes × 105 colonnes** dans `billboard.csv` et **97 thèmes** dans `topics.csv` (une colonne). Les deux fichiers sont livrés dans `data/`. Les 1 177 lignes correspondent à des couples `song`–`artist` distincts, sans doublon exact ; les dates vont du **4 août 1958 au 11 janvier 2025**, sans date manquante. La période de référence **2020–2024 compte 81 titres** ; **2025 compte un seul titre**. La première année, 1958, est aussi partielle. La liste de thèmes ne répond pas aux trois questions choisies et ne sert donc pas aux calculs du prototype.

Le [README et dictionnaire TidyTuesday officiels](https://github.com/rfordatascience/tidytuesday/blob/main/data/2025/2025-08-26/readme.md) ont été consultés pour définir l'unité, les indicateurs et les crédits. Les colonnes nécessaires existent. Le CSV précise les modalités observées de `artist_structure` : 0, 0,5, 1, 1,5, 2 et 2,5. Les variantes +0,5 portent l'indication d'au moins un invité ; elles ne transforment pas le format groupe/solo/duo. Le fichier ne présente **aucun doublon exact** ni de doublon sur `song` + `artist`.

Nettoyages appliqués : date interprétée comme première semaine au n°1 ; colonnes quantitatives converties en numérique ; valeurs manquantes préservées ; listes de genres/origines/crédits séparées sur `;`, espaces normalisés et catégories dédupliquées dans un titre ; `Funk / Soul` fusionné avec `Funk/Soul`. Deux libellés d'origine corrigés : `Unites States` → `United States` et `Columbia` → `Colombia` (**inférence de correction à vérifier sur la ligne**). `Puerto Rico` reste visible comme territoire propre dans le tableau des origines ; pour la partition exclusive, il est rangé du côté américain en tant que territoire des États-Unis. Cette convention est révisable.

Sur les 81 titres de 2020–2024, `cdr_genre` manque sur **81/81**, contre **16/81** pour `discogs_genre`. La catégorie `Non renseigné` est maintenue pour ce dernier, même dans les graphiques de genres. Filtrer un genre nommé exclut ces 16 titres du sous-ensemble : le filtre le signale. Sur la base entière, `front_person_age` manque pour **22/1 177**, `bpm`, `energy`, `danceability`, `loudness_d_b` et `acousticness` chacun pour **2/1 177** ; les durées et intros sont complètes. Après exclusion de `Unknown` dans les crédits, les tailles d'équipe ne sont pas calculables pour **2** lignes d'auteurs tous crédits, **3** lignes hors samples/interpolations et **4** lignes de producteurs.

Des limites du dictionnaire sont maintenues : `artist_place_of_origin` indique des pays de naissance, pas les nationalités ni la géographie de commercialisation ; `front_person_age` est l'âge du frontperson ou chef de groupe (moyenne possible), pas l'âge individuel de tous les interprètes ; `featured_artists` peut inclure des instrumentistes. Le fichier ne couvre que les titres arrivés au n°1 : aucune comparaison avec des titres non classés ne permet de conclure à une cause du succès.

## 2. Architecture et filtres

La barre latérale propose deux périodes A/B, chacune en **intervalle d'années** ou en **décennie**, et un **filtre de genre Discogs commun**. Par défaut A = 1958–1969 (226 titres), B = 2020–2024 (81). Les effectifs se mettent à jour. Une alerte apparaît pour les sous-ensembles vides, inférieurs à dix titres, ou contenant 2025 ; l'utilisateur peut choisir deux plages qui se recouvrent, mais elles ne sont alors pas indépendantes. La première année 1958 est signalée comme partielle.

1. **Format et son :** repères immédiats de durée/intro, distributions, caractéristique sonore choisie, instrumentation et genres. Les unités et les effectifs exploitables sont affichés.
2. **Origines :** partition États-Unis/mixte/hors États-Unis, pays/territoires associés, puis indicateur complémentaire de paroles non anglaises et tableau croisé accessible.
3. **Artistes et création :** âge et format, distinction entre invités répertoriés et plusieurs artistes au crédit, taille des équipes et réutilisation ; classement par crédit et âge/genre en exploration secondaire.

Chaque page donne accès aux titres filtrés et à un export CSV. Les notes méthodologiques sont repliables. Un agent IA futur recevrait des résultats déjà calculés et la liste filtrée pour rédiger un commentaire contrôlable ; **aucun agent n'est nécessaire au fonctionnement**.

## 3. Tableau de choix des visualisations

Toutes les parts ci-dessous ont pour dénominateur le **nombre total de titres filtrés de la période**, sauf si une valeur est explicitement annoncée comme un nombre de valeurs exploitables. Les titres sont comptés une fois, sans poids des semaines au n°1. Les catégories multiples peuvent donner une somme supérieure à 100 %.

| Question et tâche | Variables et calcul | Encodage et interaction | Utilité A&R et justification |
|---|---|---|---|
| Q1 · comparer niveau et dispersion de durée et d'intro | `length_sec`, `intro_length_sec` ; médiane et boîte sur valeurs connues, n indiqué | Deux repères A/B, boîtes groupées, survol des quartiles | Situer un format envisagé ; les boîtes exposent la diversité que masquerait une moyenne. |
| Q1 · examiner un attribut sonore | `bpm`, `energy`, `danceability`, `acousticness`, `loudness_d_b` ; distributions séparées, n | Sélecteur d'indicateur et boîte A/B ; unités conservées | Évite de comparer sur une même échelle des BPM, dB et indices 0–100. |
| Q1 · comparer l'instrumentation | `guitar_based`, `piano_keyboard_based`, `vocally_based`, `bass_based` ; taux de 1 ; séparément `orchestral_strings`, `horns_winds` | Deux panneaux de barres horizontales groupées A/B, dans une section repliable | Distinction entre rôle central et simple présence ; plusieurs indicateurs peuvent valoir 1 par titre. |
| Q1 · comparer les genres représentés | `discogs_genre` ; compte une fois par titre et genre, y compris « Non renseigné », / tous les titres | Barres A/B, principales catégories, même filtre pour les deux périodes | Situer les étiquettes Discogs ; barres adaptées aux comparaisons de catégories et limite de couverture visible. |
| Q2 · examiner la composition États-Unis/international | `artist_place_of_origin` ; 3 classes exclusives après corrections et convention Porto Rico | Barres groupées A/B, effectifs au survol | Permet de comparer une partition dont les parts s'additionnent à 100 %, avec une convention explicitée. |
| Q2 · comparer les pays/territoires associés | listes d'origines ; titres par pays / tous les titres, top 9 de l'ensemble A+B | Barres horizontales groupées A/B, effectifs au survol | Présente les origines combinées sans forcer une affectation unique trompeuse. |
| Q2 · compléter par la langue | `foreign_language=1` / tous les titres ; tableau origine × indicateur avec effectifs | Barre A/B, détail replié | Distingue présence de paroles non anglaises et lieu de naissance ; très petits effectifs signalés. |
| Q3 · observer l'âge du frontperson | `front_person_age` ; distribution des âges renseignés par titre, n | Boîtes A/B avec points extrêmes | Fait voir médiane et dispersion sans assimiler une moyenne de groupe à un âge individuel. |
| Q3 · comparer les formats et collaborations | `artist_structure` → groupe/solo/duo ; +0,5 → invité ; chaîne `artist` → indicateur distinct de plusieurs crédits | Barres A/B, puis deux barres pour les indicateurs non exclusifs | Sépare format et invités ; la détection de crédits est une approximation et ne mesure pas un featuring commercial. |
| Q3 · comparer les équipes | listes `songwriters`, variante sans crédits de sample/interpolation, `producers` ; nombre de noms distincts par titre, `Unknown` manquant | Sélecteur du type de crédit et boîtes A/B ; n | Compare la taille et la variabilité des équipes, sans confondre crédit total et équipe de création originale. |
| Q3 · comparer les réemplois | `sample`, `interpolation`, `cover` ; titres avec indicateur = 1 / tous les titres | Barres groupées A/B et effectifs au survol | Trois pratiques potentiellement cumulables, affichées sans catégorie exclusive artificielle. |

Une carte mondiale n'a pas été retenue pour cette première itération : des titres associent plusieurs origines et les dénominateurs par territoire sont plus lisibles en barres. Les courbes de tendances annuelles risqueraient aussi de surinterpréter des années peu fournies ; le filtre par décennies permet de construire des comparaisons avant d'en ajouter.

## 4. Premiers constats calculés

Comparaison **1958–1969 (226 titres)** avec **2020–2024 (81 titres)**, sans poids lié à `weeks_at_number_one` :

| Indicateur | 1958–1969 | 2020–2024 |
|---|---:|---:|
| Durée médiane | 161,5 s (n=226) | 200 s (n=81) |
| Intro médiane | 9 s (n=226) | 11 s (n=81) |
| Dansabilité médiane (0–100) | 55 (n=226) | 68 (n=81) |
| Caractère acoustique médian (0–100) | 60 (n=226) | 12 (n=81) |
| Âge médian du frontperson/chef | 23,5 ans (n=220) | 30 ans (n=81) |
| Auteurs par titre, tous crédits · médiane | 2 (n=224) | 5 (n=81) |
| Producteurs par titre · médiane | 1 (n=222) | 2 (n=81) |
| Formats solo | 92/226 (40,7 %) | 60/81 (74,1 %) |
| Origines uniquement américaines, Porto Rico inclus | 180/226 (79,6 %) | 49/81 (60,5 %) |
| Origines mixtes États-Unis/autres | 0/226 | 13/81 (16,0 %) |
| Genre Discogs non renseigné | 0/226 | 16/81 (19,8 %) |
| Titres avec paroles non anglaises | 3/226 (1,3 %) | 4/81 (4,9 %) |

Ces écarts sont descriptifs et sensibles à la couverture des champs, aux conventions de crédit, à la durée inégale des deux fenêtres et au fait que **seuls les n°1 figurent au fichier**. La fréquence de paroles non anglaises porte sur quatre titres récents : elle ne justifie pas une conclusion détaillée par pays ou langue. La première période commence en août 1958.

## 5. Exécution et vérifications

Lancer l'application avec les commandes du `README.md`. Le code livré comprend `app.py`, `analysis.py`, `requirements.txt` et les deux CSV fournis. Les contrôles ont porté sur le chargement du CSV analytique, les colonnes et modalités, les doublons, les valeurs manquantes, les effectifs des périodes, les calculs de médianes et de parts, les trois regroupements d'origines, et la compilation du code. Les graphiques n'emploient pas de pondération hebdomadaire. La sélection vide est traitée avant les calculs graphiques.

Points à corriger lors de la revue du groupe : vérifier manuellement les cas d'origines composées de groupes et la correction `Columbia` ; examiner la qualité des crédits et les graphies équivalentes de personnes ; évaluer les faibles effectifs par filtre ; vérifier, titre par titre, le repérage approximatif des collaborations depuis la chaîne `artist`. Le nombre de titres n°1 par artiste reste un **classement des chaînes de crédit complètes**, pas une attribution individuelle. Le diagnostic visuel devra aussi être confronté aux principes du cours et à une revue sur écran de l'application.
