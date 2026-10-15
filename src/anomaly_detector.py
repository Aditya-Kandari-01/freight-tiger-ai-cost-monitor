
import pandas as pd
from pathlib import Path


def calculate_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Sort route records chronologically
    df = df.sort_values(
        ["origin", "destination", "week_of"]
    ).reset_index(drop=True)

    # STEP 2A: Historical comparison
    route_groups = df.groupby(
        ["origin", "destination", "route_type"]
    )["cost_per_tonne_km"]

    df["historical_avg"] = route_groups.transform(
        lambda s: s.shift(1).rolling(
            window=8,
            min_periods=1
        ).mean()
    )

    df["vs_own_history"] = (
        (df["cost_per_tonne_km"] - df["historical_avg"])
        / df["historical_avg"]
    ) * 100

    # STEP 2B: Peer comparison
    peer_groups = df.groupby(
        ["route_type", "week_of"]
    )["cost_per_tonne_km"]

    peer_sum = peer_groups.transform("sum")
    peer_count = peer_groups.transform("count")

    df["peer_avg"] = (
        (peer_sum - df["cost_per_tonne_km"])
        / (peer_count - 1).replace(0, float("nan"))
    )

    df["vs_similar_routes"] = (
        (df["cost_per_tonne_km"] - df["peer_avg"])
        / df["peer_avg"]
    ) * 100

    return df


if __name__ == "__main__":
    input_path = Path("output/weekly_costs.csv")
    output_path = Path("output/weekly_comparisons.csv")

    df = pd.read_csv(input_path)
    df["week_of"] = pd.to_datetime(df["week_of"])

    result = calculate_comparisons(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print(f"Processed {len(result)} weekly records")
    print(
        result[
            [
                "origin",
                "destination",
                "week_of",
                "cost_per_tonne_km",
                "vs_own_history",
                "vs_similar_routes",
            ]
        ].head(10).to_string(index=False)
    )
