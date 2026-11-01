# Méthodes de l’observatoire

## Périmètre et unité

Le fichier contient **1 177 titres**, datés de leur première semaine au n°1, du
**4 août 1958 au 11 janvier 2025**. Un titre compte une fois, sans pondération par
`weeks_at_number_one` et sans décompte d’artistes uniques. Les semaines au n°1 ne
sont pas nécessairement situées dans la période filtrée. Un artiste peut
contribuer à plusieurs titres. Les 97 thèmes de `topics.csv` restent hors analyse.
Les CSV bruts sont inchangés.

L’application décrit uniquement ces n°1 : ni causalité, ni prédiction, ni recette
de succès, ni recommandation de recrutement ou norme de production obligatoire.
Les comparaisons servent à situer un projet artistique.

## Périodes et filtres

Au démarrage : mode Décennies, période étudiée **2000–2009**, référence **2020–2024** (81 titres).
Le menu propose séparément **2020–janv. 2025** (82 titres), ainsi que des
intervalles personnalisés pouvant isoler 2025. Les réglages des deux modes sont
indépendants et persistants. 1958 et 2025 sont partielles. Les chevauchements et
les périodes identiques sont signalés près des sélecteurs.

Discogs est la seule classification des genres. `cdr_genre`, absent de la
période récente, n’est jamais utilisé en complément. Un genre renseigné exclut
les lignes sans genre. « Non renseigné » permet de les examiner ; ce n’est pas
un genre musical. Le filtre est identique pour les deux périodes et les courbes.
Sur 2020–2024 sans filtre : 65/81 genres renseignés, 16 manquants (19,8 %).
Cette couverture est recalculée avec les sélections.

## Calculs et données manquantes

Les médianes et quartiles utilisent les valeurs exploitables ; leurs effectifs
sont affichés. Les parts utilisent **tous les titres filtrés** au dénominateur,
y compris les inconnus. Un indicateur entièrement inconnu est indisponible ;
une sélection vide aussi. Un zéro connu reste zéro. Aucun delta n’est calculé
si un côté est indisponible. Le seuil de prudence de moins de 10 titres ou
valeurs exploitables est un repère d’affichage, aucune garantie au-delà.

Les variations de parts sont exprimées en **points de pourcentage** (référence − période étudiée).
Aucune variation relative n’est affichée : pas de division par une base nulle.
Les constats textuels sont déterministes et recalculés après chaque filtre.

Genres et pays sont cumulables : leur somme peut dépasser 100 %. Les formats et
la partition des origines sont exclusifs et totalisent 100 %, inconnus inclus.
Le top 9 des genres et le top 10 des pays sont classés selon la **moyenne des
parts des périodes disponibles**, avec poids égaux. Catégorie absente d’une
période non vide : zéro ; période vide : aucun poids. Égalité : ordre alphabétique.
Une même liste et un même ordre servent aux deux périodes. « Non renseigné » est ajouté aux
genres, hors du top 9 ; les autres catégories restent dans Détails et les filtres.
Pour les genres musicaux, une période entièrement sans genre renseigné est
indisponible et exclue du classement ; elle n’est pas assimilée à une absence
connue de tous les genres. Sa part « Non renseigné » reste calculable.

## Courbes et distributions

Chaque point résume les titres de la **période explicitement inscrite sur l’axe**,
avec le genre actif : 1958–1959, 1960–1969, …, 2020–janv. 2025. Il n’est pas une
observation de l’année 1950 ou 2020. Les points sont placés au milieu de leur
intervalle. Les cartes de comparaison décrivent les intervalles choisis, même s’ils coupent
ces périodes : aucun aplat ne suggère leur équivalence avec une décennie.

La médiane partage les valeurs en deux moitiés. Q1–Q3 contient leur moitié
centrale ; **ce n’est pas un intervalle de confiance**. Quartiles : interpolation
linéaire pandas, indice `(n−1) × p`, sur les valeurs triées. Les boîtes reçoivent
explicitement ces mêmes quartiles : la convention interne « linear » de Plotly
n’était pas identique (Q1 des 81 intros récentes : 6,75 s au lieu de 7 s).
Moustaches : valeurs observées extrêmes dans Q1 − 1,5 IQR et Q3 + 1,5 IQR.
Les points hors moustaches sont visibles pour son, âge, crédits ; masqués pour
durée et intro, tout en restant dans les calculs et les titres associés.

La bande Q1–Q3 et la courbe sont interrompues lorsqu’une période n’a pas de
valeur exploitable. Les équipes proposent trois indicateurs temporels
(auteurs tous crédits, hors samples/interpolations, producteurs). Les pratiques
proposent sample, interpolation ou reprise, sur tous les titres de la décennie.
Les distributions des deux périodes restent accessibles dans la même section.

## Format & son

Les cinq vues séparent le panorama, la durée et l’introduction, la signature
sonore, l’instrumentation et les genres. L’accueil « Explorer les n°1 » présente
les trois parcours analytiques ; la sous-page Format « Vue d’ensemble » garde
son nom et sa fonction. Les anciens accès aux introductions et aux instruments redirigent
vers leurs vues fusionnées, sans changer les filtres. Les sélecteurs affichent
un graphique principal à la fois, sans retirer de mesure ou de mode d’analyse.
Leur choix est conservé après navigation. La navigation fixe est commune à tout
le dashboard : deux niveaux dans les rubriques à plusieurs sous-pages, un seul
sur l’accueil. Routes et clés des filtres restent inchangées.

La phrase récurrente de portée historique est retirée de l’interface, y compris
ses variantes dans les guides et Détails. Cette suppression rédactionnelle ne
change ni les courbes, ni leur filtre de genre, ni les observations partielles,
ni les infobulles. Les conventions de calcul restent celles décrites ci-dessous.

« Année » remplace « Période » uniquement dans cette interface : les mêmes
plages, bornes inclusives et dénominateurs restent utilisés. Les écarts ne sont
plus affichés dans les cartes, graphiques, survols ou tableaux de Format & son ;
les deux valeurs et les effectifs restent consultables. Les fonctions de calcul
des différences et leur affichage dans les autres rubriques restent inchangés.

La **part de l’introduction** est calculée pour chaque titre :
`intro_ratio = 100 * intro_length_sec / length_sec`, uniquement lorsque les deux
valeurs sont renseignées et `length_sec > 0`. La médiane et les quartiles sont
calculés sur les ratios individuels ; **ce n’est pas le ratio des médianes**.
Une introduction de zéro seconde contribue au calcul. Une durée totale nulle,
négative ou manquante, ou une introduction manquante, donne un ratio manquant.
Les effectifs exploitables peuvent donc différer selon les trois mesures.
Les durées médianes totales sont affichées en minutes et secondes ; les
distributions restent en secondes. Les introductions sont en secondes, les
ratios en %. Les effectifs renseignés et les effectifs totaux sont distingués,
y compris lorsque les deux sélections sont identiques ou vides.

Les cinq caractéristiques sonores gardent leurs échelles propres : tempo en
BPM, énergie/dansabilité/caractère acoustique en scores sur 100, niveau sonore
en dB. Les scores ont une échelle graphique de 0 à 100 ; les dB conservent
leurs valeurs négatives, sans imposer une origine à zéro. Aucun radar ni
agrégat ne mélange ces grandeurs. Deux médianes décrivent deux distributions ;
leur comparaison ne démontre pas une évolution identique pour chaque titre.

L’**instrumentation** sépare le rôle central (voix, guitare, piano/claviers,
basse) de la présence de cordes orchestrales ou cuivres/vents. Tous ces
indicateurs peuvent se cumuler. Chaque barre utilise tous les titres filtrés
de sa période au dénominateur, avec les effectifs renseignés dans le survol
et Détails. Le fichier binaire distingue 0, 1 et valeur absente.

L’historique des **genres Discogs** utilise, à chaque décennie, le nombre de
titres associés au genre choisi divisé par tous les titres filtrés de cette
décennie. Un titre multigenre contribue une fois à chaque genre associé.
Une période de comparaison ou décennie vide ou sans aucun genre musical renseigné
est indisponible pour un genre musical ; une absence connue d’un genre vaut zéro. « Non renseigné »
peut être suivi séparément : ses occurrences et son dénominateur restent connus
même si tous les genres manquent. Il n’y a aucun complément par `cdr_genre`.

Le sélecteur historique de genre est distinct du filtre global : dans le
sous-corpus Pop, suivre Rock mesure la présence conjointe de Pop et Rock ;
suivre Pop donne 100 % pour toute décennie non vide. Les cartes A/B et les
distributions utilisent seulement les deux périodes choisies, alors que tous
les historiques couvrent 1958–janvier 2025, avec ce même filtre global.

Les exemples de Format & son se trouvent dans Détails et utilisent la mesure
du graphique sélectionné ainsi que la sélection d’exemples choisie. Les cibles
Q1/médiane/Q3 sont calculées sur tous les titres filtrés de cette période ;
les titres sont pris dans cette même sélection, sans doublon, par distance
absolue à la cible, puis date, titre et artiste en cas d’égalité. Les raccourcis
vers Données préservent les filtres et le fonctionnement de la recherche/export.
Les tableaux de Détails conservent les médianes, quartiles et effectifs utiles
à la lecture du graphique actif. Les guides visibles restent courts ; les
définitions des sources, le ratio d’introduction et les limites des historiques
restent accessibles dans ce volet. Un astérisque signale les décennies partielles
1958–1959 et 2020–janvier 2025 sur les petits écrans.

## Artistes, collaborations, crédits

`front_person_age` : âge du frontperson ou chef de groupe, éventuellement moyenne
s’ils sont plusieurs ; ni âge de chaque membre, ni forcément du chanteur
principal. Décimales conservées. `artist_structure` : 0 groupe, 1 solo, 2 duo ;
+0,5 signifie invité répertorié. `featured_artists` peut contenir un instrumentiste.

L’association d’artistes au crédit est **distincte** de ces deux notions. La
qualification, ses sources et ses limites sont détaillées dans
[Audit des collaborations](livrables/AUDIT_COLLABORATIONS.md). Les séparateurs
seuls ne donnent plus un résultat positif. Les cas non établis restent
indéterminés. Une mention explicite ft./feat., une confirmation documentaire ou
une inférence à partir de crédits distincts peuvent signaler une association.
Cette dernière catégorie reste étiquetée comme inférence et la méthode n’est
pas une classification exhaustive des collaborations réelles.

Les auteurs et producteurs sont comptés par titre : séparation sur « ; », casse
et espaces normalisés, noms dédupliqués. « Unknown » reste manquant. Les auteurs
tous crédits et hors crédits de samples/interpolations sont distincts. Un nom
correspond à un crédit nettoyé ; ce n’est pas une résolution d’identité entre
personnes homonymes. Sample, interpolation et reprise peuvent se cumuler.

## Origines et langue

`artist_place_of_origin` : pays de naissance selon le dictionnaire du cadrage,
ni nationalité, ni marché, ni langue. Séparation sur « ; », espaces retirés,
déduplication par titre. Corrections : `Unites States` → `United States` ;
`Columbia` → `Colombia` pour *We Don't Talk About Bruno*. Cette dernière correction
est étayée par [Disney, casting d’Encanto](https://news.disney.com/cast-of-encanto)
(Mauro Castillo, Cali, Colombie) et la distribution listée par Disney. Elle ne
vaut pas vérification exhaustive de l’origine de chaque membre du casting.
Le libellé brut reste dans les exports. Les 35 combinaisons de libellés source
ont été contrôlées pour leur séparation et leur partition ; le CSV d’audit
conserve toutes les lignes concernées.

Porto Rico est inclus avec les États-Unis dans la partition exclusive, mais
reste séparé sur la carte et dans la comparaison par territoire. Origines mixtes :
au moins une origine américaine (Porto Rico inclus) et une autre ; non classable :
aucune origine exploitable.

Carte : gamme séquentielle, borne commune aux deux périodes. Pays documenté mais absent d’une
sélection renseignée : zéro. Pays non documenté dans le corpus ou sélection sans
origine exploitable : sans donnée, gris. Les repères de petites îles et le
sélecteur permettent de retrouver Porto Rico, la Barbade et Trinité-et-Tobago.
Le mode de comparaison simultanée utilise des barres à base commune.

`foreign_language` indique seulement la présence de paroles non anglaises.
3/226 titres sur 1958–1969 et 4/81 sur 2020–2024 ; 22 titres sur le corpus.
Le complément compact proposé dans Origines conserve l’arbitrage collectif
ouvert : aucune décision de retrait confirmée dans le document consulté.

## Accès aux titres et export

Chaque analyse offre une sélection contextuelle par période, avec recherche titre/artiste.
Les mesures numériques permettent trois titres distincts proches de Q1,
médiane, Q3. Les cibles sont calculées sur la sélection courante (après recherche
si utilisée). En cas d’égalité : date, titre, artiste. Moins de trois valeurs
exploitables : autant d’exemples que possible. Aucune sélection automatique
d’extrêmes ni jugement sur leur qualité.

La table HTML et le CSV viennent d’un même DataFrame. Aucun tri client implicite
ne peut désynchroniser leur ordre. Les valeurs numériques ne sont pas arrondies.
Dates au format ISO ; cellules absentes affichées « Non disponible », vides dans
le CSV. Les booléens dérivés sont libellés Oui/Non/Indéterminé dans les deux.
Un tableau large défile dans son propre cadre accessible au clavier ; il ne
force pas un débordement de la page sur mobile.

## Présentation

Période étudiée violette, référence bleu-vert, ordre constant. Empilements : palette catégorielle et texte
blanc sur les aplats de couleur. Les barres partent de zéro, les
compositions restent sur 0–100 %. Les points conservent une échelle complète,
et les axes des mesures gardent leurs unités. Les symboles et dates des périodes
maintiennent une lecture indépendante de la couleur.

Les options « Situer mon morceau », assistant IA, radar et jauge restent
prospectives, dans le bilan ; aucune n’est nécessaire pour utiliser l’application.
