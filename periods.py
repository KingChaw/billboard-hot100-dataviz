"""Libellés de présentation, indépendants des identifiants des deux sélections."""
import re


def date_label(years):
    start, end = map(int, years)
    if start == end:
        return "janv. 2025" if end == 2025 else str(start)
    return f"{start} – {'janv. 2025' if end == 2025 else end}"


def period_labels(frames):
    labels = {}
    for index, (key, data) in enumerate(frames.items()):
        years = data.attrs.get("period_years")
        if years is None and len(data) and "year" in data:
            years = (data.year.min(), data.year.max())
        labels[key] = date_label(years) if years is not None else (
            "Sélection étudiée" if index == 0 else "Sélection de référence")
    # Deux sélections identiques gardent leurs identifiants et restent discernables.
    if len(set(labels.values())) < len(labels):
        labels = {key: f"{label} · {'étudiée' if i == 0 else 'référence'}"
                  for i, (key, label) in enumerate(labels.items())}
    return labels


def difference_label(frames):
    studied, reference = period_labels(frames).values()
    return f"{reference} − {studied}"


def display_comparison(table, frames):
    """Renommer à la frontière d'affichage ; conserver les colonnes de calcul."""
    studied, reference = period_labels(frames).values()
    names = {"B − A (points)": f"Écart (points) · {reference} − {studied}"}
    for column in table.columns:
        if column in names:
            continue
        for internal, label in (("A", studied), ("B", reference)):
            if column.startswith(internal + " "):
                names[column] = label + column[1:]
    return table.rename(columns=names)


def export_slug(label):
    return re.sub(r"[^\w-]+", "_", label, flags=re.UNICODE).strip("_")
