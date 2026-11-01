"""Agrégats descriptifs, dénominateurs et comparaisons équilibrées."""
import pandas as pd

from analysis import category_shares
from collaboration_rules import FEATURING  # noqa: F401  (réexporté pour ui)

ORIGINS = {
    "États-Unis uniquement (dont Porto Rico)": "Uniquement États-Unis",
    "Mixte États-Unis / autres": "Mixte",
    "Hors États-Unis uniquement": "Uniquement hors États-Unis",
    "Non classable": "Non classable",
}
ORIGIN_HELP = {
    "Uniquement États-Unis": "Toutes les origines renseignées associées au titre relèvent des États-Unis. Porto Rico est inclus selon la convention du projet.",
    "Mixte": "Au moins une origine américaine (Porto Rico inclus) et une origine hors États-Unis sont associées au titre.",
    "Uniquement hors États-Unis": "Toutes les origines renseignées associées au titre sont hors États-Unis et hors Porto Rico.",
    "Non classable": "Aucune origine exploitable n’est renseignée ; ces titres restent dans le dénominateur.",
}
METRICS = {
    "length_sec": ("Durée", "s"), "intro_length_sec": ("Introduction", "s"),
    "bpm": ("Tempo", "BPM"), "energy": ("Énergie", "score / 100"),
    "danceability": ("Dansabilité", "score / 100"),
    "acousticness": ("Caractère acoustique", "score / 100"),
    "loudness_d_b": ("Niveau sonore", "dB"),
}
# Mesure dérivée réservée à Format & son ; les autres sélecteurs restent inchangés.
FORMAT_METRICS = {**METRICS, "intro_ratio": ("Part de l’introduction", "%")}
SOUND_HELP = {
    "bpm": "Le tempo indique la vitesse de la pulsation, en battements par minute. Un tempo élevé ne signifie pas nécessairement une énergie élevée.",
    "energy": "Score de 0 à 100 décrivant l’intensité et l’activité perçues. Il résume une estimation acoustique, pas la qualité du morceau.",
    "danceability": "Score de 0 à 100 estimant l’aptitude à danser, à partir notamment de la pulsation et de la régularité rythmique. Il ne mesure pas le succès en club.",
    "acousticness": "Score de 0 à 100 estimant le caractère acoustique de l’enregistrement. Il ne compte pas les instruments acoustiques.",
    "loudness_d_b": "Niveau sonore moyen de l’enregistrement, en décibels (dB). Une valeur moins négative correspond à un niveau plus élevé ; ce n’est pas le volume choisi par l’auditeur.",
}
CREDITS = {"writers_original": "Auteurs (sans les crédits de samples)", "writers_all": "Auteurs (crédits de samples inclus)", "producer_count": "Producteurs"}
REUSE = {"sample": "Sample", "interpolation": "Interpolation", "cover": "Reprise"}
AXES = {"length_sec": "Durée (secondes)", "intro_length_sec": "Introduction (secondes)",
        "front_person_age": "Âge (années)",
        **{c: "Nombre de personnes créditées" for c in CREDITS}, "writers_original": "Nombre d’auteurs crédités", "producer_count": "Nombre de producteurs crédités",
        **{c: f"{label} ({unit})" for c, (label, unit) in METRICS.items() if c not in ("length_sec", "intro_length_sec")}}
# Correspondance explicite des libellés présents dans le CSV, sans géocodage externe.
COUNTRIES = {
    "Australia": ("AUS", "Australie"), "Austria": ("AUT", "Autriche"),
    "Barbados": ("BRB", "Barbade"), "Belgium": ("BEL", "Belgique"),
    "Canada": ("CAN", "Canada"), "Colombia": ("COL", "Colombie"),
    "Cuba": ("CUB", "Cuba"), "Czech Republic": ("CZE", "Tchéquie"),
    "France": ("FRA", "France"), "Germany": ("DEU", "Allemagne"),
    "Greece": ("GRC", "Grèce"), "Haiti": ("HTI", "Haïti"),
    "Ireland": ("IRL", "Irlande"), "Italy": ("ITA", "Italie"),
    "Jamaica": ("JAM", "Jamaïque"), "Japan": ("JPN", "Japon"),
    "Mexico": ("MEX", "Mexique"), "Netherlands": ("NLD", "Pays-Bas"),
    "New Zealand": ("NZL", "Nouvelle-Zélande"), "Nigeria": ("NGA", "Nigeria"),
    "Norway": ("NOR", "Norvège"), "Puerto Rico": ("PRI", "Porto Rico"),
    "Senegal": ("SEN", "Sénégal"), "South Africa": ("ZAF", "Afrique du Sud"),
    "South Korea": ("KOR", "Corée du Sud"), "Spain": ("ESP", "Espagne"),
    "Sweden": ("SWE", "Suède"), "Trinidad and Tobago": ("TTO", "Trinité-et-Tobago"),
    "United Kingdom": ("GBR", "Royaume-Uni"), "United States": ("USA", "États-Unis"),
}


def decades(df, column=None, origin=None, coverage=None, binary=None, genre=None):
    """Une médiane et Q1–Q3, ou une part / tous les titres ; pas de zéro inventé."""
    first, last = coverage or ((int(df.year.min()), int(df.year.max())) if len(df) else (1958, 2025))
    rows = []
    for decade in range(first // 10 * 10, last // 10 * 10 + 1, 10):
        start, end = max(first, decade), min(last, decade + 9)
        d = df[df.year.between(start, end)]
        label = f"{start}–{end}"
        if end == 2025:
            label = f"{start}–janv. 2025" if start != end else "janv. 2025"
        row = dict(decade=decade, start=start, end=end, label=label, position=(start + end) / 2,
                   total=len(d), partial=decade < first or decade + 9 > last)
        if genre is not None:
            valid = len(d) if genre == "Non renseigné" else int(d.genres.map(lambda g: g != ["Non renseigné"]).sum())
            count = int(d.genres.map(lambda g: genre in g).sum())
            row.update(value=100 * count / len(d) if len(d) and valid else float("nan"),
                       valid=valid, count=count, q1=float("nan"), q3=float("nan"))
        elif origin is not None:
            valid = int(d.origins.map(bool).sum())
            count = int(d.origin_group.eq(origin).sum())
            row.update(value=100 * count / len(d) if len(d) and valid else float("nan"),
                       valid=valid, count=count, q1=float("nan"), q3=float("nan"))
        elif binary is not None:
            valid = int(d[binary].notna().sum())
            count = int(d[binary].eq(1).sum())
            row.update(value=100 * count / len(d) if len(d) and valid else float("nan"),
                       valid=valid, count=count, q1=float("nan"), q3=float("nan"))
        else:
            values = d[column].dropna()
            row.update(value=values.median(), q1=values.quantile(.25), q3=values.quantile(.75), valid=len(values))
        rows.append(row)
    return pd.DataFrame(rows)


def ranked_categories(data, limit=9, missing="Non renseigné"):
    """Moyenne des parts A/B ; catégories absentes à zéro, périodes vides exclues.

    Une période sans aucune part disponible ne reçoit aucun poids. Les deux
    périodes disponibles pèsent chacune 1/2, quelle que soit leur taille.
    """
    if data.empty:
        return [missing] if missing else []
    available = data.groupby("période")["part"].apply(lambda s: s.notna().any())
    periods = available[available].index
    matrix = data.pivot_table(index="catégorie", columns="période", values="part", aggfunc="first")
    scores = matrix.reindex(columns=periods).fillna(0).mean(axis=1)
    scores = scores.drop(index=missing, errors="ignore") if missing else scores
    order = sorted(scores.index, key=lambda name: (-scores[name] if pd.notna(scores[name]) else 0, name))[:limit]
    if missing:
        order.append(missing)
    return order


def comparison_rows(data, frames, order):
    """Même ordre et écarts en points ; aucune comparaison si un côté manque."""
    rows = []
    for category in order:
        row = {"Indicateur": category}
        values = []
        for label, (period, frame) in zip(("A", "B"), frames.items()):
            found = data[data["catégorie"].eq(category) & data["période"].eq(period)]
            if found.empty:
                value, count, valid = (0.0, 0, len(frame)) if len(frame) else (float("nan"), 0, 0)
            else:
                item = found.iloc[0]
                value, count, valid = item.part, int(item.effectif), int(item.get("renseignés", len(frame)))
            values.append(value)
            row.update({f"{label} (%)": value, f"{label} · titres concernés": count,
                        f"{label} · total": len(frame), f"{label} · renseignés": valid})
        row["B − A (points)"] = values[1] - values[0]
        rows.append(row)
    return pd.DataFrame(rows)


def quartile_examples(data, column):
    """Jusqu’à trois titres distincts, proches de Q1, médiane et Q3 du filtre actif."""
    available = data.dropna(subset=[column]).sort_values(["date", "song", "artist"], kind="stable")
    rows = []
    for label, quantile in [("Q1", .25), ("Médiane", .5), ("Q3", .75)]:
        remaining = available.drop(index=[row["index"] for row in rows])
        if remaining.empty:
            break
        target = available[column].quantile(quantile)
        index = (remaining[column] - target).abs().idxmin()
        row = remaining.loc[index]
        rows.append({"index": index, "repère": label, "cible": target,
                     "song": row.song, "artist": row.artist, "value": row[column]})
    return rows


def overlap_message(a, b):
    if tuple(a) == tuple(b):
        return "Les deux périodes sont identiques : mêmes titres, aucun changement temporel mesuré."
    if max(a[0], b[0]) <= min(a[1], b[1]):
        return "Les deux périodes se chevauchent : des titres contribuent aux deux périodes."
    return None


def country_frame(frames, all_data):
    """Un pays documenté dans le corpus peut valoir 0 ; une sélection inconnue vaut NaN."""
    known = sorted(set(all_data.origins.explode().dropna()))
    rows = []
    for period, data in frames.items():
        shares = category_shares(data, "origins").set_index("catégorie")
        valid = int(data.origins.map(bool).sum())
        for country in known:
            count = int(shares.loc[country, "effectif"]) if country in shares.index else 0
            iso, label = COUNTRIES.get(country, (None, country))
            rows.append({"période": period, "pays": label, "source": country, "iso": iso,
                         "effectif": count, "total": len(data), "renseignés": valid,
                         "part": count * 100 / len(data) if len(data) and valid else float("nan")})
    return pd.DataFrame(rows)
