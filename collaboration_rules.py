"""Qualification prudente des crédits, distincte du format et des invités.

Les séparateurs ouvrent une vérification, ils ne constituent pas une preuve.
Voir livrables/AUDIT_COLLABORATIONS.md et le CSV d'audit complet.
"""
import re
import unicodedata

import pandas as pd


def normalized(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value))).strip().casefold()


ESTABLISHED_ACTS = {
    "Diana Ross & The Supremes": "https://www.motownmuseum.org/artist/supremes/",
    "Simon & Garfunkel": "https://www.simonandgarfunkel.com/biography/",
    "Daryl Hall & John Oates": "https://rockhall.com/inductees/hall-and-oates/",
    "Earth, Wind & Fire": "https://www.earthwindandfire.com/history/biography/",
    "KC & the Sunshine Band": "https://heykcsb.com/pages/about-kc",
    "Huey Lewis & the News": "https://hueylewisandthenews.com/the-band",
    "Paul McCartney & Wings": "https://www.paulmccartney.com/news/wings-meet-the-band",
    "Sly & the Family Stone": "https://catalog.rockhall.com/rrhof-ais/Details/archive/110000022",
    "The Mamas & the Papas": "https://catalog.rockhall.com/rrhof-ais/Details/archive/110000022",
}
CONFIRMED_ASSOCIATIONS = {
    "Coldplay & BTS": "https://www.coldplay.com/my-universe-single-with-bts-on-september-24th/",
    "Sam Smith & Kim Petras": "https://www.universalmusic.ca/2022/10/24/sam-smiths-unholy-ft-kim-petras-is-no-1/",
    "The Kid Laroi & Justin Bieber": "https://www.sonymusic.ca/press_release/the-kid-laroi-and-justin-bieber-team-up-in-the-long-awaited-new-song-stay",
    "Jawsh 685, Jason Derulo, & BTS": "https://www.sonymusic.ca/press_release/jawsh-685-and-jason-derulo-team-up-with-bts-for-remix-of-savage-love-laxed-siren-beat",
    "6ix9ine & Nicki Minaj": "https://music.apple.com/us/song/trollz/1711520636",
    "Future, Metro Boomin, & Kendrick Lamar": "https://www.youtube.com/watch?v=N9bKBAA22Go",
    "Carolina Gaitán, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz, and the Encanto cast": "https://d23.com/why-everyone-is-talking-about-bruno-from-encanto/",
}
FEATURE = re.compile(r"\b(?:ft\.?|feat\.?|featuring)\s", re.I)
SEPARATOR = re.compile(r"\s(?:&|\+|and|with)\s|,", re.I)


def qualify_credits(df):
    acts = {normalized(k): v for k, v in ESTABLISHED_ACTS.items()}
    associations = {normalized(k): v for k, v in CONFIRMED_ASSOCIATIONS.items()}
    # Preuve interne limitée : crédit individuel présent ailleurs dans le corpus.
    # Les associations ainsi repérées restent distinguées des confirmations externes.
    standalone = {normalized(a) for a in df.artist.dropna()
                  if not SEPARATOR.search(str(a)) and not FEATURE.search(str(a))}
    rows = []
    for artist in df.artist:
        if pd.isna(artist) or normalized(artist) in ("", "unknown", "n/a"):
            rows.append((pd.NA, "Crédit manquant", ""))
            continue
        key = normalized(artist)
        if key in acts:
            rows.append((False, "Formation constituée documentée", acts[key]))
        elif FEATURE.search(str(artist)):
            rows.append((True, "Mention explicite ft./feat./featuring", "Crédit source du titre"))
        elif key in associations:
            rows.append((True, "Association documentée", associations[key]))
        elif SEPARATOR.search(str(artist)):
            names = [normalized(x) for x in re.split(r"\s+(?:&|\+|and|with)\s+|,\s*", str(artist), flags=re.I) if x.strip()]
            if len(names) > 1 and all(name in standalone for name in names):
                rows.append((True, "Crédits distincts retrouvés dans le corpus (inférence)", " ; ".join(names)))
            else:
                rows.append((pd.NA, "Crédit composé à vérifier", "Séparateur seul insuffisant"))
        else:
            rows.append((False, "Un seul crédit identifié", "Ne prouve pas l'absence de toute collaboration"))
    out = pd.DataFrame(rows, index=df.index, columns=["collaboration_credit", "collaboration_status", "collaboration_evidence"])
    out["collaboration_credit"] = out.collaboration_credit.astype("boolean")
    return out
