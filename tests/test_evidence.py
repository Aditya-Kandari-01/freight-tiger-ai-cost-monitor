
import pandas as pd

from src.note_retriever import (
    load_notes,
    retrieve_notes
)
from src.evidence_validator import validate_evidence
from src.report_generator import generate_report


def check_note(route, week, history_change=30.0):
    notes = load_notes("data/context_notes.csv")

    origin, destination = route.split("-")

    anomaly = {
        "origin": origin,
        "destination": destination,
        "week_of": week,
        "vs_own_history": history_change
    }

    candidates = retrieve_notes(
        route, week, notes
    )

    return validate_evidence(anomaly, candidates)


def test_festival_justification():
    note_id, _ = check_note(
        "Ahmedabad-Mumbai", "2025-01-20"
    )
    assert note_id == "N002"


def test_flood_justification():
    note_id, _ = check_note(
        "Chennai-Bangalore", "2025-02-24"
    )
    assert note_id == "N001"


def test_flood_second_week():
    note_id, _ = check_note(
        "Chennai-Bangalore", "2025-03-03"
    )
    assert note_id == "N001"


def test_flood_outside_date_range():
    note_id, _ = check_note(
        "Chennai-Bangalore", "2025-03-17"
    )
    assert note_id == ""


def test_unexplained_delhi_jaipur():
    note_id, _ = check_note(
        "Delhi-Jaipur", "2024-11-11"
    )
    assert note_id == ""


def test_unrelated_route():
    note_id, _ = check_note(
        "Mumbai-Pune", "2025-01-20"
    )
    assert note_id == ""


def test_diesel_note_cannot_explain_large_spike():
    note_id, _ = check_note(
        "Mumbai-Pune", "2025-05-05",
        history_change=30.0
    )
    assert note_id == ""


def test_diesel_note_can_support_small_increase():
    note_id, _ = check_note(
        "Mumbai-Pune", "2025-05-05",
        history_change=6.0
    )
    assert note_id == "N003"


def test_negative_context_cannot_justify_spike():
    note_id, _ = check_note(
        "Mumbai-Delhi", "2024-07-29"
    )
    assert note_id == ""


def test_report_has_required_columns():
    notes = load_notes("data/context_notes.csv")

    df = pd.DataFrame([{
        "origin": "Ahmedabad",
        "destination": "Mumbai",
        "route_type": "Medium",
        "week_of": "2025-01-20",
        "cost_per_tonne_km": 3.29,
        "vs_own_history": 29.47,
        "vs_similar_routes": 22.49,
        "potential_anomaly": True
    }])

    result = generate_report(df, notes)

    assert len(result) == 1
    assert result.loc[0, "flagged"] == "No (justified)"
    assert result.loc[0, "matched_note_id"] == "N002"
    assert len(result.columns) == 8
