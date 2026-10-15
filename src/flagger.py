
import pandas as pd
from pathlib import Path

THRESHOLD = 20.0


def flag_anomalies(df: pd.DataFrame, threshold=THRESHOLD):
    df = df.copy()

    history = df["vs_own_history"]
    peers = df["vs_similar_routes"]

    # A significant increase relative to either baseline
    history_spike = history > threshold
    peer_spike = peers > threshold

    # Costs should be rising relative to known history.
    # For the first week, history is unavailable.
    rising = (history > 0) | history.isna()

    df["potential_anomaly"] = (
        rising & (history_spike | peer_spike)
    )

    df["flagged"] = df["potential_anomaly"].map({
        True: "Yes",
        False: "No"
    })

    return df


if __name__ == "__main__":
    input_path = Path("output/weekly_comparisons.csv")
    output_path = Path("output/flagged_anomalies.csv")

    df = pd.read_csv(input_path)

    result = flag_anomalies(df)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(output_path, index=False)

    print("Total records:", len(result))

    print(
        "Potential anomalies:",
        result["potential_anomaly"].sum()
    )

    print(
        "Normal records:",
        (~result["potential_anomaly"]).sum()
    )

    print(
        result.loc[
            result["potential_anomaly"],
            [
                "origin",
                "destination",
                "week_of",
                "vs_own_history",
                "vs_similar_routes",
                "flagged"
            ]
        ].head(10).to_string(index=False)
    )
