
import pandas as pd


# Evidence windows derived from context_notes.csv.
# Extend these only when the notes provide evidence.
EVIDENCE_RULES = {
    "N001": {
        "start": "2025-02-24",
        "end": "2025-03-08",
        "supports_increase": True,
        "max_increase": None
    },
    "N002": {
        "start": "2025-01-20",
        "end": "2025-01-26",
        "supports_increase": True,
        "max_increase": None
    },
    "N003": {
        "start": "2025-05-05",
        "end": "2025-05-11",
        "supports_increase": True,
        "max_increase": 7.0
    }
}


def validate_evidence(anomaly, candidates):
    """
    Returns:
        (matched_note_id, explanation)

    Only accept documented cost increases when
    their route, date, and magnitude are supported.
    """

    week_start = pd.Timestamp(
        anomaly["week_of"]
    ).normalize()

    week_end = week_start + pd.Timedelta(
        days=6
    )

    historical_change = anomaly.get(
        "vs_own_history"
    )

    for note in candidates:
        note_id = note["note_id"]

        rule = EVIDENCE_RULES.get(note_id)

        if rule is None:
            continue

        if not rule["supports_increase"]:
            continue

        event_start = pd.Timestamp(rule["start"])
        event_end = pd.Timestamp(rule["end"])

        # Weeks must overlap the documented event.
        dates_overlap = (
            week_start <= event_end
            and week_end >= event_start
        )

        if not dates_overlap:
            continue

        # Recheck applicability, not just retrieval.
        route = (
            f"{anomaly['origin']}-"
            f"{anomaly['destination']}"
        )

        applies_to = note["applies_to"]

        if (
            applies_to.lower() != "all routes"
            and applies_to.lower() != route.lower()
        ):
            continue

        # A small documented diesel increase must
        # not justify an unrelated large spike.
        max_increase = rule["max_increase"]

        if max_increase is not None:
            if pd.isna(historical_change):
                continue

            if not (
                0 < historical_change <= max_increase
            ):
                continue

        reason = (
            f"Matches note {note_id}: "
            f"{note['note']} "
            "The documented event overlaps this "
            "route-week and supports higher costs."
        )

        return note_id, reason

    return "", (
        "No sufficiently relevant and supportive "
        "contextual note explains the cost increase. "
        "Flagged for human review."
    )
