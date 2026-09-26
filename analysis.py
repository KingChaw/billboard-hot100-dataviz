"""Préparation des données et calculs communs à l'application."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


DATA = Path(__file__).resolve().parent / "data" / "billboard.csv"
GENRE_LABELS = {"Funk / Soul": "Funk/Soul", "Funk /Soul": "Funk/Soul"}
ORIGIN_LABELS = {"Unites States": "United States", "Columbia": "Colombia"}
FORMATS = {0.0: "Groupe", 1.0: "Solo", 2.0: "Duo"}
UNKNOWN = {"", "unknown", "n/a", "na", "none", "not known"}
NUMERIC = ["length_sec", "intro_length_sec", "bpm", "energy", "danceability",
           "loudness_d_b", "acousticness", "front_person_age", "artist_structure",
           "sample", "interpolation", "cover", "foreign_language", "vocally_based",
           "bass_based", "guitar_based", "piano_keyboard_based", "orchestral_strings",
           "horns_winds", "weeks_at_number_one"]


def categories(value, aliases=None):
    """Découpe les listes à point-virgule et déduplique par titre."""
    if pd.isna(value):
        return []
    aliases = aliases or {}
    result = []
    for piece in str(value).split(";"):
        piece = aliases.get(piece.strip(), piece.strip())
        if piece and piece.lower() not in UNKNOWN and piece not in result:
            result.append(piece)
    return result


def credits(value):
    seen = set()
    for name in categories(value):
        key = unicodedata.normalize("NFKC", name).casefold().strip()
        key = re.sub(r"\s+", " ", key)
        if key not in UNKNOWN:
            seen.add(key)
    return float(len(seen)) if seen else float("nan")


def origin_group(origins):
    if not origins:
        return "Non classable"
    # Porto Rico est un territoire américain : regroupé avec les États-Unis
    # pour la partition à trois catégories, affiché séparément par pays/territoire.
    american = [x in ("United States", "Puerto Rico") for x in origins]
    if all(american):
        return "États-Unis uniquement (dont Porto Rico)"
    if any(american):
        return "Mixte États-Unis / autres"
    return "Hors États-Unis uniquement"


def prepare(path=DATA):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["year"] = df["date"].dt.year
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["genres"] = df["discogs_genre"].apply(lambda x: categories(x, GENRE_LABELS) or ["Non renseigné"])
    df["origins"] = df["artist_place_of_origin"].apply(lambda x: categories(x, ORIGIN_LABELS))
    df["origin_group"] = df["origins"].apply(origin_group)
    rounded = df["artist_structure"].apply(lambda x: x - 0.5 if pd.notna(x) and x % 1 == 0.5 else x)
    df["artist_format"] = rounded.map(FORMATS).fillna("Non renseigné")
    df["listed_guest"] = df["artist_structure"].apply(lambda x: pd.NA if pd.isna(x) else bool(x % 1 == 0.5)).astype("boolean")
    # Présence d'un autre interprète identifiable dans la chaîne artist ;
    # approximation à examiner ligne par ligne, sans prétendre mesurer les featurings commerciaux.
    df["collaboration_credit"] = df["artist"].fillna("").str.contains(
        r"\bft\.?\b|\bfeat\.?\b|\bfeaturing\b|\s&\s|\s\+\s|\s,\s.*\s(?:and|&)\s",
        case=False, regex=True)
    for source, target in [
        ("songwriters", "writers_all"),
        ("songwriters_w_o_interpolation_sample_credits", "writers_original"),
        ("producers", "producer_count"),
    ]:
        df[target] = df[source].apply(credits)
    return df


def select(df, years, genre="Tous les genres"):
    out = df[df["year"].between(*years)].copy()
    if genre != "Tous les genres":
        out = out[out["genres"].apply(lambda values: genre in values)]
    return out


def category_shares(df, column):
    n = len(df)
    if not n:
        return pd.DataFrame(columns=["catégorie", "effectif", "part"])
    counts = df[column].explode().value_counts()
    return pd.DataFrame({"catégorie": counts.index, "effectif": counts.values,
                         "part": counts.values * 100 / n})


def binary_shares(df, columns, labels):
    n = len(df)
    return pd.DataFrame([
        {"catégorie": labels[col], "effectif": int(df[col].eq(1).sum()),
         "part": 100 * df[col].eq(1).sum() / n if n else 0,
         "renseignés": int(df[col].notna().sum())}
        for col in columns
    ])
