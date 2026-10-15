
import pandas as pd
import pytest

from src.anomaly_detector import calculate_comparisons


def test_historical_comparison_excludes_current_week():
    df = pd.DataFrame({
        "origin": ["A", "A", "A"],
        "destination": ["B", "B", "B"],
        "route_type": ["Short"] * 3,
        "week_of": pd.to_datetime([
            "2026-01-05",
            "2026-01-12",
            "2026-01-19"
        ]),
        "cost_per_tonne_km": [10.0, 20.0, 30.0]
    })

    result = calculate_comparisons(df)

    assert pd.isna(result.loc[0, "historical_avg"])
    assert result.loc[1, "historical_avg"] == 10.0
    assert result.loc[2, "historical_avg"] == 15.0

    assert result.loc[2, "vs_own_history"] == pytest.approx(100.0)


def test_peer_comparison_excludes_current_route():
    df = pd.DataFrame({
        "origin": ["A", "C", "E"],
        "destination": ["B", "D", "F"],
        "route_type": ["Short"] * 3,
        "week_of": pd.to_datetime(["2026-01-05"] * 3),
        "cost_per_tonne_km": [10.0, 20.0, 30.0]
    })

    result = calculate_comparisons(df)

    target = result[
        (result["origin"] == "A")
        & (result["destination"] == "B")
    ].iloc[0]

    assert target["peer_avg"] == pytest.approx(25.0)
    assert target["vs_similar_routes"] == pytest.approx(-60.0)


def test_single_route_has_no_peer_average():
    df = pd.DataFrame({
        "origin": ["A"],
        "destination": ["B"],
        "route_type": ["Long"],
        "week_of": pd.to_datetime(["2026-01-05"]),
        "cost_per_tonne_km": [10.0]
    })

    result = calculate_comparisons(df)

    assert pd.isna(result.loc[0, "peer_avg"])
    assert pd.isna(result.loc[0, "vs_similar_routes"])
