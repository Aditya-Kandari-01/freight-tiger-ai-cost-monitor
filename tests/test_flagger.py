
import pandas as pd

from src.flagger import flag_anomalies


def test_flags_historical_spike():
    df = pd.DataFrame({
        "vs_own_history": [35.0],
        "vs_similar_routes": [5.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "Yes"


def test_flags_peer_spike_when_cost_is_rising():
    df = pd.DataFrame({
        "vs_own_history": [8.0],
        "vs_similar_routes": [30.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "Yes"


def test_normal_costs():
    df = pd.DataFrame({
        "vs_own_history": [5.0],
        "vs_similar_routes": [10.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "No"


def test_declining_cost_not_flagged():
    df = pd.DataFrame({
        "vs_own_history": [-10.0],
        "vs_similar_routes": [35.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "No"


def test_missing_history_with_peer_spike():
    df = pd.DataFrame({
        "vs_own_history": [float("nan")],
        "vs_similar_routes": [30.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "Yes"


def test_exact_threshold_not_flagged():
    df = pd.DataFrame({
        "vs_own_history": [20.0],
        "vs_similar_routes": [20.0]
    })

    result = flag_anomalies(df)

    assert result.iloc[0]["flagged"] == "No"
