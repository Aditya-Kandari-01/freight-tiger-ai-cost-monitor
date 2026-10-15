
import pytest

from src.note_retriever import load_notes
from src.semantic_retriever import SemanticNoteRetriever


@pytest.fixture(scope="module")
def retriever():
    notes = load_notes("data/context_notes.csv")
    return SemanticNoteRetriever(notes)


@pytest.mark.parametrize(
    "route,week,expected_note",
    [
        ("Ahmedabad-Mumbai", "2025-01-20", "N002"),
        ("Chennai-Bangalore", "2025-02-24", "N001"),
        ("Chennai-Bangalore", "2025-03-03", "N001"),
    ]
)
def test_relevant_note_is_retrieved(
    retriever, route, week, expected_note
):
    candidates = retriever.search(
        route=route,
        week_of=week,
        top_k=10
    )

    retrieved_ids = [
        candidate["note_id"]
        for candidate in candidates
    ]

    assert expected_note in retrieved_ids


def test_unrelated_route_note_not_retrieved(retriever):
    candidates = retriever.search(
        route="Delhi-Jaipur",
        week_of="2025-02-24",
        top_k=10
    )

    retrieved_ids = [
        candidate["note_id"]
        for candidate in candidates
    ]

    assert "N001" not in retrieved_ids
