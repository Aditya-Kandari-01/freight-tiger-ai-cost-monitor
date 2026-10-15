from src.semantic_retriever import SemanticNoteRetriever
from pathlib import Path

import pandas as pd

from src.note_retriever import (
    load_notes,
    retrieve_notes
)
from src.evidence_validator import validate_evidence


OUTPUT_COLUMNS = [
    "route",
    "week_of",
    "cost_per_tonne_km",
    "vs_own_history",
    "vs_similar_routes",
    "flagged",
    "matched_note_id",
    "reason"
]

def format_comparison(value, comparison_type):
    if pd.isna(value):
        return ""

    if comparison_type == "history":
        description = "vs this route's past average"
    else:
        description = "vs similar-length routes this week"

    return f"{value:+.1f}% {description}"


def generate_report(df, notes):
    results = []

    semantic_retriever = SemanticNoteRetriever(notes)
    for _, row in df.iterrows():
        route = (
            f"{row['origin']}-{row['destination']}"
        )

        flagged = "No"
        matched_note_id = ""
        reason = "No significant cost anomaly detected."

        if bool(row["potential_anomaly"]):
            candidates = semantic_retriever.search(
                route=route,
                week_of=row["week_of"],
                top_k=len(notes)
            )

            matched_note_id, reason = (
                validate_evidence(row, candidates)
            )

            if matched_note_id:
                flagged = "No (justified)"
            else:
                flagged = "Yes"

        results.append({
            "route": route,
            "week_of": pd.Timestamp(
                row["week_of"]
            ).strftime("%Y-%m-%d"),
            "cost_per_tonne_km": round(
                row["cost_per_tonne_km"], 4
            ),
            
            "vs_own_history": format_comparison(
                row["vs_own_history"],
                "history"
            ),
            "vs_similar_routes": format_comparison(
                row["vs_similar_routes"],
                "peers"
            ),

            "flagged": flagged,
            "matched_note_id": matched_note_id,
            "reason": reason
        })

    return pd.DataFrame(
        results, columns=OUTPUT_COLUMNS
    )


def main():
    input_path = Path("output/flagged_anomalies.csv")
    output_path = Path("output/final_report.csv")

    df = pd.read_csv(input_path)
    df["week_of"] = pd.to_datetime(df["week_of"])

    notes = load_notes("data/context_notes.csv")

    report = generate_report(df, notes)

    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    report.to_csv(output_path, index=False)

    print("Total records:", len(report))
    print(
        "Unexplained anomalies:",
        (report["flagged"] == "Yes").sum()
    )
    print(
        "Justified anomalies:",
        (report["flagged"] == "No (justified)").sum()
    )
    print(
        "Normal records:",
        (report["flagged"] == "No").sum()
    )

    print("\nEvidence-matched anomalies:")
    print(
        report.loc[
            report["flagged"] == "No (justified)",
            [
                "route",
                "week_of",
                "matched_note_id",
                "flagged"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
