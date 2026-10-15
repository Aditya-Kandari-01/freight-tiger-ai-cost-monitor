
import pandas as pd

from src.note_retriever import load_notes, retrieve_notes
from src.evidence_validator import validate_evidence


EVALUATION_CASES = [
    {
        "route": "Ahmedabad-Mumbai",
        "week": "2025-01-20",
        "increase": 29.47,
        "expected": "N002"
    },
    {
        "route": "Chennai-Bangalore",
        "week": "2025-02-24",
        "increase": 31.46,
        "expected": "N001"
    },
    {
        "route": "Chennai-Bangalore",
        "week": "2025-03-03",
        "increase": 22.78,
        "expected": "N001"
    },
    {
        "route": "Chennai-Bangalore",
        "week": "2025-03-17",
        "increase": 13.69,
        "expected": ""
    },
    {
        "route": "Delhi-Jaipur",
        "week": "2024-11-11",
        "increase": 35.52,
        "expected": ""
    },
    {
        "route": "Mumbai-Delhi",
        "week": "2024-07-29",
        "increase": 30.0,
        "expected": ""
    },
    {
        "route": "Mumbai-Pune",
        "week": "2025-05-05",
        "increase": 30.0,
        "expected": ""
    },
    {
        "route": "Mumbai-Pune",
        "week": "2025-05-05",
        "increase": 6.0,
        "expected": "N003"
    },
    {
        "route": "Mumbai-Pune",
        "week": "2025-10-27",
        "increase": 30.0,
        "expected": ""
    }
]


def main():
    notes = load_notes()
    correct = 0

    print("Evidence Validation Evaluation\n")

    for case in EVALUATION_CASES:
        origin, destination = case["route"].split("-")

        anomaly = {
            "origin": origin,
            "destination": destination,
            "week_of": case["week"],
            "vs_own_history": case["increase"]
        }

        candidates = retrieve_notes(
            case["route"],
            case["week"],
            notes
        )

        predicted, _ = validate_evidence(
            anomaly, candidates
        )

        passed = predicted == case["expected"]
        correct += int(passed)

        status = "PASS" if passed else "FAIL"

        print(
            f"{status} | {case['route']} | "
            f"{case['week']} | "
            f"Expected: {case['expected'] or 'None'} | "
            f"Predicted: {predicted or 'None'}"
        )

    total = len(EVALUATION_CASES)
    accuracy = correct / total * 100

    print(f"\nCases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")

    if correct != total:
        raise SystemExit("Evidence evaluation failed")


if __name__ == "__main__":
    main()
