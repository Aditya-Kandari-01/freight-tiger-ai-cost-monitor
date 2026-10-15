
import pandas as pd


def load_notes(path="data/context_notes.csv"):
    notes = pd.read_csv(path)
    notes["date"] = pd.to_datetime(
        notes["date"], errors="raise"
    )
    return notes


def retrieve_notes(
    route,
    week_of,
    notes,
    max_days=21
):
    """
    Retrieve potentially relevant notes using
    route matching and date proximity.

    Retrieval does NOT mean the note is valid
    justification for higher costs.
    """
    week = pd.Timestamp(week_of).normalize()
    candidates = []

    for _, note in notes.iterrows():
        applies_to = str(note["applies_to"])
        note_date = pd.Timestamp(note["date"])

        # Notes can be route-specific or nationwide
        route_match = (
            applies_to.lower() == "all routes"
            or applies_to.lower() == route.lower()
        )

        if not route_match:
            continue

        days_difference = abs(
            (week - note_date).days
        )

        if days_difference > max_days:
            continue

        candidates.append({
            "note_id": str(note["note_id"]),
            "date": note_date,
            "applies_to": applies_to,
            "note": str(note["note"]),
            "days_difference": days_difference
        })

    # Specific routes first, then closest date
    candidates.sort(
        key=lambda n: (
            n["applies_to"].lower() == "all routes",
            n["days_difference"],
            n["note_id"]
        )
    )

    return candidates
